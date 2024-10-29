from django import forms
from .models import Cut, Order, Column, Refrigerator

class SellMilasForm(forms.Form):
    cut = forms.ModelChoiceField(queryset=Cut.objects.all(), label="Seleccionar corte:")
    milas_to_sell = forms.IntegerField(min_value=1, label="Número milanesas vendidas:")

class FulfillOrderForm(forms.Form):
    tuppers_to_add = forms.IntegerField(
        label='Cantidad de tupper a agregar',
        min_value=0,
        required=False,
        initial=0,
    )
    refrigerator = forms.ChoiceField(
        choices=[],  # Initially empty, will populate in the view
        label="Seleccione heladera",
        required=True,
    )
    column = forms.ChoiceField(
        choices=[],  # Initially empty, will populate dynamically in JavaScript
        label="Seleccione la columna",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)
        super().__init__(*args, **kwargs)
        # Populate refrigerator choices as (id, name) tuples
        self.fields['refrigerator'].choices = [('', 'Select Refrigerator:')] + [(refrigerator.id, refrigerator.name) for refrigerator in Refrigerator.objects.all()]

        self.fields['column'].choices = [
            ('', 'Select Column:')
        ]

    def clean_tuppers_to_add(self):
        tuppers_to_add = self.cleaned_data['tuppers_to_add']
        if tuppers_to_add > self.order.tuppers_remaining:
            raise forms.ValidationError("You cannot add more tuppers than remaining.")
        return tuppers_to_add