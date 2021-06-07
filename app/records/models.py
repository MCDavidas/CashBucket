from django.db import models
from django.contrib.auth.models import User

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy


VALUE_CHOICES = [
    ('BLR', 'BLR'),
    ('RUB', 'RUB'),
    ('UAH', 'UAH'),
    ('PLN', 'PLN'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
]


EXPENSE_CATEGORY_CHOICES = [
    ('Питание', 'Питание'),
    ('Коммунальные расходы', 'Коммунальные расходы'),
    ('Транспорт', 'Транспорт'),
    ('Образование', 'Образование'),
    ('Одежда и косметика', 'Одежда и косметика'),
    ('Развлечения', 'Развлечения'),
    ('Медицина', 'Медицина'),
    ('Прочее', 'Прочее'),
]


def validate_positive(value):
    if value < 0:
        raise ValidationError(
            gettext_lazy('Inter a positive number'),
            params={'value': value},
        )


class Rate(models.Model):
    name = models.CharField(max_length=20)
    count = models.CharField(max_length=10)
    value = models.FloatField(validators=[validate_positive])


class ExpenseRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.FloatField(validators=[validate_positive])
    category = models.CharField(max_length=25, choices=EXPENSE_CATEGORY_CHOICES)
    text = models.CharField(blank=True, max_length=50)
    type = models.CharField(max_length=3, choices=VALUE_CHOICES, default='BLR')
    value_in_blr = models.FloatField(validators=[validate_positive])


class IncomeRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField()
    value = models.FloatField(validators=[validate_positive])
    text = models.CharField(blank=True, max_length=50)
    type = models.CharField(max_length=3, choices=VALUE_CHOICES, default='BLR')
    value_in_blr = models.FloatField(validators=[validate_positive])


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    value = models.FloatField(validators=[validate_positive])


class CategoryStat:
    def __init__(self, record_type, year, month, week):
        self.record_type = record_type
        self.year = year
        self.month = month
        self.week = week


class BudgetRemainder:
    def __init__(self, pk, start_time, finish_time, value, value_remain):
        self.pk = pk
        self.start_time = start_time
        self.finish_time = finish_time
        self.value = value
        self.value_remain = value_remain
        self.negative = False
        if self.value_remain[0] == '-':
            self.negative = True
