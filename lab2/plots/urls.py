from django.urls import path
from . import views

urlpatterns = [
    path('', views.monitor_view, name='monitor_view'),
]