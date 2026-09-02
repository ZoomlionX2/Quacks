from config.chip_config import ChipColor
from config.shop_config import ShopItem, ShopItemPair, SHOP_CATALOG_PAIRS, SHOP_CATALOG, TWO_VALUE_CHIP_BY_COLOR
from game_engine.phase_3_evaluation.step_e_buy_chips import is_color_unlocked, create_buying_priority, \
    finalize_chip_purchase
from models.player import Player
from models.supply_bank import SupplyBank


DISPARITY_VALUE_FLAG = 5 # When possible, we wish to avoid a pair consisting of a 4-chip and a 1-chip (combined value = 5)


def disparity_is_good(pair: ShopItemPair, supply_bank: SupplyBank) -> bool:
    """Verifies if the disparity between the chip values is acceptable."""
    # Approve any disparity other than the largest one (4-chip and 1-chip)
    if pair.combined_value != DISPARITY_VALUE_FLAG:
        return True

    # Approve colors that don't have a 2-chip
    if pair.first_item.color in [ChipColor.ORANGE, ChipColor.BLACK, ChipColor.PURPLE]:
        return True
    if pair.second_item.color in [ChipColor.ORANGE, ChipColor.BLACK, ChipColor.PURPLE]:
        return True

    # Approve if either of the two-chips is out-of-stock
    two_chip_a = TWO_VALUE_CHIP_BY_COLOR.get(pair.first_item.color)
    two_chip_b = TWO_VALUE_CHIP_BY_COLOR.get(pair.second_item.color)

    if two_chip_a is not None and supply_bank[two_chip_a] == 0:
        return True

    if two_chip_b is not None and supply_bank[two_chip_b] == 0:
        return True

    return False


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

            for pair in SHOP_CATALOG_PAIRS:
                # Can we afford the pair?
                if not pair.price <= budget:
                    continue

                # Are the colors correct?
                if not ((pair.first_item.color == color_a and pair.second_item.color == color_b)
                or (pair.first_item.color == color_b and pair.second_item.color == color_a)
                ):
                    continue

                # Is the disparity acceptable?
                if not disparity_is_good(pair, supply_bank):
                        continue

                # Are the items in stock?
                if not ((supply_bank[pair.first_item] > 0) and (supply_bank[pair.second_item] > 0)):
                    continue

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


def buy_least_disparity(player: Player, supply_bank: SupplyBank, money: int,
                        current_round: int) -> None:
    """Avoids buying a 4-chip and 1-chip if the 1-chip has a higher-value variant that can be afforded by downgrading
    the 4-chip."""
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