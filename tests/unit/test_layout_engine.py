import unittest
from unittest.mock import MagicMock
from liturgical_calendar.image_generation.layout_engine import LayoutEngine

class DummyFont:
    def __init__(self, ascent=10, descent=2, width=100, height=20):
        self._ascent = ascent
        self._descent = descent
        self._width = width
        self._height = height
    def getmetrics(self):
        return (self._ascent, self._descent)
    def getbbox(self, text):
        # Return a bbox with width proportional to text length
        w = self._width + len(text) * 5
        h = self._height
        return (0, 0, w, h)

class DummyDraw:
    def textbbox(self, pos, text, font=None):
        return font.getbbox(text)

class TestLayoutEngine(unittest.TestCase):
    def setUp(self):
        self.engine = LayoutEngine()
        self.dummy_font = DummyFont()
        self.dummy_draw = DummyDraw()
        self.fonts = {
            'sans_uc': self.dummy_font,
            'serif': self.dummy_font,
            'sans': self.dummy_font,
            'serif_96': self.dummy_font,
            'sans_32': self.dummy_font,
            'sans_26': self.dummy_font,
        }

    def test_create_header_layout(self):
        layout = self.engine.create_header_layout(
            season="Easter",
            date="1 April 2024",
            fonts=self.fonts,
            draw=self.dummy_draw,
            width=500,
            padding=10
        )
        self.assertIn('season', layout)
        self.assertIn('date', layout)
        self.assertIn('dash', layout)
        self.assertIn('baseline_y', layout)
        self.assertIn('height', layout)
        self.assertIsInstance(layout['season']['pos'], tuple)

    def test_create_artwork_layout_main(self):
        artwork = {'name': 'Jesus', 'cached_file': 'foo.png'}
        layout = self.engine.create_artwork_layout(
            artwork=artwork,
            next_artwork=None,
            width=500,
            art_size=200,
            y=50,
            fonts=self.fonts,
            draw=self.dummy_draw
        )
        self.assertIn('main', layout)
        self.assertFalse(layout['show_next'])
        self.assertEqual(layout['main']['artwork'], artwork)

    def test_create_artwork_layout_with_next(self):
        artwork = {'name': 'Jesus', 'cached_file': 'foo.png'}
        next_artwork = {'name': 'Mary', 'cached_file': 'bar.png', 'date': '2 April 2024'}
        class DummyFontManager:
            def get_text_size(self, text, font):
                return (100, 20)
            def get_text_metrics(self, font):
                return (10, 2)
        dummy_font_manager = DummyFontManager()
        layout = self.engine.create_artwork_layout(
            artwork=artwork,
            next_artwork=next_artwork,
            width=500,
            art_size=200,
            y=50,
            fonts=self.fonts,
            draw=self.dummy_draw,
            font_manager=dummy_font_manager
        )
        self.assertTrue(layout['show_next'])
        self.assertIn('next', layout)
        self.assertIn('next_label', layout)
        self.assertIn('next_title', layout)
        self.assertIn('next_date', layout)

    def test_create_title_layout(self):
        layout = self.engine.create_title_layout(
            title="The Resurrection",
            fonts={'serif_96': self.dummy_font},
            draw=self.dummy_draw,
            width=500,
            padding=10,
            title_font_size=96,
            title_line_height=1.2,
            start_y=300
        )
        self.assertIn('lines', layout)
        self.assertGreaterEqual(len(layout['lines']), 1)
        for line in layout['lines']:
            self.assertIn('text', line)
            self.assertIn('font', line)
            self.assertIn('pos', line)
        self.assertIn('last_baseline', layout)

    def test_create_readings_layout(self):
        week = "EASTER 2"
        readings = ["Acts 2:14a,22-32", "Psalm 16", "1 Peter 1:3-9", "John 20:19-31"]
        layout = self.engine.create_readings_layout(
            week=week,
            readings=readings,
            fonts={'serif': self.dummy_font, 'sans_uc': self.dummy_font},
            draw=self.dummy_draw,
            width=800,
            padding=20,
            start_y=600,
            line_height=48
        )
        self.assertIn('week', layout)
        self.assertIn('readings', layout)
        self.assertIn('vertical_line', layout)
        self.assertIn('last_baseline', layout)
        self.assertEqual(len(layout['readings']), len(readings))

if __name__ == '__main__':
    unittest.main() 