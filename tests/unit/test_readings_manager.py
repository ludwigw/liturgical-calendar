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
from unittest.mock import patch

from liturgical_calendar.exceptions import ReadingsNotFoundError


class TestReadingsManager(unittest.TestCase):
    """Test cases for ReadingsManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Expanded mock data for sunday_readings, weekday_readings, and fixed_weekday_readings
        self.mock_sunday_readings = {
            "Advent 1": {
                "A": [
                    "Isaiah 2:1-5",
                    "Romans 13:11-14",
                    "Matthew 24:36-44",
                    "Psalm 122",
                ],
                "B": ["mock"],
                "C": ["mock"],
            },
            "Christmas 1": {
                "A": [
                    "Isaiah 63:7-9",
                    "Hebrews 2:10-18",
                    "Matthew 2:13-23",
                    "Psalm 148",
                ],
                "B": [
                    "Isaiah 61:10-62:3",
                    "Galatians 4:4-7",
                    "Luke 2:22-40",
                    "Psalm 148",
                ],
                "C": [
                    "1 Samuel 2:18-20, 26",
                    "Colossians 3:12-17",
                    "Luke 2:41-52",
                    "Psalm 148",
                ],
            },
            "Epiphany 1": {
                "A": [
                    "Isaiah 61:10-62:3",
                    "Galatians 4:4-7",
                    "Luke 2:22-40",
                    "Psalm 148",
                ],
                "B": ["mock"],
                "C": ["mock"],
            },
            "Lent 1": {
                "A": [
                    "Genesis 2:15-17; 3:1-7",
                    "Romans 5:12-19",
                    "Matthew 4:1-11",
                    "Psalm 32",
                ],
                "B": [
                    "Genesis 9:8-17",
                    "1 Peter 3:18-22",
                    "Mark 1:9-15",
                    "Psalm 25:1-10",
                ],
                "C": [
                    "Deuteronomy 26:1-11",
                    "Romans 10:8b-13",
                    "Luke 4:1-13",
                    "Psalm 91:1-2, 9-16",
                ],
            },
        }
        self.mock_weekday_readings = {
            "Advent 1": {
                "Monday": {
                    "1": ["Isaiah 25:1-9", "Matthew 12:1-21"],
                    "2": ["Isaiah 42:18-end", "Revelation 19"],
                },
                "Tuesday": {
                    "1": ["Isaiah 26:1-13", "Matthew 12:22-37"],
                    "2": ["Isaiah 43:1-13", "Revelation 20"],
                },
            },
            "Lent 1": {
                "Monday": {
                    "1": ["Genesis 41:25-45", "Galations 3:23-4:7"],
                    "2": ["Jeremiah 4:19-end", "John 5:1-18"],
                },
                "Tuesday": {
                    "1": ["Genesis 41:46-42:5", "Galations 4:8-20"],
                    "2": ["Jeremiah 5:1-19", "John 5:19-29"],
                },
            },
            "Epiphany 1": {
                "Monday": {
                    "1": ["Epiphany 1 Monday Reading 1", "Epiphany 1 Monday Reading 2"],
                    "2": ["mock"],
                }
            },
        }
        self.mock_fixed_weekday_readings = {
            "12-29": {
                "1": ["1 John 2:3-11", "John 21:19-25"],
                "2": ["2 Samuel 7:18-29", "Luke 1:67-79"],
            },
            "12-30": {
                "1": ["1 John 2:3-11", "John 21:19-25"],
                "2": ["2 Samuel 7:18-29", "Luke 1:67-79"],
            },
            "01-02": {
                "1": ["1 John 2:22-28", "John 1:19-34"],
                "2": ["1 Kings 8:1-13", "Luke 2:41-52"],
            },
            "01-07": {"2": ["1 Kings 8:41-53", "Luke 4:14-21"]},
            "01-08": {
                "1": ["Fixed Jan 8 Reading 1", "Fixed Jan 8 Reading 2"],
                "2": ["Fixed Jan 8 Reading 1", "Fixed Jan 8 Reading 2"],
            },
        }
        # Patch the data modules
        patcher1 = patch(
            "liturgical_calendar.data.readings_data.sunday_readings",
            self.mock_sunday_readings,
        )
        patcher2 = patch(
            "liturgical_calendar.data.readings_data.weekday_readings",
            self.mock_weekday_readings,
        )
        patcher3 = patch(
            "liturgical_calendar.data.readings_data.fixed_weekday_readings",
            self.mock_fixed_weekday_readings,
        )
        self.addCleanup(patcher1.stop)
        self.addCleanup(patcher2.stop)
        self.addCleanup(patcher3.stop)
        patcher1.start()
        patcher2.start()
        patcher3.start()
        from liturgical_calendar.core.readings_manager import ReadingsManager

        self.readings_manager = ReadingsManager()

    def test_get_yearly_cycle(self):
        """Test yearly cycle calculation."""
        # Test even years (cycle 1)
        sunday_cycle, weekday_cycle = self.readings_manager.get_yearly_cycle(2024)
        self.assertEqual(sunday_cycle, "B")
        self.assertEqual(weekday_cycle, 1)

        sunday_cycle, weekday_cycle = self.readings_manager.get_yearly_cycle(2026)
        self.assertEqual(sunday_cycle, "A")
        self.assertEqual(weekday_cycle, 1)

        # Test odd years (cycle 2)
        sunday_cycle, weekday_cycle = self.readings_manager.get_yearly_cycle(2023)
        self.assertEqual(sunday_cycle, "A")
        self.assertEqual(weekday_cycle, 2)

        sunday_cycle, weekday_cycle = self.readings_manager.get_yearly_cycle(2025)
        self.assertEqual(sunday_cycle, "C")
        self.assertEqual(weekday_cycle, 2)

    def test_get_sunday_readings_valid(self):
        """Test getting Sunday readings for valid week and cycle."""
        # Test Advent 1, Cycle A
        readings = self.readings_manager.get_sunday_readings("Advent 1", "A")
        expected = ["Isaiah 2:1-5", "Romans 13:11-14", "Matthew 24:36-44", "Psalm 122"]
        self.assertEqual(readings, expected)

        # Test Christmas 1, Cycle B
        readings = self.readings_manager.get_sunday_readings("Christmas 1", "B")
        expected = ["Isaiah 61:10-62:3", "Galatians 4:4-7", "Luke 2:22-40", "Psalm 148"]
        self.assertEqual(readings, expected)

    def test_get_sunday_readings_invalid_week(self):
        """Test getting Sunday readings for invalid week."""
        readings = self.readings_manager.get_sunday_readings("Invalid Week", "A")
        self.assertEqual(readings, [])

    def test_get_sunday_readings_invalid_cycle(self):
        """Test getting Sunday readings for invalid cycle."""
        readings = self.readings_manager.get_sunday_readings("Advent 1", "D")
        self.assertEqual(readings, [])

    def test_get_weekday_readings_valid(self):
        """Test getting weekday readings for valid parameters."""
        # Test Advent 1, Monday, Cycle 1
        readings = self.readings_manager.get_weekday_readings("Advent 1", "Monday", 1)
        expected = ["Isaiah 25:1-9", "Matthew 12:1-21"]
        self.assertEqual(readings, expected)

        # Test Lent 1, Tuesday, Cycle 2
        readings = self.readings_manager.get_weekday_readings("Lent 1", "Tuesday", 2)
        expected = ["Jeremiah 5:1-19", "John 5:19-29"]
        self.assertEqual(readings, expected)

    def test_get_weekday_readings_invalid_week(self):
        """Test getting weekday readings for invalid week."""
        readings = self.readings_manager.get_weekday_readings(
            "Invalid Week", "Monday", 1
        )
        self.assertEqual(readings, [])

    def test_get_weekday_readings_invalid_day(self):
        """Test getting weekday readings for invalid day."""
        readings = self.readings_manager.get_weekday_readings(
            "Advent 1", "InvalidDay", 1
        )
        self.assertEqual(readings, [])

    def test_get_weekday_readings_invalid_cycle(self):
        """Test getting weekday readings for invalid cycle."""
        readings = self.readings_manager.get_weekday_readings("Advent 1", "Monday", 3)
        self.assertEqual(readings, [])

    def test_get_readings_for_date_sunday(self):
        """Test getting readings for a Sunday date."""
        liturgical_info = {"week": "Advent 1"}
        readings = self.readings_manager.get_readings_for_date(
            "2024-12-01", liturgical_info
        )
        # 2024 is cycle B, so we should get cycle B readings
        expected = [
            "Isaiah 64:1-9",
            "1 Corinthians 1:3-9",
            "Mark 13:24-37",
            "Psalm 80:1-8, 18-20",
        ]
        self.assertEqual(readings, expected)

    def test_get_readings_for_date_weekday(self):
        """Test getting readings for a weekday date."""
        liturgical_info = {"weekday_reading": "Advent 1"}
        readings = self.readings_manager.get_readings_for_date(
            "2024-12-02", liturgical_info
        )  # Monday
        # 2024 is cycle 1 for weekdays, so we should get cycle 1 readings
        expected = ["Isaiah 25:1-9", "Matthew 12:1-21"]
        self.assertEqual(readings, expected)

    def test_get_readings_for_date_weekday_fallback(self):
        """Test getting readings for weekday when weekday_reading is None."""
        liturgical_info = {"week": "Advent 1", "weekday_reading": None}
        readings = self.readings_manager.get_readings_for_date(
            "2024-12-02", liturgical_info
        )  # Monday
        # Should fall back to 'week' when 'weekday_reading' is None
        expected = ["Isaiah 25:1-9", "Matthew 12:1-21"]
        self.assertEqual(readings, expected)

    def test_get_readings_for_date_no_week_info(self):
        """Test getting readings when no week information is provided."""
        readings = self.readings_manager.get_readings_for_date("2024-01-01", {})
        self.assertEqual(readings, [])

    def test_get_readings_for_date_invalid_date(self):
        """Test getting readings for invalid date format."""
        with self.assertRaises(ReadingsNotFoundError):
            self.readings_manager.get_readings_for_date("invalid-date", {})

    def test_get_readings_for_date_missing_liturgical_info(self):
        """Test getting readings when liturgical_info is missing required keys."""
        readings = self.readings_manager.get_readings_for_date(
            "2024-01-01", {"foo": "bar"}
        )
        self.assertEqual(readings, [])

    def test_get_feast_readings(self):
        """Test getting feast readings (currently returns empty list)."""
        readings = self.readings_manager.get_feast_readings({})
        self.assertEqual(readings, [])

    def test_validate_readings_data_valid(self):
        """Test validation of valid readings data."""
        valid_readings = {
            "Old Testament": ["Isaiah 2:1-5"],
            "Epistle": ["Romans 13:11-14"],
            "Gospel": ["Matthew 24:36-44"],
            "Psalm": ["Psalm 122"],
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
            "Old Testament": ["Isaiah 2:1-5"],
            "Epistle": ["Romans 13:11-14"],
            # Missing 'Gospel' and 'Psalm'
        }
        self.assertFalse(self.readings_manager.validate_readings_data(invalid_readings))

    def test_get_available_weeks(self):
        """Test getting list of available weeks."""
        weeks = self.readings_manager.get_available_weeks()
        expected = ["Advent 1", "Christmas 1", "Epiphany 1", "Lent 1"]
        self.assertEqual(sorted(weeks), sorted(expected))

    def test_get_available_weekday_weeks(self):
        """Test getting list of available weekday weeks."""
        weekday_weeks = self.readings_manager.get_available_weekday_weeks()
        expected = ["Advent 1", "Lent 1", "Epiphany 1"]
        self.assertEqual(sorted(weekday_weeks), sorted(expected))

    def test_edge_cases_cycle_calculation(self):
        """Test edge cases for cycle calculation."""
        # Test year 0 (should handle gracefully)
        self.assertEqual(self.readings_manager.get_yearly_cycle(0), ("C", 1))
        # Test negative year (should handle gracefully)
        self.assertEqual(self.readings_manager.get_yearly_cycle(-1), ("B", 2))
        # Test very large year
        self.assertEqual(self.readings_manager.get_yearly_cycle(9999), ("C", 2))

    def test_readings_data_structure(self):
        """Test that the readings data structure is maintained."""
        # Test that Sunday readings have the expected structure
        advent_1_readings = self.readings_manager.sunday_readings["Advent 1"]
        self.assertIn("A", advent_1_readings)
        self.assertIn("B", advent_1_readings)
        self.assertIn("C", advent_1_readings)

        # Test that weekday readings have the expected structure
        advent_1_weekday = self.readings_manager.weekday_readings["Advent 1"]
        self.assertIn("Monday", advent_1_weekday)
        self.assertIn("Tuesday", advent_1_weekday)
        monday_readings = advent_1_weekday["Monday"]
        self.assertIn("1", monday_readings)
        self.assertIn("2", monday_readings)

    def test_get_fixed_weekday_readings(self):
        """Test fixed weekday readings retrieval."""
        # Test Dec 29 (cycle 1)
        readings = self.readings_manager.get_fixed_weekday_readings("2024-12-29", 1)
        self.assertEqual(readings, ["1 John 2:3-11", "John 21:19-25"])

        # Test Dec 29 (cycle 2)
        readings = self.readings_manager.get_fixed_weekday_readings("2023-12-29", 2)
        self.assertEqual(readings, ["2 Samuel 7:18-29", "Luke 1:67-79"])

        # Test Jan 2 (cycle 1)
        readings = self.readings_manager.get_fixed_weekday_readings("2024-01-02", 1)
        self.assertEqual(readings, ["1 John 2:22-28", "John 1:19-34"])

        # Test Jan 7 (cycle 2)
        readings = self.readings_manager.get_fixed_weekday_readings("2023-01-07", 2)
        self.assertEqual(readings, ["1 Kings 8:41-53", "Luke 4:14-21"])

        # Test non-fixed date (should return empty list)
        readings = self.readings_manager.get_fixed_weekday_readings("2024-01-15", 1)
        self.assertEqual(readings, [])

    def test_get_readings_for_date_fixed_weekday_precedence(self):
        """Test that fixed weekday readings take precedence over week-based readings."""
        # Test Dec 29, 2024 (Monday, cycle 1)
        liturgical_info = {
            "week": "Christmas 1",
            "weekday_reading": "Christmas 1",
            "name": None,  # Not a feast
        }
        readings = self.readings_manager.get_readings_for_date(
            "2024-12-30", liturgical_info
        )  # Monday
        self.assertEqual(readings, ["1 John 2:3-11", "John 21:19-25"])

        # Test Jan 2, 2023 (Monday, cycle 2)
        liturgical_info = {
            "week": "Christmas 2",
            "weekday_reading": "Christmas 2",
            "name": None,  # Not a feast
        }
        readings = self.readings_manager.get_readings_for_date(
            "2023-01-02", liturgical_info
        )
        # Should get fixed weekday readings, not week-based readings
        self.assertEqual(readings, ["1 Kings 8:1-13", "Luke 2:41-52"])

    def test_get_readings_for_date_week_based_fallback(self):
        """Test that week-based readings are used as fallback for non-fixed dates."""
        # Test a regular weekday that should use week-based readings
        liturgical_info = {
            "week": "Epiphany 1",
            "weekday_reading": "Epiphany 1",
            "name": None,  # Not a feast
        }
        readings = self.readings_manager.get_readings_for_date(
            "2024-01-15", liturgical_info
        )
        # Should get week-based readings (not empty)
        self.assertGreater(len(readings), 0)

    def test_get_readings_for_date_sunday(self):
        """Test Sunday readings retrieval."""
        liturgical_info = {"week": "Epiphany 1", "name": None}
        readings = self.readings_manager.get_readings_for_date(
            "2024-01-07", liturgical_info
        )  # Sunday
        # Should get Sunday readings for Epiphany 1
        self.assertGreater(len(readings), 0)

    def test_epiphany1_precedence_over_fixed_weekday_readings(self):
        """If Epiphany 1 starts early (e.g., 2024), Jan 8 should use Epiphany 1 weekday readings, not fixed readings."""
        # 2024-01-08 is a Monday, Epiphany 1 is Jan 7, 2024
        liturgical_info = {
            "week": "Epiphany 1",
            "weekday_reading": "Epiphany 1",
            "name": None,
        }
        readings = self.readings_manager.get_readings_for_date(
            "2024-01-08", liturgical_info
        )
        # Should get Epiphany 1 weekday readings (not fixed readings)
        expected = ["Epiphany 1 Monday Reading 1", "Epiphany 1 Monday Reading 2"]
        self.assertEqual(readings, expected)

    def test_fixed_weekday_readings_when_epiphany1_is_late(self):
        """If Epiphany 1 starts late (e.g., 2025), Jan 8 should use fixed weekday readings, not Epiphany 1 readings."""
        # 2025-01-08 is a Wednesday, Epiphany 1 is Jan 12, 2025
        liturgical_info = {
            "week": "Christmas 2",
            "weekday_reading": "Christmas 2",
            "name": None,
        }
        readings = self.readings_manager.get_readings_for_date(
            "2025-01-08", liturgical_info
        )
        # Should get fixed weekday readings
        expected = ["Fixed Jan 8 Reading 1", "Fixed Jan 8 Reading 2"]
        self.assertEqual(readings, expected)


if __name__ == "__main__":
    unittest.main()
