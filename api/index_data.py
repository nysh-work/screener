"""
Index data service for fetching Nifty index information.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import yfinance as yf
import pandas as pd
from calculations.technical import calculate_ema, calculate_macd, calculate_choppiness_index
from utils.logger import get_logger

logger = get_logger(__name__)

# Nifty index symbols mapping
NIFTY_INDICES = {
    'nifty_50': '^NSEI',      # NIFTY 50
    'nifty_midcap': '^NSEMDCP50', # NIFTY Midcap
    'nifty_bank': '^NSEBANK',  # NIFTY Bank
    'nifty_it': '^CNXIT',     # NIFTY IT
    'nifty_auto': '^CNXAUTO'  # NIFTY Auto
}

class IndexDataService:
    """Service for fetching and calculating index data."""
    
    def __init__(self):
        self.cache = {}
        self.cache_timeout = 300  # 5 minutes
    
    def get_index_data(self, index_key: str) -> Optional[Dict]:
        """
        Get current index data with technical indicators.
        
        Args:
            index_key: One of 'nifty_50', 'nifty_midcap', 'nifty_bank', 'nifty_it', 'nifty_auto'
            
        Returns:
            Dictionary with index data or None if failed
        """
        if index_key not in NIFTY_INDICES:
            logger.error(f"Invalid index key: {index_key}")
            return None
        
        # Check cache first
        cache_key = f"index_{index_key}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_timeout):
                logger.info(f"Returning cached data for {index_key}")
                return cached_data
        
        try:
            symbol = NIFTY_INDICES[index_key]
            
            # Fetch 30 days of data for calculations
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            # Download data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(start=start_date, end=end_date)
            
            if hist_data.empty:
                logger.error(f"No data found for {symbol}")
                return None
            
            # Get current price (last close)
            current_price = float(hist_data['Close'].iloc[-1])
            
            # Calculate 14-day high and low
            recent_data = hist_data.tail(14)
            high_14d = float(recent_data['High'].max())
            low_14d = float(recent_data['Low'].min())
            
            # Calculate EMAs
            closes = hist_data['Close']
            ema_20 = calculate_ema(closes, 20)
            ema_50 = calculate_ema(closes, 50)
            
            # Calculate MACD
            macd_line, signal_line, histogram = calculate_macd(closes)
            current_macd = float(macd_line.iloc[-1]) if len(macd_line) > 0 else 0
            
            # Calculate Choppiness Index
            choppiness_series = calculate_choppiness_index(
                recent_data['High'],
                recent_data['Low'],
                recent_data['Close'],
                period=14
            )
            choppiness = float(choppiness_series.iloc[-1]) if len(choppiness_series) > 0 and not pd.isna(choppiness_series.iloc[-1]) else 0
            
            # Get index name
            index_names = {
                'nifty_50': 'NIFTY 50',
                'nifty_midcap': 'NIFTY Midcap',
                'nifty_bank': 'NIFTY Bank',
                'nifty_it': 'NIFTY IT',
                'nifty_auto': 'NIFTY Auto'
            }
            
            result = {
                'index_name': index_names.get(index_key, index_key),
                'symbol': symbol,
                'current_price': round(current_price, 2),
                'high_14d': round(high_14d, 2),
                'low_14d': round(low_14d, 2),
                'ema_20': round(float(ema_20.iloc[-1]), 2) if len(ema_20) > 0 and not pd.isna(ema_20.iloc[-1]) else round(current_price, 2),
                'ema_50': round(float(ema_50.iloc[-1]), 2) if len(ema_50) > 0 and not pd.isna(ema_50.iloc[-1]) else round(current_price, 2),
                'macd': round(current_macd, 2),
                'choppiness_index': round(float(choppiness), 2) if choppiness is not None and not pd.isna(choppiness) else 0,
                'last_updated': datetime.now().isoformat()
            }
            
            # Cache the result
            self.cache[cache_key] = (result, datetime.now())
            
            logger.info(f"Successfully fetched data for {index_key}: {current_price}")
            return result
            
        except Exception as e:
            logger.error(f"Error fetching data for {index_key}: {str(e)}")
            return None
    
    def get_all_indices_data(self) -> Dict[str, Dict]:
        """
        Get data for all Nifty indices.
        
        Returns:
            Dictionary with all index data
        """
        results = {}
        
        for index_key in NIFTY_INDICES.keys():
            index_data = self.get_index_data(index_key)
            if index_data:
                results[index_key] = index_data
            else:
                # Provide fallback data if fetch fails
                results[index_key] = {
                    'index_name': index_key.replace('_', ' ').title(),
                    'symbol': NIFTY_INDICES[index_key],
                    'current_price': 0,
                    'high_14d': 0,
                    'low_14d': 0,
                    'ema_20': 0,
                    'ema_50': 0,
                    'macd': 0,
                    'choppiness_index': 0,
                    'last_updated': datetime.now().isoformat(),
                    'error': 'Failed to fetch data'
                }
        
        return results
    
    def refresh_cache(self):
        """Refresh all cached index data."""
        logger.info("Refreshing index data cache")
        for index_key in NIFTY_INDICES.keys():
            self.get_index_data(index_key)  # This will update cache
