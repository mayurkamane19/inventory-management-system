from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.utils import timezone
import datetime
from apps.products.models import Product, Category
from apps.contacts.models import Supplier, Customer
from apps.transactions.models import Purchase, Sale, SaleItem
from apps.inventory.models import Inventory

@login_required
def dashboard_index_view(request):
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    total_products = Product.objects.filter(status='Active').count()
    total_categories = Category.objects.filter(status='Active').count()
    total_suppliers = Supplier.objects.count()
    total_customers = Customer.objects.count()

    total_purchase_val = Purchase.objects.aggregate(total=Sum('total_amount'))['total'] or 0.00
    total_sales_val = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or 0.00

    current_inventory_value = Product.objects.aggregate(
        val=Sum(ExpressionWrapper(F('stock_quantity') * F('selling_price'), output_field=DecimalField()))
    )['val'] or 0.00

    todays_sales = Sale.objects.filter(sale_date__gte=today_start).aggregate(total=Sum('total_amount'))['total'] or 0.00
    monthly_sales = Sale.objects.filter(sale_date__gte=month_start).aggregate(total=Sum('total_amount'))['total'] or 0.00
    monthly_purchase = Purchase.objects.filter(purchase_date__gte=month_start).aggregate(total=Sum('total_amount'))['total'] or 0.00

    low_stock_products = Product.objects.filter(stock_quantity__gt=0, stock_quantity__lte=F('reorder_level')).count()
    out_of_stock_products = Product.objects.filter(stock_quantity__lte=0).count()

    # Recent Activities
    latest_purchases = Purchase.objects.select_related('supplier').all().order_by('-purchase_date')[:5]
    latest_sales = Sale.objects.select_related('customer').all().order_by('-sale_date')[:5]
    recently_added_products = Product.objects.select_related('category').all().order_by('-created_at')[:5]

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_suppliers': total_suppliers,
        'total_customers': total_customers,
        'total_purchase_val': total_purchase_val,
        'total_sales_val': total_sales_val,
        'current_inventory_value': current_inventory_value,
        'todays_sales': todays_sales,
        'monthly_sales': monthly_sales,
        'monthly_purchase': monthly_purchase,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'latest_purchases': latest_purchases,
        'latest_sales': latest_sales,
        'recently_added_products': recently_added_products,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def analytics_api_view(request):
    """JSON API endpoint returning data formatted for Chart.js graphs"""
    # 1. Monthly Sales vs Purchase (Last 6 Months)
    months_labels = []
    sales_data = []
    purchase_data = []
    
    today = timezone.now().date()
    for i in range(5, -1, -1):
        m_date = today - datetime.timedelta(days=i*30)
        month_name = m_date.strftime("%b %Y")
        months_labels.append(month_name)
        
        m_sales = Sale.objects.filter(sale_date__year=m_date.year, sale_date__month=m_date.month).aggregate(t=Sum('total_amount'))['t'] or 0.00
        m_purchases = Purchase.objects.filter(purchase_date__year=m_date.year, purchase_date__month=m_date.month).aggregate(t=Sum('total_amount'))['t'] or 0.00
        
        sales_data.append(float(m_sales))
        purchase_data.append(float(m_purchases))

    # 2. Stock Category Pie Chart
    category_counts = Category.objects.annotate(prod_count=Count('products')).values('name', 'prod_count')
    cat_labels = [c['name'] for c in category_counts]
    cat_data = [c['prod_count'] for c in category_counts]

    # 3. Top 5 Selling Products
    top_items = SaleItem.objects.values('product__name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:5]
    top_prod_labels = [item['product__name'] for item in top_items]
    top_prod_data = [item['total_qty'] for item in top_items]

    return JsonResponse({
        'monthly_labels': months_labels,
        'sales_data': sales_data,
        'purchase_data': purchase_data,
        'cat_labels': cat_labels,
        'cat_data': cat_data,
        'top_prod_labels': top_prod_labels,
        'top_prod_data': top_prod_data,
    })

@login_required
def global_search_view(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query) if query else []
    suppliers = Supplier.objects.filter(company__icontains=query) if query else []
    customers = Customer.objects.filter(name__icontains=query) if query else []
    categories = Category.objects.filter(name__icontains=query) if query else []

    return render(request, 'dashboard/search_results.html', {
        'query': query,
        'products': products,
        'suppliers': suppliers,
        'customers': customers,
        'categories': categories,
    })
