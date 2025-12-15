# New Features Added

This document outlines all the new features added to the Stock Screener application.

## 1. Fixed Growth Metrics Population ✅

### What Changed
- **Historical Financial Data Fetching**: Now fetches multi-year financial statements from yfinance
- **CAGR Calculations**: Properly calculates 3-year and 5-year CAGRs for:
  - Revenue
  - Net Profit
  - Operating Cash Flow
- **Automatic Population**: Growth metrics are automatically calculated during data updates

### New Methods
- `YFinanceFetcher.fetch_historical_financials()`: Fetches historical income statements and cash flows
- `YFinanceFetcher.calculate_growth_metrics_from_history()`: Calculates CAGR values

### Usage
```bash
# Growth metrics are automatically calculated when updating stocks
python main.py update --universe nifty50

# Growth screens now work properly with real data
python main.py screen --type growth
```

---

## 2. Expanded Stock Universe 🌍

### What Changed
- **Multiple Index Support**: Added support for NIFTY 50, NIFTY 100, and NIFTY 500
- **Custom Stock Lists**: Can load stocks from CSV or text files
- **200+ Stocks Available**: Expanded from 20 stocks to 200+ stocks across major indices

### New Functions
- `get_nifty_50()`: Returns all NIFTY 50 constituents
- `get_nifty_100()`: Returns all NIFTY 100 constituents
- `get_nifty_500()`: Returns representative NIFTY 500 stocks
- `load_stocks_from_file(path)`: Loads custom stock list from file

### Usage
```bash
# Update using different universes
python main.py update --universe nifty50
python main.py update --universe nifty100
python main.py update --universe nifty500

# Load custom stock list from file
python main.py update --from-file stocks.csv

# Limit number of stocks
python main.py update --universe nifty100 --limit 50
```

---

## 3. Technical Indicators 📈

### What Changed
- **New Technical Indicators Table**: Stores technical indicators for all stocks
- **5 Key Indicators Calculated**:
  - **EMA 20 & 50**: Exponential Moving Averages for trend identification
  - **MACD**: Moving Average Convergence Divergence with signal line and histogram
  - **Choppiness Index**: Measures market choppiness (61.8+ = choppy, 38.2- = trending)
  - **ATR (14)**: Average True Range for volatility measurement

### New Module
- `calculations/technical.py`: Complete technical indicators library
  - `calculate_ema()`: EMA calculation
  - `calculate_macd()`: MACD with signal and histogram
  - `calculate_choppiness_index()`: Choppiness indicator
  - `calculate_atr()`: Average True Range
  - `detect_macd_crossover()`: Detects bullish/bearish MACD crosses
  - `get_ema_trend()`: Determines trend based on EMA positions
  - `interpret_choppiness_index()`: Interprets CI values

### Usage
```bash
# Technical indicators are automatically calculated during updates
python main.py update --universe nifty50

# Skip historical data for faster updates (no technical indicators)
python main.py update --universe nifty50 --no-history
```

### Example: Using Technical Indicators in Custom Screens
```bash
# Create a screen with technical filters
python main.py custom create "momentum" \
  --description "Stocks with bullish momentum" \
  --criteria '{"ema_20": {"operator": ">", "value": 100}, "macd": {"operator": ">", "value": 0}, "choppiness_index": {"operator": "<", "value": 38.2}}' \
  --logic AND
```

---

## 4. Custom Screen Builder 🔧

### What Changed
- **Create Custom Screens**: Define your own screening criteria
- **Save and Reuse**: Save screens to database for repeated use
- **Flexible Criteria**: Support for 30+ metrics with custom thresholds
- **JSON-based Configuration**: Define criteria using simple JSON format

### New Module
- `screener/custom_builder.py`: Custom screen management
  - `create_screen()`: Create new custom screen
  - `update_screen()`: Update existing screen
  - `delete_screen()`: Remove custom screen
  - `list_screens()`: List all custom screens
  - `run_screen()`: Execute custom screen
  - `create_from_template()`: Create custom screen from predefined template

### Database Tables
- `custom_screens`: Stores user-defined screening criteria

### CLI Commands
```bash
# Create a custom screen
python main.py custom create "my-screen" \
  --description "High ROE with low debt" \
  --criteria '{"roe": {"operator": ">", "value": 20}, "debt_equity": {"operator": "<", "value": 0.5}}' \
  --logic AND

# List all custom screens
python main.py custom list

# Run a custom screen
python main.py custom run "my-screen" --limit 20 --output results.csv

# Delete a custom screen
python main.py custom delete "my-screen"
```

### Supported Criteria Fields
**Valuation**: price_to_book, price_to_earnings, ev_ebitda
**Profitability**: roe, roce, opm, npm
**Leverage**: debt_equity, current_ratio, interest_coverage
**Growth**: revenue_cagr_3y, revenue_cagr_5y, profit_cagr_3y, profit_cagr_5y
**Quality**: altman_z_score, promoter_holding, ocf_to_net_profit
**Technical**: ema_20, ema_50, macd, choppiness_index, atr_14
**Other**: market_cap, price

### Operators
`<`, `>`, `<=`, `>=`, `=`, `!=`

---

## 5. Portfolio Tracker 💼

### What Changed
- **Track Holdings**: Maintain a portfolio of stock holdings
- **Real-time P&L**: Calculate unrealized profit/loss
- **Portfolio Analytics**: View summary statistics
- **Purchase History**: Track purchase date, price, and quantity

### New Module
- `portfolio/tracker.py`: Portfolio management
  - `add_holding()`: Add stock to portfolio
  - `remove_holding()`: Remove holding
  - `get_portfolio()`: View all holdings
  - `update_portfolio_prices()`: Refresh current prices
  - `get_portfolio_summary()`: Get summary statistics

### Database Tables
- `portfolio`: Stores portfolio holdings

### CLI Commands
```bash
# Add a stock to portfolio
python main.py portfolio add RELIANCE --quantity 10 --price 2500 --date 2024-01-15 --notes "Long term hold"

# View portfolio
python main.py portfolio view

# Update current prices
python main.py portfolio update

# Remove a holding
python main.py portfolio remove 1  # Remove holding with ID 1
```

### Portfolio Summary
The portfolio view shows:
- Individual holdings with P&L
- Total invested amount
- Current portfolio value
- Total unrealized P&L
- Return percentage
- Best and worst performers

---

## 6. Watchlist Management 👀

### What Changed
- **Track Interesting Stocks**: Maintain a watchlist without buying
- **Target Prices**: Set target prices for each stock
- **Upside Calculation**: Automatically calculates upside to target
- **Notes**: Add notes for each watchlist stock

### Database Tables
- `watchlist`: Stores watchlist stocks

### CLI Commands
```bash
# Add to watchlist
python main.py watchlist add TCS --target 4000 --notes "Waiting for dip"

# View watchlist
python main.py watchlist view

# Remove from watchlist
python main.py watchlist remove TCS
```

---

## 7. Backtesting Engine 🔄

### What Changed
- **Test Screens Historically**: See how screens would have performed in the past
- **Return Analysis**: Calculate average, median, min, max returns
- **Performance Metrics**: Track winning/losing stocks, best/worst performers
- **Save Results**: Store backtest results for comparison

### New Module
- `backtesting/engine.py`: Backtesting framework
  - `run_backtest()`: Execute backtest for a screen
  - `get_backtest_history()`: View past backtest results
  - `compare_screens()`: Compare performance of multiple screens

### Database Tables
- `backtest_results`: Stores historical backtest results

### CLI Commands
```bash
# Run a backtest
python main.py backtest run value --screen-type predefined \
  --start-date 2024-01-01 --end-date 2024-12-01 --holding-period 90

# Run backtest on custom screen
python main.py backtest run "my-screen" --screen-type custom \
  --start-date 2024-01-01

# View backtest history
python main.py backtest history

# Filter by screen name
python main.py backtest history --screen value
```

### Backtest Metrics
- Total stocks screened
- Stocks that passed criteria
- Average return %
- Median return %
- Best performing stock
- Worst performing stock
- Number of winning/losing stocks
- Standard deviation of returns

---

## Updated CLI Structure

```
Stock Screener CLI
├── init                    # Initialize database
├── update                  # Update stock data
│   ├── --universe         # Select universe (top20, nifty50, nifty100, nifty500)
│   ├── --from-file        # Load from custom file
│   ├── --no-history       # Skip historical data (faster)
│   └── --limit            # Limit number of stocks
│
├── screen                  # Run predefined screens
│   ├── --type             # Screen type (value, growth, quality, etc.)
│   ├── --sector           # Filter by sector
│   └── --output           # Save results to file
│
├── list-screens           # List predefined screens
├── info                   # Show stock details
├── status                 # Database status
├── db                     # Database maintenance
│
├── portfolio              # Portfolio management
│   ├── add               # Add holding
│   ├── remove            # Remove holding
│   ├── view              # View portfolio
│   └── update            # Update prices
│
├── watchlist              # Watchlist management
│   ├── add               # Add to watchlist
│   ├── remove            # Remove from watchlist
│   └── view              # View watchlist
│
├── custom                 # Custom screens
│   ├── create            # Create custom screen
│   ├── list              # List custom screens
│   ├── run               # Run custom screen
│   └── delete            # Delete custom screen
│
└── backtest              # Backtesting
    ├── run               # Run backtest
    └── history           # View backtest history
```

---

## Database Schema Updates

### New Tables
1. **technical_indicators**: Stores EMA, MACD, Choppiness Index, ATR
2. **portfolio**: User portfolio holdings
3. **watchlist**: Stocks being watched
4. **custom_screens**: User-defined screening criteria
5. **backtest_results**: Historical backtest results

### Updated Tables
- **growth_metrics**: Now properly populated with historical CAGR data

---

## Example Workflows

### Workflow 1: Complete Setup and Analysis
```bash
# 1. Initialize database
python main.py init

# 2. Fetch NIFTY 50 stocks with full data
python main.py update --universe nifty50

# 3. Run a value screen
python main.py screen --type value --output value_stocks.csv

# 4. Add interesting stocks to watchlist
python main.py watchlist add RELIANCE --target 3000
python main.py watchlist add TCS --target 4000

# 5. Create a custom screen
python main.py custom create "high-quality" \
  --description "High quality stocks" \
  --criteria '{"roe": {"operator": ">", "value": 20}, "roce": {"operator": ">", "value": 20}, "debt_equity": {"operator": "<", "value": 0.5}}'

# 6. Run the custom screen
python main.py custom run "high-quality" --limit 10

# 7. Add stocks to portfolio
python main.py portfolio add RELIANCE --quantity 10 --price 2500

# 8. Backtest the screen
python main.py backtest run "high-quality" --screen-type custom --start-date 2024-01-01
```

### Workflow 2: Technical Analysis Screening
```bash
# 1. Update with technical indicators
python main.py update --universe nifty100

# 2. Create a momentum screen
python main.py custom create "momentum" \
  --description "Bullish momentum stocks" \
  --criteria '{"ema_20": {"operator": ">", "value": 100}, "macd": {"operator": ">", "value": 0}, "choppiness_index": {"operator": "<", "value": 38.2}, "roe": {"operator": ">", "value": 15}}'

# 3. Run the momentum screen
python main.py custom run "momentum" --output momentum_stocks.xlsx

# 4. Add to watchlist for monitoring
python main.py watchlist add INFY --notes "Strong momentum, watching for entry"
```

### Workflow 3: Portfolio Management
```bash
# 1. Add multiple holdings
python main.py portfolio add RELIANCE --quantity 10 --price 2500 --date 2024-01-15
python main.py portfolio add TCS --quantity 5 --price 3800 --date 2024-02-01
python main.py portfolio add INFY --quantity 20 --price 1500 --date 2024-03-10

# 2. View portfolio
python main.py portfolio view

# 3. Update prices regularly
python main.py portfolio update

# 4. Track performance over time
python main.py portfolio view
```

---

## Performance Considerations

1. **Update Speed**:
   - Use `--no-history` flag for faster updates when you don't need growth metrics or technical indicators
   - Use `--limit` to control the number of stocks fetched

2. **Rate Limiting**:
   - yfinance has rate limits. Consider adding delays between stocks if fetching large universes
   - The application handles rate limit errors gracefully

3. **Database Size**:
   - Historical data increases database size
   - Use `python main.py db --vacuum` to optimize database periodically

---

## Migration Notes

If you're upgrading from the previous version:

1. **Re-initialize Database**: Run `python main.py init` to create new tables
2. **Re-fetch Data**: Run `python main.py update` to populate growth metrics and technical indicators
3. **Existing Screens**: Predefined screens still work, but growth screens now have real data

---

## Technical Details

### Growth Metrics Calculation
- Uses yfinance's `.income_stmt` and `.cashflow` methods
- Requires at least 4 years of data for 3Y CAGR, 6 years for 5Y CAGR
- Handles missing data gracefully

### Technical Indicators
- Uses pandas for efficient calculations
- Calculated on 1 year of daily price data
- Stored with `as_of_date` for historical tracking

### Backtesting
- Simple buy-and-hold strategy
- Calculates returns based on actual historical prices
- Stores detailed results including individual stock performance

---

## Future Enhancements (Not Implemented Yet)

- Interactive visualizations (charts/graphs)
- Alert system for price targets and criteria changes
- Email/webhook notifications
- API for programmatic access
- More technical indicators (RSI, Bollinger Bands, etc.)
- Advanced backtesting (periodic rebalancing, position sizing)
- Peer comparison and sector benchmarking

---

## Support

For issues or questions:
- Check the logs in `logs/` directory
- Review database status with `python main.py status`
- Use `python main.py db --backup` before making major changes
