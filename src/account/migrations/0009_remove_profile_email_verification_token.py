# Generated by Django 4.2.1 on 2023-06-27 16:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_profile_email_verification_token_profile_is_verify'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='email_verification_token',
        ),
    ]
