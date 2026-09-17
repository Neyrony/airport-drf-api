from django.urls import reverse

from core.test_case_authorized import AuthenticatedTestCase


class UserAdminTest(AuthenticatedTestCase):
    def test_display_user(self):
        url = reverse("admin:user_user_changelist")
        response = self.client.get(url)

        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.is_staff)
