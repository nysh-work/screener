#!/usr/bin/env python3
"""
Stock Screener CLI - Main entry point.
"""
import click
from datetime import datetime, date
from data.database import Database
from data.fetcher import (
    YFinanceFetcher, get_nse_top_stocks, get_nifty_50,
    get_nifty_100, get_nifty_500, load_stocks_from_file
)
from screener.engine import ScreeningEngine
from screener.criteria import list_available_screens
from screener.custom_builder import CustomScreenBuilder
from portfolio.tracker import PortfolioTracker
from backtesting.engine import BacktestEngine
from reports.console import (
    display_screen_results, print_error, print_success,
    print_info, print_warning, display_sector_analysis
)
from utils.logger import get_logger

logger = get_logger(__name__)


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Stock Screener for Indian Equity Markets (NSE/BSE)

    A comprehensive tool for screening stocks based on fundamental analysis.
    """
    pass


@cli.command()
@click.option('--full', is_flag=True, help='Full data refresh (fetch all data)')
@click.option('--incremental', is_flag=True, help='Incremental update (default)')
@click.option('--tickers', '-t', multiple=True, help='Specific tickers to update')
@click.option('--limit', '-l', type=int, default=20, help='Limit number of stocks to fetch')
@click.option('--universe', '-u', type=click.Choice(['top20', 'nifty50', 'nifty100', 'nifty500']),
              default='top20', help='Stock universe to fetch')
@click.option('--from-file', type=click.Path(exists=True), help='Load tickers from file')
@click.option('--no-history', is_flag=True, help='Skip historical data (faster)')
def update(full, incremental, tickers, limit, universe, from_file, no_history):
    """Update stock data from yfinance."""
    print_info("Starting data update...")

    db = Database()
    fetcher = YFinanceFetcher()

    # Determine which tickers to fetch
    if tickers:
        ticker_list = list(tickers)
        print_info(f"Fetching data for {len(ticker_list)} specified tickers")
    elif from_file:
        ticker_list = load_stocks_from_file(from_file)
        if not ticker_list:
            print_error("No tickers loaded from file")
            return
        print_info(f"Loaded {len(ticker_list)} tickers from file")
    else:
        # Select universe
        if universe == 'nifty50':
            ticker_list = get_nifty_50()[:limit] if limit else get_nifty_50()
        elif universe == 'nifty100':
            ticker_list = get_nifty_100()[:limit] if limit else get_nifty_100()
        elif universe == 'nifty500':
            ticker_list = get_nifty_500()[:limit] if limit else get_nifty_500()
        else:
            ticker_list = get_nse_top_stocks()[:limit]

        print_info(f"Fetching data for {len(ticker_list)} stocks from {universe}")

    success_count = 0
    error_count = 0
    include_history = not no_history

    with click.progressbar(ticker_list, label='Fetching stock data') as bar:
        for ticker in bar:
            try:
                # Fetch all data for the ticker
                data = fetcher.fetch_all_data(ticker, include_history=include_history)

                if data:
                    # Save to database
                    db.add_company(data['company'])
                    db.add_fundamentals(data['fundamentals'])
                    db.add_derived_metrics(data['derived_metrics'])
                    db.add_growth_metrics(data['growth_metrics'])
                    db.add_quality_metrics(data['quality_metrics'])

                    # Save technical indicators if available
                    if 'technical_indicators' in data:
                        db.add_technical_indicators(data['technical_indicators'])

                    success_count += 1
                else:
                    error_count += 1
                    logger.warning(f"No data found for {ticker}")

            except Exception as e:
                error_count += 1
                logger.error(f"Error processing {ticker}: {str(e)}")

    # Log operation
    db.log_operation(
        operation='data_update',
        details=f"Updated {success_count} stocks, {error_count} errors",
        status='success' if error_count == 0 else 'partial'
    )

    print_success(f"Data update complete: {success_count} succeeded, {error_count} failed")


@cli.command()
@click.option('--type', '-t', 'screen_type', required=True,
              type=click.Choice(['value', 'growth', 'balanced', 'quality', 'turnaround']),
              help='Type of predefined screen to run')
@click.option('--sector', '-s', multiple=True, help='Filter by sector')
@click.option('--min-market-cap', type=float, help='Minimum market cap in Crores')
@click.option('--limit', '-l', type=int, default=50, help='Maximum results to display')
@click.option('--output', '-o', help='Save results to file (csv/excel)')
def screen(screen_type, sector, min_market_cap, limit, output):
    """Run a predefined screening strategy."""
    print_info(f"Running {screen_type} screen...")

    db = Database()
    engine = ScreeningEngine(db)

    # Prepare additional filters
    additional_filters = {}
    if sector:
        additional_filters['sector'] = list(sector)
    if min_market_cap:
        additional_filters['min_market_cap'] = min_market_cap

    try:
        # Run screen
        results = engine.run_predefined_screen(screen_type, additional_filters)

        # Get statistics
        stats = engine.get_screen_statistics(results)

        # Get screen config for display
        from screener.criteria import get_screen_config
        screen_config = get_screen_config(screen_type)

        # Display results
        display_screen_results(
            results=results,
            screen_name=screen_config['name'],
            screen_description=screen_config['description'],
            criteria=screen_config['criteria'],
            stats=stats,
            limit=limit
        )

        # Show sector distribution
        if stats['sectors']:
            display_sector_analysis(stats['sectors'])

        # Save to file if requested
        if output:
            if output.endswith('.csv'):
                results.to_csv(output, index=False)
                print_success(f"Results saved to {output}")
            elif output.endswith('.xlsx'):
                results.to_excel(output, index=False, engine='openpyxl')
                print_success(f"Results saved to {output}")
            else:
                print_error("Output format not supported. Use .csv or .xlsx")

    except Exception as e:
        print_error(f"Error running screen: {str(e)}")
        logger.error(f"Screen error: {str(e)}", exc_info=True)


@cli.command('list-screens')
def list_screens():
    """List all available predefined screens."""
    print_info("Available Screening Strategies:\n")

    screens = list_available_screens()

    for key, name, description in screens:
        click.echo(f"  [bold cyan]{key}[/bold cyan]")
        click.echo(f"    Name: {name}")
        click.echo(f"    Description: {description}")
        click.echo()


@cli.command()
@click.argument('ticker')
def info(ticker):
    """Show detailed information for a specific stock."""
    print_info(f"Fetching information for {ticker}...")

    db = Database()

    try:
        stock_data = db.get_latest_metrics(ticker.upper())

        if stock_data:
            from reports.console import display_stock_detail
            display_stock_detail(stock_data)
        else:
            print_warning(f"No data found for {ticker}. Try running 'update' first.")

    except Exception as e:
        print_error(f"Error fetching stock info: {str(e)}")


@cli.command()
def status():
    """Check database status and data freshness."""
    print_info("Database Status:\n")

    db = Database()

    try:
        tickers = db.get_all_tickers()
        click.echo(f"  Total stocks in database: {len(tickers)}")

        # Get latest update time from audit log
        query = """
        SELECT timestamp, details
        FROM audit_log
        WHERE operation = 'data_update'
        ORDER BY timestamp DESC
        LIMIT 1
        """
        results = db.execute_query(query)

        if results:
            last_update = results[0]['timestamp']
            click.echo(f"  Last update: {last_update}")
            click.echo(f"  Details: {results[0]['details']}")
        else:
            print_warning("  No update history found")

        print_success("Database is operational")

    except Exception as e:
        print_error(f"Error checking status: {str(e)}")


@cli.command()
@click.option('--vacuum', is_flag=True, help='Optimize database')
@click.option('--backup', is_flag=True, help='Create database backup')
def db(vacuum, backup):
    """Database maintenance operations."""
    database = Database()

    if vacuum:
        print_info("Vacuuming database...")
        database.vacuum()
        print_success("Database optimized")

    if backup:
        print_info("Creating backup...")
        database.backup()
        print_success("Backup created")


@cli.command()
def init():
    """Initialize the database (first-time setup)."""
    print_info("Initializing database...")

    try:
        db = Database()
        db.create_tables()
        print_success("Database initialized successfully!")
        print_info("\nNext steps:")
        click.echo("  1. Run 'python main.py update' to fetch stock data")
        click.echo("  2. Run 'python main.py screen --type value' to run a screen")

    except Exception as e:
        print_error(f"Error initializing database: {str(e)}")


# Portfolio Management Commands
@cli.group()
def portfolio():
    """Manage your stock portfolio."""
    pass


@portfolio.command('add')
@click.argument('ticker')
@click.option('--quantity', '-q', type=float, required=True, help='Number of shares')
@click.option('--price', '-p', type=float, required=True, help='Purchase price per share')
@click.option('--date', '-d', 'date_str', help='Purchase date (YYYY-MM-DD)')
@click.option('--notes', '-n', help='Optional notes')
def portfolio_add(ticker, quantity, price, date_str, notes):
    """Add a stock to your portfolio."""
    try:
        tracker = PortfolioTracker()
        purchase_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()

        if tracker.add_holding(ticker, quantity, price, purchase_date, notes):
            print_success(f"Added {quantity} shares of {ticker} at ₹{price} to portfolio")
        else:
            print_error("Failed to add to portfolio")

    except Exception as e:
        print_error(f"Error adding to portfolio: {str(e)}")


@portfolio.command('remove')
@click.argument('portfolio_id', type=int)
def portfolio_remove(portfolio_id):
    """Remove a holding from portfolio."""
    try:
        tracker = PortfolioTracker()
        if tracker.remove_holding(portfolio_id):
            print_success(f"Removed holding ID {portfolio_id} from portfolio")
        else:
            print_error("Failed to remove from portfolio")
    except Exception as e:
        print_error(f"Error removing from portfolio: {str(e)}")


@portfolio.command('view')
def portfolio_view():
    """View portfolio holdings."""
    try:
        tracker = PortfolioTracker()
        holdings = tracker.get_portfolio()

        if holdings.empty:
            print_warning("Portfolio is empty")
            return

        click.echo("\n📊 Portfolio Holdings:\n")
        for _, row in holdings.iterrows():
            click.echo(f"  ID: {row['id']} | {row['ticker']} - {row['company_name']}")
            click.echo(f"    Quantity: {row['quantity']} shares @ ₹{row['purchase_price']:.2f}")
            click.echo(f"    Current: ₹{row['current_price']:.2f}")
            click.echo(f"    P&L: ₹{row['unrealized_pnl']:.2f} ({row['return_pct']:.2f}%)")
            click.echo()

        # Show summary
        summary = tracker.get_portfolio_summary()
        click.echo(f"\n💰 Portfolio Summary:")
        click.echo(f"  Total Holdings: {summary['total_holdings']}")
        click.echo(f"  Invested: ₹{summary['total_invested']:.2f}")
        click.echo(f"  Current Value: ₹{summary['current_value']:.2f}")
        click.echo(f"  Total P&L: ₹{summary['total_pnl']:.2f} ({summary['total_return_pct']:.2f}%)")

    except Exception as e:
        print_error(f"Error viewing portfolio: {str(e)}")


@portfolio.command('update')
def portfolio_update():
    """Update current prices for all holdings."""
    try:
        tracker = PortfolioTracker()
        count = tracker.update_portfolio_prices()
        print_success(f"Updated prices for {count} holdings")
    except Exception as e:
        print_error(f"Error updating portfolio: {str(e)}")


# Watchlist Commands
@cli.group()
def watchlist():
    """Manage your stock watchlist."""
    pass


@watchlist.command('add')
@click.argument('ticker')
@click.option('--target', '-t', type=float, help='Target price')
@click.option('--notes', '-n', help='Optional notes')
def watchlist_add(ticker, target, notes):
    """Add a stock to watchlist."""
    try:
        tracker = PortfolioTracker()
        if tracker.add_to_watchlist(ticker, target, notes):
            print_success(f"Added {ticker} to watchlist")
        else:
            print_error("Failed to add to watchlist")
    except Exception as e:
        print_error(f"Error adding to watchlist: {str(e)}")


@watchlist.command('remove')
@click.argument('ticker')
def watchlist_remove(ticker):
    """Remove a stock from watchlist."""
    try:
        tracker = PortfolioTracker()
        if tracker.remove_from_watchlist(ticker):
            print_success(f"Removed {ticker} from watchlist")
        else:
            print_error("Failed to remove from watchlist")
    except Exception as e:
        print_error(f"Error removing from watchlist: {str(e)}")


@watchlist.command('view')
def watchlist_view():
    """View watchlist stocks."""
    try:
        tracker = PortfolioTracker()
        stocks = tracker.get_watchlist()

        if stocks.empty:
            print_warning("Watchlist is empty")
            return

        click.echo("\n👀 Watchlist:\n")
        for _, row in stocks.iterrows():
            click.echo(f"  {row['ticker']} - {row['company_name']} ({row['sector']})")
            click.echo(f"    Current: ₹{row['current_price']:.2f}")
            if row['target_price']:
                click.echo(f"    Target: ₹{row['target_price']:.2f} ({row['upside_pct']:.2f}% upside)")
            if row['notes']:
                click.echo(f"    Notes: {row['notes']}")
            click.echo()

    except Exception as e:
        print_error(f"Error viewing watchlist: {str(e)}")


# Custom Screen Commands
@cli.group()
def custom():
    """Create and manage custom screens."""
    pass


@custom.command('create')
@click.argument('name')
@click.option('--description', '-d', required=True, help='Screen description')
@click.option('--criteria', '-c', required=True, help='Criteria in JSON format')
@click.option('--logic', '-l', default='AND', type=click.Choice(['AND', 'OR']),
              help='Logic operator')
def custom_create(name, description, criteria, logic):
    """Create a new custom screen."""
    try:
        import json
        criteria_dict = json.loads(criteria)

        builder = CustomScreenBuilder()
        if builder.create_screen(name, description, criteria_dict, logic):
            print_success(f"Created custom screen: {name}")
        else:
            print_error("Failed to create custom screen")

    except json.JSONDecodeError:
        print_error("Invalid JSON format for criteria")
    except Exception as e:
        print_error(f"Error creating custom screen: {str(e)}")


@custom.command('list')
def custom_list():
    """List all custom screens."""
    try:
        builder = CustomScreenBuilder()
        screens = builder.list_screens()

        if not screens:
            print_warning("No custom screens found")
            return

        click.echo("\n📋 Custom Screens:\n")
        for screen in screens:
            click.echo(f"  {screen['name']}")
            click.echo(f"    Description: {screen['description']}")
            click.echo(f"    Created: {screen['created_at']}")
            click.echo()

    except Exception as e:
        print_error(f"Error listing custom screens: {str(e)}")


@custom.command('run')
@click.argument('name')
@click.option('--limit', '-l', type=int, default=50, help='Maximum results')
@click.option('--output', '-o', help='Save to file (csv/xlsx)')
def custom_run(name, limit, output):
    """Run a custom screen."""
    try:
        builder = CustomScreenBuilder()
        results = builder.run_screen(name)

        if results is None or results.empty:
            print_warning(f"No results from screen: {name}")
            return

        # Display results (reuse screen display logic)
        screen_config = builder.get_screen(name)
        if screen_config:
            click.echo(f"\n🔍 {screen_config['name']}")
            click.echo(f"   {screen_config['description']}\n")

        click.echo(f"Found {len(results)} stocks:\n")
        for _, row in results.head(limit).iterrows():
            click.echo(f"  {row['ticker']} - {row.get('company_name', '')}")

        # Save if requested
        if output:
            if output.endswith('.csv'):
                results.to_csv(output, index=False)
                print_success(f"Results saved to {output}")
            elif output.endswith('.xlsx'):
                results.to_excel(output, index=False, engine='openpyxl')
                print_success(f"Results saved to {output}")

    except Exception as e:
        print_error(f"Error running custom screen: {str(e)}")


@custom.command('delete')
@click.argument('name')
@click.confirmation_option(prompt='Are you sure you want to delete this screen?')
def custom_delete(name):
    """Delete a custom screen."""
    try:
        builder = CustomScreenBuilder()
        if builder.delete_screen(name):
            print_success(f"Deleted custom screen: {name}")
        else:
            print_error("Failed to delete custom screen")
    except Exception as e:
        print_error(f"Error deleting custom screen: {str(e)}")


# Backtesting Commands
@cli.group()
def backtest():
    """Backtest screening strategies."""
    pass


@backtest.command('run')
@click.argument('screen_name')
@click.option('--screen-type', type=click.Choice(['predefined', 'custom']),
              default='predefined', help='Screen type')
@click.option('--start-date', '-s', required=True, help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e', help='End date (YYYY-MM-DD), default: today')
@click.option('--holding-period', '-p', type=int, default=90,
              help='Holding period in days')
def backtest_run(screen_name, screen_type, start_date, end_date, holding_period):
    """Run a backtest for a screen."""
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d').date()
        end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else date.today()

        engine = BacktestEngine()

        # Get screen config
        if screen_type == 'predefined':
            from screener.criteria import get_screen_config
            screen_config = get_screen_config(screen_name)
        else:
            builder = CustomScreenBuilder()
            screen_config = builder.get_screen(screen_name)
            if not screen_config:
                print_error(f"Custom screen not found: {screen_name}")
                return

        # Run backtest
        print_info(f"Running backtest for {screen_name}...")
        results = engine.run_backtest(screen_name, screen_config, start, end, holding_period)

        if results:
            click.echo(f"\n📈 Backtest Results for {screen_name}\n")
            click.echo(f"  Period: {start} to {end}")
            click.echo(f"  Stocks Passed: {results.get('stocks_passed', 0)}")
            click.echo(f"  Average Return: {results.get('average_return', 0):.2f}%")
            click.echo(f"  Median Return: {results.get('median_return', 0):.2f}%")
            if 'best_performer' in results:
                click.echo(f"  Best: {results['best_performer']}")
            if 'worst_performer' in results:
                click.echo(f"  Worst: {results['worst_performer']}")

            print_success("Backtest completed and saved")
        else:
            print_error("Backtest failed")

    except Exception as e:
        print_error(f"Error running backtest: {str(e)}")


@backtest.command('history')
@click.option('--screen', '-s', help='Filter by screen name')
def backtest_history(screen):
    """View backtest history."""
    try:
        engine = BacktestEngine()
        history = engine.get_backtest_history(screen)

        if history.empty:
            print_warning("No backtest history found")
            return

        click.echo("\n📜 Backtest History:\n")
        for _, row in history.iterrows():
            click.echo(f"  {row['screen_name']} - {row['backtest_date']}")
            click.echo(f"    Period: {row['start_date']} to {row['end_date']}")
            click.echo(f"    Stocks: {row['stocks_passed']}")
            click.echo(f"    Avg Return: {row['average_return']:.2f}%")
            click.echo()

    except Exception as e:
        print_error(f"Error viewing backtest history: {str(e)}")


if __name__ == '__main__':
    cli()
