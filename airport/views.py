from django.db.models import Count, F
from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from airport.models import (
    Airport,
    Route,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
    AirplaneType,
)
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    AirplaneSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
    AirplaneTypeSerializer,
    RouteListRetrieveSerializer,
    AirplaneListRetrieveSerializer,
    FlightListSerializer,
    FlightRetrieveSerializer,
    OrderListSerializer,
    OrderRetrieveSerializer,
)


class AirportViewSet(ModelViewSet):
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = Airport.objects.all()
        if self.action == "list":
            name = self.request.query_params.get("name")
            closest_big_city = self.request.query_params.get("closest_big_city")

            if name:
                queryset = queryset.filter(name__icontains=name)

            if closest_big_city:
                queryset = queryset.filter(closest_big_city__icontains=closest_big_city)

        return queryset


class RouteViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = Route.objects.all()
        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("source", "destination")

            if self.action == "list":
                source = self.request.query_params.get("source")
                destination = self.request.query_params.get("destination")

                if source:
                    queryset = queryset.filter(source__name__icontains=source)

                if destination:
                    queryset = queryset.filter(destination__name__icontains=destination)

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return RouteListRetrieveSerializer

        return RouteSerializer


class AirplaneTypeViewSet(ModelViewSet):
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        queryset = AirplaneType.objects.all()

        if self.action == "list":
            name = self.request.query_params.get("name")

            if name:
                queryset = queryset.filter(name__icontains=name)

        return queryset


class AirplaneViewSet(ModelViewSet):
    def get_queryset(self):
        queryset = Airplane.objects.all()

        if self.action in ("list", "retrieve"):
            queryset = queryset.select_related("airplane_type")

            if self.action == "list":
                name = self.request.query_params.get("name")

                if name:
                    queryset = queryset.filter(name__icontains=name)

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return AirplaneListRetrieveSerializer

        return AirplaneSerializer


class CrewViewSet(ModelViewSet):
    serializer_class = CrewSerializer

    def get_queryset(self):
        queryset = Crew.objects.all()
        if self.action == "list":
            first_name = self.request.query_params.get("first_name")
            last_name = self.request.query_params.get("last_name")

            if first_name:
                queryset = queryset.filter(first_name__icontains=first_name)

            if last_name:
                queryset = queryset.filter(last_name__icontains=last_name)

        return queryset


class FlightViewSet(ModelViewSet):
    @staticmethod
    def _str_to_int_list(line):
        return [int(x) for x in line.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        elif self.action == "retrieve":
            return FlightRetrieveSerializer
        return FlightSerializer

    def get_queryset(self):
        queryset = Flight.objects.all()

        if self.action in ("list", "retrieve"):
            queryset = queryset.annotate(
                tickets_available=F("airplane__seats_in_row") * F("airplane__rows")
                - Count("tickets")
            )

            queryset = queryset.select_related(
                "route__source", "route__destination", "airplane__airplane_type"
            ).prefetch_related("crews")

            if self.action == "list":
                crews = self.request.query_params.get("crews")
                airplane_name = self.request.query_params.get("airplane_name")
                source = self.request.query_params.get("source")
                destination = self.request.query_params.get("destination")

                if crews:
                    crews = self._str_to_int_list(crews)
                    queryset = queryset.filter(crews__in=crews)

                if airplane_name:
                    queryset = queryset.filter(airplane__name__icontains=airplane_name)

                if source:
                    queryset = queryset.filter(route__source__name__icontains=source)

                if destination:
                    queryset = queryset.filter(
                        route__destination__name__icontains=destination
                    )

                queryset = queryset.distinct()

        return queryset


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderRetrieveSerializer

        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()

        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__flight__airplane")
        elif self.action == "retrieve":
            queryset = queryset.prefetch_related(
                "tickets__flight__airplane__airplane_type",
                "tickets__flight__route__source",
                "tickets__flight__route__destination",
                "tickets__flight__crews",
            )

        return queryset


class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()
