from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Sum
import datetime

from records.forms import LoginForm, RegisterForm, ExpenseRecordForm, IncomeRecordForm, SearchForm, MONTHS, BudgetForm
from records.utils import update_rates, convert
from records.models import ExpenseRecord, Rate, IncomeRecord, CategoryStat, EXPENSE_CATEGORY_CHOICES, Budget, BudgetRemainder

import matplotlib.pyplot as plt
import numpy as np
import pylab
import io
import PIL, PIL.Image
from matplotlib import gridspec


def home_view(request):
    return render(request, 'records/home.html', {'login_flag': request.user.is_authenticated})


def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('records:home'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('records:dashboard', kwargs={'param': 'all_time', 'count': 1}))
            else:
                form = LoginForm()
                return render(request, 'records/login.html',
                              {'form': form,
                               'flag': True,
                               'error_message': 'Неверный логин или пароль'})
    else:
        form = LoginForm()

    return render(request, 'records/login.html', {'form': form, 'flag': True})


def rates_view(request):
    # update_rates()
    data = Rate.objects.all()
    return render(request, 'records/rates.html',
                  {'data': data, 'login_flag': request.user.is_authenticated})


def register_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('records:home'))

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['username']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']

            if User.objects.filter(username=name).exists():
                return render(request, 'records/login.html',
                              {'form': form,
                               'flag': False,
                               'error_message': 'Этот логин уже занят'})

            if password != confirm_password:
                return render(request, 'records/login.html',
                              {'form': form,
                               'flag': False,
                               'error_message': 'Пароли не совпадают'})

            if len(password) < 6:
                return render(request, 'records/login.html',
                              {'form': form,
                               'flag': False,
                               'error_message': 'Пароль слишком короткий'})

            user = User.objects.create_user(username=name, password=password)
            user.save()
            login(request, user)
            return HttpResponseRedirect(reverse('records:dashboard', kwargs={'param': 'all_time', 'count': 1}))
    else:
        form = RegisterForm()

    return render(request, 'records/login.html', {'form': form, 'flag': False})


@login_required(login_url='records:login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('records:home'))


@login_required(login_url='records:login')
def dashboard_view(request, param='all_time', count=1):
    if param not in ('all_time', 'year', 'month', 'week', 'day'):
        raise Http404("Page does not exist. Try .../dashboard/workplace/all_time/1/")

    records = ExpenseRecord.objects.filter(user=request.user)
    if param == 'year':
        records = records.filter(date__gte=datetime.date.today() - datetime.timedelta(days=365))
    if param == 'month':
        records = records.filter(date__gte=datetime.date.today() - datetime.timedelta(days=30))
    if param == 'week':
        records = records.filter(date__gte=datetime.date.today() - datetime.timedelta(days=7))
    if param == 'day':
        records = records.filter(date__gte=datetime.date.today() - datetime.timedelta(days=1))

    if count < 1 or ((count - 1) * 20 >= records.count() > 0):
        raise Http404("Page does not exist. Try .../dashboard/workplace/all_time/1/")

    next_flag = prev_flag = False
    if count > 1:
        prev_flag = True
    if count * 20 < records.count():
        next_flag = True

    return render(request, 'records/dashboard.html', {'records': records.order_by('-date')[(count - 1) * 20:count * 20],
                                                      'warning': check_budget(request.user),
                                                      'workflow_param': param,
                                                      'next': next_flag,
                                                      'prev': prev_flag,
                                                      'count_prev': count - 1,
                                                      'count_next': count + 1})


@login_required(login_url='records:login')
def dashboard_income_view(request, param='all_time', count=1):
    if param not in ('all_time', 'year', 'month', 'week', 'day'):
        raise Http404("Page does not exist. Try .../dashboard_income/workplace/all_time/1/")

    records = IncomeRecord.objects.filter(user=request.user)
    if param == 'year':
        records = records.filter(date__gte=datetime.date.today() - datetime.timedelta(days=365))
    if param == 'month':
        records = records.filter(date__gte=datetime.date.today() - datetime.timedelta(days=30))
    if param == 'week':
        records = records.filter(date__gte=datetime.date.today() - datetime.timedelta(days=7))
    if param == 'day':
        records = records.filter(date__gte=datetime.date.today() - datetime.timedelta(days=1))

    if count < 1 or ((count - 1) * 20 >= records.count() > 0):
        raise Http404("Page does not exist. Try .../dashboard_income/workplace/all_time/1/")

    next_flag = prev_flag = False
    if count > 1:
        prev_flag = True
    if count * 20 < records.count():
        next_flag = True

    return render(request, 'records/dashboard_income.html',
                  {'records': records.order_by('-date')[(count - 1) * 20:count * 20],
                   'warning': check_budget(request.user),
                   'workflow_param': param,
                   'next': next_flag,
                   'prev': prev_flag,
                   'count_prev': count - 1,
                   'count_next': count + 1})


@login_required(login_url='records:login')
def new_record_view(request, workflow_param):
    if workflow_param not in ('expense', 'income'):
        raise Http404("Page does not exist. Try .../dashboard/workplace/all_time/1/")

    success_flag = False
    if workflow_param == 'expense':
        if request.method == 'POST':
            form = ExpenseRecordForm(request.POST)
            if form.is_valid() and ExpenseRecord.objects.filter(user=request.user).count() < 1000:
                p = ExpenseRecord(user=request.user, value=form.cleaned_data['value'],
                                  category=form.cleaned_data['category'],
                                  text=form.cleaned_data['text'],
                                  type=form.cleaned_data['type'],
                                  date=datetime.datetime.now(),
                                  value_in_blr=convert(form.cleaned_data['value'], form.cleaned_data['type']))
                p.save()
                form = ExpenseRecordForm()
                success_flag = True
        else:
            form = ExpenseRecordForm()
    else:
        if request.method == 'POST':
            form = IncomeRecordForm(request.POST)
            if form.is_valid() and IncomeRecord.objects.filter(user=request.user).count() < 1000:
                p = IncomeRecord(user=request.user, value=form.cleaned_data['value'],
                                 text=form.cleaned_data['text'],
                                 type=form.cleaned_data['type'],
                                 date=datetime.datetime.now(),
                                 value_in_blr=convert(form.cleaned_data['value'], form.cleaned_data['type']))
                p.save()
                form = IncomeRecordForm()
                success_flag = True
        else:
            form = IncomeRecordForm()

    return render(request, 'records/new_record.html', {'form': form,
                                                       'warning': check_budget(request.user),
                                                       'workflow_param': workflow_param,
                                                       'success_flag': success_flag})


@login_required(login_url='records:login')
def remove_view(request, record_type, param, workflow_param):
    if (workflow_param not in ('all_time', 'year', 'month', 'week', 'day')) or (record_type not in (0, 1)):
        raise Http404("Page does not exist. Try .../dashboard/workplace/all_time/1/")

    if record_type:
        ExpenseRecord.objects.get(id=param).delete()
        str_url = 'records:dashboard'
    else:
        IncomeRecord.objects.get(id=param).delete()
        str_url = 'records:dashboard_income'

    return HttpResponseRedirect(reverse(str_url, kwargs={'param': workflow_param, 'count': 1}))


@login_required(login_url='records:login')
def profile_view(request):
    return render(request, 'records/profile.html', {'user': request.user,
                                                    'warning': check_budget(request.user)})


@login_required(login_url='records:login')
def menu_view(request):
    return render(request, 'records/menu.html', {'warning': check_budget(request.user)})


@login_required(login_url='records:login')
def search_view(request):
    income = expense = []
    flag = False

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data['date'].year, form.cleaned_data['date'].month, form.cleaned_data['date'].day)
            income = IncomeRecord.objects.filter(date__day=form.cleaned_data['date'].day,
                                                 date__month=form.cleaned_data['date'].month,
                                                 date__year=form.cleaned_data['date'].year)
            expense = ExpenseRecord.objects.filter(date__day=form.cleaned_data['date'].day,
                                                   date__month=form.cleaned_data['date'].month,
                                                   date__year=form.cleaned_data['date'].year)
            flag = True
    else:
        form = SearchForm()

    return render(request, 'records/search.html', {'form': form,
                                                   'warning': check_budget(request.user),
                                                   'income': income,
                                                   'expense': expense,
                                                   'flag': flag})


def check(curr):
    if not curr:
        curr = 0.0
    return curr


@login_required(login_url='record:login')
def category_view(request, workflow_param):
    category_list = []

    for category in EXPENSE_CATEGORY_CHOICES:
        category_list.append(CategoryStat(category[0],
                                          str("{:.2f}".format(check(ExpenseRecord.objects.filter(
                                              user=request.user,
                                              category=category[0],
                                              date__gte=datetime.date.today() - datetime.timedelta(days=365)).aggregate(
                                              Sum('value_in_blr'))['value_in_blr__sum']))),
                                          str("{:.2f}".format(check(ExpenseRecord.objects.filter(
                                              user=request.user,
                                              category=category[0],
                                              date__month=datetime.date.today().month).aggregate(
                                              Sum('value_in_blr'))['value_in_blr__sum']))),
                                          str("{:.2f}".format(check(ExpenseRecord.objects.filter(
                                              user=request.user,
                                              category=category[0],
                                              date__gte=datetime.date.today() - datetime.timedelta(days=7)).aggregate(
                                              Sum('value_in_blr'))['value_in_blr__sum']))),
                                          ))

    return render(request, 'records/category.html', {'category_list': category_list,
                                                     'warning': check_budget(request.user),
                                                     'workflow_param': workflow_param})


def check_budget(user):
    Budget.objects.filter(user=user, finish_time__lt=datetime.date.today()).delete()
    for x in [x.value - check(ExpenseRecord.objects.filter(user=user, date__gt=x.start_time).aggregate(
                                   Sum('value_in_blr'))['value_in_blr__sum'])
              for x in Budget.objects.filter(user=user)]:
        if x < 0:
            return True
    return False


@login_required(login_url='records:login')
def remove_limit_view(request, param):
    Budget.objects.get(pk=param).delete()
    return HttpResponseRedirect(reverse('records:budget'))


@login_required(login_url='records:login')
def budget_view(request):
    check_budget(request.user)

    success_flag = False
    error_str = ''

    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid() and Budget.objects.filter(user=request.user).count() < 10:
            p = Budget(user=request.user, value=form.cleaned_data['value'],
                       start_time=datetime.date.today(),
                       finish_time=datetime.date.today() + datetime.timedelta(days=form.cleaned_data['days']))
            p.save()
            form = BudgetForm()
            success_flag = True
        elif Budget.objects.filter(user=request.user).count() >= 10:
            error_str = 'Уже отслеживается слишком много балансов!'
        elif form.is_valid():
            error_str = 'Некорректно заполненная форма!'
    else:
        form = BudgetForm()

    budgets = [BudgetRemainder(x.pk, x.start_time.date(), x.finish_time.date(), str("{:.2f}".format(x.value)),
                               str("{:.2f}".format(x.value - check(ExpenseRecord.objects.filter(user=request.user,
                                date__gt=x.start_time).aggregate(Sum('value_in_blr'))['value_in_blr__sum']))))
               for x in Budget.objects.filter(user=request.user)]

    return render(request, 'records/budget.html', {'form': form,
                                                   'warning': check_budget(request.user),
                                                   'budgets': budgets,
                                                   'error_str': error_str,
                                                   'success_flag': success_flag})


@login_required(login_url='records:login')
def category_graph_view(request, param):
    if param not in ('year', 'month', 'week'):
        raise Http404("Page does not exist. Try .../dashboard/workplace/all_time/1/")

    days = 7
    if param == 'year':
        days = 365
    elif param == 'month':
        days = 30

    none_zero_categories = []
    values = []
    values_for_bar = []
    for category in EXPENSE_CATEGORY_CHOICES:
        if param == 'month':
            curr = str("{:.2f}".format(check(ExpenseRecord.objects.filter(user=request.user,
                                                      category=category[0],
                                                      date__month=datetime.date.today().month)
                         .aggregate(Sum('value_in_blr'))['value_in_blr__sum'])))
        else:
            curr = str("{:.2f}".format(check(ExpenseRecord.objects.filter(user=request.user,
                                                      category=category[0],
                                                      date__gte=datetime.date.today() - datetime.timedelta(days=days))
                         .aggregate(Sum('value_in_blr'))['value_in_blr__sum'])))

        if curr != '0.00':
            values.append(curr)
            none_zero_categories.append(category[0])
        values_for_bar.append(curr)

    buffer = io.BytesIO()

    fig = plt.figure(1, figsize=(10, 10))
    ax2 = plt.subplot(211)
    ax1 = plt.subplot(212)

    ax2.axis('equal')
    ax2.pie(values, labels=none_zero_categories, autopct='%1.1f%%')

    width = 0.3
    ax1.bar(np.arange(len(values_for_bar)), [float(x) for x in values_for_bar], width=width, color='royalblue')
    ax1.grid(color='#95a5a6', linestyle='--', linewidth=2, axis='y', alpha=0.7)
    ax1.set_ylabel('BYN')
    ax1.set_xticks(np.arange(len(values_for_bar)))
    ax1.set_xticklabels([x[0] for x in EXPENSE_CATEGORY_CHOICES])
    ax1.xaxis.set_tick_params(rotation=30, labelsize=10)

    fig.tight_layout()
    plt.grid(True)
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    pil_image = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pil_image.save(buffer, "PNG")
    pylab.close()

    return HttpResponse(buffer.getvalue(), content_type="image/png")


@login_required(login_url='records:login')
def analytics_view(request, workflow_param):
    if workflow_param not in ('year', 'month', 'week'):
        raise Http404("Page does not exist. Try .../dashboard/workplace/all_time/1/")

    sum_year = sum_month = sum_week = 0

    for elem in ExpenseRecord.objects.filter(user=request.user):
        if elem.date.date() > datetime.date.today() - datetime.timedelta(days=365):
            sum_year += elem.value_in_blr
        if elem.date.date() > datetime.date.today() - datetime.timedelta(days=30):
            sum_month += elem.value_in_blr
        if elem.date.date() > datetime.date.today() - datetime.timedelta(days=7):
            sum_week += elem.value_in_blr

    return render(request, 'records/analytics.html', {
        'warning': check_budget(request.user),
        'sum_year': str("{:.2f}".format(sum_year)),
        'sum_month': str("{:.2f}".format(sum_month)),
        'sum_week': str("{:.2f}".format(sum_week)),
        'workflow_param': workflow_param,
    })


@login_required(login_url='records:login')
def graph_view(request, param):
    if param not in ('year', 'month', 'week'):
        raise Http404("Page does not exist. Try .../dashboard/workplace/all_time/1/")

    buffer = io.BytesIO()
    x = []
    y = []
    data1 = []
    data2 = []

    fig = plt.figure(1, figsize=(10, 10))
    ax2 = plt.subplot(211)
    ax1 = plt.subplot(212)

    if param == 'week':
        fig.suptitle('График за последние 10 дней')
        for i in range(10):
            curr = datetime.date.today() - datetime.timedelta(days=i)
            expense_sum = sum([elem.value_in_blr for elem in ExpenseRecord.objects.filter(
                user=request.user,
                date__day=curr.day,
                date__month=curr.month,
                date__year=curr.year,
            )])
            x.append(curr)
            y.append(expense_sum)
            data1.append(expense_sum)
            data2.append(sum([elem.value_in_blr for elem in IncomeRecord.objects.filter(
                user=request.user,
                date__day=curr.day,
                date__month=curr.month,
                date__year=curr.year,
            )]))

    if param == 'month':
        fig.suptitle('График за 31 день')
        for i in range(31):
            curr = datetime.date.today() - datetime.timedelta(days=i)
            expense_sum = sum([elem.value_in_blr for elem in ExpenseRecord.objects.filter(
                user=request.user,
                date__day=curr.day,
                date__month=curr.month,
                date__year=curr.year,
            )])
            x.append(curr)
            y.append(expense_sum)
            data1.append(expense_sum)
            data2.append(sum([elem.value_in_blr for elem in IncomeRecord.objects.filter(
                user=request.user,
                date__day=curr.day,
                date__month=curr.month,
                date__year=curr.year,
            )]))

    if param == 'year':
        fig.suptitle('График за год')
        for i in range(12):
            month = datetime.datetime.now().month - i

            if month < 1:
                month += 12
                expense_sum = sum([elem.value_in_blr for elem in ExpenseRecord.objects.filter(
                    user=request.user,
                    date__month=month,
                    date__year=datetime.date.today().year - 1,
                )])
                x.append(MONTHS[month])
                y.append(expense_sum)
                data1.append(expense_sum)
                data2.append(sum([elem.value_in_blr for elem in IncomeRecord.objects.filter(
                    user=request.user,
                    date__month=month,
                    date__year=datetime.date.today().year - 1,
                )]))
            else:
                expense_sum = sum([elem.value_in_blr for elem in ExpenseRecord.objects.filter(
                    user=request.user,
                    date__month=month,
                    date__year=datetime.date.today().year,
                )])
                x.append(MONTHS[month])
                y.append(expense_sum)
                data1.append(expense_sum)
                data2.append(sum([elem.value_in_blr for elem in IncomeRecord.objects.filter(
                    user=request.user,
                    date__month=month,
                    date__year=datetime.date.today().year,
                )]))
        x.reverse()
        y.reverse()

    ax1.plot_date(x, y, 'go--')
    ax1.set_ylabel('BYN')
    ax1.set_title('Кривая расходов')
    ax1.grid(True)
    ax1.xaxis.set_tick_params(rotation=30, labelsize=10)

    width = 0.3
    ax2.bar(np.arange(len(x)) - width/2, data1[::-1], width=width, color='r', label='Расходы')
    ax2.bar(np.arange(len(x)) + width/2, data2[::-1], width=width, color='b', label='Доходы')
    ax2.grid(color='#95a5a6', linestyle='--', linewidth=2, axis='y', alpha=0.7)
    ax2.set_ylabel('BYN')
    ax2.set_xticks(np.arange(len(x)))
    if param != 'year':
        x = x[::-1]
    ax2.set_xticklabels(x)
    ax2.legend()
    ax2.xaxis.set_tick_params(rotation=30, labelsize=10)

    '''plt.gcf().autofmt_xdate()'''
    '''fig.autofmt_xdate()'''
    fig.tight_layout()
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    pil_image = PIL.Image.frombytes("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pil_image.save(buffer, "PNG")
    pylab.close()

    return HttpResponse(buffer.getvalue(), content_type="image/png")