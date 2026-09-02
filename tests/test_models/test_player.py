import unittest
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat
from models.strategy import ExplosionRoundStrat, ExplodedStrat
from config.chip_config import ChipColor
from models.player import Player

class TestPlayer(unittest.TestCase):

    def setUp(self):
        # Create a dummy strategy profile
        self.mock_profile = GameStrategyProfile(
            colors=(ChipColor.GREEN, ChipColor.BLUE),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.MEDIUM,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.POINTS
        )

        # Instantiate a player with that strategy profile
        self.player = Player(strategy_profile=self.mock_profile)

    def test_player_initialization(self):
        """Verify the player state initializes with clean defaults and correct profile"""
        self.assertEqual(self.player.victory_points, 0)
        self.assertEqual(self.player.current_space, 0)
        self.assertEqual(self.player.rat_token, 0)
        self.assertEqual(self.player.ruby, 1)
        self.assertTrue(self.player.flask_full)
        self.assertEqual(self.player.strategy_profile.value, ValueStrat.HIGHEST_VALUE_PAIR)

    def test_starting_bag_composition(self):
        """Verify the starting bag populates with exactly 9 chips of the correct types"""
        self.player.setup_starting_bag()

        # Total count check
        self.assertEqual(len(self.player.unplayed_chips), 9)

        # Type checks
        white_chips = [c for c in self.player.unplayed_chips if c.color == ChipColor.WHITE]
        green_chips = [c for c in self.player.unplayed_chips if c.color == ChipColor.GREEN]
        orange_chips = [c for c in self.player.unplayed_chips if c.color == ChipColor.ORANGE]

        self.assertEqual(len(white_chips), 7)
        self.assertEqual(len(green_chips), 1)
        self.assertEqual(len(orange_chips), 1)

        # Value sum check: 4*(1) + 2*(2) + 1*(3) = 11 total white value
        white_value_sum = sum(c.value for c in white_chips)
        self.assertEqual(white_value_sum, 11)


if __name__ == '__main__':
    unittest.main()

