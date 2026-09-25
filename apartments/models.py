from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Apartment(models.Model):
    class Location(models.TextChoices):
        JIMETA = "Jimeta", "Jimeta"
        YOLA_TOWN = "Yola Town", "Yola Town"
        GIREI = "Girei", "Girei"
        DOUBELI = "Doubeli", "Doubeli"
        VINIKILANG = "Vinikilang", "Vinikilang"
        NGURORE = "Ngurore", "Ngurore"
    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PENDING = "PENDING", "Pending review"
        AVAILABLE = "AVAILABLE", "Available"
        RESERVED = "RESERVED", "Reserved"
        RENTED = "RENTED", "Rented"
        UNPUBLISHED = "UNPUBLISHED", "Unpublished"
    AMENITIES = ("Water", "Electricity", "Parking", "Security", "Kitchen", "Furnished", "Prepaid meter", "Compound", "Air conditioning", "Wardrobe", "Borehole")

    landlord = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="apartments")
    title = models.CharField(max_length=180)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(1)], db_index=True, help_text="Annual rent in Nigerian Naira")
    location = models.CharField(max_length=80, choices=Location.choices, db_index=True)
    bedrooms = models.PositiveSmallIntegerField(default=1)
    bathrooms = models.PositiveSmallIntegerField(default=1)
    amenities = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT, db_index=True)
    moderation_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["location", "price", "status"])]

    def __str__(self): return self.title
    @property
    def primary_image(self): return self.images.filter(is_primary=True).first() or self.images.first()
    @property
    def is_public(self): return self.status == self.Status.AVAILABLE


class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="apartments/%Y/%m/")
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["-is_primary", "uploaded_at"]
    def __str__(self): return f"Image for {self.apartment}"


class Favourite(models.Model):
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favourites")
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="favourited_by")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["tenant", "apartment"], name="unique_tenant_favourite")]


class InteractionLog(models.Model):
    class Action(models.TextChoices):
        VIEW = "VIEW", "View"; CLICK = "CLICK", "Click"; SAVE = "SAVE", "Save"; MESSAGE = "MESSAGE", "Message"; BOOKING = "BOOKING", "Booking request"
    tenant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interactions")
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="interactions")
    action = models.CharField(max_length=10, choices=Action.choices)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta: indexes = [models.Index(fields=["tenant", "action", "timestamp"])]
