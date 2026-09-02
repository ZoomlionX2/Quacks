import unittest
from unittest.mock import patch

from config.chip_config import ChipColor
from config.shop_config import SHOP_CATALOG
from game_engine.phase_3_evaluation import run_evaluation_phase

from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat
from models.supply_bank import SupplyBank


class TestPhase3Evaluation(unittest.TestCase):

    def setUp(self):
        self.mock_profile_a = GameStrategyProfile(
            colors=(ChipColor.PURPLE, ChipColor.BLUE, ChipColor.BLACK),
            value=ValueStrat.HIGHEST_SINGLE_VALUE,
            ruby=RubyStrat.DROPLET,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.LOW,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.MONEY
        )

        self.mock_profile_b = GameStrategyProfile(
            colors=(ChipColor.RED, ChipColor.ORANGE),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.MEDIUM,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.POINTS
        )

        self.player_a = Player(self.mock_profile_a)
        self.player_b = Player(self.mock_profile_b)
        self.supply_bank = SupplyBank(SHOP_CATALOG)
        self.current_round = 2


    def test_run_evaluation_phase(self):
        """Ensures the 6 evaluation phases are executed."""
        with (
            patch('game_engine.phase_3_evaluation.step_a_bonus_die.roll_bonus_die') as mock_step_a, \
            patch('game_engine.phase_3_evaluation.step_b_chip_actions.execute_chip_actions') as mock_step_b, \
            patch('game_engine.phase_3_evaluation.step_c_rubies.award_ruby') as mock_step_c, \
            patch('game_engine.phase_3_evaluation.step_d_points.award_victory_points') as mock_step_d, \
            patch('game_engine.phase_3_evaluation.step_e_buy_chips.execute_buying_phase') as mock_step_e, \
            patch('game_engine.phase_3_evaluation.step_f_end_of_turn.execute_end_of_turn_actions') as mock_step_f
        ):

            run_evaluation_phase(self.player_a, self.player_b, self.supply_bank, self.current_round)

            # Step A
            mock_step_a.assert_called_once_with(self.player_a, self.player_b, self.supply_bank)

            # Step B
            mock_step_b.assert_called_once_with(self.player_a, self.player_b)

            # Step C
            self.assertEqual(mock_step_c.call_count, 2)
            mock_step_c.assert_any_call(self.player_a)
            mock_step_c.assert_any_call(self.player_b)

            # Step D
            self.assertEqual(mock_step_d.call_count, 2)
            mock_step_d.assert_any_call(self.player_a, self.current_round)
            mock_step_d.assert_any_call(self.player_b, self.current_round)

            # Step E
            self.assertEqual(mock_step_e.call_count, 2)
            mock_step_e.assert_any_call(self.player_a, self.supply_bank, self.current_round)
            mock_step_e.assert_any_call(self.player_b, self.supply_bank, self.current_round)

            # Step F
            self.assertEqual(mock_step_f.call_count, 2)
            mock_step_f.assert_any_call(self.player_a, self.current_round)
            mock_step_f.assert_any_call(self.player_b, self.current_round)


if __name__ == '__main__':
    unittest.main()