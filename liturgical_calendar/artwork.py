"""
Artwork management for liturgical calendar images.

This module provides a clean public interface for artwork operations by delegating
to the ArtworkManager class. This follows the refactoring pattern established in
Phase 1 of the project to separate concerns and improve maintainability.

The module maintains backward compatibility with existing code while providing
access to the new modular architecture underneath.

Functions:
    lookup_feast_artwork: Look up artwork for a given feast key
    get_image_source_for_date: Get artwork information for a specific date
    find_squashed_artworks: Find artwork entries that are never selected
"""
from .core.artwork_manager import ArtworkManager

# Create singleton instance
artwork_manager = ArtworkManager()

# Public interface - delegate to manager
def lookup_feast_artwork(relative_to, pointer, cycle_index=0):
    """
    Look up artwork for a given feast key.
    
    Args:
        relative_to: The season ('easter' or 'christmas')
        pointer: The day offset or date key
        cycle_index: Which artwork to select if multiple options (0-based)
        
    Returns:
        Artwork entry dict or None if not found
    """
    return artwork_manager.lookup_feast_artwork(relative_to, pointer, cycle_index)

def get_image_source_for_date(date, liturgical_result=None):
    """
    Get the image source for a given date.
    
    Args:
        date: Date string in YYYY-MM-DD format
        liturgical_result: Optional liturgical calendar result for prioritization
        
    Returns:
        Artwork information dict or None if no artwork found
    """
    return artwork_manager.get_artwork_for_date(date, liturgical_result)

def find_squashed_artworks():
    """
    Find artwork entries that are never selected due to higher precedence feasts.
    
    Returns:
        List of squashed artwork entries with metadata
    """
    return artwork_manager.find_squashed_artworks()
