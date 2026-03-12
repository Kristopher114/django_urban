from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Customer
from .forms import UserRegisterForm, CustomerForm
from products.models import Category, Product


@login_required
def customer_dashboard(request):
    # Just grab all categories for the main page
    categories = Category.objects.all()
    
    context = {
        'categories': categories,
    }
    return render(request, 'customers/dashboard.html', context)
# --- VIEW 2: The Specific Menu List ---

@login_required
def menu_list_view(request, category_name):
    # 1. Find the specific category
    category = get_object_or_404(Category, name__iexact=category_name)
    
    # 2. Grab all products that belong to this specific category
    # (This assumes your Product model has a ForeignKey called 'category')
    products = Product.objects.filter(category=category)
    
    # 3. Pass BOTH the category and the products to the HTML
    context = {
        'category': category,
        'products': products, 
    }
    
    return render(request, 'menufolder/menu_list.html', context)

# ── Register New Customer ──────────────────────────────────────────────────────
def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        customer_form = CustomerForm(request.POST)
        if user_form.is_valid() and customer_form.is_valid():
            user = user_form.save(commit=False)
            user.email = user_form.cleaned_data['email']
            user.save()  # this properly hashes password

            customer = customer_form.save(commit=False)
            customer.user = user
            customer.save()

            messages.success(request, f'Account created for {user.username}!')
            return redirect('customer_login')
    else:
        user_form = UserRegisterForm()
        customer_form = CustomerForm()
    
    context = {
        'user_form': user_form,
        'customer_form': customer_form
    }
    return render(request, 'customers/register.html', context)

# ── LOGIN  Customer ──────────────────────────────────────────────────────
def customer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

        

    return render(request, 'customers/login.html')

@login_required
def customer_logout(request):
    """Log out the current user."""
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('customer_login')

# ── Customer Profile ──────────────────────────────────────────────────────────

@login_required
def customer_profile(request):
    """View the logged-in customer's profile."""
    customer = get_object_or_404(Customer, user=request.user)
    return render(request, 'customers/profile.html', {'customer': customer})


@login_required
def edit_profile(request):
    """Edit the logged-in customer's profile."""
    customer = get_object_or_404(Customer, user=request.user)

    if request.method == 'POST':
        customer.address = request.POST.get('address', customer.address)
        customer.phone   = request.POST.get('phone',   customer.phone)
        customer.save()

        customer.user.first_name = request.POST.get('first_name', customer.user.first_name)
        customer.user.last_name  = request.POST.get('last_name',  customer.user.last_name)
        customer.user.email      = request.POST.get('email',      customer.user.email)
        customer.user.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('customer_profile')

    return render(request, 'customers/edit_profile.html', {'customer': customer})


# ── Admin / Staff Views ───────────────────────────────────────────────────────
# ── Admin / Staff Views ───────────────────────────────────────────────────────

def staff_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the user exists in the database
        user = authenticate(request, username=username, password=password)
        
        # Make sure the user exists AND is a staff member
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard') # Redirects to the dashboard URL
        else:
            # Tell the user if they messed up!
            messages.error(request, 'Invalid credentials or you do not have staff access.')

    return render(request, 'staff/staff_login.html')

@login_required
def admin_dashboard(request):
    """The POS dashboard for staff members."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('customer_profile')
        
    # 1. Grab all categories
    categories = Category.objects.all()
    
    # 2. Grab all products (select_related speeds up the database query)
    products = Product.objects.select_related('category').all()
    
    context = {
        'categories': categories,
        'products': products,
    }
        
    return render(request, 'staff/admin_dashboard.html', context)

# ... Keep your customer_list, customer_detail, and delete_customer views exactly as they are!

@login_required
def customer_list(request):
    """List all customers — staff/admin only."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('customer_profile')

    customers = Customer.objects.select_related('user').all()
    return render(request, 'customers/customer_list.html', {'customers': customers})


@login_required
def customer_detail(request, pk):
    """View a specific customer — staff/admin only."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('customer_profile')

    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'staff/customer_detail.html', {'customer': customer})


@login_required
def delete_customer(request, pk):
    """Delete a customer account — staff/admin only."""
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('customer_profile')

    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        customer.user.delete()   # cascades to Customer via OneToOneField
        messages.success(request, 'Customer deleted successfully.')
        return redirect('customer_list')

    return render(request, 'customers/confirm_delete.html', {'customer': customer})