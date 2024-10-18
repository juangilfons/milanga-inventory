from django.contrib import admin
from .models import Refrigerator, Column, Cut, SubColumn, Order
# Register your models here.

admin.site.register(Refrigerator)
admin.site.register(Column)
admin.site.register(Cut)
admin.site.register(SubColumn)
admin.site.register(Order)