from django.shortcuts import render

from inventory.models import Refrigerator, SubColumn

from .forms import HeladeraForm
from .models import Refrigerator


# Create your views here.

def inventory(request):
    if request.method == 'POST':
        form = HeladeraForm(request.POST)
        if form.is_valid():
            Heladera = Refrigerator(name=form.cleaned_data['name'])
            Heladera.save()
    sub_columns = SubColumn.objects.all()

    heladeras = Refrigerator.objects.all()
    form = HeladeraForm()
    return render(request, 'inventory/inventory.html', {'sub_columns': sub_columns, 'heladeras': heladeras, 'form': form})
