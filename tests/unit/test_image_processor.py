import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import os
import shutil
from liturgical_calendar.caching.image_processor import ImageProcessor
from PIL import Image

class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = ImageProcessor()
        self.test_dir = Path("test_image_processor_tmp")
        self.test_dir.mkdir(exist_ok=True)
        self.image_path = self.test_dir / "test.jpg"
        # Create a valid image file
        img = Image.new('RGB', (100, 100), color='red')
        img.save(self.image_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('requests.Session.get')
    def test_download_image_success(self, mock_get):
        # Mock a successful image download
        mock_response = MagicMock()
        mock_response.iter_content = lambda chunk_size: [b'123', b'456']
        mock_response.raise_for_status = lambda: None
        mock_get.return_value = mock_response
        out_path = self.test_dir / "downloaded.jpg"
        result = self.processor.download_image("http://example.com/image.jpg", out_path)
        self.assertTrue(result)
        self.assertTrue(out_path.exists())

    @patch('requests.Session.get')
    def test_download_image_failure(self, mock_get):
        # Simulate a failed download
        mock_get.side_effect = Exception("Network error")
        out_path = self.test_dir / "fail.jpg"
        result = self.processor.download_image("http://bad.url/image.jpg", out_path)
        self.assertFalse(result)
        self.assertFalse(out_path.exists())

    def test_validate_image_success(self):
        self.assertTrue(self.processor.validate_image(self.image_path))

    def test_validate_image_failure(self):
        # Write invalid data to file
        bad_path = self.test_dir / "bad.jpg"
        with open(bad_path, 'wb') as f:
            f.write(b'not an image')
        self.assertFalse(self.processor.validate_image(bad_path))
        self.assertFalse(bad_path.exists())  # Should be deleted

    def test_upsample_image_needed(self):
        small_path = self.test_dir / "small.jpg"
        img = Image.new('RGB', (50, 50), color='blue')
        img.save(small_path)
        out_path = self.test_dir / "upsampled.jpg"
        result = self.processor.upsample_image(small_path, out_path, (100, 100))
        self.assertTrue(result)
        with Image.open(out_path) as up_img:
            self.assertEqual(up_img.size, (100, 100))

    def test_upsample_image_not_needed(self):
        out_path = self.test_dir / "copy.jpg"
        result = self.processor.upsample_image(self.image_path, out_path, (50, 50))
        self.assertFalse(result)
        with Image.open(out_path) as img:
            self.assertEqual(img.size, (100, 100))

    def test_archive_original_success(self):
        archive_dir = self.test_dir / "archive"
        archive_dir.mkdir(exist_ok=True)
        orig_path = self.test_dir / "to_archive.jpg"
        img = Image.new('RGB', (10, 10), color='green')
        img.save(orig_path)
        result = self.processor.archive_original(orig_path, archive_dir)
        self.assertTrue(result)
        archived_path = archive_dir / orig_path.name
        self.assertTrue(archived_path.exists())
        self.assertFalse(orig_path.exists())

    def test_archive_original_failure(self):
        archive_dir = self.test_dir / "archive"
        # Try to archive a non-existent file
        orig_path = self.test_dir / "does_not_exist.jpg"
        result = self.processor.archive_original(orig_path, archive_dir)
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main() 