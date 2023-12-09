# Generated by Django 4.2.1 on 2023-07-21 15:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0014_followercounthistory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='followercounthistory',
            name='profile',
        ),
        migrations.AddField(
            model_name='followercounthistory',
            name='user',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]