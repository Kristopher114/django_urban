from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Pointing to views.menu_list instead of views.home
    path('', views.menu_list, name='menu_list'), 

    # --- STAFF INVENTORY URLS ---
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.product_create, name='product_create'),
]