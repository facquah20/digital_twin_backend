"""
Run with: python manage.py shell < seed_data.py
Seeds the database with the river system from the spec.
"""
import django, os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "river_twin.settings")
django.setup()

from river.models import RiverSystem, ContaminantSource, MonitoringStation, CrossSection

# Remove existing
RiverSystem.objects.all().delete()

river = RiverSystem.objects.create(
    name="River Alpha – Digital Twin",
    description="Primary monitoring river with 5 contaminant sources and 6 monitoring stations.",
    total_length_km=2.0,
    base_flow_rate=12.5,
    sinuosity_index=1.35,
)

# Cross-sections (pools and riffles along the reach)
sections = [
    (0.0,  "riffle", 18.0, 0.4, 1.5, 0.0,  0.012, -0.4),
    (0.3,  "pool",   22.0, 1.8, 2.0, 0.5,  0.037, -1.8),
    (0.6,  "run",    20.0, 0.9, 1.8, 0.2,  0.020, -0.9),
    (0.9,  "pool",   24.0, 2.1, 2.2, -0.3, 0.036, -2.1),
    (1.2,  "riffle", 16.0, 0.3, 1.4, 0.1,  0.009, -0.3),
    (1.5,  "pool",   21.0, 1.6, 2.0, 0.4,  0.033, -1.6),
    (1.8,  "run",    19.0, 0.8, 1.7, 0.0,  0.018, -0.8),
]
for km, stype, w, d, bh, toff, a, b in sections:
    CrossSection.objects.create(
        river=river, km_marker=km, section_type=stype,
        width_m=w, max_depth_m=d, bank_height_m=bh,
        thalweg_offset_m=toff, parabola_a=a, parabola_b=b,
    )

# Contaminant sources
sources = [
    ("Industrial Effluent (Factory A)", "Factory A",  "heavy_metals", 0.48, 8.5,  0.15, "pulsed",  6.0, 2.0, 0.8),
    ("Chemical Spill",                  "Chem Spill",  "organic",      0.65, 12.0, 0.40, "batch",   None, None, 0.5),
    ("Agricultural Runoff",             "Agri Runoff", "nutrients",    0.85, 5.5,  0.05, "continuous", None, None, 2.2),
    ("Sewage Overflow",                 "Sewage OVF",  "pathogens",    1.10, 1e6,  0.80, "pulsed",  4.0, 8.0, 0.3),
    ("Mining Leachate",                 "Mine Leach",  "heavy_metals", 1.40, 15.0, 0.10, "continuous", None, None, 1.1),
]
for name, label, ctype, km, peak, decay, mode, on, off, flow in sources:
    ContaminantSource.objects.create(
        river=river, name=name, source_label=label, contaminant_type=ctype,
        km_location=km, peak_concentration=peak, decay_rate=decay,
        discharge_mode=mode, pulse_on_hours=on, pulse_off_hours=off,
        flow_rate_m3s=flow, plume_sigma_x=5.0, plume_sigma_y=2.0,
    )

# Monitoring stations
stations = [
    ("STN-01", "Upstream Reference",      "upstream_reference", 0.10,  0.05,  0.04,  0.03,  1000.0),
    ("STN-02", "Industrial Outfall Zone", "industrial_outfall",  0.55,  0.20,  0.15,  0.10,  5000.0),
    ("STN-03", "Agricultural Buffer Zone","agricultural_buffer", 0.90,  0.12,  0.10,  0.30,  2000.0),
    ("STN-04", "Municipal Water Intake",  "municipal_intake",    1.15,  0.05,  0.03,  0.02,  500.0),
    ("STN-05", "Wetland Buffer",          "wetland_buffer",      1.35,  0.08,  0.06,  0.05,  1500.0),
    ("STN-06", "Downstream Gauge",        "downstream_gauge",    1.90,  0.15,  0.10,  0.08,  3000.0),
]
for code, name, role, km, t_hm, t_org, t_nut, t_path in stations:
    MonitoringStation.objects.create(
        river=river, station_code=code, name=name, role=role, km_location=km,
        alert_threshold_heavy_metals=t_hm, alert_threshold_organics=t_org,
        alert_threshold_nutrients=t_nut, alert_threshold_pathogens=t_path,
    )

print(f"✅ Seeded river: {river.name}")
print(f"   Cross-sections : {CrossSection.objects.filter(river=river).count()}")
print(f"   Contaminant sources: {ContaminantSource.objects.filter(river=river).count()}")
print(f"   Monitoring stations: {MonitoringStation.objects.filter(river=river).count()}")
