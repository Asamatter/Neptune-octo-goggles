# Generated by Django 4.2.1 on 2023-07-03 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_tag_delete_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.post'),
        ),
    ]
