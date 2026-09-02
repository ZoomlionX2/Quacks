import unittest

from dataclasses import replace
from config.chip_config import ChipColor
from config.shop_config import SHOP_CATALOG, ShopItem
from game_engine.phase_3_evaluation.step_e_buy_chips import finalize_chip_purchase

from game_engine.phase_3_evaluation.step_e_buy_chips.highest_value_pair import select_pair_to_purchase, \
    select_single_to_purchase, buy_highest_value_pair
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat
from models.supply_bank import SupplyBank


class TestHighestValuePair(unittest.TestCase):

    def setUp(self):
        """Set up clean objects."""
        # Create a dummy strategy profile
        self.mock_profile = GameStrategyProfile(
            colors=(ChipColor.BLACK, ChipColor.YELLOW, ChipColor.RED),
            value=ValueStrat.HIGHEST_VALUE_PAIR,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.AT_RISK,
            explosion_prob=ExplosionProbabilityToleranceStrat.MEDIUM,
            explosion_round=ExplosionRoundStrat.MID,
            exploded=ExplodedStrat.POINTS
        )

        # Instantiate player with that strategy profile
        self.player = Player(strategy_profile=self.mock_profile)

        # Other parameters
        self.current_round = 2


    def test_select_pair_to_purchase(self):
        """Ensures the most expensive pair of shop items that meets the qualifications is selected for purchase."""
        supply_bank = SupplyBank(SHOP_CATALOG)
        color_list = [ChipColor.BLUE, ChipColor.PURPLE, ChipColor.RED]
        budget = 15

        # Respects budget, respects colors, does not buy locked colors
        pair = select_pair_to_purchase(color_list, color_list, supply_bank, budget, self.current_round)
        self.assertTrue(pair.first_item == ShopItem(ChipColor.RED, 2, 10, 8)
                                            or pair.first_item == ShopItem(ChipColor.BLUE, 1, 5, 14))
        self.assertTrue(pair.second_item == ShopItem(ChipColor.RED, 2, 10, 8)
                                             or pair.second_item == ShopItem(ChipColor.BLUE, 1, 5, 14))
        self.assertTrue(pair.first_item.color != pair.second_item.color)

        # Does not select out-of-stock items
        while supply_bank[ShopItem(ChipColor.RED, 2, 10, 8)] > 0:
            finalize_chip_purchase(self.player, supply_bank, ShopItem(ChipColor.RED, 2, 10, 8), 100)

        pair = select_pair_to_purchase(color_list, color_list, supply_bank, budget, self.current_round)
        self.assertTrue(pair.first_item == ShopItem(ChipColor.RED, 1, 6, 12)
                                            or pair.first_item == ShopItem(ChipColor.BLUE, 1, 5, 14))
        self.assertTrue(pair.second_item == ShopItem(ChipColor.RED, 1, 6, 12)
                                             or pair.second_item == ShopItem(ChipColor.BLUE, 1, 5, 14))

        # Returns none if no suitable pair found
        budget = 3
        pair = select_pair_to_purchase(color_list, color_list, supply_bank, budget, self.current_round)
        self.assertEqual(pair, None)


    def test_select_single_to_purchase(self):
        """Ensure function returns the best single shop item that can be purchased that meets the qualifications."""
        supply_bank = SupplyBank(SHOP_CATALOG)
        color_list = [ChipColor.PURPLE, ChipColor.RED]
        budget = 11

        # Respects budget, respects colors, buys highest priced item
        single = select_single_to_purchase(color_list, supply_bank, budget, self.current_round)
        self.assertEqual(single, ShopItem(ChipColor.RED, 2, 10, 8))

        # Does not select locked colors
        color_list = [ChipColor.PURPLE]
        single = select_single_to_purchase(color_list, supply_bank, budget, self.current_round)
        self.assertEqual(single, None)


    def test_highest_value_pair(self):
        """Verifies that the highest value chip is purchased followed by a second chip."""
        supply_bank = SupplyBank(SHOP_CATALOG)
        budget = 34

        # Purchases a pair in the preferred colors
        self.player.unplayed_chips = [Chip(ChipColor.BLACK, 1)]
        buy_highest_value_pair(self.player, supply_bank, budget, self.current_round)
        self.assertTrue(self.player.unplayed_chips == [Chip(ChipColor.BLACK, 1), Chip(ChipColor.YELLOW, 4),
                                                      Chip(ChipColor.RED, 4)]
                        or self.player.unplayed_chips == [Chip(ChipColor.BLACK, 1), Chip(ChipColor.RED, 4),
                                                      Chip(ChipColor.YELLOW, 4)])

        # Purchases a pair with one preferred color and one non-preferred color
        new_strategy_profile = replace(
            self.mock_profile,
            colors=(ChipColor.PURPLE, ChipColor.YELLOW)
        )
        self.player.strategy_profile = new_strategy_profile

        budget = 26
        self.player.unplayed_chips.clear()
        buy_highest_value_pair(self.player, supply_bank, budget, self.current_round)
        self.assertTrue(Chip(ChipColor.YELLOW, 4) in self.player.unplayed_chips)
        self.assertTrue(Chip(ChipColor.BLUE, 1) in self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 2)

        # Purchases a pair with two non-preferred colors
        new_strategy_profile = replace(
            self.mock_profile,
            colors=(ChipColor.PURPLE, ChipColor.YELLOW)
        )
        self.player.strategy_profile = new_strategy_profile

        budget = 7
        self.player.unplayed_chips.clear()
        buy_highest_value_pair(self.player, supply_bank, budget, self.current_round)
        self.assertTrue(Chip(ChipColor.GREEN, 1) in self.player.unplayed_chips)
        self.assertTrue(Chip(ChipColor.ORANGE, 1) in self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 2)

        # Purchases a single with non-preferred color
        budget = 4
        self.player.unplayed_chips.clear()
        buy_highest_value_pair(self.player, supply_bank, budget, self.current_round)
        self.assertTrue(Chip(ChipColor.GREEN, 1) in self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 1)


if __name__ == '__main__':
    unittest.main()