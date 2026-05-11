from django.db import models
from river.models import MonitoringStation, ContaminantSource


class SensorReading(models.Model):
    """Raw sensor reading received from a field workstation."""
    STATUS_CHOICES = [("ok","OK"),("alert","Alert"),("critical","Critical"),("error","Error")]

    station = models.ForeignKey(MonitoringStation, on_delete=models.CASCADE, related_name="readings")
    received_at = models.DateTimeField(auto_now_add=True)
    sensor_timestamp = models.DateTimeField(help_text="Timestamp from the sensor device")

    # Measured contaminant concentrations (mg/L unless noted)
    heavy_metals_mgl = models.FloatField(null=True, blank=True)
    organics_mgl = models.FloatField(null=True, blank=True)
    nutrients_mgl = models.FloatField(null=True, blank=True)
    pathogens_cfu = models.FloatField(null=True, blank=True, help_text="CFU/100mL")
    suspended_solids_mgl = models.FloatField(null=True, blank=True)
    ph = models.FloatField(null=True, blank=True)
    dissolved_oxygen_mgl = models.FloatField(null=True, blank=True)
    temperature_c = models.FloatField(null=True, blank=True)
    turbidity_ntu = models.FloatField(null=True, blank=True)
    conductivity_us = models.FloatField(null=True, blank=True, help_text="μS/cm")
    flow_rate_m3s = models.FloatField(null=True, blank=True)

    # Device metadata
    device_id = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    battery_level_pct = models.FloatField(null=True, blank=True)
    signal_strength_dbm = models.FloatField(null=True, blank=True)

    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="ok")
    is_processed = models.BooleanField(default=False)
    raw_payload = models.JSONField(default=dict, help_text="Full raw JSON from sensor")

    class Meta:
        ordering = ["-received_at"]
        indexes = [
            models.Index(fields=["station", "-received_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Reading [{self.station.station_code}] @ {self.sensor_timestamp}"


class AlertEvent(models.Model):
    """Generated when a sensor reading breaches a threshold."""
    SEVERITY_CHOICES = [("warning","Warning"),("critical","Critical"),("emergency","Emergency")]
    CONTAMINANT_CHOICES = [
        ("heavy_metals","Heavy Metals"),("organics","Organics"),
        ("nutrients","Nutrients"),("pathogens","Pathogens"),("other","Other"),
    ]

    reading = models.ForeignKey(SensorReading, on_delete=models.CASCADE, related_name="alerts")
    station = models.ForeignKey(MonitoringStation, on_delete=models.CASCADE, related_name="alerts")
    created_at = models.DateTimeField(auto_now_add=True)
    contaminant_type = models.CharField(max_length=30, choices=CONTAMINANT_CHOICES)
    measured_value = models.FloatField()
    threshold_value = models.FloatField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    message = models.TextField()
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.severity.upper()}] {self.station.station_code} - {self.contaminant_type}"


class SimulationTrigger(models.Model):
    """Records each time an alert causes the digital twin simulation to be triggered."""
    STATUS_CHOICES = [("pending","Pending"),("sent","Sent"),("failed","Failed"),("acknowledged","Acknowledged")]

    alert = models.ForeignKey(AlertEvent, on_delete=models.CASCADE, related_name="triggers")
    triggered_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    payload = models.JSONField(default=dict, help_text="Payload sent to the simulation engine")
    response_code = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    retry_count = models.IntegerField(default=0)

    class Meta:
        ordering = ["-triggered_at"]

    def __str__(self):
        return f"Trigger [{self.status}] for Alert {self.alert_id} @ {self.triggered_at}"
