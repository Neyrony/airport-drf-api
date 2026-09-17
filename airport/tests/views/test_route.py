from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from airport.models import Airport, Route
from airport.serializers import RouteListRetrieveSerializer, RouteSerializer
from core.test_case_authorized import UserAPITestCase, AdminAPITestCase

URL = reverse("airport:route-list")


def get_detail_url(pk):
    return reverse("airport:route-detail", kwargs={"pk": pk})


def get_data():
    airport1, created = Airport.objects.get_or_create(
        name="Boryspil International Airport", closest_big_city="Kyiv"
    )
    airport_2, created = Airport.objects.get_or_create(
        name="Josep Tarradellas Barcelona–El Prat Airport", closest_big_city="Barcelona"
    )
    return {"source": airport1.pk, "destination": airport_2.pk, "distance": 1500}


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


class UnauthorizedTest(BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_details_page(self):
        url = get_detail_url(self.route.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url, data=get_data())
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
        url = get_detail_url(self.route.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data={"distance": 400})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list(self):
        response = self.client.get(URL)

        all_routers = Route.objects.all()
        route_serializer = RouteListRetrieveSerializer(all_routers, many=True)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"], route_serializer.data)

    def test_list_filter(self):
        data = get_data()
        self.route_2 = Route.objects.create(
            source_id=data["source"],
            destination_id=data["destination"],
            distance=data["distance"],
        )
        route_2_serializer = RouteListRetrieveSerializer(self.route_2)

        response = self.client.get(URL, {"source": "Boryspil"})
        self.assertEqual(response.data["results"], [route_2_serializer.data])

        response = self.client.get(URL, {"destination": "Tarradellas"})
        self.assertEqual(response.data["results"], [route_2_serializer.data])

    def test_retrieve(self):
        url = get_detail_url(self.route.pk)

        response = self.client.get(url)

        route_serializer = RouteListRetrieveSerializer(self.route)

        self.assertEqual(response.data, route_serializer.data)


class AdminTest(AdminAPITestCase, BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_details_page(self):
        url = get_detail_url(self.route.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(url, data={"distance": 400})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create(self):
        data = get_data()
        response = self.client.post(URL, data=data)

        route = Route.objects.get(pk=response.data["id"])

        self.assertEqual(route.source.id, data["source"])
        self.assertEqual(route.destination.id, data["destination"])
        self.assertEqual(route.distance, data["distance"])

    def test_validation(self):
        data = {
            "source": self.airport_1.id,
            "destination": self.airport_1.id,
            "distance": 400,
        }

        route_serializer = RouteSerializer(data=data)
        with self.assertRaises(ValidationError):
            route_serializer.is_valid(raise_exception=True)

    def test_update(self):
        data = get_data()
        url = get_detail_url(self.route.pk)

        self.client.put(url, data=data)

        self.route.refresh_from_db()

        self.assertEqual(self.route.source.id, data["source"])
        self.assertEqual(self.route.destination.id, data["destination"])
        self.assertEqual(self.route.distance, data["distance"])

    def test_partial_update(self):
        url = get_detail_url(self.route.pk)

        distance = 400
        self.client.patch(url, data={"distance": distance})

        self.route.refresh_from_db()

        self.assertEqual(self.route.distance, distance)

    def test_delete(self):
        url = get_detail_url(self.route.pk)

        self.client.delete(url)

        with self.assertRaises(Route.DoesNotExist):
            self.route.refresh_from_db()
