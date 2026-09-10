from rest_framework.viewsets import ModelViewSet

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
    serializer_class = AirplaneSerializer
    queryset = Airplane.objects.all()


class CrewViewSet(ModelViewSet):
    serializer_class = CrewSerializer
    queryset = Crew.objects.all()


class FlightViewSet(ModelViewSet):
    serializer_class = FlightSerializer
    queryset = Flight.objects.all()


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()


class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.all()
