import unittest
from config.shop_config import SHOP_CATALOG, SHOP_CATALOG_PAIRS
from config.chip_config import ChipColor

class TestShopConfig(unittest.TestCase):

    def setUp(self):
        self.shop = SHOP_CATALOG
        self.pairs = SHOP_CATALOG_PAIRS


    def test_shop_catalog_length(self):
        """Verify the shop catalog loads all 15 starting ingredient entries."""
        self.assertEqual(len(self.shop), 15)


    def test_specific_item_pricing(self):
        """Sanity check that a green 1 costs exactly 4 money."""
        green_1 = next(item for item in SHOP_CATALOG if item.color == ChipColor.GREEN and item.value == 1)
        self.assertEqual(green_1.price, 4)


    def test_shop_catalog_pair_length(self):
        """Confirm that catalog of shop item pairs contains exactly 93 pairs."""
        # The combinations formula n!/(r!(n-r)! where n=12 and r=2 yields 105 pairs. You must then subtract the instances
        # of duplicate colors since 4 colors have 3 variants, which would be combined by the formula. 3 choose 2 yields
        # 3 combinations each for a total of 12 that must be subtracted.
        self.assertEqual(len(self.pairs), 93)


if __name__ == '__main__':
    unittest.main()