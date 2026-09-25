from django.test import TestCase
from django.urls import reverse
from .models import User


class RegistrationTests(TestCase):
    def test_tenant_registration_assigns_tenant_role(self):
        response = self.client.post(reverse("accounts:register_tenant"), {"full_name": "Ada Tenant", "email": "ada@example.com", "phone": "08000000000", "password1": "Strong-pass-123", "password2": "Strong-pass-123"})
        self.assertRedirects(response, reverse("accounts:preferences"))
        self.assertEqual(User.objects.get(email="ada@example.com").role, User.Role.TENANT)
