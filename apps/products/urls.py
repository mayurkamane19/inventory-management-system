from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Categories
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/add/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update_view, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete_view, name='category_delete'),

    # Products
    path('', views.product_list_view, name='product_list'),
    path('add/', views.product_create_view, name='product_create'),
    path('<int:pk>/', views.product_detail_view, name='product_detail'),
    path('<int:pk>/edit/', views.product_update_view, name='product_update'),
    path('<int:pk>/delete/', views.product_delete_view, name='product_delete'),
]
