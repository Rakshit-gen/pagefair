from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EngineerViewSet,
    FairnessCsvView,
    FairnessView,
    ImportIncidentsView,
    IncidentViewSet,
)

router = DefaultRouter()
router.register("engineers", EngineerViewSet)
router.register("incidents", IncidentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("fairness/", FairnessView.as_view()),
    path("fairness/export/", FairnessCsvView.as_view()),
    path("import/incidents/", ImportIncidentsView.as_view()),
]
