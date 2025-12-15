"""
Initialize the database schema.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.database import Database


def main():
    """Create database tables."""
    print("Setting up stock screener database...")

    db = Database()
    db.create_tables()

    print("Database setup complete!")
    print("Tables created:")
    print("  - company_master")
    print("  - fundamentals")
    print("  - derived_metrics")
    print("  - growth_metrics")
    print("  - quality_metrics")
    print("  - audit_log")


if __name__ == '__main__':
    main()
