from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.models import User


class Command(BaseCommand):
    help = "Create or promote the administrator configured with ADMIN_EMAIL and ADMIN_PASSWORD."

    def handle(self, *args, **options):
        values = {"ADMIN_EMAIL": settings.ADMIN_EMAIL.strip(), "ADMIN_PASSWORD": settings.ADMIN_PASSWORD}
        configured = [name for name, value in values.items() if value]
        if not configured:
            self.stdout.write("No administrator credentials configured; provisioning skipped.")
            return
        missing = [name for name, value in values.items() if not value]
        if missing:
            raise CommandError("Administrator provisioning requires: " + ", ".join(missing))

        user, created = User.objects.get_or_create(
            email=values["ADMIN_EMAIL"],
            defaults={
                "full_name": "Administrator",
                "phone": "0000000000",
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
