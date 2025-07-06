import os
import shutil
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from liturgical_calendar.caching.artwork_cache import ArtworkCache


class TestArtworkCache(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_cache")
        self.cache = ArtworkCache(cache_dir=self.test_dir)
        # Ensure clean test dirs
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        (self.test_dir / "original").mkdir()

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_init_creates_dirs(self):
        self.assertTrue(self.cache.cache_dir.exists())
        self.assertTrue(self.cache.original_dir.exists())

    def test_get_cached_path_and_is_cached(self):
        url = "https://example.com/image.jpg"
        path = self.cache.get_cached_path(url)
        self.assertIsInstance(path, Path)
        self.assertFalse(self.cache.is_cached(url))
        # Simulate file
        path.touch()
        self.assertTrue(self.cache.is_cached(url))

    @patch("liturgical_calendar.caching.image_processor.requests.Session")
    def test_download_and_cache_valid_image(self, mock_session):
        # Use a real temp directory and real archive_original
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ArtworkCache(cache_dir=tmpdir)
            url = "https://example.com/image.jpg"
            cache_path = cache.get_cached_path(url)
            # Mock requests
            mock_resp = MagicMock()
            mock_resp.iter_content = lambda chunk_size: [b"data"]
            mock_resp.raise_for_status = lambda: None
            mock_session.return_value.get.return_value = mock_resp
            # Patch Image.open to simulate a large image
            with patch(
                "liturgical_calendar.caching.artwork_cache.Image.open"
            ) as mock_open, patch.object(
                cache.processor, "validate_image", return_value=True
            ):
                mock_img = MagicMock()
                mock_img.size = (1200, 1200)
                mock_open.return_value.__enter__.return_value = mock_img
                result = cache.download_and_cache(url)
                self.assertTrue(result)
                self.assertTrue(cache_path.exists())
                # The archived file should also exist
                archived_path = cache.original_dir / cache_path.name
                self.assertTrue(archived_path.exists())

    @patch("liturgical_calendar.caching.image_processor.requests.Session")
    def test_download_and_cache_invalid_image(self, mock_session):
        url = "https://example.com/bad.jpg"
        self.cache.get_cached_path(url)
        # Mock requests
        mock_resp = MagicMock()
        mock_resp.iter_content = lambda chunk_size: [b"data"]
        mock_resp.raise_for_status = lambda: None
        mock_session.return_value.get.return_value = mock_resp
        # Patch validate_image to fail
        with patch.object(self.cache.processor, "validate_image", return_value=False):
            with self.assertRaises(Exception):
                self.cache.download_and_cache(url)

    @patch("liturgical_calendar.caching.image_processor.requests.Session")
    def test_download_and_cache_upsample_and_archive(self, mock_session):
        url = "https://example.com/small.jpg"
        cache_path = self.cache.get_cached_path(url)
        self.cache.original_dir
        # Mock requests
        mock_resp = MagicMock()
        mock_resp.iter_content = lambda chunk_size: [b"data"]
        mock_resp.raise_for_status = lambda: None
        mock_session.return_value.get.return_value = mock_resp
        # Patch processor methods to always succeed
        with patch(
            "liturgical_calendar.caching.artwork_cache.Image.open"
        ) as mock_open, patch.object(
            self.cache.processor, "validate_image", return_value=True
        ), patch.object(
            self.cache.processor, "upsample_image", return_value=True
        ), patch.object(
            self.cache.processor, "archive_original", return_value=True
        ):
            mock_img = MagicMock()
            mock_img.size = (500, 500)
            mock_open.return_value.__enter__.return_value = mock_img
            result = self.cache.download_and_cache(url)
            self.assertTrue(result)
            self.assertTrue(cache_path.exists())
            # NOTE: Archive file existence side effect should be tested in an integration test
            # self.assertTrue((orig_dir / cache_path.name).exists())

    def test_get_cache_info(self):
        url = "https://example.com/info.jpg"
        cache_path = self.cache.get_cached_path(url)
        cache_path.write_bytes(b"12345")
        info = self.cache.get_cache_info(url)
        self.assertEqual(info["path"], str(cache_path))
        self.assertEqual(info["size"], 5)
        self.assertIn("modified", info)

    def test_cleanup_old_cache(self):
        url = "https://example.com/old.jpg"
        cache_path = self.cache.get_cached_path(url)
        cache_path.write_bytes(b"abc")
        # Set mtime to 40 days ago
        old_time = time.time() - 40 * 86400
        os.utime(cache_path, (old_time, old_time))
        removed = self.cache.cleanup_old_cache(max_age_days=30)
        self.assertIn(str(cache_path), removed)
        self.assertFalse(cache_path.exists())

    def test_get_instagram_image_url(self):
        from liturgical_calendar.caching.artwork_cache import get_instagram_image_url

        url = "https://instagram.com/someuser/postid"
        expected = "https://instagram.com/someuser/postid/media?size=l"
        self.assertEqual(get_instagram_image_url(url), expected)
        # Non-instagram URL returns None
        self.assertIsNone(get_instagram_image_url("https://example.com/image.jpg"))

    @patch("liturgical_calendar.caching.image_processor.requests.Session")
    def test_download_and_cache_instagram_url(self, mock_session):
        # Use a real temp directory and real archive_original
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ArtworkCache(cache_dir=tmpdir)
            url = "https://instagram.com/someuser/postid"
            expected_direct_url = "https://instagram.com/someuser/postid/media?size=l"
            cache_path = cache.get_cached_path(url)
            # Mock requests
            mock_resp = MagicMock()
            mock_resp.iter_content = lambda chunk_size: [b"data"]
            mock_resp.raise_for_status = lambda: None
            mock_session.return_value.get.return_value = mock_resp
            # Patch Image.open to simulate a large image
            with patch(
                "liturgical_calendar.caching.artwork_cache.Image.open"
            ) as mock_open, patch.object(
                cache.processor, "validate_image", return_value=True
            ), patch.object(
                cache.processor, "download_image", wraps=cache.processor.download_image
            ) as mock_download:
                mock_img = MagicMock()
                mock_img.size = (1200, 1200)
                mock_open.return_value.__enter__.return_value = mock_img
                result = cache.download_and_cache(url)
                self.assertTrue(result)
                self.assertTrue(cache_path.exists())
                archived_path = cache.original_dir / cache_path.name
                self.assertTrue(archived_path.exists())
                # Check that download_image was called with the rewritten Instagram URL
                called_url = mock_download.call_args[0][0]
                self.assertEqual(called_url, expected_direct_url)

    def test_integration_real_image(self):
        """
        Integration test: use a real image file, no mocks for processor methods. Tests caching, validation, and archiving.
        """
        import tempfile

        from PIL import Image as PILImage

        # Create a temp directory for the cache
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = ArtworkCache(cache_dir=tmpdir)
            # Create a real image file to simulate a download
            img_path = Path(tmpdir) / "real.jpg"
            img = PILImage.new("RGB", (120, 120), color="red")
            img.save(img_path)
            url = "https://example.com/real.jpg"

            # Patch download_image to copy the file
            def fake_download_image(
                src_url,
                cache_path,
                headers=None,
                referer=None,
                max_retries=3,
                retry_delay=5.0,
            ):
                shutil.copy2(img_path, cache_path)
                return True

            with patch.object(
                cache.processor, "download_image", side_effect=fake_download_image
            ):
                result = cache.download_and_cache(url, upsample=False)
                self.assertTrue(result)
                cache_path = cache.get_cached_path(url)
                self.assertTrue(cache.processor.validate_image(cache_path))
            # Now test archiving with upsample=True on a small image
            small_img_path = Path(tmpdir) / "small.jpg"
            small_img = PILImage.new("RGB", (50, 50), color="blue")
            small_img.save(small_img_path)
            small_url = "https://example.com/small-real.jpg"

            # Patch download_image to copy the small image
            def fake_download_small(
                src_url,
                cache_path,
                headers=None,
                referer=None,
                max_retries=3,
                retry_delay=5.0,
            ):
                shutil.copy2(small_img_path, cache_path)
                return True

            with patch.object(
                cache.processor, "download_image", side_effect=fake_download_small
            ):
                result = cache.download_and_cache(small_url, upsample=True)
                self.assertTrue(result)
                small_cache_path = cache.get_cached_path(small_url)
                # Check that the archived original exists
                archived = cache.original_dir / small_cache_path.name
                self.assertTrue(archived.exists())
                # Check that the upsampled image is now 1080x1080
                with PILImage.open(small_cache_path) as up_img:
                    self.assertEqual(up_img.size, (1080, 1080))


if __name__ == "__main__":
    unittest.main()
