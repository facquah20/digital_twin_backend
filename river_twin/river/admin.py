from django.contrib import admin
from .models import RiverSystem, CrossSection, ContaminantSource, MonitoringStation


class CrossSectionInline(admin.TabularInline):
    model = CrossSection
    extra = 0
    fields = ("km_marker","section_type","width_m","max_depth_m","bank_height_m")


class ContaminantSourceInline(admin.TabularInline):
    model = ContaminantSource
    extra = 0
    fields = ("name","contaminant_type","km_location","peak_concentration","is_active")


class MonitoringStationInline(admin.TabularInline):
    model = MonitoringStation
    extra = 0
    fields = ("station_code","name","role","km_location","is_active")


@admin.register(RiverSystem)
class RiverSystemAdmin(admin.ModelAdmin):
    list_display = ("name","total_length_km","base_flow_rate","is_active","created_at")
    list_filter = ("is_active",)
    inlines = [ContaminantSourceInline, MonitoringStationInline, CrossSectionInline]


@admin.register(ContaminantSource)
class ContaminantSourceAdmin(admin.ModelAdmin):
    list_display = ("name","source_label","contaminant_type","km_location","discharge_mode","is_active","river")
    list_filter = ("contaminant_type","discharge_mode","is_active","river")
    search_fields = ("name","source_label")


@admin.register(MonitoringStation)
class MonitoringStationAdmin(admin.ModelAdmin):
    list_display = ("station_code","name","role","km_location","is_active","last_reading_at","river")
    list_filter = ("role","is_active","river")
    search_fields = ("station_code","name")


@admin.register(CrossSection)
class CrossSectionAdmin(admin.ModelAdmin):
    list_display = ("river","km_marker","section_type","width_m","max_depth_m")
    list_filter = ("section_type","river")
