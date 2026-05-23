from django.db import models

class Contragent(models.Model):
    registration_date = models.DateField(verbose_name="Дата регистрации")
    ogrn = models.CharField(max_length=15, verbose_name="ОГРН")
    inn = models.CharField(max_length=12, verbose_name="ИНН", blank=True, null=True)
    kpp = models.CharField(max_length=9, verbose_name="КПП")
    short_name = models.CharField(max_length=128, verbose_name="Краткое название")
    full_name = models.CharField(max_length=128, verbose_name="Полное название")
    address = models.CharField(max_length=128, verbose_name="Адрес")
    position = models.CharField(max_length=64, verbose_name="Должность")
    full_fio = models.CharField(max_length=128, verbose_name="ФИО")
    initials_fio = models.CharField(max_length=128, verbose_name="Фамилия и инициалы", editable=False)

    #перегрузка функции объекта .save()
    def save(self, *args, **kwargs):
        # при создании нового объекта автоматически генерится initials_fio
        parts = self.full_fio.split()
        if len(parts) >= 3:
            self.initials_fio = f"{parts[0]} {parts[1][0]}.{parts[2][0]}."
        elif len(parts) == 2:
            self.initials_fio = f"{parts[0]} {parts[1][0]}."
        else:
            self.initials_fio = self.full_fio
        super().save(*args, **kwargs)

    def __str__(self):
        return self.short_name
