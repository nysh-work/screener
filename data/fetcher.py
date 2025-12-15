"""
Data fetcher for stock information using yfinance.
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, List, Tuple
from datetime import datetime, date, timedelta
from utils.logger import get_logger
from utils.helpers import clean_numeric
from calculations.ratios import (
    calculate_roe, calculate_roce, calculate_debt_equity,
    calculate_current_ratio, calculate_interest_coverage,
    calculate_price_to_book, calculate_ev_ebitda,
    calculate_opm, calculate_npm, calculate_altman_z_score
)
from calculations.growth import calculate_cagr
from calculations.technical import (
    calculate_ema, calculate_macd, calculate_choppiness_index,
    calculate_atr, detect_macd_crossover
)

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

    def fetch_historical_financials(self, ticker: str) -> Optional[Dict]:
        """
        Fetch historical financial data for growth calculations.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with historical revenue, profit, and OCF data
        """
        try:
            yf_ticker = self._get_ticker_symbol(ticker)
            stock = yf.Ticker(yf_ticker)

            # Get income statement and cashflow
            income_stmt = stock.income_stmt
            cashflow = stock.cashflow

            historical_data = {
                'ticker': ticker,
                'revenue': [],
                'net_profit': [],
                'operating_cashflow': [],
                'dates': []
            }

            if not income_stmt.empty:
                # Extract revenue and net profit (columns are dates, most recent first)
                for col in income_stmt.columns:
                    revenue = clean_numeric(income_stmt.loc['Total Revenue', col] if 'Total Revenue' in income_stmt.index else 0)
                    net_profit = clean_numeric(income_stmt.loc['Net Income', col] if 'Net Income' in income_stmt.index else 0)

                    if revenue and net_profit:
                        historical_data['revenue'].append(revenue / 1e7)  # Convert to Crores
                        historical_data['net_profit'].append(net_profit / 1e7)
                        historical_data['dates'].append(col)

            if not cashflow.empty:
                # Extract operating cashflow
                for col in cashflow.columns:
                    ocf = clean_numeric(cashflow.loc['Operating Cash Flow', col] if 'Operating Cash Flow' in cashflow.index else 0)
                    if ocf:
                        historical_data['operating_cashflow'].append(ocf / 1e7)

            logger.info(f"Fetched {len(historical_data['revenue'])} historical data points for {ticker}")
            return historical_data if historical_data['revenue'] else None

        except Exception as e:
            logger.error(f"Error fetching historical financials for {ticker}: {str(e)}")
            return None

    def calculate_growth_metrics_from_history(self, ticker: str, historical_data: Dict) -> Dict:
        """
        Calculate growth metrics from historical data.

        Args:
            ticker: Stock ticker symbol
            historical_data: Dictionary with historical financial data

        Returns:
            Dictionary with growth metrics
        """
        metrics = {
            'ticker': ticker,
            'as_of_date': date.today(),
        }

        try:
            revenue = historical_data.get('revenue', [])
            net_profit = historical_data.get('net_profit', [])
            ocf = historical_data.get('operating_cashflow', [])

            # Calculate revenue CAGR (need at least 4 years for 3Y CAGR)
            if len(revenue) >= 4:
                metrics['revenue_cagr_3y'] = calculate_cagr(revenue[-1], revenue[-4], 3)

            if len(revenue) >= 6:
                metrics['revenue_cagr_5y'] = calculate_cagr(revenue[-1], revenue[-6], 5)

            # Calculate profit CAGR
            if len(net_profit) >= 4:
                metrics['profit_cagr_3y'] = calculate_cagr(net_profit[-1], net_profit[-4], 3)

            if len(net_profit) >= 6:
                metrics['profit_cagr_5y'] = calculate_cagr(net_profit[-1], net_profit[-6], 5)

            # Calculate OCF CAGR
            if len(ocf) >= 4:
                metrics['ocf_cagr_3y'] = calculate_cagr(ocf[-1], ocf[-4], 3)

            logger.info(f"Calculated growth metrics for {ticker}")
            return metrics

        except Exception as e:
            logger.error(f"Error calculating growth metrics for {ticker}: {str(e)}")
            return metrics

    def fetch_historical_prices(self, ticker: str, period: str = '1y') -> Optional[pd.DataFrame]:
        """
        Fetch historical price data.

        Args:
            ticker: Stock ticker symbol
            period: Period for historical data (e.g., '1y', '6mo', '3mo')

        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            yf_ticker = self._get_ticker_symbol(ticker)
            stock = yf.Ticker(yf_ticker)
            hist = stock.history(period=period)

            if hist.empty:
                logger.warning(f"No historical price data found for {ticker}")
                return None

            logger.info(f"Fetched {len(hist)} days of price data for {ticker}")
            return hist

        except Exception as e:
            logger.error(f"Error fetching historical prices for {ticker}: {str(e)}")
            return None

    def calculate_technical_indicators_from_history(self, ticker: str, price_data: pd.DataFrame) -> Optional[Dict]:
        """
        Calculate technical indicators from historical price data.

        Args:
            ticker: Stock ticker symbol
            price_data: DataFrame with OHLCV data

        Returns:
            Dictionary with technical indicators
        """
        try:
            if price_data is None or price_data.empty:
                return None

            close = price_data['Close']
            high = price_data['High']
            low = price_data['Low']

            indicators = {
                'ticker': ticker,
                'as_of_date': date.today(),
            }

            # Calculate EMAs
            if len(close) >= 50:
                ema_20 = calculate_ema(close, 20)
                ema_50 = calculate_ema(close, 50)
                indicators['ema_20'] = float(ema_20.iloc[-1])
                indicators['ema_50'] = float(ema_50.iloc[-1])

            # Calculate MACD
            if len(close) >= 26:
                macd_line, signal_line, histogram = calculate_macd(close)
                indicators['macd'] = float(macd_line.iloc[-1])
                indicators['macd_signal'] = float(signal_line.iloc[-1])
                indicators['macd_histogram'] = float(histogram.iloc[-1])

            # Calculate Choppiness Index
            if len(close) >= 14:
                ci = calculate_choppiness_index(high, low, close, period=14)
                indicators['choppiness_index'] = float(ci.iloc[-1])

            # Calculate ATR
            if len(close) >= 14:
                atr = calculate_atr(high, low, close, period=14)
                indicators['atr_14'] = float(atr.iloc[-1])

            logger.info(f"Calculated technical indicators for {ticker}")
            return indicators

        except Exception as e:
            logger.error(f"Error calculating technical indicators for {ticker}: {str(e)}")
            return None

    def fetch_all_data(self, ticker: str, include_history: bool = True) -> Optional[Dict]:
        """
        Fetch all data for a ticker (company info, fundamentals, derived metrics, growth, technical).

        Args:
            ticker: Stock ticker symbol
            include_history: Whether to fetch historical data for growth and technical indicators

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

            # Fetch and calculate growth metrics from historical data
            growth_metrics = {
                'ticker': ticker,
                'as_of_date': date.today(),
            }

            if include_history:
                logger.info(f"Fetching historical data for {ticker}...")
                historical_financials = self.fetch_historical_financials(ticker)
                if historical_financials:
                    growth_metrics = self.calculate_growth_metrics_from_history(ticker, historical_financials)

            # Fetch and calculate technical indicators
            technical_indicators = None
            if include_history:
                logger.info(f"Fetching price history for {ticker}...")
                price_data = self.fetch_historical_prices(ticker, period='1y')
                if price_data is not None:
                    technical_indicators = self.calculate_technical_indicators_from_history(ticker, price_data)

            result = {
                'company': company_data,
                'fundamentals': fundamentals,
                'derived_metrics': derived_metrics,
                'growth_metrics': growth_metrics,
                'quality_metrics': quality_metrics
            }

            if technical_indicators:
                result['technical_indicators'] = technical_indicators

            return result

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


def get_nifty_50() -> List[str]:
    """
    Get NIFTY 50 constituents.

    Returns:
        List of ticker symbols
    """
    return [
        'ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK',
        'BAJAJ-AUTO', 'BAJFINANCE', 'BAJAJFINSV', 'BPCL', 'BHARTIARTL',
        'BRITANNIA', 'CIPLA', 'COALINDIA', 'DIVISLAB', 'DRREDDY',
        'EICHERMOT', 'GRASIM', 'HCLTECH', 'HDFCBANK', 'HDFCLIFE',
        'HEROMOTOCO', 'HINDALCO', 'HINDUNILVR', 'ICICIBANK', 'ITC',
        'INDUSINDBK', 'INFY', 'JSWSTEEL', 'KOTAKBANK', 'LT',
        'M&M', 'MARUTI', 'NESTLEIND', 'NTPC', 'ONGC',
        'POWERGRID', 'RELIANCE', 'SBILIFE', 'SBIN', 'SUNPHARMA',
        'TCS', 'TATACONSUM', 'TATAMOTORS', 'TATASTEEL', 'TECHM',
        'TITAN', 'ULTRACEMCO', 'UPL', 'WIPRO', 'LTIM'
    ]


def get_nifty_100() -> List[str]:
    """
    Get NIFTY 100 constituents (includes NIFTY 50).

    Returns:
        List of ticker symbols
    """
    nifty_50 = get_nifty_50()
    nifty_next_50 = [
        'ACC', 'AUBANK', 'ATUL', 'ABBOTINDIA', 'ADANIGREEN',
        'AMBUJACEM', 'APOLLOTYRE', 'ASHOKLEY', 'ASTRAL', 'AUROPHARMA',
        'DALBHARAT', 'BANDHANBNK', 'BANKBARODA', 'BERGEPAINT', 'BEL',
        'BOSCHLTD', 'CANBK', 'CHOLAFIN', 'COLPAL', 'CONCOR',
        'DABUR', 'DLF', 'GAIL', 'GODREJCP', 'GUJGASLTD',
        'HAL', 'HAVELLS', 'HDFCAMC', 'ICICIGI', 'ICICIPRULI',
        'IDEA', 'IDFCFIRSTB', 'INDIGO', 'INDUSTOWER', 'IOC',
        'IRCTC', 'IGL', 'JINDALSTEL', 'JUBLFOOD', 'LICHSGFIN',
        'LUPIN', 'MARICO', 'MCDOWELL-N', 'MUTHOOTFIN', 'NMDC',
        'NAUKRI', 'PEL', 'PERSISTENT', 'PETRONET', 'PIDILITIND'
    ]
    return nifty_50 + nifty_next_50


def get_nifty_500() -> List[str]:
    """
    Get NIFTY 500 constituents (includes NIFTY 100).
    Returns a representative subset due to size.

    Returns:
        List of ticker symbols
    """
    # Return NIFTY 100 + additional popular stocks from NIFTY 500
    nifty_100 = get_nifty_100()
    additional_stocks = [
        'ABCAPITAL', 'ABFRL', 'APLLTD', 'APLAPOLLO', 'ALKEM',
        'ARE&M', 'AARTIIND', 'AAVAS', 'AEGISCHEM', 'AFFLE',
        'AJANTPHARM', 'APLLTD', 'ASAHIINDIA', 'ASTRAZEN', 'BAJAJCON',
        'BALKRISIND', 'BATAINDIA', 'BAYERCROP', 'BIRLACORPN', 'BLUEDART',
        'BLUESTARCO', 'BSOFT', 'BSE', 'CAMS', 'CANFINHOME',
        'CAPLIPOINT', 'CASTROLIND', 'CEATLTD', 'CENTENKA', 'CENTRALBK',
        'CHAMBLFERT', 'CHOLAHLDNG', 'COFORGE', 'CROMPTON', 'CUMMINSIND',
        'DEEPAKNTR', 'DELTACORP', 'DIXON', 'DMART', 'ECLERX',
        'EIHOTEL', 'ELGIEQUIP', 'EMAMILTD', 'ENDURANCE', 'ESCORTS',
        'EXIDEIND', 'FEDERALBNK', 'FINEORG', 'FORTIS', 'FSL',
        'GICRE', 'GILLETTE', 'GLAXO', 'GLENMARK', 'GMRINFRA',
        'GNFC', 'GODFRYPHLP', 'GODREJAGRO', 'GODREJIND', 'GODREJPROP',
        'GRANULES', 'GRAPHITE', 'GESHIP', 'GRINDWELL', 'GSFC',
        'GSPL', 'GUJALKALI', 'HAPPSTMNDS', 'HATSUN', 'HEG',
        'HIMATSEIDE', 'HONAUT', 'HUDCO', 'IBREALEST', 'IDBI',
        'IDFC', 'IFBIND', 'IIFL', 'INDHOTEL', 'INDIANB',
        'INDIACEM', 'INDIAMART', 'INDIGOPNTS', 'INFIBEAM', 'INOXLEISUR'
    ]
    return nifty_100 + additional_stocks


def load_stocks_from_file(file_path: str) -> List[str]:
    """
    Load stock tickers from a CSV or text file.

    Args:
        file_path: Path to file containing stock tickers

    Returns:
        List of ticker symbols
    """
    import csv

    tickers = []
    try:
        with open(file_path, 'r') as f:
            if file_path.endswith('.csv'):
                reader = csv.reader(f)
                # Skip header if exists
                header = next(reader, None)
                for row in reader:
                    if row:
                        tickers.append(row[0].strip().upper())
            else:
                # Text file with one ticker per line
                tickers = [line.strip().upper() for line in f if line.strip()]

        logger.info(f"Loaded {len(tickers)} tickers from {file_path}")
        return tickers
    except Exception as e:
        logger.error(f"Error loading tickers from file: {str(e)}")
        return []
