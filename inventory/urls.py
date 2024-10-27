from django.urls import path

from . import views


urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('sell_milas/', views.sell_milas, name='sell_milas'),
    path('orders/', views.orders, name='orders'),
    path('ajax/get-columns/', views.get_columns_for_refrigerator, name='get_columns_for_refrigerator'),
    path('expiration/', views.expiration_tracking_view, name='reports'),
]