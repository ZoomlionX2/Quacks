import unittest

from config.chip_config import ChipColor
from game_engine.phase_3_evaluation.step_b_chip_actions import execute_black_special_action, execute_green_special_action, \
    execute_purple_special_action, execute_chip_actions
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat


class TestStepBChipActions(unittest.TestCase):

    def setUp(self):
        """Set up clean objects."""
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

        # Instantiate player with that strategy profile
        self.player1 = Player(strategy_profile=self.mock_profile)
        self.player2 = Player(strategy_profile=self.mock_profile)

    def test_execute_black_special_action(self):
        """Verifies that black chip special actions are properly executed."""
        # Neither player has played black chips
        self.player1.played_chips.clear()
        self.player2.played_chips.clear()
        self.player1.droplet = 0
        self.player2.droplet = 0

        execute_black_special_action(self.player1, self.player2)

        self.assertEqual(self.player1.droplet, 0)
        self.assertEqual(self.player2.droplet, 0)


        # Both players played an equal amount of black chips
        self.player1.played_chips.append(Chip(ChipColor.BLACK, 1))
        self.player2.played_chips.append(Chip(ChipColor.BLACK, 1))

        execute_black_special_action(self.player1, self.player2)

        self.assertEqual(self.player1.droplet, 1)
        self.assertEqual(self.player2.droplet, 1)


        # One player has played more black chips than the other
        self.player2.played_chips.clear()
        self.player1.droplet = 0
        self.player2.droplet = 0
        self.player1.ruby = 0
        self.player2.ruby = 0

        execute_black_special_action(self.player1, self.player2)

        self.assertEqual(self.player1.droplet, 1)
        self.assertEqual(self.player1.ruby, 1)
        self.assertEqual(self.player2.droplet, 0)
        self.assertEqual(self.player2.ruby, 0)


    def test_execute_green_special_action(self):
        """Verifies green chip special actions are properly executed."""
        # No green on last or second-to-last space (awards 0 rubies)
        self.player1.ruby = 0
        self.player1.played_chips.clear()
        for _ in range(5):
            self.player1.played_chips.append(Chip(ChipColor.ORANGE, 1))

        execute_green_special_action(self.player1)
        self.assertEqual(self.player1.ruby, 0)

        # Green on last space (awards 1 ruby)
        self.player1.played_chips.append(Chip(ChipColor.GREEN, 1))
        execute_green_special_action(self.player1)
        self.assertEqual(self.player1.ruby, 1)

        # Green on second-to-last space (awards 1 ruby)
        self.player1.ruby = 0
        self.player1.played_chips.append(Chip(ChipColor.ORANGE, 1))
        execute_green_special_action(self.player1)
        self.assertEqual(self.player1.ruby, 1)

        # Green on last and second-to-last space (awards 2 rubies)
        self.player1.ruby = 0
        self.player1.played_chips.pop()
        self.player1.played_chips.append(Chip(ChipColor.GREEN, 4))
        execute_green_special_action(self.player1)
        self.assertEqual(self.player1.ruby, 2)


    def test_execute_purple_special_action(self):
        """Verifies purple chip special actions are properly executed."""
        # No purple chips in pot
        self.player1.victory_points = 0
        self.player1.ruby = 0
        self.player1.droplet = 0
        self.player1.played_chips.clear()
        for _ in range(5):
            self.player1.played_chips.append(Chip(ChipColor.ORANGE, 1))

        execute_purple_special_action(self.player1)
        self.assertEqual(self.player1.victory_points, 0)
        self.assertEqual(self.player1.ruby, 0)
        self.assertEqual(self.player1.droplet, 0)

        # One purple chip in pot
        self.player1.played_chips.append(Chip(ChipColor.PURPLE, 1))
        execute_purple_special_action(self.player1)
        self.assertEqual(self.player1.victory_points, 1)
        self.assertEqual(self.player1.ruby, 0)
        self.assertEqual(self.player1.droplet, 0)

        # Two purple chips in pot
        self.player1.victory_points = 0

        self.player1.played_chips.append(Chip(ChipColor.PURPLE, 1))
        execute_purple_special_action(self.player1)
        self.assertEqual(self.player1.victory_points, 1)
        self.assertEqual(self.player1.ruby, 1)
        self.assertEqual(self.player1.droplet, 0)

        # Three purple chips in pot
        self.player1.victory_points = 0
        self.player1.ruby = 0
        self.player1.droplet = 0

        self.player1.played_chips.append(Chip(ChipColor.PURPLE, 1))
        execute_purple_special_action(self.player1)
        self.assertEqual(self.player1.victory_points, 2)
        self.assertEqual(self.player1.ruby, 0)
        self.assertEqual(self.player1.droplet, 1)

        # Five purple chips in pot
        self.player1.victory_points = 0
        self.player1.ruby = 0
        self.player1.droplet = 0

        self.player1.played_chips.append(Chip(ChipColor.PURPLE, 1))
        self.player1.played_chips.append(Chip(ChipColor.PURPLE, 1))
        execute_purple_special_action(self.player1)
        self.assertEqual(self.player1.victory_points, 2)
        self.assertEqual(self.player1.ruby, 0)
        self.assertEqual(self.player1.droplet, 1)


    def test_execute_chip_actions(self):
        """Verify that the Chip Action phase is executed correctly."""

        # Set up starting values
        self.player1.victory_points = 0
        self.player1.droplet = 0
        self.player1.ruby = 0

        self.player2.victory_points = 0
        self.player2.droplet = 0
        self.player2.ruby = 0

        # Set up player1 played chips
        for _ in range(3):
            self.player1.played_chips.append(Chip(ChipColor.WHITE, 1))
        self.player1.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player1.played_chips.append(Chip(ChipColor.BLACK, 1))
        self.player1.played_chips.append(Chip(ChipColor.BLACK, 1))
        self.player1.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player1.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player1.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player1.played_chips.append(Chip(ChipColor.GREEN, 1))
        self.player1.played_chips.append(Chip(ChipColor.ORANGE, 1))

        # Set up player2 played chips
        self.player2.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player2.played_chips.append(Chip(ChipColor.PURPLE, 1))
        self.player2.played_chips.append(Chip(ChipColor.BLACK, 1))
        self.player2.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player2.played_chips.append(Chip(ChipColor.ORANGE, 1))
        self.player2.played_chips.append(Chip(ChipColor.PURPLE, 1))
        self.player2.played_chips.append(Chip(ChipColor.GREEN, 1))
        self.player2.played_chips.append(Chip(ChipColor.ORANGE, 1))
        for _ in range(3):
            self.player2.played_chips.append(Chip(ChipColor.WHITE, 1))
        self.player2.played_chips.append(Chip(ChipColor.GREEN, 1))

        # Run Chip Action phase and verify rewarded values
        execute_chip_actions(self.player1, self.player2)

        self.assertEqual(self.player1.victory_points, 0)
        self.assertEqual(self.player1.droplet, 1)
        self.assertEqual(self.player1.ruby, 2)

        self.assertEqual(self.player2.victory_points, 1)
        self.assertEqual(self.player2.droplet, 0)
        self.assertEqual(self.player2.ruby, 2)

if __name__ == '__main__':
    unittest.main()