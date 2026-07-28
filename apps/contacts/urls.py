from django.urls import path
from . import views

app_name = 'contacts'

urlpatterns = [
    # Suppliers
    path('suppliers/', views.supplier_list_view, name='supplier_list'),
    path('suppliers/add/', views.supplier_create_view, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update_view, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete_view, name='supplier_delete'),

    # Customers
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/add/', views.customer_create_view, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update_view, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete_view, name='customer_delete'),
]
