from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Category, Product
from .forms import CategoryForm, ProductForm
from apps.audit.models import log_activity

# --- CATEGORY VIEWS ---

@login_required
def category_list_view(request):
    search_query = request.GET.get('search', '')
    categories = Category.objects.all().order_by('-created_at')
    if search_query:
        categories = categories.filter(name__icontains=search_query)

    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    form = CategoryForm()
    return render(request, 'products/category_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'form': form
    })

@login_required
def category_create_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            log_activity(request.user, "Create Category", "Products", f"Created category '{category.name}'.", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"Category '{category.name}' created successfully!")
            return redirect('products:category_list')
        else:
            messages.error(request, "Error creating category. Please check the inputs.")
    return redirect('products:category_list')

@login_required
def category_update_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Update Category", "Products", f"Updated category '{category.name}'.", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"Category '{category.name}' updated successfully!")
            return redirect('products:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'products/category_form.html', {'form': form, 'category': category})

@login_required
def category_delete_view(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = category.name
        category.delete()
        log_activity(request.user, "Delete Category", "Products", f"Deleted category '{name}'.", request.META.get('REMOTE_ADDR'))
        messages.success(request, f"Category '{name}' deleted!")
        return redirect('products:category_list')
    return render(request, 'products/category_confirm_delete.html', {'category': category})

# --- PRODUCT VIEWS ---

@login_required
def product_list_view(request):
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '')
    stock_status = request.GET.get('stock_status', '')

    products = Product.objects.select_related('category', 'supplier').all().order_by('-created_at')

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query) |
            Q(barcode__icontains=search_query)
        )
    if category_id:
        products = products.filter(category_id=category_id)
    
    if stock_status == 'low':
        products = [p for p in products if 0 < p.stock_quantity <= p.reorder_level]
    elif stock_status == 'out':
        products = [p for p in products if p.stock_quantity <= 0]
    elif stock_status == 'in':
        products = [p for p in products if p.stock_quantity > p.reorder_level]

    categories = Category.objects.filter(status='Active')
    
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'category_id': category_id,
        'stock_status': stock_status,
    })

@login_required
def product_detail_view(request, pk):
    product = get_object_or_404(Product.objects.select_related('category', 'supplier'), pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def product_create_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            log_activity(request.user, "Create Product", "Products", f"Created product '{product.name}' (SKU: {product.sku}).", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"Product '{product.name}' added successfully!")
            return redirect('products:product_list')
        else:
            messages.error(request, "Error creating product. Please verify form fields.")
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})

@login_required
def product_update_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Update Product", "Products", f"Updated product '{product.name}' (SKU: {product.sku}).", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"Product '{product.name}' updated successfully!")
            return redirect('products:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'products/product_form.html', {'form': form, 'product': product, 'title': 'Edit Product'})

@login_required
def product_delete_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        log_activity(request.user, "Delete Product", "Products", f"Deleted product '{name}'.", request.META.get('REMOTE_ADDR'))
        messages.success(request, f"Product '{name}' deleted!")
        return redirect('products:product_list')
    return render(request, 'products/product_confirm_delete.html', {'product': product})
