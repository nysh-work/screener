"""
Core screening engine for filtering stocks.
"""
import pandas as pd
from typing import Dict, List, Optional
from data.database import Database
from screener.criteria import get_screen_config
from utils.logger import get_logger

logger = get_logger(__name__)


class ScreeningEngine:
    """Execute screening strategies on stock data."""

    def __init__(self, db: Database):
        """
        Initialize screening engine.

        Args:
            db: Database instance
        """
        self.db = db

    def _build_where_clause(self, criteria: Dict[str, Dict], logic: str = 'AND') -> tuple:
        """
        Build SQL WHERE clause from criteria.

        Args:
            criteria: Dictionary of field names to filter conditions
            logic: 'AND' or 'OR' for combining criteria

        Returns:
            Tuple of (where_clause_string, parameters_list)
        """
        # Mapping of column names to their table aliases
        column_table_map = {
            'market_cap': 'c',
            'sector': 'c',
            'industry': 'c',
            'price_to_book': 'd',
            'price_to_earnings': 'd',
            'ev_ebitda': 'd',
            'roe': 'd',
            'roce': 'd',
            'debt_equity': 'd',
            'current_ratio': 'd',
            'interest_coverage': 'd',
            'opm': 'd',
            'npm': 'd',
            'revenue_cagr_3y': 'g',
            'revenue_cagr_5y': 'g',
            'profit_cagr_3y': 'g',
            'profit_cagr_5y': 'g',
            'promoter_holding': 'q',
            'altman_z_score': 'q',
            'ocf_to_net_profit': 'q',
        }

        where_clauses = []
        params = {}

        for field, condition in criteria.items():
            operator = condition['operator']
            value = condition.get('value')

            # Add table prefix if field is in our mapping
            qualified_field = f"{column_table_map[field]}.{field}" if field in column_table_map else field
            param_name = field.replace('.', '_')

            if operator == 'between':
                where_clauses.append(f"{qualified_field} BETWEEN :{param_name}_min AND :{param_name}_max")
                params[f'{param_name}_min'] = condition['min']
                params[f'{param_name}_max'] = condition['max']
            elif operator == 'in':
                # For IN operator with list of values
                placeholders = ','.join([f':{param_name}_{i}' for i in range(len(value))])
                where_clauses.append(f"{qualified_field} IN ({placeholders})")
                for i, v in enumerate(value):
                    params[f'{param_name}_{i}'] = v
            else:
                where_clauses.append(f"{qualified_field} {operator} :{param_name}")
                params[param_name] = value

        where_sql = f" {logic} ".join(where_clauses)
        return where_sql, params

    def apply_criteria(
        self,
        criteria: Dict[str, Dict],
        logic: str = 'AND',
        additional_filters: Dict = None
    ) -> pd.DataFrame:
        """
        Apply screening criteria to database.

        Args:
            criteria: Dictionary of field names to filter conditions
            logic: 'AND' or 'OR' for combining multiple criteria
            additional_filters: Additional filters (sector, min_market_cap, etc.)

        Returns:
            DataFrame with stocks matching criteria
        """
        where_sql, params = self._build_where_clause(criteria, logic)

        # Add additional filters
        additional_clauses = []
        if additional_filters:
            if 'sector' in additional_filters and additional_filters['sector']:
                sectors = additional_filters['sector']
                if isinstance(sectors, str):
                    sectors = [sectors]
                sector_placeholders = ','.join([f':sector_{i}' for i in range(len(sectors))])
                additional_clauses.append(f"c.sector IN ({sector_placeholders})")
                for i, sector in enumerate(sectors):
                    params[f'sector_{i}'] = sector

            if 'min_market_cap' in additional_filters and additional_filters['min_market_cap']:
                additional_clauses.append("c.market_cap >= :min_market_cap")
                params['min_market_cap'] = additional_filters['min_market_cap']

        if additional_clauses:
            where_sql = f"({where_sql}) AND {' AND '.join(additional_clauses)}"

        # Build main query
        query = f"""
        SELECT DISTINCT
            c.ticker,
            c.company_name,
            c.sector,
            c.industry,
            c.market_cap,
            f.price,
            d.price_to_book,
            d.price_to_earnings,
            d.ev_ebitda,
            d.roe,
            d.roce,
            d.debt_equity,
            d.current_ratio,
            d.interest_coverage,
            d.opm,
            d.npm,
            g.revenue_cagr_3y,
            g.profit_cagr_3y,
            q.promoter_holding,
            q.altman_z_score,
            q.ocf_to_net_profit
        FROM company_master c
        LEFT JOIN fundamentals f ON c.ticker = f.ticker
        LEFT JOIN derived_metrics d ON c.ticker = d.ticker
        LEFT JOIN growth_metrics g ON c.ticker = g.ticker
        LEFT JOIN quality_metrics q ON c.ticker = q.ticker
        WHERE {where_sql}
        ORDER BY d.roe DESC, c.market_cap DESC
        """

        logger.info(f"Executing screening query with {len(criteria)} criteria")
        logger.debug(f"Query: {query}")
        logger.debug(f"Params: {params}")

        try:
            results = self.db.execute_query(query, params)
            df = pd.DataFrame(results)

            logger.info(f"Screen returned {len(df)} results")
            return df

        except Exception as e:
            logger.error(f"Error executing screen: {str(e)}")
            raise

    def run_predefined_screen(
        self,
        screen_name: str,
        additional_filters: Dict = None
    ) -> pd.DataFrame:
        """
        Execute a predefined screening strategy.

        Args:
            screen_name: Name of the screen (value, growth, balanced, etc.)
            additional_filters: Additional filters to apply

        Returns:
            DataFrame with screening results
        """
        try:
            screen_config = get_screen_config(screen_name)

            logger.info(f"Running {screen_config['name']}")
            logger.info(f"Description: {screen_config['description']}")

            criteria = screen_config['criteria']
            logic = screen_config.get('logic', 'AND')

            results = self.apply_criteria(criteria, logic, additional_filters)

            # Log to audit trail
            self.db.log_operation(
                operation='screen_run',
                details=f"Screen: {screen_name}, Results: {len(results)}",
                status='success'
            )

            return results

        except Exception as e:
            logger.error(f"Error running screen {screen_name}: {str(e)}")
            self.db.log_operation(
                operation='screen_run',
                details=f"Screen: {screen_name}, Error: {str(e)}",
                status='failure'
            )
            raise

    def run_custom_screen(self, criteria: Dict, logic: str = 'AND') -> pd.DataFrame:
        """
        Run a custom screen with user-defined criteria.

        Args:
            criteria: Custom criteria dictionary
            logic: AND or OR logic

        Returns:
            DataFrame with results
        """
        logger.info(f"Running custom screen with {len(criteria)} criteria")
        return self.apply_criteria(criteria, logic)

    def get_screen_statistics(self, results: pd.DataFrame) -> Dict:
        """
        Calculate statistics for screening results.

        Args:
            results: DataFrame with screening results

        Returns:
            Dictionary with statistics
        """
        if results.empty:
            return {
                'total_stocks': 0,
                'sectors': [],
                'avg_roe': None,
                'median_pb': None,
                'median_de': None,
            }

        stats = {
            'total_stocks': len(results),
            'sectors': results['sector'].value_counts().to_dict() if 'sector' in results else {},
            'avg_roe': results['roe'].mean() if 'roe' in results else None,
            'median_pb': results['price_to_book'].median() if 'price_to_book' in results else None,
            'median_de': results['debt_equity'].median() if 'debt_equity' in results else None,
            'avg_market_cap': results['market_cap'].mean() if 'market_cap' in results else None,
        }

        return stats
