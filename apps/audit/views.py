from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.management import call_command
from django.http import HttpResponse
from io import StringIO
from .models import AuditLog, log_activity

@login_required
def audit_list_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('dashboard:index')

    module_filter = request.GET.get('module', '')
    search_query = request.GET.get('search', '')

    logs = AuditLog.objects.select_related('user').all()

    if module_filter:
        logs = logs.filter(module=module_filter)

    if search_query:
        logs = logs.filter(action__icontains=search_query)

    paginator = Paginator(logs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'audit/audit_list.html', {
        'page_obj': page_obj,
        'module_filter': module_filter,
        'search_query': search_query,
    })

@login_required
def backup_database_view(request):
    if not hasattr(request.user, 'profile') or request.user.profile.role != 'Admin':
        messages.error(request, "Access denied. Admin permissions required.")
        return redirect('dashboard:index')

    buffer = StringIO()
    call_command('dumpdata', indent=2, stdout=buffer)
    data = buffer.getvalue()
    buffer.close()

    log_activity(request.user, "Database Backup", "Audit", "Exported full JSON database dump.", request.META.get('REMOTE_ADDR'))

    response = HttpResponse(data, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename="inventory_db_backup.json"'
    return response
