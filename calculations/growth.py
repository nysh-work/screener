"""
Growth metrics calculations.
"""
import numpy as np
from typing import Optional
from utils.helpers import safe_divide


def calculate_cagr(start_value: float, end_value: float, periods: int) -> float:
    """
    Calculate Compound Annual Growth Rate (CAGR).

    Formula: ((End Value / Start Value) ^ (1 / Periods)) - 1

    Args:
        start_value: Initial value
        end_value: Final value
        periods: Number of years

    Returns:
        CAGR as percentage
    """
    if start_value is None or start_value <= 0 or end_value is None or periods == 0:
        return np.nan

    try:
        cagr = ((end_value / start_value) ** (1 / periods) - 1) * 100
        return cagr
    except (ZeroDivisionError, ValueError):
        return np.nan


def calculate_growth_rate(old_value: float, new_value: float) -> float:
    """
    Calculate simple growth rate between two periods.

    Formula: ((New Value - Old Value) / Old Value) × 100

    Args:
        old_value: Previous period value
        new_value: Current period value

    Returns:
        Growth rate as percentage
    """
    return safe_divide(new_value - old_value, old_value, np.nan) * 100


def calculate_yoy_growth(current: float, previous: float) -> float:
    """
    Calculate Year-over-Year growth.

    Args:
        current: Current year value
        previous: Previous year value

    Returns:
        YoY growth as percentage
    """
    return calculate_growth_rate(previous, current)
