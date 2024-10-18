from django import forms
from .models import Cut, Order, Column

class SellMilasForm(forms.Form):
    cut = forms.ModelChoiceField(queryset=Cut.objects.all(), label="Select Cut")
    milas_to_sell = forms.IntegerField(min_value=1, label="Number of Milas to Sell")

class FulfillOrderForm(forms.Form):
    tuppers_to_add = forms.IntegerField(
        label='Tuppers to Add',
        min_value=0,
        required=False,
        initial=0,
    )
    column = forms.ModelChoiceField(
        queryset=Column.objects.all(),  # This will be dynamically populated in the view
        label="Select Column",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)  # Get the specific order being fulfilled
        super().__init__(*args, **kwargs)
    
    def clean_tuppers_to_add(self):
        tuppers_to_add = self.cleaned_data['tuppers_to_add']
        if tuppers_to_add > self.order.tuppers_remaining:
            raise forms.ValidationError("You cannot add more tuppers than remaining.")
        return tuppers_to_add