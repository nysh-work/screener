"""
SQLAlchemy ORM models for the stock screener database.
"""
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class CompanyMaster(Base):
    """Master table for company information."""
    __tablename__ = 'company_master'

    ticker = Column(String(50), primary_key=True)
    company_name = Column(String(200))
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)  # in Crores
    listing_date = Column(Date)
    isin = Column(String(50))
    exchange = Column(String(20))

    # Relationships
    fundamentals = relationship("Fundamentals", back_populates="company")
    derived_metrics = relationship("DerivedMetrics", back_populates="company")
    growth_metrics = relationship("GrowthMetrics", back_populates="company")
    quality_metrics = relationship("QualityMetrics", back_populates="company")
    technical_indicators = relationship("TechnicalIndicators", backref="company")
    portfolio = relationship("Portfolio", backref="company")
    watchlist = relationship("Watchlist", backref="company")


class Fundamentals(Base):
    """Fundamental financial data."""
    __tablename__ = 'fundamentals'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), ForeignKey('company_master.ticker'), nullable=False)
    as_of_date = Column(Date, nullable=False)
    price = Column(Float)
    book_value = Column(Float)
    market_cap = Column(Float)
    enterprise_value = Column(Float)
    ebitda = Column(Float)
    net_profit = Column(Float)
    total_assets = Column(Float)
    total_equity = Column(Float)
    total_debt = Column(Float)
    current_assets = Column(Float)
    current_liabilities = Column(Float)
    revenue = Column(Float)
    operating_profit = Column(Float)
    interest_expense = Column(Float)
    cash_flow_operations = Column(Float)

    # Relationship
    company = relationship("CompanyMaster", back_populates="fundamentals")


class DerivedMetrics(Base):
    """Calculated financial ratios and metrics."""
    __tablename__ = 'derived_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), ForeignKey('company_master.ticker'), nullable=False)
    as_of_date = Column(Date, nullable=False)
    price_to_book = Column(Float)
    price_to_earnings = Column(Float)
    ev_ebitda = Column(Float)
    roe = Column(Float)
    roce = Column(Float)
    debt_equity = Column(Float)
    current_ratio = Column(Float)
    interest_coverage = Column(Float)
    opm = Column(Float)  # Operating Profit Margin
    npm = Column(Float)  # Net Profit Margin
    asset_turnover = Column(Float)

    # Relationship
    company = relationship("CompanyMaster", back_populates="derived_metrics")


class GrowthMetrics(Base):
    """Growth-related metrics."""
    __tablename__ = 'growth_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), ForeignKey('company_master.ticker'), nullable=False)
    as_of_date = Column(Date, nullable=False)
    revenue_cagr_3y = Column(Float)
    revenue_cagr_5y = Column(Float)
    profit_cagr_3y = Column(Float)
    profit_cagr_5y = Column(Float)
    ocf_cagr_3y = Column(Float)
    eps_growth_3y = Column(Float)

    # Relationship
    company = relationship("CompanyMaster", back_populates="growth_metrics")


class QualityMetrics(Base):
    """Quality and governance metrics."""
    __tablename__ = 'quality_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), ForeignKey('company_master.ticker'), nullable=False)
    as_of_date = Column(Date, nullable=False)
    promoter_holding = Column(Float)
    pledged_percentage = Column(Float)
    altman_z_score = Column(Float)
    piotroski_score = Column(Integer)
    ocf_to_net_profit = Column(Float)
    days_sales_outstanding = Column(Float)
    inventory_turnover = Column(Float)

    # Relationship
    company = relationship("CompanyMaster", back_populates="quality_metrics")


class AuditLog(Base):
    """Audit trail for operations."""
    __tablename__ = 'audit_log'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    operation = Column(String(50))
    details = Column(Text)
    user = Column(String(50))
    status = Column(String(20))


class TechnicalIndicators(Base):
    """Technical indicators for stocks."""
    __tablename__ = 'technical_indicators'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), ForeignKey('company_master.ticker'), nullable=False)
    as_of_date = Column(Date, nullable=False)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    choppiness_index = Column(Float)
    atr_14 = Column(Float)  # Average True Range


class Portfolio(Base):
    """User portfolio holdings."""
    __tablename__ = 'portfolio'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), ForeignKey('company_master.ticker'), nullable=False)
    purchase_date = Column(Date, nullable=False)
    quantity = Column(Float, nullable=False)
    purchase_price = Column(Float, nullable=False)
    current_price = Column(Float)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Watchlist(Base):
    """User watchlist for tracking stocks."""
    __tablename__ = 'watchlist'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(50), ForeignKey('company_master.ticker'), nullable=False)
    added_date = Column(Date, default=datetime.utcnow)
    target_price = Column(Float)
    notes = Column(Text)
    alert_enabled = Column(Integer, default=0)  # SQLite doesn't have boolean


class CustomScreen(Base):
    """User-defined custom screening criteria."""
    __tablename__ = 'custom_screens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    criteria = Column(Text, nullable=False)  # JSON string of criteria
    logic = Column(String(10), default='AND')  # AND or OR
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class BacktestResult(Base):
    """Results from backtesting screens."""
    __tablename__ = 'backtest_results'

    id = Column(Integer, primary_key=True, autoincrement=True)
    screen_name = Column(String(100), nullable=False)
    backtest_date = Column(Date, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_stocks_screened = Column(Integer)
    stocks_passed = Column(Integer)
    average_return = Column(Float)
    median_return = Column(Float)
    best_performer = Column(String(50))
    worst_performer = Column(String(50))
    results_detail = Column(Text)  # JSON string of detailed results
    created_at = Column(DateTime, default=datetime.utcnow)
