from django.shortcuts import render, redirect
from .models import Refrigerator, Cut, Order, SubColumn, OrderAllocation, Column
from .forms import SellMilasForm, FulfillOrderForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.db.models import Sum
from collections import defaultdict
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

@login_required
def sell_milas(request):
    if request.method == 'POST':
        form = SellMilasForm(request.POST)
        if form.is_valid():
            cut = form.cleaned_data['cut']
            milas_to_sell = form.cleaned_data['milas_to_sell']

            try:
                cut.sell_milas(milas_to_sell, request.user)  # This will handle selling milas
                messages.success(request, f"Venta exitosa de {milas_to_sell} milanesas de {cut.name}!")
            except ObjectDoesNotExist:
                messages.error(request, "No milanesas available for this cut.")
            except ValueError as e:
                messages.error(request, str(e))  # Show the error message if there are insufficient milas
            return redirect('sell_milas')  # Redirect to the same page or somewhere else after success
    else:
        form = SellMilasForm()

    return render(request, 'inventory/sell_milas.html', {'form': form})

@login_required
def orders(request):
    unfulfilled_orders = Order.objects.filter(tuppers_remaining__gt=0)

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        processed_any_form = False

        try:
            order = Order.objects.get(id=order_id)  # Get the specific order being processed
            form = FulfillOrderForm(request.POST, order=order)

            if form.is_valid():
                tuppers_to_add = form.cleaned_data.get('tuppers_to_add')
                refrigerator_id = int(form.cleaned_data.get('refrigerator'))
                column_pos = int(form.cleaned_data.get('column')) - 1
                column = Column.get_column(refrigerator_id, column_pos)
                if tuppers_to_add:
                    try:
                        order.allocate_tuppers(column_id=column.id, tuppers_to_add=tuppers_to_add, user=request.user)
                        messages.success(request, f"Successfully fulfilled {tuppers_to_add} tuppers for {order.cut.name}!")
                        processed_any_form = True
                    except ValueError as e:
                        messages.error(request, str(e))  # Handle error if over-allocating tuppers
            else:
                print(form.errors)
                messages.error(request, f"Error fulfilling order for {order.cut.name}")

        except Order.DoesNotExist:
            messages.error(request, "Order not found.")

        if processed_any_form:
            return redirect('orders')

    forms = [(order, FulfillOrderForm(order=order)) for order in unfulfilled_orders]

    context = {'forms': forms}
    return render(request, 'inventory/orders.html', context)


def get_columns_for_refrigerator(request):
    refrigerator_id = request.GET.get('refrigerator_id')
    column_ids = Column.objects.filter(refrigerator_id=refrigerator_id).values_list('id', flat=True)
    return JsonResponse(list(column_ids), safe=False)


def expiration_tracking_view(request):
    allocations = OrderAllocation.objects.select_related('order', 'order__cut', 'column').order_by('order__cut__name', 'order__expiration_date')

    # Group allocations by `Order ID`
    grouped_allocations = defaultdict(list)
    for allocation in allocations:
        grouped_allocations[allocation.order.id].append(allocation)

    context = {
        'grouped_allocations': dict(grouped_allocations),  # Convert to regular dict for easier template access
    }

    return render(request, 'inventory/reports.html', context)