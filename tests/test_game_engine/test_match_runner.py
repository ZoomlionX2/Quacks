import unittest
from unittest.mock import patch, call, ANY

from config.chip_config import ChipColor
from game_engine.match_runner import generate_results, run_match
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat


class TestMatchRunner(unittest.TestCase):

    def setUp(self):
        self.mock_profile = GameStrategyProfile(
            colors=(ChipColor.GREEN, ChipColor.BLUE),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.MEDIUM,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.POINTS
        )

        self.player_a = Player(self.mock_profile)
        self.player_b = Player(self.mock_profile)


    def test_generate_results(self):
        """Ensure match end stats are correctly returned."""
        # Create player_a bag
        player_a_bag = [Chip(ChipColor.WHITE, 2), Chip(ChipColor.GREEN, 1), Chip(ChipColor.GREEN, 1),
                        Chip(ChipColor.BLUE, 4), Chip(ChipColor.BLUE, 1), Chip(ChipColor.GREEN, 2),
                        Chip(ChipColor.ORANGE, 1), Chip(ChipColor.BLUE, 2)]

        self.player_a.unplayed_chips.extend(player_a_bag)

        # Declare milestones
        self.player_a.droplet = 5
        self.player_a.current_space = 27
        self.player_a.explosion_count = 3
        self.player_a.farthest_space_reached = 27

        # Declare outcomes
        self.player_a.victory_points = 50
        self.player_b.victory_points = 10

        results = generate_results(self.player_a, self.player_b)

        # Color strategy
        self.assertEqual(results["color_strat_all"], 8) # The first 7 strats are the single colors
        self.assertEqual(results["color_strat_green"], 1)
        self.assertEqual(results["color_strat_blue"], 1)
        self.assertEqual(results["color_strat_red"], 0)
        self.assertEqual(results["color_strat_yellow"], 0)
        self.assertEqual(results["color_strat_orange"], 0)
        self.assertEqual(results["color_strat_purple"], 0)
        self.assertEqual(results["color_strat_black"], 0)

        # Value strategy
        self.assertEqual(results["value_strat_pair"], 1)
        self.assertEqual(results["value_strat_single"], 0)
        self.assertEqual(results["value_strat_disparity"], 0)

        # Ruby strategy
        self.assertEqual(results["ruby_strat_save"], 1)
        self.assertEqual(results["ruby_strat_droplet"], 0)
        self.assertEqual(results["ruby_strat_flask"], 0)
        self.assertEqual(results["ruby_strat_balanced"], 0)

        # Flask strategy
        self.assertEqual(results["flask_strat_three"], 0)
        self.assertEqual(results["flask_strat_risk"], 1)
        self.assertEqual(results["flask_strat_ruby"], 0)
        self.assertEqual(results["flask_strat_seventy"], 0)
        self.assertEqual(results["flask_strat_fifty"], 0)

        # Explosion risk tolerance probability-based strategy
        self.assertEqual(results["ex_prob_strat_high"], 0)
        self.assertEqual(results["ex_prob_strat_medium"], 1)
        self.assertEqual(results["ex_prob_strat_low"], 0)
        self.assertEqual(results["ex_prob_strat_very_low"], 0)
        self.assertEqual(results["ex_prob_strat_never"], 0)

        # Explosion risk tolerance round-based strategy
        self.assertEqual(results["ex_round_strat_always"], 0)
        self.assertEqual(results["ex_round_strat_early"], 0)
        self.assertEqual(results["ex_round_strat_early_mid"], 0)
        self.assertEqual(results["ex_round_strat_mid"], 1)
        self.assertEqual(results["ex_round_strat_mid_late"], 0)
        self.assertEqual(results["ex_round_strat_late"], 0)

        # Exploded strategy
        self.assertEqual(results["exploded_strat_points"], 1)
        self.assertEqual(results["exploded_strat_money"], 0)
        self.assertEqual(results["exploded_strat_early"], 0)
        self.assertEqual(results["exploded_strat_mid"], 0)

        # Chip distribution
        self.assertEqual(results["green-1"], 2)
        self.assertEqual(results["green-2"], 1)
        self.assertEqual(results["green-4"], 0)
        self.assertEqual(results["blue-1"], 1)
        self.assertEqual(results["blue-2"], 1)
        self.assertEqual(results["blue-4"], 1)
        self.assertEqual(results["red-1"], 0)
        self.assertEqual(results["red-2"], 0)
        self.assertEqual(results["red-4"], 0)
        self.assertEqual(results["yellow-1"], 0)
        self.assertEqual(results["yellow-2"], 0)
        self.assertEqual(results["yellow-4"], 0)
        self.assertEqual(results["orange-1"], 1)
        self.assertEqual(results["purple-1"], 0)
        self.assertEqual(results["black-1"], 0)

        # Color distribution
        self.assertEqual(results["green_count"], 3)
        self.assertEqual(results["blue_count"], 3)
        self.assertEqual(results["red_count"], 0)
        self.assertEqual(results["yellow_count"], 0)
        self.assertEqual(results["orange_count"], 1)
        self.assertEqual(results["purple_count"], 0)
        self.assertEqual(results["black_count"], 0)

        # Value distribution (should NOT include the white)
        self.assertEqual(results["one_count"], 4)
        self.assertEqual(results["two_count"], 2)
        self.assertEqual(results["four_count"], 1)

        # Milestones
        self.assertEqual(results["final_droplet_position"], 5)
        self.assertEqual(results["farthest_space_reached"], 27)
        self.assertEqual(results["explosion_count"], 3)

        # Outcome
        self.assertEqual(results["player_a_vp"], 50)
        self.assertEqual(results["player_b_vp"], 10)
        self.assertEqual(results["margin"], 40)
        self.assertEqual(results["percent_dif"], 4.64)
        self.assertEqual(results["tie"], 0)
        self.assertEqual(results["player_a_won"], 1)


    def test_run_match(self):
        """Mocks the core loop steps to verify the 9-round match timeline runs chronologically."""
        with (
            patch('game_engine.match_runner.play_single_round') as mock_round,
            patch('game_engine.match_runner.generate_results') as mock_results
        ):
            mock_results.return_value = {"mock_key": "success_data"}

            results = run_match(self.mock_profile, self.mock_profile)

            self.assertEqual(mock_round.call_count, 9)

            self.assertEqual(mock_round.call_args_list[0], call(ANY, ANY, ANY, 1))
            self.assertEqual(mock_round.call_args_list[8], call(ANY, ANY, ANY, 9))

            mock_results.assert_called_once()
            self.assertEqual(results, {"mock_key": "success_data"})


if __name__ == '__main__':
    unittest.main()
