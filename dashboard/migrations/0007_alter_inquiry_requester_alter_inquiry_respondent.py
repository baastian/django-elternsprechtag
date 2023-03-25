# Generated by Django 4.1 on 2022-09-26 20:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dashboard", "0006_rename_teacherstudentinquiry_inquiry"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inquiry",
            name="requester",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_requester",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="inquiry",
            name="respondent",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_respondent",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
