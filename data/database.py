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

from data.models import Base, CompanyMaster, Fundamentals, DerivedMetrics, GrowthMetrics, QualityMetrics, AuditLog


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
            q.piotroski_score
        FROM company_master c
        LEFT JOIN fundamentals f ON c.ticker = f.ticker
        LEFT JOIN derived_metrics d ON c.ticker = d.ticker
        LEFT JOIN growth_metrics g ON c.ticker = g.ticker
        LEFT JOIN quality_metrics q ON c.ticker = q.ticker
        WHERE c.ticker = :ticker
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
