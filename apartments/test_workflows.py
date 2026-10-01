from datetime import timedelta

from django.test import TestCase
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from accounts.admin import VerificationAdmin
from accounts.models import LandlordVerification, User
from bookings.models import Booking
from .models import Apartment, Favourite


class RoleWorkflowTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com", full_name="Verified Owner", phone="08000000000",
            role=User.Role.LANDLORD, is_verified=True, password="Strong-pass-123",
        )
        self.unverified_owner = User.objects.create_user(
            email="new-owner@example.com", full_name="New Owner", phone="08000000002",
            role=User.Role.LANDLORD, password="Strong-pass-123",
        )
        self.tenant = User.objects.create_user(
            email="tenant@example.com", full_name="Tenant", phone="08000000001",
            role=User.Role.TENANT, password="Strong-pass-123",
        )
        self.apartment = Apartment.objects.create(
            landlord=self.owner, title="Jimeta family flat", description="Bright and secure.",
            price=450000, location=Apartment.Location.JIMETA, bedrooms=2, bathrooms=1,
            amenities=["Water", "Parking"], status=Apartment.Status.AVAILABLE,
        )

    def test_unverified_owner_cannot_start_listing(self):
        self.client.force_login(self.unverified_owner)
        response = self.client.get(reverse("apartments:create"))
        self.assertRedirects(response, reverse("accounts:verification"))

    def test_public_property_pages_render_with_the_fallback_photography(self):
        home = self.client.get(reverse("apartments:home"))
        detail = self.client.get(reverse("apartments:detail", args=[self.apartment.pk]))
        self.assertContains(home, "aparthub-hero.jpg")
        self.assertContains(detail, "apartment-exterior.jpg")

    def test_verified_owner_submits_pending_listing(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("apartments:create"), {
            "title": "Girei studio", "description": "Freshly finished studio.", "price": 250000,
            "location": Apartment.Location.GIREI, "bedrooms": 1, "bathrooms": 1,
            "amenities": ["Water", "Electricity"],
        })
        created = Apartment.objects.get(title="Girei studio")
        self.assertEqual(created.status, Apartment.Status.PENDING)
        self.assertRedirects(response, reverse("apartments:image_add", args=[created.pk]))

    def test_tenant_can_save_and_cancel_booking_only_via_post(self):
        self.client.force_login(self.tenant)
        favourite_url = reverse("apartments:toggle_favourite", args=[self.apartment.pk])
        self.assertEqual(self.client.get(favourite_url).status_code, 405)
        self.assertEqual(self.client.post(favourite_url).status_code, 302)
        self.assertTrue(Favourite.objects.filter(tenant=self.tenant, apartment=self.apartment).exists())

        booking = Booking.objects.create(
            tenant=self.tenant, apartment=self.apartment,
            requested_date=timezone.localdate() + timedelta(days=1), requested_time="10:00",
        )
        cancel_url = reverse("bookings:cancel", args=[booking.pk])
        self.assertEqual(self.client.get(cancel_url).status_code, 405)
        self.assertEqual(self.client.post(cancel_url).status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.CANCELLED)

    def test_administrator_can_sign_in_using_administrator_role(self):
        admin = User.objects.create_user(
            email="admin@example.com", full_name="Administrator", phone="08000000003",
            role=User.Role.ADMIN, is_staff=True, password="Strong-pass-123",
        )
        response = self.client.post(reverse("accounts:login"), {
            "account_type": "ADMIN", "username": admin.email, "password": "Strong-pass-123",
        })
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_admin_verification_action_enables_owner_listing_access(self):
        admin = User.objects.create_user(
            email="reviewer@example.com", full_name="Reviewer", phone="08000000004",
            role=User.Role.ADMIN, is_staff=True, password="Strong-pass-123",
        )
        submission = LandlordVerification.objects.create(
            user=self.unverified_owner, document="verification_documents/example.pdf",
            document_type=LandlordVerification.DocumentType.OTHER,
        )
        request = RequestFactory().post("/admin/")
        request.user = admin
        VerificationAdmin(LandlordVerification, None).approve_verifications(
            request, LandlordVerification.objects.filter(pk=submission.pk)
        )
        self.unverified_owner.refresh_from_db()
        self.assertTrue(self.unverified_owner.is_verified)
