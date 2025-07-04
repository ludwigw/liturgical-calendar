"""
Custom exception hierarchy for the Liturgical Calendar project.
Use these exceptions for structured error handling across all modules and scripts.
"""

class LiturgicalCalendarError(Exception):
    """Base exception for all liturgical calendar errors."""
    pass

class ConfigError(LiturgicalCalendarError):
    """Raised for configuration-related errors."""
    pass

class ArtworkNotFoundError(LiturgicalCalendarError):
    """Raised when artwork cannot be found or loaded."""
    pass

class ReadingsNotFoundError(LiturgicalCalendarError):
    """Raised when readings for a date or feast cannot be found."""
    pass

class ImageGenerationError(LiturgicalCalendarError):
    """Raised for errors during image generation or processing."""
    pass

class CacheError(LiturgicalCalendarError):
    """Raised for errors related to caching or cache operations."""
    pass 