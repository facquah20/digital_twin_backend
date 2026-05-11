from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ingest_reading, bulk_ingest, SensorReadingViewSet, AlertEventViewSet, SimulationTriggerViewSet

router = DefaultRouter()
router.register(r"readings", SensorReadingViewSet, basename="reading")
router.register(r"alerts", AlertEventViewSet, basename="alert")
router.register(r"triggers", SimulationTriggerViewSet, basename="trigger")

urlpatterns = [
    path("ingest/", ingest_reading, name="ingest-reading"),
    path("bulk-ingest/", bulk_ingest, name="bulk-ingest"),
] + router.urls
