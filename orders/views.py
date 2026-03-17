import json
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Import your models from both apps!
from products.models import Product
from orders.models import Order, OrderItem, Payment
from django.utils import timezone
import datetime
from django.db.models import Sum, Avg

def is_store_open():
    """Returns True if current time is within operating hours (8am - 8pm)"""
    # Get the current local time in Asia/Manila
    current_time = timezone.localtime().time()
    
    # Set your open and close times (24-hour format)
    opening_time = datetime.time(1, 0)   # 8:00 AM
    closing_time = datetime.time(23, 0 )  # 8:00 PM
    
    return opening_time <= current_time <= closing_time

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # 1. Grab the cart from the session, or create an empty one if it doesn't exist yet
        cart = request.session.get('customer_cart', {})
        
        # Session keys must be strings!
        prod_id = str(product.id) 
        
        # 2. If the item is already in the cart, add 1 to the quantity
        if prod_id in cart:
            cart[prod_id]['quantity'] += 1
        # 3. Otherwise, add the item to the cart for the first time
        else:
            cart[prod_id] = {
                'name': product.name,
                'price': str(product.price), # Convert decimals to strings for session storage
                'quantity': 1,
            }
            
        # 4. Save the updated cart back to the session
        request.session['customer_cart'] = cart
        request.session.modified = True
        
        messages.success(request, f"{product.name} was added to your cart!")
        
        # Redirect the user right back to the page they were just on
        return redirect(request.META.get('HTTP_REFERER', 'customer_dashboard'))

@login_required
def view_cart(request):
    # Grab the cart from the session (or an empty dictionary if they haven't added anything yet)
    cart = request.session.get('customer_cart', {})
    
    cart_items = []
    subtotal = Decimal('0.00')
    
    # Loop through the session data to build our display list and do the math
    for product_id, item_data in cart.items():
        price = Decimal(item_data['price'])
        quantity = item_data['quantity']
        item_total = price * quantity
        
        subtotal += item_total
        
        cart_items.append({
            'product_id': product_id,
            'name': item_data['name'],
            'price': price,
            'quantity': quantity,
            'total': item_total
        })
        
    # Calculate tax and final total
    tax = subtotal * Decimal('0.12')
    total = subtotal + tax
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
        'is_open': is_store_open(), # PASS THE OPEN STATUS TO THE HTML
    }
    return render(request, 'customers/cart.html', context)

@login_required
def remove_from_cart(request, product_id):
    if request.method == 'POST':
        # 1. Grab the current cart
        cart = request.session.get('customer_cart', {})
        prod_id = str(product_id)
        
        # 2. Check if the item actually exists in the cart before trying to delete it
        if prod_id in cart:
            item_name = cart[prod_id]['name'] # Save name for the success message
            
            # 3. Delete it from the dictionary
            del cart[prod_id]
            
            # 4. Save the updated cart back to the session
            request.session['customer_cart'] = cart
            request.session.modified = True
            
            messages.success(request, f"{item_name} was removed from your cart.")
            
    # Redirect right back to the cart page
    return redirect('orders:view_cart')

@login_required(login_url='login') # Force users to log in before checking out!
def checkout(request):
    # 1. NEW: Check if the store is actually open!
    if not is_store_open():
        messages.error(request, "Sorry, we are currently closed! Operating hours are 8:00 AM to 8:00 PM.")
        return redirect('orders:view_cart')

    cart = request.session.get('customer_cart', {})

    # If they try to go to checkout with an empty cart, kick them back to the menu
    if not cart:
        messages.warning(request, "Your cart is empty! Please add some items first.")
        return redirect('products:menu_list')

    # 1. Calculate the math safely on the backend
    subtotal = Decimal('0.00')
    for product_id, item_data in cart.items():
        subtotal += Decimal(item_data['price']) * item_data['quantity']
        
    tax = subtotal * Decimal('0.12')
    total = subtotal + tax

    # 2. Handle the Form Submission
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method') # Will be 'COD' or 'PayPal'
        address = request.POST.get('delivery_address')
        phone = request.POST.get('phone_number')

        # Step A: Create the Order (Make sure you add address/phone to your models.py!)
        order = Order.objects.create(
            user=request.user,
            status='Pending',
            total_amount=total,
            # delivery_address=address,  <-- Add these to your Order model
            # phone_number=phone
        )

        # Step B: Loop through the cart to create OrderItems and update stock
        for prod_id, item_data in cart.items():
            product = Product.objects.get(id=prod_id)
            qty = item_data['quantity']
            
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                subtotal=Decimal(item_data['price']) * qty
            )
            
            # Deduct from inventory!
            product.stock_quantity -= qty
            product.save()

        # Step C: Create the Payment Record
        Payment.objects.create(
            order=order,
            amount=total,
            payment_method=payment_method,
            status='Pending'
        )


        # Step D: Clear the customer's cart so they can start fresh!
        request.session['customer_cart'] = {}
        request.session.modified = True

        # NEW: Check how they want to pay!
        if payment_method == 'PayPal':
            # Send them to the secure PayPal page
            return redirect('orders:paypal_payment', order_id=order.id)
        else:
            # COD chosen: Just show success and go to menu
            messages.success(request, f"Order #{order.id} placed successfully! Pay our rider upon delivery.")
            return redirect('products:menu_list')

    # 3. If it's a GET request, just show them the checkout page with their totals
    context = {
        'subtotal': subtotal,
        'tax': tax,
        'total': total,
    }
    return render(request, 'customers/checkout.html', context)

@login_required(login_url='login')
def paypal_payment(request, order_id):
    """Renders the page with the official PayPal buttons."""
    # Ensure this user actually owns this order!
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'customers/paypal_payment.html', {'order': order})

@login_required(login_url='login')
def payment_complete(request):
    """Receives the success ping from PayPal and updates our database."""
    body = json.loads(request.body)
    
    order = Order.objects.get(id=body['orderID'])
    payment = order.payment # Grabs the linked Payment model
    
    # Update the database to show they actually paid!
    payment.status = 'Completed'
    payment.transaction_id = body['transactionID']
    payment.save()
    
    return JsonResponse('Payment completed!', safe=False)

@login_required(login_url='login')
def customer_orders(request):
    # Fetch all orders that belong exclusively to the logged-in user, newest first!
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    
    return render(request, 'customers/order_list.html', {'orders': orders})


#------ admin side---------------------------------------------
@login_required(login_url='login')
def staff_order_list(request):
    """Fetches all orders for the staff dashboard, newest first."""
    # You can also filter this to exclude 'Completed' if you only want active orders!
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'staff/order_list.html', {'orders': orders})

@login_required(login_url='login')
def update_order_status(request, order_id):
    """Securely updates the status of an order when staff change it."""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        # Update the order status
        order.status = new_status
        order.save()
        
        # If they mark the order as Completed, let's also mark the Payment as Completed (for COD)
        if new_status == 'Completed' and order.payment.status == 'Pending':
            order.payment.status = 'Completed'
            order.payment.save()
            
        messages.success(request, f"Order #{order.id} is now marked as {new_status}.")
        
    return redirect('orders:staff_order_list')


@login_required
def process_checkout(request):
    """Receives cart JSON from the POS and creates database records."""
    if request.method == 'POST':
        try:
            # 1. Unpack the JSON data sent by JavaScript
            data = json.loads(request.body)
            cart_items = data.get('cart', {})
            
            if not cart_items:
                return JsonResponse({'success': False, 'error': 'Cart is empty!'})

            # 2. Calculate totals securely on the backend
            # NEVER trust the frontend JavaScript to tell you the final price!
            subtotal = Decimal('0.00')
            for item_id, item_data in cart_items.items():
                product = Product.objects.get(id=item_id)
                qty = int(item_data['qty'])
                subtotal += product.price * qty
                
            tax = subtotal * Decimal('0.12')
            total_amount = subtotal + tax

            # 3. Create the main Order record
            order = Order.objects.create(
                user=request.user,
                status='Completed', # POS walk-in orders are completed instantly
                total_amount=total_amount
            )

            # 4. Loop through the cart to create OrderItems and update stock
            for item_id, item_data in cart_items.items():
                product = Product.objects.get(id=item_id)
                qty = int(item_data['qty'])
                item_subtotal = product.price * qty

                # Save the specific item to the order
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    subtotal=item_subtotal
                )
                
                # Deduct the sold amount from your inventory!
                product.stock_quantity -= qty
                product.save()

            return JsonResponse({'success': True, 'message': f'Payment successful! Order #{order.id} saved.'})

        except Exception as e:
            # If anything crashes, tell the frontend exactly what went wrong
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': True, 'message': 'Payment successful!', 'order_id': order.id})

@login_required(login_url='login')
def sales_analytics(request):
    """Generates a 7-Day Sales Report."""
    if not request.user.is_staff:
        return redirect('products:menu_list')

    today = timezone.now().date()
    seven_days_ago = today - datetime.timedelta(days=6)

    # 1. Get all completed orders from the last 7 days
    completed_orders = Order.objects.filter(
        order_date__date__gte=seven_days_ago, 
        status='Completed'
    ).order_by('-order_date')

    # 2. Calculate the "Big Numbers" for the report
    total_revenue = completed_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = completed_orders.count()
    avg_order = completed_orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0

    # 3. Build the daily chart data
    dates_list = []
    sales_list = []

    for i in range(6, -1, -1):
        target_date = today - datetime.timedelta(days=i)
        dates_list.append(target_date.strftime('%b %d')) 
        
        daily_total = completed_orders.filter(
            order_date__date=target_date
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        
        sales_list.append(float(daily_total))

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'avg_order': avg_order,
        'recent_orders': completed_orders, # Passing the actual orders to the table
        'dates': json.dumps(dates_list),
        'sales': json.dumps(sales_list),
    }
    return render(request, 'staff/analytics.html', context)