from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Customer

# Form for User
class UserRegisterForm(UserCreationForm):
    # We add the widget here for explicit fields
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    # We use __init__ to target the auto-generated fields (like passwords)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({'placeholder': 'Create a Username'})
        
        # UserCreationForm automatically names its password fields 'password1' and 'password2'
        if 'password1' in self.fields:
            self.fields['password1'].widget.attrs.update({'placeholder': 'Create a Password'})
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})


# Form for Customer info
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'address', 'phone']
        
        # For a standard ModelForm, we can just use the widgets dictionary
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number (e.g. 09123456789)'}),
            'address': forms.Textarea(attrs={
                'placeholder': 'Complete Delivery Address', 
                'rows': 3  # Makes the text box shorter so it fits nicely
            }),
        }