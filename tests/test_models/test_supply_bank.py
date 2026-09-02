import unittest
from config.chip_config import ChipColor
from config.shop_config import ShopItem
from models.supply_bank import SupplyBank

class TestSupplyBank(unittest.TestCase):

    def setUp(self):
        self.green_item = ShopItem(ChipColor.GREEN, 1, price=4, starting_quantity=15)
        self.blue_item = ShopItem(ChipColor.BLUE, 2, price=10, starting_quantity=2)

        self.mock_catalog = (self.green_item, self.blue_item)
        self.bank = SupplyBank(self.mock_catalog)

    def test_bracket_notation_lookup(self):
        """Verify that bracket syntax correctly reads the configured starting stock."""
        self.assertEqual(self.bank[self.green_item], 15)
        self.assertEqual(self.bank[self.blue_item], 2)

    def test_successful_purchase_decrements_stock(self):
        """Verify a valid purchase drops stock by 1 and returns True."""
        purchase_success = self.bank.purchase_item(self.green_item)

        self.assertTrue(purchase_success)
        self.assertEqual(self.bank[self.green_item], 14)

    def test_out_of_stock_fails_safely(self):
        """Verify purchasing an empty item returns False and stops decrementing at 0."""
        # Buy both available blue chips to empty the stock
        self.bank.purchase_item(self.blue_item)
        self.bank.purchase_item(self.blue_item)
        self.assertEqual(self.bank[self.blue_item], 0)

        # Try to buy a third blue chip
        third_purchase = self.bank.purchase_item(self.blue_item)

        self.assertFalse(third_purchase)
        self.assertEqual(self.bank[self.blue_item], 0)

if __name__ == '__main__':
    unittest.main()