import unittest
import tempfile
import os
from pathlib import Path
from unittest import mock
from liturgical_calendar.utils import file_system

class TestFileSystemUtils(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.test_file = self.test_dir / "testfile.txt"

    def tearDown(self):
        self.temp_dir.cleanup()

    @mock.patch("shutil.disk_usage")
    def test_check_disk_space_sufficient(self, mock_disk_usage):
        # Simulate plenty of free space
        mock_disk_usage.return_value = mock.Mock(total=100000000, used=1000000, free=90000000)
        self.assertTrue(file_system.check_disk_space(self.test_dir, required_bytes=1024, min_free_mb=1))

    @mock.patch("shutil.disk_usage")
    def test_check_disk_space_insufficient(self, mock_disk_usage):
        # Simulate not enough free space
        mock_disk_usage.return_value = mock.Mock(total=100000000, used=99000000, free=100000)
        with self.assertRaises(OSError):
            file_system.check_disk_space(self.test_dir, required_bytes=1024*1024*10, min_free_mb=10)

    def test_ensure_directory_creates_and_checks_writable(self):
        # Directory should be created and writable
        new_dir = self.test_dir / "subdir"
        result = file_system.ensure_directory(new_dir)
        self.assertTrue(result.exists())
        self.assertTrue(os.access(result, os.W_OK))

    def test_ensure_directory_not_writable(self):
        # Make directory read-only and check for OSError
        new_dir = self.test_dir / "readonly"
        new_dir.mkdir()
        new_dir.chmod(0o400)  # Read-only
        try:
            with self.assertRaises(OSError):
                file_system.ensure_directory(new_dir)
        finally:
            new_dir.chmod(0o700)  # Restore permissions for cleanup

    def test_safe_write_file_success(self):
        def write_func(path):
            with open(path, "w") as f:
                f.write("hello world")
        result = file_system.safe_write_file(self.test_file, write_func, estimated_size=100)
        self.assertTrue(result)
        self.assertTrue(self.test_file.exists())
        with open(self.test_file) as f:
            self.assertEqual(f.read(), "hello world")

    def test_safe_write_file_permission_error(self):
        # Simulate PermissionError during write
        def write_func(path):
            raise PermissionError("No write access")
        with self.assertRaises(OSError):
            file_system.safe_write_file(self.test_file, write_func, estimated_size=100)
        self.assertFalse(self.test_file.exists())

    def test_safe_write_file_general_error(self):
        # Simulate generic error during write
        def write_func(path):
            raise RuntimeError("Something went wrong")
        with self.assertRaises(RuntimeError):
            file_system.safe_write_file(self.test_file, write_func, estimated_size=100)
        self.assertFalse(self.test_file.exists())

    def test_cleanup_partial_file(self):
        # Create a partial file and ensure cleanup removes it
        partial_file = self.test_dir / "partial.tmp.txt"
        with open(partial_file, "w") as f:
            f.write("partial")
        self.assertTrue(partial_file.exists())
        file_system._cleanup_partial_file(partial_file)
        self.assertFalse(partial_file.exists())

    def test_safe_save_image(self):
        from PIL import Image
        img = Image.new("RGB", (10, 10), color="red")
        out_path = self.test_dir / "testimg.jpg"
        result = file_system.safe_save_image(img, out_path, quality=80)
        self.assertTrue(result)
        self.assertTrue(out_path.exists())

if __name__ == "__main__":
    unittest.main() 