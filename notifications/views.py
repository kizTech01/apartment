from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
@login_required
def notification_list(request):
    items = request.user.notifications.all()
    items.filter(is_read=False).update(is_read=True)
    return render(request, "notifications/list.html", {"notifications": items})
