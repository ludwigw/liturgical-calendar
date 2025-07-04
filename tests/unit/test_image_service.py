"""
Tests for the ImageService class.

This module tests the ImageService's ability to orchestrate image generation
operations and coordinate between different components.
"""

import unittest
import os
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from liturgical_calendar.services.image_service import ImageService
from liturgical_calendar.core.artwork_manager import ArtworkManager
from liturgical_calendar.core.readings_manager import ReadingsManager
from liturgical_calendar.core.season_calculator import SeasonCalculator
from liturgical_calendar.services.feast_service import FeastService


class TestImageService(unittest.TestCase):
    """Test cases for the ImageService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_artwork_manager = Mock(spec=ArtworkManager)
        self.mock_readings_manager = Mock(spec=ReadingsManager)
        self.mock_season_calculator = Mock(spec=SeasonCalculator)
        self.mock_feast_service = Mock(spec=FeastService)
        
        # Create a mock config object
        self.mock_config = Mock()
        self.mock_config.IMAGE_WIDTH = 1404
        self.mock_config.IMAGE_HEIGHT = 1872
        self.mock_config.FONTS_DIR = "fonts"
        self.mock_config.PADDING = 48
        self.mock_config.ARTWORK_SIZE = 1080
        self.mock_config.ROW_SPACING = 48
        self.mock_config.HEADER_FONT_SIZE = 36
        self.mock_config.TITLE_FONT_SIZE = 96
        self.mock_config.TITLE_LINE_HEIGHT = 1.2
        self.mock_config.COLUMN_FONT_SIZE = 36
        self.mock_config.BG_COLOR = (255, 255, 255)
        self.mock_config.TEXT_COLOR = (74, 74, 74)
        self.mock_config.LINE_COLOR = (151, 151, 151)
        
        self.image_service = ImageService(
            artwork_manager=self.mock_artwork_manager,
            readings_manager=self.mock_readings_manager,
            season_calculator=self.mock_season_calculator,
            feast_service=self.mock_feast_service,
            config=self.mock_config
        )
    
    def test_init_with_dependencies(self):
        """Test initialization with injected dependencies."""
        service = ImageService(
            artwork_manager=self.mock_artwork_manager,
            readings_manager=self.mock_readings_manager,
            season_calculator=self.mock_season_calculator,
            feast_service=self.mock_feast_service
        )
        
        self.assertEqual(service.artwork_manager, self.mock_artwork_manager)
        self.assertEqual(service.readings_manager, self.mock_readings_manager)
        self.assertEqual(service.season_calculator, self.mock_season_calculator)
        self.assertEqual(service.feast_service, self.mock_feast_service)
    
    def test_init_without_dependencies(self):
        """Test initialization without injected dependencies."""
        with patch('liturgical_calendar.services.image_service.ArtworkManager') as mock_artwork:
            with patch('liturgical_calendar.services.image_service.ReadingsManager') as mock_readings:
                with patch('liturgical_calendar.services.image_service.SeasonCalculator') as mock_calc:
                    with patch('liturgical_calendar.services.image_service.FeastService') as mock_feast:
                        # Create a mock config for the service
                        mock_config = Mock()
                        service = ImageService(config=mock_config)
                        
                        mock_artwork.assert_called_once()
                        mock_readings.assert_called_once()
                        mock_calc.assert_called_once()
                        mock_feast.assert_called_once()
    
    def test_generate_liturgical_image_success(self):
        """Test successful image generation."""
        # Mock feast service
        feast_info = {
            'name': 'Easter Sunday',
            'season': 'Easter',
            'week': 'Easter 2',
            'weekno': 2,
            'colour': 'white',
            'colourcode': '#FFFFFF',
            'readings': {'gospel': 'John 20:19-31'},
            'date': date(2023, 4, 16)
        }
        self.mock_feast_service.get_complete_feast_info.return_value = feast_info
        
        # Mock artwork manager
        artwork_info = {
            'url': 'https://example.com/artwork.jpg',
            'title': 'Resurrection',
            'artist': 'Unknown'
        }
        self.mock_artwork_manager.get_artwork_for_date.return_value = artwork_info
        
        # Mock the pipeline
        with patch('liturgical_calendar.image_generation.pipeline.ImageGenerationPipeline') as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline.generate_image.return_value = '/tmp/test_output.png'
            mock_pipeline_class.return_value = mock_pipeline
            
            result = self.image_service.generate_liturgical_image('2023-04-16')
        
        # Verify the result
        self.assertTrue(result['success'])
        self.assertEqual(result['date'], '2023-04-16')
        self.assertEqual(result['feast_info'], feast_info)
        self.assertEqual(result['artwork_info'], artwork_info)
        self.assertTrue(result['image_generated'])
        self.assertEqual(result['file_path'], '/tmp/test_output.png')
        
        # Verify service calls
        self.mock_feast_service.get_complete_feast_info.assert_called_once_with('2023-04-16', False)
        self.mock_artwork_manager.get_artwork_for_date.assert_called_once_with('2023-04-16', feast_info)
    
    def test_generate_liturgical_image_no_feast_info(self):
        """Test image generation when no feast info is available."""
        self.mock_feast_service.get_complete_feast_info.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.image_service.generate_liturgical_image('2023-04-16')
        
        self.assertIn("No feast information found for date: 2023-04-16", str(context.exception))
    
    def test_generate_liturgical_image_with_output_path(self):
        """Test image generation with output path."""
        # Mock feast service
        feast_info = {
            'name': 'Easter Sunday',
            'season': 'Easter',
            'colour': 'white',
            'date': date(2023, 4, 16)
        }
        self.mock_feast_service.get_complete_feast_info.return_value = feast_info
        
        # Mock artwork manager
        artwork_info = {
            'url': 'https://example.com/artwork.jpg',
            'title': 'Resurrection',
            'artist': 'Unknown'
        }
        self.mock_artwork_manager.get_artwork_for_date.return_value = artwork_info
        
        # Mock the pipeline
        with patch('liturgical_calendar.image_generation.pipeline.ImageGenerationPipeline') as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline.generate_image.return_value = '/tmp/test.png'
            mock_pipeline_class.return_value = mock_pipeline
            
            result = self.image_service.generate_liturgical_image(
                '2023-04-16', 
                output_path='/tmp/test.png'
            )
        
        self.assertEqual(result['file_path'], '/tmp/test.png')
        # Verify artwork manager was called with correct parameters
        self.mock_artwork_manager.get_artwork_for_date.assert_called_once_with('2023-04-16', feast_info)
    
    def test_generate_multiple_images_success(self):
        """Test generating multiple images successfully."""
        # Mock feast service
        feast_info = {
            'name': 'Easter Sunday',
            'season': 'Easter',
            'colour': 'white',
            'date': date(2023, 4, 16)
        }
        self.mock_feast_service.get_complete_feast_info.return_value = feast_info
        
        # Mock artwork manager
        artwork_info = {
            'url': 'https://example.com/artwork.jpg',
            'title': 'Resurrection',
            'artist': 'Unknown'
        }
        self.mock_artwork_manager.get_artwork_for_date.return_value = artwork_info
        
        date_list = ['2023-04-16', '2023-04-17']
        
        # Mock the pipeline
        with patch('liturgical_calendar.image_generation.pipeline.ImageGenerationPipeline') as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline.generate_image.return_value = '/tmp/liturgical_2023-04-16.png'
            mock_pipeline_class.return_value = mock_pipeline
            
            results = self.image_service.generate_multiple_images(date_list, '/tmp')
        
        self.assertEqual(len(results), 2)
        self.assertTrue(all(result['success'] for result in results))
        self.assertEqual(results[0]['date'], '2023-04-16')
        self.assertEqual(results[1]['date'], '2023-04-17')
    
    def test_generate_multiple_images_with_errors(self):
        """Test generating multiple images with some errors."""
        # Mock feast service to raise exception for second date
        def mock_get_feast_info(date_str, transferred=False):
            if date_str == '2023-04-17':
                raise ValueError("Test error")
            return {
                'name': 'Easter Sunday',
                'season': 'Easter',
                'colour': 'white',
                'date': date(2023, 4, 16)
            }
        
        self.mock_feast_service.get_complete_feast_info.side_effect = mock_get_feast_info
        
        # Mock artwork manager
        artwork_info = {
            'url': 'https://example.com/artwork.jpg',
            'title': 'Resurrection',
            'artist': 'Unknown'
        }
        self.mock_artwork_manager.get_artwork_for_date.return_value = artwork_info
        
        date_list = ['2023-04-16', '2023-04-17']
        
        # Mock the pipeline
        with patch('liturgical_calendar.image_generation.pipeline.ImageGenerationPipeline') as mock_pipeline_class:
            mock_pipeline = Mock()
            mock_pipeline.generate_image.return_value = '/tmp/liturgical_2023-04-16.png'
            mock_pipeline_class.return_value = mock_pipeline
            
            results = self.image_service.generate_multiple_images(date_list)
        
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0]['success'])
        self.assertFalse(results[1]['success'])
        self.assertIn('error', results[1])
    
    def test_select_artwork_feast_specific(self):
        """Test artwork selection for feast-specific artwork."""
        feast_info = {'name': 'Easter Sunday', 'season': 'Easter', 'date': date(2023, 4, 16)}
        artwork_info = {'url': 'https://example.com/easter.jpg'}
        
        self.mock_artwork_manager.get_artwork_for_date.return_value = artwork_info
        
        result = self.image_service._select_artwork(feast_info)
        
        self.assertEqual(result, artwork_info)
        self.mock_artwork_manager.get_artwork_for_date.assert_called_once_with('2023-04-16', feast_info)
    
    def test_select_artwork_no_artwork_found(self):
        """Test artwork selection when no artwork is found."""
        feast_info = {'name': 'Easter Sunday', 'season': 'Easter', 'date': date(2023, 4, 16)}
        
        self.mock_artwork_manager.get_artwork_for_date.return_value = None
        
        result = self.image_service._select_artwork(feast_info)
        
        self.assertEqual(result, {})
        self.mock_artwork_manager.get_artwork_for_date.assert_called_once_with('2023-04-16', feast_info)
    
    def test_select_artwork_no_date_in_feast_info(self):
        """Test artwork selection when feast_info has no date."""
        feast_info = {'name': 'Easter Sunday', 'season': 'Easter'}
        
        result = self.image_service._select_artwork(feast_info)
        
        self.assertEqual(result, {})
        # Should not call artwork manager since there's no date
        self.mock_artwork_manager.get_artwork_for_date.assert_not_called()
    
    def test_prepare_image_data(self):
        """Test image data preparation."""
        feast_info = {
            'name': 'Easter Sunday',
            'season': 'Easter',
            'week': 'Easter 2',
            'weekno': 2,
            'colour': 'white',
            'colourcode': '#FFFFFF',
            'readings': {'gospel': 'John 20:19-31'},
            'date': date(2023, 4, 16),
            'weekday_reading': 'Easter 2',
            'martyr': False,
            'type': 'Feast'
        }
        
        artwork_info = {
            'url': 'https://example.com/artwork.jpg',
            'title': 'Resurrection',
            'artist': 'Unknown'
        }
        
        result = self.image_service._prepare_image_data(feast_info, artwork_info)
        
        expected_data = {
            'name': 'Easter Sunday',
            'season': 'Easter',
            'week': 'Easter 2',
            'weekno': 2,
            'colour': 'white',
            'colourcode': '#FFFFFF',
            'readings': {'gospel': 'John 20:19-31'},
            'date': date(2023, 4, 16),
            'weekday_reading': 'Easter 2',
            'feast_type': 'Feast',
            'artwork_info': artwork_info,
            'url': 'https://example.com/artwork.jpg',
            'title': 'Resurrection',
            'artist': 'Unknown',
            'cached_file': '',
            'artwork_name': ''  # Artwork name
        }
        
        self.assertEqual(result, expected_data)
    
    def test_prepare_image_data_with_martyr(self):
        """Test image data preparation with martyr feast."""
        feast_info = {
            'name': 'St. Stephen',
            'season': 'Christmas',
            'colour': 'red',
            'martyr': True,
            'date': date(2023, 12, 26)
        }
        
        artwork_info = {
            'url': 'https://example.com/artwork.jpg',
            'title': 'St. Stephen',
            'artist': 'Unknown'
        }
        
        result = self.image_service._prepare_image_data(feast_info, artwork_info)
        
        self.assertTrue(result['martyr'])
        self.assertEqual(result['name'], 'St. Stephen')
    
    def test_validate_image_data_valid(self):
        """Test validation of valid image data."""
        valid_data = {
            'name': 'Easter Sunday',
            'season': 'Easter',
            'colour': 'white'
        }
        
        self.assertTrue(self.image_service.validate_image_data(valid_data))
    
    def test_validate_image_data_invalid(self):
        """Test validation of invalid image data."""
        invalid_data = {
            'season': 'Easter',
            'colour': 'white'
            # Missing 'name' field
        }
        
        self.assertFalse(self.image_service.validate_image_data(invalid_data))
    
    def test_validate_image_data_empty(self):
        """Test validation of empty image data."""
        self.assertFalse(self.image_service.validate_image_data({}))
    
    def test_get_image_generation_stats(self):
        """Test image generation statistics."""
        results = [
            {
                'success': True,
                'feast_info': {'season': 'Easter', 'colour': 'white'}
            },
            {
                'success': True,
                'feast_info': {'season': 'Easter', 'colour': 'white'}
            },
            {
                'success': False,
                'error': 'Test error'
            },
            {
                'success': True,
                'feast_info': {'season': 'Advent', 'colour': 'purple'}
            }
        ]
        
        stats = self.image_service.get_image_generation_stats(results)
        
        self.assertEqual(stats['total'], 4)
        self.assertEqual(stats['successful'], 3)
        self.assertEqual(stats['failed'], 1)
        self.assertEqual(stats['success_rate'], 0.75)
        self.assertEqual(stats['season_counts']['Easter'], 2)
        self.assertEqual(stats['season_counts']['Advent'], 1)
        self.assertEqual(stats['color_counts']['white'], 2)
        self.assertEqual(stats['color_counts']['purple'], 1)


if __name__ == '__main__':
    unittest.main() 