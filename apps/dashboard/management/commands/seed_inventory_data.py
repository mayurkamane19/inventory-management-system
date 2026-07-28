from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import datetime

from apps.authentication.models import UserProfile
from apps.products.models import Category, Product
from apps.contacts.models import Supplier, Customer
from apps.transactions.models import Purchase, PurchaseItem, Sale, SaleItem

class Command(BaseCommand):
    help = 'Seeds initial sample data for the Inventory Management System'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))

        # 1. Create Superuser / Admin & Staff Users
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@inventory.com',
                'first_name': 'System',
                'last_name': 'Admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserProfile.objects.update_or_create(user=admin_user, defaults={'role': 'Admin', 'phone': '+1 555-0100'})
            self.stdout.write(self.style.SUCCESS('Admin user created: admin / admin123'))

        staff_user, created = User.objects.get_or_create(
            username='staff1',
            defaults={
                'email': 'staff@inventory.com',
                'first_name': 'John',
                'last_name': 'Staff',
                'is_staff': True,
                'is_superuser': False
            }
        )
        if created:
            staff_user.set_password('staff123')
            staff_user.save()
            UserProfile.objects.update_or_create(user=staff_user, defaults={'role': 'Staff', 'phone': '+1 555-0101'})
            self.stdout.write(self.style.SUCCESS('Staff user created: staff1 / staff123'))

        # 2. Create Categories
        cats_data = [
            ('Electronics', 'Gadgets, computers, and electronic components'),
            ('Office Supplies', 'Paper, pens, staplers, and desk tools'),
            ('Furniture', 'Desks, chairs, filing cabinets, and office furniture'),
            ('Hardware', 'Tools, cables, adapters, and equipment'),
            ('Beverages', 'Coffee, tea, and office snacks'),
        ]
        cat_objs = {}
        for name, desc in cats_data:
            cat, _ = Category.objects.get_or_create(name=name, defaults={'description': desc, 'status': 'Active'})
            cat_objs[name] = cat

        # 3. Create Suppliers
        suppliers_data = [
            ('TechSupply Corp', 'TechSupply Corporation Ltd', '+1 555-0192', 'sales@techsupply.com', '100 Silicon Valley Way, CA'),
            ('Global Office Dist', 'Global Office Distributors', '+1 555-0184', 'orders@globaloffice.com', '45 Commercial Blvd, NY'),
            ('Apex Hardware Ltd', 'Apex Industrial Hardware', '+1 555-0129', 'contact@apexhardware.com', '88 Trade Park, TX'),
        ]
        sup_objs = []
        for name, company, phone, email, address in suppliers_data:
            sup, _ = Supplier.objects.get_or_create(company=company, defaults={
                'name': name, 'phone': phone, 'email': email, 'address': address
            })
            sup_objs.append(sup)

        # 4. Create Customers
        customers_data = [
            ('Acme Corporation', '+1 555-0391', 'procurement@acme.com', '500 Enterprise Ave, CA'),
            ('Jane Smith', '+1 555-0842', 'jane.smith@example.com', '12 Maple Street, NY'),
            ('Summit Retailers', '+1 555-0721', 'info@summitretail.com', '770 Market Street, IL'),
        ]
        cust_objs = []
        for name, phone, email, address in customers_data:
            cust, _ = Customer.objects.get_or_create(name=name, defaults={
                'phone': phone, 'email': email, 'address': address
            })
            cust_objs.append(cust)

        # 5. Create Products
        products_data = [
            ('PRD-ELEC-001', 'Wireless Ergonomic Mouse', '8901234567890', 'Electronics', sup_objs[0], 15.00, 29.99, 50, 10, '2.4GHz Wireless mouse with ergonomic palm grip'),
            ('PRD-ELEC-002', '27-inch 4K LED Monitor', '8901234567891', 'Electronics', sup_objs[0], 180.00, 299.99, 15, 5, 'Ultra HD 4K IPS display with HDMI and DisplayPort'),
            ('PRD-FURN-001', 'High-Back Executive Desk Chair', '8901234567892', 'Furniture', sup_objs[1], 85.00, 159.99, 8, 10, 'Breathable mesh chair with lumbar support'),
            ('PRD-OFFC-001', 'Heavy Duty Desktop Stapler', '8901234567893', 'Office Supplies', sup_objs[1], 4.50, 11.99, 120, 20, 'Staples up to 50 sheets of paper'),
            ('PRD-HARD-001', 'USB-C Multiport Adapter 7-in-1', '8901234567894', 'Hardware', sup_objs[2], 12.00, 24.99, 3, 10, 'Includes 4K HDMI, USB 3.0, SD Card Reader'),
            ('PRD-ELEC-003', 'Mechanical RGB Gaming Keyboard', '8901234567895', 'Electronics', sup_objs[0], 40.00, 79.99, 0, 5, 'Blue switch tactile mechanical keyboard'),
        ]

        prod_objs = []
        for sku, name, barcode, cat_name, supplier, u_price, s_price, stock, reorder, desc in products_data:
            prod, created = Product.objects.get_or_create(sku=sku, defaults={
                'name': name,
                'barcode': barcode,
                'category': cat_objs[cat_name],
                'supplier': supplier,
                'unit_price': Decimal(str(u_price)),
                'selling_price': Decimal(str(s_price)),
                'stock_quantity': stock,
                'reorder_level': reorder,
                'description': desc,
                'status': 'Active'
            })
            prod_objs.append(prod)

        # 6. Create Purchases & PurchaseItems
        if not Purchase.objects.exists():
            pur1 = Purchase.objects.create(
                invoice_no='PUR-2026-001',
                supplier=sup_objs[0],
                total_amount=Decimal('1650.00'),
                purchase_date=timezone.now() - datetime.timedelta(days=10),
                created_by=admin_user,
                notes='Initial tech stock order'
            )
            PurchaseItem.objects.create(purchase=pur1, product=prod_objs[0], quantity=50, purchase_price=Decimal('15.00'), subtotal=Decimal('750.00'))
            PurchaseItem.objects.create(purchase=pur1, product=prod_objs[1], quantity=5, purchase_price=Decimal('180.00'), subtotal=Decimal('900.00'))

        # 7. Create Sales & SaleItems
        if not Sale.objects.exists():
            sale1 = Sale.objects.create(
                invoice_no='INV-2026-001',
                customer=cust_objs[0],
                subtotal=Decimal('299.90'),
                discount=Decimal('10.00'),
                gst_amount=Decimal('52.18'),
                total_amount=Decimal('342.08'),
                sale_date=timezone.now() - datetime.timedelta(days=3),
                created_by=admin_user,
                notes='Corporate order'
            )
            SaleItem.objects.create(sale=sale1, product=prod_objs[0], quantity=2, selling_price=Decimal('29.99'), total_price=Decimal('59.98'))
            SaleItem.objects.create(sale=sale1, product=prod_objs[1], quantity=1, selling_price=Decimal('239.92'), total_price=Decimal('239.92'))

        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
