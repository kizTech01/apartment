from django.conf import settings
from django.db import models
from apartments.models import Apartment
class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name="messages")
    content = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ["timestamp"]
