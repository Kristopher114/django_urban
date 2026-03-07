from django.shortcuts import render
from .models import Category # Don't forget to import your model!

def home(request):
    # Fetch all categories from the database
    categories = Category.objects.all()
    
    # Pass them to the template in the context dictionary
    context = {
        'categories': categories
    }
    return render(request, 'customers/dashboard.html', context)