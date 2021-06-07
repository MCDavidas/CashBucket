from django import forms
from records.models import IncomeRecord, ExpenseRecord, Budget
from captcha.fields import CaptchaField


BUDGET_DAYS = [(7, '7 дней'), (30, '30 дней'), (90, '90 дней'), (365, '365 дней')]
YEAR_CHOICES = ['2019', '2020', '2021']
MONTHS = {
    1: ('Январь'), 2: ('Февраль'), 3: ('Март'), 4: ('Апрель'),
    5: ('Май'), 6: ('Июнь'), 7: ('Июль'), 8: ('Август'),
    9: ('Сентябрь'), 10: ('Октябрь'), 11: ('Ноябрь'), 12: ('Декабрь')
}


class LoginForm(forms.Form):
    username = forms.CharField(label='', max_length=20,
                               widget=forms.TextInput(attrs={
                                   'placeholder': 'логин',
                                   'class': 'fadeIn second',
                                   'autocomplete': 'off'}))
    password = forms.CharField(label='',
                               widget=forms.PasswordInput(attrs={
                                   'placeholder': 'пароль',
                                   'class': "fadeIn third",
                                   'autocomplete': 'off'}))


class RegisterForm(forms.Form):
    username = forms.CharField(label='', max_length=20,
                               widget=forms.TextInput(attrs={
                                   'placeholder': 'логин',
                                   'autocomplete': 'off'}))
    password = forms.CharField(label='',
                               widget=forms.PasswordInput(attrs={
                                   'placeholder': 'пароль',
                                   'autocomplete': 'off'}))
    confirm_password = forms.CharField(label='',
                                       widget=forms.PasswordInput(attrs={
                                           'placeholder': 'повторите пароль',
                                           'autocomplete': 'off'}))
    captcha = CaptchaField()


class ExpenseRecordForm(forms.ModelForm):
    class Meta:
        model = ExpenseRecord
        fields = ['category', 'text', 'value', 'type']
        widgets = {
            'category': forms.Select(attrs={
                'class': 'form-control',
            }),
            'text': forms.Textarea(attrs={
                'autocomplete': 'off',
                'class': 'form-control',
                'placeholder': 'Необязательное поле',
                'rows': 2,
            }),
            'value': forms.NumberInput(attrs={
                'min': 0,
                'max': 9999999,
                'value': 0,
                'class': 'form-control',
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
            })
        }


class IncomeRecordForm(forms.ModelForm):
    class Meta:
        model = IncomeRecord
        fields = ['text', 'value', 'type']
        widgets = {
            'text': forms.Textarea(attrs={
                'autocomplete': 'off',
                'class': 'form-control',
                'placeholder': 'Необязательное поле',
                'rows': 2,
            }),
            'value': forms.NumberInput(attrs={
                'min': 0,
                'max': 9999999,
                'value': 0,
                'class': 'form-control',
            }),
            'type': forms.Select(attrs={
                'class': 'form-control',
            })
        }


class BudgetForm(forms.Form):
    days = forms.IntegerField(widget=forms.Select(choices=BUDGET_DAYS,
                                                  attrs={'class': 'form-control',}))
    value = forms.IntegerField(widget=forms.NumberInput(attrs={
                'min': 0,
                'max': 9999999,
                'value': 0,
                'class': 'form-control',
            }),)


class SearchForm(forms.Form):
    '''category = forms.ChoiceField(choices=EXPENSE_CATEGORY_CHOICES,
                                 widget=forms.Select(attrs={
                                     'class': 'form-control',
                                     'autocomplete': 'off'}))'''
    date = forms.DateField(widget=forms.SelectDateWidget(years=YEAR_CHOICES, months=MONTHS,
                                                         attrs={
                                                             'class': 'form-control',
                                                         }))
