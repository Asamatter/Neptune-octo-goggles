# Generated by Django 4.2 on 2023-08-12 16:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0026_remove_circle_user_circle_host_circlepost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='host',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
