"""
Artwork management for liturgical calendar images.
Handles feast artwork lookup, image source retrieval, and caching.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from liturgical_calendar.config.settings import Settings
from liturgical_calendar.funcs import date_to_days, get_cache_filename, get_easter
from liturgical_calendar.logging import get_logger

from ..caching.artwork_cache import ArtworkCache
from ..data.artwork_data import feasts as artwork_feasts
from ..data.feasts_data import (  # Only if needed for squashed artwork
    get_liturgical_feast,
)
from .readings_manager import ReadingsManager


class ArtworkManager:
    """
    Manages artwork selection and retrieval for liturgical calendar dates.

    This class encapsulates all artwork-related logic that was previously scattered
    throughout the codebase. It provides a clean interface for:
    - Looking up artwork by feast keys (season, pointer, cycle)
    - Retrieving artwork for specific dates with liturgical prioritization
    - Finding artwork entries that are never selected due to precedence rules
    - Managing cached artwork file paths
    - Automatic caching of missing artwork on first run

    The manager maintains the original data structure and logic while providing
    a more maintainable and testable interface. It works with the refactored
    data structure in artwork_data.py and integrates with the ReadingsManager
    for cycle calculations.

    Attributes:
        feasts: The artwork data dictionary containing easter and christmas season feasts
        cache: ArtworkCache instance for downloading and managing cached artwork
    """

    def __init__(self, config=None):
        """Initialize the ArtworkManager with artwork feast data."""
        self.feasts = artwork_feasts
        self.config = config
        self.logger = get_logger(__name__)

        # Use cache directory from config if available, otherwise use default
        cache_dir = None
        if config and hasattr(config, "CACHE_DIR"):
            cache_dir = config.CACHE_DIR
            self.logger.info("Using custom cache directory from config: %s", cache_dir)
        self.cache = ArtworkCache(cache_dir=cache_dir)

    def lookup_feast_artwork(
        self, relative_to: str, pointer: Any, cycle_index: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Return the artwork feast(s) for a given key. If multiple, select by cycle_index (default 0).

        Args:
            relative_to: The season ('easter' or 'christmas')
            pointer: The day offset or date key
            cycle_index: Which artwork to select if multiple options (0-based)

        Returns:
            Artwork entry dict or None if not found
        """
        feast_list = self.feasts[relative_to].get(pointer)
        if not feast_list:
            return None
        # Always treat as list
        if not isinstance(feast_list, list):
            feast_list = [feast_list]
        return feast_list[cycle_index % len(feast_list)]

    def get_artwork_for_date(
        self,
        date_str: str,
        auto_cache: bool = True,
        feast_info: Optional[  # pylint: disable=unused-argument
            Dict[str, Any]
        ] = None,  # Added for backward compatibility
    ) -> Optional[Dict[str, Any]]:
        """
        Get artwork information for a given date.

        Args:
            date_str: Date string in YYYY-MM-DD format
            auto_cache: Whether to automatically cache missing artwork (default: True)
            feast_info: Feast information (added for backward compatibility, not currently used)

        Returns:
            dict: Artwork object with 'source', 'name', 'url' (if exists), 'martyr' (if exists),
                  'cached_file' (if cached), and 'cached' (bool) keys
        """
        # Create ReadingsManager instance
        readings_manager = ReadingsManager()

        # Parse the date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day

        # Get the yearly cycle (A, B, C)
        sunday_cycle, _unused_weekday_cycle = readings_manager.get_yearly_cycle(year)
        cycle_index = {"A": 0, "B": 1, "C": 2}[sunday_cycle]

        # Format the date key for christmas-based feasts
        date_key = f"{month:02d}-{day:02d}"
        possible_entries = []

        # Check easter-based feasts first (calculate days from easter)
        easter_month, easter_day = get_easter(year)
        easter_date = date_to_days(year, easter_month, easter_day)
        current_date = date_to_days(year, month, day)
        easter_point = current_date - easter_date
        easter_feasts = self.feasts["easter"]

        if easter_point in easter_feasts:
            entry_list = easter_feasts[easter_point]
            if isinstance(entry_list, list):
                possible_entries.extend(entry_list)
            else:
                possible_entries.append(entry_list)

        # Check christmas-based feasts
        christmas_feasts = self.feasts["christmas"]
        if date_key in christmas_feasts:
            entry_list = christmas_feasts[date_key]
            if isinstance(entry_list, list):
                possible_entries.extend(entry_list)
            else:
                possible_entries.append(entry_list)

        # Select the best entry based on cycle and precedence
        selected_entry = None
        if possible_entries:
            # Sort by cycle preference (current cycle first, then others)
            cycle_priorities = [
                cycle_index,
                (cycle_index + 1) % 3,
                (cycle_index + 2) % 3,
            ]

            for cycle_priority in cycle_priorities:
                for entry in possible_entries:
                    if isinstance(entry, dict) and entry.get("cycle") == cycle_priority:
                        selected_entry = entry
                        break
                if selected_entry:
                    break

            # If no cycle-specific entry found, use the first available
            if not selected_entry and possible_entries:
                selected_entry = (
                    possible_entries[0]
                    if isinstance(possible_entries[0], dict)
                    else None
                )

        if not selected_entry:
            return None

        # Build result dictionary
        result = {
            "name": selected_entry.get("name", ""),
            "source": selected_entry.get("source"),
            "url": selected_entry.get("url"),
            "martyr": selected_entry.get("martyr"),
        }

        # Check cache status and handle auto-caching
        source_url = result.get("source")
        if source_url:
            cache_filename = get_cache_filename(source_url)
            cached_path = Path(Settings.CACHE_DIR) / cache_filename

            if cached_path.exists():
                result["cached_file"] = str(cached_path)
                result["cached"] = True
            else:
                result["cached_file"] = None
                result["cached"] = False

                # Auto-cache if enabled and this is the first run scenario
                if auto_cache:
                    self.logger.info(
                        "Artwork not cached for %s, attempting to download: %s",
                        date_str,
                        source_url,
                    )
                    try:
                        success = self.cache.download_and_cache(source_url)
                        if success:
                            result["cached_file"] = str(cached_path)
                            result["cached"] = True
                            self.logger.info(
                                "Successfully cached artwork for %s", date_str
                            )
                        else:
                            self.logger.warning(
                                "Failed to cache artwork for %s: %s",
                                date_str,
                                source_url,
                            )
                    except (
                        OSError,
                        IOError,
                        ConnectionError,
                        TimeoutError,
                        ValueError,
                        TypeError,
                    ) as e:
                        self.logger.error(
                            "Error caching artwork for %s: %s", date_str, e
                        )
        else:
            result["cached_file"] = None
            result["cached"] = False

        return result

    def get_cached_artwork_path(self, source_url: str) -> Optional[str]:
        """
        Get the cached file path for a given source URL.

        Args:
            source_url: The source URL of the artwork

        Returns:
            Path to cached file if it exists, None otherwise
        """
        cache_filename = get_cache_filename(source_url)
        cached_path = Path(Settings.CACHE_DIR) / cache_filename
        return str(cached_path) if cached_path.exists() else None

    def find_next_artwork(self, current_date: str) -> Optional[Dict[str, Any]]:
        """
        Find the next artwork after a given date that has a cached file.

        Args:
            current_date: Date string in YYYY-MM-DD format

        Returns:
            Next artwork entry with 'date' field added, or None if not found
        """
        # Parse the current date
        current_date_obj = datetime.strptime(current_date, "%Y-%m-%d").date()

        # Look ahead up to 366 days for the next artwork with cached file
        for days_ahead in range(1, 367):
            check_date = current_date_obj + timedelta(days=days_ahead)
            check_date_str = check_date.strftime("%Y-%m-%d")

            # Get artwork for this future date
            artwork = self.get_artwork_for_date(check_date_str)
            if artwork and artwork.get("cached_file"):
                # Add the date to the artwork info for display
                artwork["date"] = check_date.strftime("%-d %B, %Y")
                return artwork

        return None

    def validate_artwork_data(self, artwork_entry: Dict[str, Any]) -> bool:
        """
        Validate that an artwork entry has required fields.

        Args:
            artwork_entry: The artwork entry to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["name"]
        return all(field in artwork_entry for field in required_fields)

    def find_squashed_artworks(self) -> List[Dict[str, Any]]:
        """
        Find artwork entries that are never selected due to high-precedence feasts.

        Returns:
            List of squashed artwork entries
        """
        squashed = []
        for season, items in self.feasts.items():
            for pointer, entries in items.items():
                if not isinstance(entries, list):
                    entries = [entries]
                # Get the liturgical name and prec for this date
                feast = None
                try:
                    feast = get_liturgical_feast(season, pointer)
                except (ValueError, KeyError, TypeError):
                    pass
                if not feast or feast.get("prec", 0) <= 5:
                    continue
                lit_name = feast.get("name")
                for entry in entries:
                    if entry.get("name") and entry.get("name") != lit_name:
                        squashed.append(
                            {
                                "season": season,
                                "pointer": pointer,
                                "liturgical_name": lit_name,
                                "prec": feast.get("prec"),
                                "artwork_name": entry.get("name"),
                                "source": entry.get("source", None),
                            }
                        )
        return squashed
