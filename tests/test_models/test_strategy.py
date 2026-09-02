import unittest
from models.strategy import COLOR_STRATS


class TestStrategy(unittest.TestCase):

    def test_strategy_combinations_count(self):
        """Verify that 127 color combinations are created"""
        self.assertEqual(len(COLOR_STRATS), 127)

if __name__ == '__main__':
    unittest.main()