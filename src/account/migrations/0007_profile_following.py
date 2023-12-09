# Generated by Django 4.2.1 on 2023-06-24 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_alter_profile_bio_alter_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='following',
            field=models.ManyToManyField(related_name='followers', to='account.profile'),
        ),
    ]
