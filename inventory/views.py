from django.shortcuts import render
from django.contrib.auth.decorators import login_required

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
