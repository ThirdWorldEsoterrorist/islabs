from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('create/', views.create_data, name='create_data'),
    path('process/', views.process_data, name='process_data'),
]