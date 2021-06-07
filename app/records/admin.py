from django.contrib import admin
from records.models import Rate, ExpenseRecord, IncomeRecord, Budget

# Register your models here.
admin.site.register(Rate)
admin.site.register(ExpenseRecord)
admin.site.register(IncomeRecord)
admin.site.register(Budget)
