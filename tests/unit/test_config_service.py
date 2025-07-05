"""
Tests for the ConfigService class.

This module tests the ConfigService's ability to manage configuration
settings and provide a centralized way to access and modify configuration.
"""

import unittest
import os
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, mock_open
from liturgical_calendar.services.config_service import ConfigService


class TestConfigService(unittest.TestCase):
    """Test cases for the ConfigService class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'test_config.json')
        self.config_service = ConfigService(self.config_file)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_with_config_file(self):
        """Test initialization with specific config file."""
        service = ConfigService(self.config_file)
        self.assertEqual(service.config_file, self.config_file)
    
    def test_init_without_config_file(self):
        """Test initialization without config file."""
        with patch.object(ConfigService, '_get_default_config_path') as mock_path:
            mock_path.return_value = '/tmp/default_config.json'
            service = ConfigService()
            self.assertEqual(service.config_file, '/tmp/default_config.json')
    
    def test_get_simple_key(self):
        """Test getting a simple configuration key."""
        test_config = {'test_key': 'test_value'}
        self.config_service._config = test_config
        
        result = self.config_service.get('test_key')
        self.assertEqual(result, 'test_value')
    
    def test_get_nested_key(self):
        """Test getting a nested configuration key."""
        test_config = {
            'section': {
                'subsection': {
                    'key': 'value'
                }
            }
        }
        self.config_service._config = test_config
        
        result = self.config_service.get('section.subsection.key')
        self.assertEqual(result, 'value')
    
    def test_get_key_with_default(self):
        """Test getting a key with default value."""
        result = self.config_service.get('nonexistent_key', 'default_value')
        self.assertEqual(result, 'default_value')
    
    def test_get_nonexistent_nested_key(self):
        """Test getting a nonexistent nested key."""
        test_config = {'section': {'existing': 'value'}}
        self.config_service._config = test_config
        
        result = self.config_service.get('section.nonexistent', 'default')
        self.assertEqual(result, 'default')
    
    def test_set_simple_key(self):
        """Test setting a simple configuration key."""
        self.config_service.set('test_key', 'test_value')
        self.assertEqual(self.config_service._config['test_key'], 'test_value')
    
    def test_set_nested_key(self):
        """Test setting a nested configuration key."""
        self.config_service.set('section.subsection.key', 'value')
        self.assertEqual(self.config_service._config['section']['subsection']['key'], 'value')
    
    def test_set_nested_key_creates_structure(self):
        """Test that setting nested keys creates the necessary structure."""
        self.config_service.set('new.section.key', 'value')
        
        self.assertIn('new', self.config_service._config)
        self.assertIn('section', self.config_service._config['new'])
        self.assertEqual(self.config_service._config['new']['section']['key'], 'value')
    
    def test_get_all(self):
        """Test getting all configuration values."""
        test_config = {'key1': 'value1', 'key2': 'value2'}
        self.config_service._config = test_config
        
        result = self.config_service.get_all()
        self.assertEqual(result, test_config)
        self.assertIsNot(result, test_config)  # Should be a copy
    
    def test_reset_to_defaults(self):
        """Test resetting configuration to default values."""
        # Set some custom values
        self.config_service.set('custom.key', 'custom_value')
        
        # Reset to defaults
        self.config_service.reset_to_defaults()
        
        # Check that custom values are gone and defaults are present
        self.assertIsNone(self.config_service.get('custom.key'))
        self.assertEqual(self.config_service.get('image.width'), 1080)
        self.assertEqual(self.config_service.get('artwork.cache_dir'), './cache')
    
    def test_get_image_settings(self):
        """Test getting image generation settings."""
        settings = self.config_service.get_image_settings()
        
        expected_settings = {
            'width': 1080,
            'height': 1080,
            'format': 'PNG',
            'quality': 95,
            'background_color': '#FFFFFF',
            'font_family': 'Arial',
            'font_size': 24,
            'text_color': '#000000'
        }
        
        self.assertEqual(settings, expected_settings)
    
    def test_get_artwork_settings(self):
        """Test getting artwork settings."""
        settings = self.config_service.get_artwork_settings()
        
        expected_settings = {
            'cache_dir': './cache',
            'max_cache_size': 1000,
            'download_timeout': 30,
            'preferred_sources': ['met', 'nga'],
            'fallback_artwork': 'default.jpg'
        }
        
        self.assertEqual(settings, expected_settings)
    
    def test_get_readings_settings(self):
        """Test getting readings settings."""
        settings = self.config_service.get_readings_settings()
        
        expected_settings = {
            'include_psalm': True,
            'include_gospel': True,
            'include_epistle': True,
            'max_reading_length': 200,
            'translation': 'NRSV'
        }
        
        self.assertEqual(settings, expected_settings)
    
    def test_get_output_settings(self):
        """Test getting output settings."""
        settings = self.config_service.get_output_settings()
        
        expected_settings = {
            'output_dir': './output',
            'filename_format': 'liturgical_{date}.png',
            'create_subdirs': True,
            'overwrite_existing': False
        }
        
        self.assertEqual(settings, expected_settings)
    
    def test_get_logging_settings(self):
        """Test getting logging settings."""
        settings = self.config_service.get_logging_settings()
        
        expected_settings = {
            'level': 'INFO',
            'file': None,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'max_file_size': 10 * 1024 * 1024,
            'backup_count': 5
        }
        
        self.assertEqual(settings, expected_settings)
    
    def test_validate_config_valid(self):
        """Test configuration validation with valid settings."""
        # Create a valid configuration
        self.config_service.set('image.width', 1080)
        self.config_service.set('image.height', 1080)
        self.config_service.set('image.quality', 95)
        self.config_service.set('artwork.cache_dir', self.temp_dir)
        self.config_service.set('output.directory', self.temp_dir)
        
        result = self.config_service.validate_config()
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
        self.assertEqual(len(result['warnings']), 0)
    
    def test_validate_config_invalid_dimensions(self):
        """Test configuration validation with invalid image dimensions."""
        self.config_service.set('image.width', -1)
        self.config_service.set('image.height', 0)
        
        result = self.config_service.validate_config()
        
        self.assertFalse(result['valid'])
        self.assertEqual(len(result['errors']), 1)
        self.assertIn("Image dimensions must be positive", result['errors'][0])
    
    def test_validate_config_invalid_quality(self):
        """Test configuration validation with invalid image quality."""
        self.config_service.set('image.quality', 150)
        
        result = self.config_service.validate_config()
        
        self.assertFalse(result['valid'])
        self.assertEqual(len(result['errors']), 1)
        self.assertIn("Image quality must be between 1 and 100", result['errors'][0])
    
    def test_validate_config_invalid_cache_size(self):
        """Test configuration validation with invalid cache size."""
        self.config_service.set('artwork.max_cache_size', -1)
        
        result = self.config_service.validate_config()
        
        self.assertTrue(result['valid'])  # Warnings don't make config invalid
        self.assertEqual(len(result['warnings']), 1)
        self.assertIn("Artwork cache size should be positive", result['warnings'][0])
    
    def test_validate_config_creates_directories(self):
        """Test that validation creates required directories."""
        non_existent_dir = os.path.join(self.temp_dir, 'new_dir')
        self.config_service.set('artwork.cache_dir', non_existent_dir)
        self.config_service.set('output.directory', non_existent_dir)
        
        result = self.config_service.validate_config()
        
        self.assertTrue(result['valid'])
        self.assertTrue(os.path.exists(non_existent_dir))
    
    def test_load_config_existing_file(self):
        """Test loading configuration from existing file."""
        test_config = {'test_key': 'test_value'}
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
        
        # Create new service instance to trigger loading
        service = ConfigService(self.config_file)
        
        self.assertEqual(service.get('test_key'), 'test_value')
    
    def test_load_config_corrupted_file(self):
        """Test loading configuration from corrupted file."""
        # Write invalid JSON
        with open(self.config_file, 'w') as f:
            f.write('invalid json content')
        
        # Create new service instance to trigger loading
        service = ConfigService(self.config_file)
        
        # Should fall back to defaults
        self.assertEqual(service.get('image.width'), 1080)
        self.assertEqual(service.get('artwork.cache_dir'), './cache')
    
    def test_load_config_nonexistent_file(self):
        """Test loading configuration from nonexistent file."""
        # Remove the config file if it exists
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        
        # Create new service instance to trigger loading
        service = ConfigService(self.config_file)
        
        # Should create default config file
        self.assertTrue(os.path.exists(self.config_file))
        self.assertEqual(service.get('image.width'), 1080)
    
    def test_save_config(self):
        """Test saving configuration to file."""
        self.config_service.set('test_key', 'test_value')
        self.config_service.save()
        
        # Verify file was written
        self.assertTrue(os.path.exists(self.config_file))
        
        # Read and verify content
        with open(self.config_file, 'r') as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config['test_key'], 'test_value')
    
    def test_save_config_error(self):
        """Test saving configuration with error."""
        # Make the directory read-only to cause a save error
        os.chmod(self.temp_dir, 0o444)
        
        try:
            with self.assertRaises(RuntimeError) as context:
                self.config_service.save()
            self.assertIn("Failed to save configuration", str(context.exception))
        finally:
            # Restore permissions
            os.chmod(self.temp_dir, 0o755)
    
    def test_get_default_config_path(self):
        """Test getting default configuration file path."""
        with patch('os.path.expanduser') as mock_expanduser:
            with patch('os.makedirs') as mock_makedirs:
                mock_expanduser.return_value = '/home/testuser/.liturgical_calendar'
                path = self.config_service._get_default_config_path()
                expected_path = '/home/testuser/.liturgical_calendar/config.json'
                self.assertEqual(path, expected_path)
                mock_makedirs.assert_called_once_with('/home/testuser/.liturgical_calendar', exist_ok=True)
    
    def test_get_default_config(self):
        """Test getting default configuration values."""
        config = self.config_service._get_default_config()
        
        # Check that all expected sections are present
        self.assertIn('image', config)
        self.assertIn('artwork', config)
        self.assertIn('readings', config)
        self.assertIn('output', config)
        self.assertIn('logging', config)
        
        # Check some specific values
        self.assertEqual(config['image']['width'], 1080)
        self.assertEqual(config['artwork']['cache_dir'], './cache')
        self.assertEqual(config['readings']['translation'], 'NRSV')


if __name__ == '__main__':
    unittest.main() 