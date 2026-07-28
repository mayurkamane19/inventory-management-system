from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('stock/', views.stock_overview_view, name='stock_overview'),
    path('movements/', views.stock_movement_view, name='stock_movement'),
]
