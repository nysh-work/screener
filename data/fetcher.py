"""
Data fetcher for stock information using yfinance.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List
from datetime import datetime, date
from utils.logger import get_logger
from utils.helpers import clean_numeric
from calculations.ratios import (
    calculate_roe, calculate_roce, calculate_debt_equity,
    calculate_current_ratio, calculate_interest_coverage,
    calculate_price_to_book, calculate_ev_ebitda,
    calculate_opm, calculate_npm, calculate_altman_z_score
)
from calculations.growth import calculate_cagr

logger = get_logger(__name__)


class YFinanceFetcher:
    """Fetch stock data from Yahoo Finance for Indian stocks."""

    def __init__(self):
        """Initialize the fetcher."""
        self.session = None

    def _get_ticker_symbol(self, ticker: str) -> str:
        """
        Convert ticker to Yahoo Finance format (add .NS for NSE or .BO for BSE).

        Args:
            ticker: Base ticker symbol (e.g., 'RELIANCE')

        Returns:
            Formatted ticker (e.g., 'RELIANCE.NS')
        """
        if not ticker.endswith('.NS') and not ticker.endswith('.BO'):
            return f"{ticker}.NS"  # Default to NSE
        return ticker

    def fetch_stock_info(self, ticker: str) -> Optional[Dict]:
        """
        Fetch comprehensive stock information.

        Args:
            ticker: Stock ticker symbol (e.g., 'RELIANCE')

        Returns:
            Dictionary with company master data or None if error
        """
        try:
            yf_ticker = self._get_ticker_symbol(ticker)
            stock = yf.Ticker(yf_ticker)
            info = stock.info

            if not info or 'symbol' not in info:
                logger.warning(f"No data found for {ticker}")
                return None

            # Extract company master data
            data = {
                'ticker': ticker,
                'company_name': info.get('longName', info.get('shortName', ticker)),
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'market_cap': clean_numeric(info.get('marketCap', 0)) / 1e7 if info.get('marketCap') else None,  # Convert to Crores
                'isin': info.get('isin'),
                'exchange': 'NSE' if yf_ticker.endswith('.NS') else 'BSE',
            }

            logger.info(f"Successfully fetched company info for {ticker}")
            return data

        except Exception as e:
            logger.error(f"Error fetching company info for {ticker}: {str(e)}")
            return None

    def fetch_fundamentals(self, ticker: str) -> Optional[Dict]:
        """
        Fetch fundamental financial data.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with fundamental data or None if error
        """
        try:
            yf_ticker = self._get_ticker_symbol(ticker)
            stock = yf.Ticker(yf_ticker)
            info = stock.info

            if not info:
                logger.warning(f"No fundamental data found for {ticker}")
                return None

            # Get balance sheet and income statement
            balance_sheet = stock.balance_sheet
            income_stmt = stock.income_stmt
            cashflow = stock.cashflow

            # Extract data (convert to Crores - divide by 1e7)
            fundamentals = {
                'ticker': ticker,
                'as_of_date': date.today(),
                'price': clean_numeric(info.get('currentPrice')),
                'book_value': clean_numeric(info.get('bookValue')),
                'market_cap': clean_numeric(info.get('marketCap', 0)) / 1e7 if info.get('marketCap') else None,
                'enterprise_value': clean_numeric(info.get('enterpriseValue', 0)) / 1e7 if info.get('enterpriseValue') else None,
            }

            # Try to extract from financial statements
            if not balance_sheet.empty:
                try:
                    latest_bs = balance_sheet.iloc[:, 0]
                    fundamentals['total_assets'] = clean_numeric(latest_bs.get('Total Assets', 0)) / 1e7
                    fundamentals['total_equity'] = clean_numeric(latest_bs.get('Stockholders Equity', latest_bs.get('Total Equity Gross Minority Interest', 0))) / 1e7
                    fundamentals['total_debt'] = clean_numeric(latest_bs.get('Total Debt', 0)) / 1e7
                    fundamentals['current_assets'] = clean_numeric(latest_bs.get('Current Assets', 0)) / 1e7
                    fundamentals['current_liabilities'] = clean_numeric(latest_bs.get('Current Liabilities', 0)) / 1e7
                except Exception as e:
                    logger.debug(f"Error extracting balance sheet data: {e}")

            if not income_stmt.empty:
                try:
                    latest_is = income_stmt.iloc[:, 0]
                    fundamentals['revenue'] = clean_numeric(latest_is.get('Total Revenue', 0)) / 1e7
                    fundamentals['operating_profit'] = clean_numeric(latest_is.get('Operating Income', 0)) / 1e7
                    fundamentals['ebitda'] = clean_numeric(latest_is.get('EBITDA', 0)) / 1e7
                    fundamentals['net_profit'] = clean_numeric(latest_is.get('Net Income', 0)) / 1e7
                    fundamentals['interest_expense'] = clean_numeric(latest_is.get('Interest Expense', 0)) / 1e7
                except Exception as e:
                    logger.debug(f"Error extracting income statement data: {e}")

            if not cashflow.empty:
                try:
                    latest_cf = cashflow.iloc[:, 0]
                    fundamentals['cash_flow_operations'] = clean_numeric(latest_cf.get('Operating Cash Flow', 0)) / 1e7
                except Exception as e:
                    logger.debug(f"Error extracting cashflow data: {e}")

            logger.info(f"Successfully fetched fundamentals for {ticker}")
            return fundamentals

        except Exception as e:
            logger.error(f"Error fetching fundamentals for {ticker}: {str(e)}")
            return None

    def calculate_derived_metrics(self, fundamentals: Dict, info: Dict = None) -> Dict:
        """
        Calculate derived metrics from fundamental data.

        Args:
            fundamentals: Fundamental data dictionary
            info: Additional info from yfinance

        Returns:
            Dictionary with derived metrics
        """
        metrics = {
            'ticker': fundamentals['ticker'],
            'as_of_date': fundamentals.get('as_of_date', date.today()),
        }

        # Price ratios
        if fundamentals.get('price') and fundamentals.get('book_value'):
            metrics['price_to_book'] = calculate_price_to_book(
                fundamentals['price'],
                fundamentals['book_value']
            )

        # EV/EBITDA
        if fundamentals.get('enterprise_value') and fundamentals.get('ebitda'):
            metrics['ev_ebitda'] = calculate_ev_ebitda(
                fundamentals['enterprise_value'],
                fundamentals['ebitda']
            )

        # ROE
        if fundamentals.get('net_profit') and fundamentals.get('total_equity'):
            metrics['roe'] = calculate_roe(
                fundamentals['net_profit'],
                fundamentals['total_equity']
            )

        # ROCE (using EBITDA as proxy for EBIT)
        if fundamentals.get('ebitda') and fundamentals.get('total_assets') and fundamentals.get('current_liabilities'):
            capital_employed = fundamentals['total_assets'] - fundamentals['current_liabilities']
            metrics['roce'] = calculate_roce(fundamentals['ebitda'], capital_employed)

        # Debt to Equity
        if fundamentals.get('total_debt') is not None and fundamentals.get('total_equity'):
            metrics['debt_equity'] = calculate_debt_equity(
                fundamentals['total_debt'],
                fundamentals['total_equity']
            )

        # Current Ratio
        if fundamentals.get('current_assets') and fundamentals.get('current_liabilities'):
            metrics['current_ratio'] = calculate_current_ratio(
                fundamentals['current_assets'],
                fundamentals['current_liabilities']
            )

        # Interest Coverage
        if fundamentals.get('operating_profit') and fundamentals.get('interest_expense'):
            metrics['interest_coverage'] = calculate_interest_coverage(
                fundamentals['operating_profit'],
                fundamentals['interest_expense']
            )

        # Operating Profit Margin
        if fundamentals.get('operating_profit') and fundamentals.get('revenue'):
            metrics['opm'] = calculate_opm(
                fundamentals['operating_profit'],
                fundamentals['revenue']
            )

        # Net Profit Margin
        if fundamentals.get('net_profit') and fundamentals.get('revenue'):
            metrics['npm'] = calculate_npm(
                fundamentals['net_profit'],
                fundamentals['revenue']
            )

        # P/E ratio from info if available
        if info:
            pe = clean_numeric(info.get('trailingPE'))
            if pe:
                metrics['price_to_earnings'] = pe

        return metrics

    def calculate_quality_metrics(self, fundamentals: Dict, info: Dict = None) -> Dict:
        """
        Calculate quality metrics.

        Args:
            fundamentals: Fundamental data dictionary
            info: Additional info from yfinance

        Returns:
            Dictionary with quality metrics
        """
        metrics = {
            'ticker': fundamentals['ticker'],
            'as_of_date': fundamentals.get('as_of_date', date.today()),
        }

        # Promoter holding from info
        if info:
            metrics['promoter_holding'] = clean_numeric(info.get('heldPercentInsiders', 0)) * 100

        # OCF to Net Profit
        if fundamentals.get('cash_flow_operations') and fundamentals.get('net_profit') and fundamentals['net_profit'] != 0:
            metrics['ocf_to_net_profit'] = fundamentals['cash_flow_operations'] / fundamentals['net_profit']

        # Altman Z-Score
        if all(fundamentals.get(k) for k in ['current_assets', 'current_liabilities', 'total_assets', 'ebitda', 'market_cap', 'revenue', 'total_debt']):
            working_capital = fundamentals['current_assets'] - fundamentals['current_liabilities']
            # Use retained earnings proxy (we don't have it, so use 0)
            retained_earnings = 0
            total_liabilities = fundamentals.get('total_debt', 0) + fundamentals.get('current_liabilities', 0)

            metrics['altman_z_score'] = calculate_altman_z_score(
                working_capital=working_capital,
                retained_earnings=retained_earnings,
                ebit=fundamentals.get('ebitda', 0),  # Using EBITDA as proxy
                market_value_equity=fundamentals['market_cap'],
                sales=fundamentals['revenue'],
                total_assets=fundamentals['total_assets'],
                total_liabilities=total_liabilities if total_liabilities > 0 else 1
            )

        return metrics

    def fetch_all_data(self, ticker: str) -> Optional[Dict]:
        """
        Fetch all data for a ticker (company info, fundamentals, derived metrics).

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with all data categorized or None if error
        """
        try:
            yf_ticker = self._get_ticker_symbol(ticker)
            stock = yf.Ticker(yf_ticker)
            info = stock.info

            company_data = self.fetch_stock_info(ticker)
            if not company_data:
                return None

            fundamentals = self.fetch_fundamentals(ticker)
            if not fundamentals:
                return None

            derived_metrics = self.calculate_derived_metrics(fundamentals, info)
            quality_metrics = self.calculate_quality_metrics(fundamentals, info)

            # Initialize growth metrics (will be calculated separately with historical data)
            growth_metrics = {
                'ticker': ticker,
                'as_of_date': date.today(),
            }

            return {
                'company': company_data,
                'fundamentals': fundamentals,
                'derived_metrics': derived_metrics,
                'growth_metrics': growth_metrics,
                'quality_metrics': quality_metrics
            }

        except Exception as e:
            logger.error(f"Error fetching all data for {ticker}: {str(e)}")
            return None


def get_nse_top_stocks() -> List[str]:
    """
    Get a list of popular NSE stocks for initial testing.

    Returns:
        List of ticker symbols
    """
    return [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
        'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'BAJFINANCE',
        'ASIANPAINT', 'MARUTI', 'LT', 'AXISBANK', 'WIPRO',
        'TITAN', 'NESTLEIND', 'KOTAKBANK', 'ULTRACEMCO', 'SUNPHARMA'
    ]
