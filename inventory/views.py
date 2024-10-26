from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from .forms import SellMilasForm
from inventory.models import Refrigerator, Cut


# Create your views here.

@login_required
def inventory(request):
    refrigerators = Refrigerator.objects.prefetch_related('column_set__subcolumn_set')
    cuts = Cut.objects.all()

    context = {
        'refrigerators': refrigerators,
        'cuts': cuts
    }
    return render(request, 'inventory/inventory.html', context)

def sell_milas(request):
    if request.method == 'POST':
        form = SellMilasForm(request.POST)
        if form.is_valid():
            cut = form.cleaned_data['cut']
            milas_to_sell = form.cleaned_data['milas_to_sell']

            try:
                cut.sell_milas(milas_to_sell)  # This will handle selling milas
                messages.success(request, f"Venta exitosa de {milas_to_sell} milanesas de {cut.name}!")
            except ObjectDoesNotExist:
                messages.error(request, "No milanesas available for this cut.")
            except ValueError as e:
                messages.error(request, str(e))  # Show the error message if there are insufficient milas
            return redirect('sell_milas')  # Redirect to the same page or somewhere else after success
    else:
        form = SellMilasForm()

    return render(request, 'inventory/sell_milas.html', {'form': form})

def orders(request):
    return render(request, 'inventory/orders.html')