"""
Season calculation logic for the liturgical calendar.

This module contains the SeasonCalculator class which handles all season-related
calculations including determining liturgical seasons, week numbers, and weekday readings.
"""

from datetime import date, timedelta
from typing import Dict
from ..funcs import (
    get_easter, get_advent_sunday, date_to_days, day_of_week, 
    add_delta_days, render_week_name, get_week_number
)


class SeasonCalculator:
    """
    Handles liturgical season calculations including season determination,
    week number calculation, and weekday reading assignment.
    """
    
    def __init__(self):
        """Initialize the SeasonCalculator."""
        pass
    
    def determine_season(self, f_date: date) -> str:
        """
        Determine the liturgical season for a given date.
        See docs/liturgical_logic.md §2 for season calculation and edge cases.
        
        Args:
            f_date: The date to calculate the season for
            
        Returns:
            The liturgical season name
        """
        year = f_date.year
        days = date_to_days(f_date.year, f_date.month, f_date.day)
        easter_month, easter_day = get_easter(year)
        easterday = date_to_days(year, easter_month, easter_day)
        # For Jan/Feb, use previous year's Christmas
        if f_date.month <= 2:
            christmasday = date_to_days(year - 1, 12, 25)
        else:
            christmasday = date_to_days(year, 12, 25)
        advent_sunday = get_advent_sunday(year)
        easter_point = days - easterday
        christmas_point = days - christmasday
        # Use original logic
        if easter_point >= -62 and easter_point <= -47:
            return 'Pre-Lent'
        elif christmas_point >= advent_sunday and christmas_point <= -1:
            return 'Advent'
        elif christmas_point >= 0 and christmas_point <= 11:
            return 'Christmas'
        elif christmas_point >= 12 and christmas_point < 40:
            return 'Epiphany'
        elif easter_point <= -62:
            return 'Ordinary Time'
        elif easter_point > -47 and easter_point < -7:
            return 'Lent'
        elif easter_point >= -7 and easter_point < 0:
            return 'Holy Week'
        elif easter_point >= 0 and easter_point < 49:
            return 'Easter'
        elif easter_point >= 49 and easter_point < 56:
            return 'Pentecost'
        else:
            advent_sunday_abs = date_to_days(year, 12, 25) + advent_sunday
            weeks_until_advent = (advent_sunday_abs - days) // 7
            dayofweek = day_of_week(f_date.year, f_date.month, f_date.day)
            if dayofweek == 0 and 0 < weeks_until_advent <= 4:
                return 'Pre-Advent'
            else:
                return 'Trinity'
    
    def week_info(self, f_date: date) -> Dict:
        """
        Calculate the week information for the Sunday that starts the current week.
        Used for weekdays to determine which Sunday's season and week number to use.
        See docs/liturgical_logic.md §3 (Sunday-Based Week Naming) for rationale.
        
        Args:
            f_date: The current date
            
        Returns:
            A dictionary containing season, week_name, week_start_sunday, and weekday_reading_key
        """
        year = f_date.year
        days = date_to_days(f_date.year, f_date.month, f_date.day)
        easter_month, easter_day = get_easter(year)
        easterday = date_to_days(year, easter_month, easter_day)
        if f_date.month <= 2:
            christmasday = date_to_days(year - 1, 12, 25)
        else:
            christmasday = date_to_days(year, 12, 25)
        advent_sunday = get_advent_sunday(year)
        easter_point = days - easterday
        christmas_point = days - christmasday
        dayofweek = day_of_week(f_date.year, f_date.month, f_date.day)
        week_start_sunday_days = days - dayofweek
        week_start_sunday = add_delta_days(week_start_sunday_days)
        week_start_sunday_date = date(*week_start_sunday)
        # Use the logic from calculate_week_number and calculate_weekday_reading inline
        # (copying the logic, not calling the old public methods)
        # Calculate all points for the week-starting Sunday
        sunday_easter_point = week_start_sunday_days - easterday
        if week_start_sunday_date.month <= 2:
            sunday_christmasday = date_to_days(year - 1, 12, 25)
        else:
            sunday_christmasday = date_to_days(year, 12, 25)
        sunday_christmas_point = week_start_sunday_days - sunday_christmasday
        sunday_advent_sunday = advent_sunday
        sunday_season = self.determine_season(week_start_sunday_date)
        # Use current date's season for the season field, but Sunday's season for week naming
        current_season = self.determine_season(f_date)
        # Week number and name logic (copied from calculate_week_number and calculate_weekday_reading)
        if sunday_season == 'Pre-Lent':
            weekno = ((-49 - sunday_easter_point) // 7) + 1
            week_name = render_week_name('Pre-Lent', weekno, sunday_easter_point)[0]
            weekday_reading_key = week_name
        elif sunday_season == 'Advent':
            weekno = 1 + (sunday_christmas_point - sunday_advent_sunday) // 7
            week_name = render_week_name('Advent', weekno, sunday_easter_point)[0]
            weekday_reading_key = week_name
        elif sunday_season == 'Christmas':
            if sunday_christmas_point == 0:
                weekno = 1
            else:
                weekno = 1 + (sunday_christmas_point) // 7
            week_name = render_week_name('Christmas', weekno, sunday_easter_point)[0]
            weekday_reading_key = None
        elif sunday_season == 'Epiphany':
            weekno = max(1, 1 + (sunday_christmas_point - 12) // 7)
            week_name = render_week_name('Epiphany', weekno, sunday_easter_point)[0]
            weekday_reading_key = f"Epiphany {weekno}"
        elif sunday_season == 'Lent':
            first_sunday_lent_easter_point = -42
            weeks_from_first_sunday = (sunday_easter_point - first_sunday_lent_easter_point) // 7
            weekno = max(1, weeks_from_first_sunday + 1)
            week_name = render_week_name('Lent', weekno, sunday_easter_point)[0]
            weekday_reading_key = week_name
        elif sunday_season == 'Holy Week':
            week_name = 'Holy Week'
            weekday_reading_key = week_name
        elif sunday_season == 'Easter':
            weekno = 1 + sunday_easter_point // 7
            week_name = render_week_name('Easter', weekno, sunday_easter_point)[0]
            weekday_reading_key = week_name
        elif sunday_season == 'Pentecost':
            week_name = 'Pentecost'
            weekday_reading_key = week_name
        elif sunday_season == 'Trinity':
            # For Sundays after Trinity, use Proper N (get_week_number - 18)
            # For weekdays after Trinity, use Trinity N ((sunday_easter_point - 56) // 7 + 1)
            # Trinity Sunday and first week after Pentecost (easter_point 56-62) should be labeled 'Trinity'
            weekno = get_week_number(week_start_sunday_date) - 18
            if 56 <= sunday_easter_point < 63:
                week_name = 'Trinity'
            else:
                week_name = f"Proper {weekno}"
            # Trinity Weekday Readings have a different numbering system
            trinity_week = (sunday_easter_point - 56) // 7 + 1
            weekday_reading_key = f"Trinity {trinity_week}"
        elif sunday_season == 'Pre-Advent':
            advent_sunday_abs = date_to_days(year, 12, 25) + advent_sunday
            weeks_until_advent = (advent_sunday_abs - days) // 7
            if weeks_until_advent == 0:
                week_name = 'Advent 1'
            else:
                week_name = f"{weeks_until_advent} before Advent"
            weekday_reading_key = week_name
        elif sunday_season == 'Ordinary Time':
            # Map Ordinary Time to Epiphany N or Trinity N as appropriate
            # Use Epiphany N if before Lent, Trinity N if after Pentecost
            # Here, use Epiphany N for Pre-Lent/Ordinary Time before Lent
            weekno = max(1, 1 + (sunday_christmas_point - 12) // 7)
            week_name = render_week_name('Epiphany', weekno, sunday_easter_point)[0]
            weekday_reading_key = f"Epiphany {weekno}"
        else:
            week_name = sunday_season
            weekday_reading_key = week_name
        # Calculate Ash Wednesday (Easter - 46 days)
        ash_wednesday_days = easterday - 46
        pre_lent_start_sunday_days = ash_wednesday_days - 7*5
        ash_wednesday_date_tuple = add_delta_days(ash_wednesday_days)
        pre_lent_start_sunday_date_tuple = add_delta_days(pre_lent_start_sunday_days)
        ash_wednesday_date = date(*ash_wednesday_date_tuple)
        pre_lent_start_sunday_date = date(*pre_lent_start_sunday_date_tuple)
        # ---
        # Pre-Lent Weekday Reading Key Override
        #
        # The lectionary assigns week-based readings for Pre-Lent weekdays using keys like
        # '5 before Lent', '4 before Lent', ..., '1 before Lent'. However, Sundays only use
        # '2 before Lent' and '1 before Lent' as week names, because the Pre-Lent season is
        # defined as three Sundays before Lent, but weekday readings extend to five weeks.
        #
        # This override ensures that for the five weeks before Ash Wednesday, weekdays get
        # the correct 'N before Lent' reading key, matching the lectionary data. The override
        # only applies for n in 1..5; otherwise, the main logic is used.
        # ---
        if pre_lent_start_sunday_date <= week_start_sunday_date < ash_wednesday_date:
            n = ((ash_wednesday_days - week_start_sunday_days) // 7 + 1)
            if 1 <= n <= 5:
                override_weekday_reading_key = f"{n} before Lent"
            else:
                override_weekday_reading_key = None
        else:
            override_weekday_reading_key = None
        # At the end, override the weekday_reading_key if needed
        if override_weekday_reading_key:
            weekday_reading_key = override_weekday_reading_key
        
        # Fixed weekday readings override
        # For specific dates in the Christmas/Epiphany period, set weekday_reading_key to None
        # so that the ReadingsManager can use fixed weekday readings instead
        month_day = f"{f_date.month:02d}-{f_date.day:02d}"
        fixed_weekday_dates = {
            "12-29", "12-30", "12-31",  # Dec 29-31
            "01-02", "01-03", "01-04", "01-05",  # Jan 2-5
            "01-07", "01-08", "01-09", "01-10", "01-11", "01-12"  # Jan 7-12
        }
        if month_day in fixed_weekday_dates:
            weekday_reading_key = None
        
        return {
            'season': current_season,
            'week_name': week_name,
            'week_start_sunday': week_start_sunday_date,
            'weekday_reading_key': weekday_reading_key
        } 