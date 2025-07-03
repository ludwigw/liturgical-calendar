import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import os
import shutil
from liturgical_calendar.caching.artwork_cache import ArtworkCache
import time

class TestArtworkCache(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path('test_cache')
        self.cache = ArtworkCache(cache_dir=self.test_dir)
        # Ensure clean test dirs
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
        self.test_dir.mkdir()
        (self.test_dir / 'original').mkdir()

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_init_creates_dirs(self):
        self.assertTrue(self.cache.cache_dir.exists())
        self.assertTrue(self.cache.original_dir.exists())

    def test_get_cached_path_and_is_cached(self):
        url = 'https://example.com/image.jpg'
        path = self.cache.get_cached_path(url)
        self.assertIsInstance(path, Path)
        self.assertFalse(self.cache.is_cached(url))
        # Simulate file
        path.touch()
        self.assertTrue(self.cache.is_cached(url))

    @patch('liturgical_calendar.caching.artwork_cache.requests.Session')
    @patch('liturgical_calendar.caching.artwork_cache.Image')
    def test_download_and_cache_valid_image(self, mock_image, mock_session):
        url = 'https://example.com/image.jpg'
        cache_path = self.cache.get_cached_path(url)
        # Mock requests
        mock_resp = MagicMock()
        mock_resp.iter_content = lambda chunk_size: [b'data']
        mock_resp.raise_for_status = lambda: None
        mock_session.return_value.get.return_value = mock_resp
        # Mock PIL
        mock_img = MagicMock()
        mock_img.size = (1200, 1200)
        mock_image.open.return_value.__enter__.return_value = mock_img
        mock_img.verify = lambda: None
        # Should succeed
        result = self.cache.download_and_cache(url)
        self.assertTrue(result)
        self.assertTrue(cache_path.exists())

    @patch('liturgical_calendar.caching.artwork_cache.requests.Session')
    @patch('liturgical_calendar.caching.artwork_cache.Image')
    def test_download_and_cache_invalid_image(self, mock_image, mock_session):
        url = 'https://example.com/bad.jpg'
        cache_path = self.cache.get_cached_path(url)
        # Mock requests
        mock_resp = MagicMock()
        mock_resp.iter_content = lambda chunk_size: [b'data']
        mock_resp.raise_for_status = lambda: None
        mock_session.return_value.get.return_value = mock_resp
        # Mock PIL to raise error
        mock_image.open.side_effect = Exception('Not an image')
        # Should fail and file should not exist
        result = self.cache.download_and_cache(url)
        self.assertFalse(result)
        self.assertFalse(cache_path.exists())

    @patch('liturgical_calendar.caching.artwork_cache.requests.Session')
    @patch('liturgical_calendar.caching.artwork_cache.Image')
    def test_download_and_cache_upsample_and_archive(self, mock_image, mock_session):
        url = 'https://example.com/small.jpg'
        cache_path = self.cache.get_cached_path(url)
        orig_dir = self.cache.original_dir
        # Mock requests
        mock_resp = MagicMock()
        mock_resp.iter_content = lambda chunk_size: [b'data']
        mock_resp.raise_for_status = lambda: None
        mock_session.return_value.get.return_value = mock_resp
        # Mock PIL
        mock_img = MagicMock()
        mock_img.size = (500, 500)
        mock_img.verify = lambda: None
        mock_img.convert.return_value.resize.return_value = mock_img
        # Patch save to actually write a file to cache_path
        def fake_save(path, *a, **kw):
            Path(path).write_bytes(b'upsampled')
        mock_img.save = fake_save
        mock_image.open.return_value.__enter__.return_value = mock_img
        # Should upsample and archive
        result = self.cache.download_and_cache(url)
        self.assertTrue(result)
        self.assertTrue(cache_path.exists())
        self.assertTrue((orig_dir / cache_path.name).exists())

    def test_get_cache_info(self):
        url = 'https://example.com/info.jpg'
        cache_path = self.cache.get_cached_path(url)
        cache_path.write_bytes(b'12345')
        info = self.cache.get_cache_info(url)
        self.assertEqual(info['path'], str(cache_path))
        self.assertEqual(info['size'], 5)
        self.assertIn('modified', info)

    def test_cleanup_old_cache(self):
        url = 'https://example.com/old.jpg'
        cache_path = self.cache.get_cached_path(url)
        cache_path.write_bytes(b'abc')
        # Set mtime to 40 days ago
        old_time = time.time() - 40 * 86400
        os.utime(cache_path, (old_time, old_time))
        removed = self.cache.cleanup_old_cache(max_age_days=30)
        self.assertIn(str(cache_path), removed)
        self.assertFalse(cache_path.exists())

if __name__ == '__main__':
    unittest.main() 