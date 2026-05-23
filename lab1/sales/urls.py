from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('client/', views.client_base, name='client_base'),
    path('client/search/', views.client_search, name='client_search'),
    path('product/', views.product_base, name='product_base'),
    path('order/create', views.order_create, name='order_create'),
    path('order/', views.order_base, name='order_base'),
    path('product/add/', views.product_add, name='product_add')
]