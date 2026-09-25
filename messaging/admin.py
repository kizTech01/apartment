from django.contrib import admin
from .models import Message
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "apartment", "is_read", "timestamp")
    search_fields = ("sender__email", "receiver__email", "content")
    readonly_fields = ("timestamp",)
