from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index_view, name='index'),
    path('api/analytics/', views.analytics_api_view, name='analytics_api'),
    path('search/', views.global_search_view, name='global_search'),
]
