"""
Configuration management for the liturgical calendar project.

This module provides centralized configuration settings for the liturgical calendar
application, including image generation parameters, caching settings, and feature toggles.
Settings can be loaded from YAML files and overridden by environment variables.
"""

import os

import yaml


class Settings:
    """
    Centralized configuration for the liturgical calendar project.
    All settings should be accessed via this class.

    Usage:
        - Defaults are set as class attributes.
        - Call Settings.load_from_file('config.yaml') to load from a YAML file (optional).
        - Environment variables with matching names (e.g., IMAGE_WIDTH) override both defaults and file values.
        - Precedence: ENV > config file > code default.
    """

    # Image generation settings
    IMAGE_WIDTH = 1404  # px
    IMAGE_HEIGHT = 1872  # px
    FONTS_DIR = "fonts"  # Directory for font files
    PADDING = 48  # px
    ARTWORK_SIZE = 1080  # px
    ROW_SPACING = 48  # px
    HEADER_FONT_SIZE = 36
    TITLE_FONT_SIZE = 96
    TITLE_LINE_HEIGHT = 1.2
    COLUMN_FONT_SIZE = 36
    BG_COLOR = (255, 255, 255)  # White background
    TEXT_COLOR = (74, 74, 74)  # Default text color
    LINE_COLOR = (151, 151, 151)  # Divider line color

    # Caching settings
    CACHE_DIR = "cache"
    ORIGINALS_SUBDIR = "original"
    MAX_CACHE_SIZE = None  # e.g., "1GB" (not enforced yet)
    CACHE_CLEANUP_DAYS = 30  # Remove files older than this

    # Build settings
    BUILD_DIR = "build"  # Directory for generated images

    # Fallback/placeholder settings
    PLACEHOLDER_COLOR = (230, 230, 230)  # Light gray color for missing artwork

    # API/network settings
    REQUEST_TIMEOUT = 30  # seconds
    MAX_RETRIES = 3
    USER_AGENT = "Mozilla/5.0"

    # Feature toggles
    ENABLE_UPSAMPLING = True
    LOGGING_LEVEL = "INFO"  # Can be overridden

    @classmethod
    def load_from_file(cls, path="config.yaml"):
        """
        Load configuration from a YAML file, then apply environment variable overrides.
        ENV variables must match the class attribute names (e.g., IMAGE_WIDTH).
        """
        if path and isinstance(path, str) and path.strip() and os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            for key, value in data.items():
                if hasattr(cls, key):
                    setattr(cls, key, value)
        # ENV override
        for key in dir(cls):
            if key.isupper() and key in os.environ:
                val = os.environ[key]
                # Try to cast to the type of the default value
                default = getattr(cls, key)
                try:
                    if isinstance(default, bool):
                        val = val.lower() in ("1", "true", "yes", "on")
                    elif isinstance(default, int):
                        val = int(val)
                    elif isinstance(default, float):
                        val = float(val)
                    elif isinstance(default, tuple):
                        # For color tuples: "255,255,255"
                        val = tuple(int(x) for x in val.split(","))
                    # else: leave as string
                except Exception:
                    pass
                setattr(cls, key, val)
