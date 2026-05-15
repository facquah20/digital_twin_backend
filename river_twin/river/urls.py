from rest_framework.routers import DefaultRouter
from .views import RiverSystemViewSet, CrossSectionViewSet, ContaminantSourceViewSet, MonitoringStationViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.urls import path

router = DefaultRouter()
router.register(r"river-systems", RiverSystemViewSet, basename="river-system")
router.register(r"cross-sections", CrossSectionViewSet, basename="cross-section")
router.register(r"contaminant-sources", ContaminantSourceViewSet, basename="contaminant-source")
router.register(r"monitoring-stations", MonitoringStationViewSet, basename="monitoring-station")

urlpatterns = router.urls + [
     # Schema engine
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger Interactive UI
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Redoc UI (Optional)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
