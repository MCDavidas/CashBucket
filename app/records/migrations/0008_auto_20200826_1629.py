# Generated by Django 3.0.6 on 2020-08-26 13:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import records.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('records', '0007_auto_20200818_1551'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Record',
            new_name='IncomeRecord',
        ),
        migrations.CreateModel(
            name='ExpenseRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('value', models.FloatField(validators=[records.models.validate_positive])),
                ('category', models.CharField(choices=[('Питание', 'Питание'), ('Коммунальные расходы', 'Коммунальные расходы'), ('Транспорт', 'Транспорт'), ('Образование', 'Образование'), ('Одежда и косметика', 'Одежда и косметика'), ('Развлечения', 'Развлечения'), ('Медицина', 'Медицина'), ('Прочее', 'Прочее')], max_length=25)),
                ('text', models.CharField(max_length=50)),
                ('type', models.CharField(choices=[('BLR', 'BLR'), ('RUB', 'RUB'), ('UAH', 'UAH'), ('PLN', 'PLN'), ('USD', 'USD'), ('EUR', 'EUR')], default='BLR', max_length=3)),
                ('value_in_blr', models.FloatField(validators=[records.models.validate_positive])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]