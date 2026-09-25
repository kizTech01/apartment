from django.contrib import admin
from .models import Booking
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("apartment", "tenant", "requested_date", "requested_time", "status")
    list_filter = ("status",); search_fields = ("apartment__title", "tenant__email")
