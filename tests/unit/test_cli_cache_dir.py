"""Test cache directory configuration in CLI commands."""

import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from liturgical_calendar.cli import main


class TestCLICacheDirectory(unittest.TestCase):
    """Test cache directory configuration in CLI commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("liturgical_calendar.cli.ArtworkCache")
    def test_cache_artwork_command_with_cache_dir(self, mock_artwork_cache):
        """Test that cache-artwork command accepts --cache-dir option."""
        # Mock the artwork cache
        mock_cache = MagicMock()
        mock_artwork_cache.return_value = mock_cache
        mock_cache.cache_multiple_artwork.return_value = {
            "success": 100,
            "failed": 10,
            "total": 110,
            "failed_urls": [],
        }

        # Test with cache directory and capture logs
        with patch(
            "sys.argv", ["litcal", "cache-artwork", "--cache-dir", self.temp_dir]
        ):
            with self.assertLogs("liturgical_calendar.cli", level="INFO") as cm:
                main()
        # Verify that the cache was created with the custom directory
        mock_artwork_cache.assert_called_once_with(cache_dir=self.temp_dir)
        # Verify logging
        found = any(
            "Using custom cache directory for cache-artwork" in msg for msg in cm.output
        )
        self.assertTrue(
            found, "Custom cache directory logging not found for cache-artwork"
        )

    @patch("liturgical_calendar.cli.ImageService")
    def test_generate_command_with_cache_dir(self, mock_image_service):
        """Test that generate command accepts --cache-dir option."""
        # Mock the image service
        mock_service = MagicMock()
        mock_image_service.return_value = mock_service
        mock_service.generate_liturgical_image.return_value = {
            "success": True,
            "file_path": "/tmp/test_output.png",
        }
        # Test with cache directory and capture logs
        with patch(
            "sys.argv",
            ["litcal", "generate", "2024-12-25", "--cache-dir", self.temp_dir],
        ):
            with self.assertLogs("liturgical_calendar.cli", level="INFO") as cm:
                main()
        # Verify that the cache directory was set in the config
        mock_image_service.assert_called_once()
        call_args = mock_image_service.call_args
        config = call_args[1]["config"]
        self.assertEqual(config.CACHE_DIR, self.temp_dir)
        # Verify logging
        found = any("Using custom cache directory" in msg for msg in cm.output)
        self.assertTrue(
            found, "Custom cache directory logging not found for generate command"
        )

    @patch("liturgical_calendar.cli.ImageService")
    @patch("liturgical_calendar.logging.get_logger")
    def test_generate_command_without_cache_dir(
        self, mock_get_logger, mock_image_service
    ):
        """Test that generate command works without --cache-dir option."""
        # Mock the logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Mock the image service
        mock_service = MagicMock()
        mock_image_service.return_value = mock_service
        mock_service.generate_liturgical_image.return_value = {
            "success": True,
            "file_path": "/tmp/test_output.png",
        }

        # Reset the config to default before testing
        from liturgical_calendar.cli import SimpleConfig

        SimpleConfig.CACHE_DIR = "cache"

        # Test without cache directory
        with patch("sys.argv", ["litcal", "generate", "2024-12-25"]):
            main()

        # Verify that the cache directory was not set (uses default)
        mock_image_service.assert_called_once()
        call_args = mock_image_service.call_args
        config = call_args[1]["config"]
        self.assertEqual(config.CACHE_DIR, "cache")  # Default value

        # Verify no custom cache directory logging
        cache_dir_logged = False
        for call in mock_logger.info.call_args_list:
            if "Using custom cache directory" in str(call):
                cache_dir_logged = True
                break
        self.assertFalse(
            cache_dir_logged, "Custom cache directory logging found when not expected"
        )

    @patch("liturgical_calendar.cli.ArtworkCache")
    @patch("liturgical_calendar.logging.get_logger")
    def test_cache_artwork_command_without_cache_dir(
        self, mock_get_logger, mock_artwork_cache
    ):
        """Test that cache-artwork command works without --cache-dir option."""
        # Mock the logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Mock the artwork cache
        mock_cache = MagicMock()
        mock_artwork_cache.return_value = mock_cache
        mock_cache.cache_multiple_artwork.return_value = {
            "success": 100,
            "failed": 10,
            "total": 110,
            "failed_urls": [],
        }

        # Test without cache directory
        with patch("sys.argv", ["litcal", "cache-artwork"]):
            main()

        # Verify that the cache was created with None (default directory)
        mock_artwork_cache.assert_called_once_with(cache_dir=None)

        # Verify no custom cache directory logging
        cache_dir_logged = False
        for call in mock_logger.info.call_args_list:
            if "Using custom cache directory for cache-artwork" in str(call):
                cache_dir_logged = True
                break
        self.assertFalse(
            cache_dir_logged, "Custom cache directory logging found when not expected"
        )


if __name__ == "__main__":
    unittest.main()
