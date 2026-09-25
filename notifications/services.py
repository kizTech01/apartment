from .models import Notification
def notify(recipient, title, message, notification_type="SYSTEM", link=""):
    return Notification.objects.create(recipient=recipient, title=title, message=message, notification_type=notification_type, link=link)
