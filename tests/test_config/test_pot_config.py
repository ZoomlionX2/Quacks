import unittest
from config.pot_config import POT_BOARD_SPACES


class TestPotConfig(unittest.TestCase):

    def test_pot_total_spaces(self):
        """Verify the board pot data contains exactly 54 spaces"""
        self.assertEqual(len(POT_BOARD_SPACES), 54)

    def test_pot_named_tuple_properties(self):
        """Verify board spaces return descriptive names and correct boolean ruby flags"""
        # Test space 0 (0, 0, 0)
        space_zero = POT_BOARD_SPACES[0]
        self.assertFalse(space_zero.ruby)
        self.assertEqual(space_zero.victory_points, 0)
        self.assertEqual(space_zero.money, 0)

        # Test space 5 (True, 0, 5)
        space_five = POT_BOARD_SPACES[5]
        self.assertTrue(space_five.ruby)
        self.assertEqual(space_five.victory_points, 0)
        self.assertEqual(space_five.money, 5)

        # Test last space (False, 15, 35)
        last_space = POT_BOARD_SPACES[53]
        self.assertFalse(last_space.ruby)
        self.assertEqual(last_space.victory_points, 15)
        self.assertEqual(last_space.money, 35)

if __name__ == '__main__':
    unittest.main()