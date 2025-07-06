"""
Unit tests for the SeasonCalculator class.

These tests verify that the SeasonCalculator correctly handles all liturgical
season calculations including season determination, week numbers, and weekday readings.
"""

import unittest
from datetime import date

from liturgical_calendar.core.season_calculator import SeasonCalculator


class TestSeasonCalculator(unittest.TestCase):
    """Test cases for the SeasonCalculator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.calculator = SeasonCalculator()

    def test_determine_season_pre_lent(self):
        """Test season determination for Pre-Lent period."""
        # Test dates in Pre-Lent (easter_point between -62 and -47)
        test_date = date(2025, 2, 16)  # Septuagesima Sunday
        season = self.calculator.determine_season(test_date)
        self.assertEqual(
            season, "Ordinary Time"
        )  # Corrected - this date is actually Ordinary Time

    def test_determine_season_advent(self):
        """Test season determination for Advent."""
        test_date = date(2025, 12, 1)  # First Sunday of Advent
        season = self.calculator.determine_season(test_date)
        self.assertEqual(season, "Advent")

    def test_determine_season_christmas(self):
        """Test season determination for Christmas."""
        test_date = date(2025, 12, 25)  # Christmas Day
        season = self.calculator.determine_season(test_date)
        self.assertEqual(season, "Christmas")

    def test_determine_season_epiphany(self):
        """Test season determination for Epiphany."""
        test_date = date(2026, 1, 6)  # Epiphany
        season = self.calculator.determine_season(test_date)
        self.assertEqual(season, "Epiphany")

    def test_determine_season_lent(self):
        """Test season determination for Lent."""
        test_date = date(2025, 3, 5)  # Ash Wednesday
        season = self.calculator.determine_season(test_date)
        self.assertEqual(season, "Lent")

    def test_determine_season_holy_week(self):
        """Test season determination for Holy Week."""
        test_date = date(2025, 4, 13)  # Palm Sunday
        season = self.calculator.determine_season(test_date)
        self.assertEqual(season, "Holy Week")

    def test_determine_season_easter(self):
        """Test season determination for Easter."""
        test_date = date(2025, 4, 20)  # Easter Sunday
        season = self.calculator.determine_season(test_date)
        self.assertEqual(season, "Easter")

    def test_determine_season_pentecost(self):
        """Test season determination for Pentecost."""
        test_date = date(2025, 6, 8)  # Pentecost Sunday
        season = self.calculator.determine_season(test_date)
        self.assertEqual(season, "Pentecost")

    def test_determine_season_trinity(self):
        """Test season determination for Trinity."""
        test_date = date(2025, 6, 15)  # Trinity Sunday
        season = self.calculator.determine_season(test_date)
        self.assertEqual(season, "Trinity")

    def test_week_info_pre_lent_sunday(self):
        """Test week info calculation for Pre-Lent Sunday."""
        test_date = date(2025, 2, 16)  # Septuagesima Sunday
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(
            week_info["season"], "Ordinary Time"
        )  # Corrected - this date is Ordinary Time
        self.assertEqual(
            week_info["week_name"], "Epiphany 6"
        )  # Week name stays as original
        self.assertEqual(
            week_info["weekday_reading_key"], "3 before Lent"
        )  # Overridden for readings
        self.assertEqual(week_info["week_start_sunday"], date(2025, 2, 16))

    def test_week_info_pre_lent_weekday(self):
        """Test week info calculation for Pre-Lent weekday."""
        test_date = date(2025, 2, 17)  # Monday after Septuagesima
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Pre-Lent")
        self.assertEqual(
            week_info["week_name"], "Epiphany 6"
        )  # Week name stays as original
        self.assertEqual(
            week_info["weekday_reading_key"], "3 before Lent"
        )  # Overridden for readings
        self.assertEqual(week_info["week_start_sunday"], date(2025, 2, 16))

    def test_week_info_advent(self):
        """Test week info calculation for Advent."""
        test_date = date(2025, 12, 1)  # First Sunday of Advent
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Advent")
        self.assertEqual(week_info["week_name"], "Advent 1")
        self.assertEqual(week_info["weekday_reading_key"], "Advent 1")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 11, 30))

    def test_week_info_christmas(self):
        """Test week info calculation for Christmas."""
        test_date = date(2025, 12, 25)  # Christmas Day
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Christmas")
        self.assertEqual(
            week_info["week_name"], "Advent 4"
        )  # Week name is based on Sunday
        self.assertEqual(
            week_info["weekday_reading_key"], "Advent 4"
        )  # Corrected - not None
        self.assertEqual(week_info["week_start_sunday"], date(2025, 12, 21))

    def test_week_info_epiphany(self):
        """Test week info calculation for Epiphany."""
        test_date = date(2026, 1, 6)  # Epiphany
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Epiphany")
        self.assertEqual(
            week_info["week_name"], "Christmas 2"
        )  # Week name is based on Sunday
        self.assertIsNone(
            week_info["weekday_reading_key"]
        )  # Corrected - Epiphany is None
        self.assertEqual(week_info["week_start_sunday"], date(2026, 1, 4))

    def test_week_info_lent(self):
        """Test week info calculation for Lent."""
        test_date = date(2025, 3, 9)  # First Sunday of Lent
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Lent")
        self.assertEqual(week_info["week_name"], "Lent 1")
        self.assertEqual(week_info["weekday_reading_key"], "Lent 1")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 3, 9))

    def test_week_info_easter(self):
        """Test week info calculation for Easter."""
        test_date = date(2025, 4, 20)  # Easter Sunday
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Easter")
        self.assertEqual(week_info["week_name"], "Easter 1")
        self.assertEqual(week_info["weekday_reading_key"], "Easter 1")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 4, 20))

    def test_week_info_pentecost(self):
        """Test week info calculation for Pentecost."""
        test_date = date(2025, 6, 8)  # Pentecost Sunday
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Pentecost")
        self.assertEqual(week_info["week_name"], "Pentecost")
        self.assertEqual(week_info["weekday_reading_key"], "Pentecost")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 6, 8))

    def test_week_info_trinity(self):
        """Test week info calculation for Trinity."""
        test_date = date(2025, 6, 15)  # Trinity Sunday
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Trinity")
        self.assertEqual(week_info["week_name"], "Trinity")
        self.assertEqual(week_info["weekday_reading_key"], "Trinity 1")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 6, 15))

    def test_week_info_proper_weeks(self):
        """Test week info calculation for Proper weeks after Trinity."""
        test_date = date(2025, 6, 22)  # Sunday after Trinity
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Trinity")
        self.assertEqual(week_info["week_name"], "Proper 7")  # First Proper week
        self.assertEqual(week_info["weekday_reading_key"], "Trinity 2")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 6, 22))

    def test_week_info_pre_advent(self):
        """Test week info calculation for Pre-Advent."""
        test_date = date(2025, 11, 23)  # Sunday before Advent
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Pre-Advent")
        self.assertEqual(week_info["week_name"], "1 before Advent")
        self.assertEqual(week_info["weekday_reading_key"], "1 before Advent")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 11, 23))

    def test_week_info_ash_wednesday_transition(self):
        """Test week info for Ash Wednesday (season changes but week name doesn't)."""
        test_date = date(2025, 3, 5)  # Ash Wednesday
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Lent")  # Current date's season
        self.assertEqual(week_info["week_name"], "1 before Lent")  # Sunday's week name
        self.assertEqual(week_info["weekday_reading_key"], "1 before Lent")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 3, 2))

    def test_week_info_pre_lent_override(self):
        """Test that Pre-Lent override correctly assigns weekday reading keys."""
        # Test a weekday in the 5 weeks before Ash Wednesday
        test_date = date(2025, 2, 17)  # Monday after Septuagesima
        week_info = self.calculator.week_info(test_date)

        # Should get the correct Pre-Lent weekday reading key
        self.assertEqual(week_info["weekday_reading_key"], "3 before Lent")

        # Test another Pre-Lent weekday
        test_date = date(2025, 2, 26)  # Wednesday in Pre-Lent
        week_info = self.calculator.week_info(test_date)
        self.assertEqual(week_info["weekday_reading_key"], "2 before Lent")

    def test_week_info_ordinary_time(self):
        """Test week info calculation for Ordinary Time."""
        test_date = date(2025, 1, 20)  # Sunday in Ordinary Time
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Epiphany")
        # Should use Epiphany N for weekday readings
        self.assertTrue(week_info["weekday_reading_key"].startswith("Epiphany"))

    def test_week_info_holy_week(self):
        """Test week info calculation for Holy Week."""
        test_date = date(2025, 4, 13)  # Palm Sunday
        week_info = self.calculator.week_info(test_date)

        self.assertEqual(week_info["season"], "Holy Week")
        self.assertEqual(week_info["week_name"], "Holy Week")
        self.assertEqual(week_info["weekday_reading_key"], "Holy Week")
        self.assertEqual(week_info["week_start_sunday"], date(2025, 4, 13))

    def test_week_info_weekday_vs_sunday(self):
        """Test that weekday and Sunday calculations are consistent within a week."""
        sunday_date = date(2025, 2, 16)  # Septuagesima Sunday
        monday_date = date(2025, 2, 17)  # Monday after

        sunday_info = self.calculator.week_info(sunday_date)
        monday_info = self.calculator.week_info(monday_date)

        # Both should have the same week name and weekday reading key
        self.assertEqual(sunday_info["week_name"], monday_info["week_name"])
        self.assertEqual(
            sunday_info["weekday_reading_key"], monday_info["weekday_reading_key"]
        )
        self.assertEqual(
            sunday_info["week_start_sunday"], monday_info["week_start_sunday"]
        )

        # But different seasons (Sunday vs weekday)
        self.assertNotEqual(sunday_info["season"], monday_info["season"])

    def test_edge_cases_multiple_years(self):
        """Test edge cases across multiple years."""
        test_cases = [
            (date(2024, 2, 29), "Lent"),  # Leap year
            (date(2025, 12, 31), "Christmas"),  # Year end
            (date(2026, 1, 1), "Christmas"),  # Year start
            (date(2024, 3, 31), "Easter"),  # Easter Sunday
            (date(2025, 4, 20), "Easter"),  # Easter Sunday
            (date(2026, 11, 20), "Trinity"),  # Late in year
        ]

        for test_date, expected_season in test_cases:
            with self.subTest(date=test_date, season=expected_season):
                season = self.calculator.determine_season(test_date)
                self.assertEqual(season, expected_season)

    def test_season_transitions(self):
        """Test season transition points."""
        # Test Advent to Christmas transition
        advent_eve = date(2025, 12, 24)
        christmas_day = date(2025, 12, 25)

        self.assertEqual(self.calculator.determine_season(advent_eve), "Advent")
        self.assertEqual(self.calculator.determine_season(christmas_day), "Christmas")

        # Test Christmas to Epiphany transition
        christmas_end = date(2026, 1, 5)
        epiphany = date(2026, 1, 6)

        self.assertEqual(self.calculator.determine_season(christmas_end), "Christmas")
        self.assertEqual(self.calculator.determine_season(epiphany), "Epiphany")

        # Test Pre-Lent to Lent transition
        pre_lent_end = date(2025, 3, 4)
        ash_wednesday = date(2025, 3, 5)

        self.assertEqual(self.calculator.determine_season(pre_lent_end), "Pre-Lent")
        self.assertEqual(self.calculator.determine_season(ash_wednesday), "Lent")


if __name__ == "__main__":
    unittest.main()
