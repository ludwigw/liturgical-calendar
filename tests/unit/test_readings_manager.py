"""
Unit tests for ReadingsManager class.

Tests the functionality of the ReadingsManager class including:
- Yearly cycle calculation
- Sunday and weekday readings retrieval
- Date-based readings selection
- Data validation
- Error handling
"""

import unittest
from datetime import date
from unittest.mock import patch, MagicMock

from liturgical_calendar.core.readings_manager import ReadingsManager


class TestReadingsManager(unittest.TestCase):
    """Test cases for ReadingsManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock the readings data to avoid dependency on actual data
        self.mock_sunday_readings = {
            'Advent 1': {
                'A': ['Isaiah 2:1-5', 'Romans 13:11-14', 'Matthew 24:36-44', 'Psalm 122'],
                'B': ['Isaiah 64:1-9', '1 Corinthians 1:3-9', 'Mark 13:24-37', 'Psalm 80:1-8, 18-20'],
                'C': ['Jeremiah 33:14-16', '1 Thessalonians 3:9-13', 'Luke 21:25-36', 'Psalm 25:1-9']
            },
            'Christmas 1': {
                'A': ['Isaiah 63:7-9', 'Hebrews 2:10-18', 'Matthew 2:13-23', 'Psalm 148'],
                'B': ['Isaiah 61:10-62:3', 'Galatians 4:4-7', 'Luke 2:22-40', 'Psalm 148'],
                'C': ['1 Samuel 2:18-20, 26', 'Colossians 3:12-17', 'Luke 2:41-52', 'Psalm 148']
            }
        }
        
        self.mock_weekday_readings = {
            'Advent 1': {
                'Monday': {'1': ['Isaiah 25:1-9', 'Matthew 12:1-21'], '2': ['Isaiah 42:18-end', 'Revelation 19']},
                'Tuesday': {'1': ['Isaiah 26:1-13', 'Matthew 12:22-37'], '2': ['Isaiah 43:1-13', 'Revelation 20']}
            },
            'Lent 1': {
                'Monday': {'1': ['Genesis 41:25-45', 'Galations 3:23-4:7'], '2': ['Jeremiah 4:19-end', 'John 5:1-18']},
                'Tuesday': {'1': ['Genesis 41:46-42:5', 'Galations 4:8-20'], '2': ['Jeremiah 5:1-19', 'John 5:19-29']}
            }
        }
        
        # Create ReadingsManager with mocked data
        with patch('liturgical_calendar.readings_data.sunday_readings', self.mock_sunday_readings), \
             patch('liturgical_calendar.readings_data.weekday_readings', self.mock_weekday_readings):
            self.readings_manager = ReadingsManager()
    
    def test_get_yearly_cycle(self):
        """Test yearly cycle calculation for different years."""
        # Use production-derived values
        self.assertEqual(self.readings_manager.get_yearly_cycle(2023), ('A', 2))
        self.assertEqual(self.readings_manager.get_yearly_cycle(2024), ('B', 1))
        self.assertEqual(self.readings_manager.get_yearly_cycle(2025), ('C', 2))
        self.assertEqual(self.readings_manager.get_yearly_cycle(2026), ('A', 1))
        # Test edge cases
        self.assertEqual(self.readings_manager.get_yearly_cycle(1), ('A', 2))
        self.assertEqual(self.readings_manager.get_yearly_cycle(2000), ('B', 1))
        self.assertEqual(self.readings_manager.get_yearly_cycle(2100), ('C', 1))
    
    def test_get_sunday_readings_valid(self):
        """Test getting Sunday readings for valid week and cycle."""
        # Test Advent 1, Cycle A
        readings = self.readings_manager.get_sunday_readings('Advent 1', 'A')
        expected = ['Isaiah 2:1-5', 'Romans 13:11-14', 'Matthew 24:36-44', 'Psalm 122']
        self.assertEqual(readings, expected)
        
        # Test Christmas 1, Cycle B
        readings = self.readings_manager.get_sunday_readings('Christmas 1', 'B')
        expected = ['Isaiah 61:10-62:3', 'Galatians 4:4-7', 'Luke 2:22-40', 'Psalm 148']
        self.assertEqual(readings, expected)
    
    def test_get_sunday_readings_invalid_week(self):
        """Test getting Sunday readings for invalid week."""
        readings = self.readings_manager.get_sunday_readings('Invalid Week', 'A')
        self.assertEqual(readings, {})
    
    def test_get_sunday_readings_invalid_cycle(self):
        """Test getting Sunday readings for invalid cycle."""
        readings = self.readings_manager.get_sunday_readings('Advent 1', 'D')
        self.assertEqual(readings, {})
    
    def test_get_weekday_readings_valid(self):
        """Test getting weekday readings for valid parameters."""
        # Test Advent 1, Monday, Cycle 1
        readings = self.readings_manager.get_weekday_readings('Advent 1', 'Monday', 1)
        expected = ['Isaiah 25:1-9', 'Matthew 12:1-21']
        self.assertEqual(readings, expected)
        
        # Test Lent 1, Tuesday, Cycle 2
        readings = self.readings_manager.get_weekday_readings('Lent 1', 'Tuesday', 2)
        expected = ['Jeremiah 5:1-19', 'John 5:19-29']
        self.assertEqual(readings, expected)
    
    def test_get_weekday_readings_invalid_week(self):
        """Test getting weekday readings for invalid week."""
        readings = self.readings_manager.get_weekday_readings('Invalid Week', 'Monday', 1)
        self.assertEqual(readings, {})
    
    def test_get_weekday_readings_invalid_day(self):
        """Test getting weekday readings for invalid day."""
        readings = self.readings_manager.get_weekday_readings('Advent 1', 'InvalidDay', 1)
        self.assertEqual(readings, {})
    
    def test_get_weekday_readings_invalid_cycle(self):
        """Test getting weekday readings for invalid cycle."""
        readings = self.readings_manager.get_weekday_readings('Advent 1', 'Monday', 3)
        self.assertEqual(readings, {})
    
    def test_get_readings_for_date_sunday(self):
        """Test getting readings for a Sunday date."""
        liturgical_info = {'week': 'Advent 1'}
        readings = self.readings_manager.get_readings_for_date('2024-12-01', liturgical_info)
        # 2024 is cycle B, so we should get cycle B readings
        expected = ['Isaiah 64:1-9', '1 Corinthians 1:3-9', 'Mark 13:24-37', 'Psalm 80:1-8, 18-20']
        self.assertEqual(readings, expected)
    
    def test_get_readings_for_date_weekday(self):
        """Test getting readings for a weekday date."""
        liturgical_info = {'weekday_reading': 'Advent 1'}
        readings = self.readings_manager.get_readings_for_date('2024-12-02', liturgical_info)  # Monday
        # 2024 is cycle 1 for weekdays, so we should get cycle 1 readings
        expected = ['Isaiah 25:1-9', 'Matthew 12:1-21']
        self.assertEqual(readings, expected)
    
    def test_get_readings_for_date_weekday_fallback(self):
        """Test getting readings for weekday when weekday_reading is None."""
        liturgical_info = {'week': 'Advent 1', 'weekday_reading': None}
        readings = self.readings_manager.get_readings_for_date('2024-12-02', liturgical_info)  # Monday
        # Should fall back to 'week' when 'weekday_reading' is None
        expected = ['Isaiah 25:1-9', 'Matthew 12:1-21']
        self.assertEqual(readings, expected)
    
    def test_get_readings_for_date_no_week_info(self):
        """Test getting readings when no week information is provided."""
        liturgical_info = {}
        readings = self.readings_manager.get_readings_for_date('2024-12-01', liturgical_info)
        self.assertEqual(readings, {})
    
    def test_get_readings_for_date_invalid_date(self):
        """Test getting readings for invalid date format."""
        liturgical_info = {'week': 'Advent 1'}
        readings = self.readings_manager.get_readings_for_date('invalid-date', liturgical_info)
        self.assertEqual(readings, {})
    
    def test_get_readings_for_date_missing_liturgical_info(self):
        """Test getting readings when liturgical_info is missing required keys."""
        liturgical_info = {'some_other_key': 'value'}
        readings = self.readings_manager.get_readings_for_date('2024-12-01', liturgical_info)
        self.assertEqual(readings, {})
    
    def test_get_feast_readings(self):
        """Test getting feast readings (currently returns empty dict)."""
        feast_data = {'name': 'Christmas Day', 'prec': 1}
        readings = self.readings_manager.get_feast_readings(feast_data)
        self.assertEqual(readings, {})
    
    def test_validate_readings_data_valid(self):
        """Test validation of valid readings data."""
        valid_readings = {
            'Old Testament': ['Isaiah 2:1-5'],
            'Epistle': ['Romans 13:11-14'],
            'Gospel': ['Matthew 24:36-44'],
            'Psalm': ['Psalm 122']
        }
        self.assertTrue(self.readings_manager.validate_readings_data(valid_readings))
    
    def test_validate_readings_data_invalid_type(self):
        """Test validation of invalid readings data type."""
        self.assertFalse(self.readings_manager.validate_readings_data("not a dict"))
        self.assertFalse(self.readings_manager.validate_readings_data([]))
        self.assertFalse(self.readings_manager.validate_readings_data(None))
    
    def test_validate_readings_data_missing_keys(self):
        """Test validation of readings data with missing keys."""
        invalid_readings = {
            'Old Testament': ['Isaiah 2:1-5'],
            'Epistle': ['Romans 13:11-14']
            # Missing 'Gospel' and 'Psalm'
        }
        self.assertFalse(self.readings_manager.validate_readings_data(invalid_readings))
    
    def test_get_available_weeks(self):
        """Test getting list of available weeks."""
        weeks = self.readings_manager.get_available_weeks()
        expected = ['Advent 1', 'Christmas 1']
        self.assertEqual(weeks, expected)
    
    def test_get_available_weekday_weeks(self):
        """Test getting list of available weekday weeks."""
        weekday_weeks = self.readings_manager.get_available_weekday_weeks()
        expected = ['Advent 1', 'Lent 1']
        self.assertEqual(weekday_weeks, expected)
    
    def test_edge_cases_cycle_calculation(self):
        """Test edge cases for cycle calculation."""
        # Test year 0 (should handle gracefully)
        self.assertEqual(self.readings_manager.get_yearly_cycle(0), ('C', 1))
        # Test negative year (should handle gracefully)
        self.assertEqual(self.readings_manager.get_yearly_cycle(-1), ('B', 2))
        # Test very large year
        self.assertEqual(self.readings_manager.get_yearly_cycle(9999), ('C', 2))
    
    def test_readings_data_structure(self):
        """Test that the readings data structure is maintained."""
        # Test that Sunday readings have the expected structure
        advent_1_readings = self.readings_manager.sunday_readings['Advent 1']
        self.assertIn('A', advent_1_readings)
        self.assertIn('B', advent_1_readings)
        self.assertIn('C', advent_1_readings)
        
        # Test that weekday readings have the expected structure
        advent_1_weekday = self.readings_manager.weekday_readings['Advent 1']
        self.assertIn('Monday', advent_1_weekday)
        self.assertIn('Tuesday', advent_1_weekday)
        monday_readings = advent_1_weekday['Monday']
        self.assertIn('1', monday_readings)
        self.assertIn('2', monday_readings)


if __name__ == '__main__':
    unittest.main() 