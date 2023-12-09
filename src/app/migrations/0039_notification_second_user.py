# Generated by Django 4.2 on 2023-09-21 23:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0038_notification_replied_notification_reply'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='second_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='second_user_notifications', to=settings.AUTH_USER_MODEL),
        ),
    ]