from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    FlightViewSet,
    RouteViewSet,
    CrewViewSet,
    AirplaneTypeViewSet,
    OrderViewSet,
    TicketViewSet, AirplaneViewSet,
)

airport_router = routers.DefaultRouter()

airport_router.register("airports", AirportViewSet, basename="airport")
airport_router.register("routes", RouteViewSet, basename="route")
airport_router.register("airplane-types", AirplaneTypeViewSet, basename="airplane-type")
airport_router.register("airplane", AirplaneViewSet, basename="airplane")
airport_router.register("crews", CrewViewSet)
airport_router.register("flights", FlightViewSet, basename="flight")
airport_router.register("orders", OrderViewSet, basename="order")
airport_router.register("tickets", TicketViewSet, basename="ticket")

urlpatterns = [
    path("", include(airport_router.urls)),
]

app_name = "airport"
