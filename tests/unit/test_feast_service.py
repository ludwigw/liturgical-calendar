"""
Tests for the FeastService class.

This module tests the FeastService's ability to orchestrate feast-related
operations and coordinate between different components.
"""

import unittest
from datetime import date
from unittest.mock import Mock, patch

from liturgical_calendar.core.readings_manager import ReadingsManager
from liturgical_calendar.core.season_calculator import SeasonCalculator
from liturgical_calendar.services.feast_service import FeastService


class TestFeastService(unittest.TestCase):
    """Test cases for the FeastService class."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_season_calculator = Mock(spec=SeasonCalculator)
        self.mock_readings_manager = Mock(spec=ReadingsManager)
        self.feast_service = FeastService(
            season_calculator=self.mock_season_calculator,
            readings_manager=self.mock_readings_manager,
        )

    def test_init_with_dependencies(self):
        """Test initialization with injected dependencies."""
        service = FeastService(
            season_calculator=self.mock_season_calculator,
            readings_manager=self.mock_readings_manager,
        )

        self.assertEqual(service.season_calculator, self.mock_season_calculator)
        self.assertEqual(service.readings_manager, self.mock_readings_manager)

    def test_init_without_dependencies(self):
        """Test initialization without injected dependencies."""
        with patch(
            "liturgical_calendar.services.feast_service.SeasonCalculator"
        ) as mock_calc:
            with patch(
                "liturgical_calendar.services.feast_service.ReadingsManager"
            ) as mock_readings:
                FeastService()

                mock_calc.assert_called_once()
                mock_readings.assert_called_once()

    @patch("liturgical_calendar.funcs.get_advent_sunday")
    def test_get_complete_feast_info_basic(self, mock_advent):
        """Test basic feast info retrieval."""
        # Mock dependencies
        mock_advent.return_value = 50

        # Mock season calculator methods
        self.mock_season_calculator.determine_season.return_value = "Easter"
        self.mock_season_calculator.week_info.return_value = {
            "season": "Easter",
            "week_name": "Easter 2",
            "week_start_sunday": date(2023, 4, 16),
            "weekday_reading_key": "Easter 2",
        }

        # Mock readings manager
        self.mock_readings_manager.get_readings_for_date.return_value = {
            "gospel": "John 20:19-31",
            "epistle": "1 Peter 1:3-9",
        }

        # Mock feast data - return Easter feast only for easter lookup, None for christmas lookup
        with patch(
            "liturgical_calendar.services.feast_service.get_liturgical_feast"
        ) as mock_feast:

            def mock_feast_side_effect(relative_to, pointer):
                if relative_to == "easter" and pointer == 0:  # Easter Sunday
                    return {"name": "Easter", "prec": 9, "type": "Principal Feast"}
                else:
                    return None

            mock_feast.side_effect = mock_feast_side_effect

            result = self.feast_service.get_complete_feast_info(
                "2023-04-09"
            )  # Easter Sunday

        # Verify the result - should be Easter feast
        self.assertEqual(result["name"], "Easter")
        self.assertEqual(result["season"], "Easter")
        self.assertEqual(result["colour"], "white")
        self.assertIn("readings", result)
        self.assertEqual(result["date"], date(2023, 4, 9))

    def test_validate_feast_data_valid(self):
        """Test validation of valid feast data."""
        valid_data = {"name": "Test Feast", "prec": 1, "colour": "white"}

        self.assertTrue(self.feast_service.validate_feast_data(valid_data))

    def test_validate_feast_data_invalid(self):
        """Test validation of invalid feast data."""
        invalid_data = {
            "prec": 1,
            "colour": "white",
            # Missing 'name' field
        }

        self.assertFalse(self.feast_service.validate_feast_data(invalid_data))

    def test_validate_feast_data_empty(self):
        """Test validation of empty feast data."""
        self.assertFalse(self.feast_service.validate_feast_data({}))

    @patch("liturgical_calendar.funcs.get_advent_sunday")
    def test_get_complete_feast_info_sunday(self, mock_advent):
        """Test feast info for a Sunday."""
        # Mock dependencies
        mock_advent.return_value = 50

        # Mock season calculator
        self.mock_season_calculator.determine_season.return_value = "Easter"
        self.mock_season_calculator.week_info.return_value = {
            "season": "Easter",
            "week_name": "Easter 2",
            "week_start_sunday": date(2023, 4, 23),
            "weekday_reading_key": "Easter 2",
        }

        # Mock readings manager
        self.mock_readings_manager.get_readings_for_date.return_value = {
            "gospel": "John 20:19-31"
        }

        # Mock feast data - no specific feast for today or yesterday
        with patch(
            "liturgical_calendar.services.feast_service.get_liturgical_feast"
        ) as mock_feast:

            def mock_feast_side_effect(relative_to, pointer):
                return None

            mock_feast.side_effect = mock_feast_side_effect
            result = self.feast_service.get_complete_feast_info(
                "2023-04-23"
            )  # Regular Sunday after Easter

        # Should have Easter 2 as the feast name (week name for Sunday)
        self.assertEqual(result["name"], "Easter 2")
        self.assertEqual(result["prec"], 5)

    @patch("liturgical_calendar.funcs.get_easter")
    @patch("liturgical_calendar.funcs.date_to_days")
    @patch("liturgical_calendar.funcs.get_advent_sunday")
    def test_get_complete_feast_info_transferred(
        self, mock_advent, mock_date_to_days, mock_easter
    ):
        """Test feast info with transferred feast."""
        # Mock dependencies
        mock_easter.return_value = (4, 16)
        mock_date_to_days.side_effect = [100, 105]
        mock_advent.return_value = 50

        # Mock season calculator
        self.mock_season_calculator.determine_season.return_value = "Easter"
        self.mock_season_calculator.week_info.return_value = {
            "season": "Easter",
            "week_name": "Easter 2",
            "week_start_sunday": date(2023, 4, 25),
            "weekday_reading_key": "Easter 2",
        }

        # Mock readings manager
        self.mock_readings_manager.get_readings_for_date.return_value = {
            "gospel": "John 20:19-31"
        }

        # Mock feast data for transferred feast
        with patch(
            "liturgical_calendar.services.feast_service.get_liturgical_feast"
        ) as mock_feast:
            mock_feast.return_value = {"name": "St. Mark", "prec": 2, "colour": "red"}

            result = self.feast_service.get_complete_feast_info(
                "2023-04-25", transferred=True
            )

        # Should return the transferred feast
        self.assertEqual(result["name"], "St. Mark")
        self.assertEqual(result["prec"], 2)

    def test_get_season_url(self):
        """Test getting season URLs."""
        urls = {
            "Advent": "https://en.wikipedia.org/wiki/Advent",
            "Christmas": "https://en.wikipedia.org/wiki/Christmastide",
            "Lent": "https://en.wikipedia.org/wiki/Lent",
            "Easter": "https://en.wikipedia.org/wiki/Eastertide",
            "Unknown": "https://en.wikipedia.org/wiki/Ordinary_Time",
        }

        for season, expected_url in urls.items():
            url = self.feast_service._get_season_url(season)
            self.assertEqual(url, expected_url)

    def test_normalize_weekno(self):
        """Test week number normalization."""
        # Test valid week number
        self.assertEqual(self.feast_service._normalize_weekno(5, "Easter"), 5)

        # Test None week number for non-special seasons
        self.assertIsNone(self.feast_service._normalize_weekno(None, "Ordinary Time"))

        # Test None week number for special seasons
        self.assertIsNone(self.feast_service._normalize_weekno(None, "Lent"))

        # Test zero week number
        self.assertIsNone(self.feast_service._normalize_weekno(0, "Easter"))

    def test_determine_colour(self):
        """Test liturgical color determination."""
        # Test rose Sundays
        result = {"name": "Advent 3"}
        self.assertEqual(
            self.feast_service._determine_colour(result, "Advent", 0, 0), "rose"
        )

        result = {"name": "Lent 4"}
        self.assertEqual(
            self.feast_service._determine_colour(result, "Lent", 0, 0), "rose"
        )

        # Test feast with existing color
        result = {"name": "Test Feast", "colour": "red"}
        self.assertEqual(
            self.feast_service._determine_colour(result, "Easter", 0, 0), "red"
        )

        # Test martyr feast (prec > 4 and not 5)
        result = {"name": "St. Stephen", "prec": 6, "martyr": True}
        self.assertEqual(
            self.feast_service._determine_colour(result, "Christmas", 0, 0), "red"
        )

        # Test regular feast
        result = {"name": "St. John", "prec": 6}
        self.assertEqual(
            self.feast_service._determine_colour(result, "Christmas", 0, 0), "white"
        )

        # Test season color
        result = {"name": "Sunday", "prec": 5}
        self.assertEqual(
            self.feast_service._determine_colour(result, "Advent", 0, 0), "purple"
        )
        self.assertEqual(
            self.feast_service._determine_colour(result, "Easter", 0, 0), "white"
        )
        self.assertEqual(
            self.feast_service._determine_colour(result, "Ordinary Time", 0, 0), "green"
        )

    def test_get_colour_code(self):
        """Test color code retrieval."""
        color_codes = {
            "white": "#FFFFFF",
            "red": "#FF0000",
            "green": "#00FF00",
            "purple": "#800080",
            "rose": "#FFB6C1",
            "unknown": "#000000",
        }

        for color, expected_code in color_codes.items():
            code = self.feast_service._get_colour_code(color)
            self.assertEqual(code, expected_code)

    def test_apply_precedence_rules_normal(self):
        """Test precedence rules for normal feasts."""
        possibles = [
            {"name": "Sunday", "prec": 5},
            {"name": "High Feast", "prec": 1},
            {"name": "Low Feast", "prec": 3},
        ]

        result = self.feast_service._apply_precedence_rules(
            possibles, transferred=False
        )
        self.assertEqual(result["name"], "Sunday")
        self.assertEqual(result["prec"], 5)

    def test_apply_precedence_rules_transferred(self):
        """Test precedence rules for transferred feasts."""
        possibles = [{"name": "High Feast", "prec": 1}, {"name": "Sunday", "prec": 5}]

        result = self.feast_service._apply_precedence_rules(possibles, transferred=True)
        self.assertIsNone(result)  # Sundays don't get transferred

    def test_get_liturgical_info(self):
        """Test the get_liturgical_info method returns the same as get_complete_feast_info."""
        with patch.object(
            self.feast_service, "get_complete_feast_info"
        ) as mock_get_complete:
            mock_get_complete.return_value = {"test": "data"}
            result = self.feast_service.get_liturgical_info("2024-12-25")
            mock_get_complete.assert_called_once_with("2024-12-25")
            self.assertEqual(result, {"test": "data"})


if __name__ == "__main__":
    unittest.main()
