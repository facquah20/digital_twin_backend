from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ingest_reading, bulk_ingest, SensorReadingViewSet, AlertEventViewSet, SimulationTriggerViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

router = DefaultRouter()
router.register(r"readings", SensorReadingViewSet, basename="reading")
router.register(r"alerts", AlertEventViewSet, basename="alert")
router.register(r"triggers", SimulationTriggerViewSet, basename="trigger")

urlpatterns = [
    path("ingest/", ingest_reading, name="ingest-reading"),
    path("bulk-ingest/", bulk_ingest, name="bulk-ingest"),
] + router.urls + [
     # Schema engine
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger Interactive UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI (Optional)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
