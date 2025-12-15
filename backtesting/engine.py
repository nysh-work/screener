"""
Backtesting engine for testing screens on historical data.
"""
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
import json
from data.database import Database
from data.fetcher import YFinanceFetcher
from screener.engine import ScreeningEngine
from utils.logger import get_logger

logger = get_logger(__name__)


class BacktestEngine:
    """Backtest screening strategies on historical data."""

    def __init__(self, db: Database = None):
        """Initialize backtest engine."""
        self.db = db if db else Database()
        self.fetcher = YFinanceFetcher()
        self.screening_engine = ScreeningEngine(self.db)

    def run_backtest(self, screen_name: str, screen_config: Dict,
                    start_date: date, end_date: date = None,
                    holding_period_days: int = 90) -> Dict:
        """
        Run a backtest for a screening strategy.

        Args:
            screen_name: Name of the screen
            screen_config: Screen configuration (criteria, logic)
            start_date: Start date for backtest
            end_date: End date for backtest (default: today)
            holding_period_days: Number of days to hold stocks after screen

        Returns:
            Dictionary with backtest results
        """
        try:
            if end_date is None:
                end_date = date.today()

            logger.info(f"Running backtest for {screen_name} from {start_date} to {end_date}")

            # For simplicity, run screen once at start_date
            # In a full implementation, we'd run it periodically
            results = self._backtest_single_period(
                screen_config,
                start_date,
                end_date,
                holding_period_days
            )

            # Save results
            backtest_data = {
                'screen_name': screen_name,
                'backtest_date': date.today(),
                'start_date': start_date,
                'end_date': end_date,
                'total_stocks_screened': results.get('total_stocks', 0),
                'stocks_passed': results.get('stocks_passed', 0),
                'average_return': results.get('average_return', 0),
                'median_return': results.get('median_return', 0),
                'best_performer': results.get('best_performer'),
                'worst_performer': results.get('worst_performer'),
                'results_detail': json.dumps(results.get('details', []))
            }

            self.db.save_backtest_result(backtest_data)
            logger.info(f"Backtest completed: {results.get('stocks_passed', 0)} stocks passed")

            return results

        except Exception as e:
            logger.error(f"Error running backtest: {str(e)}")
            return {}

    def _backtest_single_period(self, screen_config: Dict, screen_date: date,
                               end_date: date, holding_period_days: int) -> Dict:
        """
        Run backtest for a single period.

        Args:
            screen_config: Screen configuration
            screen_date: Date to run screen
            end_date: End date for calculating returns
            holding_period_days: Holding period in days

        Returns:
            Dictionary with results
        """
        try:
            # Get all tickers available at screen date
            tickers = self.db.get_all_tickers()

            # Run screen (using current data as proxy for historical)
            # In a full implementation, we'd fetch historical fundamentals
            results_df = self.screening_engine.run_custom_screen(screen_config)

            if results_df.empty:
                return {
                    'total_stocks': len(tickers),
                    'stocks_passed': 0,
                    'average_return': 0,
                    'median_return': 0,
                    'details': []
                }

            # Calculate returns for each passed stock
            returns = []
            details = []

            for _, row in results_df.iterrows():
                ticker = row['ticker']

                # Calculate holding period end date
                hold_end = min(screen_date + timedelta(days=holding_period_days), end_date)

                # Get price at screen date and end date
                returns_data = self._calculate_return(ticker, screen_date, hold_end)

                if returns_data:
                    returns.append(returns_data['return'])
                    details.append({
                        'ticker': ticker,
                        'company_name': row.get('company_name', ticker),
                        'buy_price': returns_data['buy_price'],
                        'sell_price': returns_data['sell_price'],
                        'return': returns_data['return'],
                        'screen_date': str(screen_date),
                        'sell_date': str(hold_end)
                    })

            if returns:
                return {
                    'total_stocks': len(tickers),
                    'stocks_passed': len(results_df),
                    'average_return': np.mean(returns),
                    'median_return': np.median(returns),
                    'best_performer': max(details, key=lambda x: x['return'])['ticker'],
                    'worst_performer': min(details, key=lambda x: x['return'])['ticker'],
                    'winning_stocks': len([r for r in returns if r > 0]),
                    'losing_stocks': len([r for r in returns if r < 0]),
                    'max_return': max(returns),
                    'min_return': min(returns),
                    'std_return': np.std(returns),
                    'details': details
                }
            else:
                return {
                    'total_stocks': len(tickers),
                    'stocks_passed': len(results_df),
                    'average_return': 0,
                    'median_return': 0,
                    'details': []
                }

        except Exception as e:
            logger.error(f"Error in single period backtest: {str(e)}")
            return {}

    def _calculate_return(self, ticker: str, buy_date: date, sell_date: date) -> Optional[Dict]:
        """
        Calculate return for a stock between two dates.

        Args:
            ticker: Stock ticker
            buy_date: Purchase date
            sell_date: Sell date

        Returns:
            Dictionary with return data or None
        """
        try:
            # Fetch historical prices
            yf_ticker = self.fetcher._get_ticker_symbol(ticker)

            import yfinance as yf
            stock = yf.Ticker(yf_ticker)

            # Get historical data
            hist = stock.history(start=buy_date, end=sell_date + timedelta(days=5))

            if hist.empty or len(hist) < 2:
                logger.warning(f"Insufficient data for {ticker}")
                return None

            # Get buy and sell prices
            buy_price = hist['Close'].iloc[0]
            sell_price = hist['Close'].iloc[-1]

            # Calculate return
            return_pct = ((sell_price - buy_price) / buy_price) * 100

            return {
                'buy_price': float(buy_price),
                'sell_price': float(sell_price),
                'return': float(return_pct)
            }

        except Exception as e:
            logger.error(f"Error calculating return for {ticker}: {str(e)}")
            return None

    def get_backtest_history(self, screen_name: str = None) -> pd.DataFrame:
        """
        Get backtest history.

        Args:
            screen_name: Optional screen name to filter

        Returns:
            DataFrame with backtest results
        """
        try:
            results = self.db.get_backtest_results(screen_name)
            if not results:
                return pd.DataFrame()

            return pd.DataFrame(results)

        except Exception as e:
            logger.error(f"Error getting backtest history: {str(e)}")
            return pd.DataFrame()

    def compare_screens(self, screen_names: List[str], start_date: date,
                       end_date: date = None) -> pd.DataFrame:
        """
        Compare performance of multiple screens.

        Args:
            screen_names: List of screen names
            start_date: Start date
            end_date: End date (default: today)

        Returns:
            DataFrame with comparison results
        """
        try:
            comparison = []

            for screen_name in screen_names:
                results = self.db.get_backtest_results(screen_name)

                if results:
                    # Filter by date range
                    filtered = [r for r in results
                               if start_date <= r['start_date'] <= (end_date or date.today())]

                    if filtered:
                        comparison.append({
                            'screen_name': screen_name,
                            'avg_return': np.mean([r['average_return'] for r in filtered]),
                            'median_return': np.mean([r['median_return'] for r in filtered]),
                            'num_backtests': len(filtered),
                            'avg_stocks_passed': np.mean([r['stocks_passed'] for r in filtered])
                        })

            return pd.DataFrame(comparison)

        except Exception as e:
            logger.error(f"Error comparing screens: {str(e)}")
            return pd.DataFrame()
