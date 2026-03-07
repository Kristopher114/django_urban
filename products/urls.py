from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Pointing to views.menu_list instead of views.home
    path('', views.menu_list, name='menu_list'), 
]