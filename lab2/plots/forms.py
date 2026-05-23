from django import forms

class DataForm(forms.Form):
    value = forms.FloatField(label="Введите число", error_messages={'invalid': "Ошибка: неверный формат вводных данных"})

class FilterForm(forms.Form):
    min_val = forms.FloatField(required=False, label="Нижняя граница")
    max_val = forms.FloatField(required=False, label="Верхняя граница")
    divisor = forms.FloatField(required=False, label="Кратные числу")