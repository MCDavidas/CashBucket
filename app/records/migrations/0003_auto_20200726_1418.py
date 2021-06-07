# Generated by Django 3.0.6 on 2020-07-26 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('records', '0002_auto_20200726_1401'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='type',
            field=models.CharField(choices=[('BLR', 'BLR'), ('RUB', 'RUB'), ('UAH', 'UAH'), ('PLN', 'PLN'), ('USD', 'USD'), ('EUR', 'EUR')], default='BLR', max_length=3),
        ),
    ]
