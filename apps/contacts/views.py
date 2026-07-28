from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Supplier, Customer
from .forms import SupplierForm, CustomerForm
from apps.audit.models import log_activity

# --- SUPPLIER VIEWS ---

@login_required
def supplier_list_view(request):
    search_query = request.GET.get('search', '')
    suppliers = Supplier.objects.all().order_by('-created_at')
    if search_query:
        suppliers = suppliers.filter(
            Q(name__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    paginator = Paginator(suppliers, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    form = SupplierForm()
    return render(request, 'contacts/supplier_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'form': form
    })

@login_required
def supplier_create_view(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            log_activity(request.user, "Create Supplier", "Contacts", f"Added supplier '{supplier.company or supplier.name}'.", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"Supplier '{supplier.name}' added successfully!")
            return redirect('contacts:supplier_list')
        else:
            messages.error(request, "Error adding supplier.")
    return redirect('contacts:supplier_list')

@login_required
def supplier_update_view(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Update Supplier", "Contacts", f"Updated supplier '{supplier.name}'.", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"Supplier '{supplier.name}' updated!")
            return redirect('contacts:supplier_list')
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'contacts/supplier_form.html', {'form': form, 'supplier': supplier})

@login_required
def supplier_delete_view(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        name = supplier.name
        supplier.delete()
        log_activity(request.user, "Delete Supplier", "Contacts", f"Deleted supplier '{name}'.", request.META.get('REMOTE_ADDR'))
        messages.success(request, f"Supplier '{name}' deleted!")
        return redirect('contacts:supplier_list')
    return render(request, 'contacts/supplier_confirm_delete.html', {'supplier': supplier})

# --- CUSTOMER VIEWS ---

@login_required
def customer_list_view(request):
    search_query = request.GET.get('search', '')
    customers = Customer.objects.all().order_by('-created_at')
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    paginator = Paginator(customers, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    form = CustomerForm()
    return render(request, 'contacts/customer_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'form': form
    })

@login_required
def customer_create_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            log_activity(request.user, "Create Customer", "Contacts", f"Added customer '{customer.name}'.", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"Customer '{customer.name}' added successfully!")
            return redirect('contacts:customer_list')
        else:
            messages.error(request, "Error adding customer.")
    return redirect('contacts:customer_list')

@login_required
def customer_update_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Update Customer", "Contacts", f"Updated customer '{customer.name}'.", request.META.get('REMOTE_ADDR'))
            messages.success(request, f"Customer '{customer.name}' updated!")
            return redirect('contacts:customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'contacts/customer_form.html', {'form': form, 'customer': customer})

@login_required
def customer_delete_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        log_activity(request.user, "Delete Customer", "Contacts", f"Deleted customer '{name}'.", request.META.get('REMOTE_ADDR'))
        messages.success(request, f"Customer '{name}' deleted!")
        return redirect('contacts:customer_list')
    return render(request, 'contacts/customer_confirm_delete.html', {'customer': customer})
