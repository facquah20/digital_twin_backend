# River Digital Twin — Django Backend

A production-ready REST API backend for the River Digital Twin water-quality monitoring system.

---

## Quick Start

```bash
# 1. Install dependencies
pip install django djangorestframework django-cors-headers

# 2. Apply migrations
python manage.py migrate

# 3. Seed with the default river configuration
python manage.py shell < seed_data.py

# 4. Create an admin user (optional)
python manage.py createsuperuser

# 5. Run the development server
python manage.py runserver
```

# 6. How to visit the swagger documentation
Navigate to http://localhost:8000/api/docs
---

## Architecture

```
river_twin/          ← Django project root
├── river/           ← River geometry & configuration app
│   ├── models.py    ← RiverSystem, CrossSection, ContaminantSource, MonitoringStation
│   ├── serializers.py
│   ├── views.py     ← CRUD ViewSets
│   └── admin.py
├── sensors/         ← Sensor ingest & alerting app
│   ├── models.py    ← SensorReading, AlertEvent, SimulationTrigger
│   ├── serializers.py
│   ├── views.py     ← Ingest endpoints + Dashboard
│   ├── services.py  ← Threshold evaluation & simulation trigger logic
│   └── admin.py
└── seed_data.py     ← Pre-loads the 5 sources + 6 stations from spec
```

---

## API Reference

### River Configuration  `GET /api/river/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/river/river-systems/` | List or create river systems |
| GET/PUT/PATCH/DELETE | `/api/river/river-systems/{id}/` | Manage a river system |
| GET | `/api/river/river-systems/{id}/summary/` | Full system detail (nested) |
| POST | `/api/river/river-systems/{id}/toggle_active/` | Enable/disable river |
| GET/POST | `/api/river/contaminant-sources/` | Manage contaminant sources |
| POST | `/api/river/contaminant-sources/{id}/toggle_active/` | Enable/disable source |
| GET/POST | `/api/river/monitoring-stations/` | Manage monitoring stations |
| GET/POST | `/api/river/cross-sections/` | Manage bathymetry cross-sections |

### Sensor Ingest  `POST /api/sensors/`

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/api/sensors/ingest/` | **Primary ingest — single reading from a workstation** |
| **POST** | `/api/sensors/bulk-ingest/` | Batch ingest — array of readings |
| GET | `/api/sensors/readings/` | Browse all readings (filterable) |
| GET | `/api/sensors/readings/latest/` | Latest reading per station |
| GET | `/api/sensors/readings/dashboard/` | Aggregated monitoring dashboard |
| GET | `/api/sensors/alerts/` | Browse alert events |
| POST | `/api/sensors/alerts/{id}/acknowledge/` | Acknowledge a single alert |
| POST | `/api/sensors/alerts/acknowledge_bulk/` | Acknowledge multiple alerts |
| GET | `/api/sensors/triggers/` | Browse simulation triggers |

---

## Sensor Ingest Payload

Workstations POST to `POST /api/sensors/ingest/`:

```json
{
  "station_code": "STN-02",
  "sensor_timestamp": "2025-05-10T14:30:00Z",
  "device_id": "WS-FIELD-04",
  "firmware_version": "2.1.3",
  "battery_level_pct": 87.5,
  "heavy_metals_mgl": 0.31,
  "organics_mgl": 0.08,
  "nutrients_mgl": 0.12,
  "pathogens_cfu": 1200.0,
  "ph": 7.2,
  "dissolved_oxygen_mgl": 8.4,
  "temperature_c": 18.5,
  "turbidity_ntu": 3.2,
  "flow_rate_m3s": 11.8
}
```

Response:
```json
{
  "reading_id": 42,
  "station_code": "STN-02",
  "status": "alert",
  "alerts_triggered": 1,
  "alerts": [
    { "id": 7, "contaminant": "heavy_metals", "severity": "critical" }
  ],
  "received_at": "2025-05-10T14:30:01.234Z"
}
```

---

## Alert Severity Logic

| Ratio (measured / threshold) | Severity |
|------------------------------|----------|
| 1.0 – 1.49× | `warning` |
| 1.5 – 1.99× | `critical` |
| ≥ 2.0× | `emergency` |

---

## Simulation Trigger Integration

Every `AlertEvent` automatically creates a `SimulationTrigger` record with the full context payload.
To wire it to your desktop application, edit `sensors/services.py` -> `_fire_simulation_trigger()`:

```python
import requests
resp = requests.post(
    settings.SIMULATION_ENGINE_WEBHOOK_URL,   # set in settings.py
    json=payload,
    timeout=5,
)
```

---

## Pre-loaded River Data

| Item | Count |
|------|-------|
| River Systems | 1 (River Alpha) |
| Cross-sections | 7 |
| Contaminant Sources | 5 (Factory A, Chem Spill, Agri Runoff, Sewage, Mining) |
| Monitoring Stations | 6 (STN-01 … STN-06) |

---

## Admin Interface

Visit `http://localhost:8000/admin/` — all models are registered with inline editing.
