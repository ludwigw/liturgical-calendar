"""
This Python module will return the name, season, week number and liturgical
colour for any day in the Gregorian calendar, according to the Anglican
tradition of the Church of England.
"""

import sys
from datetime import datetime, date

from .funcs import get_easter, get_advent_sunday, date_to_days, day_of_week, add_delta_days, colour_code, get_week_number, render_week_name
from .data.feasts_data import feasts, get_liturgical_feast
from .services.feast_service import FeastService
from .services.image_service import ImageService
from .services.config_service import ConfigService
from .config.settings import Settings

##########################################################################

# Instantiate the services
feast_service = FeastService()
image_service = ImageService()
config_service = ConfigService()

def liturgical_calendar(s_date: str, transferred: bool = False):
    """
    Return the liturgical colour for a given day
    This func contains the main logic
    """
    if isinstance(s_date, datetime):
        s_date = s_date.date().strftime("%Y-%m-%d")
    elif isinstance(s_date, date):
        s_date = s_date.strftime("%Y-%m-%d")
    # If string, assume it's already in YYYY-MM-DD format
    return feast_service.get_complete_feast_info(s_date, transferred)

def main():
    """
    Main function for command line usage
    """
    # Optionally load config file from argument or default location
    config_path = None
    if len(sys.argv) > 2 and not sys.argv[2].startswith('-'):
        config_path = sys.argv[2]
    Settings.load_from_file(config_path)  # Loads config from file/env if present
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        date_str = date.today().strftime("%Y-%m-%d")
    
    result = liturgical_calendar(date_str)
    print(f"Date: {date_str}")
    print(f"Season: {result.get('season', 'Unknown')}")
    print(f"Week: {result.get('week', 'Unknown')}")
    print(f"Name: {result.get('name', 'Unknown')}")
    print(f"Colour: {result.get('colour', 'Unknown')}")

if __name__ == "__main__":
    main()
