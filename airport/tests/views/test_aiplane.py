from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from airport.models import Airplane, AirplaneType
from airport.serializers import AirplaneListRetrieveSerializer
from core.test_case_authorized import UserAPITestCase, AdminAPITestCase

URL = reverse("airport:airplane-list")


def get_detail_url(pk):
    return reverse("airport:airplane-detail", kwargs={"pk": pk})


def get_upload_image_url(pk):
    return reverse("airport:airplane-upload-image", kwargs={"pk": pk})


def get_data():
    airplane_type = AirplaneType.objects.create(name="test2")
    return {
        "name": "Test name",
        "rows": 10,
        "seats_in_row": 10,
        "airplane_type": airplane_type.pk,
    }


class BaseTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airplane_type = AirplaneType.objects.create(name="test")
        cls.airplane = Airplane.objects.create(
            name="Test", rows=11, seats_in_row=11, airplane_type=cls.airplane_type
        )


class UnauthorizedTest(BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_details_page(self):
        data = get_data()
        url = get_detail_url(self.airplane.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.patch(url, data={"name": data["name"]})
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
        url = get_detail_url(self.airplane.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.patch(url, data={"name": data["name"]})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list(self):
        response = self.client.get(URL)

        all_airplanes = Airplane.objects.all()
        airports_serializer = AirplaneListRetrieveSerializer(all_airplanes, many=True)

        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"], airports_serializer.data)

    def test_list_filter(self):
        data = get_data()
        data["airplane_type"] = self.airplane_type
        name = data["name"]
        self.airplane2 = Airplane.objects.create(**data)

        airplane2_serializer = AirplaneListRetrieveSerializer(self.airplane2)
        response = self.client.get(URL, {"name": name})

        self.assertEqual(response.data["results"], [airplane2_serializer.data])

    def test_retrieve(self):
        url = get_detail_url(self.airplane.pk)

        response = self.client.get(url)

        airport_serializer = AirplaneListRetrieveSerializer(self.airplane)

        self.assertEqual(response.data, airport_serializer.data)


class AdminTest(AdminAPITestCase, BaseTest):
    def test_access_list_pages(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(URL, data=get_data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_access_details_page(self):
        data = get_data()
        url = get_detail_url(self.airplane.pk)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(url, data={"name": data["name"]})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create(self):
        data = get_data()
        response = self.client.post(URL, data=data)

        airplane_type = data.pop("airplane_type")
        airplane = Airplane.objects.get(pk=response.data["id"])

        for info, value in data.items():
            with self.subTest(info=info):
                self.assertEqual(getattr(airplane, info), value)

        self.assertEqual(airplane_type, getattr(airplane, "airplane_type_id"))

    def test_update(self):
        data = get_data()
        url = get_detail_url(self.airplane.pk)

        self.client.put(url, data=data)

        self.airplane.refresh_from_db()

        airplane_type = data.pop("airplane_type")

        for info, value in data.items():
            with self.subTest(info=info):
                self.assertEqual(getattr(self.airplane, info), value)

        self.assertEqual(airplane_type, getattr(self.airplane, "airplane_type_id"))

    def test_partial_update(self):
        data = get_data()
        url = get_detail_url(self.airplane.pk)

        self.client.patch(url, data={"name": data["name"]})

        self.airplane.refresh_from_db()

        self.assertEqual(self.airplane.name, data["name"])

    def test_delete(self):
        url = get_detail_url(self.airplane.pk)

        self.client.delete(url)

        with self.assertRaises(Airplane.DoesNotExist):
            self.airplane.refresh_from_db()

    def test_upload_image(self):
        tiny_gif = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x05\x04\x04"
            b"\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44"
            b"\x01\x00\x3b"
        )
        fake_image = SimpleUploadedFile("plane.gif", tiny_gif, content_type="image/gif")

        response = self.client.post(
            get_upload_image_url(self.airplane.pk),
            {"image": fake_image},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.airplane.refresh_from_db()
        self.assertTrue(self.airplane.image)

        self.addCleanup(self.airplane.image.delete, save=False)
