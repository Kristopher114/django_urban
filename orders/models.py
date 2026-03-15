from django.db import models
from django.contrib.auth.models import User

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    ORDER_STATUS_CHOICES = (
        ('Pending', 'Pending'),               # 1. Customer clicked checkout, order received.
        ('Preparing', 'Preparing in Kitchen'),# 2. Staff accepted it and is making the food/drinks.
        ('Ready', 'Ready for Pickup/Rider'),  # 3. Food is bagged and waiting at the counter.
        ('Out for Delivery', 'Out for Delivery'), # 4. The rider has left the shop.
        ('Completed', 'Delivered & Completed'),   # 5. Customer received it safely!
        ('Canceled', 'Canceled'),             # 6. Customer or Staff canceled it (e.g., out of stock).
    )
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Payment(models.Model):
    # 1. Define explicit choices so your database stays clean
    # (No spelling mistakes like 'Paypal' vs 'PayPal' vs 'paypal')
    PAYMENT_METHODS = (
        ('PayPal', 'PayPal'),
        ('COD', 'Cash on Delivery'),
        ('Cash', 'In-Store Cash'), # In case your POS needs to use this table too!
    )

    PAYMENT_STATUS = (
        ('Pending', 'Pending'),       # Used when COD is chosen, or PayPal is loading
        ('Completed', 'Completed'),   # Used when PayPal succeeds, or COD cash is handed over
        ('Failed', 'Failed'),         # Used if a card declines on PayPal
        ('Refunded', 'Refunded'),
    )

    # Added related_name='payment' so you can easily do `order.payment.status` later
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Apply the choices we made above
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='Pending')
    
    # 2. CRITICAL FOR APIs: The Transaction ID
    # Allow this to be blank/null because COD orders won't have one initially
    transaction_id = models.CharField(max_length=100, blank=True, null=True, help_text="PayPal Transaction ID")

    # 3. Use standard naming for timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # Automatically updates when status changes!

    def __str__(self):
        return f"{self.payment_method} - Order #{self.order.id} ({self.status})"