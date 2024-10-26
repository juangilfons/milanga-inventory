from django.shortcuts import render, redirect
from .models import Refrigerator, Cut, Order, SubColumn
from .forms import SellMilasForm, FulfillOrderForm
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import JsonResponse
# Create your views here.

def inventory(request):
    return render(request, 'inventory/inventory.html')

def display_refrigerators(request):
    refrigerators = Refrigerator.objects.all()
    cuts = Cut.objects.all() 
    context = {
        'refrigerators': refrigerators,
        'cuts': cuts
    }
    return render(request, 'refrigerators.html', context)

def sell_milas_view(request):
    if request.method == 'POST':
        form = SellMilasForm(request.POST)
        if form.is_valid():
            cut = form.cleaned_data['cut']
            milas_to_sell = form.cleaned_data['milas_to_sell']

            try:
                cut.sell_milas(milas_to_sell, request.user)  # This will handle selling milas
                messages.success(request, f"Successfully sold {milas_to_sell} milas from {cut.name}!")
            except ObjectDoesNotExist:
                messages.error(request, "No milanesas available for this cut.")
            except ValueError as e:
                messages.error(request, str(e))  # Show the error message if there are insufficient milas
            return redirect('sell_milas')  # Redirect to the same page or somewhere else after success
    else:
        form = SellMilasForm()

    return render(request, 'sell_milas.html', {'form': form})

def supplier_page(request):
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
            return redirect('supplier')

    forms = [(order, FulfillOrderForm(order=order)) for order in unfulfilled_orders]

    context = {'forms': forms}
    return render(request, 'supplier_page.html', context)

def inventory_page(request):
    cuts = Cut.objects.all()
    context = {'cuts': cuts}

    return render(request, 'inventory_page.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('inventory_page')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('inventory')

from django.http import JsonResponse
from .models import Column

def get_columns_for_refrigerator(request):
    refrigerator_id = request.GET.get('refrigerator_id')
    column_ids = Column.objects.filter(refrigerator_id=refrigerator_id).values_list('id', flat=True)
    return JsonResponse(list(column_ids), safe=False)
