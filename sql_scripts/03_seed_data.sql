-- ============================================================================
-- SQL SERVER T-SQL SEED DATA: Sample Records for Testing
-- Script: 03_seed_data.sql
-- ============================================================================

-- 1. Insert Initial Users
INSERT INTO dbo.Users (Username, PasswordHash, Email, FirstName, LastName, Role, IsActive)
VALUES 
('admin', 'pbkdf2_sha256$600000$adminpasshash$', 'admin@inventory.com', 'System', 'Admin', 'Admin', 1),
('staff1', 'pbkdf2_sha256$600000$staffpasshash$', 'staff@inventory.com', 'John', 'Staff', 'Staff', 1);

-- 2. Insert Categories
INSERT INTO dbo.Categories (CategoryName, Description, Status)
VALUES 
('Electronics', 'Gadgets, computers, and electronic components', 'Active'),
('Office Supplies', 'Paper, pens, staplers, and desk tools', 'Active'),
('Furniture', 'Desks, chairs, filing cabinets, and office furniture', 'Active'),
('Hardware', 'Tools, cables, adapters, and equipment', 'Active'),
('Beverages', 'Coffee, tea, and office snacks', 'Active');

-- 3. Insert Suppliers
INSERT INTO dbo.Suppliers (SupplierName, Company, Phone, Email, Address)
VALUES 
('TechSupply Corp', 'TechSupply Corporation Ltd', '+1 555-0192', 'sales@techsupply.com', '100 Silicon Valley Way, CA'),
('Global Office Dist', 'Global Office Distributors', '+1 555-0184', 'orders@globaloffice.com', '45 Commercial Blvd, NY'),
('Apex Hardware Ltd', 'Apex Industrial Hardware', '+1 555-0129', 'contact@apexhardware.com', '88 Trade Park, TX');

-- 4. Insert Customers
INSERT INTO dbo.Customers (CustomerName, Phone, Email, Address)
VALUES 
('Acme Corporation', '+1 555-0391', 'procurement@acme.com', '500 Enterprise Ave, CA'),
('Jane Smith', '+1 555-0842', 'jane.smith@example.com', '12 Maple Street, NY'),
('Summit Retailers', '+1 555-0721', 'info@summitretail.com', '770 Market Street, IL');

-- 5. Insert Products
INSERT INTO dbo.Products (SKU, ProductName, Barcode, CategoryID, SupplierID, UnitPrice, SellingPrice, StockQuantity, ReorderLevel, Description, Status)
VALUES 
('PRD-ELEC-001', 'Wireless Ergonomic Mouse', '8901234567890', 1, 1, 15.00, 29.99, 50, 10, '2.4GHz Wireless mouse with ergonomic palm grip', 'Active'),
('PRD-ELEC-002', '27-inch 4K LED Monitor', '8901234567891', 1, 1, 180.00, 299.99, 15, 5, 'Ultra HD 4K IPS display with HDMI and DisplayPort', 'Active'),
('PRD-FURN-001', 'High-Back Executive Desk Chair', '8901234567892', 3, 2, 85.00, 159.99, 8, 10, 'Breathable mesh chair with lumbar support', 'Active'),
('PRD-OFFC-001', 'Heavy Duty Desktop Stapler', '8901234567893', 2, 2, 4.50, 11.99, 120, 20, 'Staples up to 50 sheets of paper', 'Active'),
('PRD-HARD-001', 'USB-C Multiport Adapter 7-in-1', '8901234567894', 4, 3, 12.00, 24.99, 3, 10, 'Includes 4K HDMI, USB 3.0, SD Card Reader', 'Active'),
('PRD-ELEC-003', 'Mechanical RGB Gaming Keyboard', '8901234567895', 1, 1, 40.00, 79.99, 0, 5, 'Blue switch tactile mechanical keyboard', 'Active');

-- 6. Insert Inventory records matching Products
INSERT INTO dbo.Inventory (ProductID, CurrentStock, LowStockThreshold, Status)
SELECT 
    ProductID, 
    StockQuantity, 
    ReorderLevel,
    CASE 
        WHEN StockQuantity = 0 THEN 'Out of Stock'
        WHEN StockQuantity <= ReorderLevel THEN 'Low Stock'
        ELSE 'In Stock'
    END
FROM dbo.Products;

-- 7. Insert Purchases & PurchaseItems
INSERT INTO dbo.Purchases (InvoiceNo, SupplierID, TotalAmount, PurchaseDate, CreatedBy, Notes)
VALUES 
('PUR-2026-001', 1, 1650.00, DATEADD(day, -10, GETDATE()), 1, 'Initial tech stock order'),
('PUR-2026-002', 2, 680.00, DATEADD(day, -5, GETDATE()), 1, 'Office supplies and furniture replenishment');

INSERT INTO dbo.PurchaseItems (PurchaseID, ProductID, Quantity, PurchasePrice, Subtotal)
VALUES 
(1, 1, 50, 15.00, 750.00),
(1, 2, 5, 180.00, 900.00),
(2, 3, 8, 85.00, 680.00);

-- 8. Insert Sales & SaleItems
INSERT INTO dbo.Sales (InvoiceNo, CustomerID, Subtotal, Discount, GSTAmount, TotalAmount, SaleDate, CreatedBy, Notes)
VALUES 
('INV-2026-001', 1, 299.90, 10.00, 26.09, 315.99, DATEADD(day, -3, GETDATE()), 1, 'Bulk corporate purchase'),
('INV-2026-002', 2, 159.99, 0.00, 14.40, 174.39, DATEADD(day, -1, GETDATE()), 2, 'Direct store sale');

INSERT INTO dbo.SaleItems (SaleID, ProductID, Quantity, SellingPrice, TotalPrice)
VALUES 
(1, 1, 2, 29.99, 59.98),
(1, 2, 1, 239.92, 239.92),
(2, 3, 1, 159.99, 159.99);

-- 9. Insert Stock Movement
INSERT INTO dbo.StockMovement (ProductID, MovementType, Quantity, UnitPrice, BalanceAfter, MovementDate, ReferenceNo, CreatedBy, Notes)
VALUES 
(1, 'PURCHASE', 50, 15.00, 50, DATEADD(day, -10, GETDATE()), 'PUR-2026-001', 1, 'Initial Purchase'),
(2, 'PURCHASE', 5, 180.00, 5, DATEADD(day, -10, GETDATE()), 'PUR-2026-001', 1, 'Initial Purchase'),
(1, 'SALE', 2, 29.99, 48, DATEADD(day, -3, GETDATE()), 'INV-2026-001', 1, 'Sale Invoice #INV-2026-001');
