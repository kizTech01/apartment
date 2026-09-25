from django.test import TestCase
from accounts.models import Preference, User
from .models import Apartment
from recommendations.services import recommend_apartments


class ApartmentRulesTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", full_name="Owner", phone="08000000000", role=User.Role.LANDLORD, is_verified=True, password="Strong-pass-123")
        self.tenant = User.objects.create_user(email="tenant@example.com", full_name="Tenant", phone="08000000001", role=User.Role.TENANT, password="Strong-pass-123")
        Preference.objects.create(tenant=self.tenant, min_price=300000, max_price=600000, preferred_location="Jimeta", min_bedrooms=2, amenities_wanted=["Water", "Parking"])

    def test_only_available_homes_are_recommended(self):
        available = Apartment.objects.create(landlord=self.owner, title="Jimeta flat", description="Test", price=500000, location="Jimeta", bedrooms=2, bathrooms=1, amenities=["Water", "Parking"], status=Apartment.Status.AVAILABLE)
        Apartment.objects.create(landlord=self.owner, title="Rented flat", description="Test", price=500000, location="Jimeta", bedrooms=2, bathrooms=1, status=Apartment.Status.RENTED)
        result = recommend_apartments(self.tenant)
        self.assertEqual([row["apartment"] for row in result], [available])
        self.assertGreaterEqual(result[0]["score"], 0)
        self.assertLessEqual(result[0]["score"], 100)
