"""
Predefined screening criteria and screen definitions.
"""

# Predefined screening strategies
PREDEFINED_SCREENS = {
    'value': {
        'name': 'Value Screen',
        'description': 'Traditional value investing criteria',
        'logic': 'AND',
        'criteria': {
            'price_to_book': {'operator': '<', 'value': 5},
            'ev_ebitda': {'operator': '<', 'value': 12},
            'roe': {'operator': '>', 'value': 15},
            'debt_equity': {'operator': '<', 'value': 1.5},
            'interest_coverage': {'operator': '>', 'value': 3},
            'market_cap': {'operator': '>', 'value': 500},
        }
    },
    'growth': {
        'name': 'Growth Screen',
        'description': 'High-growth companies with sustainable metrics',
        'logic': 'AND',
        'criteria': {
            'revenue_cagr_3y': {'operator': '>', 'value': 20},
            'opm': {'operator': '>', 'value': 20},
            'debt_equity': {'operator': '<', 'value': 1},
            'interest_coverage': {'operator': '>', 'value': 5},
        }
    },
    'balanced': {
        'name': 'Balanced Screen',
        'description': 'Reasonably-valued growth companies',
        'logic': 'AND',
        'criteria': {
            'price_to_book': {'operator': '<', 'value': 8},
            'ev_ebitda': {'operator': '<', 'value': 20},
            'roe': {'operator': '>', 'value': 12},
            'opm': {'operator': '>', 'value': 15},
            'debt_equity': {'operator': '<', 'value': 2},
            'interest_coverage': {'operator': '>', 'value': 3},
        }
    },
    'quality': {
        'name': 'Quality Screen',
        'description': 'High-quality businesses with strong fundamentals',
        'logic': 'AND',
        'criteria': {
            'roe': {'operator': '>', 'value': 20},
            'roce': {'operator': '>', 'value': 20},
            'opm': {'operator': '>', 'value': 15},
            'interest_coverage': {'operator': '>', 'value': 5},
            'debt_equity': {'operator': '<', 'value': 0.5},
            'altman_z_score': {'operator': '>', 'value': 2.6},
        }
    },
    'turnaround': {
        'name': 'Turnaround Screen',
        'description': 'Companies showing operational improvement',
        'logic': 'AND',
        'criteria': {
            'opm': {'operator': '>', 'value': 20},
            'debt_equity': {'operator': '<', 'value': 2},
            'market_cap': {'operator': '>', 'value': 200},
        }
    }
}


def get_screen_config(screen_name: str) -> dict:
    """
    Get configuration for a predefined screen.

    Args:
        screen_name: Name of the screen

    Returns:
        Screen configuration dictionary

    Raises:
        ValueError: If screen name is not found
    """
    if screen_name not in PREDEFINED_SCREENS:
        available = ', '.join(PREDEFINED_SCREENS.keys())
        raise ValueError(f"Unknown screen: {screen_name}. Available: {available}")

    return PREDEFINED_SCREENS[screen_name]


def list_available_screens() -> list:
    """
    Get list of available predefined screens.

    Returns:
        List of tuples (name, description)
    """
    return [
        (name, config['name'], config['description'])
        for name, config in PREDEFINED_SCREENS.items()
    ]
