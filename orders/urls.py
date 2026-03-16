from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # ... any other order URLs you might have ...
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.customer_orders, name='customer_orders'),

    # Add these below your checkout url
    path('payment/<int:order_id>/', views.paypal_payment, name='paypal_payment'),
    path('payment-complete/', views.payment_complete, name='payment_complete'),
    # The checkout endpoint for the POS
    path('staff/orders/', views.staff_order_list, name='staff_order_list'),
    path('staff/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('pos/checkout/', views.process_checkout, name='process_checkout'),
]