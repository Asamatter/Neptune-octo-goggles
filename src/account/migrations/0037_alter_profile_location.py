# Generated by Django 4.2 on 2023-09-05 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0036_alter_profile_website'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='location',
            field=models.CharField(blank=True, choices=[('Africa', 'Africa'), ('Antarctica', 'Antarctica'), ('Asia', 'Asia'), ('Europe', 'Europe'), ('North America', 'North America'), ('Oceania', 'Oceania'), ('South America', 'South America')], max_length=20),
        ),
    ]