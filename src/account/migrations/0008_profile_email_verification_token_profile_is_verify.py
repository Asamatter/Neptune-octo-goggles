# Generated by Django 4.2.1 on 2023-06-27 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_profile_following'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email_verification_token',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_verify',
            field=models.BooleanField(default=False),
        ),
    ]