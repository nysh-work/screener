"""
Portfolio tracking and management.
"""
from datetime import date, datetime
from typing import Dict, List, Optional
import pandas as pd
from data.database import Database
from data.fetcher import YFinanceFetcher
from utils.logger import get_logger

logger = get_logger(__name__)


class PortfolioTracker:
    """Manage portfolio holdings and watchlist."""

    def __init__(self, db: Database = None):
        """Initialize portfolio tracker."""
        self.db = db if db else Database()
        self.fetcher = YFinanceFetcher()

    def add_holding(self, ticker: str, quantity: float, purchase_price: float,
                    purchase_date: date, notes: str = None) -> bool:
        """
        Add a stock to portfolio.

        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares
            purchase_price: Purchase price per share
            purchase_date: Date of purchase
            notes: Optional notes

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current price
            current_price = self._get_current_price(ticker)

            portfolio_data = {
                'ticker': ticker.upper(),
                'quantity': quantity,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'purchase_date': purchase_date,
                'notes': notes
            }

            success = self.db.add_to_portfolio(portfolio_data)
            if success:
                logger.info(f"Added {quantity} shares of {ticker} to portfolio")
                return True
            else:
                logger.warning(f"Duplicate holding not added: {ticker} {quantity} shares @ ₹{purchase_price} on {purchase_date}")
                return False

        except Exception as e:
            logger.error(f"Error adding to portfolio: {str(e)}")
            return False

    def remove_holding(self, portfolio_id: int) -> bool:
        """
        Remove a holding from portfolio.

        Args:
            portfolio_id: Portfolio entry ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.remove_from_portfolio(portfolio_id)
            logger.info(f"Removed holding ID {portfolio_id} from portfolio")
            return True
        except Exception as e:
            logger.error(f"Error removing from portfolio: {str(e)}")
            return False

    def get_portfolio(self) -> pd.DataFrame:
        """
        Get portfolio holdings with current metrics.

        Returns:
            DataFrame with portfolio holdings
        """
        try:
            holdings = self.db.get_portfolio()
            if not holdings:
                return pd.DataFrame()

            df = pd.DataFrame(holdings)
            return df

        except Exception as e:
            logger.error(f"Error getting portfolio: {str(e)}")
            return pd.DataFrame()

    def update_portfolio_prices(self) -> int:
        """
        Update current prices for all holdings.

        Returns:
            Number of holdings updated
        """
        try:
            holdings = self.db.get_portfolio()
            updated_count = 0

            for holding in holdings:
                ticker = holding['ticker']
                current_price = self._get_current_price(ticker)

                if current_price:
                    self.db.update_portfolio_prices(ticker, current_price)
                    updated_count += 1

            logger.info(f"Updated prices for {updated_count} holdings")
            return updated_count

        except Exception as e:
            logger.error(f"Error updating portfolio prices: {str(e)}")
            return 0

    def get_portfolio_summary(self) -> Dict:
        """
        Get portfolio summary statistics.

        Returns:
            Dictionary with summary metrics
        """
        try:
            holdings = self.get_portfolio()

            if holdings.empty:
                return {
                    'total_holdings': 0,
                    'total_invested': 0,
                    'current_value': 0,
                    'total_pnl': 0,
                    'total_return_pct': 0
                }

            total_invested = (holdings['quantity'] * holdings['purchase_price']).sum()
            current_value = (holdings['quantity'] * holdings['current_price']).sum()
            total_pnl = current_value - total_invested
            total_return_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0

            return {
                'total_holdings': len(holdings),
                'total_invested': total_invested,
                'current_value': current_value,
                'total_pnl': total_pnl,
                'total_return_pct': total_return_pct,
                'best_performer': holdings.loc[holdings['return_pct'].idxmax()]['ticker'] if not holdings.empty else None,
                'worst_performer': holdings.loc[holdings['return_pct'].idxmin()]['ticker'] if not holdings.empty else None
            }

        except Exception as e:
            logger.error(f"Error calculating portfolio summary: {str(e)}")
            return {}

    def add_to_watchlist(self, ticker: str, target_price: float = None, notes: str = None) -> bool:
        """
        Add a stock to watchlist.

        Args:
            ticker: Stock ticker symbol
            target_price: Optional target price
            notes: Optional notes

        Returns:
            True if successful, False otherwise
        """
        try:
            watchlist_data = {
                'ticker': ticker.upper(),
                'target_price': target_price,
                'notes': notes,
                'added_date': date.today()
            }

            self.db.add_to_watchlist(watchlist_data)
            logger.info(f"Added {ticker} to watchlist")
            return True

        except Exception as e:
            logger.error(f"Error adding to watchlist: {str(e)}")
            return False

    def remove_from_watchlist(self, ticker: str) -> bool:
        """
        Remove a stock from watchlist.

        Args:
            ticker: Stock ticker symbol

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.remove_from_watchlist(ticker.upper())
            logger.info(f"Removed {ticker} from watchlist")
            return True
        except Exception as e:
            logger.error(f"Error removing from watchlist: {str(e)}")
            return False

    def get_watchlist(self) -> pd.DataFrame:
        """
        Get watchlist with current prices.

        Returns:
            DataFrame with watchlist stocks
        """
        try:
            watchlist = self.db.get_watchlist()
            if not watchlist:
                return pd.DataFrame()

            df = pd.DataFrame(watchlist)
            return df

        except Exception as e:
            logger.error(f"Error getting watchlist: {str(e)}")
            return pd.DataFrame()

    def _get_current_price(self, ticker: str) -> Optional[float]:
        """
        Get current price for a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Current price or None if not available
        """
        try:
            yf_ticker = self.fetcher._get_ticker_symbol(ticker)
            import yfinance as yf
            stock = yf.Ticker(yf_ticker)
            info = stock.info

            return info.get('currentPrice') or info.get('regularMarketPrice')

        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {str(e)}")
            return None
