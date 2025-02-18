from django.urls import path, include
from rest_framework import routers
from station.views import (CrewViewSet,
                           StationViewSet,
                           RouteViewSet,
                           TrainTypeViewSet,
                           TrainViewSet,
                           OrderViewSet,
                           JourneyViewSet)

router = routers.DefaultRouter()
router.register("crew", CrewViewSet)
router.register("station", StationViewSet)
router.register("route", RouteViewSet)
router.register("train_type", TrainTypeViewSet)
router.register("train", TrainViewSet)
router.register("order", OrderViewSet)
router.register("journey", JourneyViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "station"
