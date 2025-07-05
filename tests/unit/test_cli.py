import unittest
from unittest import mock
from datetime import date
from liturgical_calendar.cli import get_date_str, SimpleConfig, main

class TestCLIUnit(unittest.TestCase):
    def test_get_date_str(self):
        test_date = date(2024, 12, 25)
        result = get_date_str(test_date)
        self.assertEqual(result, "2024-12-25")

    def test_simple_config_attributes(self):
        config = SimpleConfig()
        expected_attrs = [
            'IMAGE_WIDTH', 'IMAGE_HEIGHT', 'BG_COLOR', 'TEXT_COLOR',
            'LINE_COLOR', 'FONTS_DIR', 'PADDING', 'ARTWORK_SIZE',
            'ROW_SPACING', 'HEADER_FONT_SIZE', 'TITLE_FONT_SIZE',
            'TITLE_LINE_HEIGHT', 'COLUMN_FONT_SIZE'
        ]
        for attr in expected_attrs:
            self.assertTrue(hasattr(config, attr), f"Missing attribute: {attr}")

    # Example: test argument parsing and error handling in-process
    @mock.patch('sys.argv', ['litcal', 'generate', 'invalid-date'])
    @mock.patch('builtins.print')
    def test_generate_invalid_date_inprocess(self, mock_print):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)
        mock_print.assert_any_call('Invalid date format. Use YYYY-MM-DD.')

if __name__ == '__main__':
    unittest.main() 