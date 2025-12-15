#!/usr/bin/env python3
"""
Stock Screener CLI - Main entry point.
"""
import click
from datetime import datetime
from data.database import Database
from data.fetcher import YFinanceFetcher, get_nse_top_stocks
from screener.engine import ScreeningEngine
from screener.criteria import list_available_screens
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
def update(full, incremental, tickers, limit):
    """Update stock data from yfinance."""
    print_info("Starting data update...")

    db = Database()
    fetcher = YFinanceFetcher()

    # Determine which tickers to fetch
    if tickers:
        ticker_list = list(tickers)
        print_info(f"Fetching data for {len(ticker_list)} specified tickers")
    elif full:
        ticker_list = get_nse_top_stocks()[:limit]
        print_info(f"Full refresh: Fetching top {len(ticker_list)} NSE stocks")
    else:
        # Default: fetch top stocks
        ticker_list = get_nse_top_stocks()[:limit]
        print_info(f"Fetching data for {len(ticker_list)} stocks")

    success_count = 0
    error_count = 0

    with click.progressbar(ticker_list, label='Fetching stock data') as bar:
        for ticker in bar:
            try:
                # Fetch all data for the ticker
                data = fetcher.fetch_all_data(ticker)

                if data:
                    # Save to database
                    db.add_company(data['company'])
                    db.add_fundamentals(data['fundamentals'])
                    db.add_derived_metrics(data['derived_metrics'])
                    db.add_growth_metrics(data['growth_metrics'])
                    db.add_quality_metrics(data['quality_metrics'])

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


if __name__ == '__main__':
    cli()
