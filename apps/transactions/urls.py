from django.urls import path
from . import views

app_name = 'transactions'

urlpatterns = [
    # Purchases
    path('purchases/', views.purchase_list_view, name='purchase_list'),
    path('purchases/create/', views.purchase_create_view, name='purchase_create'),
    path('purchases/<int:pk>/', views.purchase_detail_view, name='purchase_detail'),

    # Sales
    path('sales/', views.sale_list_view, name='sale_list'),
    path('sales/create/', views.sale_create_view, name='sale_create'),
    path('sales/<int:pk>/invoice/', views.sale_invoice_view, name='sale_invoice'),
]
