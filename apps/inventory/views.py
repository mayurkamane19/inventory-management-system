from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from apps.products.models import Product
from .models import Inventory, StockMovement
from apps.audit.models import log_activity

@login_required
def stock_overview_view(request):
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    products = Product.objects.select_related('category', 'inventory_record').all().order_by('name')

    if search_query:
        products = products.filter(name__icontains=search_query)

    if status_filter == 'low':
        products = products.filter(stock_quantity__gt=0, stock_quantity__lte=F('reorder_level'))
    elif status_filter == 'out':
        products = products.filter(stock_quantity__lte=0)
    elif status_filter == 'in':
        products = products.filter(stock_quantity__gt=F('reorder_level'))

    total_products = Product.objects.count()
    low_stock_count = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lte=F('reorder_level')).count()
    out_of_stock_count = Product.objects.filter(stock_quantity__lte=0).count()
    
    total_valuation = Product.objects.aggregate(
        val=Sum(ExpressionWrapper(F('stock_quantity') * F('selling_price'), output_field=DecimalField()))
    )['val'] or 0.00

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'inventory/stock_overview.html', {
        'page_obj': page_obj,
        'total_products': total_products,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'total_valuation': total_valuation,
        'status_filter': status_filter,
        'search_query': search_query,
    })

@login_required
def stock_movement_view(request):
    type_filter = request.GET.get('type', '')
    search_query = request.GET.get('search', '')

    movements = StockMovement.objects.select_related('product', 'created_by').all()

    if search_query:
        movements = movements.filter(product__name__icontains=search_query)

    if type_filter:
        movements = movements.filter(movement_type=type_filter)

    paginator = Paginator(movements, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'inventory/stock_movement.html', {
        'page_obj': page_obj,
        'type_filter': type_filter,
        'search_query': search_query
    })
