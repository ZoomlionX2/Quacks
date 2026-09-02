import unittest
from config.tails_config import RAT_TAIL_LOCATIONS


class TestTailsConfig(unittest.TestCase):

    def test_total_milestones_count(self):
        """Verify the total number of tail milestones matches the expected count."""
        self.assertEqual(len(RAT_TAIL_LOCATIONS), 23)

    def test_boundary_milestone_locations(self):
        """Verify that the first and last physical tail milestones are correctly positioned."""
        # The first tail printed on the physical board sits at space 1
        self.assertEqual(RAT_TAIL_LOCATIONS[0], 1)

        # The last tail printed on the physical board sits at space 48
        self.assertEqual(RAT_TAIL_LOCATIONS[-1], 48)


if __name__ == '__main__':
    unittest.main()