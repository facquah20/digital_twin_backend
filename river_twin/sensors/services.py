"""
Core business logic:
  - process a raw sensor reading
  - evaluate thresholds and create AlertEvents
  - fire SimulationTrigger records (stub for your desktop app webhook)
"""
import logging
from django.utils import timezone
from .models import SensorReading, AlertEvent, SimulationTrigger
from river.models import MonitoringStation

logger = logging.getLogger(__name__)


THRESHOLD_MAP = [
    # (reading_field, station_threshold_field, alert_label, contaminant_key)
    ("heavy_metals_mgl", "alert_threshold_heavy_metals", "Heavy Metals", "heavy_metals"),
    ("organics_mgl",     "alert_threshold_organics",     "Organics",     "organics"),
    ("nutrients_mgl",    "alert_threshold_nutrients",     "Nutrients",    "nutrients"),
    ("pathogens_cfu",    "alert_threshold_pathogens",     "Pathogens",    "pathogens"),
]


def process_reading(reading: SensorReading) -> list[AlertEvent]:
    """
    Evaluate a SensorReading against station thresholds.
    Creates AlertEvent rows and SimulationTrigger rows for each breach.
    Returns list of created AlertEvents.
    """
    station = reading.station
    alerts_created = []

    for field, threshold_field, label, contaminant_key in THRESHOLD_MAP:
        value = getattr(reading, field, None)
        threshold = getattr(station, threshold_field, None)

        if value is None or threshold is None:
            continue

        if value > threshold:
            ratio = value / threshold
            if ratio >= 2.0:
                severity = "emergency"
            elif ratio >= 1.5:
                severity = "critical"
            else:
                severity = "warning"

            message = (
                f"{label} concentration at {station.name} ({station.station_code}) "
                f"is {value:.3f} (threshold: {threshold:.3f}, ratio: {ratio:.2f}x). "
                f"Severity: {severity.upper()}."
            )

            alert = AlertEvent.objects.create(
                reading=reading,
                station=station,
                contaminant_type=contaminant_key,
                measured_value=value,
                threshold_value=threshold,
                severity=severity,
                message=message,
            )
            alerts_created.append(alert)
            logger.warning("ALERT created: %s", message)

            # Fire simulation trigger
            _fire_simulation_trigger(alert, reading)

    # Update status on the reading
    if any(a.severity == "emergency" for a in alerts_created):
        reading.status = "critical"
    elif alerts_created:
        reading.status = "alert"
    else:
        reading.status = "ok"

    reading.is_processed = True
    reading.save(update_fields=["status", "is_processed"])

    # Update station last_reading_at
    station.last_reading_at = reading.received_at
    station.save(update_fields=["last_reading_at"])

    return alerts_created


def _fire_simulation_trigger(alert: AlertEvent, reading: SensorReading):
    """
    Build and record a trigger payload for the digital twin simulation engine.
    In production, replace the stub with an actual HTTP call to your desktop app's
    webhook endpoint.
    """
    payload = {
        "trigger_type": "contaminant_alert",
        "alert_id": alert.id,
        "severity": alert.severity,
        "station": {
            "code": alert.station.station_code,
            "name": alert.station.name,
            "km_location": alert.station.km_location,
            "role": alert.station.role,
        },
        "reading": {
            "id": reading.id,
            "sensor_timestamp": reading.sensor_timestamp.isoformat(),
            "heavy_metals_mgl": reading.heavy_metals_mgl,
            "organics_mgl": reading.organics_mgl,
            "nutrients_mgl": reading.nutrients_mgl,
            "pathogens_cfu": reading.pathogens_cfu,
            "ph": reading.ph,
            "dissolved_oxygen_mgl": reading.dissolved_oxygen_mgl,
            "temperature_c": reading.temperature_c,
            "flow_rate_m3s": reading.flow_rate_m3s,
        },
        "contaminant_type": alert.contaminant_type,
        "measured_value": alert.measured_value,
        "threshold_value": alert.threshold_value,
        "triggered_at": timezone.now().isoformat(),
    }

    trigger = SimulationTrigger.objects.create(
        alert=alert,
        payload=payload,
        status="pending",
    )

    # --- STUB: replace this block with your actual webhook call ---
    # import requests
    # try:
    #     resp = requests.post(
    #         settings.SIMULATION_ENGINE_WEBHOOK_URL,
    #         json=payload,
    #         timeout=5,
    #     )
    #     trigger.response_code = resp.status_code
    #     trigger.response_body = resp.text[:2000]
    #     trigger.status = "sent" if resp.ok else "failed"
    # except Exception as exc:
    #     trigger.status = "failed"
    #     trigger.response_body = str(exc)
    # trigger.save()
    # --- END STUB ---

    # For now mark as sent (simulation engine integration pending)
    trigger.status = "sent"
    trigger.save(update_fields=["status"])

    logger.info("SimulationTrigger %d fired for alert %d", trigger.id, alert.id)
    return trigger
