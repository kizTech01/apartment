from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User


class Command(BaseCommand):
    help = "Create or promote the administrator configured with ADMIN_* environment variables."

    def handle(self, *args, **options):
        values = {
            "ADMIN_EMAIL": settings.ADMIN_EMAIL.strip(),
            "ADMIN_FULL_NAME": settings.ADMIN_FULL_NAME.strip(),
            "ADMIN_PHONE": settings.ADMIN_PHONE.strip(),
            "ADMIN_PASSWORD": settings.ADMIN_PASSWORD,
        }
        configured = [name for name, value in values.items() if value]
        if not configured:
            self.stdout.write("No ADMIN_* variables configured; administrator provisioning skipped.")
            return
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise CommandError("Administrator provisioning requires: " + ", ".join(missing))

        user, created = User.objects.get_or_create(
            email=values["ADMIN_EMAIL"],
            defaults={
                "full_name": values["ADMIN_FULL_NAME"],
                "phone": values["ADMIN_PHONE"],
                "role": User.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            user.set_password(values["ADMIN_PASSWORD"])
            user.save(update_fields=("password",))
            self.stdout.write(self.style.SUCCESS("Administrator account created."))
            return

        changes = []
        for field, value in (
            ("full_name", values["ADMIN_FULL_NAME"]),
            ("phone", values["ADMIN_PHONE"]),
            ("role", User.Role.ADMIN),
            ("is_staff", True),
            ("is_superuser", True),
            ("is_active", True),
        ):
            if getattr(user, field) != value:
                setattr(user, field, value)
                changes.append(field)
        if not user.check_password(values["ADMIN_PASSWORD"]):
            user.set_password(values["ADMIN_PASSWORD"])
            changes.append("password")
        if changes:
            user.save(update_fields=changes)
            self.stdout.write(self.style.SUCCESS("Existing administrator account synchronised."))
        else:
            self.stdout.write("Administrator account is already configured.")
