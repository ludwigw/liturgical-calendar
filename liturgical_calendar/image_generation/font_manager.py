from pathlib import Path
from typing import Any, Dict, Tuple

from PIL import ImageFont

from liturgical_calendar.config.settings import Settings
from liturgical_calendar.logging import get_logger


class FontManager:
    def __init__(self, fonts_dir: Path = None):
        self.fonts_dir = Path(fonts_dir) if fonts_dir else Path(Settings.FONTS_DIR)
        self._cache: Dict[Tuple[str, int], Any] = {}
        self.logger = get_logger(__name__)

    def get_font(self, font_name: str, size: int):
        try:
            self.logger.info(f"Loading font: {font_name} at size {size}")
            key = (font_name, size)
            if key in self._cache:
                return self._cache[key]
            font_path = self.fonts_dir / font_name
            font = ImageFont.truetype(str(font_path), size)
            self._cache[key] = font
            self.logger.info(f"Font loaded: {font_name} at size {size}")
            return font
        except Exception as e:
            self.logger.exception(f"Error loading font {font_name} at size {size}: {e}")
            raise

    def get_text_size(self, text: str, font: Any) -> Tuple[int, int]:
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    def get_text_metrics(self, font: Any) -> Tuple[int, int]:
        return font.getmetrics()
