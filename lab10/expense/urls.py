from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('table/', views.expense_table, name='expense_table'),
    path('report/', views.create_report, name='create_report'),
    path('add/', views.add_expense, name='add_expense'),
]