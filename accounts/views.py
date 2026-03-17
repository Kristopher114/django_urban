from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Customer
from .forms import UserRegisterForm, CustomerForm
from products.models import Category, Product
from orders.models import Order # Make sure Order is imported!

@login_required()
def customer_dashboard(request):
    # Just grab all categories for the main page
    categories = Category.objects.all()
        # Grab the 3 most recent orders for this specific user
    recent_orders = Order.objects.filter(user=request.user).order_by('-order_date')[:3]

    context = {
        'categories': categories,
        'recent_orders': recent_orders,

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
def manage_staff(request):
    """Allows Superusers to view and create staff accounts."""
    
    # SECURITY: Bounce them out if they aren't the big boss!
    if not request.user.is_superuser:
        messages.error(request, "Access Denied. Only the store owner can manage staff.")
        return redirect('orders:staff_dashboard') # Adjust this redirect to your main staff page

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')

        # Safety Check: Does the username already exist?
        if User.objects.filter(username=username).exists():
            messages.error(request, f"The username '{username}' is already taken.")
        else:
            # Create the user and safely encrypt the password!
            new_staff = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            # THIS IS THE MAGIC LINE: Give them POS and Kitchen access!
            new_staff.is_staff = True 
            new_staff.save()
            
            messages.success(request, f"Staff account for {first_name} created successfully!")
            return redirect('manage_staff') # Refresh the page

    # Get a list of all current staff and superusers to display in the table
    staff_members = User.objects.filter(is_staff=True).order_by('-is_superuser', '-date_joined')

    return render(request, 'staff/manage_staff.html', {'staff_members': staff_members})