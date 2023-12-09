# Generated by Django 4.2 on 2023-08-12 16:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('account', '0024_alter_profile_following_circle'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='circle',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='people', to=settings.AUTH_USER_MODEL),
        ),
    ]
