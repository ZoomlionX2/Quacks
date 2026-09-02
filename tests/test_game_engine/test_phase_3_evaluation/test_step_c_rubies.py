import unittest

from config.chip_config import ChipColor
from game_engine.phase_2_potions import update_current_space
from game_engine.phase_3_evaluation.step_c_rubies import award_ruby
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat


class TestStepCRubies(unittest.TestCase):

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


    def test_award_ruby(self):
        """Verify that rubies are awarded according to scoring space."""
        # Last chip on space before ruby-awarding space
        self.player.played_chips.clear()
        self.player.ruby = 0
        self.player.droplet = 1
        self.player.rat_token = 0
        self.player.current_space = 0

        update_current_space(self.player, Chip(ChipColor.WHITE, 2), True)
        update_current_space(self.player, Chip(ChipColor.WHITE, 2), False)

        award_ruby(self.player)
        self.assertEqual(self.player.ruby, 1)

        # Last chip not on space before ruby-awarding space
        self.player.played_chips.clear()
        self.player.ruby = 0
        self.player.droplet = 1
        self.player.rat_token = 0
        self.player.current_space = 0

        update_current_space(self.player, Chip(ChipColor.WHITE, 2), True)
        update_current_space(self.player, Chip(ChipColor.WHITE, 2), False)
        update_current_space(self.player, Chip(ChipColor.WHITE, 2), False)

        award_ruby(self.player)
        self.assertEqual(self.player.ruby, 0)

if __name__ == '__main__':
    unittest.main()