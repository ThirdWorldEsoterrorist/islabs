from django.urls import path
from . import views #для ссылки на функции в views.py

urlpatterns = [
    path('', views.login, name='login'), #основная страница: авторизация
    path('logout/', views.logout, name='logout'), #выйти на страницу авторизации
    path('list/', views.employee_list, name='employee_list'), #список сотрудников (после успешной авторизации)
    path('create/', views.create_employee, name='create_employee'), #создание нового сотрудника
    path('edit/<int:emp_id>/', views.edit_employee, name='edit_employee'), #редактирование существующего сотрудника
    path('delete/<int:emp_id>/', views.delete_employee, name='delete_employee'), #удалить существующего сотрудника
]