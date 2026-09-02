import unittest
from unittest.mock import patch

from config.chip_config import ChipColor
from config.shop_config import SHOP_CATALOG
from game_engine import play_single_round
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat
from models.supply_bank import SupplyBank


class TestPlaySingleRound(unittest.TestCase):

    def test_play_single_round(self):
        """Ensures the three main game phases are executed."""
        with (
            patch('game_engine.phase_1_prep.calculate_rat_tails') as mock_phase_1, \
            patch('game_engine.phase_2_potions.run_potions_phase') as mock_phase_2, \
            patch('game_engine.phase_3_evaluation.run_evaluation_phase') as mock_phase_3
        ):
            game_strategy_profile = GameStrategyProfile(
                colors=(ChipColor.RED,),
                value=ValueStrat.HIGHEST_VALUE_PAIR,
                ruby=RubyStrat.SAVE,
                flask=FlaskStrat.AT_RISK,
                explosion_prob=ExplosionProbabilityToleranceStrat.LOW,
                explosion_round=ExplosionRoundStrat.MID,
                exploded=ExplodedStrat.POINTS
            )

            player_a = Player(game_strategy_profile)
            player_b = Player(game_strategy_profile)
            supply_bank = SupplyBank(SHOP_CATALOG)
            current_round = 3

            play_single_round(player_a, player_b, supply_bank, current_round)

            # Phase 1
            mock_phase_1.assert_called_once_with(player_a, player_b)

            # Phase 2
            self.assertEqual(mock_phase_2.call_count, 2)
            mock_phase_2.assert_any_call(player_a, current_round)
            mock_phase_2.assert_any_call(player_b, current_round)

            # Phase 3
            mock_phase_3.assert_called_once_with(player_a, player_b, supply_bank, current_round)


if __name__ == '__main__':
    unittest.main()