from django.urls import path
from . import views

urlpatterns = [
    path('login/',  views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),

    path('register/', views.register, name='register'),

    path('profile/',              views.customer_profile, name='customer_profile'),
    path('profile/edit/',         views.edit_profile,     name='edit_profile'),
    path('customers/',            views.customer_list,    name='customer_list'),
    path('customers/<int:pk>/',   views.customer_detail,  name='customer_detail'),
    path('customers/<int:pk>/delete/', views.delete_customer, name='delete_customer'),
]