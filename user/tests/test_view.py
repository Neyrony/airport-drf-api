from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.test_case_authorized import UserAPITestCase
from user.serializers import UserSerializer

REGISTER_URL = reverse("user:register")

PROFILE_URL = reverse("user:profile")


class UnauthorizedTest(APITestCase):
    def test_create_user(self):
        email = "test@test.com"
        password = "Testpass12345!"
        data = {"email": email, "password": password}
        response = self.client.post(REGISTER_URL, data)

        user = get_user_model().objects.get(email=email)
        user_serializer = UserSerializer(user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, user_serializer.data)

    def test_manage_user(self):
        response = self.client.get(PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.put(PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.patch(PROFILE_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserTest(UserAPITestCase):
    def test_manage_user(self):
        response = self.client.get(PROFILE_URL)

        user_serializer = UserSerializer(self.user)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, user_serializer.data)

        data = {"email": "test@new.com", "password": "QWERTY!@#"}

        response = self.client.put(PROFILE_URL, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], data["email"])
        self.assertTrue(self.user.check_password(data["password"]))

        new_password = "ZXCV!@#"
        response = self.client.patch(PROFILE_URL, data={"password": new_password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(new_password))
