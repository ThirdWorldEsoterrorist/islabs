from django import forms
from .models import *
from django.core.exceptions import ValidationError

class ReportForm(forms.Form):
    title = forms.CharField(
        max_length=150,
        label="Заголовок отчета",
        widget=forms.TextInput(attrs={'placeholder': 'Введите название отчета'})
    )
    type = forms.ChoiceField(
        choices=Expense.TYPE_CHOICES,
        label="Тип издержки"
    )
    start_date = forms.DateField(
        label="Начальная дата",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label="Конечная дата",
        widget=forms.DateInput(attrs={'type': 'date'})
    )

# НОВАЯ ФОРМА: Для добавления издержки
class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['type', 'amount', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'placeholder': '0.00'}),
        }