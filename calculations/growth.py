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

    Handles negative values (e.g., negative cash flows):
    - If both values are positive: standard CAGR
    - If both values are negative: CAGR based on absolute values (becoming less negative is positive growth)
    - If values cross zero: use average annual growth rate instead
    - If start_value is zero: return NaN

    Args:
        start_value: Initial value
        end_value: Final value
        periods: Number of years

    Returns:
        CAGR as percentage
    """
    if start_value is None or end_value is None or periods == 0:
        return np.nan

    # Handle zero start value
    if start_value == 0:
        return np.nan

    try:
        # Case 1: Both positive - standard CAGR
        if start_value > 0 and end_value > 0:
            cagr = ((end_value / start_value) ** (1 / periods) - 1) * 100
            return cagr

        # Case 2: Both negative - use absolute values
        # Becoming less negative (moving towards zero) is positive growth
        elif start_value < 0 and end_value < 0:
            # Use absolute values for calculation
            abs_start = abs(start_value)
            abs_end = abs(end_value)
            # If becoming less negative (abs_end < abs_start), this will be negative CAGR
            # We flip the sign to make it positive growth
            cagr = ((abs_end / abs_start) ** (1 / periods) - 1) * 100
            # Flip sign: reducing negativity is good
            return -cagr

        # Case 3: Values cross zero - use average annual growth rate
        # This avoids complex numbers from raising negative ratio to fractional power
        else:
            # Average annual growth rate = (end - start) / (periods * |start|)
            avg_growth = ((end_value - start_value) / (periods * abs(start_value))) * 100
            return avg_growth

    except (ZeroDivisionError, ValueError, TypeError):
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
