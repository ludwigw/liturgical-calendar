"""
ReadingsManager class for handling liturgical readings selection.

This module provides a centralized way to manage and retrieve readings
for different liturgical dates, seasons, and cycles.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple


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
        from ..data.readings_data import sunday_readings, weekday_readings
        self.sunday_readings = sunday_readings
        self.weekday_readings = weekday_readings
    
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
    
    def get_sunday_readings(self, week: str, cycle: str) -> Dict[str, List[str]]:
        """
        Get Sunday readings for a specific week and cycle.
        
        Args:
            week: The liturgical week (e.g., 'Advent 1', 'Proper 4')
            cycle: The lectionary cycle ('A', 'B', or 'C')
            
        Returns:
            Dictionary containing the readings for the week and cycle.
            Returns empty dict if not found.
        """
        return self.sunday_readings.get(week, {}).get(cycle, {})
    
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
    
    def get_feast_readings(self, feast_data: Dict) -> Dict[str, List[str]]:
        """
        Get readings for a feast day.
        
        Args:
            feast_data: Dictionary containing feast information
            
        Returns:
            Dictionary containing the feast readings.
            Returns empty dict if no readings found.
        """
        # This method can be extended to handle feast-specific readings
        # For now, return empty dict as feast readings are handled elsewhere
        return {}
    
    def get_readings_for_date(self, date_str: str, liturgical_info: Dict) -> List[str]:
        """
        Get readings for a specific date based on liturgical information.
        
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
                # It's a weekday
                weekday_reading = liturgical_info.get('weekday_reading')
                if weekday_reading is None:
                    weekday_reading = liturgical_info.get('week')
                
                if weekday_reading:
                    day_of_week = date.strftime('%A')  # Get the day of the week (e.g., 'Monday')
                    return self.get_weekday_readings(weekday_reading, day_of_week, weekday_cycle)
            
            return []
            
        except (ValueError, KeyError, TypeError) as e:
            # Log error in a production environment
            print(f"Error getting readings for date {date_str}: {e}")
            return []
    
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