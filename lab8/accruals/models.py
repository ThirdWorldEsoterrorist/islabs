from django.db import models

class Accrual(models.Model):
    employee_id = models.CharField(max_length=50, verbose_name="Номер сотрудника")
    full_name = models.CharField(max_length=255, verbose_name="Полное имя")
    payment = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Сумма начисления")

    def __str__(self):
        return f"{self.full_name} ({self.employee_id}) — {self.payment} руб."
