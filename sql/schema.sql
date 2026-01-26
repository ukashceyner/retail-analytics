-- ABOUTME: PostgreSQL schema for retail orders analytics database.
-- ABOUTME: Defines orders table, indexes for query performance, and summary view.

-- Create main orders table
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY,
    order_date DATE NOT NULL,
    ship_mode VARCHAR(50),
    segment VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code INTEGER,
    region VARCHAR(50),
    category VARCHAR(100),
    sub_category VARCHAR(100),
    product_id VARCHAR(100),
    cost_price DECIMAL(10,2),
    list_price DECIMAL(10,2),
    quantity INTEGER,
    discount_percent DECIMAL(5,2),
    discount DECIMAL(10,2),
    sale_price DECIMAL(10,2),
    profit DECIMAL(10,2),
    profit_margin DECIMAL(5,2),
    year INTEGER,
    month INTEGER,
    month_name VARCHAR(20),
    quarter INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for query performance
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_product_id ON orders(product_id);
CREATE INDEX IF NOT EXISTS idx_orders_category ON orders(category);
CREATE INDEX IF NOT EXISTS idx_orders_region ON orders(region);
CREATE INDEX IF NOT EXISTS idx_orders_year_month ON orders(year, month);

-- Create view for summary statistics
CREATE OR REPLACE VIEW order_summary AS
SELECT
    COUNT(*) as total_orders,
    SUM(sale_price) as total_revenue,
    SUM(profit) as total_profit,
    AVG(sale_price) as avg_order_value,
    AVG(profit_margin) as avg_profit_margin,
    MIN(order_date) as first_order_date,
    MAX(order_date) as last_order_date
FROM orders;
