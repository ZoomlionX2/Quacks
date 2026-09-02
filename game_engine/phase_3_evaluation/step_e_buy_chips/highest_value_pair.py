from config.chip_config import ChipColor
from config.shop_config import ShopItem, SHOP_CATALOG_PAIRS, SHOP_CATALOG, ShopItemPair
from game_engine.phase_3_evaluation.step_e_buy_chips import create_buying_priority, is_color_unlocked, \
    finalize_chip_purchase
from models.player import Player
from models.supply_bank import SupplyBank


def select_pair_to_purchase(color_list_a: list[ChipColor], color_list_b: list[ChipColor], supply_bank: SupplyBank,
                            budget: int, current_round: int) -> ShopItemPair | None:
    """Searches for the best pair of shop items that can be purchased that can be created from the given color list."""
    for color_a in color_list_a:
        if not is_color_unlocked(color_a, current_round):
            continue
        for color_b in color_list_b:
            # Ensure no duplicate colors
            if color_a == color_b:
                continue

            if not is_color_unlocked(color_b, current_round):
                continue

            # Search for suitable chip pairs
            for pair in SHOP_CATALOG_PAIRS:
                if (pair.price <= budget                                                          # Can we afford them?
                and ((pair.first_item.color == color_a and pair.second_item.color == color_b)     # Correct colors?
                or (pair.first_item.color == color_b and pair.second_item.color == color_a))      # Correct colors?
                and ((supply_bank[pair.first_item] > 0) and (supply_bank[pair.second_item] > 0))  # In stock?
                ):
                    return pair

    return None


def select_single_to_purchase(color_list: list[ChipColor], supply_bank: SupplyBank, budget: int, current_round: int)\
        -> ShopItem | None:
    """Searches for the best single shop item that can be purchased according to the given color list."""
    for color in color_list:
        if not is_color_unlocked(color, current_round):
            continue

        highest_price = 0
        item_to_select = None
        for item in SHOP_CATALOG:
            if (item.color == color
                and item.price <= budget
                and supply_bank[item] > 0
            ):
                if item.price > highest_price:
                    item_to_select = item

        if item_to_select is not None:
            return item_to_select

    return None


def buy_highest_value_pair(player: Player, supply_bank: SupplyBank, money: int,
                           current_round: int) -> None:
    """Buys the highest value chip followed by the second-highest value chip."""
    budget = money
    preferred_color_list = create_buying_priority(player, use_fallback=False)
    non_preferred_color_list = create_buying_priority(player, use_fallback=True)

    single = None

    # Purchase pass 1: pairs of preferred colors
    pair = select_pair_to_purchase(preferred_color_list, preferred_color_list, supply_bank, budget, current_round)

    # Purchase pass 2: pairs of one preferred color and one non-preferred
    if pair is None:
        pair = select_pair_to_purchase(preferred_color_list, non_preferred_color_list, supply_bank, budget,
                                       current_round)

    # Purchase pass 3: pairs of non-preferred colors
    if pair is None:
        pair = select_pair_to_purchase(non_preferred_color_list, non_preferred_color_list, supply_bank, budget,
                                       current_round)

    # Purchase pass 4: single from preferred colors
    if pair is None:
        single = select_single_to_purchase(preferred_color_list, supply_bank, budget, current_round)

    # Purchase pass 5: single from non-preferred colors
    if pair is None and single is None:
        single = select_single_to_purchase(non_preferred_color_list, supply_bank, budget, current_round)

    # Finalize transaction
    if pair is not None:
        money = finalize_chip_purchase(player, supply_bank, pair.first_item, money)
        finalize_chip_purchase(player, supply_bank, pair.second_item, money)
        return

    if pair is None and single is not None:
        finalize_chip_purchase(player, supply_bank, single, money)