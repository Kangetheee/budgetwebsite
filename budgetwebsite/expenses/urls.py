from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('',views.index, name="expenses"),
    path('add-expense', views.add_expense, name="add-expenses"),
    path('edit_expense/<int:id>', views.expense_edit, name="expense-edit"),
    path('expense_delete/<int:id>', views.expense_delete, name="delete_expense"),
    path('search-expenses', csrf_exempt(views.search_expense), name="search-expense"),
    path('expense_category_summary', views.expense_category_summary, name="expense_category_summary"),
    path('stats', views.stats_view,name="stats"),
    path('export_csv', views.export_csv, name="export-csv"),
    # path('export_pdf', views.export_pdf, name="export-pdf"),
]