from django.db import models

#модель сотрудника
class Employee(models.Model):
    ROLE_CHOICES = ( #варианты выбора должности
        ('guest', 'Гость'),
        ('secret', 'Секретарь'),
        ('undir', 'Заместитель директора'),
        ('dir', 'Директор'),
    )
    #verbose_name - для отображения названий, за что каждое поле отвечает, в форме (см. list.html)
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    middle_name = models.CharField(max_length=50, verbose_name="Отчество")
    login = models.CharField(max_length=50, unique=True, verbose_name="Логин")
    password = models.CharField(max_length=128, verbose_name="Пароль", blank=True, null=True)
    role = models.CharField(max_length=20,  verbose_name="Должность", choices=ROLE_CHOICES,
                default='guest')
    address = models.CharField(max_length=255, verbose_name="Адрес", blank=True)

    work_phone = models.CharField(max_length=17, blank=True, verbose_name="Рабочий телефон")
    personal_phone = models.CharField(max_length=17, blank=True, verbose_name="Личный телефон")
