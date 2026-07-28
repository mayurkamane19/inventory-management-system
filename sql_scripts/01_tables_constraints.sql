-- ============================================================================
-- SQL SERVER T-SQL DATABASE SCHEMA: Inventory Management System
-- Script: 01_tables_constraints.sql
-- ============================================================================

-- Create Database if not exists (Uncomment when running directly on SQL Server)
-- IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'InventoryDB')
-- BEGIN
--     CREATE DATABASE InventoryDB;
-- END
-- GO
-- USE InventoryDB;
-- GO

-- ----------------------------------------------------------------------------
-- 1. Table: Users
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.Users', 'U') IS NOT NULL DROP TABLE dbo.Users;
CREATE TABLE dbo.Users (
    UserID INT IDENTITY(1,1) NOT NULL,
    Username NVARCHAR(50) NOT NULL,
    PasswordHash NVARCHAR(255) NOT NULL,
    Email NVARCHAR(100) NOT NULL,
    FirstName NVARCHAR(50) NULL,
    LastName NVARCHAR(50) NULL,
    Role NVARCHAR(20) NOT NULL DEFAULT 'Staff', -- 'Admin' or 'Staff'
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Users PRIMARY KEY CLUSTERED (UserID),
    CONSTRAINT UQ_Users_Username UNIQUE (Username),
    CONSTRAINT UQ_Users_Email UNIQUE (Email),
    CONSTRAINT CK_Users_Role CHECK (Role IN ('Admin', 'Staff'))
);

-- ----------------------------------------------------------------------------
-- 2. Table: Categories
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.Categories', 'U') IS NOT NULL DROP TABLE dbo.Categories;
CREATE TABLE dbo.Categories (
    CategoryID INT IDENTITY(1,1) NOT NULL,
    CategoryName NVARCHAR(100) NOT NULL,
    Description NVARCHAR(500) NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active', -- 'Active', 'Inactive'
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Categories PRIMARY KEY CLUSTERED (CategoryID),
    CONSTRAINT UQ_Categories_Name UNIQUE (CategoryName),
    CONSTRAINT CK_Categories_Status CHECK (Status IN ('Active', 'Inactive'))
);

-- ----------------------------------------------------------------------------
-- 3. Table: Suppliers
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.Suppliers', 'U') IS NOT NULL DROP TABLE dbo.Suppliers;
CREATE TABLE dbo.Suppliers (
    SupplierID INT IDENTITY(1,1) NOT NULL,
    SupplierName NVARCHAR(100) NOT NULL,
    Company NVARCHAR(100) NULL,
    Phone NVARCHAR(20) NULL,
    Email NVARCHAR(100) NULL,
    Address NVARCHAR(255) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Suppliers PRIMARY KEY CLUSTERED (SupplierID)
);

-- ----------------------------------------------------------------------------
-- 4. Table: Customers
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.Customers', 'U') IS NOT NULL DROP TABLE dbo.Customers;
CREATE TABLE dbo.Customers (
    CustomerID INT IDENTITY(1,1) NOT NULL,
    CustomerName NVARCHAR(100) NOT NULL,
    Phone NVARCHAR(20) NULL,
    Email NVARCHAR(100) NULL,
    Address NVARCHAR(255) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Customers PRIMARY KEY CLUSTERED (CustomerID)
);

-- ----------------------------------------------------------------------------
-- 5. Table: Products
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.Products', 'U') IS NOT NULL DROP TABLE dbo.Products;
CREATE TABLE dbo.Products (
    ProductID INT IDENTITY(1,1) NOT NULL,
    SKU NVARCHAR(50) NOT NULL,
    ProductName NVARCHAR(150) NOT NULL,
    Barcode NVARCHAR(50) NULL,
    CategoryID INT NOT NULL,
    SupplierID INT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    SellingPrice DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    StockQuantity INT NOT NULL DEFAULT 0,
    ReorderLevel INT NOT NULL DEFAULT 10,
    ImagePath NVARCHAR(255) NULL,
    Description NVARCHAR(MAX) NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active', -- 'Active', 'Inactive'
    QRCodePath NVARCHAR(255) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Products PRIMARY KEY CLUSTERED (ProductID),
    CONSTRAINT UQ_Products_SKU UNIQUE (SKU),
    CONSTRAINT FK_Products_Categories FOREIGN KEY (CategoryID) REFERENCES dbo.Categories(CategoryID),
    CONSTRAINT FK_Products_Suppliers FOREIGN KEY (SupplierID) REFERENCES dbo.Suppliers(SupplierID),
    CONSTRAINT CK_Products_UnitPrice CHECK (UnitPrice >= 0),
    CONSTRAINT CK_Products_SellingPrice CHECK (SellingPrice >= 0),
    CONSTRAINT CK_Products_StockQuantity CHECK (StockQuantity >= 0),
    CONSTRAINT CK_Products_ReorderLevel CHECK (ReorderLevel >= 0)
);

-- ----------------------------------------------------------------------------
-- 6. Table: Purchases
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.Purchases', 'U') IS NOT NULL DROP TABLE dbo.Purchases;
CREATE TABLE dbo.Purchases (
    PurchaseID INT IDENTITY(1,1) NOT NULL,
    InvoiceNo NVARCHAR(50) NOT NULL,
    SupplierID INT NOT NULL,
    TotalAmount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    PurchaseDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    CreatedBy INT NULL,
    Notes NVARCHAR(500) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Purchases PRIMARY KEY CLUSTERED (PurchaseID),
    CONSTRAINT UQ_Purchases_InvoiceNo UNIQUE (InvoiceNo),
    CONSTRAINT FK_Purchases_Suppliers FOREIGN KEY (SupplierID) REFERENCES dbo.Suppliers(SupplierID),
    CONSTRAINT FK_Purchases_Users FOREIGN KEY (CreatedBy) REFERENCES dbo.Users(UserID)
);

-- ----------------------------------------------------------------------------
-- 7. Table: PurchaseItems
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.PurchaseItems', 'U') IS NOT NULL DROP TABLE dbo.PurchaseItems;
CREATE TABLE dbo.PurchaseItems (
    PurchaseItemID INT IDENTITY(1,1) NOT NULL,
    PurchaseID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    PurchasePrice DECIMAL(18,2) NOT NULL,
    Subtotal DECIMAL(18,2) NOT NULL,
    CONSTRAINT PK_PurchaseItems PRIMARY KEY CLUSTERED (PurchaseItemID),
    CONSTRAINT FK_PurchaseItems_Purchases FOREIGN KEY (PurchaseID) REFERENCES dbo.Purchases(PurchaseID) ON DELETE CASCADE,
    CONSTRAINT FK_PurchaseItems_Products FOREIGN KEY (ProductID) REFERENCES dbo.Products(ProductID),
    CONSTRAINT CK_PurchaseItems_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_PurchaseItems_PurchasePrice CHECK (PurchasePrice >= 0)
);

-- ----------------------------------------------------------------------------
-- 8. Table: Sales
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.Sales', 'U') IS NOT NULL DROP TABLE dbo.Sales;
CREATE TABLE dbo.Sales (
    SaleID INT IDENTITY(1,1) NOT NULL,
    InvoiceNo NVARCHAR(50) NOT NULL,
    CustomerID INT NULL,
    Subtotal DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    Discount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    GSTAmount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    TotalAmount DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    SaleDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    CreatedBy INT NULL,
    Notes NVARCHAR(500) NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    CONSTRAINT PK_Sales PRIMARY KEY CLUSTERED (SaleID),
    CONSTRAINT UQ_Sales_InvoiceNo UNIQUE (InvoiceNo),
    CONSTRAINT FK_Sales_Customers FOREIGN KEY (CustomerID) REFERENCES dbo.Customers(CustomerID),
    CONSTRAINT FK_Sales_Users FOREIGN KEY (CreatedBy) REFERENCES dbo.Users(UserID)
);

-- ----------------------------------------------------------------------------
-- 9. Table: SaleItems
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.SaleItems', 'U') IS NOT NULL DROP TABLE dbo.SaleItems;
CREATE TABLE dbo.SaleItems (
    SaleItemID INT IDENTITY(1,1) NOT NULL,
    SaleID INT NOT NULL,
    ProductID INT NOT NULL,
    Quantity INT NOT NULL,
    SellingPrice DECIMAL(18,2) NOT NULL,
    TotalPrice DECIMAL(18,2) NOT NULL,
    CONSTRAINT PK_SaleItems PRIMARY KEY CLUSTERED (SaleItemID),
    CONSTRAINT FK_SaleItems_Sales FOREIGN KEY (SaleID) REFERENCES dbo.Sales(SaleID) ON DELETE CASCADE,
    CONSTRAINT FK_SaleItems_Products FOREIGN KEY (ProductID) REFERENCES dbo.Products(ProductID),
    CONSTRAINT CK_SaleItems_Quantity CHECK (Quantity > 0),
    CONSTRAINT CK_SaleItems_SellingPrice CHECK (SellingPrice >= 0)
);

-- ----------------------------------------------------------------------------
-- 10. Table: Inventory
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.Inventory', 'U') IS NOT NULL DROP TABLE dbo.Inventory;
CREATE TABLE dbo.Inventory (
    InventoryID INT IDENTITY(1,1) NOT NULL,
    ProductID INT NOT NULL,
    CurrentStock INT NOT NULL DEFAULT 0,
    LowStockThreshold INT NOT NULL DEFAULT 10,
    LastStockUpdate DATETIME2 NOT NULL DEFAULT GETDATE(),
    Status NVARCHAR(20) NOT NULL DEFAULT 'In Stock', -- 'In Stock', 'Low Stock', 'Out of Stock'
    CONSTRAINT PK_Inventory PRIMARY KEY CLUSTERED (InventoryID),
    CONSTRAINT UQ_Inventory_Product UNIQUE (ProductID),
    CONSTRAINT FK_Inventory_Products FOREIGN KEY (ProductID) REFERENCES dbo.Products(ProductID) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 11. Table: StockMovement
-- ----------------------------------------------------------------------------
IF OBJECT_ID('dbo.StockMovement', 'U') IS NOT NULL DROP TABLE dbo.StockMovement;
CREATE TABLE dbo.StockMovement (
    MovementID INT IDENTITY(1,1) NOT NULL,
    ProductID INT NOT NULL,
    MovementType NVARCHAR(20) NOT NULL, -- 'PURCHASE', 'SALE', 'ADJUSTMENT'
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL DEFAULT 0.00,
    BalanceAfter INT NOT NULL,
    MovementDate DATETIME2 NOT NULL DEFAULT GETDATE(),
    ReferenceNo NVARCHAR(50) NULL,
    CreatedBy INT NULL,
    Notes NVARCHAR(255) NULL,
    CONSTRAINT PK_StockMovement PRIMARY KEY CLUSTERED (MovementID),
    CONSTRAINT FK_StockMovement_Products FOREIGN KEY (ProductID) REFERENCES dbo.Products(ProductID),
    CONSTRAINT FK_StockMovement_Users FOREIGN KEY (CreatedBy) REFERENCES dbo.Users(UserID),
    CONSTRAINT CK_StockMovement_Type CHECK (MovementType IN ('PURCHASE', 'SALE', 'ADJUSTMENT'))
);

-- ----------------------------------------------------------------------------
-- INDEXES FOR QUERY OPTIMIZATION
-- ----------------------------------------------------------------------------
CREATE NONCLUSTERED INDEX IX_Products_SKU ON dbo.Products(SKU);
CREATE NONCLUSTERED INDEX IX_Products_Barcode ON dbo.Products(Barcode);
CREATE NONCLUSTERED INDEX IX_Products_Category ON dbo.Products(CategoryID);
CREATE NONCLUSTERED INDEX IX_Products_Supplier ON dbo.Products(SupplierID);
CREATE NONCLUSTERED INDEX IX_Purchases_Date ON dbo.Purchases(PurchaseDate);
CREATE NONCLUSTERED INDEX IX_Sales_Date ON dbo.Sales(SaleDate);
CREATE NONCLUSTERED INDEX IX_StockMovement_Product_Date ON dbo.StockMovement(ProductID, MovementDate DESC);
