# Generated by Django 3.0.6 on 2020-10-23 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0010_budget'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='start_time',
            field=models.DateTimeField(),
        ),
    ]
