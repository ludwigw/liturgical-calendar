"""
Artwork management for liturgical calendar images.
Handles feast artwork lookup, image source retrieval, and caching.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..data.artwork_data import feasts as artwork_feasts
from ..data.feasts_data import get_liturgical_feast  # Only if needed for squashed artwork
from liturgical_calendar.logging import get_logger
from liturgical_calendar.config.settings import Settings


class ArtworkManager:
    """
    Manages artwork selection and retrieval for liturgical calendar dates.
    
    This class encapsulates all artwork-related logic that was previously scattered
    throughout the codebase. It provides a clean interface for:
    - Looking up artwork by feast keys (season, pointer, cycle)
    - Retrieving artwork for specific dates with liturgical prioritization
    - Finding artwork entries that are never selected due to precedence rules
    - Managing cached artwork file paths
    
    The manager maintains the original data structure and logic while providing
    a more maintainable and testable interface. It works with the refactored
    data structure in artwork_data.py and integrates with the ReadingsManager
    for cycle calculations.
    
    Attributes:
        feasts: The artwork data dictionary containing easter and christmas season feasts
    """
    
    def __init__(self, config=None):
        """Initialize the ArtworkManager with artwork feast data."""
        self.feasts = artwork_feasts
        self.config = config
        self.logger = get_logger(__name__)
    
    def lookup_feast_artwork(self, relative_to: str, pointer: Any, cycle_index: int = 0) -> Optional[Dict[str, Any]]:
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
    
    def get_artwork_for_date(self, date_str: str, liturgical_info: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get artwork information for a given date.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            liturgical_info: Optional result from liturgical_calendar to help prioritize feasts
            
        Returns:
            dict: Artwork object with 'source', 'name', 'url' (if exists), 'martyr' (if exists),
                  'cached_file' (if cached), and 'cached' (bool) keys
        """
        from .readings_manager import ReadingsManager
        from ..funcs import get_easter, date_to_days, get_cache_filename
        
        # Create ReadingsManager instance
        readings_manager = ReadingsManager()
        
        # Parse the date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        
        # Get the yearly cycle (A, B, C)
        sunday_cycle, weekday_cycle = readings_manager.get_yearly_cycle(year)
        cycle_index = {'A': 0, 'B': 1, 'C': 2}[sunday_cycle]
        
        # Format the date key for christmas-based feasts
        date_key = f"{month:02d}-{day:02d}"
        possible_entries = []
        
        # Check easter-based feasts first (calculate days from easter)
        easter_month, easter_day = get_easter(year)
        easter_date = date_to_days(year, easter_month, easter_day)
        current_date = date_to_days(year, month, day)
        easter_point = current_date - easter_date
        easter_feasts = self.feasts['easter']
        
        if easter_point in easter_feasts:
            entry_list = easter_feasts[easter_point]
            if isinstance(entry_list, list):
                possible_entries.extend(entry_list)
            else:
                possible_entries.append(entry_list)
        
        # Check christmas-based feasts
        christmas_feasts = self.feasts['christmas']
        if date_key in christmas_feasts:
            entry_list = christmas_feasts[date_key]
            if isinstance(entry_list, list):
                possible_entries.extend(entry_list)
            else:
                possible_entries.append(entry_list)
        
        if not possible_entries:
            return None
        
        # If we have liturgical result, prioritize entries that match the liturgical name
        if liturgical_info:
            liturgical_name = liturgical_info.get('name')
            liturgical_prec = liturgical_info.get('prec', 0)
            if liturgical_prec >= 5:
                # Only for feasts with prec >= 5, match by name
                matching_entries = [entry for entry in possible_entries if entry.get('name') == liturgical_name]
                if matching_entries:
                    # If multiple matching entries, select by cycle
                    selected_entry = matching_entries[cycle_index % len(matching_entries)]
                else:
                    # If no exact match, select by cycle from all entries
                    selected_entry = possible_entries[cycle_index % len(possible_entries)]
            else:
                # For prec < 5, select by cycle from all entries
                selected_entry = possible_entries[cycle_index % len(possible_entries)]
        else:
            selected_entry = possible_entries[cycle_index % len(possible_entries)]
        
        result = {
            'source': selected_entry.get('source'),
            'name': selected_entry.get('name')
        }
        if 'url' in selected_entry:
            result['url'] = selected_entry['url']
        if 'martyr' in selected_entry:
            result['martyr'] = selected_entry['martyr']
        
        # Add cached file info
        source_url = selected_entry.get('source')
        if source_url:
            cache_filename = get_cache_filename(source_url)
            cached_path = Path(Settings.CACHE_DIR) / cache_filename
            if cached_path.exists():
                result['cached_file'] = str(cached_path)
                result['cached'] = True
            else:
                result['cached_file'] = None
                result['cached'] = False
        else:
            result['cached_file'] = None
            result['cached'] = False
        
        return result




    
    def get_cached_artwork_path(self, source_url: str) -> Optional[str]:
        """
        Get the cached file path for a given source URL.
        
        Args:
            source_url: The source URL of the artwork
            
        Returns:
            Path to cached file if it exists, None otherwise
        """
        from ..funcs import get_cache_filename
        
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
        from datetime import datetime, timedelta
        
        # Parse the current date
        current_date_obj = datetime.strptime(current_date, "%Y-%m-%d").date()
        
        # Look ahead up to 366 days for the next artwork with cached file
        for days_ahead in range(1, 367):
            check_date = current_date_obj + timedelta(days=days_ahead)
            check_date_str = check_date.strftime("%Y-%m-%d")
            
            # Get artwork for this future date
            artwork = self.get_artwork_for_date(check_date_str)
            if artwork and artwork.get('cached_file'):
                # Add the date to the artwork info for display
                artwork['date'] = check_date.strftime('%-d %B, %Y')
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
        required_fields = ['name']
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
                except Exception:
                    pass
                if not feast or feast.get('prec', 0) <= 5:
                    continue
                lit_name = feast.get('name')
                for entry in entries:
                    if entry.get('name') and entry.get('name') != lit_name:
                        squashed.append({
                            'season': season,
                            'pointer': pointer,
                            'liturgical_name': lit_name,
                            'prec': feast.get('prec'),
                            'artwork_name': entry.get('name'),
                            'source': entry.get('source', None)
                        })
        return squashed

    def get_artwork_for_feast(self, feast_info):
        try:
            feast_name = feast_info.get('name', 'Unknown')
            self.logger.info(f"Looking up artwork for feast: {feast_name}")
            artwork = self._lookup_artwork(feast_info)
            if artwork:
                self.logger.info(f"Artwork found for feast: {feast_name}")
            else:
                self.logger.info(f"No artwork found for feast: {feast_name}")
            return artwork
        except Exception as e:
            self.logger.exception(f"Error looking up artwork for feast {feast_name}: {e}")
            raise

    def _lookup_artwork(self, feast_info):
        # ... existing logic ...
        pass 