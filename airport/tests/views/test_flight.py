import datetime

from django.db.models import Count, F
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Flight, Crew, Airport, Route, Airplane
from airport.serializers import FlightListSerializer, FlightRetrieveSerializer
from core.test_case_authorized import UserAPITestCase, AdminAPITestCase

URL = reverse("airport:flight-list")


def get_detail_url(pk):
    return reverse("airport:flight-detail", kwargs={"pk": pk})


def get_data():
    airport_1_1 = Airport.objects.create(
        name="test_name1_1", closest_big_city="test_city1_1"
    )
    airport_2_1 = Airport.objects.create(
        name="test_name2_1", closest_big_city="test_city2_1"
    )
    route_2 = Route.objects.create(
        source=airport_1_1, destination=airport_2_1, distance=10
    )
    airplane = Airplane.objects.create(name="test2", rows=10, seats_in_row=10)
    crew = Crew.objects.create(first_name="John", last_name="Clay")
    return {
        "departure_time": timezone.now(),
        "arrival_time": timezone.now() + datetime.timedelta(days=1),
        "route": route_2.pk,
        "airplane": airplane.pk,
        "crews": [crew.pk],
    }


class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airport_1 = Airport.objects.create(
            name="test_name1", closest_big_city="test_city1"
        )
        cls.airport_2 = Airport.objects.create(
            name="test_name2", closest_big_city="test_city2"
        )
        cls.route = Route.objects.create(
            source=cls.airport_1, destination=cls.airport_2, distance=10
        )
        cls.airplane = Airplane.objects.create(name="test", rows=10, seats_in_row=10)
        cls.flight = Flight.objects.create(
            route=cls.route,
            airplane=cls.airplane,
            departure_time=timezone.now(),
            arrival_time=timezone.now() + datetime.timedelta(days=1),
        )


class UnauthorizedTest(BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_details_page(self):
        data = get_data()
        url = get_detail_url(self.flight.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(
            url,
            data={"arrival_time": data["arrival_time"] + datetime.timedelta(days=1)},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserTest(UserAPITestCase, BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_access_details_page(self):
        data = get_data()
        url = get_detail_url(self.flight.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(
            url,
            data={"arrival_time": data["arrival_time"] + datetime.timedelta(days=1)},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list(self):
        response = self.client.get(URL)

        all_flights = Flight.objects.annotate(
            tickets_available=F("airplane__seats_in_row") * F("airplane__rows")
            - Count("tickets")
        )
        flight_serializer = FlightListSerializer(all_flights, many=True)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"], flight_serializer.data)

    def test_list_filter(self):
        data = get_data()
        route_id = data.pop("route")
        airplane_id = data.pop("airplane")
        crew_ids = data.pop("crews")

        self.flight2 = Flight.objects.create(
            **data, route_id=route_id, airplane_id=airplane_id
        )
        self.flight2.crews.add(*crew_ids)

        self.flight2_queryset = Flight.objects.filter(id=self.flight2.pk).annotate(
            tickets_available=F("airplane__seats_in_row") * F("airplane__rows")
            - Count("tickets")
        )

        flight2_serializer = FlightListSerializer(self.flight2_queryset, many=True)
        response = self.client.get(URL, {"crews": f"{crew_ids[0]}"})

        self.assertEqual(response.data["results"], flight2_serializer.data)

        response = self.client.get(URL, {"airplane_name": self.flight2.airplane.name})

        self.assertEqual(response.data["results"], flight2_serializer.data)

        response = self.client.get(URL, {"source": self.flight2.route.source.name})

        self.assertEqual(response.data["results"], flight2_serializer.data)

        response = self.client.get(
            URL, {"destination": self.flight2.route.destination.name}
        )

        self.assertEqual(response.data["results"], flight2_serializer.data)

    def test_retrieve(self):
        url = get_detail_url(self.flight.pk)

        response = self.client.get(url)

        flight_serializer = FlightRetrieveSerializer(self.flight)

        self.assertEqual(response.data, flight_serializer.data)


class AdminTest(AdminAPITestCase, BaseTest):
    def test_access_list_pages(self):
        data = get_data()
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_details_page(self):
        data = get_data()
        url = get_detail_url(self.flight.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(
            url,
            data={"arrival_time": data["arrival_time"] + datetime.timedelta(days=1)},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create(self):
        data = get_data()
        response = self.client.post(URL, data=data)

        flight = Flight.objects.get(pk=response.data["id"])

        route = data.pop("route")
        airplane = data.pop("airplane")
        data.pop("crews")

        for info, value in data.items():
            with self.subTest(info=info):
                self.assertEqual(getattr(flight, info), value)

        self.assertEqual(route, flight.route.pk)
        self.assertEqual(airplane, flight.airplane.pk)
        self.assertEqual(1, len(flight.crews.all()))

    def test_update(self):
        data = get_data()
        url = get_detail_url(self.flight.pk)

        self.client.put(url, data=data)

        self.flight.refresh_from_db()

        route = data.pop("route")
        airplane = data.pop("airplane")
        data.pop("crews")

        for info, value in data.items():
            with self.subTest(info=info):
                self.assertEqual(getattr(self.flight, info), value)

        self.assertEqual(route, self.flight.route.pk)
        self.assertEqual(airplane, self.flight.airplane.pk)
        self.assertEqual(1, len(self.flight.crews.all()))

    def test_partial_update(self):
        arrival_time = timezone.now() + datetime.timedelta(days=10)
        url = get_detail_url(self.flight.pk)

        self.client.patch(url, data={"arrival_time": arrival_time})

        self.flight.refresh_from_db()

        self.assertEqual(self.flight.arrival_time, arrival_time)

    def test_delete(self):
        url = get_detail_url(self.flight.pk)

        self.client.delete(url)

        with self.assertRaises(Flight.DoesNotExist):
            self.flight.refresh_from_db()
