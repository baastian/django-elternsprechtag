# Generated by Django 5.0.6 on 2024-08-12 00:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0053_teachereventgroup_lead_manual_override'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='event_group',
            new_name='teacher_event_group',
        ),
    ]
