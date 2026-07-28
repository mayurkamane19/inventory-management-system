from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
import datetime
from .models import Purchase, PurchaseItem, Sale, SaleItem
from .forms import PurchaseForm, SaleForm
from apps.contacts.models import Supplier, Customer
from apps.products.models import Product
from apps.audit.models import log_activity

# --- PURCHASE VIEWS ---

@login_required
def purchase_list_view(request):
    search_query = request.GET.get('search', '')
    purchases = Purchase.objects.select_related('supplier', 'created_by').all().order_by('-purchase_date')
    if search_query:
        purchases = purchases.filter(invoice_no__icontains=search_query)

    paginator = Paginator(purchases, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'transactions/purchase_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
def purchase_create_view(request):
    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        invoice_no = request.POST.get('invoice_no')
        purchase_date = request.POST.get('purchase_date') or timezone.now()
        notes = request.POST.get('notes', '')

        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        purchase_prices = request.POST.getlist('purchase_price[]')

        if not supplier_id or not invoice_no or not product_ids:
            messages.error(request, "Please fill in all required fields and add at least one line item.")
            return redirect('transactions:purchase_create')

        supplier = get_object_or_404(Supplier, pk=supplier_id)
        
        # Create Purchase Header
        purchase = Purchase.objects.create(
            invoice_no=invoice_no,
            supplier=supplier,
            purchase_date=purchase_date,
            created_by=request.user,
            notes=notes,
            total_amount=Decimal('0.00')
        )

        total_amount = Decimal('0.00')
        for pid, qty, price in zip(product_ids, quantities, purchase_prices):
            if pid and qty and price:
                product = get_object_or_404(Product, pk=pid)
                q = int(qty)
                p = Decimal(price)
                subtotal = q * p
                total_amount += subtotal

                # Save PurchaseItem -> Trigger Signal will update stock and record StockMovement!
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=q,
                    purchase_price=p,
                    subtotal=subtotal
                )

        purchase.total_amount = total_amount
        purchase.save()

        log_activity(request.user, "Create Purchase", "Transactions", f"Created purchase order #{purchase.invoice_no} (Total: ₹{total_amount}).", request.META.get('REMOTE_ADDR'))
        messages.success(request, f"Purchase Order #{purchase.invoice_no} recorded & stock updated!")
        return redirect('transactions:purchase_list')

    suppliers = Supplier.objects.all()
    products = Product.objects.filter(status='Active')
    auto_inv = f"PUR-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    return render(request, 'transactions/purchase_form.html', {
        'suppliers': suppliers,
        'products': products,
        'auto_inv': auto_inv,
        'now_str': timezone.now().strftime('%Y-%m-%dT%H:%M')
    })

@login_required
def purchase_detail_view(request, pk):
    purchase = get_object_or_404(Purchase.objects.select_related('supplier', 'created_by').prefetch_related('items__product'), pk=pk)
    return render(request, 'transactions/purchase_detail.html', {'purchase': purchase})

# --- SALES INVOICE VIEWS ---

@login_required
def sale_list_view(request):
    search_query = request.GET.get('search', '')
    sales = Sale.objects.select_related('customer', 'created_by').all().order_by('-sale_date')
    if search_query:
        sales = sales.filter(invoice_no__icontains=search_query)

    paginator = Paginator(sales, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'transactions/sale_list.html', {
        'page_obj': page_obj,
        'search_query': search_query
    })

@login_required
def sale_create_view(request):
    if request.method == 'POST':
        customer_id = request.POST.get('customer')
        invoice_no = request.POST.get('invoice_no')
        sale_date = request.POST.get('sale_date') or timezone.now()
        discount_val = Decimal(request.POST.get('discount', '0.00'))
        gst_percent = Decimal(request.POST.get('gst_percent', '18.00'))
        notes = request.POST.get('notes', '')

        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        selling_prices = request.POST.getlist('selling_price[]')

        if not invoice_no or not product_ids:
            messages.error(request, "Please add products and valid details for the invoice.")
            return redirect('transactions:sale_create')

        customer = get_object_or_404(Customer, pk=customer_id) if customer_id else None

        subtotal = Decimal('0.00')
        items_to_create = []

        # Validate stock availability first
        for pid, qty, price in zip(product_ids, quantities, selling_prices):
            if pid and qty and price:
                product = get_object_or_404(Product, pk=pid)
                q = int(qty)
                p = Decimal(price)
                if product.stock_quantity < q:
                    messages.error(request, f"Insufficient stock for '{product.name}'! Available: {product.stock_quantity}, Requested: {q}")
                    return redirect('transactions:sale_create')
                
                line_total = q * p
                subtotal += line_total
                items_to_create.append((product, q, p, line_total))

        # Calculate Financials
        gst_amount = (subtotal - discount_val) * (gst_percent / Decimal('100.00'))
        if gst_amount < Decimal('0.00'):
            gst_amount = Decimal('0.00')
        total_amount = (subtotal - discount_val) + gst_amount

        # Create Sale Header
        sale = Sale.objects.create(
            invoice_no=invoice_no,
            customer=customer,
            subtotal=subtotal,
            discount=discount_val,
            gst_amount=gst_amount,
            total_amount=total_amount,
            sale_date=sale_date,
            created_by=request.user,
            notes=notes
        )

        # Create SaleItems -> Trigger Signal will decrease stock and record StockMovement!
        for product, q, p, line_total in items_to_create:
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=q,
                selling_price=p,
                total_price=line_total
            )

        log_activity(request.user, "Process Sale", "Transactions", f"Generated sale invoice #{sale.invoice_no} (Total: ₹{total_amount}).", request.META.get('REMOTE_ADDR'))
        messages.success(request, f"Invoice #{sale.invoice_no} generated successfully!")
        return redirect('transactions:sale_invoice', pk=sale.pk)

    customers = Customer.objects.all()
    products = Product.objects.filter(status='Active', stock_quantity__gt=0)
    auto_inv = f"INV-{timezone.now().strftime('%Y%m%d%H%M%S')}"
    return render(request, 'transactions/sale_form.html', {
        'customers': customers,
        'products': products,
        'auto_inv': auto_inv,
        'now_str': timezone.now().strftime('%Y-%m-%dT%H:%M')
    })

@login_required
def sale_invoice_view(request, pk):
    sale = get_object_or_404(Sale.objects.select_related('customer', 'created_by').prefetch_related('items__product'), pk=pk)
    return render(request, 'transactions/sale_invoice.html', {'sale': sale})
