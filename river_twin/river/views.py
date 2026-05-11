from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RiverSystem, CrossSection, ContaminantSource, MonitoringStation
from .serializers import (
    RiverSystemSerializer, RiverSystemListSerializer,
    CrossSectionSerializer, ContaminantSourceSerializer, MonitoringStationSerializer,
)


class RiverSystemViewSet(viewsets.ModelViewSet):
    queryset = RiverSystem.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return RiverSystemListSerializer
        return RiverSystemSerializer

    @action(detail=True, methods=["get"])
    def summary(self, request, pk=None):
        """Full system overview: geometry + sources + stations."""
        river = self.get_object()
        serializer = RiverSystemSerializer(river)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        river = self.get_object()
        river.is_active = not river.is_active
        river.save(update_fields=["is_active"])
        return Response({"id": river.id, "is_active": river.is_active})


class CrossSectionViewSet(viewsets.ModelViewSet):
    serializer_class = CrossSectionSerializer

    def get_queryset(self):
        qs = CrossSection.objects.all()
        river_id = self.request.query_params.get("river")
        if river_id:
            qs = qs.filter(river_id=river_id)
        return qs


class ContaminantSourceViewSet(viewsets.ModelViewSet):
    serializer_class = ContaminantSourceSerializer

    def get_queryset(self):
        qs = ContaminantSource.objects.all()
        river_id = self.request.query_params.get("river")
        if river_id:
            qs = qs.filter(river_id=river_id)
        ctype = self.request.query_params.get("type")
        if ctype:
            qs = qs.filter(contaminant_type=ctype)
        return qs

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        source = self.get_object()
        source.is_active = not source.is_active
        source.save(update_fields=["is_active"])
        return Response({"id": source.id, "is_active": source.is_active})


class MonitoringStationViewSet(viewsets.ModelViewSet):
    serializer_class = MonitoringStationSerializer

    def get_queryset(self):
        qs = MonitoringStation.objects.all()
        river_id = self.request.query_params.get("river")
        if river_id:
            qs = qs.filter(river_id=river_id)
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs
