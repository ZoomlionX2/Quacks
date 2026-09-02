from config.chip_config import ChipColor
from config.shop_config import ShopItem, SHOP_CATALOG
from game_engine.phase_3_evaluation.step_e_buy_chips import create_buying_priority, finalize_chip_purchase, \
    is_color_unlocked
from models.player import Player
from models.supply_bank import SupplyBank


def select_item_to_purchase(color_list: list[ChipColor], shop_catalog: tuple[ShopItem, ...], supply_bank: SupplyBank,
                            budget: int, current_round: int, first_selection_color: ChipColor | None) -> ShopItem | None:
    """Scans prioritized colors to find the highest-cost affordable variant available."""

    # Prevent buying two chips of the same color
    active_colors = list(color_list)
    if first_selection_color in active_colors:
        active_colors.remove(first_selection_color)

    item_to_purchase = None

    # Search shop catalog for items to purchase according to the specified colors
    for color_to_purchase in active_colors:
        if not is_color_unlocked(color_to_purchase, current_round):
            continue
        highest_price = 0
        for item in shop_catalog:
            if (item.color == color_to_purchase                         # Is the item the right color?
                and highest_price < item.price <= budget                # Can we afford it?
                and supply_bank[item] > 0                               # Is it in stock?
            ):
                # Guarantees the highest priced item is selected regardless of the order of the shop catalog items
                if item.price > highest_price:
                    highest_price = item.price
                    item_to_purchase = item

        # Don't search other colors if something suitable was found
        if item_to_purchase is not None:
            return item_to_purchase

    return None


def buy_highest_single_value(player: Player, supply_bank: SupplyBank, money: int,
                             current_round: int) -> None:
    """Buys the highest value chip even if it means not purchasing a second chip."""
    budget = money
    color_list = create_buying_priority(player, use_fallback=False)

    first_item_to_purchase = select_item_to_purchase(color_list, SHOP_CATALOG, supply_bank, budget, current_round,
                                                     first_selection_color=None)
    second_item_to_purchase: ShopItem | None = None

    # Fall-back if no shop item could be selected as determined by color strategy
    if first_item_to_purchase is None:
        color_list = create_buying_priority(player, use_fallback=True)
        first_item_to_purchase = select_item_to_purchase(color_list, SHOP_CATALOG, supply_bank, budget, current_round,
                                                         first_selection_color=None)

    # Attempt to select a second shop item
    if first_item_to_purchase is not None:
        budget -= first_item_to_purchase.price
        second_item_to_purchase = select_item_to_purchase(color_list, SHOP_CATALOG, supply_bank, budget, current_round,
                                                          first_selection_color=first_item_to_purchase.color)

    # Purchase the items
    if first_item_to_purchase is not None:
        money = finalize_chip_purchase(player, supply_bank, first_item_to_purchase, money)

    if second_item_to_purchase is not None:
        finalize_chip_purchase(player, supply_bank, second_item_to_purchase, money)
