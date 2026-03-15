from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product  # Import both models!
from .forms import ProductForm, CategoryForm

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
            
            # Fixed! We told Django exactly which app the URL belongs to.
            return redirect('products:inventory_list')
    else:
        form = ProductForm()

    context = {
        'form': form,
        'title': 'Add New Product'
    }
    return render(request, 'staff/product_form.html', context)

@login_required
def category_create(request,pk=None):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES) # request.FILES is required for images!
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            
            # Fixed! We told Django exactly which app the URL belongs to.
            return redirect('products:inventory_list')
    else:
        form = CategoryForm()
        # Pass all existing categories to the template
    categories = Category.objects.all()

    context = {
        'form': form,
        'title': 'Add New Category',
        'categories': categories
    }
    return render(request, 'staff/category_form.html', context)

@login_required
def edit_product(request, pk):
    # 1. Kick out non-staff members
    if not request.user.is_staff:
        return redirect('dashboard')

    # 2. Grab the specific product from the database
    product = get_object_or_404(Product, pk=pk)

    # 3. Handle the form
    if request.method == 'POST':
        # CRITICAL: Pass 'instance=product' so Django updates it instead of duplicating it
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'{product.name} updated successfully!')
            return redirect('products:inventory_list')

    else:
        # Pre-fill the form with the current product's data
        form = ProductForm(instance=product)

    # 4. Pass the data to your HTML
    context = {
        'form': form,
        # A nice touch: Make the title dynamic based on the product name!
        'title': f'Edit {product.name}' 
    }
    
    # Notice I changed this back to 'products/product_form.html' assuming that is where you saved it!
    return render(request, 'staff/product_form.html', context)

@login_required
def delete_product(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    product = get_object_or_404(Product, pk=pk)
    
    # Check if the modal sent the secure POST request
    if request.method == 'POST':
        product_name = product.name # Save the name before deleting to use in the message
        product.delete()
        messages.success(request, f'{product_name} was successfully deleted.')
        
    return redirect('products:inventory_list')

@login_required
def delete_category(request, pk):
    if not request.user.is_staff:
        return redirect('dashboard')
        
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        cat_name = category.name
        category.delete()
        messages.success(request, f'Category "{cat_name}" deleted.')
        
    # Redirect right back to the create page so they can keep managing categories
    return redirect('products:category_create')



