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

    # s_date could in a variety of formats
    # We standardise to f_date as a Date
    if isinstance(s_date, datetime):
        # If datetime, strip it to the date
        f_date = s_date.date()
    elif isinstance(s_date, date):
        # If date, accept it
        f_date = s_date
    elif isinstance(s_date, str):
        # If string, try to parse a YYYY-MM-DD
        f_date = datetime.strptime(s_date, "%Y-%m-%d").date()
    else:
        # Otherwise use today's date
        f_date = date.today()

    # Extract the components from the date
    year = f_date.year
    month = f_date.month
    day = f_date.day
    dayofweek = day_of_week(year, month, day)

    # Calculate some values in Julian date
    days = date_to_days(year, month, day)
    easterm, easterd = get_easter(year)
    easterday = date_to_days(year, easterm, easterd)

    # Calculate key liturgical points
    easter_point = days - easterday
    christmas_point = config_service.calculate_christmas_point(year, month, days)
    advent_sunday = get_advent_sunday(year)

    # Use SeasonCalculator for season and week number
    season = feast_service.season_calculator.determine_season(f_date, easter_point, christmas_point, advent_sunday)
    weekno = feast_service.season_calculator.calculate_week_number(f_date, easter_point, christmas_point, advent_sunday, dayofweek)
    
    # Use SeasonCalculator for weekday_reading
    weekday_reading = feast_service.season_calculator.calculate_weekday_reading(f_date, easter_point, christmas_point, advent_sunday, dayofweek, days, easterday)

    # Get season URL from config service
    season_url = config_service.get_season_url(season)

    # Render a Week name with or without number
    # For weekdays, determine the week name based on the Sunday that starts the week
    if dayofweek == 0:
        # It's a Sunday, use the current season
        # Special case: if weekday_reading is "N before Advent", use that for the week name too
        if weekday_reading and weekday_reading.endswith(' before Advent'):
            week = weekday_reading
        else:
            week, season = feast_service.season_calculator.render_week_name(season, weekno, easter_point)
    else:
        # It's a weekday, calculate what the season would be for the Sunday that starts this week
        sunday_season, sunday_weekno = feast_service.season_calculator.calculate_sunday_week_info(f_date, dayofweek, days, easterday, year)
        week, _ = feast_service.season_calculator.render_week_name(sunday_season, sunday_weekno, easter_point)

    # Only set weekno to None if it's not positive and not Pre-Lent, Christmas, or Lent
    if weekno is not None and int(weekno) > 0:
        weekno = int(weekno)
    elif season not in ['Pre-Lent', 'Christmas', 'Lent']:
        weekno = None

    # Change Pre-Lent and Pre-Advent seasons to Ordinary Time for the final result
    if season in ['Pre-Lent', 'Pre-Advent']:
        season = 'Ordinary Time'

    # Use FeastService to get possible feasts
    possibles = feast_service.get_possible_feasts(
        easter_point=easter_point,
        month=month,
        day=day,
        transferred=transferred,
        s_date=s_date,
        days=days,
        season=season,
        weekno=weekno,
        dayofweek=dayofweek
    )

    # Get the highest priority feast using FeastService
    result = feast_service.get_highest_priority_feast(possibles, transferred)

    # Append season info regardless
    result['season'] = season
    result['season_url'] = season_url
    result['weekno'] = weekno
    result['week'] = week
    result['date'] = f_date
    result['weekday_reading'] = weekday_reading 

    # Use ImageService to determine color
    result['colour'] = image_service.determine_color(
        result=result,
        season=season,
        christmas_point=christmas_point,
        advent_sunday=advent_sunday
    )

    # Set colour code
    result['colourcode'] = colour_code(result['colour'])

    # Get readings using FeastService's readings_manager
    if 'readings' not in result:
        result['readings'] = feast_service.readings_manager.get_readings_for_date(f_date.strftime("%Y-%m-%d"), result)
    else:
        # If readings already exist (from feast data), append weekday readings
        if result['prec'] < 5:  # Lower precedence feast
            weekday_readings = feast_service.readings_manager.get_readings_for_date(f_date.strftime("%Y-%m-%d"), result)
            if weekday_readings and isinstance(weekday_readings, dict) and weekday_readings:
                # Merge the readings - feast readings take priority, add weekday readings
                merged_readings = result['readings'].copy()
                for key, value in weekday_readings.items():
                    if key not in merged_readings:
                        merged_readings[key] = value
                result['readings'] = merged_readings

    # Get artwork using ImageService
    result['artwork'] = image_service.get_artwork_for_date(f_date.strftime("%Y-%m-%d"), result)

    return result

def main():
    """
    Main function for command line usage
    """
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
