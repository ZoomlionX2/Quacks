import itertools
from dataclasses import dataclass
from config.chip_config import ChipColor


@dataclass(frozen=True)
class ShopItem:
    color: ChipColor
    value: int
    price: int
    starting_quantity: int

SHOP_CATALOG: tuple[ShopItem, ...] = (
            ShopItem(ChipColor.GREEN, 1, 4, 15),
            ShopItem(ChipColor.GREEN, 2, 8, 10),
            ShopItem(ChipColor.GREEN, 4, 14, 13),
            ShopItem(ChipColor.BLUE, 1, 5, 14),
            ShopItem(ChipColor.BLUE, 2, 10, 10),
            ShopItem(ChipColor.BLUE, 4, 19, 10),
            ShopItem(ChipColor.RED, 1, 6, 12),
            ShopItem(ChipColor.RED, 2, 10, 8),
            ShopItem(ChipColor.RED, 4, 16, 10),
            ShopItem(ChipColor.YELLOW, 1, 8, 13),
            ShopItem(ChipColor.YELLOW, 2, 12, 6),
            ShopItem(ChipColor.YELLOW, 4, 18, 10),
            ShopItem(ChipColor.ORANGE, 1, 3, 20),
            ShopItem(ChipColor.PURPLE, 1, 9, 15),
            ShopItem(ChipColor.BLACK, 1, 10, 18)
)

# Just the items with a value of two for increased search speed by the least_disparity chip-buying strategy
TWO_VALUE_CHIP_BY_COLOR = {
    item.color: item for item in SHOP_CATALOG if item.value == 2
}

@dataclass(frozen=True)
class ShopItemPair:
    first_item: ShopItem
    second_item: ShopItem | None
    combined_value: int
    price: int

def generate_shop_item_pairs() -> tuple[ShopItemPair, ...]:
    """Generates a tuple of all possible combinations of 1 or 2 shop items that don't have the same color."""
    combos_list: list[ShopItemPair] = []

    # Generate all pairs of shop items
    for item_a, item_b in itertools.combinations(SHOP_CATALOG, 2):
        if item_a.color != item_b.color:
            combined_price = item_a.price + item_b.price
            combined_value = item_a.value + item_b.value
            combos_list.append(ShopItemPair(first_item=item_a,
                                            second_item=item_b,
                                            combined_value=combined_value,
                                            price=combined_price))

    # Sort from the highest price to lowest, then combined chip value
    combos_list.sort(
        key=lambda x: (x.price, x.combined_value),
        reverse=True
    )

    return tuple(combos_list)

SHOP_CATALOG_PAIRS = generate_shop_item_pairs()