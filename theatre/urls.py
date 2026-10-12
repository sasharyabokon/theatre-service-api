from django.urls import path, include
from rest_framework import routers
from rest_framework.routers import DefaultRouter

from theatre.views import TicketViewSet, GenreViewSet, ActorViewSet, PlayViewSet, PerformanceViewSet, \
    TheatreHallViewSet, ReservationViewSet

router = routers.DefaultRouter()
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("plays", PlayViewSet)
router.register("theatre_halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservations", ReservationViewSet)
router.register("tickets", TicketViewSet)

app_name = "theatre"

urlpatterns = [
    path("", include(router.urls)),
]