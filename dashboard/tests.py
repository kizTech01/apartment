from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from apartments.models import Apartment
from moderation.models import ListingReport
from notifications.models import Notification


class AdministratorWorkspaceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@example.com", full_name="Platform Admin", phone="08000000010",
            role=User.Role.ADMIN, is_staff=True, password="Strong-pass-123",
        )
        self.owner = User.objects.create_user(
            email="owner@example.com", full_name="Property Owner", phone="08000000011",
            role=User.Role.LANDLORD, is_verified=True, password="Strong-pass-123",
        )
        self.tenant = User.objects.create_user(
            email="tenant@example.com", full_name="Tenant User", phone="08000000012",
            role=User.Role.TENANT, password="Strong-pass-123",
        )
        self.apartment = Apartment.objects.create(
            landlord=self.owner, title="Pending Jimeta flat", description="A well-kept home.",
            price=450000, location=Apartment.Location.JIMETA, bedrooms=2, bathrooms=1,
            status=Apartment.Status.PENDING,
        )

    def test_non_administrator_cannot_open_administrator_queue(self):
        self.client.force_login(self.tenant)
        response = self.client.get(reverse("dashboard:listing_queue"))
        self.assertEqual(response.status_code, 403)

    def test_administrator_queues_and_user_workspace_render(self):
        self.assertTrue(self.admin.is_staff)
        self.client.force_login(self.admin)
        for name in ("verification_queue", "listing_queue", "report_queue", "user_list"):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(f"dashboard:{name}")).status_code, 200)
        self.assertEqual(self.client.get(reverse("admin:index")).status_code, 200)

    def test_administrator_can_publish_listing_and_notifies_owner(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse("dashboard:review_listing", args=[self.apartment.pk]), {
            "decision": Apartment.Status.AVAILABLE,
            "moderation_note": "",
        })
        self.assertRedirects(response, reverse("dashboard:listing_queue"))
        self.apartment.refresh_from_db()
        self.assertEqual(self.apartment.status, Apartment.Status.AVAILABLE)
        self.assertTrue(Notification.objects.filter(recipient=self.owner, notification_type="LISTING").exists())

    def test_administrator_can_resolve_listing_report(self):
        report = ListingReport.objects.create(
            apartment=self.apartment, reporter=self.tenant, reason=ListingReport.Reason.PRICE,
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse("dashboard:review_report", args=[report.pk]), {"decision": ListingReport.Status.RESOLVED})
        self.assertRedirects(response, reverse("dashboard:report_queue"))
        report.refresh_from_db()
        self.assertEqual(report.status, ListingReport.Status.RESOLVED)
        self.assertIsNotNone(report.resolved_at)

    def test_administrator_cannot_change_another_administrator_account(self):
        other_admin = User.objects.create_user(
            email="other-admin@example.com", full_name="Other Admin", phone="08000000013",
            role=User.Role.ADMIN, password="Strong-pass-123",
        )
        self.client.force_login(self.admin)
        response = self.client.post(reverse("dashboard:manage_user", args=[other_admin.pk]), {
            "full_name": other_admin.full_name,
            "phone": other_admin.phone,
            "role": User.Role.TENANT,
            "is_active": "on",
        })
        self.assertEqual(response.status_code, 200)
        other_admin.refresh_from_db()
        self.assertEqual(other_admin.role, User.Role.ADMIN)
