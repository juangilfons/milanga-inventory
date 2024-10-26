from django.urls import path

from . import views


urlpatterns = [
    path('', views.inventory, name='inventory'),
    path('refrigerators/', views.display_refrigerators, name='refrigerators'),
    path('sell-milas/', views.sell_milas_view, name='sell_milas'),
    path('supplier/', views.supplier_page, name='supplier'),
    path('inventory/', views.inventory_page, name='inventory'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('ajax/get-columns/', views.get_columns_for_refrigerator, name='get_columns_for_refrigerator'),
    path('expiration/', views.expiration_tracking_view, name='expiration'), 
]