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
    serializer_class = RouteSerializer
    queryset = Route.objects.all()


class AirplaneTypeViewSet(ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()


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
