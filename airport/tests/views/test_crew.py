from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Crew
from airport.serializers import CrewSerializer
from core.test_case_authorized import UserAPITestCase, AdminAPITestCase

URL = reverse("airport:crew-list")


def get_detail_url(pk):
    return reverse("airport:crew-detail", kwargs={"pk": pk})


def get_data():
    return {"first_name": "Andrew", "last_name": "Black"}


class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.crew = Crew.objects.create(first_name="test first name", last_name="test last name")


class UnauthorizedTest(BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_details_page(self):
        url = get_detail_url(self.crew.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url, data={"first_name": get_data()["first_name"]})
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
        url = get_detail_url(self.crew.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data={"first_name": get_data()["first_name"]})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list(self):
        response = self.client.get(URL)

        all_crews = Crew.objects.all()
        crews_serializer = CrewSerializer(all_crews, many=True)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"], crews_serializer.data)

    def test_list_filter(self):
        first_name = get_data()["first_name"]
        last_name = get_data()["last_name"]
        self.crew2 = Crew.objects.create(**get_data())

        crew2_serializer = CrewSerializer(self.crew2)
        response = self.client.get(URL, {"first_name": first_name})

        self.assertEqual(response.data["results"], [crew2_serializer.data])

        response = self.client.get(URL, {"last_name": last_name})

        self.assertEqual(response.data["results"], [crew2_serializer.data])

    def test_retrieve(self):
        url = get_detail_url(self.crew.pk)

        response = self.client.get(url)

        crew_serializer = CrewSerializer(self.crew)

        self.assertEqual(response.data, crew_serializer.data)


class AdminTest(AdminAPITestCase, BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_details_page(self):
        url = get_detail_url(self.crew.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(url, data={"first_name": get_data()["first_name"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create(self):
        response = self.client.post(URL, data=get_data())

        crew = Crew.objects.get(pk=response.data["id"])

        for info, value in get_data().items():
            with self.subTest(info=info):
                self.assertEqual(getattr(crew, info), value)

    def test_update(self):
        url = get_detail_url(self.crew.pk)

        self.client.put(url, data=get_data())

        self.crew.refresh_from_db()

        for info, value in get_data().items():
            with self.subTest(info=info):
                self.assertEqual(getattr(self.crew, info), value)

    def test_partial_update(self):
        name = "Sam"
        url = get_detail_url(self.crew.pk)

        self.client.patch(url, data={"first_name": name})

        self.crew.refresh_from_db()

        self.assertEqual(self.crew.first_name, name)

    def test_delete(self):
        url = get_detail_url(self.crew.pk)

        self.client.delete(url)

        with self.assertRaises(Crew.DoesNotExist):
            self.crew.refresh_from_db()
