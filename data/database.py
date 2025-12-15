"""
Database operations and management.
"""
import os
from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

from data.models import (
    Base, CompanyMaster, Fundamentals, DerivedMetrics, GrowthMetrics, QualityMetrics,
    AuditLog, TechnicalIndicators, Portfolio, Watchlist, CustomScreen, BacktestResult
)


class Database:
    """Database manager for stock screener."""

    def __init__(self, db_url: str = None):
        """
        Initialize database connection.

        Args:
            db_url: Database URL (default: sqlite:///data_files/screener.db)
        """
        if db_url is None:
            db_url = os.getenv('DATABASE_URL', 'sqlite:///data_files/screener.db')

        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables in the database."""
        # Ensure data_files directory exists
        os.makedirs('data_files', exist_ok=True)
        Base.metadata.create_all(self.engine)
        print("Database tables created successfully.")

    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        Base.metadata.drop_all(self.engine)
        print("All tables dropped.")

    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions.

        Usage:
            with db.get_session() as session:
                # do database operations
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        Execute a raw SQL query and return results.

        Args:
            query: SQL query string
            params: Query parameters for prepared statements

        Returns:
            List of dictionaries with query results
        """
        with self.get_session() as session:
            if params:
                result = session.execute(text(query), params)
            else:
                result = session.execute(text(query))

            # Convert to list of dicts
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]

    def add_company(self, company_data: Dict) -> None:
        """Add or update company master data."""
        with self.get_session() as session:
            company = session.query(CompanyMaster).filter_by(
                ticker=company_data['ticker']
            ).first()

            if company:
                # Update existing
                for key, value in company_data.items():
                    setattr(company, key, value)
            else:
                # Create new
                company = CompanyMaster(**company_data)
                session.add(company)

    def add_fundamentals(self, fundamentals_data: Dict) -> None:
        """Add fundamental data for a company."""
        with self.get_session() as session:
            fundamentals = Fundamentals(**fundamentals_data)
            session.add(fundamentals)

    def add_derived_metrics(self, metrics_data: Dict) -> None:
        """Add derived metrics for a company."""
        with self.get_session() as session:
            metrics = DerivedMetrics(**metrics_data)
            session.add(metrics)

    def add_growth_metrics(self, growth_data: Dict) -> None:
        """Add growth metrics for a company."""
        with self.get_session() as session:
            growth = GrowthMetrics(**growth_data)
            session.add(growth)

    def add_quality_metrics(self, quality_data: Dict) -> None:
        """Add quality metrics for a company."""
        with self.get_session() as session:
            quality = QualityMetrics(**quality_data)
            session.add(quality)

    def add_technical_indicators(self, technical_data: Dict) -> None:
        """Add technical indicators for a company."""
        with self.get_session() as session:
            indicators = TechnicalIndicators(**technical_data)
            session.add(indicators)

    def add_to_portfolio(self, portfolio_data: Dict) -> None:
        """Add a stock to portfolio."""
        with self.get_session() as session:
            holding = Portfolio(**portfolio_data)
            session.add(holding)

    def remove_from_portfolio(self, portfolio_id: int) -> None:
        """Remove a stock from portfolio by ID."""
        with self.get_session() as session:
            holding = session.query(Portfolio).filter_by(id=portfolio_id).first()
            if holding:
                session.delete(holding)

    def get_portfolio(self) -> List[Dict]:
        """Get all portfolio holdings."""
        query = """
        SELECT
            p.id,
            p.ticker,
            c.company_name,
            p.purchase_date,
            p.quantity,
            p.purchase_price,
            p.current_price,
            p.notes,
            (p.quantity * p.current_price) - (p.quantity * p.purchase_price) as unrealized_pnl,
            ((p.current_price - p.purchase_price) / p.purchase_price * 100) as return_pct,
            dm.ev_ebitda,
            dm.price_to_book,
            ti.ema_20,
            ti.ema_50,
            ti.macd,
            ti.choppiness_index
        FROM portfolio p
        LEFT JOIN company_master c ON p.ticker = c.ticker
        LEFT JOIN derived_metrics dm ON p.ticker = dm.ticker
        LEFT JOIN technical_indicators ti ON p.ticker = ti.ticker
        WHERE (ti.as_of_date = (SELECT MAX(as_of_date) FROM technical_indicators WHERE ticker = p.ticker) OR ti.as_of_date IS NULL)
        AND (dm.as_of_date = (SELECT MAX(as_of_date) FROM derived_metrics WHERE ticker = p.ticker) OR dm.as_of_date IS NULL)
        ORDER BY p.purchase_date DESC
        """
        return self.execute_query(query)

    def update_portfolio_prices(self, ticker: str, current_price: float) -> None:
        """Update current price for all holdings of a ticker."""
        with self.get_session() as session:
            holdings = session.query(Portfolio).filter_by(ticker=ticker).all()
            for holding in holdings:
                holding.current_price = current_price

    def add_to_watchlist(self, watchlist_data: Dict) -> None:
        """Add a stock to watchlist."""
        with self.get_session() as session:
            # Check if already exists
            existing = session.query(Watchlist).filter_by(
                ticker=watchlist_data['ticker']
            ).first()
            if not existing:
                watchlist = Watchlist(**watchlist_data)
                session.add(watchlist)

    def remove_from_watchlist(self, ticker: str) -> None:
        """Remove a stock from watchlist."""
        with self.get_session() as session:
            watchlist = session.query(Watchlist).filter_by(ticker=ticker).first()
            if watchlist:
                session.delete(watchlist)

    def get_watchlist(self) -> List[Dict]:
        """Get all watchlist stocks."""
        query = """
        SELECT
            w.ticker,
            c.company_name,
            c.sector,
            w.added_date,
            w.target_price,
            w.notes,
            f.price as current_price,
            ((w.target_price - f.price) / f.price * 100) as upside_pct,
            dm.ev_ebitda,
            dm.price_to_book,
            ti.ema_20,
            ti.ema_50,
            ti.macd,
            ti.choppiness_index
        FROM watchlist w
        LEFT JOIN company_master c ON w.ticker = c.ticker
        LEFT JOIN fundamentals f ON w.ticker = f.ticker
        LEFT JOIN derived_metrics dm ON w.ticker = dm.ticker
        LEFT JOIN technical_indicators ti ON w.ticker = ti.ticker
        WHERE f.as_of_date = (SELECT MAX(as_of_date) FROM fundamentals WHERE ticker = w.ticker)
        AND (ti.as_of_date = (SELECT MAX(as_of_date) FROM technical_indicators WHERE ticker = w.ticker) OR ti.as_of_date IS NULL)
        AND (dm.as_of_date = (SELECT MAX(as_of_date) FROM derived_metrics WHERE ticker = w.ticker) OR dm.as_of_date IS NULL)
        ORDER BY w.added_date DESC
        """
        return self.execute_query(query)

    def save_custom_screen(self, screen_data: Dict) -> None:
        """Save a custom screen."""
        with self.get_session() as session:
            # Check if screen with same name exists
            existing = session.query(CustomScreen).filter_by(
                name=screen_data['name']
            ).first()

            if existing:
                # Update existing
                for key, value in screen_data.items():
                    setattr(existing, key, value)
                existing.updated_at = datetime.utcnow()
            else:
                # Create new
                screen = CustomScreen(**screen_data)
                session.add(screen)

    def get_custom_screen(self, name: str) -> Optional[Dict]:
        """Get a custom screen by name."""
        with self.get_session() as session:
            screen = session.query(CustomScreen).filter_by(name=name).first()
            if screen:
                return {
                    'id': screen.id,
                    'name': screen.name,
                    'description': screen.description,
                    'criteria': screen.criteria,
                    'logic': screen.logic,
                    'created_at': screen.created_at,
                    'updated_at': screen.updated_at
                }
            return None

    def list_custom_screens(self) -> List[Dict]:
        """List all custom screens."""
        query = """
        SELECT id, name, description, created_at, updated_at
        FROM custom_screens
        ORDER BY name
        """
        return self.execute_query(query)

    def delete_custom_screen(self, name: str) -> None:
        """Delete a custom screen by name."""
        with self.get_session() as session:
            screen = session.query(CustomScreen).filter_by(name=name).first()
            if screen:
                session.delete(screen)

    def save_backtest_result(self, backtest_data: Dict) -> None:
        """Save backtest results."""
        with self.get_session() as session:
            result = BacktestResult(**backtest_data)
            session.add(result)

    def get_backtest_results(self, screen_name: str = None) -> List[Dict]:
        """Get backtest results, optionally filtered by screen name."""
        if screen_name:
            query = """
            SELECT * FROM backtest_results
            WHERE screen_name = :screen_name
            ORDER BY backtest_date DESC
            """
            return self.execute_query(query, {'screen_name': screen_name})
        else:
            query = """
            SELECT * FROM backtest_results
            ORDER BY backtest_date DESC
            """
            return self.execute_query(query)

    def get_company(self, ticker: str) -> Optional[CompanyMaster]:
        """Retrieve company by ticker."""
        with self.get_session() as session:
            return session.query(CompanyMaster).filter_by(ticker=ticker).first()

    def get_all_tickers(self) -> List[str]:
        """Get list of all tickers in database."""
        with self.get_session() as session:
            result = session.query(CompanyMaster.ticker).all()
            return [row[0] for row in result]

    def log_operation(self, operation: str, details: str, status: str = 'success', user: str = 'system') -> None:
        """Log an operation to audit trail."""
        with self.get_session() as session:
            log = AuditLog(
                operation=operation,
                details=details,
                user=user,
                status=status
            )
            session.add(log)

    def get_latest_metrics(self, ticker: str) -> Optional[Dict]:
        """
        Get the latest metrics for a ticker.

        Returns:
            Dictionary with all metrics or None if not found
        """
        query = """
        SELECT
            c.ticker,
            c.company_name,
            c.sector,
            c.industry,
            c.market_cap,
            f.price,
            d.price_to_book,
            d.price_to_earnings,
            d.ev_ebitda,
            d.roe,
            d.roce,
            d.debt_equity,
            d.current_ratio,
            d.interest_coverage,
            d.opm,
            d.npm,
            g.revenue_cagr_3y,
            g.profit_cagr_3y,
            q.promoter_holding,
            q.altman_z_score,
            q.piotroski_score,
            ti.ema_20,
            ti.ema_50,
            ti.macd,
            ti.choppiness_index
        FROM company_master c
        LEFT JOIN fundamentals f ON c.ticker = f.ticker
        LEFT JOIN derived_metrics d ON c.ticker = d.ticker
        LEFT JOIN growth_metrics g ON c.ticker = g.ticker
        LEFT JOIN quality_metrics q ON c.ticker = q.ticker
        LEFT JOIN technical_indicators ti ON c.ticker = ti.ticker
        WHERE c.ticker = :ticker
        AND (ti.as_of_date = (SELECT MAX(as_of_date) FROM technical_indicators WHERE ticker = c.ticker) OR ti.as_of_date IS NULL)
        ORDER BY f.as_of_date DESC
        LIMIT 1
        """

        results = self.execute_query(query, {'ticker': ticker})
        return results[0] if results else None

    def vacuum(self):
        """Optimize database by reclaiming space."""
        with self.engine.connect() as conn:
            conn.execute(text("VACUUM"))
        print("Database vacuumed successfully.")

    def backup(self, backup_path: str = None):
        """
        Create a backup of the database.

        Args:
            backup_path: Path for backup file (default: data_files/screener_backup_YYYYMMDD.db)
        """
        if backup_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'data_files/screener_backup_{timestamp}.db'

        import shutil
        db_path = self.engine.url.database
        shutil.copy2(db_path, backup_path)
        print(f"Database backed up to: {backup_path}")
