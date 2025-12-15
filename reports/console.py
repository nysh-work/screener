"""
Console output using Rich library for beautiful terminal tables.
"""
import pandas as pd
from typing import Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from datetime import datetime
from utils.helpers import format_currency, format_percentage

console = Console()


def display_screen_results(
    results: pd.DataFrame,
    screen_name: str,
    screen_description: str = None,
    criteria: Dict = None,
    stats: Dict = None,
    limit: int = 50
):
    """
    Display screening results in a rich table format.

    Args:
        results: DataFrame with screening results
        screen_name: Name of the screen
        screen_description: Description of the screen
        criteria: Criteria used for screening
        stats: Statistics dictionary
        limit: Maximum number of results to display
    """
    # Header
    console.print()
    console.print(f"[bold cyan]{'=' * 80}[/bold cyan]")
    console.print(f"[bold white]{screen_name}[/bold white] [dim](as of {datetime.now().strftime('%d-%b-%Y')})[/dim]")
    console.print(f"[bold cyan]{'=' * 80}[/bold cyan]")

    if screen_description:
        console.print(f"[dim]{screen_description}[/dim]")
        console.print()

    # Display criteria
    if criteria:
        console.print("[bold]Criteria Applied:[/bold]")
        for field, condition in criteria.items():
            operator = condition['operator']
            value = condition.get('value', '')
            field_display = field.replace('_', ' ').title()

            if operator == 'between':
                console.print(f"  • {field_display}: {condition['min']} to {condition['max']}")
            else:
                console.print(f"  • {field_display} {operator} {value}")
        console.print()

    # Display statistics
    if stats:
        console.print(f"[bold]Total Matches:[/bold] {stats.get('total_stocks', 0)} stocks")

        if stats.get('avg_roe'):
            console.print(
                f"[bold]Average ROE:[/bold] {stats['avg_roe']:.1f}%  |  "
                f"[bold]Median P/B:[/bold] {stats.get('median_pb', 0):.1f}  |  "
                f"[bold]Median D/E:[/bold] {stats.get('median_de', 0):.2f}"
            )
        console.print()

    # Display results table
    if results.empty:
        console.print("[yellow]No stocks match the criteria.[/yellow]")
        return

    # Limit results
    display_results = results.head(limit)

    # Create table
    table = Table(show_header=True, header_style="bold magenta", show_lines=False)

    # Add columns
    table.add_column("Ticker", style="cyan", width=12)
    table.add_column("Company", style="white", width=25)
    table.add_column("Sector", style="blue", width=15)
    table.add_column("MCap\n(₹Cr)", justify="right", style="yellow", width=10)
    table.add_column("P/B", justify="right", style="green", width=6)
    table.add_column("P/E", justify="right", style="green", width=6)
    table.add_column("EV/\nEBITDA", justify="right", style="green", width=7)
    table.add_column("ROE\n%", justify="right", style="cyan", width=6)
    table.add_column("D/E", justify="right", style="magenta", width=6)
    table.add_column("Int\nCov", justify="right", style="blue", width=6)

    # Add rows
    for _, row in display_results.iterrows():
        table.add_row(
            str(row.get('ticker', 'N/A')),
            str(row.get('company_name', 'N/A'))[:25],
            str(row.get('sector', 'N/A'))[:15],
            f"{row.get('market_cap', 0):,.0f}" if pd.notna(row.get('market_cap')) else "N/A",
            f"{row.get('price_to_book', 0):.1f}" if pd.notna(row.get('price_to_book')) else "N/A",
            f"{row.get('price_to_earnings', 0):.1f}" if pd.notna(row.get('price_to_earnings')) else "N/A",
            f"{row.get('ev_ebitda', 0):.1f}" if pd.notna(row.get('ev_ebitda')) else "N/A",
            f"{row.get('roe', 0):.1f}" if pd.notna(row.get('roe')) else "N/A",
            f"{row.get('debt_equity', 0):.2f}" if pd.notna(row.get('debt_equity')) else "N/A",
            f"{row.get('interest_coverage', 0):.1f}" if pd.notna(row.get('interest_coverage')) else "N/A",
        )

    console.print(table)

    # Footer
    if len(results) > limit:
        console.print(f"\n[dim]Showing top {limit} of {len(results)} results[/dim]")

    console.print(f"\n[bold cyan]{'=' * 80}[/bold cyan]\n")


def display_stock_detail(stock_data: Dict):
    """
    Display detailed information for a single stock.

    Args:
        stock_data: Dictionary with stock data
    """
    console.print()
    console.print(Panel.fit(
        f"[bold white]{stock_data.get('company_name', 'N/A')}[/bold white]\n"
        f"[cyan]{stock_data.get('ticker', 'N/A')}[/cyan] | {stock_data.get('sector', 'N/A')} | {stock_data.get('industry', 'N/A')}",
        title="Stock Details",
        border_style="cyan"
    ))

    # Create tables for different metric categories
    # Valuation Metrics
    val_table = Table(title="Valuation Metrics", show_header=True, header_style="bold yellow")
    val_table.add_column("Metric", style="white")
    val_table.add_column("Value", justify="right", style="cyan")

    val_table.add_row("Market Cap", format_currency(stock_data.get('market_cap', 0)))
    val_table.add_row("Price", f"₹{stock_data.get('price', 0):.2f}" if stock_data.get('price') else "N/A")
    val_table.add_row("Price to Book", f"{stock_data.get('price_to_book', 0):.2f}" if stock_data.get('price_to_book') else "N/A")
    val_table.add_row("Price to Earnings", f"{stock_data.get('price_to_earnings', 0):.2f}" if stock_data.get('price_to_earnings') else "N/A")
    val_table.add_row("EV/EBITDA", f"{stock_data.get('ev_ebitda', 0):.2f}" if stock_data.get('ev_ebitda') else "N/A")

    console.print(val_table)

    # Profitability Metrics
    prof_table = Table(title="Profitability Metrics", show_header=True, header_style="bold green")
    prof_table.add_column("Metric", style="white")
    prof_table.add_column("Value", justify="right", style="cyan")

    prof_table.add_row("ROE", format_percentage(stock_data.get('roe', 0)))
    prof_table.add_row("ROCE", format_percentage(stock_data.get('roce', 0)))
    prof_table.add_row("Operating Margin", format_percentage(stock_data.get('opm', 0)))
    prof_table.add_row("Net Profit Margin", format_percentage(stock_data.get('npm', 0)))

    console.print(prof_table)

    # Leverage Metrics
    lev_table = Table(title="Leverage & Safety", show_header=True, header_style="bold red")
    lev_table.add_column("Metric", style="white")
    lev_table.add_column("Value", justify="right", style="cyan")

    lev_table.add_row("Debt to Equity", f"{stock_data.get('debt_equity', 0):.2f}" if stock_data.get('debt_equity') else "N/A")
    lev_table.add_row("Current Ratio", f"{stock_data.get('current_ratio', 0):.2f}" if stock_data.get('current_ratio') else "N/A")
    lev_table.add_row("Interest Coverage", f"{stock_data.get('interest_coverage', 0):.2f}" if stock_data.get('interest_coverage') else "N/A")
    lev_table.add_row("Altman Z-Score", f"{stock_data.get('altman_z_score', 0):.2f}" if stock_data.get('altman_z_score') else "N/A")

    console.print(lev_table)
    console.print()


def display_sector_analysis(sector_stats: Dict):
    """
    Display sector-wise analysis.

    Args:
        sector_stats: Dictionary with sector statistics
    """
    console.print()
    console.print("[bold cyan]Sector Distribution[/bold cyan]")
    console.print()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Sector", style="cyan", width=30)
    table.add_column("Count", justify="right", style="yellow", width=10)
    table.add_column("Percentage", justify="right", style="green", width=12)

    total = sum(sector_stats.values())

    for sector, count in sorted(sector_stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total * 100) if total > 0 else 0
        table.add_row(sector, str(count), f"{percentage:.1f}%")

    console.print(table)
    console.print()


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str):
    """Print a success message."""
    console.print(f"[bold green]✓[/bold green] {message}")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[bold blue]ℹ[/bold blue] {message}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")
