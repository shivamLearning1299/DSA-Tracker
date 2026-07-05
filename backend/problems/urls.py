from rest_framework.routers import DefaultRouter

from .views import ProblemViewSet, SheetViewSet, StatsView, TopicViewSet

router = DefaultRouter()
router.register("problems", ProblemViewSet, basename="problem")
router.register("sheets", SheetViewSet, basename="sheet")
router.register("topics", TopicViewSet, basename="topic")
router.register("stats", StatsView, basename="stats")

urlpatterns = router.urls
