from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('accrual/', views.add_accrual, name='add_accrual'),
]