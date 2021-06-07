from bs4 import BeautifulSoup
import requests

from records.models import Rate


def convert(value, type):
    if type == 'BLR':
        return value
    if type == 'RUB':
        return value * Rate.objects.get(count='100 RUB').value / 100
    if type == 'UAH':
        return value * Rate.objects.get(count='100 UAH').value / 100
    if type == 'PLN':
        return value * Rate.objects.get(count='10 PLN').value / 10
    if type == 'USD':
        return value * Rate.objects.get(count='1 USD').value
    if type == 'EUR':
        return value * Rate.objects.get(count='1 EUR').value


def update_rates():
    try:
        page = requests.get('https://www.nbrb.by/statistics/rates/ratesDaily.asp')
    except requests.exceptions.RequestException:
        return 1

    if page.status_code != 200:
        print('Error ', page.status_code)
        return 2

    names = []
    count = []
    value = []
    soap = BeautifulSoup(page.text, 'html.parser')

    for it in soap.findAll('span', class_='text'):
        names.append(it.text)

    for it in soap.findAll('td', class_='curAmount'):
        count.append(it.text)

    for it in soap.findAll('td', class_='curCours'):
        value.append(float(it.text[1:].replace(',', '.')))

    Rate.objects.all().delete()
    for i in range(len(names)):
        rate = Rate.objects.create(name=names[i], count=count[i], value=value[i])
        rate.save()

    return 0