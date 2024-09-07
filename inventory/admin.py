from xmlrpc.client import Fault

from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Refrigerator)
admin.site.register(Column)
admin.site.register(Cut)
admin.site.register(SubColumn)

