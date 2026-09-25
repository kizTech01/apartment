from django.conf import settings
from django.db import models
from apartments.models import Apartment
class ListingReport(models.Model):
    class Reason(models.TextChoices):
        FAKE = "FAKE", "Fake listing"; DUPLICATE = "DUPLICATE", "Duplicate listing"; PRICE = "PRICE", "Incorrect price"; LOCATION = "LOCATION", "Incorrect location"; MISLEADING = "MISLEADING", "Misleading information"; OTHER = "OTHER", "Other"
    class Status(models.TextChoices): PENDING = "PENDING", "Pending"; REVIEWING = "REVIEWING", "Reviewing"; RESOLVED = "RESOLVED", "Resolved"; DISMISSED = "DISMISSED", "Dismissed"
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listing_reports")
    reason = models.CharField(max_length=12, choices=Reason.choices)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ["-created_at"]
