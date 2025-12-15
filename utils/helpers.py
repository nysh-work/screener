"""
Helper utility functions.
"""
from typing import Any, Optional
import numpy as np


def safe_divide(numerator: float, denominator: float, default: Any = np.nan) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.

    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Value to return if division fails (default: np.nan)

    Returns:
        Result of division or default value
    """
    if denominator == 0 or denominator is None or np.isnan(denominator):
        return default
    if numerator is None or np.isnan(numerator):
        return default
    return numerator / denominator


def format_currency(value: float, decimals: int = 2) -> str:
    """
    Format a number as Indian currency (Crores).

    Args:
        value: Value in crores
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if value is None or np.isnan(value):
        return "N/A"
    return f"₹{value:,.{decimals}f} Cr"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a number as percentage.

    Args:
        value: Value (e.g., 15.5 for 15.5%)
        decimals: Number of decimal places

    Returns:
        Formatted string
    """
    if value is None or np.isnan(value):
        return "N/A"
    return f"{value:.{decimals}f}%"


def clean_numeric(value: Any) -> Optional[float]:
    """
    Clean and convert value to float, handling None and invalid values.

    Args:
        value: Value to convert

    Returns:
        Float value or None
    """
    if value is None or value == '' or (isinstance(value, float) and np.isnan(value)):
        return None

    try:
        return float(value)
    except (ValueError, TypeError):
        return None
