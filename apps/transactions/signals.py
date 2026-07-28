from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from apps.authentication.models import UserProfile
from apps.products.models import Product
from apps.inventory.models import Inventory, StockMovement
from .models import PurchaseItem, SaleItem

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance, role='Admin' if instance.is_superuser else 'Staff')
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

@receiver(post_save, sender=Product)
def create_or_update_product_inventory(sender, instance, created, **kwargs):
    status = 'Out of Stock' if instance.stock_quantity <= 0 else ('Low Stock' if instance.stock_quantity <= instance.reorder_level else 'In Stock')
    Inventory.objects.update_or_create(
        product=instance,
        defaults={
            'current_stock': instance.stock_quantity,
            'low_stock_threshold': instance.reorder_level,
            'status': status,
        }
    )

@receiver(post_save, sender=PurchaseItem)
def handle_purchase_item_stock(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock_quantity += instance.quantity
        product.save()

        StockMovement.objects.create(
            product=product,
            movement_type='PURCHASE',
            quantity=instance.quantity,
            unit_price=instance.purchase_price,
            balance_after=product.stock_quantity,
            reference_no=instance.purchase.invoice_no,
            created_by=instance.purchase.created_by,
            notes=f"Purchase Invoice #{instance.purchase.invoice_no}"
        )

@receiver(post_save, sender=SaleItem)
def handle_sale_item_stock(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock_quantity -= instance.quantity
        if product.stock_quantity < 0:
            product.stock_quantity = 0
        product.save()

        StockMovement.objects.create(
            product=product,
            movement_type='SALE',
            quantity=instance.quantity,
            unit_price=instance.selling_price,
            balance_after=product.stock_quantity,
            reference_no=instance.sale.invoice_no,
            created_by=instance.sale.created_by,
            notes=f"Sale Invoice #{instance.sale.invoice_no}"
        )
