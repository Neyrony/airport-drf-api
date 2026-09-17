from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Airport
from airport.serializers import AirportSerializer
from core.test_case_authorized import UserAPITestCase, AdminAPITestCase

URL = reverse("airport:airport-list")


def get_detail_url(pk):
    return reverse("airport:airport-detail", kwargs={"pk": pk})


def get_data():
    return {"name": "Test name", "closest_big_city": "Test big city"}


class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airport = Airport.objects.create(name="Test", closest_big_city="Test city")


class UnauthorizedTest(BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_details_page(self):
        url = get_detail_url(self.airport.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url, data={"name": get_data()["name"]})
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
        url = get_detail_url(self.airport.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data={"name": get_data()["name"]})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list(self):
        response = self.client.get(URL)

        all_airports = Airport.objects.all()
        airports_serializer = AirportSerializer(all_airports, many=True)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"], airports_serializer.data)

    def test_list_filter(self):
        name = "Boryspil International Airport"
        city = "Kyiv"
        self.airport2 = Airport.objects.create(name=name, closest_big_city=city)

        airport2_serializer = AirportSerializer(self.airport2)
        response = self.client.get(URL, {"name": name})

        self.assertEqual(response.data["results"], [airport2_serializer.data])

        response = self.client.get(URL, {"closest_big_city": city})

        self.assertEqual(response.data["results"], [airport2_serializer.data])

    def test_retrieve(self):
        url = get_detail_url(self.airport.pk)

        response = self.client.get(url)

        airport_serializer = AirportSerializer(self.airport)

        self.assertEqual(response.data, airport_serializer.data)


class AdminTest(AdminAPITestCase, BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_details_page(self):
        url = get_detail_url(self.airport.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(url, data={"name": get_data()["name"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create(self):
        response = self.client.post(URL, data=get_data())

        airport = Airport.objects.get(pk=response.data["id"])

        for info, value in get_data().items():
            with self.subTest(info=info):
                self.assertEqual(getattr(airport, info), value)

    def test_update(self):
        url = get_detail_url(self.airport.pk)

        self.client.put(url, data=get_data())

        self.airport.refresh_from_db()

        for info, value in get_data().items():
            with self.subTest(info=info):
                self.assertEqual(getattr(self.airport, info), value)

    def test_partial_update(self):
        url = get_detail_url(self.airport.pk)

        self.client.patch(url, data={"name": get_data()["name"]})

        self.airport.refresh_from_db()

        self.assertEqual(self.airport.name, get_data()["name"])

    def test_delete(self):
        url = get_detail_url(self.airport.pk)

        self.client.delete(url)

        with self.assertRaises(Airport.DoesNotExist):
            self.airport.refresh_from_db()
