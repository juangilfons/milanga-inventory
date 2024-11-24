from django import forms
from .models import Cut, Order, Column, Refrigerator

class SellMilasForm(forms.Form):
    cut = forms.ModelChoiceField(queryset=Cut.objects.all(),label="Seleccionar corte:", required=True)
    tuppers_to_sell = forms.IntegerField(
        min_value=1,
        label="Número de tuppers vendidos:",
        required=False,
    )
    milas_to_sell = forms.IntegerField(
        min_value=1,
        label="Número de milanesas vendidas:",
        required=False,
    )

    def clean_milas_to_sell(self):
        data = self.cleaned_data.get('milas_to_sell')
        return int(data) if data not in (None, '') else 0

    def clean_tuppers_to_sell(self):
        data = self.cleaned_data.get('tuppers_to_sell')
        return int(data) if data not in (None, '') else 0

    def clean(self):
        cleaned_data = super().clean()
        milas_to_sell = cleaned_data.get('milas_to_sell')
        tuppers_to_sell = cleaned_data.get('tuppers_to_sell')

        if not milas_to_sell and not tuppers_to_sell:
            raise forms.ValidationError("Debe ingresar al menos un valor en 'Número de milanesas' o 'Número de tappers'.")
        
        return cleaned_data

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


        self.fields['column'].choices = [('', 'Select Column:')]
        if 'refrigerator' in self.data:
            try:
                refrigerator_id = int(self.data.get('refrigerator'))
                self.fields['column'].choices += [
                    (index + 1, index + 1)
                    for index, column in enumerate(Column.objects.filter(refrigerator_id=refrigerator_id).order_by('id'))
                ]
            except (ValueError, TypeError):
                # If there's an issue with refrigerator_id, keep column choices empty
                self.fields['column'].choices = []


    def clean_tuppers_to_add(self):
        tuppers_to_add = self.cleaned_data['tuppers_to_add']
        if tuppers_to_add > self.order.tuppers_remaining:
            raise forms.ValidationError("No puedes guardar mas tuppers.")
        return tuppers_to_add

class RefrigeratorForm(forms.ModelForm):
    num_columns = forms.IntegerField(
        min_value=1,
        required=True,
        initial=1,
    )
    default_capacity = forms.IntegerField(
        min_value=1,
        required=True,
        initial=1,
    )

    class Meta:
        model = Refrigerator
        fields = ['name']
    
    def save(self, commit=True):
        refrigerator = super().save(commit=commit)
        if commit:
            refrigerator.create_columns(
                num_columns=self.cleaned_data['num_columns'],
                default_capacity=self.cleaned_data['default_capacity'],
            )
        return refrigerator