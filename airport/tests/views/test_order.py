import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Order, Flight, Airport, Route, Airplane
from airport.serializers import (
    OrderListSerializer,
    OrderRetrieveSerializer,
    OrderSerializer,
)

URL = reverse("airport:order-list")


def get_detail_url(pk):
    return reverse("airport:order-detail", kwargs={"pk": pk})


class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.regular_user = get_user_model().objects.create_user(
            email="test@example.com",
            password="test12345",
        )
        cls.order = Order.objects.create(user=cls.regular_user)
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


class UnauthorizedTest(BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_details_page(self):
        url = get_detail_url(self.order.pk)

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
            email="user@user.com", password="qwerty12345"
        )
        cls.current_user_order = Order.objects.create(user=cls.user)

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "tickets": [
                {"seat": 1, "row": 1, "flight": self.flight.pk},
            ]
        }

        response = self.client.post(URL, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_details_page(self):
        url = get_detail_url(self.current_user_order.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list(self):
        response = self.client.get(URL)

        another_users_order_serializer = OrderListSerializer(self.order)
        users_order_serializer = OrderListSerializer(self.current_user_order)

        self.assertIn(users_order_serializer.data, response.data["results"])
        self.assertNotIn(another_users_order_serializer.data, response.data["results"])

    def test_retrieve(self):
        url = get_detail_url(self.current_user_order.pk)

        response = self.client.get(url)

        order_serializer = OrderRetrieveSerializer(self.current_user_order)

        self.assertEqual(response.data, order_serializer.data)

        self.client.force_authenticate(user=self.regular_user)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AdminTest(BaseTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = get_user_model().objects.create_user(
            email="admin@admin.com", password="qwerty12345", is_staff=True
        )
        cls.current_user_order = Order.objects.create(user=cls.user)

    def setUp(self):
        super().setUp()
        self.client.force_authenticate(user=self.user)

    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = {
            "tickets": [
                {"seat": 1, "row": 1, "flight": self.flight.pk},
            ]
        }

        response = self.client.post(URL, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_details_page(self):
        url = get_detail_url(self.current_user_order.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.patch(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create(self):
        flight = self.flight
        data = {"tickets": [{"row": 1, "seat": 1, "flight": flight.id}]}
        response = self.client.post(URL, data=data, format="json")

        order = Order.objects.get(id=response.data["id"])
        order_serializer = OrderSerializer(order)

        self.assertEqual(order_serializer.data, response.data)

    def test_create_validation(self):
        flight = self.flight
        data = {"tickets": [{"row": -1, "seat": 1000, "flight": flight.id}]}
        response = self.client.post(URL, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete(self):
        url = get_detail_url(self.current_user_order.pk)

        self.client.delete(url)

        with self.assertRaises(Order.DoesNotExist):
            self.current_user_order.refresh_from_db()
