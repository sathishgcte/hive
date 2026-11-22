from django import forms
from .models import Flat, Payment, Expense

class FlatForm(forms.ModelForm):
    class Meta:
        model = Flat
        fields = ['number', 'resident_name', 'monthly_maintenance', 'active']

class MonthForm(forms.Form):
    month = forms.DateField(input_formats=['%Y-%m'], widget=forms.DateInput(format='%Y-%m', attrs={'type': 'month'}))

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['date', 'amount', 'mode', 'reference']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['date', 'category', 'description', 'amount', 'mode']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}
