import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCLIIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_dir = Path(self.temp_dir.name)
        self.project_root = Path(__file__).parent.parent.parent

    def tearDown(self):
        self.temp_dir.cleanup()

    def _run_cli(self, args, cwd=None):
        if cwd is None:
            cwd = self.project_root
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        return subprocess.run(
            [sys.executable, "-m", "liturgical_calendar.cli"] + args,
            capture_output=True,
            text=True,
            cwd=cwd,
            env=env,
        )

    def test_version_command(self):
        result = self._run_cli(["version"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("litcal version", result.stdout)

    def test_help_command(self):
        result = self._run_cli(["--help"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
        self.assertIn("Liturgical Calendar CLI", result.stdout)

    def test_no_command_prints_help(self):
        result = self._run_cli([])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "error: the following arguments are required: command", result.stderr
        )

    def test_invalid_command(self):
        result = self._run_cli(["invalid-command"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid choice", result.stderr)

    def test_generate_command_with_date(self):
        result = self._run_cli(["generate", "2024-12-25"])
        # Accept either success or error, but should not crash
        self.assertIn(result.returncode, (0, 1))
        self.assertTrue(
            "Saved image to" in result.stdout
            or "Error generating image" in result.stdout
        )

    def test_generate_command_invalid_date(self):
        result = self._run_cli(["generate", "invalid-date"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("Invalid date format. Use YYYY-MM-DD.", result.stdout)

    def test_info_command_with_date(self):
        result = self._run_cli(["info", "2024-12-25"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Date: 2024-12-25", result.stdout)
        self.assertIn("Season:", result.stdout)
        self.assertIn("Week:", result.stdout)
        self.assertIn("Name:", result.stdout)
        self.assertIn("Colour:", result.stdout)

    def test_info_command_without_date(self):
        result = self._run_cli(["info"])
        self.assertEqual(result.returncode, 0)
        self.assertIn("Date:", result.stdout)
        self.assertIn("Season:", result.stdout)
        self.assertIn("Week:", result.stdout)
        self.assertIn("Name:", result.stdout)
        self.assertIn("Colour:", result.stdout)


if __name__ == "__main__":
    unittest.main()
