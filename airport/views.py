from django.db.models import Count, F
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
    TicketListSerializer,
    TicketRetrieveSerializer,
    AirplaneImageSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all airports",
        description="Show all airports that can be filtered by name and closest_big_city",
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                description="Filter by airport name",
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="closest_big_city",
                type=str,
                description="Filter by closest big city",
                location="query",
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Show detailed information about a specific airport"
    ),
    create=extend_schema(
        summary="Create a new airport",
    ),
    update=extend_schema(
        summary="Updates a specific airport completely",
    ),
    partial_update=extend_schema(summary="Updates a specific airport partly"),
    destroy=extend_schema(
        summary="Destroy a specific airport",
    ),
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


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all routes",
        description="Show all routes that can be filtered by source and destination",
        parameters=[
            OpenApiParameter(
                name="source",
                type=str,
                description="Filter by source",
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="destination",
                type=str,
                description="Filter by destination",
                location="query",
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(summary="Show detailed information about routes"),
    create=extend_schema(
        summary="Create a new route",
    ),
    update=extend_schema(summary="Updates a specific route completely"),
    partial_update=extend_schema(summary="Updates a specific route partly"),
    destroy=extend_schema(
        summary="Delete a specific route",
    ),
)
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


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all airplane types",
        description="Show all airplane types that can be filtered by name",
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                description="Filter by name",
                location="query",
                required=False,
            )
        ],
    ),
    retrieve=extend_schema(summary="Show detailed information about airplane type"),
    create=extend_schema(
        summary="Create a new airplane type",
    ),
    update=extend_schema(summary="Updates a specific airplane type completely"),
    partial_update=extend_schema(summary="Updates a specific airplane type partly"),
    destroy=extend_schema(
        summary="Delete a specific airplane type",
    ),
)
class AirplaneTypeViewSet(ModelViewSet):
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        queryset = AirplaneType.objects.all()

        if self.action == "list":
            name = self.request.query_params.get("name")

            if name:
                queryset = queryset.filter(name__icontains=name)

        return queryset


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all airplanes",
        description="Show all airplanes that can be filtered by name",
        parameters=[
            OpenApiParameter(
                name="name",
                type=str,
                description="Filter by name",
                location="query",
                required=False,
            )
        ],
    ),
    retrieve=extend_schema(summary="Show detailed information about airplane"),
    create=extend_schema(
        summary="Create a new airplane",
    ),
    update=extend_schema(summary="Updates a specific airplane completely"),
    partial_update=extend_schema(summary="Updates a specific airplane partly"),
    destroy=extend_schema(
        summary="Delete a specific airplane",
    ),
    upload_image=extend_schema(
        summary="Upload an image to existing airplane",
        request=AirplaneImageSerializer,
        responses={
            status.HTTP_200_OK: AirplaneImageSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                description="Invalid image format or file size exceeded"
            ),
            status.HTTP_404_NOT_FOUND: OpenApiResponse(
                description="Airplane not found"
            ),
        },
    ),
)
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
        elif self.action == "upload_image":
            return AirplaneImageSerializer

        return AirplaneSerializer

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, *args, **kwargs):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all crews",
        description="Show all crews that can be filtered by first name and last name",
        parameters=[
            OpenApiParameter(
                name="first_name",
                type=str,
                description="Filter by first name",
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="last_name",
                type=str,
                description="Filter by last name",
                location="query",
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(summary="Show detailed information about crew"),
    create=extend_schema(
        summary="Create a new crew",
    ),
    update=extend_schema(summary="Updates a specific crew completely"),
    partial_update=extend_schema(summary="Updates a specific crew partly"),
    destroy=extend_schema(
        summary="Delete a specific crew",
    ),
)
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


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all flights",
        description="Show all flights that can be filtered by its crews, airplane name, source and destination",
        parameters=[
            OpenApiParameter(
                name="crews",
                type=str,
                description="Filter by its crews",
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="airplane_name",
                type=str,
                description="Filter by airplane name",
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="source",
                type=str,
                description="Filter by source",
                location="query",
                required=False,
            ),
            OpenApiParameter(
                name="destination",
                type=str,
                description="Filter by destination",
                location="query",
                required=False,
            ),
        ],
    ),
    retrieve=extend_schema(summary="Show detailed information about flight"),
    create=extend_schema(
        summary="Create a new flight",
    ),
    update=extend_schema(summary="Updates a specific flight completely"),
    partial_update=extend_schema(summary="Updates a specific flight r"),
    destroy=extend_schema(
        summary="Delete a specific flight",
    ),
)
class FlightViewSet(ModelViewSet):
    @staticmethod
    def _str_to_int_list(line):
        try:
            return [int(x.strip()) for x in line.split(",")]
        except ValueError:
            return []

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


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all user's orders",
    ),
    retrieve=extend_schema(
        summary="Show detailed information about user's order",
    ),
    create=extend_schema(
        summary="Create a new order",
    ),
    destroy=extend_schema(
        summary="Delete an order",
    ),
)
class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.none()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        elif self.action == "retrieve":
            return OrderRetrieveSerializer

        return OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)

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


@extend_schema_view(
    list=extend_schema(
        summary="Show list of all user's tickets",
    ),
    retrieve=extend_schema(
        summary="Show detailed information about ticket",
    ),
)
class TicketViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Ticket.objects.none()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Ticket.objects.filter(order__user=self.request.user)

        if self.action == "list":
            queryset = queryset.select_related("flight__airplane")
        elif self.action == "retrieve":
            queryset = queryset.select_related(
                "flight__airplane__airplane_type",
                "flight__route__source",
                "flight__route__destination",
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        elif self.action == "retrieve":
            return TicketRetrieveSerializer

        return TicketSerializer
