from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import LandlordVerification, Preference, User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "full_name", "role", "is_verified", "is_active", "created_at")
    list_filter = ("role", "is_verified", "is_active")
    search_fields = ("email", "full_name", "phone")
    ordering = ("-created_at",)
    fieldsets = ((None, {"fields": ("email", "password")}), ("Personal", {"fields": ("full_name", "phone", "role", "is_verified")}), ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}), ("Dates", {"fields": ("last_login", "date_joined", "created_at")}))
    readonly_fields = ("created_at",)
    add_fieldsets = ((None, {"classes": ("wide",), "fields": ("email", "full_name", "phone", "role", "password1", "password2")}),)

@admin.register(LandlordVerification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ("user", "document_type", "status", "submitted_at", "reviewer")
    list_filter = ("status", "document_type")
    search_fields = ("user__email", "user__full_name")
    readonly_fields = ("submitted_at", "reviewed_at")
    actions = ("approve_verifications", "reject_verifications")

    @staticmethod
    def _sync_owner_verification(user):
        user.is_verified = user.verifications.filter(status=LandlordVerification.Status.APPROVED).exists()
        user.save(update_fields=("is_verified",))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        self._sync_owner_verification(obj.user)

    @admin.action(description="Approve selected owner verifications")
    def approve_verifications(self, request, queryset):
        from django.utils import timezone
        queryset.update(status=LandlordVerification.Status.APPROVED, reviewer=request.user, reviewed_at=timezone.now())
        for user in User.objects.filter(verifications__in=queryset).distinct():
            self._sync_owner_verification(user)

    @admin.action(description="Reject selected owner verifications")
    def reject_verifications(self, request, queryset):
        from django.utils import timezone
        queryset.update(status=LandlordVerification.Status.REJECTED, reviewer=request.user, reviewed_at=timezone.now())
        for user in User.objects.filter(verifications__in=queryset).distinct():
            self._sync_owner_verification(user)

admin.site.register(Preference)
