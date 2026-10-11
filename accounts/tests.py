from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from tempfile import TemporaryDirectory
from .models import LandlordVerification, User


class RegistrationTests(TestCase):
    def test_tenant_registration_assigns_tenant_role(self):
        response = self.client.post(reverse("accounts:register_tenant"), {"full_name": "Ada Tenant", "email": "ada@example.com", "phone": "08000000000", "password1": "Strong-pass-123", "password2": "Strong-pass-123"})
        self.assertRedirects(response, reverse("accounts:preferences"))
        self.assertEqual(User.objects.get(email="ada@example.com").role, User.Role.TENANT)

    def test_landlord_can_submit_a_verification_document(self):
        owner = User.objects.create_user(
            email="owner@example.com", full_name="Owner", phone="08000000000",
            role=User.Role.LANDLORD, password="Strong-pass-123",
        )
        self.client.force_login(owner)
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post(reverse("accounts:verification"), {
                "document_type": LandlordVerification.DocumentType.OTHER,
                "document": SimpleUploadedFile("evidence.pdf", b"%PDF-1.4 evidence", content_type="application/pdf"),
            })
        self.assertRedirects(response, reverse("accounts:verification"))
        self.assertTrue(LandlordVerification.objects.filter(user=owner).exists())

    @override_settings(
        ADMIN_EMAIL="admin@example.com",
        ADMIN_FULL_NAME="Platform Administrator",
        ADMIN_PHONE="08000000000",
        ADMIN_PASSWORD="Strong-pass-123",
    )
    def test_provision_admin_creates_a_superuser_from_environment_settings(self):
        call_command("provision_admin")
        admin = User.objects.get(email="admin@example.com")
        self.assertEqual(admin.role, User.Role.ADMIN)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password("Strong-pass-123"))

        response = self.client.post(reverse("accounts:login"), {
            "account_type": "ADMIN",
            "username": "admin@example.com",
            "password": "Strong-pass-123",
        })
        self.assertRedirects(response, reverse("dashboard:home"))

        admin.set_password("Old-password-123")
        admin.save(update_fields=("password",))
        call_command("provision_admin")
        admin.refresh_from_db()
        self.assertTrue(admin.check_password("Strong-pass-123"))
