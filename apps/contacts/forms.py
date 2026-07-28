from django import forms
from .models import Supplier, Customer

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'company', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Contact Person Name'}),
            'company': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Company Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Email Address'}),
            'address': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3, 'placeholder': 'Full Address'}),
        }

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Customer Name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Email Address'}),
            'address': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3, 'placeholder': 'Full Address'}),
        }
