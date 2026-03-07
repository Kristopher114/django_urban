from django.shortcuts import render
from .models import Category, Product  # Import both models!

def menu_list(request):
    # Fetch all categories and products from the database
    categories = Category.objects.all()
    products = Product.objects.all()
    
    # Pass them to the template
    context = {
        'categories': categories,
        'products': products
    }
    return render(request, 'menufolder/menu_list.html', context)