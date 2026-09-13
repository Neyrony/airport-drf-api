from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase

class AuthenticatedTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="test12345",
            first_name="Andrew",
            last_name="Smith",
        )
        self.client.force_login(self.user)


class AdminAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="test12345",
            first_name="John",
            last_name="Green",
        )
        self.client.force_login(self.user)


class UserAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            password="test12345",
            first_name="Eric",
            last_name="Brown",
        )
        self.client.force_login(self.user)
