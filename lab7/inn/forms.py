from .models import Contragent
from django import forms

class ContragentForm(forms.ModelForm):
    class Meta:
        model = Contragent
        fields = '__all__'
        widgets = {'registration_date': forms.DateInput(attrs={'type': 'date'})}
