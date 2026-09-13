import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

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


class ModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.airport_1 = Airport.objects.create(
            name="test_name1", closest_big_city="test_city1"
        )
        cls.airport_2 = Airport.objects.create(
            name="test_name2", closest_big_city="test_city2"
        )
        cls.route = Route.objects.create(
            source=cls.airport_1, destination=cls.airport_2, distance=10
        )
        cls.airplane_type = AirplaneType.objects.create(name="test")
        cls.airplane = Airplane.objects.create(
            name="test", rows=10, seats_in_row=10, airplane_type=cls.airplane_type
        )
        cls.crew = Crew.objects.create(first_name="John", last_name="Doe")
        cls.flight = Flight.objects.create(
            route=cls.route,
            airplane=cls.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + datetime.timedelta(days=1),
        )
        cls.order = Order.objects.create(
            user=get_user_model().objects.create_user(
                email="test@example.com", password=""
            )
        )
        cls.ticket = Ticket.objects.create(
            row=1, seat=1, flight=cls.flight, order=cls.order
        )

    def test_airport_str(self):
        self.assertEqual(
            str(self.airport_1),
            f"{self.airport_1.name} ({self.airport_1.closest_big_city})",
        )

    def test_route_str(self):
        self.assertEqual(
            str(self.route),
            f"{self.route.source.name} -> {self.route.destination.name}",
        )

    def test_airplane_type_str(self):
        self.assertEqual(str(self.airplane_type), self.airplane_type.name)

    def test_airplane(self):
        self.assertEqual(str(self.airplane), self.airplane.name)

    def test_crew_str(self):
        self.assertEqual(
            str(self.crew), f"{self.crew.first_name} {self.crew.last_name}"
        )

    def test_flight_str(self):
        self.assertEqual(
            str(self.flight), f"{self.flight.route} - {self.flight.airplane}"
        )

    def test_order_str(self):
        self.assertEqual(str(self.order), str(self.order.id))

    def test_ticket_str(self):
        self.assertEqual(str(self.ticket), f"{self.ticket.row}-{self.ticket.seat}")

    def test_property_in_airplane(self):
        self.assertEqual(
            self.airplane.seats, self.airplane.rows * self.airplane.seats_in_row
        )

    def test_custom_validation_in_tickets(self):
        with self.assertRaises(ValidationError):
            Ticket.objects.create(row=-1, seat=-1, flight=self.flight, order=self.order)

    def test_ticket_constraint(self):
        with self.assertRaises(ValidationError):
            Ticket.objects.create(row=1, seat=1, flight=self.flight, order=self.order)

    def test_route_constraint(self):
        with self.assertRaises((IntegrityError, ValidationError)):
            Route.objects.create(
                source=self.airport_1, destination=self.airport_2, distance=11
            )

    def test_route_source_destination_validation(self):
        with self.assertRaises(ValidationError):
            Route.objects.create(source=self.airport_1, destination=self.airport_1, distance=12)


    def test_airplane_type_constraint(self):
        with self.assertRaises(IntegrityError):
            AirplaneType.objects.create(name="test")
