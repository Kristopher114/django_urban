from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Pointing to views.menu_list instead of views.home
    path('', views.menu_list, name='menu_list'), 

    # --- STAFF INVENTORY URLS ---
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.product_create, name='product_create'),
    path('inventory/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('inventory/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('category/add/', views.category_create, name='category_create'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),
]