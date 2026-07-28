-- ============================================================================
-- SQL SERVER T-SQL OBJECTS: Views, Stored Procedures, Functions, Triggers
-- Script: 02_views_procedures_triggers.sql
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. VIEWS
-- ----------------------------------------------------------------------------

-- View: Low Stock Products
IF OBJECT_ID('dbo.vw_LowStockProducts', 'V') IS NOT NULL DROP VIEW dbo.vw_LowStockProducts;
GO
CREATE VIEW dbo.vw_LowStockProducts AS
SELECT 
    p.ProductID,
    p.SKU,
    p.ProductName,
    c.CategoryName,
    p.StockQuantity,
    p.ReorderLevel,
    CASE 
        WHEN p.StockQuantity = 0 THEN 'Out of Stock'
        WHEN p.StockQuantity <= p.ReorderLevel THEN 'Low Stock'
        ELSE 'In Stock'
    END AS StockStatus,
    p.SellingPrice,
    (p.StockQuantity * p.SellingPrice) AS StockValue
FROM dbo.Products p
INNER JOIN dbo.Categories c ON p.CategoryID = c.CategoryID
WHERE p.StockQuantity <= p.ReorderLevel;
GO

-- View: Monthly Sales Summary (Aggregates & Window Functions)
IF OBJECT_ID('dbo.vw_MonthlySalesSummary', 'V') IS NOT NULL DROP VIEW dbo.vw_MonthlySalesSummary;
GO
CREATE VIEW dbo.vw_MonthlySalesSummary AS
SELECT 
    YEAR(SaleDate) AS SaleYear,
    MONTH(SaleDate) AS SaleMonth,
    COUNT(SaleID) AS TotalOrders,
    SUM(Subtotal) AS GrossSales,
    SUM(Discount) AS TotalDiscount,
    SUM(GSTAmount) AS TotalGST,
    SUM(TotalAmount) AS NetRevenue,
    LAG(SUM(TotalAmount), 1, 0) OVER (ORDER BY YEAR(SaleDate), MONTH(SaleDate)) AS PreviousMonthRevenue,
    (SUM(TotalAmount) - LAG(SUM(TotalAmount), 1, 0) OVER (ORDER BY YEAR(SaleDate), MONTH(SaleDate))) AS RevenueGrowth
FROM dbo.Sales
GROUP BY YEAR(SaleDate), MONTH(SaleDate);
GO

-- View: Top Selling Products
IF OBJECT_ID('dbo.vw_TopSellingProducts', 'V') IS NOT NULL DROP VIEW dbo.vw_TopSellingProducts;
GO
CREATE VIEW dbo.vw_TopSellingProducts AS
SELECT 
    p.ProductID,
    p.SKU,
    p.ProductName,
    c.CategoryName,
    SUM(si.Quantity) AS TotalQuantitySold,
    SUM(si.TotalPrice) AS TotalRevenue,
    DENSE_RANK() OVER (ORDER BY SUM(si.Quantity) DESC) AS SalesRank
FROM dbo.SaleItems si
INNER JOIN dbo.Products p ON si.ProductID = p.ProductID
INNER JOIN dbo.Categories c ON p.CategoryID = c.CategoryID
GROUP BY p.ProductID, p.SKU, p.ProductName, c.CategoryName;
GO

-- ----------------------------------------------------------------------------
-- 2. FUNCTIONS
-- ----------------------------------------------------------------------------

-- Scalar Function: Calculate Total Inventory Value
IF OBJECT_ID('dbo.fn_CalculateInventoryValue', 'FN') IS NOT NULL DROP FUNCTION dbo.fn_CalculateInventoryValue;
GO
CREATE FUNCTION dbo.fn_CalculateInventoryValue()
RETURNS DECIMAL(18,2)
AS
BEGIN
    DECLARE @TotalValue DECIMAL(18,2);
    SELECT @TotalValue = ISNULL(SUM(StockQuantity * SellingPrice), 0.00)
    FROM dbo.Products
    WHERE Status = 'Active';
    RETURN @TotalValue;
END;
GO

-- Table-Valued Function: Get Customer Purchase History
IF OBJECT_ID('dbo.fn_GetCustomerSalesHistory', 'IF') IS NOT NULL DROP FUNCTION dbo.fn_GetCustomerSalesHistory;
GO
CREATE FUNCTION dbo.fn_GetCustomerSalesHistory(@CustomerID INT)
RETURNS TABLE
AS
RETURN (
    SELECT 
        s.SaleID,
        s.InvoiceNo,
        s.SaleDate,
        s.TotalAmount,
        COUNT(si.SaleItemID) AS ItemCount
    FROM dbo.Sales s
    INNER JOIN dbo.SaleItems si ON s.SaleID = si.SaleID
    WHERE s.CustomerID = @CustomerID
    GROUP BY s.SaleID, s.InvoiceNo, s.SaleDate, s.TotalAmount
);
GO

-- ----------------------------------------------------------------------------
-- 3. STORED PROCEDURES
-- ----------------------------------------------------------------------------

-- Stored Procedure: Process Sale Invoice with Transaction Control
IF OBJECT_ID('dbo.sp_ProcessSaleInvoice', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_ProcessSaleInvoice;
GO
CREATE PROCEDURE dbo.sp_ProcessSaleInvoice
    @InvoiceNo NVARCHAR(50),
    @CustomerID INT = NULL,
    @Subtotal DECIMAL(18,2),
    @Discount DECIMAL(18,2),
    @GSTAmount DECIMAL(18,2),
    @TotalAmount DECIMAL(18,2),
    @CreatedBy INT = NULL,
    @Notes NVARCHAR(500) = NULL,
    @NewSaleID INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    BEGIN TRANSACTION;
    BEGIN TRY
        INSERT INTO dbo.Sales (InvoiceNo, CustomerID, Subtotal, Discount, GSTAmount, TotalAmount, SaleDate, CreatedBy, Notes)
        VALUES (@InvoiceNo, @CustomerID, @Subtotal, @Discount, @GSTAmount, @TotalAmount, GETDATE(), @CreatedBy, @Notes);

        SET @NewSaleID = SCOPE_IDENTITY();

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

-- Stored Procedure: Dashboard Statistics Summary
IF OBJECT_ID('dbo.sp_GetDashboardStats', 'P') IS NOT NULL DROP PROCEDURE dbo.sp_GetDashboardStats;
GO
CREATE PROCEDURE dbo.sp_GetDashboardStats
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        (SELECT COUNT(*) FROM dbo.Products WHERE Status = 'Active') AS TotalProducts,
        (SELECT COUNT(*) FROM dbo.Categories WHERE Status = 'Active') AS TotalCategories,
        (SELECT COUNT(*) FROM dbo.Suppliers) AS TotalSuppliers,
        (SELECT COUNT(*) FROM dbo.Customers) AS TotalCustomers,
        (SELECT ISNULL(SUM(TotalAmount), 0) FROM dbo.Purchases) AS TotalPurchase,
        (SELECT ISNULL(SUM(TotalAmount), 0) FROM dbo.Sales) AS TotalSales,
        (SELECT ISNULL(SUM(StockQuantity * SellingPrice), 0) FROM dbo.Products) AS CurrentInventoryValue,
        (SELECT ISNULL(SUM(TotalAmount), 0) FROM dbo.Sales WHERE CAST(SaleDate AS DATE) = CAST(GETDATE() AS DATE)) AS TodaysSales,
        (SELECT ISNULL(SUM(TotalAmount), 0) FROM dbo.Sales WHERE MONTH(SaleDate) = MONTH(GETDATE()) AND YEAR(SaleDate) = YEAR(GETDATE())) AS MonthlySales,
        (SELECT ISNULL(SUM(TotalAmount), 0) FROM dbo.Purchases WHERE MONTH(PurchaseDate) = MONTH(GETDATE()) AND YEAR(PurchaseDate) = YEAR(GETDATE())) AS MonthlyPurchase,
        (SELECT COUNT(*) FROM dbo.Products WHERE StockQuantity <= ReorderLevel AND StockQuantity > 0) AS LowStockProducts,
        (SELECT COUNT(*) FROM dbo.Products WHERE StockQuantity = 0) AS OutOfStockProducts;
END;
GO

-- ----------------------------------------------------------------------------
-- 4. TRIGGERS
-- ----------------------------------------------------------------------------

-- Trigger: Automatically Increase Stock after PurchaseItem Insert
IF OBJECT_ID('dbo.trg_AfterPurchaseItemInsert', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_AfterPurchaseItemInsert;
GO
CREATE TRIGGER dbo.trg_AfterPurchaseItemInsert
ON dbo.PurchaseItems
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Update Product Stock Quantity
    UPDATE p
    SET p.StockQuantity = p.StockQuantity + i.Quantity,
        p.UpdatedAt = GETDATE()
    FROM dbo.Products p
    INNER JOIN inserted i ON p.ProductID = i.ProductID;

    -- Record Stock Movement
    INSERT INTO dbo.StockMovement (ProductID, MovementType, Quantity, UnitPrice, BalanceAfter, MovementDate, ReferenceNo, CreatedBy)
    SELECT 
        i.ProductID,
        'PURCHASE',
        i.Quantity,
        i.PurchasePrice,
        p.StockQuantity,
        GETDATE(),
        pur.InvoiceNo,
        pur.CreatedBy
    FROM inserted i
    INNER JOIN dbo.Products p ON i.ProductID = p.ProductID
    INNER JOIN dbo.Purchases pur ON i.PurchaseID = pur.PurchaseID;
END;
GO

-- Trigger: Automatically Decrease Stock after SaleItem Insert
IF OBJECT_ID('dbo.trg_AfterSaleItemInsert', 'TR') IS NOT NULL DROP TRIGGER dbo.trg_AfterSaleItemInsert;
GO
CREATE TRIGGER dbo.trg_AfterSaleItemInsert
ON dbo.SaleItems
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Update Product Stock Quantity
    UPDATE p
    SET p.StockQuantity = p.StockQuantity - i.Quantity,
        p.UpdatedAt = GETDATE()
    FROM dbo.Products p
    INNER JOIN inserted i ON p.ProductID = i.ProductID;

    -- Record Stock Movement
    INSERT INTO dbo.StockMovement (ProductID, MovementType, Quantity, UnitPrice, BalanceAfter, MovementDate, ReferenceNo, CreatedBy)
    SELECT 
        i.ProductID,
        'SALE',
        i.Quantity,
        i.SellingPrice,
        p.StockQuantity,
        GETDATE(),
        s.InvoiceNo,
        s.CreatedBy
    FROM inserted i
    INNER JOIN dbo.Products p ON i.ProductID = p.ProductID
    INNER JOIN dbo.Sales s ON i.SaleID = s.SaleID;
END;
GO
