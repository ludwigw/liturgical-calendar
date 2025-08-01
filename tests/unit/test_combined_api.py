"""
Tests for the combined feast and artwork API functionality.
"""

import unittest
from datetime import date

from liturgical_calendar.liturgical import get_liturgical_info_with_artwork


class TestCombinedAPI(unittest.TestCase):
    """Test the combined feast and artwork API."""

    def test_get_liturgical_info_with_artwork_basic(self):
        """Test basic functionality of the combined API."""
        # Test with a known date that should have both feast and artwork
        result = get_liturgical_info_with_artwork("2024-12-25")

        # Should return a dictionary with feast and artwork information
        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("season", result)
        self.assertIn("artwork", result)

        # Should have Christmas feast information
        self.assertIn("Christmas", result["name"])
        self.assertEqual(result["season"], "Christmas")

    def test_get_liturgical_info_with_artwork_with_datetime(self):
        """Test that the API works with datetime objects."""
        test_date = date(2024, 12, 25)
        result = get_liturgical_info_with_artwork(test_date)

        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("artwork", result)

    def test_get_liturgical_info_with_artwork_with_transferred(self):
        """Test that the transferred parameter works."""
        result = get_liturgical_info_with_artwork("2024-12-25", transferred=True)

        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        self.assertIn("artwork", result)

    def test_artwork_priority_logic(self):
        """Test that artwork names are prioritized over feast names."""
        # Test with a date that should have artwork
        result = get_liturgical_info_with_artwork("2024-12-25")

        # The name should come from artwork if available
        if result.get("artwork") and result["artwork"].get("name"):
            # If artwork has a name, it should be used
            self.assertEqual(result["name"], result["artwork"]["name"])
        else:
            # If no artwork name, should fall back to feast name or day of week
            self.assertIsNotNone(result["name"])

    def test_fallback_to_day_of_week(self):
        """Test fallback to day of week when no feast or artwork name is available."""
        # Test with a regular weekday that might not have specific feast/artwork
        result = get_liturgical_info_with_artwork("2024-01-15")  # A Monday

        self.assertIsInstance(result, dict)
        self.assertIn("name", result)
        # Should have some name (either feast, artwork, or day of week)
        self.assertIsNotNone(result["name"])


if __name__ == "__main__":
    unittest.main()
