from django.contrib.auth import get_user_model
from django.test import TestCase


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
