import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone, dateformat, html

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
from core.test_case_authorized import AuthenticatedTestCase


class AirportAdminTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.airport = Airport.objects.create(
            name="test_name", closest_big_city="test_city"
        )

    def test_display_airport(self):
        url = reverse("admin:airport_airport_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.airport.name)
        self.assertContains(response, self.airport.closest_big_city)


class RouteAdminTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.airport_1 = Airport.objects.create(
            name="test_name1", closest_big_city="test_city1"
        )
        self.airport_2 = Airport.objects.create(
            name="test_name2", closest_big_city="test_city2"
        )
        self.route = Route.objects.create(
            source=self.airport_1, destination=self.airport_2, distance=10
        )

    def test_display_route(self):
        url = reverse("admin:airport_route_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.route.source.name)
        self.assertContains(response, self.route.destination.name)
        self.assertContains(response, self.route.distance)


class AirplaneTypeAdminTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.airplane_type = AirplaneType.objects.create(name="test")

    def test_display_airplane_type(self):
        url = reverse("admin:airport_airplanetype_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.airplane_type.name)


class AirplaneAdminTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.airplane_type = AirplaneType.objects.create(name="test")
        self.airplane = Airplane.objects.create(
            name="test", rows=10, seats_in_row=10, airplane_type=self.airplane_type
        )

    def test_display_airplane(self):
        url = reverse("admin:airport_airplane_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.airplane.name)
        self.assertContains(response, self.airplane.rows)
        self.assertContains(response, self.airplane.seats_in_row)
        self.assertContains(response, self.airplane.airplane_type.name)
        self.assertContains(response, self.airplane.seats)


class CrewAdminTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")

    def test_display_crew(self):
        url = reverse("admin:airport_crew_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.crew.first_name)
        self.assertContains(response, self.crew.last_name)


class FlightAdminTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.airport_1 = Airport.objects.create(
            name="test_name1", closest_big_city="test_city1"
        )
        self.airport_2 = Airport.objects.create(
            name="test_name2", closest_big_city="test_city2"
        )
        self.route = Route.objects.create(
            source=self.airport_1, destination=self.airport_2, distance=10
        )
        self.airplane = Airplane.objects.create(name="test", rows=10, seats_in_row=10)
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + datetime.timedelta(days=1),
        )

    def test_display_flight(self):
        url = reverse("admin:airport_flight_changelist")
        response = self.client.get(url)

        self.assertContains(response, html.escape(str(self.flight)))
        self.assertContains(response, str(self.airplane))
        self.assertContains(
            response, dateformat.format(self.flight.departure_time, "N j, Y, g:i a")
        )


class OrderAdminTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password=""
        )
        self.order = Order.objects.create(
            user=self.user,
        )

    def test_display_order(self):
        url = reverse("admin:airport_order_changelist")
        response = self.client.get(url)

        self.assertContains(
            response, dateformat.format(self.order.created_at, "N j, Y, g:i a")
        )
        self.assertContains(response, str(self.user))


class TicketAdminTest(AuthenticatedTestCase):
    def setUp(self):
        super().setUp()
        self.airport_1 = Airport.objects.create(
            name="test_name1", closest_big_city="test_city1"
        )
        self.airport_2 = Airport.objects.create(
            name="test_name2", closest_big_city="test_city2"
        )
        self.route = Route.objects.create(
            source=self.airport_1, destination=self.airport_2, distance=10
        )
        self.airplane = Airplane.objects.create(
            name="test",
            rows=10,
            seats_in_row=10,
        )
        self.flight = Flight.objects.create(
            route=self.route,
            airplane=self.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + datetime.timedelta(days=1),
        )
        self.order = Order.objects.create(
            user=get_user_model().objects.create_user(
                email="test@example.com", password=""
            )
        )
        self.ticket = Ticket.objects.create(
            row=1, seat=1, flight=self.flight, order=self.order
        )

    def test_display_ticket(self):
        url = reverse("admin:airport_ticket_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.ticket.row)
        self.assertContains(response, self.ticket.seat)
        self.assertContains(response, html.escape(str(self.ticket.flight)))
        self.assertContains(response, self.ticket.order.id)


class GroupAbsence(AuthenticatedTestCase):
    def test_no_display_group(self):
        url = reverse("admin:index")
        response = self.client.get(url)

        self.assertNotContains(response, "Groups")
