"""
Font management utilities for liturgical calendar image generation.
"""

import importlib.resources
from pathlib import Path
from typing import Any, Dict, Tuple

from PIL import ImageFont

from liturgical_calendar.logging import get_logger


class FontManager:
    """Manages font loading and caching for image generation."""

    def __init__(self, fonts_dir: Path = None):
        self._cache: Dict[Tuple[str, int], Any] = {}
        self.logger = get_logger(__name__)

        if fonts_dir:
            self.fonts_dir = Path(fonts_dir)
        else:
            # Use importlib.resources to locate fonts relative to the package
            self.fonts_dir = self._get_fonts_directory()

    def _get_fonts_directory(self) -> Path:
        """
        Get the fonts directory path using importlib.resources.

        This ensures fonts can be found regardless of where the script is run from,
        whether the package is installed or run from source.
        """
        try:
            # Try to get fonts from the package resources
            fonts_path = importlib.resources.files("liturgical_calendar") / "fonts"
            if fonts_path.exists():
                self.logger.debug("Found fonts directory in package: %s", fonts_path)
                return fonts_path
        except (ImportError, FileNotFoundError):
            pass

        # Fallback to relative path from current working directory
        fallback_path = Path("liturgical_calendar") / "fonts"
        self.logger.debug("Using fallback fonts directory: %s", fallback_path)
        return fallback_path

    def get_font(self, font_name: str, size: int):
        """Return a font object for the given parameters."""
        try:
            self.logger.info("Loading font: %s at size %s", font_name, size)
            key = (font_name, size)
            if key in self._cache:
                return self._cache[key]

            font_path = self.fonts_dir / font_name

            # Verify the font file exists
            if not font_path.exists():
                raise FileNotFoundError(f"Font file not found: {font_path}")

            font = ImageFont.truetype(str(font_path), size)
            self._cache[key] = font
            self.logger.info("Font loaded: %s at size %s", font_name, size)
            return font
        except Exception as e:
            self.logger.exception(
                "Error loading font %s at size %s: %s", font_name, size, e
            )
            raise

    def get_text_size(self, text: str, font: Any) -> Tuple[int, int]:
        """Calculate the width and height of text when rendered with the given font."""
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    def get_text_metrics(self, font: Any) -> Tuple[int, int]:
        """Get the ascent and descent metrics for the given font."""
        return font.getmetrics()
