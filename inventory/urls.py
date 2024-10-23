from django.urls import path

from . import views


urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('sell_milas/', views.sell_milas, name='sell_milas'),
    path('orders/', views.orders, name='orders'),
]