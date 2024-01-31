from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Category, Expense
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
def search_expense(request):
    if request.method == 'POST':
        searchStr = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=searchStr, owner=request.user) | Expense.objects.filter(
            date__istartswith=searchStr, owner=request.user) | Expense.objects.filter(
            description__icontains=searchStr, owner=request.user) | Expense.objects.filter(
            category__icontains=searchStr, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)



@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expense = Expense.objects.filter(owner=request.user)
    # sectioning expenses into pages
    paginator = Paginator(expense, 2)
    pageNumber = request.GET.get('pageObj')
    pageObj = Paginator.get_page(paginator, pageNumber)
    currency = UserPreference.objects.get(user=request.user).currency
    context ={
        'expenses':expense,
        'pageObj': pageObj,
        'currency': currency,
    }
    return render(request, 'expenses/index.html', context)
@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)


    if request.method == 'POST':
        amount = request.POST['amount']
        # import pdb
        # pdb.set_trace()

        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'expenses/add_expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']


        if not description:
            messages.error(request, 'Description is Required')
            return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(owner=request.user,amount=amount, date=date, description=description, category=category)
        messages.success(request, 'Expense Saved')
        return redirect('expenses')

@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    expense = Expense.objects.get(pk=id)
    categories = Category.objects.all()

    context = {
        'expense': expense,
        'values': expense,
        'categories':categories
    }
    if request.method == 'GET':
        return render(request, 'expenses/edit_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        # import pdb
        # pdb.set_trace()

        if not amount:
            messages.error(request, 'Amount is Required')
            return render(request, 'expenses/edit_expense.html', context)
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not description:
            messages.error(request, 'Description is Required')
            return render(request, 'expenses/edit_expense.html', context)

        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.save()

        messages.success(request, 'Expense Update Saved')
        return redirect('expenses')

def expense_delete(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, 'Expense Deleted')
    return redirect('expenses')

# final summary
def expense_category_summary(request):
    # check today's date
    todayDate= datetime.date.today()
    # six months ago
    sixmonthsAgo= todayDate-datetime.timedelta(days=30*6)
    expenses = Expense.objects.filter(owner=request.user,date__gte=sixmonthsAgo, date__lte=todayDate)
    finalrep = {

    }

    def getCategory(expense):
        return expense.category

    categoryList = list(set(map(getCategory, expenses)))

    def getExpenseCategoryAmount(category):
        amount = 0

        filteredBycategory = expenses.filter(category=category)

        for item in filteredBycategory:
            amount += item.amount
        return amount

    for n in expenses:
        for o in categoryList:
            finalrep[o] = getExpenseCategoryAmount(o)

    return JsonResponse({'expense_category_data':finalrep}, safe=False)

def stats_view(request):
    return render(request, 'expenses/stats.html')

def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition']= ('attachment: filename=Expenses'+\
                                      str(datetime.datetime.now())+'csv')

    writer= csv.writer(response)
    writer.writerow(['Amount','Description','Category','Date'])

    expenses = Expense.objects.filter(owner=request.user)

    for expense in expenses:
        writer.writerow([expense.amount,expense.description,expense.category,expense.date])

    return response

# def export_pdf(request):
 #   response = HttpResponse(content_type='application/pdf')
  #  response['Content-Disposition'] = 'inlineattachment: filename=Expenses' + \
  #                                     str(datetime.datetime.now()) + '.pdf'

  #  response['Content-Transfer-Encoding'] = 'binary'

  #  htmlString = render_to_string('expenses/pdfOutput.html',{'expenses':[], 'total':0 })
  #  html=HTML(string=htmlString)

 #   result = html.write_pdf()

 #   with tempfile.NamedTemporaryFile(delete=True) as output:
  #      output.write(result)
  #      output.flush()

   #     output= open(output.name, 'rb')
   #     response.write(output.read())

   # return response