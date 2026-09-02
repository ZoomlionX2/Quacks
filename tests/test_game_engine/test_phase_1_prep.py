import unittest
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat
from models.strategy import ExplosionRoundStrat, ExplodedStrat
from config.chip_config import ChipColor
from game_engine.phase_1_prep import calculate_rat_tails

class TestPhase1Prep(unittest.TestCase):

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

        # Instantiate two players with that strategy profile
        self.player1 = Player(strategy_profile=self.mock_profile)
        self.player2 = Player(strategy_profile=self.mock_profile)

    # calculate_rat_tails()
    def test_tied_score(self):
        """Verify that both player's rat token is reset to zero if score is tied."""
        self.player1.victory_points = 20
        self.player2.victory_points = 20
        calculate_rat_tails(self.player1, self.player2)
        self.assertEqual(self.player1.rat_token, 0)
        self.assertEqual(self.player2.rat_token, 0)

    def test_no_tie_no_wrap(self):
        """Verify trailing player's rat token is correctly updated when leading player has not wrapped around the
        scoring track."""
        self.player1.victory_points = 20
        self.player2.victory_points = 37
        calculate_rat_tails(self.player1, self.player2)
        self.assertEqual(self.player1.rat_token, 9)
        self.assertEqual(self.player2.rat_token, 0)

    def test_no_tie_wrap_once(self):
        """Verify trailing player's rat token is correctly updated when leading player has wrapped around the
        scoring track once."""
        self.player1.victory_points = 71
        self.player2.victory_points = 37
        calculate_rat_tails(self.player1, self.player2)
        self.assertEqual(self.player1.rat_token, 0)
        self.assertEqual(self.player2.rat_token, 15)

    def test_no_tie_wrap_twice(self):
        """Verify trailing player's rat token is correctly updated when leading player has wrapped around the
        scoring track twice."""
        self.player1.victory_points = 121
        self.player2.victory_points = 37
        calculate_rat_tails(self.player1, self.player2)
        self.assertEqual(self.player1.rat_token, 0)
        self.assertEqual(self.player2.rat_token, 38)

    def test_no_tie_both_wrap(self):
        """Verify trailing player's rat token is correctly updated when both players have wrapped around the
        scoring track once."""
        self.player1.victory_points = 59
        self.player2.victory_points = 53
        calculate_rat_tails(self.player1, self.player2)
        self.assertEqual(self.player1.rat_token, 0)
        self.assertEqual(self.player2.rat_token, 2)


if __name__ == '__main__':
    unittest.main()