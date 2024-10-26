from django.contrib import admin

from .models import Refrigerator, Column, Cut, SubColumn, Order, ActionLog, OrderAllocation
# Register your models here.

admin.site.register(Refrigerator)
admin.site.register(Column)
admin.site.register(Cut)
admin.site.register(SubColumn)
admin.site.register(Order)
admin.site.register(OrderAllocation)

class ActionLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_role', 'action_type', 'object_repr', 'action_description', 'action_time')
    list_filter = ('user_role', 'action_type', 'user')
    search_fields = ('object_repr', 'action_description')


admin.site.register(ActionLog, ActionLogAdmin)
