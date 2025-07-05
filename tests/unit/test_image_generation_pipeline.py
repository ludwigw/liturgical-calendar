import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from PIL import ImageFont
from liturgical_calendar.image_generation.pipeline import ImageGenerationPipeline
from liturgical_calendar.config.settings import Settings

class DummyConfig:
    IMAGE_WIDTH = 100
    IMAGE_HEIGHT = 100
    BG_COLOR = Settings.BG_COLOR
    TEXT_COLOR = (0, 0, 0)
    LINE_COLOR = (100, 100, 100)
    FONTS_DIR = Settings.FONTS_DIR
    PADDING = Settings.PADDING
    ARTWORK_SIZE = 50
    ROW_SPACING = 5
    HEADER_FONT_SIZE = 10
    TITLE_FONT_SIZE = 20
    TITLE_LINE_HEIGHT = 1.1
    COLUMN_FONT_SIZE = 10

class TestImageGenerationPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = ImageGenerationPipeline(DummyConfig)
        # Patch services directly on the instance
        self.mock_feast = MagicMock()
        self.mock_image = MagicMock()
        self.pipeline.feast_service = self.mock_feast
        self.pipeline.image_service = self.mock_image
        # Patch font_manager.get_font to always return default font
        self.font_patch = patch.object(self.pipeline.font_manager, 'get_font', return_value=ImageFont.load_default())
        self.font_patch.start()
        # Patch builder directly on the instance
        self.mock_builder = MagicMock()
        self.pipeline.builder = self.mock_builder

    def tearDown(self):
        self.font_patch.stop()

    def test_instantiation(self):
        self.assertIsInstance(self.pipeline, ImageGenerationPipeline)
        self.assertEqual(self.pipeline.width, 100)
        self.assertEqual(self.pipeline.bg_color, (255, 255, 255))

    def test_prepare_data_with_and_without_artwork(self):
        self.mock_feast.get_liturgical_info.return_value = {'season': 'Test', 'week': 'Test', 'readings': ['R1']}
        # Patch artwork_manager.get_artwork_for_date for this test
        with patch.object(self.pipeline.artwork_manager, 'get_artwork_for_date') as mock_get_artwork:
            # Case 1: artwork present
            mock_get_artwork.return_value = {'cached_file': 'foo.png', 'name': 'Art'}
            data = self.pipeline._prepare_data('2022-01-01')
            self.assertEqual(data['artwork']['cached_file'], 'foo.png')
            # Case 2: artwork missing, next_artwork found
            mock_get_artwork.side_effect = [None, {'cached_file': 'bar.png', 'name': 'NextArt'}]
            data2 = self.pipeline._prepare_data('2022-01-02')
            self.assertIsNone(data2['artwork'])
            self.assertEqual(data2['next_artwork']['cached_file'], 'bar.png')

    @patch('liturgical_calendar.image_generation.pipeline.LiturgicalImageBuilder')
    def test_create_layout_structure(self, MockBuilder):
        # Minimal data
        data = {
            'info': {'season': 'Test', 'week': 'Test', 'readings': ['R1']},
            'friendly_date': '1 Jan 2022',
            'artwork': {'name': 'Art'},
            'next_artwork': None,
            'date': MagicMock(strftime=lambda fmt: 'Saturday'),
        }
        layout, fonts = self.pipeline._create_layout(data)
        self.assertIn('header', layout)
        self.assertIn('artwork', layout)
        self.assertIn('title', layout)
        self.assertIn('readings', layout)
        self.assertIn('colors', layout)
        self.assertIn('serif', fonts)
        self.assertIn('sans', fonts)

    def test_generate_image_calls_builder(self):
        self.mock_feast.get_liturgical_info.return_value = {'season': 'Test', 'week': 'Test', 'readings': ['R1']}
        self.mock_image.get_artwork_for_date.return_value = {'cached_file': 'foo.png', 'name': 'Art'}
        self.mock_builder.build_image.return_value = 'output.png'
        out_path = self.pipeline.generate_image('2022-01-01', out_path='dummy.png')
        self.mock_builder.build_image.assert_called()
        self.assertEqual(out_path, 'dummy.png')

if __name__ == '__main__':
    unittest.main() 