import unittest
from unittest.mock import patch

from liturgical_calendar.core.artwork_manager import ArtworkManager


class TestArtworkManager(unittest.TestCase):
    def setUp(self):
        self.artwork_manager = ArtworkManager()

    def test_auto_cache_enabled_by_default(self):
        """Test that auto-caching is enabled by default."""
        # Mock the cache to avoid actual downloads
        with patch.object(
            self.artwork_manager.cache, "download_and_cache"
        ) as mock_cache:
            mock_cache.return_value = True

            # Mock the cache path to simulate missing artwork
            with patch("pathlib.Path.exists", return_value=False):
                result = self.artwork_manager.get_artwork_for_date("2024-12-25")

                # Should attempt to cache the artwork
                mock_cache.assert_called_once()
                self.assertTrue(result.get("cached"))

    def test_auto_cache_disabled(self):
        """Test that auto-caching can be disabled."""
        # Mock the cache to avoid actual downloads
        with patch.object(
            self.artwork_manager.cache, "download_and_cache"
        ) as mock_cache:
            # Mock the cache path to simulate missing artwork
            with patch("pathlib.Path.exists", return_value=False):
                result = self.artwork_manager.get_artwork_for_date(
                    "2024-12-25", auto_cache=False
                )

                # Should not attempt to cache the artwork
                mock_cache.assert_not_called()
                self.assertFalse(result.get("cached"))

    def test_auto_cache_failure_handling(self):
        """Test that auto-caching failures are handled gracefully."""
        # Mock the cache to simulate download failure
        with patch.object(
            self.artwork_manager.cache, "download_and_cache"
        ) as mock_cache:
            mock_cache.return_value = False

            # Mock the cache path to simulate missing artwork
            with patch("pathlib.Path.exists", return_value=False):
                result = self.artwork_manager.get_artwork_for_date("2024-12-25")

                # Should attempt to cache but handle failure gracefully
                mock_cache.assert_called_once()
                self.assertFalse(result.get("cached"))

    def test_auto_cache_exception_handling(self):
        """Test that auto-caching exceptions are handled gracefully."""
        # Mock the cache to simulate an exception
        with patch.object(
            self.artwork_manager.cache, "download_and_cache"
        ) as mock_cache:
            mock_cache.side_effect = Exception("Network error")

            # Mock the cache path to simulate missing artwork
            with patch("pathlib.Path.exists", return_value=False):
                result = self.artwork_manager.get_artwork_for_date("2024-12-25")

                # Should attempt to cache but handle exception gracefully
                mock_cache.assert_called_once()
                self.assertFalse(result.get("cached"))

    def test_artwork_already_cached(self):
        """Test that auto-caching is skipped when artwork is already cached."""
        # Mock the cache to avoid actual downloads
        with patch.object(
            self.artwork_manager.cache, "download_and_cache"
        ) as mock_cache:
            # Mock the cache path to simulate existing artwork
            with patch("pathlib.Path.exists", return_value=True):
                result = self.artwork_manager.get_artwork_for_date("2024-12-25")

                # Should not attempt to cache since artwork already exists
                mock_cache.assert_not_called()
                self.assertTrue(result.get("cached"))


if __name__ == "__main__":
    unittest.main()
