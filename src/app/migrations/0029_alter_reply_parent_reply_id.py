# Generated by Django 4.2 on 2023-08-26 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_alter_reply_parent_reply_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reply',
            name='parent_reply_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
