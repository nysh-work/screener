"""
Technical indicators calculations for stock analysis.
"""
import numpy as np
import pandas as pd
from typing import Optional, Tuple


def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).

    Args:
        prices: Series of prices
        period: Period for EMA calculation

    Returns:
        Series of EMA values
    """
    return prices.ewm(span=period, adjust=False).mean()


def calculate_macd(prices: pd.Series,
                   fast_period: int = 12,
                   slow_period: int = 26,
                   signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        prices: Series of closing prices
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line period (default: 9)

    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    ema_fast = calculate_ema(prices, fast_period)
    ema_slow = calculate_ema(prices, slow_period)

    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal_period)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_choppiness_index(high: pd.Series,
                               low: pd.Series,
                               close: pd.Series,
                               period: int = 14) -> pd.Series:
    """
    Calculate Choppiness Index.

    The Choppiness Index measures market volatility and ranges from 0 to 100.
    - Values above 61.8: Market is choppy (consolidating)
    - Values below 38.2: Market is trending

    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of closing prices
        period: Period for calculation (default: 14)

    Returns:
        Series of Choppiness Index values
    """
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Sum of True Range over period
    atr_sum = true_range.rolling(window=period).sum()

    # Highest high and lowest low over period
    highest_high = high.rolling(window=period).max()
    lowest_low = low.rolling(window=period).min()

    # Choppiness Index formula
    ci = 100 * np.log10(atr_sum / (highest_high - lowest_low)) / np.log10(period)

    return ci


def calculate_atr(high: pd.Series,
                  low: pd.Series,
                  close: pd.Series,
                  period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).

    Args:
        high: Series of high prices
        low: Series of low prices
        close: Series of closing prices
        period: Period for calculation (default: 14)

    Returns:
        Series of ATR values
    """
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Calculate ATR as EMA of True Range
    atr = true_range.ewm(span=period, adjust=False).mean()

    return atr


def detect_macd_crossover(macd_line: pd.Series,
                         signal_line: pd.Series,
                         lookback: int = 5) -> Optional[str]:
    """
    Detect MACD crossover signals.

    Args:
        macd_line: MACD line values
        signal_line: Signal line values
        lookback: Number of periods to look back for crossover (default: 5)

    Returns:
        'bullish' for bullish crossover, 'bearish' for bearish crossover, None otherwise
    """
    if len(macd_line) < lookback or len(signal_line) < lookback:
        return None

    recent_macd = macd_line.iloc[-lookback:]
    recent_signal = signal_line.iloc[-lookback:]

    # Check for bullish crossover (MACD crosses above signal)
    if recent_macd.iloc[-1] > recent_signal.iloc[-1]:
        # Check if it was below in recent past
        for i in range(1, min(lookback, len(recent_macd))):
            if recent_macd.iloc[-i-1] <= recent_signal.iloc[-i-1]:
                return 'bullish'

    # Check for bearish crossover (MACD crosses below signal)
    if recent_macd.iloc[-1] < recent_signal.iloc[-1]:
        # Check if it was above in recent past
        for i in range(1, min(lookback, len(recent_macd))):
            if recent_macd.iloc[-i-1] >= recent_signal.iloc[-i-1]:
                return 'bearish'

    return None


def get_ema_trend(price: float, ema_20: float, ema_50: float) -> dict:
    """
    Determine price trend based on EMA positions.

    Args:
        price: Current price
        ema_20: 20-period EMA
        ema_50: 50-period EMA

    Returns:
        Dictionary with trend information
    """
    trend = {
        'price_above_ema20': price > ema_20,
        'price_above_ema50': price > ema_50,
        'ema20_above_ema50': ema_20 > ema_50,
        'trend': 'unknown'
    }

    # Determine overall trend
    if price > ema_20 > ema_50:
        trend['trend'] = 'strong_uptrend'
    elif price > ema_20 and price > ema_50:
        trend['trend'] = 'uptrend'
    elif price < ema_20 < ema_50:
        trend['trend'] = 'strong_downtrend'
    elif price < ema_20 and price < ema_50:
        trend['trend'] = 'downtrend'
    else:
        trend['trend'] = 'sideways'

    return trend


def interpret_choppiness_index(ci_value: float) -> dict:
    """
    Interpret Choppiness Index value.

    Args:
        ci_value: Choppiness Index value

    Returns:
        Dictionary with interpretation
    """
    interpretation = {
        'value': ci_value,
        'state': 'unknown',
        'recommendation': ''
    }

    if ci_value >= 61.8:
        interpretation['state'] = 'choppy'
        interpretation['recommendation'] = 'Market is consolidating. Wait for breakout or avoid trading.'
    elif ci_value <= 38.2:
        interpretation['state'] = 'trending'
        interpretation['recommendation'] = 'Market is trending. Follow the trend direction.'
    else:
        interpretation['state'] = 'transitional'
        interpretation['recommendation'] = 'Market is transitioning. Watch for direction.'

    return interpretation
