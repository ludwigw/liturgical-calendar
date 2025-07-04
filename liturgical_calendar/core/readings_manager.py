"""
ReadingsManager class for handling liturgical readings selection.

This module provides a centralized way to manage and retrieve readings
for different liturgical dates, seasons, and cycles.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from liturgical_calendar.exceptions import ReadingsNotFoundError


class ReadingsManager:
    """
    Manages liturgical readings for different dates, seasons, and cycles.
    
    This class handles the selection of appropriate readings based on:
    - The liturgical date and season
    - The lectionary cycle (A, B, C for Sundays; 1, 2 for weekdays)
    - Whether it's a Sunday or weekday
    - Feast days and special occasions
    """
    
    def __init__(self):
        """Initialize the ReadingsManager."""
        # Import readings data here to avoid circular imports
        from ..data.readings_data import sunday_readings, weekday_readings, fixed_weekday_readings
        self.sunday_readings = sunday_readings
        self.weekday_readings = weekday_readings
        self.fixed_weekday_readings = fixed_weekday_readings
    
    def get_yearly_cycle(self, year: int) -> Tuple[str, int]:
        """
        Determine the lectionary cycle for the given year.
        
        Args:
            year: The year to determine the cycle for.
            
        Returns:
            A tuple of (sunday_cycle, weekday_cycle) where:
            - sunday_cycle is 'A', 'B', or 'C'
            - weekday_cycle is 1 or 2
        """
        sunday_cycle = ['A', 'B', 'C'][(year - 1) % 3]
        weekday_cycle = 1 if year % 2 == 0 else 2
        return sunday_cycle, weekday_cycle
    
    def get_sunday_readings(self, week: str, cycle: str) -> List[str]:
        """
        Get Sunday readings for a specific week and cycle.
        
        Args:
            week: The liturgical week (e.g., 'Advent 1', 'Proper 4')
            cycle: The lectionary cycle ('A', 'B', or 'C')
        
        Returns:
            List containing the readings for the week and cycle.
            Returns empty list if not found.
        """
        return self.sunday_readings.get(week, {}).get(cycle, [])
    
    def get_weekday_readings(self, weekday_reading: str, day_of_week: str, cycle: int) -> List[str]:
        """
        Get weekday readings for a specific week, day, and cycle.
        
        Args:
            weekday_reading: The liturgical week (e.g., 'Advent 1', 'Lent 1', 'Proper 6')
            day_of_week: The day of the week (e.g., 'Monday', 'Tuesday')
            cycle: The weekday cycle (1 or 2)
        
        Returns:
            List containing the readings for the weekday and cycle.
            Returns empty list if not found.
        """
        return self.weekday_readings.get(weekday_reading, {}).get(day_of_week, {}).get(str(cycle), [])
    
    def get_fixed_weekday_readings(self, date_str: str, cycle: int) -> List[str]:
        """
        Get fixed weekday readings for a specific date and cycle.
        
        Args:
            date_str: Date in 'YYYY-MM-DD' format
            cycle: The weekday cycle (1 or 2)
        
        Returns:
            List containing the fixed weekday readings for the date and cycle.
            Returns empty list if not found.
        """
        try:
            # Extract MM-DD from YYYY-MM-DD
            month_day = date_str[5:]  # Get MM-DD part
            return self.fixed_weekday_readings.get(month_day, {}).get(str(cycle), [])
        except (IndexError, KeyError):
            return []
    
    def get_feast_readings(self, feast_data: Dict) -> List[str]:
        """
        Get readings for a feast day.
        
        Args:
            feast_data: Dictionary containing feast information
            
        Returns:
            List containing the feast readings.
            Returns empty list if no readings found.
        """
        # Check if the feast has readings defined
        readings = feast_data.get('readings', [])
        if readings:
            return readings
        
        # If no readings in feast_data, try to look up from feast data structure
        feast_name = feast_data.get('name', '')
        if feast_name:
            # Import feast data here to avoid circular imports
            from ..data.feasts_data import feasts
            
            # Look through both easter and christmas feast data
            for feast_type in ['easter', 'christmas']:
                if feast_type in feasts:
                    for feast_key, feast_info in feasts[feast_type].items():
                        if feast_info.get('name') == feast_name:
                            feast_readings = feast_info.get('readings', [])
                            if feast_readings:
                                return feast_readings
        
        return []
    

    
    def get_readings_for_date(self, date_str: str, liturgical_info: Dict) -> List[str]:
        """
        Get readings for a specific date based on liturgical information.
        
        This method handles Sunday and weekday readings (not feast readings).
        Precedence order:
        1. Week-based readings (if date has a weekday_reading_key)
        2. Fixed weekday readings (if date is in fixed_weekday_readings and no week-based readings)
        3. Sunday readings (if date is a Sunday)
        
        Args:
            date_str: Date in 'YYYY-MM-DD' format
            liturgical_info: Dictionary containing liturgical information including:
                - 'week': The liturgical week
                - 'weekday_reading': The weekday reading (if applicable)
        
        Returns:
            List containing the readings for the date.
            Returns empty list if no readings found.
        """
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            year = date.year
            
            # Determine the lectionary cycle for the year
            sunday_cycle, weekday_cycle = self.get_yearly_cycle(year)
            
            # Check if the date is a Sunday
            if date.weekday() == 6:  # Sunday is represented by 6
                week = liturgical_info.get('week')
                if week:
                    return self.get_sunday_readings(week, sunday_cycle)
            else:
                # It's a weekday - check precedence order
                
                # 1. Use week-based system first
                weekday_reading = liturgical_info.get('weekday_reading')
                if weekday_reading is None:
                    weekday_reading = liturgical_info.get('week')
                if weekday_reading:
                    day_of_week = date.strftime('%A')  # Get the day of the week (e.g., 'Monday')
                    week_based_readings = self.get_weekday_readings(weekday_reading, day_of_week, weekday_cycle)
                    if week_based_readings:
                        return week_based_readings
                
                # 2. Check for fixed weekday readings as fallback
                fixed_readings = self.get_fixed_weekday_readings(date_str, weekday_cycle)
                if fixed_readings:
                    return fixed_readings
            
            return []
            
        except (ValueError, KeyError, TypeError) as e:
            raise ReadingsNotFoundError(f"Error getting readings for date {date_str}: {e}")
    
    def validate_readings_data(self, readings: Dict) -> bool:
        """
        Validate that readings data has the expected structure.
        
        Args:
            readings: Dictionary containing readings data
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(readings, dict):
            return False
        
        # Check if readings contain expected keys (Old Testament, Epistle, Gospel, Psalm)
        expected_keys = ['Old Testament', 'Epistle', 'Gospel', 'Psalm']
        for key in expected_keys:
            if key not in readings:
                return False
        
        return True
    
    def get_available_weeks(self) -> List[str]:
        """
        Get a list of all available liturgical weeks.
        
        Returns:
            List of week names available in the readings data
        """
        return list(self.sunday_readings.keys())
    
    def get_available_weekday_weeks(self) -> List[str]:
        """
        Get a list of all available weekday weeks.
        
        Returns:
            List of weekday week names available in the readings data
        """
        return list(self.weekday_readings.keys()) 