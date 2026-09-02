import unittest
from config.chip_config import ChipColor
from models.chip import Chip

class TestChip(unittest.TestCase):

    def test_chip_initialization(self):
        """Verify that a Chip correctly stores and returns its color and value properties"""
        # Create a green 4 chip
        green_4 = Chip(color=ChipColor.GREEN, value=4)

        # Verify attributes read back out cleanly
        self.assertEqual(green_4.color, ChipColor.GREEN)
        self.assertEqual(green_4.value, 4)

if __name__ == '__main__':
    unittest.main()