from django import forms
from .models import Purchase, PurchaseItem, Sale, SaleItem
from apps.contacts.models import Supplier, Customer
from apps.products.models import Product

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['invoice_no', 'supplier', 'purchase_date', 'notes']
        widgets = {
            'invoice_no': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. PUR-2026-001'}),
            'supplier': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'purchase_date': forms.DateTimeInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 2}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['invoice_no', 'customer', 'discount', 'gst_amount', 'sale_date', 'notes']
        widgets = {
            'invoice_no': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'customer': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'step': '0.01'}),
            'gst_amount': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'step': '0.01'}),
            'sale_date': forms.DateTimeInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 2}),
        }
