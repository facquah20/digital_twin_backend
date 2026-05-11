from rest_framework import serializers
from .models import RiverSystem, CrossSection, ContaminantSource, MonitoringStation


class CrossSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrossSection
        fields = "__all__"


class ContaminantSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContaminantSource
        fields = "__all__"


class MonitoringStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonitoringStation
        fields = "__all__"


class RiverSystemSerializer(serializers.ModelSerializer):
    cross_sections = CrossSectionSerializer(many=True, read_only=True)
    contaminant_sources = ContaminantSourceSerializer(many=True, read_only=True)
    monitoring_stations = MonitoringStationSerializer(many=True, read_only=True)
    source_count = serializers.SerializerMethodField()
    station_count = serializers.SerializerMethodField()

    class Meta:
        model = RiverSystem
        fields = "__all__"

    def get_source_count(self, obj):
        return obj.contaminant_sources.filter(is_active=True).count()

    def get_station_count(self, obj):
        return obj.monitoring_stations.filter(is_active=True).count()


class RiverSystemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    source_count = serializers.SerializerMethodField()
    station_count = serializers.SerializerMethodField()

    class Meta:
        model = RiverSystem
        fields = ["id","name","total_length_km","base_flow_rate","is_active","source_count","station_count","created_at"]

    def get_source_count(self, obj):
        return obj.contaminant_sources.filter(is_active=True).count()

    def get_station_count(self, obj):
        return obj.monitoring_stations.filter(is_active=True).count()
