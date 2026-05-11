from rest_framework.routers import DefaultRouter
from .views import RiverSystemViewSet, CrossSectionViewSet, ContaminantSourceViewSet, MonitoringStationViewSet

router = DefaultRouter()
router.register(r"river-systems", RiverSystemViewSet, basename="river-system")
router.register(r"cross-sections", CrossSectionViewSet, basename="cross-section")
router.register(r"contaminant-sources", ContaminantSourceViewSet, basename="contaminant-source")
router.register(r"monitoring-stations", MonitoringStationViewSet, basename="monitoring-station")

urlpatterns = router.urls
