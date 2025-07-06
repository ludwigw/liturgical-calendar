"""
Main entry point for liturgical calendar calculations and CLI usage.

This Python module will return the name, season, week number and liturgical
colour for any day in the Gregorian calendar, according to the Anglican
tradition of the Church of England.
"""

import sys
from datetime import date, datetime

from liturgical_calendar.logging import get_logger, setup_logging

from .config.settings import Settings
from .exceptions import LiturgicalCalendarError
from .services.config_service import ConfigService
from .services.feast_service import FeastService
from .services.image_service import ImageService

##########################################################################

# Instantiate the services
feast_service = FeastService()
image_service = ImageService()
config_service = ConfigService()


def liturgical_calendar(s_date: str, transferred: bool = False):
    """
    Return the liturgical colour for a given day.
    This function contains the main logic for liturgical calendar calculation.
    """
    if isinstance(s_date, datetime):
        s_date = s_date.date().strftime("%Y-%m-%d")
    elif isinstance(s_date, date):
        s_date = s_date.strftime("%Y-%m-%d")
    # If string, assume it's already in YYYY-MM-DD format
    return feast_service.get_complete_feast_info(s_date, transferred)


def main():
    """Main entry point for running the script as a CLI."""
    # Parse --verbose flag
    verbose = False
    args = sys.argv[1:]
    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")
    setup_logging(level="DEBUG" if verbose else "INFO")
    logger = get_logger(__name__)
    if verbose:
        print("[INFO] Verbose mode enabled (log level: DEBUG)")
    # Optionally load config file from argument or default location
    config_path = None
    if len(args) > 1 and not args[1].startswith("-"):
        config_path = args[1]
    Settings.load_from_file(config_path)  # Loads config from file/env if present
    if len(args) > 0:
        date_str = args[0]
    else:
        date_str = date.today().strftime("%Y-%m-%d")
    try:
        logger.info("Starting liturgical.py script")
        result = liturgical_calendar(date_str)
        print(f"Date: {date_str}")
        print(f"Season: {result.get('season', 'Unknown')}")
        print(f"Week: {result.get('week', 'Unknown')}")
        print(f"Name: {result.get('name', 'Unknown')}")
        print(f"Colour: {result.get('colour', 'Unknown')}")
        logger.info("liturgical.py script completed successfully")
    except LiturgicalCalendarError as e:
        logger.error(f"Liturgical Calendar Error: {e}")
        print(f"Liturgical Calendar Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error in liturgical.py: {e}")
        print(f"Error in liturgical.py: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if "--help" in sys.argv or "-h" in sys.argv:
        print(
            "Usage: python -m liturgical_calendar.liturgical [YYYY-MM-DD] [config.yaml] [--verbose]"
        )
        print("  [YYYY-MM-DD]   Optional date to query (default: today)")
        print("  [config.yaml]  Optional path to config file")
        print("  --verbose      Enable verbose (DEBUG) logging output")
        sys.exit(0)
    main()
