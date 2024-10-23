from django import forms
from .models import Cut, Order, Column

class SellMilasForm(forms.Form):
    cut = forms.ModelChoiceField(queryset=Cut.objects.all(), label="Select Cut")
    milas_to_sell = forms.IntegerField(min_value=1, label="Number of Milas to Sell")