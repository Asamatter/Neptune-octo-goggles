# Generated by Django 4.2.1 on 2023-07-23 01:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_alter_profile_last_login'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='last_login',
        ),
    ]