import random
import unittest

from config.chip_config import ChipColor
from config.shop_config import SHOP_CATALOG
from game_engine.phase_3_evaluation.step_a_bonus_die import execute_bonus_die_reward, roll_bonus_die
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat
from models.supply_bank import SupplyBank


class TestStepABonusDie(unittest.TestCase):

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

        self.supply_bank = SupplyBank(SHOP_CATALOG)

    def test_execute_bonus_die_reward(self):
        """Verifies that bonus die rewards are successfully granted."""
        # Set baseline values
        self.player1.victory_points = 0
        self.player1.droplet = 0
        self.player1.unplayed_chips.clear()
        self.player1.ruby = 0

        # Award player1 each reward
        for roll in range(1, 7):
            execute_bonus_die_reward(self.player1, roll, self.supply_bank)

        # Verify rewards
        self.assertEqual(self.player1.victory_points, 4)
        self.assertEqual(self.player1.droplet, 1)
        self.assertTrue(Chip(ChipColor.ORANGE, 1) in self.player1.unplayed_chips)
        self.assertEqual(self.player1.ruby, 1)

    def test_roll_bonus_die(self):
        """Verifies that players are correctly selected to roll bonus die."""
        original_randint = random.randint
        random.randint = lambda x, y: 1

        try:

            # Neither qualify because both exploded
            self.player1.played_chips.clear()
            self.player2.played_chips.clear()
            self.player1.victory_points = 0
            self.player2.victory_points = 0

            for _ in range(4):
                self.player1.played_chips.append(Chip(ChipColor.WHITE, 2))
                self.player2.played_chips.append(Chip(ChipColor.WHITE, 2))

            roll_bonus_die(self.player1, self.player2, self.supply_bank)

            self.assertEqual(self.player1.victory_points, 0)
            self.assertEqual(self.player2.victory_points, 0)


            # One qualifies while the other exploded
            self.player1.played_chips.pop()

            roll_bonus_die(self.player1, self.player2, self.supply_bank)

            self.assertEqual(self.player1.victory_points, 1)
            self.assertEqual(self.player2.victory_points, 0)


            # Both qualify by reaching final scoring space
            self.player2.played_chips.pop()
            self.player1.current_space = 53
            self.player2.current_space = 53
            self.player1.victory_points = 0
            self.player2.victory_points = 0

            roll_bonus_die(self.player1, self.player2, self.supply_bank)

            self.assertEqual(self.player1.victory_points, 1)
            self.assertEqual(self.player2.victory_points, 1)


            # Only one qualifies by reaching final scoring space
            self.player2.current_space = 20
            self.player1.victory_points = 0
            self.player2.victory_points = 0

            roll_bonus_die(self.player1, self.player2, self.supply_bank)

            self.assertEqual(self.player1.victory_points, 1)
            self.assertEqual(self.player2.victory_points, 0)


            # Both qualify through a tie, but not on the final scoring space
            self.player1.current_space = 17
            self.player2.current_space = 17
            self.player1.victory_points = 0
            self.player2.victory_points = 0

            roll_bonus_die(self.player1, self.player2, self.supply_bank)

            self.assertEqual(self.player1.victory_points, 1)
            self.assertEqual(self.player2.victory_points, 1)


            # Only one qualifies by reaching a farther space, but not the final scoring space
            self.player1.current_space = 11
            self.player2.current_space = 7
            self.player1.victory_points = 0
            self.player2.victory_points = 0

            roll_bonus_die(self.player1, self.player2, self.supply_bank)

            self.assertEqual(self.player1.victory_points, 1)
            self.assertEqual(self.player2.victory_points, 0)


        finally:
            random.randint = original_randint

if __name__ == '__main__':
    unittest.main()