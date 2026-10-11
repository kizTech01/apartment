from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from accounts.models import User


def administrator_required(view):
    """Allow only platform administrators into the operational back office."""

    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.role == User.Role.ADMIN):
            raise PermissionDenied("Administrator access is required.")
        return view(request, *args, **kwargs)

    return wrapped
