def cart_item_count(request):
    """Counts the items in the Session Cart and triggers the red dot."""
    count = 0
    has_new_items = False

    # Check if they are logged in as a normal customer
    if request.user.is_authenticated and not request.user.is_staff:
        
        # 1. Grab the cart from the SESSION (This now perfectly matches your view_cart!)
        cart = request.session.get('customer_cart', {})
        
        # 2. Add up all the quantities of the items inside the session cart
        if cart:
            count = sum(item_data['quantity'] for item_data in cart.values())
            
        # 3. Check if they have seen them yet
        last_seen_count = request.session.get('seen_cart_count', 0)
        
        # If current session cart count > seen count, show the dot!
        if count > last_seen_count:
            has_new_items = True

    return {
        'cart_count': count,
        'has_new_items': has_new_items,
    }