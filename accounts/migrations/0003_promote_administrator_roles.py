from django.db import migrations


def grant_staff_access_to_administrators(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(role="ADMIN", is_staff=False).update(is_staff=True)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_managers"),
    ]

    operations = [
        migrations.RunPython(grant_staff_access_to_administrators, migrations.RunPython.noop),
    ]
