from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import AirplaneType
from airport.serializers import AirplaneTypeSerializer
from core.test_case_authorized import UserAPITestCase, AdminAPITestCase

URL = reverse("airport:airplane-type-list")


def get_detail_url(pk):
    return reverse("airport:airplane-type-detail", kwargs={"pk": pk})


def get_data():
    return {"name": "Boeing"}


class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airplane_type = AirplaneType.objects.create(name="Test")


class UnauthorizedTest(BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_details_page(self):
        url = get_detail_url(self.airplane_type.pk)

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
        url = get_detail_url(self.airplane_type.pk)

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

        all_airplane_types = AirplaneType.objects.all()
        airplane_type_serializer = AirplaneTypeSerializer(all_airplane_types, many=True)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"], airplane_type_serializer.data)

    def test_list_filter(self):
        data = get_data()
        self.airplane_type2 = AirplaneType.objects.create(**data)

        airplane_type2_serializer = AirplaneTypeSerializer(self.airplane_type2)
        response = self.client.get(URL, {"name": data["name"]})

        self.assertEqual(response.data["results"], [airplane_type2_serializer.data])

    def test_retrieve(self):
        url = get_detail_url(self.airplane_type.pk)

        response = self.client.get(url)

        airplane_type_serializer = AirplaneTypeSerializer(self.airplane_type)

        self.assertEqual(response.data, airplane_type_serializer.data)


class AdminTest(AdminAPITestCase, BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_details_page(self):
        url = get_detail_url(self.airplane_type.pk)

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

        airplane_type = AirplaneType.objects.get(pk=response.data["id"])

        self.assertEqual(airplane_type.name, get_data()["name"])

    def test_update(self):
        url = get_detail_url(self.airplane_type.pk)

        self.client.put(url, data=get_data())

        self.airplane_type.refresh_from_db()

        self.assertEqual(self.airplane_type.name, get_data()["name"])

    def test_partial_update(self):
        url = get_detail_url(self.airplane_type.pk)

        self.client.patch(url, data={"name": get_data()["name"]})

        self.airplane_type.refresh_from_db()

        self.assertEqual(self.airplane_type.name, get_data()["name"])

    def test_delete(self):
        url = get_detail_url(self.airplane_type.pk)

        self.client.delete(url)

        with self.assertRaises(AirplaneType.DoesNotExist):
            self.airplane_type.refresh_from_db()
