from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('cars/', views.cars_view, name='cars'),
    path('drivers/', views.drivers_view, name='drivers'),
    path('trips/', views.trips_view, name='trips'),
]