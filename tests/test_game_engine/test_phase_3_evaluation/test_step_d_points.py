import unittest
from dataclasses import replace
from unittest.mock import patch

from config.chip_config import ChipColor
from game_engine.phase_2_potions import update_current_space
from game_engine.phase_3_evaluation.step_d_points import award_victory_points
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat


class TestStepDPoints(unittest.TestCase):

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

        # Instantiate player with that strategy profile
        self.player = Player(strategy_profile=self.mock_profile)


    def test_award_victory_points(self):
        """Verifies victory points are awarded according to scoring space and eligibility."""
        # Player has not exploded
        self.player.victory_points = 0
        self.player.current_space = 0
        self.player.droplet = 1
        self.player.rat_token = 0

        self.player.played_chips.clear()
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        update_current_space(self.player, Chip(ChipColor.WHITE, 2), True)
        for _ in range(2):
            self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
            update_current_space(self.player, Chip(ChipColor.WHITE, 2), False)

        award_victory_points(self.player, 1)
        self.assertEqual(self.player.victory_points, 1)

        # Player has exploded but chose points
        self.player.victory_points = 0
        self.player.current_space = 0
        self.player.droplet = 1
        self.player.rat_token = 0

        self.player.played_chips.clear()
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        update_current_space(self.player, Chip(ChipColor.WHITE, 2), True)
        for _ in range(3):
            self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
            update_current_space(self.player, Chip(ChipColor.WHITE, 2), False)

        award_victory_points(self.player, 1)
        self.assertEqual(self.player.victory_points, 1)


        # Player has exploded but chose money
        new_strategy_profile = replace(
            self.mock_profile,
            exploded=ExplodedStrat.MONEY
        )
        self.player.strategy_profile = new_strategy_profile

        self.player.victory_points = 0
        self.player.current_space = 0
        self.player.droplet = 1
        self.player.rat_token = 0

        self.player.played_chips.clear()
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        update_current_space(self.player, Chip(ChipColor.WHITE, 2), True)
        for _ in range(3):
            self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
            update_current_space(self.player, Chip(ChipColor.WHITE, 2), False)

        award_victory_points(self.player, 1)
        self.assertEqual(self.player.victory_points, 0)


        # Player has exploded but chooses based on round
        new_strategy_profile = replace(
            self.mock_profile,
            exploded=ExplodedStrat.ROUND_BASED_EARLY
        )
        self.player.strategy_profile = new_strategy_profile

        self.player.victory_points = 0
        self.player.current_space = 0
        self.player.droplet = 1
        self.player.rat_token = 0

        self.player.played_chips.clear()
        self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
        update_current_space(self.player, Chip(ChipColor.WHITE, 2), True)
        for _ in range(3):
            self.player.played_chips.append(Chip(ChipColor.WHITE, 2))
            update_current_space(self.player, Chip(ChipColor.WHITE, 2), False)

        award_victory_points(self.player, 1)
        self.assertEqual(self.player.victory_points, 0)

        award_victory_points(self.player, 4)
        self.assertEqual(self.player.victory_points, 1)


        # Player has exploded but chooses randomly
        new_strategy_profile = replace(
            self.mock_profile,
            exploded=ExplodedStrat.RANDOM
        )
        self.player.strategy_profile = new_strategy_profile

        self.player.victory_points = 0
        self.player.current_space = 6
        self.player.droplet = 1
        self.player.rat_token = 0

        with (
            patch('random.choice') as mock_choice, \
            patch('game_engine.phase_2_potions.has_exploded') as mock_has_exploded
        ):
            mock_choice.return_value = True
            mock_has_exploded.return_value = True

            award_victory_points(self.player, 7)
            self.assertEqual(self.player.victory_points, 1)


if __name__ == '__main__':
    unittest.main()