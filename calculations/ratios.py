"""
Financial ratio calculations.
"""
import numpy as np
from typing import Optional
from utils.helpers import safe_divide


def calculate_roe(net_profit: float, equity: float) -> float:
    """
    Calculate Return on Equity (ROE).

    Formula: (Net Profit / Shareholders' Equity) × 100

    Args:
        net_profit: Net profit after tax
        equity: Total shareholders' equity

    Returns:
        ROE as percentage
    """
    return safe_divide(net_profit, equity, np.nan) * 100


def calculate_roce(ebit: float, capital_employed: float) -> float:
    """
    Calculate Return on Capital Employed (ROCE).

    Formula: (EBIT / Capital Employed) × 100
    where Capital Employed = Total Assets - Current Liabilities

    Args:
        ebit: Earnings before interest and tax
        capital_employed: Total assets minus current liabilities

    Returns:
        ROCE as percentage
    """
    return safe_divide(ebit, capital_employed, np.nan) * 100


def calculate_debt_equity(total_debt: float, equity: float) -> float:
    """
    Calculate Debt-to-Equity ratio.

    Formula: Total Debt / Shareholders' Equity

    Args:
        total_debt: Total debt
        equity: Shareholders' equity

    Returns:
        Debt-to-Equity ratio
    """
    return safe_divide(total_debt, equity, np.nan)


def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
    """
    Calculate Current Ratio.

    Formula: Current Assets / Current Liabilities

    Args:
        current_assets: Total current assets
        current_liabilities: Total current liabilities

    Returns:
        Current ratio
    """
    return safe_divide(current_assets, current_liabilities, np.nan)


def calculate_interest_coverage(ebit: float, interest_expense: float) -> float:
    """
    Calculate Interest Coverage ratio.

    Formula: EBIT / Interest Expense

    Args:
        ebit: Earnings before interest and tax
        interest_expense: Interest expense

    Returns:
        Interest coverage ratio
    """
    if interest_expense == 0 or interest_expense is None:
        return np.inf if ebit and ebit > 0 else np.nan
    return safe_divide(ebit, interest_expense, np.nan)


def calculate_price_to_book(price: float, book_value: float) -> float:
    """
    Calculate Price-to-Book ratio.

    Formula: Market Price / Book Value per Share

    Args:
        price: Current market price
        book_value: Book value per share

    Returns:
        P/B ratio
    """
    return safe_divide(price, book_value, np.nan)


def calculate_price_to_earnings(price: float, eps: float) -> float:
    """
    Calculate Price-to-Earnings ratio.

    Formula: Market Price / Earnings per Share

    Args:
        price: Current market price
        eps: Earnings per share

    Returns:
        P/E ratio
    """
    return safe_divide(price, eps, np.nan)


def calculate_ev_ebitda(enterprise_value: float, ebitda: float) -> float:
    """
    Calculate EV/EBITDA ratio.

    Formula: Enterprise Value / EBITDA

    Args:
        enterprise_value: Enterprise value
        ebitda: EBITDA

    Returns:
        EV/EBITDA ratio
    """
    return safe_divide(enterprise_value, ebitda, np.nan)


def calculate_opm(operating_profit: float, revenue: float) -> float:
    """
    Calculate Operating Profit Margin.

    Formula: (Operating Profit / Revenue) × 100

    Args:
        operating_profit: Operating profit
        revenue: Total revenue

    Returns:
        OPM as percentage
    """
    return safe_divide(operating_profit, revenue, np.nan) * 100


def calculate_npm(net_profit: float, revenue: float) -> float:
    """
    Calculate Net Profit Margin.

    Formula: (Net Profit / Revenue) × 100

    Args:
        net_profit: Net profit
        revenue: Total revenue

    Returns:
        NPM as percentage
    """
    return safe_divide(net_profit, revenue, np.nan) * 100


def calculate_asset_turnover(revenue: float, total_assets: float) -> float:
    """
    Calculate Asset Turnover ratio.

    Formula: Revenue / Total Assets

    Args:
        revenue: Total revenue
        total_assets: Total assets

    Returns:
        Asset turnover ratio
    """
    return safe_divide(revenue, total_assets, np.nan)


def calculate_altman_z_score(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_value_equity: float,
    sales: float,
    total_assets: float,
    total_liabilities: float
) -> float:
    """
    Calculate Altman Z-Score for bankruptcy prediction.

    Formula:
    Z = 1.2×(WC/TA) + 1.4×(RE/TA) + 3.3×(EBIT/TA) + 0.6×(MVE/TL) + 1.0×(Sales/TA)

    Interpretation:
    - Z > 2.99: Safe zone (low bankruptcy risk)
    - 1.81 < Z < 2.99: Grey zone
    - Z < 1.81: Distress zone (high bankruptcy risk)

    Args:
        working_capital: Current Assets - Current Liabilities
        retained_earnings: Cumulative retained earnings
        ebit: Earnings before interest and tax
        market_value_equity: Market capitalization
        sales: Total revenue
        total_assets: Total assets
        total_liabilities: Total liabilities

    Returns:
        Altman Z-Score
    """
    if total_assets == 0 or total_assets is None or total_liabilities == 0 or total_liabilities is None:
        return np.nan

    z = (
        1.2 * safe_divide(working_capital, total_assets, 0) +
        1.4 * safe_divide(retained_earnings, total_assets, 0) +
        3.3 * safe_divide(ebit, total_assets, 0) +
        0.6 * safe_divide(market_value_equity, total_liabilities, 0) +
        1.0 * safe_divide(sales, total_assets, 0)
    )

    return z
