from django import forms
from .models import Category, Product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Category Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3, 'placeholder': 'Optional Description'}),
            'status': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku', 'name', 'barcode', 'category', 'supplier',
            'unit_price', 'selling_price', 'stock_quantity',
            'reorder_level', 'image', 'description', 'status'
        ]
        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'e.g. PRD-ELEC-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'Product Name'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'placeholder': 'EAN/UPC Barcode'}),
            'category': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'supplier': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary', 'step': '0.01'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'image': forms.FileInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}),
        }
