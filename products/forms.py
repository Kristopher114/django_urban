from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'stock_quantity', 'product_image']
        
        # We add CSS classes here so we can style them perfectly in our dark theme later
        widgets = {
            'name': forms.TextInput(attrs={'class': 'pos-input', 'placeholder': 'e.g., Caffe Latte'}),
            'category': forms.Select(attrs={'class': 'pos-input'}),
            'description': forms.Textarea(attrs={'class': 'pos-input', 'rows': 2}),
            'price': forms.NumberInput(attrs={'class': 'pos-input', 'placeholder': '0.00'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'pos-input', 'placeholder': '0'}),
        }

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name', 'description', 'category_image']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'pos-input', 'placeholder': 'e.g., Beverages'}),
            'description': forms.Textarea(attrs={'class': 'pos-input', 'rows': 2}),
        }