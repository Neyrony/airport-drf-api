import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Ticket, Order, Airport, Route, Flight, Airplane
from airport.serializers import TicketListSerializer, TicketRetrieveSerializer

URL = reverse("airport:ticket-list")


def get_detail_url(pk):
    return reverse("airport:ticket-detail", kwargs={"pk": pk})


class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.regular_user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test12345",
        )
        order = Order.objects.create(user=cls.regular_user)
        airport_1 = Airport.objects.create(
            name="test_name1", closest_big_city="test_city1"
        )
        airport_2 = Airport.objects.create(
            name="test_name2", closest_big_city="test_city2"
        )
        route = Route.objects.create(
            source=airport_1, destination=airport_2, distance=10
        )
        airplane = Airplane.objects.create(name="test", rows=10, seats_in_row=10)
        cls.flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + datetime.timedelta(days=1),
        )
        cls.regular_user_ticket = Ticket.objects.create(
            row=10,
            seat=10,
            flight=cls.flight,
            order=order,
        )


class UnauthorizedTest(BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_details_page(self):
        url = get_detail_url(self.regular_user_ticket.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserTest(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="12345",
        )
        new_order = Order.objects.create(user=cls.user)
        cls.user_ticket = Ticket.objects.create(
            row=9, seat=9, order=new_order, flight=cls.flight
        )

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_access_details_page(self):
        url = get_detail_url(self.user_ticket.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list(self):
        response = self.client.get(URL)

        all_users_tickets = Ticket.objects.filter(order__user=self.user)
        user_tickets_serializer = TicketListSerializer(all_users_tickets, many=True)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"], user_tickets_serializer.data)

    def test_retrieve(self):
        url = get_detail_url(self.user_ticket.pk)

        response = self.client.get(url)

        ticket_serializer = TicketRetrieveSerializer(self.user_ticket)

        self.assertEqual(response.data, ticket_serializer.data)

        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminTest(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="12345",
            is_staff=True,
        )
        new_order = Order.objects.create(user=cls.user)
        cls.user_ticket = Ticket.objects.create(
            row=9, seat=9, order=new_order, flight=cls.flight
        )

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_access_details_page(self):
        url = get_detail_url(self.user_ticket.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
