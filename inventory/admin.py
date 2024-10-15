from django.contrib import admin
from .models import Refrigerator, Column, SubColumn, Cut

# Register your models here.
admin.site.register(Refrigerator)
admin.site.register(Column)
admin.site.register(SubColumn)
admin.site.register(Cut)
