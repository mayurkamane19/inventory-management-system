from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('logs/', views.audit_list_view, name='audit_list'),
    path('backup/', views.backup_database_view, name='backup_database'),
]
