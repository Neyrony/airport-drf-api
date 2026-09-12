from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
)
from airport.validators import validate_source_destination, validate_date


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_city",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "distance",
        )

    def validate(self, data):
        source = data.get("source", getattr(self.instance, "source", None))
        destination = data.get(
            "destination", getattr(self.instance, "destination", None)
        )

        if source and destination:
            validate_source_destination(source.id, destination.id, ValidationError)

        return data


class RouteListRetrieveSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type", "seats")


class AirplaneListRetrieveSerializer(AirplaneSerializer):
    airplane_type = serializers.StringRelatedField()


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")

    @staticmethod
    def get_full_name(obj):
        return f"{obj.first_name} {obj.last_name}"


class CrewFlightListSerializer(CrewSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "full_name",
        )


class CrewFlightRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class FlightSerializer(serializers.ModelSerializer):
    route = serializers.PrimaryKeyRelatedField(
        queryset=Route.objects.select_related("source", "destination")
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crews",
        )
        extra_kwargs = {
            "crews": {"style": {"base_template": "checkbox_multiple.html"}},
        }

    def validate(self, data):
        departure_time = data.get(
            "departure_time", getattr(self.instance, "departure_time", None)
        )
        arrival_time = data.get(
            "arrival_time", getattr(self.instance, "arrival_time", None)
        )

        if departure_time and arrival_time:
            validate_date(departure_time, arrival_time, ValidationError)

        return data


class FlightListSerializer(FlightSerializer):
    tickets_available = serializers.IntegerField(read_only=True)
    crews = CrewFlightListSerializer(many=True, read_only=True)
    airplane = AirplaneListRetrieveSerializer(read_only=True)
    route = RouteListRetrieveSerializer(read_only=True)

    class Meta:
        model = FlightSerializer.Meta.model
        fields = FlightSerializer.Meta.fields + ("tickets_available",)

        extra_kwargs = {
            "departure_time": {"format": "%d.%m.%Y %H:%M"},
            "arrival_time": {"format": "%d.%m.%Y %H:%M"},
        }


class FlightRetrieveSerializer(FlightSerializer):
    crews = CrewFlightRetrieveSerializer(many=True, read_only=True)
    airplane = AirplaneListRetrieveSerializer(read_only=True)
    route = RouteListRetrieveSerializer(read_only=True)

    class Meta:
        model = FlightSerializer.Meta.model
        fields = FlightSerializer.Meta.fields
        extra_kwargs = {
            "departure_time": {"format": "%d.%m.%Y %H:%M"},
            "arrival_time": {"format": "%d.%m.%Y %H:%M"},
        }


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "row",
            "seat",
            "flight",
        )


class TicketListSerializer(serializers.ModelSerializer):
    airplane_name = serializers.CharField(read_only=True, source="flight.airplane.name")
    departure_time = serializers.DateTimeField(
        read_only=True, source="flight.departure_time", format="%d.%m.%Y %H:%M"
    )
    arrival_time = serializers.DateTimeField(
        read_only=True, source="flight.arrival_time", format="%d.%m.%Y %H:%M"
    )

    class Meta:
        model = Ticket
        fields = (
            "row",
            "seat",
            "airplane_name",
            "departure_time",
            "arrival_time",
        )


class TicketRetrieveSerializer(TicketSerializer):
    flight = FlightRetrieveSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "created_at", "tickets")

    @transaction.atomic
    def create(self, validated_data):
        tickets = validated_data.pop("tickets")

        order = Order.objects.create(**validated_data)
        for ticket in tickets:
            Ticket.objects.create(order=order, **ticket)

        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderRetrieveSerializer(OrderSerializer):
    tickets = TicketRetrieveSerializer(many=True, read_only=True)
