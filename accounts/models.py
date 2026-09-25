from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class UserManager(BaseUserManager):
    """Create users with the email address used as this project's login field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The email address must be set.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superusers must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superusers must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrator"
        LANDLORD = "LANDLORD", "Landlord"
        AGENT = "AGENT", "Agent"
        TENANT = "TENANT", "Tenant"

    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=180)
    phone = models.CharField(max_length=20, validators=[RegexValidator(r"^\+?[0-9 -]{7,20}$")])
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.TENANT, db_index=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name", "phone"]
    objects = UserManager()

    @property
    def is_property_owner(self):
        return self.role in {self.Role.LANDLORD, self.Role.AGENT}

    def __str__(self):
        return self.full_name or self.email


class LandlordVerification(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
    class DocumentType(models.TextChoices):
        BUSINESS = "BUSINESS", "Business registration"
        AUTHORISATION = "AUTHORISATION", "Owner authorisation"
        OTHER = "OTHER", "Other evidence"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="verifications")
    document = models.FileField(upload_to="verification_documents/%Y/%m/")
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="reviewed_verifications")
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ["-submitted_at"]


class Preference(models.Model):
    tenant = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preference")
    min_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preferred_location = models.CharField(max_length=80, blank=True)
    min_bedrooms = models.PositiveSmallIntegerField(default=1)
    amenities_wanted = models.JSONField(default=list, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.min_price and self.max_price and self.min_price > self.max_price:
            raise ValidationError("Minimum price cannot exceed maximum price.")
