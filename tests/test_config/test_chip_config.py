import unittest
from config.chip_config import ChipColor

class TestChipConfig(unittest.TestCase):

    def test_expected_colors_exist(self):
        """Ensure all 8 core ingredient colors are defined int the StrEnum."""
        expected_colors = {"white", "green", "blue", "red", "yellow", "orange", "purple", "black"}
        actual_colors = {color.value for color in ChipColor}
        self.assertEqual(actual_colors, expected_colors)

    def test_enum_length_and_uniqueness(self):
        """Guard against accidental duplicate string values"""
        # Check that there are exactly 8 names defined
        self.assertEqual(len(ChipColor.__members__), 8)

        # Check that there are exactly 8 unique active values
        self.assertEqual(len(ChipColor), 8)

if __name__ == '__main__':
    unittest.main()