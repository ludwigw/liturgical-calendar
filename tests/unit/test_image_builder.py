import os
import tempfile
import unittest

from PIL import Image, ImageFont

from liturgical_calendar.config.settings import Settings
from liturgical_calendar.image_generation.image_builder import LiturgicalImageBuilder


class DummyConfig:
    IMAGE_WIDTH = 200
    IMAGE_HEIGHT = 100
    BG_COLOR = Settings.BG_COLOR


class TestLiturgicalImageBuilder(unittest.TestCase):
    def setUp(self):
        self.builder = LiturgicalImageBuilder(DummyConfig)
        self.font = ImageFont.load_default()
        self.tempdir = tempfile.TemporaryDirectory()
        self.tempfile = os.path.join(self.tempdir.name, "test.png")

    def tearDown(self):
        self.tempdir.cleanup()

    def test_create_base_image(self):
        img = self.builder.create_base_image()
        self.assertEqual(img.size, (DummyConfig.IMAGE_WIDTH, DummyConfig.IMAGE_HEIGHT))
        self.assertEqual(img.getpixel((0, 0)), DummyConfig.BG_COLOR)

    def test_paste_artwork_with_valid_file(self):
        # Create a small red image to use as artwork
        art_path = os.path.join(self.tempdir.name, "art.png")
        Image.new("RGB", (10, 10), (255, 0, 0)).save(art_path)
        img = self.builder.create_base_image()
        self.builder.paste_artwork(img, art_path, (0, 0), (10, 10))
        self.assertEqual(img.getpixel((5, 5)), (255, 0, 0))

    def test_paste_artwork_with_missing_file(self):
        img = self.builder.create_base_image()
        self.builder.paste_artwork(img, "nonexistent.png", (0, 0), (10, 10))
        self.assertEqual(img.getpixel((5, 5)), (230, 230, 230))

    def test_paste_artwork_with_none(self):
        img = self.builder.create_base_image()
        self.builder.paste_artwork(img, None, (0, 0), (10, 10))
        self.assertEqual(img.getpixel((5, 5)), (230, 230, 230))

    def test_draw_text(self):
        img = self.builder.create_base_image()
        self.builder.draw_text(img, "A", (5, 5), self.font, (0, 0, 0))
        # Just check that the image is still an image and no error is raised
        self.assertEqual(img.size, (DummyConfig.IMAGE_WIDTH, DummyConfig.IMAGE_HEIGHT))

    def test_build_image_minimal(self):
        # Minimal layout dict for a full build
        layout = {
            "header": {
                "season": {"text": "S", "font": self.font, "pos": (0, 0)},
                "dash": {"text": "-", "font": self.font, "pos": (10, 0)},
                "date": {"text": "D", "font": self.font, "pos": (20, 0)},
                "baseline_y": 10,
                "height": 10,
            },
            "artwork": {
                "main": {"artwork": None, "pos": (0, 10), "size": (10, 10)},
                "show_next": False,
            },
            "title": {
                "lines": [{"text": "T", "font": self.font, "pos": (0, 20)}],
                "last_baseline": 30,
            },
            "readings": {
                "week": {"text": "W", "font": self.font, "pos": (0, 40)},
                "readings": [{"text": "R", "font": self.font, "pos": (10, 40)}],
                "vertical_line": {"rect": [5, 35, 6, 50]},
                "last_baseline": 50,
            },
            "colors": {
                "text": (0, 0, 0),
                "line": (100, 100, 100),
            },
        }
        fonts = {"serif": self.font}
        out_path = self.tempfile
        result_path = self.builder.build_image(
            "2022-01-01", {}, {}, layout, fonts, out_path
        )
        self.assertTrue(os.path.isfile(result_path))
        img = Image.open(result_path)
        self.assertEqual(img.size, (DummyConfig.IMAGE_WIDTH, DummyConfig.IMAGE_HEIGHT))


if __name__ == "__main__":
    unittest.main()
