# Stock Screener for Indian Equity Markets

A comprehensive Python-based stock screener for Indian stocks listed on NSE/BSE. Filter stocks based on fundamental analysis criteria with support for multiple screening strategies.

## Features

- **Multiple Screening Strategies**: Value, Growth, Balanced, Quality, and Turnaround screens
- **Comprehensive Metrics**: Valuation, Profitability, Leverage, Growth, and Quality metrics
- **Rich Terminal Output**: Beautiful console tables with color coding
- **Data Persistence**: SQLite database for storing historical data
- **Export Capabilities**: CSV and Excel reports with formatting
- **Flexible Filtering**: Sector-based filtering and custom criteria
- **Data Source**: Yahoo Finance (yfinance) for reliable data

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- Virtual environment (recommended)

### Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database**:
   ```bash
   python main.py init
   ```

## Quick Start

### 1. Fetch Stock Data

```bash
# Fetch data for top 20 NSE stocks (default)
python main.py update

# Fetch data for more stocks
python main.py update --limit 50
```

### 2. Run a Screening Strategy

```bash
# Value investing screen
python main.py screen --type value

# Growth stocks screen
python main.py screen --type growth
```

### 3. Export Results

```bash
# Export to Excel
python main.py screen --type value --output results.xlsx
```

## Available Screens

- **value**: Traditional value investing (P/B < 5, ROE > 15%, D/E < 1.5)
- **growth**: High-growth companies (Revenue CAGR > 20%, OPM > 20%)
- **balanced**: Reasonably-valued growth (P/B < 8, ROE > 12%)
- **quality**: High-quality businesses (ROE > 20%, ROCE > 20%)
- **turnaround**: Operational improvement (OPM > 20%)

## CLI Commands

```bash
# Initialize database
python main.py init

# Update stock data
python main.py update [--limit N]

# Run screen
python main.py screen --type <value|growth|balanced|quality|turnaround>

# View stock details
python main.py info RELIANCE

# Check status
python main.py status

# Database maintenance
python main.py db --vacuum
python main.py db --backup
```

## Disclaimer

**IMPORTANT**: This tool is for educational purposes only. Not investment advice. Always conduct your own research and consult with a qualified financial advisor.

---

**Happy Screening! 📊**
