from rest_framework import serializers
from django.utils import timezone
from .models import SensorReading, AlertEvent, SimulationTrigger
from river.models import MonitoringStation


class SensorReadingIngestSerializer(serializers.Serializer):
    """
    Used for the sensor ingest endpoint.
    Sensors POST to /api/sensors/ingest/ with this payload.
    """
    station_code = serializers.CharField(max_length=50)
    sensor_timestamp = serializers.DateTimeField()
    device_id = serializers.CharField(max_length=100, required=False, allow_blank=True)
    firmware_version = serializers.CharField(max_length=50, required=False, allow_blank=True)
    battery_level_pct = serializers.FloatField(required=False, allow_null=True)
    signal_strength_dbm = serializers.FloatField(required=False, allow_null=True)

    # Measurements — all optional so sensors can send only what they measure
    heavy_metals_mgl = serializers.FloatField(required=False, allow_null=True)
    organics_mgl = serializers.FloatField(required=False, allow_null=True)
    nutrients_mgl = serializers.FloatField(required=False, allow_null=True)
    pathogens_cfu = serializers.FloatField(required=False, allow_null=True)
    suspended_solids_mgl = serializers.FloatField(required=False, allow_null=True)
    ph = serializers.FloatField(required=False, allow_null=True)
    dissolved_oxygen_mgl = serializers.FloatField(required=False, allow_null=True)
    temperature_c = serializers.FloatField(required=False, allow_null=True)
    turbidity_ntu = serializers.FloatField(required=False, allow_null=True)
    conductivity_us = serializers.FloatField(required=False, allow_null=True)
    flow_rate_m3s = serializers.FloatField(required=False, allow_null=True)

    def validate_station_code(self, value):
        try:
            MonitoringStation.objects.get(station_code=value, is_active=True)
        except MonitoringStation.DoesNotExist:
            raise serializers.ValidationError(f"No active monitoring station with code '{value}'.")
        return value


class SensorReadingSerializer(serializers.ModelSerializer):
    station_code = serializers.CharField(source="station.station_code", read_only=True)
    station_name = serializers.CharField(source="station.name", read_only=True)

    class Meta:
        model = SensorReading
        fields = "__all__"


class AlertEventSerializer(serializers.ModelSerializer):
    station_code = serializers.CharField(source="station.station_code", read_only=True)
    station_name = serializers.CharField(source="station.name", read_only=True)
    station_km = serializers.FloatField(source="station.km_location", read_only=True)

    class Meta:
        model = AlertEvent
        fields = "__all__"


class SimulationTriggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimulationTrigger
        fields = "__all__"


class AcknowledgeAlertSerializer(serializers.Serializer):
    acknowledged_by = serializers.CharField(max_length=100)
