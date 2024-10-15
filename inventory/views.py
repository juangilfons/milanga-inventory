from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from inventory.models import Refrigerator


# Create your views here.

@login_required
def inventory(request):
    refrigerators = Refrigerator.objects.prefetch_related('column_set__subcolumn_set')
    context = {
        'refrigerators': refrigerators,
    }
    return render(request, 'inventory/inventory.html', context)
