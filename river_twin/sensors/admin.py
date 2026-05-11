from django.contrib import admin
from .models import SensorReading, AlertEvent, SimulationTrigger


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("id","station","sensor_timestamp","status","is_processed","received_at",
                    "heavy_metals_mgl","organics_mgl","nutrients_mgl","pathogens_cfu")
    list_filter = ("status","is_processed","station")
    search_fields = ("station__station_code","device_id")
    readonly_fields = ("raw_payload","received_at","status","is_processed")


@admin.register(AlertEvent)
class AlertEventAdmin(admin.ModelAdmin):
    list_display = ("id","station","contaminant_type","measured_value","threshold_value",
                    "severity","is_acknowledged","created_at")
    list_filter = ("severity","contaminant_type","is_acknowledged","station")
    search_fields = ("station__station_code","message")
    actions = ["acknowledge_selected"]

    def acknowledge_selected(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_acknowledged=True, acknowledged_at=timezone.now(), acknowledged_by=str(request.user))
    acknowledge_selected.short_description = "Acknowledge selected alerts"


@admin.register(SimulationTrigger)
class SimulationTriggerAdmin(admin.ModelAdmin):
    list_display = ("id","alert","status","retry_count","response_code","triggered_at")
    list_filter = ("status",)
    readonly_fields = ("payload","response_body","triggered_at")
