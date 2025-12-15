"""
Custom screen builder for creating and managing user-defined screens.
"""
import json
from typing import Dict, List, Optional
from data.database import Database
from screener.engine import ScreeningEngine
from utils.logger import get_logger

logger = get_logger(__name__)


class CustomScreenBuilder:
    """Build and manage custom screening criteria."""

    def __init__(self, db: Database = None):
        """Initialize custom screen builder."""
        self.db = db if db else Database()
        self.engine = ScreeningEngine(self.db)

    def create_screen(self, name: str, description: str, criteria: Dict,
                     logic: str = 'AND') -> bool:
        """
        Create a new custom screen.

        Args:
            name: Screen name
            description: Screen description
            criteria: Dictionary of criteria (field: {operator, value})
            logic: Logic operator ('AND' or 'OR')

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate criteria format
            self._validate_criteria(criteria)

            screen_data = {
                'name': name,
                'description': description,
                'criteria': json.dumps(criteria),
                'logic': logic.upper()
            }

            self.db.save_custom_screen(screen_data)
            logger.info(f"Created custom screen: {name}")
            return True

        except Exception as e:
            logger.error(f"Error creating custom screen: {str(e)}")
            return False

    def update_screen(self, name: str, description: str = None, criteria: Dict = None,
                     logic: str = None) -> bool:
        """
        Update an existing custom screen.

        Args:
            name: Screen name
            description: New description (optional)
            criteria: New criteria (optional)
            logic: New logic operator (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing screen
            existing = self.db.get_custom_screen(name)
            if not existing:
                logger.error(f"Screen not found: {name}")
                return False

            # Build update data
            screen_data = {'name': name}

            if description:
                screen_data['description'] = description
            else:
                screen_data['description'] = existing['description']

            if criteria:
                self._validate_criteria(criteria)
                screen_data['criteria'] = json.dumps(criteria)
            else:
                screen_data['criteria'] = existing['criteria']

            if logic:
                screen_data['logic'] = logic.upper()
            else:
                screen_data['logic'] = existing['logic']

            self.db.save_custom_screen(screen_data)
            logger.info(f"Updated custom screen: {name}")
            return True

        except Exception as e:
            logger.error(f"Error updating custom screen: {str(e)}")
            return False

    def delete_screen(self, name: str) -> bool:
        """
        Delete a custom screen.

        Args:
            name: Screen name

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.delete_custom_screen(name)
            logger.info(f"Deleted custom screen: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting custom screen: {str(e)}")
            return False

    def get_screen(self, name: str) -> Optional[Dict]:
        """
        Get a custom screen by name.

        Args:
            name: Screen name

        Returns:
            Screen configuration or None if not found
        """
        try:
            screen = self.db.get_custom_screen(name)
            if screen:
                # Parse criteria JSON
                screen['criteria'] = json.loads(screen['criteria'])
            return screen
        except Exception as e:
            logger.error(f"Error getting custom screen: {str(e)}")
            return None

    def list_screens(self) -> List[Dict]:
        """
        List all custom screens.

        Returns:
            List of screen summaries
        """
        try:
            return self.db.list_custom_screens()
        except Exception as e:
            logger.error(f"Error listing custom screens: {str(e)}")
            return []

    def run_screen(self, name: str, additional_filters: Dict = None):
        """
        Run a custom screen.

        Args:
            name: Screen name
            additional_filters: Optional additional filters

        Returns:
            Screen results DataFrame
        """
        try:
            screen = self.get_screen(name)
            if not screen:
                logger.error(f"Screen not found: {name}")
                return None

            # Convert to engine format
            screen_config = {
                'name': screen['name'],
                'description': screen['description'],
                'criteria': screen['criteria'],
                'logic': screen['logic']
            }

            return self.engine.run_custom_screen(screen_config, additional_filters)

        except Exception as e:
            logger.error(f"Error running custom screen: {str(e)}")
            return None

    def _validate_criteria(self, criteria: Dict) -> None:
        """
        Validate criteria format.

        Args:
            criteria: Criteria dictionary

        Raises:
            ValueError: If criteria format is invalid
        """
        valid_operators = ['<', '>', '<=', '>=', '=', '!=']
        valid_fields = [
            # Valuation
            'price_to_book', 'price_to_earnings', 'ev_ebitda',
            # Profitability
            'roe', 'roce', 'opm', 'npm',
            # Leverage
            'debt_equity', 'current_ratio', 'interest_coverage',
            # Growth
            'revenue_cagr_3y', 'revenue_cagr_5y', 'profit_cagr_3y', 'profit_cagr_5y',
            # Quality
            'altman_z_score', 'promoter_holding', 'ocf_to_net_profit',
            # Technical
            'ema_20', 'ema_50', 'macd', 'choppiness_index', 'atr_14',
            # Other
            'market_cap', 'price'
        ]

        for field, condition in criteria.items():
            if field not in valid_fields:
                raise ValueError(f"Invalid field: {field}. Must be one of {valid_fields}")

            if not isinstance(condition, dict):
                raise ValueError(f"Condition for {field} must be a dictionary")

            if 'operator' not in condition or 'value' not in condition:
                raise ValueError(f"Condition for {field} must have 'operator' and 'value' keys")

            if condition['operator'] not in valid_operators:
                raise ValueError(f"Invalid operator: {condition['operator']}. Must be one of {valid_operators}")

    def create_from_template(self, template_name: str, custom_name: str,
                           parameter_overrides: Dict = None) -> bool:
        """
        Create a custom screen from a predefined template.

        Args:
            template_name: Name of the template (value, growth, quality, etc.)
            custom_name: Name for the new custom screen
            parameter_overrides: Dictionary of parameter overrides

        Returns:
            True if successful, False otherwise
        """
        try:
            from screener.criteria import get_screen_config

            # Get template
            template = get_screen_config(template_name)

            # Apply overrides
            criteria = template['criteria'].copy()
            if parameter_overrides:
                for field, condition in parameter_overrides.items():
                    if field in criteria:
                        criteria[field].update(condition)

            return self.create_screen(
                name=custom_name,
                description=f"Custom screen based on {template['name']}",
                criteria=criteria,
                logic=template['logic']
            )

        except Exception as e:
            logger.error(f"Error creating from template: {str(e)}")
            return False
