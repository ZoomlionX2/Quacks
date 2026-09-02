import unittest
from unittest.mock import patch
from dataclasses import replace

from config.chip_config import ChipColor
from config.shop_config import SHOP_CATALOG, ShopItem
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat
from game_engine.phase_3_evaluation.step_e_buy_chips import is_color_unlocked, create_buying_priority, get_max_price, \
    finalize_chip_purchase, execute_buying_phase
from models.supply_bank import SupplyBank


class TestStepEBuyChips(unittest.TestCase):

    def setUp(self):
        self.mock_profile = GameStrategyProfile(
            colors=(ChipColor.GREEN, ChipColor.BLUE, ChipColor.PURPLE, ChipColor.ORANGE),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.MEDIUM,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.POINTS
        )
        self.player = Player(self.mock_profile)
        self.current_round = 2

    def test_create_buying_priority(self):
        """Ensures the returned list contains the colors ranked from the least chips owned to greatest with ties broken
        using the max price. No white chips should be included."""
        self.player.unplayed_chips.extend([Chip(ChipColor.GREEN, 2), Chip(ChipColor.GREEN, 4),
                                                        Chip(ChipColor.GREEN, 1), Chip(ChipColor.BLUE, 1),
                                                        Chip(ChipColor.BLUE, 4), Chip(ChipColor.BLUE, 1),
                                                        Chip(ChipColor.PURPLE, 1), Chip(ChipColor.WHITE, 2),
                                                        Chip(ChipColor.WHITE, 2), Chip(ChipColor.WHITE, 3),
                                                        Chip(ChipColor.WHITE, 1), Chip(ChipColor.WHITE, 1)])

        preferred_color_list = create_buying_priority(self.player, use_fallback=False)
        self.assertEqual(preferred_color_list, [ChipColor.ORANGE, ChipColor.PURPLE, ChipColor.BLUE, ChipColor.GREEN])

        nonpreferred_color_list = create_buying_priority(self.player, use_fallback=True)
        self.assertEqual(nonpreferred_color_list, [ChipColor.YELLOW, ChipColor.RED, ChipColor.BLACK])


    def test_create_buying_priority_random(self):
        """Ensures that supplying an empty list triggers the return of a list of all colors in random order."""
        new_strategy_profile = replace(
            self.mock_profile,
            colors=()
        )
        self.player = Player(new_strategy_profile)

        with patch('random.sample') as mock_color_list:
            mock_color_list.return_value = [ChipColor.YELLOW, ChipColor.BLACK, ChipColor.ORANGE, ChipColor.GREEN,
                                            ChipColor.BLUE, ChipColor.RED, ChipColor.PURPLE]
            result = create_buying_priority(self.player, False)
            self.assertEqual(result, [ChipColor.YELLOW, ChipColor.BLACK, ChipColor.ORANGE, ChipColor.GREEN,
                                            ChipColor.BLUE, ChipColor.RED, ChipColor.PURPLE])

    def test_get_max_price(self):
        """Verifies that the highest-priced color variant is found in the shop."""
        self.assertEqual(get_max_price(ChipColor.GREEN), 14)


    def test_is_color_unlocked(self):
        """Ensures that colors are correctly gated by round."""
        self.assertFalse(is_color_unlocked(ChipColor.YELLOW, 1))
        self.assertFalse(is_color_unlocked(ChipColor.PURPLE, 2))
        self.assertTrue(is_color_unlocked(ChipColor.YELLOW, 2))
        self.assertTrue(is_color_unlocked(ChipColor.YELLOW, 4))


    def test_finalize_chip_purchase(self):
        """Ensures that the player bag, their money, and the supply bank are correctly updated when a chip is purchased."""
        supply_bank = SupplyBank(SHOP_CATALOG)
        self.player.unplayed_chips.clear()
        money = 30
        leftover_money = finalize_chip_purchase(self.player, supply_bank, ShopItem(ChipColor.BLUE, 2, 10, 10), money)

        self.assertEqual(supply_bank[ShopItem(ChipColor.BLUE, 2, 10, 10)], 9)
        self.assertEqual(self.player.unplayed_chips, [Chip(ChipColor.BLUE, 2)])
        self.assertEqual(leftover_money, 20)


class TestExecuteBuyingPhaseIntegration(unittest.TestCase):

    def setUp(self):
        self.mock_profile = GameStrategyProfile(
            colors=(ChipColor.GREEN, ChipColor.BLUE, ChipColor.PURPLE, ChipColor.ORANGE),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.MEDIUM,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.POINTS
        )
        self.player = Player(self.mock_profile)
        self.current_round = 2

    @patch('game_engine.phase_3_evaluation.step_e_buy_chips.has_exploded')
    def test_execute_buying_phase_unexploded(self, mock_has_exploded):
        """Verifies a player who has not exploded buys items according to their color and value strategies."""
        mock_has_exploded.return_value = False
        supply_bank = SupplyBank(SHOP_CATALOG)
        self.player.current_space = 20

        self.player.unplayed_chips.clear()
        execute_buying_phase(self.player, supply_bank, self.current_round)
        self.assertIn(Chip(ChipColor.BLUE, 2), self.player.unplayed_chips)
        self.assertIn(Chip(ChipColor.GREEN, 1), self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 2)

    @patch('game_engine.phase_3_evaluation.step_e_buy_chips.has_exploded')
    @patch('game_engine.phase_3_evaluation.step_e_buy_chips.should_choose_points_on_explosion')
    def test_execute_buying_phase_exploded_chose_points(self, mock_should_choose_points_on_explosion, mock_has_exploded):
        """Verifies a player who has exploded but chosen points buys nothing."""
        mock_has_exploded.return_value = True
        mock_should_choose_points_on_explosion.return_value = True
        supply_bank = SupplyBank(SHOP_CATALOG)
        self.player.current_space = 20

        self.player.unplayed_chips.clear()
        execute_buying_phase(self.player, supply_bank, self.current_round)
        self.assertEqual(len(self.player.unplayed_chips), 0)


    @patch('game_engine.phase_3_evaluation.step_e_buy_chips.has_exploded')
    @patch('game_engine.phase_3_evaluation.step_e_buy_chips.should_choose_points_on_explosion')
    def test_execute_buying_phase_exploded_chose_money(self, mock_should_choose_points_on_explosion, mock_has_exploded):
        """Verifies a player who has exploded but money and buys items according to their buying strategies."""
        mock_has_exploded.return_value = True
        mock_should_choose_points_on_explosion.return_value = False
        supply_bank = SupplyBank(SHOP_CATALOG)
        self.player.current_space = 20

        self.player.unplayed_chips.clear()
        execute_buying_phase(self.player, supply_bank, self.current_round)
        self.assertIn(Chip(ChipColor.BLUE, 2), self.player.unplayed_chips)
        self.assertIn(Chip(ChipColor.GREEN, 1), self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 2)


    @patch('game_engine.phase_3_evaluation.step_e_buy_chips.has_exploded')
    @patch('game_engine.phase_3_evaluation.step_e_buy_chips.should_choose_points_on_explosion')
    def test_execute_buying_phase_round_9(self, mock_should_choose_points_on_explosion, mock_has_exploded):
        """Ensures no new chips are purchased during the 9th round and that victory points are purchased instead."""
        mock_has_exploded.return_value = True
        mock_should_choose_points_on_explosion.return_value = False
        supply_bank = SupplyBank(SHOP_CATALOG)
        self.player.current_space = 20
        self.player.victory_points = 0
        current_round = 9

        self.player.unplayed_chips.clear()
        execute_buying_phase(self.player, supply_bank, current_round)
        self.assertEqual(self.player.victory_points, 3)
        self.assertEqual(len(self.player.unplayed_chips), 0)

    def test_execute_buying_phase_random(self):
        """Ensures a random value strategy is selected for the random player."""
        new_strategy_profile = replace(
            self.mock_profile,
            colors=(),
            value=ValueStrat.RANDOM
        )
        self.player = Player(new_strategy_profile)

        with (
            patch('random.choice') as mock_choice, \
            patch('game_engine.phase_2_potions.has_exploded') as mock_has_exploded, \
            patch('random.sample') as mock_color_list
        ):
            mock_choice.return_value = ValueStrat.HIGHEST_SINGLE_VALUE
            mock_has_exploded.return_value = False
            mock_color_list.return_value = [ChipColor.YELLOW, ChipColor.BLACK, ChipColor.ORANGE, ChipColor.GREEN,
                                            ChipColor.BLUE, ChipColor.RED, ChipColor.PURPLE]

            self.player.unplayed_chips.clear()
            self.player.current_space = 20
            supply_bank = SupplyBank(SHOP_CATALOG)
            execute_buying_phase(self.player, supply_bank, self.current_round)

            self.assertEqual(self.player.unplayed_chips, [Chip(ChipColor.YELLOW, 2), Chip(ChipColor.ORANGE, 1)])


if __name__ == '__main__':
    unittest.main()