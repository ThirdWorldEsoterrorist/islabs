from django.db import models

class Expense(models.Model):
    TYPE_CHOICES = [
        ('rent', 'Аренда помещения'),
        ('salary', 'Зарплата сотрудников'),
        ('utilities', 'Коммунальные услуги'),
        ('marketing', 'Маркетинг'),
        ('supplies', 'Закупка сырья'),
        ('transport', 'Логистика'),
    ]

    type = models.CharField(
        max_length=50,
        choices=TYPE_CHOICES,
        verbose_name="Тип издержки"
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Сумма (руб.)"
    )
    date = models.DateField(
        verbose_name="Дата учёта"
    )

    def __str__(self):
        return f"{self.get_type_display()} — {self.amount} руб. ({self.date})"
