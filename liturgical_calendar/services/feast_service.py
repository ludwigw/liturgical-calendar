"""
Feast service for orchestrating feast-related operations.

This service layer handles business logic for feast selection, precedence rules,
and feast data management. It provides a clean interface for higher-level
operations that need feast information.
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from liturgical_calendar.logging import get_logger

from ..core.readings_manager import ReadingsManager
from ..core.season_calculator import SeasonCalculator
from ..data.feasts_data import get_liturgical_feast
from ..funcs import date_to_days, day_of_week, get_easter


class FeastService:
    """
    Service for managing feast-related operations and business logic.

    This service orchestrates the interaction between different components
    (SeasonCalculator, ReadingsManager, feast data) to provide a clean
    interface for feast operations.
    """

    def __init__(
        self,
        season_calculator: Optional[SeasonCalculator] = None,
        readings_manager: Optional[ReadingsManager] = None,
    ):
        """
        Initialize the FeastService.

        Args:
            season_calculator: Optional SeasonCalculator instance for dependency injection
            readings_manager: Optional ReadingsManager instance for dependency injection
        """
        self.season_calculator = season_calculator or SeasonCalculator()
        self.readings_manager = readings_manager or ReadingsManager()
        self.logger = get_logger(__name__)

    def get_complete_feast_info(
        self, date_str: str, transferred: bool = False
    ) -> Dict[str, Any]:
        """
        Get complete feast information for a given date.

        This is the main entry point that orchestrates all feast-related operations.

        Args:
            date_str: Date string in YYYY-MM-DD format
            transferred: Whether to check for transferred feasts

        Returns:
            Complete feast information dictionary
        """
        # Parse the date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        day_of_week(year, month, day)

        # Calculate key dates and points
        easter_month, easter_day = get_easter(year)
        easter_date = date_to_days(year, easter_month, easter_day)
        current_date = date_to_days(year, month, day)
        easter_point = current_date - easter_date

        # Calculate Christmas point
        if month > 2:
            christmas_point = current_date - date_to_days(year, 12, 25)
        else:
            christmas_point = current_date - date_to_days(year - 1, 12, 25)

        # Get Advent Sunday
        advent_sunday = self._get_advent_sunday(year)

        # Get week information using the new API
        week_info = self.season_calculator.week_info(date_obj)
        season = week_info["season"]
        week_name = week_info["week_name"]
        weekday_reading = week_info["weekday_reading_key"]

        # Get week name (use week_name from week_info)
        week = week_name

        # Collect possible feasts
        possibles = self._collect_possible_feasts(
            easter_point, month, day, transferred, date_str
        )

        # Apply precedence rules
        result = self._apply_precedence_rules(possibles, transferred)

        # Handle case where no feast is selected (e.g., transferred Sunday)
        if result is None:
            result = {"name": "", "prec": 1}

        # Add season and date information
        # Presentational override: treat Pre-Lent and Pre-Advent as Ordinary Time
        display_season = (
            "Ordinary Time" if season in ["Pre-Lent", "Pre-Advent"] else season
        )
        result.update(
            {
                "season": display_season,
                "season_url": self._get_season_url(display_season),
                "weekno": None,  # We no longer calculate week numbers separately
                "week": week,
                "date": date_obj,
                "weekday_reading": weekday_reading,
            }
        )

        # Set color
        result["colour"] = self._determine_colour(
            result, season, christmas_point, advent_sunday
        )
        result["colourcode"] = self._get_colour_code(result["colour"])

        # Add readings
        result = self._add_readings(result, date_str)

        return result

    def _get_advent_sunday(self, year: int) -> int:
        """Get the date of Advent Sunday for the given year."""
        # This would need to be implemented or imported from existing code
        # For now, using a placeholder
        from ..funcs import get_advent_sunday

        return get_advent_sunday(year)

    def _collect_possible_feasts(
        self, easter_point: int, month: int, day: int, transferred: bool, date_str: str
    ) -> List[Dict[str, Any]]:
        """Collect all possible feasts for the date."""
        possibles = []
        # Easter-based feasts
        feast_from_easter = get_liturgical_feast("easter", easter_point)
        if feast_from_easter:
            possibles.append(feast_from_easter)
        # Christmas-based feasts
        feast_from_christmas = get_liturgical_feast(
            "christmas", f"{month:02d}-{day:02d}"
        )
        if feast_from_christmas:
            possibles.append(feast_from_christmas)
        # Transferred feasts
        if not transferred:
            transferred_feast = self._get_transferred_feast(date_str)
            if transferred_feast:
                possibles.append(transferred_feast)
        # Sunday - only add if no Principal Feast (prec==9) was found for this Sunday
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        dayofweek = day_of_week(date_obj.year, date_obj.month, date_obj.day)
        if dayofweek == 0:  # Sunday
            has_principal_feast = any(feast.get("prec") == 9 for feast in possibles)
            if not has_principal_feast:
                # Calculate season for Sunday using new API
                week_info = self.season_calculator.week_info(date_obj)
                week_name = week_info["week_name"]
                # Use the week name as the Sunday name (original logic with week number)
                possibles.append({"prec": 5, "type": "Sunday", "name": week_name})
        return possibles

    def _get_transferred_feast(self, date_str: str) -> Optional[Dict[str, Any]]:
        """Get transferred feast from yesterday."""
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        yesterday = date_obj + timedelta(days=-1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")
        # Recursive call to get yesterday's feast
        yesterday_feast = self.get_complete_feast_info(yesterday_str, transferred=True)
        # Only transfer if yesterday had a valid feast (not Sunday, not empty)
        if (
            yesterday_feast
            and yesterday_feast.get("prec", 0) != 5  # Not a Sunday
            and yesterday_feast.get("name", "").strip()
        ):  # Not empty
            yesterday_feast["name"] = yesterday_feast["name"] + " (transferred)"
            return yesterday_feast
        return None

    def _apply_precedence_rules(
        self, possibles: List[Dict[str, Any]], transferred: bool
    ) -> Dict[str, Any]:
        """Apply precedence rules to select the highest priority feast."""
        # Sort by precedence (highest first)
        possibles = sorted(possibles, key=lambda x: x.get("prec", 0), reverse=True)

        if transferred:
            # If two feasts coincided, return the transferred one
            try:
                if possibles[0] and possibles[0].get("prec") == 5:
                    return None  # Sundays don't get transferred
                return possibles[1] if len(possibles) > 1 else None
            except IndexError:
                return None

        # Return highest priority feast
        try:
            return possibles[0]
        except IndexError:
            return {"name": "", "prec": 1}

    def _get_season_url(self, season: str) -> str:
        """Get the Wikipedia URL for the season."""
        season_urls = {
            "Advent": "https://en.wikipedia.org/wiki/Advent",
            "Christmas": "https://en.wikipedia.org/wiki/Christmastide",
            "Epiphany": "https://en.wikipedia.org/wiki/Epiphany_season",
            "Ordinary Time": "https://en.wikipedia.org/wiki/Ordinary_Time",
            "Pre-Lent": "https://en.wikipedia.org/wiki/Septuagesima",
            "Lent": "https://en.wikipedia.org/wiki/Lent",
            "Holy Week": "https://en.wikipedia.org/wiki/Holy_Week",
            "Easter": "https://en.wikipedia.org/wiki/Eastertide",
            "Pentecost": "https://en.wikipedia.org/wiki/Ordinary_Time",
            "Trinity": "https://en.wikipedia.org/wiki/Ordinary_Time",
            "Pre-Advent": "https://en.wikipedia.org/wiki/Ordinary_Time",
        }
        return season_urls.get(season, "https://en.wikipedia.org/wiki/Ordinary_Time")

    def _normalize_weekno(self, weekno: Optional[int], season: str) -> Optional[int]:
        """Normalize week number based on season."""
        if weekno is not None and int(weekno) > 0:
            return int(weekno)
        elif season not in ["Pre-Lent", "Christmas", "Lent"]:
            return None
        return weekno

    def _determine_colour(
        self,
        result: Dict[str, Any],
        season: str,
        _christmas_point: int,
        _advent_sunday: int,
    ) -> str:
        """Determine the liturgical color for the feast."""
        # Special cases for rose Sundays
        if result.get("name") in ["Advent 3", "Lent 4"]:
            return "rose"

        # If color already set, use it
        if result.get("colour") is not None:
            return result["colour"]

        # Feast day colors
        if result.get("prec", 0) > 4 and result.get("prec") != 5:
            if result.get("martyr"):
                return "red"
            else:
                return "white"

        # Season colors
        season_colors = {
            "Advent": "purple",
            "Christmas": "white",
            "Epiphany": "white",
            "Lent": "purple",
            "Holy Week": "red",
            "Easter": "white",
        }
        return season_colors.get(season, "green")

    def _get_colour_code(self, colour: str) -> str:
        """Get the color code for the liturgical color."""
        # This would need to be implemented or imported
        # For now, returning a placeholder
        colour_codes = {
            "white": "#FFFFFF",
            "red": "#FF0000",
            "green": "#00FF00",
            "purple": "#800080",
            "rose": "#FFB6C1",
        }
        return colour_codes.get(colour, "#000000")

    def _add_readings(self, result: Dict[str, Any], date_str: str) -> Dict[str, Any]:
        """Add readings to the result with proper precedence order."""
        # 1. Check for feast readings (if high precedence feast)
        feast_prec = result.get("prec", 0)
        if feast_prec >= 5:
            feast_readings = self.readings_manager.get_feast_readings(result)
            if feast_readings:
                result["readings"] = feast_readings
                return result

        # 2. Get Sunday/weekday readings from ReadingsManager
        readings = self.readings_manager.get_readings_for_date(date_str, result)
        result["readings"] = readings

        return result

    def validate_feast_data(self, feast_data: Dict[str, Any]) -> bool:
        """
        Validate that feast data has required fields.

        Args:
            feast_data: The feast data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["name"]
        return all(field in feast_data for field in required_fields)

    def get_possible_feasts(
        self,
        easter_point: int,
        month: int,
        day: int,
        transferred: bool,
        s_date: str,
        _days: int,
        _season: str,
        _weekno: int,
        _dayofweek: int,
    ) -> list:
        """
        Public method to collect all possible feasts for the date.
        Args mirror the main function for compatibility.
        """
        return self._collect_possible_feasts(
            easter_point, month, day, transferred, s_date
        )

    def get_highest_priority_feast(self, possibles: list, transferred: bool) -> dict:
        """Get the highest priority feast from a list of possible feasts."""
        return self._apply_precedence_rules(possibles, transferred)

    def get_liturgical_info(self, date_str: str) -> Dict[str, Any]:
        """
        Get liturgical information for a given date.

        This method provides the same interface as the original liturgical_calendar function,
        making it easy to migrate existing code to use the service layer.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            Liturgical information dictionary with the same structure as liturgical_calendar
        """
        return self.get_complete_feast_info(date_str)

    def _get_week_name(self) -> str:
        """Get the liturgical week name."""
        # This method is no longer needed with the new SeasonCalculator API
        # The week name is now provided directly by week_info()
        return ""

    def get_feast_for_date(self, date_obj):
        try:
            self.logger.info(f"Looking up feast for {date_obj}")
            feast = self.season_calculator.get_feast(date_obj)
            if feast:
                self.logger.info(f"Feast found: {feast['name']}")
            else:
                self.logger.info(f"No feast found for {date_obj}")
            return feast
        except Exception as e:
            self.logger.exception(f"Error looking up feast for {date_obj}: {e}")
            raise

    def get_readings_for_date(self, date_obj):
        try:
            self.logger.info(f"Getting readings for {date_obj}")
            readings = self.readings_manager.get_readings(date_obj)
            if readings:
                self.logger.info(f"Readings found for {date_obj}")
            else:
                self.logger.info(f"No readings found for {date_obj}")
            return readings
        except Exception as e:
            self.logger.exception(f"Error getting readings for {date_obj}: {e}")
            raise
