# Generated by Django 4.2.1 on 2023-07-02 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0017_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]