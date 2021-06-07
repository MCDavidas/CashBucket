# Generated by Django 3.0.6 on 2020-07-24 20:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import records.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Record',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('value', models.FloatField(validators=[records.models.validate_positive])),
                ('text', models.CharField(max_length=100)),
                ('type', models.IntegerField(choices=[(1, 'USD'), (2, 'RUB'), (3, 'EUR'), (4, 'UAH')])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
