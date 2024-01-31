from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, Income
# Create your views here.
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
import json
from django.http import JsonResponse, HttpResponse
from userpreferences.models import UserPreference
import datetime
import csv
from django.template.loader import render_to_string
import tempfile
from django.db.models import Sum
# Create your views here.


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = Income.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Income.objects.filter(
            date__istartswith=search_str, owner=request.user) | Income.objects.filter(
            description__icontains=search_str, owner=request.user) | Income.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    sources = Source.objects.all()
    income = Income.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/add_income.html', context)

        Income.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = Income.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income.date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated successfully')

        return redirect('income')


def delete_income(request, id):
    income = Income.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Record removed')
    return redirect('income')

# final summary
def income_source_summary(request):
    # check today's date
    todayDate= datetime.date.today()
    # six months ago
    sixmonthsAgo= todayDate-datetime.timedelta(days=30*6)
    incomes = Income.objects.filter(owner=request.user,date__gte=sixmonthsAgo, date__lte=todayDate)
    finalrep = {}

    def getSource(income):
        return income.source

    sourceList = list(set(map(getSource, incomes)))

    def getIncomeSourceAmount(source):
        amount = 0

        filteredBysource = incomes.filter(source=source)

        for item in filteredBysource:
            amount += item.amount
        return amount

    for n in incomes:
        for o in sourceList:
            finalrep[o] = getIncomeSourceAmount(o)

    return JsonResponse({'income_source_data':finalrep}, safe=False)

def stats_view(request):
    return render(request, 'income/stats.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']= ('attachment: filename=Incomes'+\
                                      str(datetime.datetime.now())+'csv')

    writer= csv.writer(response)
    writer.writerow(['Amount','Description','Source','Date'])

    incomes = Income.objects.filter(owner=request.user)

    for income in incomes:
        writer.writerow([income.amount,income.description,income.source,income.date])

    return response
