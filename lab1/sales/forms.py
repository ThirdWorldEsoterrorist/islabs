from django import forms
from .models import *
from django.forms import inlineformset_factory

class ClientSearchForm(forms.Form):
    search = forms.CharField(
        label='Поиск по имени',
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Имя клиента...'})
    )


class ProductAddForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'stock']
        labels = {
            'name': 'Название товара',
            'price': 'Цена (для нового товара)',
            'stock': 'Количество товара',
        }
    price_error = ""
    stock_error = ""


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'payment']