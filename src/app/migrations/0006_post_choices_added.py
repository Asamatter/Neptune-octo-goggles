# Generated by Django 4.2.1 on 2023-06-04 14:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_choice_vote'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='choices_added',
            field=models.BooleanField(default=False),
        ),
    ]
