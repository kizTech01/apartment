from django.contrib import admin
from .models import Apartment, ApartmentImage, Favourite, InteractionLog

class ApartmentImageInline(admin.TabularInline): model = ApartmentImage; extra = 0
@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ("title", "landlord", "location", "price", "status", "created_at")
    list_filter = ("status", "location", "bedrooms")
    search_fields = ("title", "description", "landlord__email")
    list_select_related = ("landlord",); inlines = [ApartmentImageInline]
    actions = ["approve_listings", "unpublish_listings"]
    @admin.action(description="Approve selected listings")
    def approve_listings(self, request, queryset): queryset.filter(landlord__is_verified=True).update(status=Apartment.Status.AVAILABLE)
    @admin.action(description="Unpublish selected listings")
    def unpublish_listings(self, request, queryset): queryset.update(status=Apartment.Status.UNPUBLISHED)
admin.site.register(Favourite)
admin.site.register(InteractionLog)
