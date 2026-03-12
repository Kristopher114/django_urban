from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product  # Import both models!
from .forms import ProductForm

@login_required
def inventory_list(request):
    """Staff view to see all products in the inventory."""
    if not request.user.is_staff:
        return redirect('dashboard') # Kick non-staff out

    # Grab all products, and use select_related for a database performance boost!
    products = Product.objects.select_related('category').all()
    
    context = {
        'products': products
    }
    return render(request, 'staff/inventory_list.html', context)


@login_required
def product_create(request):
    """Staff view to add a new product."""
    if not request.user.is_staff:
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES) # request.FILES is required for images!
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('inventory_list')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'title': 'Add New Product'
    }
    return render(request, 'staff/product_form.html', context)


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

