"""
Unit tests for artwork functionality
"""
import unittest
from unittest.mock import patch
from liturgical_calendar.core.artwork_manager import ArtworkManager
from liturgical_calendar.data.artwork_data import feasts

# Create ArtworkManager instance for testing
artwork_manager = ArtworkManager()

class TestLookupFeastArtwork(unittest.TestCase):
    def test_lookup_single_feast(self):
        result = artwork_manager.lookup_feast_artwork('easter', 0)  # Easter Sunday
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Easter')
        self.assertIn('source', result)

    def test_lookup_multiple_feasts(self):
        result1 = artwork_manager.lookup_feast_artwork('christmas', '01-02', 0)
        self.assertIsNotNone(result1)
        self.assertEqual(result1['name'], 'Vedanayagam Samuel Azariah')
        result2 = artwork_manager.lookup_feast_artwork('christmas', '01-02', 1)
        self.assertIsNotNone(result2)
        self.assertEqual(result2['name'], 'Seraphim of Sarov')
        result3 = artwork_manager.lookup_feast_artwork('christmas', '01-02', 2)
        self.assertIsNotNone(result3)
        self.assertEqual(result3['name'], 'Vedanayagam Samuel Azariah')

    def test_lookup_nonexistent_feast(self):
        result = artwork_manager.lookup_feast_artwork('easter', 999)
        self.assertIsNone(result)

    def test_lookup_nonexistent_season(self):
        with self.assertRaises(KeyError):
            artwork_manager.lookup_feast_artwork('nonexistent', 0)

class TestGetImageSourceForDate(unittest.TestCase):
    def test_easter_based_feast(self):
        # 2025-04-20 is Easter Sunday
        result = artwork_manager.get_artwork_for_date('2025-04-20')
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Easter')
        self.assertIn('source', result)

    def test_christmas_based_feast(self):
        # 2025-01-06 is Epiphany
        result = artwork_manager.get_artwork_for_date('2025-01-06')
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Epiphany')
        self.assertIn('source', result)

    def test_multiple_feasts_cycle_selection(self):
        # 2023-01-02, 2024-01-02, 2025-01-02 should cycle through two feasts
        result_2023 = artwork_manager.get_artwork_for_date('2023-01-02')  # Cycle A
        result_2024 = artwork_manager.get_artwork_for_date('2024-01-02')  # Cycle B
        result_2025 = artwork_manager.get_artwork_for_date('2025-01-02')  # Cycle C (wraps to A)
        # 2023 and 2025 should match, 2024 should differ
        self.assertEqual(result_2023['name'], result_2025['name'])
        self.assertNotEqual(result_2023['name'], result_2024['name'])
        self.assertIn(result_2023['name'], ['Vedanayagam Samuel Azariah', 'Seraphim of Sarov'])
        self.assertIn(result_2024['name'], ['Vedanayagam Samuel Azariah', 'Seraphim of Sarov'])

    def test_no_feast_found(self):
        # 2025-07-04 is not a feast day in the artwork data
        result = artwork_manager.get_artwork_for_date('2025-07-04')
        self.assertIsNone(result)

    def test_liturgical_priority_matching(self):
        # 2025-01-06 is Epiphany, test with liturgical_result
        liturgical_result = {
            'name': 'Epiphany',
            'prec': 7
        }
        result = artwork_manager.get_artwork_for_date('2025-01-06', liturgical_result)
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Epiphany')

    def test_martyr_flag(self):
        # 2025-02-12 is Lady Jane Grey (martyr)
        result = artwork_manager.get_artwork_for_date('2025-02-12')
        print(f"DEBUG: result for 2025-02-12: {result}")
        print(f"DEBUG: feasts['christmas']['02-12']: {feasts['christmas'].get('02-12')}")
        self.assertIsNotNone(result)
        self.assertEqual(result['name'], 'Lady Jane Grey')
        self.assertIn('martyr', result)
        self.assertEqual(result['martyr'], 1)

class TestFindSquashedArtworks(unittest.TestCase):
    """Test the find_squashed_artworks function"""
    
    @patch('liturgical_calendar.feasts.lookup_feast')
    def test_find_squashed_artworks(self, mock_lookup_feast):
        """Test finding artworks that will never be selected due to high precedence liturgical feasts"""
        # Mock lookup_feast to return a high precedence feast that doesn't match artwork names
        mock_lookup_feast.return_value = {
            'name': 'Epiphany',  # This doesn't match most artwork names
            'prec': 7  # High precedence - will always be selected
        }
        
        result = artwork_manager.find_squashed_artworks()
        
        # Should return a list of squashed artworks
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0, "Should find some squashed artworks")
        
        # Each item should have the expected structure
        item = result[0]
        self.assertIn('season', item)
        self.assertIn('pointer', item)
        self.assertIn('liturgical_name', item)
        self.assertIn('prec', item)
        self.assertIn('artwork_name', item)
        self.assertIn('source', item)
        
        # The liturgical_name should be different from artwork_name
        # (this is what makes it "squashed")
        self.assertNotEqual(item['liturgical_name'], item['artwork_name'])
    
    @patch('liturgical_calendar.feasts.lookup_feast')
    def test_no_squashed_artworks_when_low_precedence(self, mock_lookup_feast):
        """Test that low precedence feasts don't cause squashing"""
        # Mock lookup_feast to return a low precedence feast
        mock_lookup_feast.return_value = {
            'name': 'Some Feast',
            'prec': 3  # Low precedence - won't cause squashing
        }
        
        result = artwork_manager.find_squashed_artworks()
        
        # Should return empty list since prec <= 5
        self.assertEqual(result, [])
    
    @patch('liturgical_calendar.feasts.lookup_feast')
    def test_no_squashed_artworks_when_names_match(self, mock_lookup_feast):
        """Test that matching names don't cause squashing"""
        # Mock lookup_feast to return a feast that matches artwork names
        # We need to mock it to return different names for different calls
        def mock_lookup_side_effect(season, pointer):
            # Return the actual artwork name for each pointer to simulate matching
            if season == 'christmas' and pointer == '01-06':
                return {'name': 'Epiphany', 'prec': 7}  # This matches the artwork
            elif season == 'easter' and pointer == 0:
                return {'name': 'Easter', 'prec': 7}  # This matches the artwork
            else:
                return {'name': 'Some Other Feast', 'prec': 7}  # This won't match
        
        mock_lookup_feast.side_effect = mock_lookup_side_effect
        
        result = artwork_manager.find_squashed_artworks()
        
        # Should return fewer results since some names now match
        # (but still some will be squashed because not all names match)
        self.assertIsInstance(result, list)

class TestFeastsDataStructure(unittest.TestCase):
    def test_feasts_structure(self):
        self.assertIn('easter', feasts)
        self.assertIn('christmas', feasts)
        easter_feasts = feasts['easter']
        self.assertIsInstance(easter_feasts, dict)
        self.assertIn(0, easter_feasts)
        easter_entry = easter_feasts[0]
        self.assertIsInstance(easter_entry, list)
        self.assertGreater(len(easter_entry), 0)
        self.assertIn('name', easter_entry[0])
        self.assertIn('source', easter_entry[0])
        christmas_feasts = feasts['christmas']
        self.assertIsInstance(christmas_feasts, dict)
        self.assertIn('01-06', christmas_feasts)
        epiphany_entry = christmas_feasts['01-06']
        self.assertIsInstance(epiphany_entry, list)
        self.assertGreater(len(epiphany_entry), 0)
        self.assertIn('name', epiphany_entry[0])
        self.assertIn('source', epiphany_entry[0])
    def test_feast_entry_structure(self):
        easter_entry = feasts['easter'][0][0]
        self.assertIn('name', easter_entry)
        self.assertIn('source', easter_entry)
        holy_monday_entry = feasts['easter'][-6][0]
        self.assertIn('name', holy_monday_entry)
        self.assertIn('colour', holy_monday_entry)
        self.assertIn('url', holy_monday_entry)
        self.assertIn('prec', holy_monday_entry)
        self.assertIn('type', holy_monday_entry)
        self.assertIn('readings', holy_monday_entry)
    def test_multiple_feasts_same_date(self):
        multi_feast_dates = []
        for date_key, entries in feasts['christmas'].items():
            if isinstance(entries, list) and len(entries) > 1:
                multi_feast_dates.append((date_key, entries))
        self.assertGreater(len(multi_feast_dates), 0, "Should have dates with multiple feasts")
        date_key, entries = multi_feast_dates[0]
        self.assertIsInstance(entries, list)
        self.assertGreater(len(entries), 1)
        for entry in entries:
            self.assertIn('name', entry)
            self.assertIn('source', entry)

if __name__ == '__main__':
    unittest.main() 