import unittest
import os
from pathlib import Path
from liturgical_calendar.image_generation.font_manager import FontManager
from liturgical_calendar.config.settings import Settings

FONTS_DIR = Settings.FONTS_DIR
SANS_FONT = 'HankenGrotesk-Medium.ttf'
SERIF_FONT = 'HappyTimes-Regular.otf'

class TestFontManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.font_manager = FontManager(FONTS_DIR)
        cls.sans_font_path = FONTS_DIR / SANS_FONT
        cls.serif_font_path = FONTS_DIR / SERIF_FONT

    def test_get_font_loads_font(self):
        if not self.sans_font_path.exists():
            self.skipTest(f"Font file {self.sans_font_path} not found.")
        font = self.font_manager.get_font(SANS_FONT, 24)
        self.assertIsNotNone(font)
        self.assertTrue(hasattr(font, 'getmetrics'))

    def test_get_font_caching(self):
        if not self.sans_font_path.exists():
            self.skipTest(f"Font file {self.sans_font_path} not found.")
        font1 = self.font_manager.get_font(SANS_FONT, 24)
        font2 = self.font_manager.get_font(SANS_FONT, 24)
        self.assertIs(font1, font2)

    def test_get_text_size(self):
        if not self.sans_font_path.exists():
            self.skipTest(f"Font file {self.sans_font_path} not found.")
        font = self.font_manager.get_font(SANS_FONT, 24)
        w, h = self.font_manager.get_text_size("Hello World", font)
        self.assertIsInstance(w, int)
        self.assertIsInstance(h, int)
        self.assertGreater(w, 0)
        self.assertGreater(h, 0)

    def test_get_text_metrics(self):
        if not self.sans_font_path.exists():
            self.skipTest(f"Font file {self.sans_font_path} not found.")
        font = self.font_manager.get_font(SANS_FONT, 24)
        ascent, descent = self.font_manager.get_text_metrics(font)
        self.assertIsInstance(ascent, int)
        self.assertIsInstance(descent, int)
        self.assertGreater(ascent, 0)
        self.assertGreaterEqual(descent, 0)

    def test_missing_font_raises(self):
        with self.assertRaises(OSError):
            self.font_manager.get_font("not_a_real_font.ttf", 24)

if __name__ == '__main__':
    unittest.main() 