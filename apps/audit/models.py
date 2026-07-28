from django.db import models
from django.contrib.auth.models import User

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100) # e.g. "Create Product", "Login", "Process Sale"
    module = models.CharField(max_length=50) # e.g. "Products", "Sales", "Auth"
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.username if self.user else 'System'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {username} - {self.action}"

def log_activity(user, action, module, details="", ip_address=None):
    AuditLog.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        module=module,
        details=details,
        ip_address=ip_address
    )
