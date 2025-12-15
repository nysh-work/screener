"""
Add sample stock data for testing the screener.
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import Database


def add_sample_data():
    """Add sample stock data to the database."""
    db = Database()

    # Sample companies with realistic Indian stock data
    samples = [
        {
            'company': {
                'ticker': 'RELIANCE',
                'company_name': 'Reliance Industries Ltd',
                'sector': 'Oil & Gas',
                'industry': 'Petroleum Products',
                'market_cap': 1750000.0,
                'exchange': 'NSE'
            },
            'fundamentals': {
                'ticker': 'RELIANCE',
                'as_of_date': date.today(),
                'price': 2450.0,
                'book_value': 1180.0,
                'market_cap': 1750000.0,
                'enterprise_value': 1850000.0,
                'ebitda': 85000.0,
                'net_profit': 68000.0,
                'total_assets': 1200000.0,
                'total_equity': 750000.0,
                'total_debt': 300000.0,
                'current_assets': 350000.0,
                'current_liabilities': 280000.0,
                'revenue': 920000.0,
                'operating_profit': 110000.0,
                'interest_expense': 15000.0,
                'cash_flow_operations': 95000.0
            },
            'derived_metrics': {
                'ticker': 'RELIANCE',
                'as_of_date': date.today(),
                'price_to_book': 2.08,
                'price_to_earnings': 25.7,
                'ev_ebitda': 21.8,
                'roe': 18.2,
                'roce': 19.5,
                'debt_equity': 0.4,
                'current_ratio': 1.25,
                'interest_coverage': 7.3,
                'opm': 12.0,
                'npm': 7.4
            },
            'growth_metrics': {
                'ticker': 'RELIANCE',
                'as_of_date': date.today(),
                'revenue_cagr_3y': 8.5,
                'profit_cagr_3y': 12.3
            },
            'quality_metrics': {
                'ticker': 'RELIANCE',
                'as_of_date': date.today(),
                'promoter_holding': 50.4,
                'altman_z_score': 3.2,
                'ocf_to_net_profit': 1.4
            }
        },
        {
            'company': {
                'ticker': 'TCS',
                'company_name': 'Tata Consultancy Services Ltd',
                'sector': 'Information Technology',
                'industry': 'IT Services',
                'market_cap': 1450000.0,
                'exchange': 'NSE'
            },
            'fundamentals': {
                'ticker': 'TCS',
                'as_of_date': date.today(),
                'price': 3950.0,
                'book_value': 820.0,
                'market_cap': 1450000.0,
                'enterprise_value': 1380000.0,
                'ebitda': 58000.0,
                'net_profit': 45000.0,
                'total_assets': 380000.0,
                'total_equity': 300000.0,
                'total_debt': 5000.0,
                'current_assets': 280000.0,
                'current_liabilities': 150000.0,
                'revenue': 230000.0,
                'operating_profit': 62000.0,
                'interest_expense': 500.0,
                'cash_flow_operations': 52000.0
            },
            'derived_metrics': {
                'ticker': 'TCS',
                'as_of_date': date.today(),
                'price_to_book': 4.82,
                'price_to_earnings': 32.2,
                'ev_ebitda': 23.8,
                'roe': 42.1,
                'roce': 45.3,
                'debt_equity': 0.02,
                'current_ratio': 1.87,
                'interest_coverage': 124.0,
                'opm': 27.0,
                'npm': 19.6
            },
            'growth_metrics': {
                'ticker': 'TCS',
                'as_of_date': date.today(),
                'revenue_cagr_3y': 11.5,
                'profit_cagr_3y': 9.8
            },
            'quality_metrics': {
                'ticker': 'TCS',
                'as_of_date': date.today(),
                'promoter_holding': 72.0,
                'altman_z_score': 8.5,
                'ocf_to_net_profit': 1.16
            }
        },
        {
            'company': {
                'ticker': 'HDFCBANK',
                'company_name': 'HDFC Bank Ltd',
                'sector': 'Banking',
                'industry': 'Private Sector Bank',
                'market_cap': 1280000.0,
                'exchange': 'NSE'
            },
            'fundamentals': {
                'ticker': 'HDFCBANK',
                'as_of_date': date.today(),
                'price': 1680.0,
                'book_value': 520.0,
                'market_cap': 1280000.0,
                'enterprise_value': 1300000.0,
                'ebitda': 95000.0,
                'net_profit': 48000.0,
                'total_assets': 2500000.0,
                'total_equity': 380000.0,
                'total_debt': 1800000.0,
                'current_assets': 850000.0,
                'current_liabilities': 750000.0,
                'revenue': 185000.0,
                'operating_profit': 75000.0,
                'interest_expense': 28000.0,
                'cash_flow_operations': 55000.0
            },
            'derived_metrics': {
                'ticker': 'HDFCBANK',
                'as_of_date': date.today(),
                'price_to_book': 3.23,
                'price_to_earnings': 26.7,
                'ev_ebitda': 13.7,
                'roe': 16.5,
                'roce': 5.2,
                'debt_equity': 4.74,
                'current_ratio': 1.13,
                'interest_coverage': 2.68,
                'opm': 40.5,
                'npm': 25.9
            },
            'growth_metrics': {
                'ticker': 'HDFCBANK',
                'as_of_date': date.today(),
                'revenue_cagr_3y': 15.2,
                'profit_cagr_3y': 18.5
            },
            'quality_metrics': {
                'ticker': 'HDFCBANK',
                'as_of_date': date.today(),
                'promoter_holding': 26.0,
                'altman_z_score': 2.1,
                'ocf_to_net_profit': 1.15
            }
        },
        {
            'company': {
                'ticker': 'INFY',
                'company_name': 'Infosys Ltd',
                'sector': 'Information Technology',
                'industry': 'IT Services',
                'market_cap': 720000.0,
                'exchange': 'NSE'
            },
            'fundamentals': {
                'ticker': 'INFY',
                'as_of_date': date.today(),
                'price': 1750.0,
                'book_value': 380.0,
                'market_cap': 720000.0,
                'enterprise_value': 680000.0,
                'ebitda': 38000.0,
                'net_profit': 28000.0,
                'total_assets': 185000.0,
                'total_equity': 155000.0,
                'total_debt': 2000.0,
                'current_assets': 125000.0,
                'current_liabilities': 65000.0,
                'revenue': 145000.0,
                'operating_profit': 41000.0,
                'interest_expense': 300.0,
                'cash_flow_operations': 32000.0
            },
            'derived_metrics': {
                'ticker': 'INFY',
                'as_of_date': date.today(),
                'price_to_book': 4.61,
                'price_to_earnings': 25.7,
                'ev_ebitda': 17.9,
                'roe': 30.5,
                'roce': 35.2,
                'debt_equity': 0.01,
                'current_ratio': 1.92,
                'interest_coverage': 136.7,
                'opm': 28.3,
                'npm': 19.3
            },
            'growth_metrics': {
                'ticker': 'INFY',
                'as_of_date': date.today(),
                'revenue_cagr_3y': 9.8,
                'profit_cagr_3y': 7.5
            },
            'quality_metrics': {
                'ticker': 'INFY',
                'as_of_date': date.today(),
                'promoter_holding': 13.0,
                'altman_z_score': 7.8,
                'ocf_to_net_profit': 1.14
            }
        },
        {
            'company': {
                'ticker': 'TITAN',
                'company_name': 'Titan Company Ltd',
                'sector': 'Consumer Discretionary',
                'industry': 'Jewellery',
                'market_cap': 320000.0,
                'exchange': 'NSE'
            },
            'fundamentals': {
                'ticker': 'TITAN',
                'as_of_date': date.today(),
                'price': 3600.0,
                'book_value': 450.0,
                'market_cap': 320000.0,
                'enterprise_value': 325000.0,
                'ebitda': 32000.0,
                'net_profit': 28500.0,
                'total_assets': 95000.0,
                'total_equity': 52000.0,
                'total_debt': 8000.0,
                'current_assets': 72000.0,
                'current_liabilities': 35000.0,
                'revenue': 425000.0,
                'operating_profit': 35000.0,
                'interest_expense': 600.0,
                'cash_flow_operations': 31000.0
            },
            'derived_metrics': {
                'ticker': 'TITAN',
                'as_of_date': date.today(),
                'price_to_book': 8.0,
                'price_to_earnings': 85.0,
                'ev_ebitda': 10.2,
                'roe': 35.8,
                'roce': 38.5,
                'debt_equity': 0.15,
                'current_ratio': 2.06,
                'interest_coverage': 58.3,
                'opm': 8.2,
                'npm': 6.7
            },
            'growth_metrics': {
                'ticker': 'TITAN',
                'as_of_date': date.today(),
                'revenue_cagr_3y': 22.5,
                'profit_cagr_3y': 28.3
            },
            'quality_metrics': {
                'ticker': 'TITAN',
                'as_of_date': date.today(),
                'promoter_holding': 52.9,
                'altman_z_score': 5.2,
                'ocf_to_net_profit': 1.09
            }
        },
        {
            'company': {
                'ticker': 'ASIANPAINT',
                'company_name': 'Asian Paints Ltd',
                'sector': 'Consumer Discretionary',
                'industry': 'Paints',
                'market_cap': 285000.0,
                'exchange': 'NSE'
            },
            'fundamentals': {
                'ticker': 'ASIANPAINT',
                'as_of_date': date.today(),
                'price': 2970.0,
                'book_value': 120.0,
                'market_cap': 285000.0,
                'enterprise_value': 275000.0,
                'ebitda': 48000.0,
                'net_profit': 35000.0,
                'total_assets': 85000.0,
                'total_equity': 62000.0,
                'total_debt': 1500.0,
                'current_assets': 58000.0,
                'current_liabilities': 28000.0,
                'revenue': 320000.0,
                'operating_profit': 51000.0,
                'interest_expense': 200.0,
                'cash_flow_operations': 42000.0
            },
            'derived_metrics': {
                'ticker': 'ASIANPAINT',
                'as_of_date': date.today(),
                'price_to_book': 24.8,
                'price_to_earnings': 65.0,
                'ev_ebitda': 5.7,
                'roe': 28.5,
                'roce': 45.2,
                'debt_equity': 0.02,
                'current_ratio': 2.07,
                'interest_coverage': 255.0,
                'opm': 15.9,
                'npm': 10.9
            },
            'growth_metrics': {
                'ticker': 'ASIANPAINT',
                'as_of_date': date.today(),
                'revenue_cagr_3y': 5.8,
                'profit_cagr_3y': 3.2
            },
            'quality_metrics': {
                'ticker': 'ASIANPAINT',
                'as_of_date': date.today(),
                'promoter_holding': 52.7,
                'altman_z_score': 9.5,
                'ocf_to_net_profit': 1.2
            }
        }
    ]

    print("Adding sample stock data...")

    for stock in samples:
        try:
            db.add_company(stock['company'])
            db.add_fundamentals(stock['fundamentals'])
            db.add_derived_metrics(stock['derived_metrics'])
            db.add_growth_metrics(stock['growth_metrics'])
            db.add_quality_metrics(stock['quality_metrics'])
            print(f"  ✓ Added {stock['company']['ticker']} - {stock['company']['company_name']}")
        except Exception as e:
            print(f"  ✗ Error adding {stock['company']['ticker']}: {str(e)}")

    # Log operation
    db.log_operation(
        operation='sample_data_load',
        details=f"Loaded {len(samples)} sample stocks",
        status='success'
    )

    print(f"\n✓ Successfully added {len(samples)} sample stocks to the database!")
    print("\nYou can now run: python main.py screen --type value")


if __name__ == '__main__':
    add_sample_data()
