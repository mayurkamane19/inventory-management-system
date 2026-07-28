from django.db import models
from apps.contacts.models import Supplier
import qrcode
from io import BytesIO
from django.core.files import File
import os

class Category(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    sku = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=150)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    stock_quantity = models.IntegerField(default=0)
    reorder_level = models.IntegerField(default=10)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def stock_status(self):
        if self.stock_quantity <= 0:
            return 'Out of Stock'
        elif self.stock_quantity <= self.reorder_level:
            return 'Low Stock'
        return 'In Stock'

    @property
    def inventory_value(self):
        return self.stock_quantity * self.selling_price

    def save(self, *args, **kwargs):
        # Generate QR code automatically if not existing
        if not self.qr_code and self.sku:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=8,
                border=2,
            )
            qr_content = f"SKU: {self.sku} | Name: {self.name} | Price: {self.selling_price}"
            qr.add_data(qr_content)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            file_name = f"qr_{self.sku}.png"
            self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)
