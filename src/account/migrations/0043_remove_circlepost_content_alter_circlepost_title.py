# Generated by Django 4.2 on 2023-09-29 14:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0042_alter_follow_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='circlepost',
            name='content',
        ),
        migrations.AlterField(
            model_name='circlepost',
            name='title',
            field=models.CharField(blank=True, max_length=280),
        ),
    ]
