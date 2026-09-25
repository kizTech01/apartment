from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from apartments.models import Apartment
class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"; ACCEPTED = "ACCEPTED", "Accepted"; DECLINED = "DECLINED", "Declined"; RESCHEDULED = "RESCHEDULED", "Rescheduled"; CANCELLED = "CANCELLED", "Cancelled"; COMPLETED = "COMPLETED", "Completed"
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="bookings")
    requested_date = models.DateField()
    requested_time = models.TimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True)
    landlord_response = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ["-created_at"]
