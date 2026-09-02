import unittest

from dataclasses import replace
from config.chip_config import ChipColor
from config.shop_config import SHOP_CATALOG, ShopItem, ShopItemPair
from game_engine.phase_3_evaluation.step_e_buy_chips import finalize_chip_purchase

from game_engine.phase_3_evaluation.step_e_buy_chips.least_disparity import select_single_to_purchase, \
    select_pair_to_purchase, disparity_is_good, buy_least_disparity
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat
from models.supply_bank import SupplyBank


class TestLeastDisparity(unittest.TestCase):

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


    def test_buy_least_disparity(self):
        """Ensures the function doesn't buy a 4-chip and 1-chip if we could afford a pair of 2-chips instead."""
        supply_bank = SupplyBank(SHOP_CATALOG)

        # Purchases a pair in the preferred colors
        money = 24
        self.player.unplayed_chips.clear()
        self.player.unplayed_chips.append(Chip(ChipColor.BLACK, 1))
        buy_least_disparity(self.player, supply_bank, money, self.current_round)
        self.assertIn(Chip(ChipColor.RED, 2), self.player.unplayed_chips)
        self.assertIn(Chip(ChipColor.YELLOW, 2), self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 3)

        # Purchases a pair consisting of one preferred and one non-preferred color
        new_strategy_profile = replace(
            self.mock_profile,
            colors=(ChipColor.PURPLE, ChipColor.YELLOW)
        )
        self.player = Player(new_strategy_profile)

        money = 24
        self.player.unplayed_chips.clear()
        buy_least_disparity(self.player, supply_bank, money, self.current_round)
        self.assertIn(Chip(ChipColor.BLUE, 2), self.player.unplayed_chips)
        self.assertIn(Chip(ChipColor.YELLOW, 2), self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 2)

        # Purchases a pair consisting of non-preferred colors
        self.current_round = 1
        money = 24
        self.player.unplayed_chips.clear()
        buy_least_disparity(self.player, supply_bank, money, self.current_round)
        self.assertIn(Chip(ChipColor.BLUE, 2), self.player.unplayed_chips)
        self.assertIn(Chip(ChipColor.RED, 2), self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 2)

        # Purchases a single in the preferred color
        new_strategy_profile = replace(
            self.mock_profile,
            colors=(ChipColor.GREEN, ChipColor.YELLOW)
        )
        self.player = Player(new_strategy_profile)

        money = 6
        self.player.unplayed_chips.clear()
        buy_least_disparity(self.player, supply_bank, money, self.current_round)
        self.assertIn(Chip(ChipColor.GREEN, 1), self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 1)

        # Purchases a single in a non-preferred color
        money = 3
        self.player.unplayed_chips.clear()
        buy_least_disparity(self.player, supply_bank, money, self.current_round)
        self.assertIn(Chip(ChipColor.ORANGE, 1), self.player.unplayed_chips)
        self.assertEqual(len(self.player.unplayed_chips), 1)


    def test_select_pair_to_purchase(self):
        """Ensure the function returns a pair meeting the criteria or None if no such pair can be found."""
        supply_bank = SupplyBank(SHOP_CATALOG)
        color_list = [ChipColor.ORANGE, ChipColor.RED, ChipColor.PURPLE]
        budget = 15

        # Respects colors and budget
        pair = select_pair_to_purchase(color_list, color_list, supply_bank, budget, self.current_round)
        self.assertTrue(pair.first_item == ShopItem(ChipColor.RED, 2, 10, 8)
                        or pair.second_item == ShopItem(ChipColor.RED, 2, 10, 8))
        self.assertTrue(pair.first_item == ShopItem(ChipColor.ORANGE, 1, 3, 20)
                        or pair.second_item == ShopItem(ChipColor.ORANGE, 1, 3, 20))

        # Allows a high disparity when lower disparity is not possible
        budget = 19
        pair = select_pair_to_purchase(color_list, color_list, supply_bank, budget, self.current_round)
        self.assertTrue(pair.first_item == ShopItem(ChipColor.RED, 4, 16, 10)
                        or pair.second_item == ShopItem(ChipColor.RED, 4, 16, 10))
        self.assertTrue(pair.first_item == ShopItem(ChipColor.ORANGE, 1, 3, 20)
                        or pair.second_item == ShopItem(ChipColor.ORANGE, 1, 3, 20))

        # Does not allow a high disparity when lower disparity is possible
        color_list = [ChipColor.RED, ChipColor.GREEN]
        budget = 20
        pair = select_pair_to_purchase(color_list, color_list, supply_bank, budget, self.current_round)
        self.assertTrue(pair.first_item == ShopItem(ChipColor.RED, 2, 10, 8)
                        or pair.second_item == ShopItem(ChipColor.RED, 2, 10, 8))
        self.assertTrue(pair.first_item == ShopItem(ChipColor.GREEN, 2, 8, 10)
                        or pair.second_item == ShopItem(ChipColor.GREEN, 2, 8, 10))

        # Does not select out-of-stock items
        while supply_bank[ShopItem(ChipColor.RED, 2, 10, 8)] > 0:
            finalize_chip_purchase(self.player, supply_bank, ShopItem(ChipColor.RED, 2, 10, 8), 100)
        pair = select_pair_to_purchase(color_list, color_list, supply_bank, budget, self.current_round)
        self.assertTrue(pair.first_item == ShopItem(ChipColor.RED, 4, 16, 10)
                        or pair.second_item == ShopItem(ChipColor.RED, 4, 16, 10))
        self.assertTrue(pair.first_item == ShopItem(ChipColor.GREEN, 1, 4, 15)
                        or pair.second_item == ShopItem(ChipColor.GREEN, 1, 4, 15))


    def test_disparity_is_good(self):
        """Ensures the function correctly approves chip pairs."""
        supply_bank = SupplyBank(SHOP_CATALOG)

        # Approve non 4-1 pairs by default
        pair = ShopItemPair(first_item=ShopItem(ChipColor.RED, 4, 16, 10),
                            second_item=ShopItem(ChipColor.YELLOW, 4, 18, 10),
                            combined_value=8,
                            price=34)
        self.assertTrue(disparity_is_good(pair, supply_bank))

        # Approve colors that don't have a 2-chip
        pair = ShopItemPair(first_item=ShopItem(ChipColor.BLACK, 1, 10, 18),
                            second_item=ShopItem(ChipColor.YELLOW, 4, 18, 10),
                            combined_value=5,
                            price=28)
        self.assertTrue(disparity_is_good(pair, supply_bank))

        # Approve if either color's 2-chip is out of stock
        while supply_bank[ShopItem(ChipColor.RED, 2, 10, 8)] > 0:
            finalize_chip_purchase(self.player, supply_bank, ShopItem(ChipColor.RED, 2, 10, 8), 100)

        pair = ShopItemPair(first_item=ShopItem(ChipColor.RED, 1, 6, 12),
                            second_item=ShopItem(ChipColor.YELLOW, 4, 18, 10),
                            combined_value=5,
                            price=24)
        self.assertTrue(disparity_is_good(pair, supply_bank))

        # Disapprove if above conditions aren't met
        pair = ShopItemPair(first_item=ShopItem(ChipColor.GREEN, 1, 4, 15),
                            second_item=ShopItem(ChipColor.YELLOW, 4, 18, 10),
                            combined_value=5,
                            price=22)
        self.assertFalse(disparity_is_good(pair, supply_bank))


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


if __name__ == '__main__':
    unittest.main()