from django.contrib import admin
from .models import Refrigerator, Column, Cut, SubColumn, Order, ActionLog, OrderAllocation
from .forms import RefrigeratorForm
# Register your models here.

# admin.site.register(Refrigerator)
# admin.site.register(Column)
# admin.site.register(Cut)
# admin.site.register(SubColumn)
# admin.site.register(Order)
# admin.site.register(OrderAllocation)

class OrderAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['cut', 'tuppers_requested', 'tuppers_remaining', 'scheduled_date', 'expiration_date']
        else:  # Creating a new object
            return ['cut', 'tuppers_requested', 'scheduled_date']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['expiration_date', 'tuppers_remaining']
        return []  # No readonly fields when creating

admin.site.register(Order, OrderAdmin)

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_role', 'action_type', 'object_repr', 'action_description', 'action_time')
    list_filter = ('user_role', 'action_type', 'user')
    search_fields = ('object_repr', 'action_description')


admin.site.register(ActionLog, ActionLogAdmin)

class CutAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['name', 'milas_per_tupper', 'reorder_threshold', 'reorder_tuppers', 'is_order_pending', 'color', 'days_until_expiration']
        else:  # Creating a new object
            return ['name', 'milas_per_tupper', 'reorder_threshold', 'reorder_tuppers', 'color', 'days_until_expiration']

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['is_order_pending']
        return []  # No readonly fields when creating

admin.site.register(Cut, CutAdmin)

class ColumnInline(admin.TabularInline):
    model = Column
    extra = 0
    fields = ['capacity']

@admin.register(Refrigerator)
class RefrigeratorAdmin(admin.ModelAdmin):
    form = RefrigeratorForm
    inlines = [ColumnInline]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.save()
            form.save(commit=True)
        else:
            return super().save_model(request, obj, form, change)