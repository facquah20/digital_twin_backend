from django.db import models


class RiverSystem(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    total_length_km = models.FloatField(help_text="Total river length in km")
    base_flow_rate = models.FloatField(help_text="Base flow rate m³/s")
    sinuosity_index = models.FloatField(default=1.3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "River System"


class CrossSection(models.Model):
    SECTION_TYPES = [("pool","Pool"),("riffle","Riffle"),("run","Run"),("glide","Glide")]
    river = models.ForeignKey(RiverSystem, on_delete=models.CASCADE, related_name="cross_sections")
    km_marker = models.FloatField()
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES)
    width_m = models.FloatField()
    max_depth_m = models.FloatField()
    bank_height_m = models.FloatField()
    thalweg_offset_m = models.FloatField(default=0.0)
    parabola_a = models.FloatField()
    parabola_b = models.FloatField()

    class Meta:
        ordering = ["km_marker"]
        unique_together = ["river", "km_marker"]

    def __str__(self):
        return f"{self.river.name} @ Km {self.km_marker:.2f} ({self.section_type})"


class ContaminantSource(models.Model):
    CONTAMINANT_TYPES = [
        ("heavy_metals","Heavy Metals"),("organic","Organic Compounds"),
        ("nutrients","Nutrients"),("pathogens","Pathogens"),
        ("suspended_solids","Suspended Solids"),("other","Other"),
    ]
    DISCHARGE_MODES = [("continuous","Continuous"),("pulsed","Pulsed"),("batch","Batch")]

    river = models.ForeignKey(RiverSystem, on_delete=models.CASCADE, related_name="contaminant_sources")
    name = models.CharField(max_length=255)
    source_label = models.CharField(max_length=100)
    contaminant_type = models.CharField(max_length=30, choices=CONTAMINANT_TYPES)
    km_location = models.FloatField()
    plume_sigma_x = models.FloatField(default=5.0)
    plume_sigma_y = models.FloatField(default=2.0)
    peak_concentration = models.FloatField()
    decay_rate = models.FloatField()
    discharge_mode = models.CharField(max_length=20, choices=DISCHARGE_MODES, default="continuous")
    pulse_on_hours = models.FloatField(null=True, blank=True)
    pulse_off_hours = models.FloatField(null=True, blank=True)
    flow_rate_m3s = models.FloatField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.contaminant_type}) @ Km {self.km_location}"

    class Meta:
        ordering = ["km_location"]


class MonitoringStation(models.Model):
    STATION_ROLES = [
        ("upstream_reference","Upstream Reference"),("industrial_outfall","Industrial Outfall Zone"),
        ("agricultural_buffer","Agricultural Buffer Zone"),("municipal_intake","Municipal Water Intake"),
        ("wetland_buffer","Wetland Buffer"),("downstream_gauge","Downstream Gauge"),("custom","Custom"),
    ]
    river = models.ForeignKey(RiverSystem, on_delete=models.CASCADE, related_name="monitoring_stations")
    name = models.CharField(max_length=255)
    station_code = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=30, choices=STATION_ROLES)
    km_location = models.FloatField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    elevation_m = models.FloatField(null=True, blank=True)
    alert_threshold_heavy_metals = models.FloatField(null=True, blank=True)
    alert_threshold_organics = models.FloatField(null=True, blank=True)
    alert_threshold_nutrients = models.FloatField(null=True, blank=True)
    alert_threshold_pathogens = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_reading_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.station_code}] {self.name} @ Km {self.km_location}"

    class Meta:
        ordering = ["km_location"]
