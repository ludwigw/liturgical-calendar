"""
Configuration service for managing application settings.

This service layer provides a centralized way to access and modify
configuration settings for the liturgical calendar application.
"""

import json
import os
from typing import Any, Dict, Optional

from liturgical_calendar.exceptions import ConfigError
from liturgical_calendar.logging import get_logger
from liturgical_calendar.utils.file_system import safe_write_file

from ..funcs import date_to_days


class ConfigService:
    """
    Service for managing configuration settings and application state.

    This service provides a centralized interface for accessing and modifying
    configuration settings, with support for different environments and
    configuration sources.
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the ConfigService.

        Args:
            config_file: Optional path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config_file = config_file or self._get_default_config_path()
        self._config = self._load_config()
        self._defaults = self._get_default_config()

    def calculate_christmas_point(self, year: int, month: int, days: int) -> int:
        """
        Calculate the Christmas point (days from Christmas).

        We will store the amount of time until (-ve) or since (+ve) Christmas in
        christmas_point. Let's make the cut-off date the end of February,
        since we'll be dealing with Easter-based dates after that, and it
        avoids the problems of considering leap years.

        Args:
            year: Year
            month: Month
            days: Julian days from epoch

        Returns:
            Days from Christmas (negative if before, positive if after)
        """
        if month > 2:
            christmas_point = days - date_to_days(year, 12, 25)
        else:
            christmas_point = days - date_to_days(year - 1, 12, 25)
        return christmas_point

    def get_season_url(self, season: str) -> str:
        """
        Get the Wikipedia URL for a liturgical season.

        Args:
            season: Liturgical season name

        Returns:
            Wikipedia URL for the season
        """
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

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports dot notation for nested keys)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config

        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        # Set the value
        config[keys[-1]] = value

    def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Complete configuration dictionary
        """
        return self._config.copy()

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self._config = self._defaults.copy()
        self._save_config()

    def reload(self) -> None:
        """Reload configuration from file."""
        self._config = self._load_config()

    def save(self) -> None:
        """Save current configuration to file."""
        self._save_config()

    def get_image_settings(self) -> Dict[str, Any]:
        """
        Get image generation settings.

        Returns:
            Dictionary of image generation settings
        """
        return {
            "width": self.get("image.width", 1080),
            "height": self.get("image.height", 1080),
            "format": self.get("image.format", "PNG"),
            "quality": self.get("image.quality", 95),
            "background_color": self.get("image.background_color", "#FFFFFF"),
            "font_family": self.get("image.font_family", "Arial"),
            "font_size": self.get("image.font_size", 24),
            "text_color": self.get("image.text_color", "#000000"),
        }

    def get_artwork_settings(self) -> Dict[str, Any]:
        """
        Get artwork settings.

        Returns:
            Dictionary of artwork settings
        """
        return {
            "cache_dir": self.get("artwork.cache_dir", "./cache"),
            "max_cache_size": self.get("artwork.max_cache_size", 1000),
            "download_timeout": self.get("artwork.download_timeout", 30),
            "preferred_sources": self.get("artwork.preferred_sources", ["met", "nga"]),
            "fallback_artwork": self.get("artwork.fallback_artwork", "default.jpg"),
        }

    def get_readings_settings(self) -> Dict[str, Any]:
        """
        Get readings settings.

        Returns:
            Dictionary of readings settings
        """
        return {
            "include_psalm": self.get("readings.include_psalm", True),
            "include_gospel": self.get("readings.include_gospel", True),
            "include_epistle": self.get("readings.include_epistle", True),
            "max_reading_length": self.get("readings.max_length", 200),
            "translation": self.get("readings.translation", "NRSV"),
        }

    def get_output_settings(self) -> Dict[str, Any]:
        """
        Get output settings.

        Returns:
            Dictionary of output settings
        """
        return {
            "output_dir": self.get("output.directory", "./output"),
            "filename_format": self.get(
                "output.filename_format", "liturgical_{date}.png"
            ),
            "create_subdirs": self.get("output.create_subdirs", True),
            "overwrite_existing": self.get("output.overwrite_existing", False),
        }

    def get_logging_settings(self) -> Dict[str, Any]:
        """
        Get logging settings.

        Returns:
            Dictionary of logging settings
        """
        return {
            "level": self.get("logging.level", "INFO"),
            "file": self.get("logging.file", None),
            "format": self.get(
                "logging.format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            ),
            "max_file_size": self.get(
                "logging.max_file_size", 10 * 1024 * 1024
            ),  # 10MB
            "backup_count": self.get("logging.backup_count", 5),
        }

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the current configuration.

        Returns:
            Dictionary with validation results
        """
        warnings = []
        errors = []

        # Check required directories
        required_dirs = [self.get("artwork.cache_dir"), self.get("output.directory")]

        for dir_path in required_dirs:
            if dir_path and not os.path.exists(dir_path):
                try:
                    os.makedirs(dir_path, exist_ok=True)
                    self.logger.info("Created missing directory: %s", dir_path)
                except (OSError, PermissionError) as e:
                    self.logger.error("Cannot create directory %s: %s", dir_path, e)
                    errors.append(f"Cannot create directory {dir_path}: {e}")

        # Check image settings
        image_settings = self.get_image_settings()
        if image_settings["width"] <= 0 or image_settings["height"] <= 0:
            self.logger.error("Image dimensions must be positive")
            errors.append("Image dimensions must be positive")

        if image_settings["quality"] < 1 or image_settings["quality"] > 100:
            self.logger.error("Image quality must be between 1 and 100")
            errors.append("Image quality must be between 1 and 100")

        # Check artwork settings
        artwork_settings = self.get_artwork_settings()
        if artwork_settings["max_cache_size"] <= 0:
            warnings.append("Artwork cache size should be positive")
            self.logger.warning("Artwork cache size should be positive")

        valid = len(errors) == 0
        if valid:
            self.logger.info("Configuration validated successfully")
        else:
            self.logger.error(
                "Configuration validation failed with %d errors", len(errors)
            )

        return {"valid": valid, "errors": errors, "warnings": warnings}

    def _get_default_config_path(self) -> str:
        """Get the default configuration file path."""
        config_dir = os.path.expanduser("~/.liturgical_calendar")
        try:
            os.makedirs(config_dir, exist_ok=True)
        except (OSError, PermissionError) as e:
            self.logger.error("Cannot create config directory %s: %s", config_dir, e)
            raise ConfigError(
                f"Cannot create config directory {config_dir}: {e}"
            ) from e
        return os.path.join(config_dir, "config.json")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "image": {
                "width": 1080,
                "height": 1080,
                "format": "PNG",
                "quality": 95,
                "background_color": "#FFFFFF",
                "font_family": "Arial",
                "font_size": 24,
                "text_color": "#000000",
            },
            "artwork": {
                "cache_dir": "./cache",
                "max_cache_size": 1000,
                "download_timeout": 30,
                "preferred_sources": ["met", "nga"],
                "fallback_artwork": "default.jpg",
            },
            "readings": {
                "include_psalm": True,
                "include_gospel": True,
                "include_epistle": True,
                "max_length": 200,
                "translation": "NRSV",
            },
            "output": {
                "directory": "./output",
                "filename_format": "liturgical_{date}.png",
                "create_subdirs": True,
                "overwrite_existing": False,
            },
            "logging": {
                "level": "INFO",
                "file": None,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "max_file_size": 10 * 1024 * 1024,
                "backup_count": 5,
            },
        }

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if not self.config_file:
            self.config_file = self._get_default_config_path()
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (OSError, ValueError, TypeError):
                # If file is corrupted, return defaults
                return self._get_default_config()
        else:
            # Create default config file
            self._config = self._get_default_config()
            self._save_config()
            return self._config

    def _save_config(self) -> None:
        """Save configuration to file."""

        def write_json(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2)

        try:
            safe_write_file(self.config_file, write_json, estimated_size=4096)
        except (OSError, ValueError, TypeError) as e:
            self.logger.error("Failed to save config file %s: %s", self.config_file, e)
            raise ConfigError(
                f"Failed to save config file {self.config_file}: {e}"
            ) from e
