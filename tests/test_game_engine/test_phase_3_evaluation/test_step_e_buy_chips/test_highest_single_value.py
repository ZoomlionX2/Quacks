import unittest

from dataclasses import replace
from config.chip_config import ChipColor
from config.shop_config import SHOP_CATALOG, ShopItem
from game_engine.phase_3_evaluation.step_e_buy_chips import finalize_chip_purchase
from game_engine.phase_3_evaluation.step_e_buy_chips.highest_single_value import select_item_to_purchase, \
    buy_highest_single_value
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat
from models.supply_bank import SupplyBank


class TestHighestSingleValue(unittest.TestCase):

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
        self.color_list = [ChipColor.BLACK, ChipColor.YELLOW, ChipColor.RED]
        self.shop = SHOP_CATALOG
        self.supply_bank = SupplyBank(self.shop)
        self.budget = 15
        self.current_round = 3
        self.first_selection_color = None


    def test_select_item_to_purchase(self):
        """Ensures that the highest priority color possible with the highest price is selected and that duplicate colors
        are not selected."""
        # First chip to purchase
        item_to_purchase = select_item_to_purchase(self.color_list, self.shop, self.supply_bank, self.budget,
                                                   self.current_round, self.first_selection_color)
        self.assertEqual(item_to_purchase, ShopItem(ChipColor.BLACK, 1, 10, 18))

        # Does not select a second black chip
        item_to_purchase = select_item_to_purchase(self.color_list, self.shop, self.supply_bank, self.budget,
                                                   self.current_round, ChipColor.BLACK)
        self.assertEqual(item_to_purchase, ShopItem(ChipColor.YELLOW, 2, 12, 6))

        # Respects budget
        self.budget = 7
        item_to_purchase = select_item_to_purchase(self.color_list, self.shop, self.supply_bank, self.budget,
                                                   self.current_round, ChipColor.BLACK)
        self.assertEqual(item_to_purchase, ShopItem(ChipColor.RED, 1, 6, 12))

        # Does not select locked chips
        self.current_round = 1
        self.budget = 13
        item_to_purchase = select_item_to_purchase(self.color_list, self.shop, self.supply_bank, self.budget,
                                                   self.current_round, ChipColor.BLACK)
        self.assertEqual(item_to_purchase, ShopItem(ChipColor.RED, 2, 10, 8))

        # Does not select out-of-stock chips
        while self.supply_bank[ShopItem(ChipColor.RED, 1, 6, 12)] > 0:
            finalize_chip_purchase(self.player, self.supply_bank, ShopItem(ChipColor.RED, 1, 6, 12), 100)

        while self.supply_bank[ShopItem(ChipColor.RED, 2, 10, 8)] > 0:
            finalize_chip_purchase(self.player, self.supply_bank, ShopItem(ChipColor.RED, 2, 10, 8), 100)

        while self.supply_bank[ShopItem(ChipColor.RED, 4, 16, 10)] > 0:
            finalize_chip_purchase(self.player, self.supply_bank, ShopItem(ChipColor.RED, 4, 16, 10), 100)

        item_to_purchase = select_item_to_purchase(self.color_list, self.shop, self.supply_bank, self.budget,
                                                   self.current_round, ChipColor.BLACK)
        self.assertEqual(item_to_purchase, None)


    def test_buy_highest_value_chip(self):
        """Ensures the highest value chip possible is purchased even if a second chip cannot be purchased."""
        self.player.unplayed_chips.clear()

        # Buys one expensive chip only
        self.budget = 15
        self.player.unplayed_chips = [Chip(ChipColor.YELLOW, 1), Chip(ChipColor.RED, 2)]
        buy_highest_single_value(self.player, self.supply_bank, self.budget, self.current_round)

        expected_bag = [Chip(ChipColor.YELLOW, 1), Chip(ChipColor.RED, 2), Chip(ChipColor.BLACK, 1)]
        self.assertEqual(self.player.unplayed_chips, expected_bag)

        # Buy one expensive chip and then a second chip with leftover money
        self.player.unplayed_chips.clear()
        self.budget = 16
        self.player.unplayed_chips = [Chip(ChipColor.YELLOW, 1), Chip(ChipColor.RED, 2)]
        buy_highest_single_value(self.player, self.supply_bank, self.budget, self.current_round)

        expected_bag = [Chip(ChipColor.YELLOW, 1), Chip(ChipColor.RED, 2), Chip(ChipColor.BLACK, 1),
                        Chip(ChipColor.RED, 1)]
        self.assertEqual(self.player.unplayed_chips, expected_bag)

        # Unable to buy chip in preferred color -> buy a non-preferred
        self.player.unplayed_chips.clear()
        self.budget = 5
        self.player.unplayed_chips = [Chip(ChipColor.YELLOW, 1), Chip(ChipColor.RED, 2)]
        buy_highest_single_value(self.player, self.supply_bank, self.budget, self.current_round)

        expected_bag = [Chip(ChipColor.YELLOW, 1), Chip(ChipColor.RED, 2), Chip(ChipColor.BLUE, 1)]
        self.assertEqual(self.player.unplayed_chips, expected_bag)

        # Unable to buy chip in preferred color -> buy two non-preferred
        new_strategy_profile = replace(
            self.mock_profile,
            colors=(ChipColor.PURPLE, ChipColor.YELLOW)
        )

        self.player.strategy_profile = new_strategy_profile

        self.current_round = 1
        self.player.unplayed_chips.clear()
        self.budget = 13
        self.player.unplayed_chips = [Chip(ChipColor.ORANGE, 1), Chip(ChipColor.BLUE, 1)]
        buy_highest_single_value(self.player, self.supply_bank, self.budget, self.current_round)

        expected_bag = [Chip(ChipColor.ORANGE, 1), Chip(ChipColor.BLUE, 1), Chip(ChipColor.RED, 2),
                        Chip(ChipColor.ORANGE, 1)]
        self.assertEqual(self.player.unplayed_chips, expected_bag)


if __name__ == '__main__':
    unittest.main()