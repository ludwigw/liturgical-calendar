"""
Custom exception hierarchy for the Liturgical Calendar project.
Use these exceptions for structured error handling across all modules and scripts.
"""


class LiturgicalCalendarError(Exception):
    """Base exception for all liturgical calendar errors."""



class ConfigError(LiturgicalCalendarError):
    """Raised for configuration-related errors."""



class ArtworkNotFoundError(LiturgicalCalendarError):
    """Raised when artwork cannot be found or loaded."""



class ReadingsNotFoundError(LiturgicalCalendarError):
    """Raised when readings for a date or feast cannot be found."""



class ImageGenerationError(LiturgicalCalendarError):
    """Raised for errors during image generation or processing."""



class CacheError(LiturgicalCalendarError):
    """Raised for errors related to caching or cache operations."""

