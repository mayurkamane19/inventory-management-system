from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class Inventory(models.Model):
    STATUS_CHOICES = (
        ('In Stock', 'In Stock'),
        ('Low Stock', 'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
    )

    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory_record')
    current_stock = models.IntegerField(default=0)
    low_stock_threshold = models.IntegerField(default=10)
    last_stock_update = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='In Stock')

    def __str__(self):
        return f"{self.product.name} - Stock: {self.current_stock}"

class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('PURCHASE', 'Purchase'),
        ('SALE', 'Sale'),
        ('ADJUSTMENT', 'Adjustment'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    balance_after = models.IntegerField()
    movement_date = models.DateTimeField(auto_now_add=True)
    reference_no = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-movement_date']

    def __str__(self):
        return f"{self.movement_type} - {self.product.name} ({self.quantity})"
