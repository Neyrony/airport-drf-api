from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase



class UserTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="test@example.com", password="")

    def test_username_absence(self):
        with self.assertRaises(TypeError):
            get_user_model().objects.create_user(username="test", password="")

    def test_email_constraint(self):
        with self.assertRaises(IntegrityError):
            get_user_model().objects.create_user(email="test@example.com", password="")

    def test_default_fields(self):
        self.assertEqual(self.user.is_staff, False)
        self.assertEqual(self.user.is_superuser, False)

    def test_username_field(self):
        self.assertEqual(self.user.USERNAME_FIELD, "email")


