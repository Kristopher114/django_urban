from django.urls import path
from . import views

urlpatterns = [
    # --- Customer URLs ---
    path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/<str:category_name>/', views.menu_list_view, name='menu_list'),
    path('register/', views.register, name='register'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # --- Staff / Admin URLs ---
    path('staff/login/', views.staff_login, name='staff_login'), # Changed to staff/login/ for clarity
    path('staff/dashboard/', views.admin_dashboard, name='admin_dashboard'), # Added this!
    path('staff/manage/', views.manage_staff, name='manage_staff'),
]