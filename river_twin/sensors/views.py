from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg, Max, Count, Q

from .models import SensorReading, AlertEvent, SimulationTrigger
from .serializers import (
    SensorReadingIngestSerializer, SensorReadingSerializer,
    AlertEventSerializer, SimulationTriggerSerializer, AcknowledgeAlertSerializer,
)
from .services import process_reading
from river.models import MonitoringStation


@api_view(["POST"])
def ingest_reading(request):
    """
    Primary sensor ingest endpoint.
    Workstations POST contaminant readings here.
    POST /api/sensors/ingest/
    """
    serializer = SensorReadingIngestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    station = MonitoringStation.objects.get(station_code=data.pop("station_code"), is_active=True)

    reading = SensorReading.objects.create(
        station=station,
        raw_payload=request.data,
        **data,
    )

    alerts = process_reading(reading)

    return Response({
        "reading_id": reading.id,
        "station_code": station.station_code,
        "status": reading.status,
        "alerts_triggered": len(alerts),
        "alerts": [
            {"id": a.id, "contaminant": a.contaminant_type, "severity": a.severity}
            for a in alerts
        ],
        "received_at": reading.received_at,
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def bulk_ingest(request):
    """
    Bulk ingest: receive an array of readings from one or more stations.
    POST /api/sensors/bulk-ingest/
    Body: { "readings": [ {...}, {...} ] }
    """
    readings_data = request.data.get("readings", [])
    if not readings_data:
        return Response({"error": "No readings provided."}, status=status.HTTP_400_BAD_REQUEST)

    results = []
    for item in readings_data:
        ser = SensorReadingIngestSerializer(data=item)
        if not ser.is_valid():
            results.append({"error": ser.errors, "raw": item})
            continue
        data = ser.validated_data
        station = MonitoringStation.objects.get(station_code=data.pop("station_code"), is_active=True)
        reading = SensorReading.objects.create(station=station, raw_payload=item, **data)
        alerts = process_reading(reading)
        results.append({
            "reading_id": reading.id,
            "station_code": station.station_code,
            "status": reading.status,
            "alerts_triggered": len(alerts),
        })

    return Response({"processed": len(results), "results": results}, status=status.HTTP_201_CREATED)


class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SensorReadingSerializer

    def get_queryset(self):
        qs = SensorReading.objects.select_related("station").all()
        station = self.request.query_params.get("station")
        if station:
            qs = qs.filter(station__station_code=station)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        since = self.request.query_params.get("since")
        if since:
            qs = qs.filter(received_at__gte=since)
        return qs[:500]

    @action(detail=False, methods=["get"])
    def latest(self, request):
        """Latest reading per station."""
        stations = MonitoringStation.objects.filter(is_active=True)
        result = []
        for st in stations:
            reading = SensorReading.objects.filter(station=st).order_by("-received_at").first()
            if reading:
                result.append(SensorReadingSerializer(reading).data)
        return Response(result)

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        """Aggregated statistics for the monitoring dashboard."""
        total = SensorReading.objects.count()
        alerts_today = AlertEvent.objects.filter(
            created_at__date=timezone.now().date()
        ).count()
        active_alerts = AlertEvent.objects.filter(is_acknowledged=False).count()
        critical = AlertEvent.objects.filter(is_acknowledged=False, severity__in=["critical","emergency"]).count()

        by_station = []
        for st in MonitoringStation.objects.filter(is_active=True):
            agg = SensorReading.objects.filter(station=st).aggregate(
                count=Count("id"),
                avg_heavy_metals=Avg("heavy_metals_mgl"),
                avg_organics=Avg("organics_mgl"),
                avg_nutrients=Avg("nutrients_mgl"),
                max_heavy_metals=Max("heavy_metals_mgl"),
                max_organics=Max("organics_mgl"),
            )
            agg["station_code"] = st.station_code
            agg["station_name"] = st.name
            agg["km_location"] = st.km_location
            agg["last_reading_at"] = st.last_reading_at
            agg["pending_alerts"] = AlertEvent.objects.filter(station=st, is_acknowledged=False).count()
            by_station.append(agg)

        return Response({
            "total_readings": total,
            "alerts_today": alerts_today,
            "active_alerts": active_alerts,
            "critical_alerts": critical,
            "by_station": by_station,
        })


class AlertEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AlertEventSerializer

    def get_queryset(self):
        qs = AlertEvent.objects.select_related("station", "reading").all()
        station = self.request.query_params.get("station")
        if station:
            qs = qs.filter(station__station_code=station)
        severity = self.request.query_params.get("severity")
        if severity:
            qs = qs.filter(severity=severity)
        unacked = self.request.query_params.get("unacknowledged")
        if unacked == "true":
            qs = qs.filter(is_acknowledged=False)
        return qs[:200]

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        ser = AcknowledgeAlertSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        alert.is_acknowledged = True
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = ser.validated_data["acknowledged_by"]
        alert.save(update_fields=["is_acknowledged","acknowledged_at","acknowledged_by"])
        return Response(AlertEventSerializer(alert).data)

    @action(detail=False, methods=["post"])
    def acknowledge_bulk(self, request):
        """Acknowledge multiple alerts at once. Body: {ids: [1,2,3], acknowledged_by: 'name'}"""
        ids = request.data.get("ids", [])
        by = request.data.get("acknowledged_by", "system")
        now = timezone.now()
        updated = AlertEvent.objects.filter(id__in=ids, is_acknowledged=False).update(
            is_acknowledged=True, acknowledged_at=now, acknowledged_by=by
        )
        return Response({"acknowledged": updated})


class SimulationTriggerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SimulationTriggerSerializer
    queryset = SimulationTrigger.objects.select_related("alert__station").all()[:200]
