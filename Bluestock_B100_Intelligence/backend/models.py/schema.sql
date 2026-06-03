-- =============================================
-- B100 Intelligence Database Schema
-- =============================================

-- Companies Table
CREATE TABLE company (
    symbol VARCHAR(20) PRIMARY KEY,
    company_name TEXT NOT NULL,
    sector VARCHAR(50) DEFAULT 'Other',
    health_score REAL DEFAULT 70,
    roe REAL DEFAULT 15,
    opm REAL DEFAULT 18,
    debt_to_equity REAL DEFAULT 0.3,
    revenue_growth REAL DEFAULT 10
);

-- Financial Data Table (for future use)
CREATE TABLE financial_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol VARCHAR(20),
    year INTEGER,
    sales BIGINT DEFAULT 0,
    net_profit BIGINT DEFAULT 0,
    opm_pct REAL DEFAULT 0,
    eps REAL DEFAULT 0,
    total_assets BIGINT DEFAULT 0,
    borrowings BIGINT DEFAULT 0,
    debt_to_equity_calc REAL DEFAULT 0,
    
    FOREIGN KEY (symbol) REFERENCES company(symbol)
);

-- Indexes for better performance
CREATE INDEX idx_company_sector ON company(sector);
CREATE INDEX idx_financial_symbol_year ON financial_data(symbol, year);