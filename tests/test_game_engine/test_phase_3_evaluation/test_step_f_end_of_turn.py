import unittest
from dataclasses import replace
from unittest.mock import patch

from config.chip_config import ChipColor
from game_engine.phase_3_evaluation.step_f_end_of_turn import spend_rubies, execute_end_of_turn_actions
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat


class TestStepFEndOfTurn(unittest.TestCase):

    def setUp(self):
        """Set up clean objects."""
        # Create a dummy strategy profile
        self.mock_profile = GameStrategyProfile(
            colors=(ChipColor.GREEN, ChipColor.BLUE),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.DROPLET,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.MEDIUM,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.POINTS
        )

        # Instantiate player with that strategy profile
        self.player = Player(strategy_profile=self.mock_profile)


    def test_spend_rubies(self):
        """Ensures rubies are spent according to the round and ruby strategy."""
        # Round 9 -> buy victory points
        current_round = 9
        self.player.ruby = 10
        self.player.droplet = 0
        self.player.flask_full = False
        self.player.victory_points = 0

        spend_rubies(self.player, current_round)
        self.assertEqual(self.player.ruby, 10)
        self.assertEqual(self.player.droplet, 0)
        self.assertFalse(self.player.flask_full)
        self.assertEqual(self.player.victory_points, 5)

        # SAVE strategy -> do not spend rubies
        new_strategy_profile = replace(
            self.mock_profile,
            ruby=RubyStrat.SAVE
        )
        self.player = Player(new_strategy_profile)

        current_round = 8
        self.player.ruby = 11
        self.player.droplet = 0
        self.player.flask_full = False

        spend_rubies(self.player, current_round)
        self.assertEqual(self.player.ruby, 11)
        self.assertEqual(self.player.droplet, 0)
        self.assertFalse(self.player.flask_full)


        # DROPLET strategy -> buy droplet advances
        new_strategy_profile = replace(
            self.mock_profile,
            ruby=RubyStrat.DROPLET
        )
        self.player = Player(new_strategy_profile)

        current_round = 8
        self.player.ruby = 11
        self.player.droplet = 0
        self.player.flask_full = False

        spend_rubies(self.player, current_round)
        self.assertEqual(self.player.ruby, 1)
        self.assertEqual(self.player.droplet, 5)
        self.assertFalse(self.player.flask_full)

        # FLASK strategy -> buy one flask refill if empty
        new_strategy_profile = replace(
            self.mock_profile,
            ruby=RubyStrat.FLASK
        )
        self.player = Player(new_strategy_profile)

        current_round = 8
        self.player.ruby = 11
        self.player.droplet = 0
        self.player.flask_full = False

        spend_rubies(self.player, current_round)
        self.assertEqual(self.player.ruby, 9)
        self.assertEqual(self.player.droplet, 0)
        self.assertTrue(self.player.flask_full)

        # BALANCED strategy -> buy flask on even rounds, spend leftover on one droplet advance
        new_strategy_profile = replace(
            self.mock_profile,
            ruby=RubyStrat.BALANCED
        )
        self.player = Player(new_strategy_profile)

        current_round = 8
        self.player.ruby = 11
        self.player.droplet = 0
        self.player.flask_full = False

        spend_rubies(self.player, current_round)
        self.assertEqual(self.player.ruby, 7)
        self.assertEqual(self.player.droplet, 1)
        self.assertTrue(self.player.flask_full)

        # BALANCED strategy -> buy one droplet advance on odd rounds
        new_strategy_profile = replace(
            self.mock_profile,
            ruby=RubyStrat.BALANCED
        )
        self.player = Player(new_strategy_profile)

        current_round = 7
        self.player.ruby = 11
        self.player.droplet = 0
        self.player.flask_full = False

        spend_rubies(self.player, current_round)
        self.assertEqual(self.player.ruby, 9)
        self.assertEqual(self.player.droplet, 1)
        self.assertFalse(self.player.flask_full)

        # RANDOM strategy -> randomly select from one of the other strategies
        new_strategy_profile = replace(
            self.mock_profile,
            ruby=RubyStrat.RANDOM
        )
        self.player = Player(new_strategy_profile)

        current_round = 7
        self.player.ruby = 11
        self.player.droplet = 0
        self.player.flask_full = False

        with patch('random.choice') as mock_choice:
            mock_choice.return_value = RubyStrat.SAVE
            spend_rubies(self.player, current_round)

            self.assertEqual(self.player.ruby, 11)
            self.assertEqual(self.player.droplet, 0)
            self.assertFalse(self.player.flask_full)


    def test_execute_end_of_turn_actions(self):
        """Ensures end-of-turn actions are correctly carried out."""
        current_round = 7
        self.player.ruby = 5
        self.player.droplet = 0
        self.player.flask_full = False
        self.player.current_space = 9

        execute_end_of_turn_actions(self.player, current_round)
        self.assertEqual(self.player.ruby, 1)
        self.assertEqual(self.player.droplet, 2)
        self.assertFalse(self.player.flask_full)
        self.assertEqual(self.player.current_space, 0)


if __name__ == '__main__':
    unittest.main()