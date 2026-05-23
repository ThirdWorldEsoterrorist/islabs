from django.urls import path
from . import views #для ссылки на функции в views.py

urlpatterns = [
    path('', views.agent_list, name='agent_list'),
    path('check_inn/', views.check_inn, name='check_inn'),
    path('create/', views.create_agent, name='create_agent'),
    path('delete/<int:pk>/', views.delete_agent, name='delete_agent'),
]