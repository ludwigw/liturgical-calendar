from pathlib import Path
from PIL import ImageFont
from typing import Dict, Tuple, Any

class FontManager:
    def __init__(self, fonts_dir: Path):
        self.fonts_dir = Path(fonts_dir)
        self._cache: Dict[Tuple[str, int], Any] = {}

    def get_font(self, font_name: str, size: int):
        key = (font_name, size)
        if key in self._cache:
            return self._cache[key]
        font_path = self.fonts_dir / font_name
        font = ImageFont.truetype(str(font_path), size)
        self._cache[key] = font
        return font

    def get_text_size(self, text: str, font: Any) -> Tuple[int, int]:
        bbox = font.getbbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width, height

    def get_text_metrics(self, font: Any) -> Tuple[int, int]:
        return font.getmetrics() 