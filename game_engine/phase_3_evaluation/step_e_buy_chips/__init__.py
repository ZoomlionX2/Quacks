import random

from config.chip_config import ChipColor
from config.pot_config import POT_BOARD_SPACES
from config.shop_config import ShopItem, SHOP_CATALOG
from game_engine.phase_2_potions import has_exploded
from game_engine.phase_3_evaluation import FINAL_ROUND
from game_engine.phase_3_evaluation.step_d_points import should_choose_points_on_explosion
from models.chip import Chip
from models.player import Player
from models.strategy import ValueStrat, PURCHASABLE_COLORS
from models.supply_bank import SupplyBank

MONEY_TO_VC_PRICE = 5

# Shared helper functions
def get_max_price(color: ChipColor) -> int:
    """Helper to find the highest cost of a specific color variant in the shop."""
    matching_prices = [item.price for item in SHOP_CATALOG if item.color == color]
    return max(matching_prices) if matching_prices else 0


def create_buying_priority(player: Player, use_fallback: bool) -> list[ChipColor]:
    """Returns a list of colors sorted by buying priority. Priority is determined first by fewest chips of that color."""
    color_list = []

    # Returns a random ordering of all colors for the random player (indicated by a blank color strategy)
    if not player.strategy_profile.colors:
        return random.sample(PURCHASABLE_COLORS, len(PURCHASABLE_COLORS))

    # Specify colors to return
    if use_fallback:
        colors_to_use = [color for color in ChipColor if color not in player.strategy_profile.colors
                         and color != ChipColor.WHITE]
    else:
        colors_to_use = player.strategy_profile.colors

    # Counts how many chips of each color the player has
    for color in colors_to_use:
        count = sum(1 for chip in player.unplayed_chips if chip.color == color)
        count += sum(1 for chip in player.played_chips if chip.color == color)
        color_list.append([color, count])

    # Sort by quantity and then by max price, return only the colors
    color_list.sort(key=lambda x: (x[1], -get_max_price(x[0])))

    return [row[0] for row in color_list]


def is_color_unlocked(color: ChipColor, current_round: int) -> bool:
    """Disallows the purchase of yellow or purple chips if they haven't been unlocked."""
    if color == ChipColor.YELLOW and current_round < 2:
        return False
    if color == ChipColor.PURPLE and current_round < 3:
        return False
    return True


def finalize_chip_purchase(player: Player, supply_bank: SupplyBank, item: ShopItem, money: int) -> int:
    """Updates the supply bank, player inventory, and money."""
    supply_bank.purchase_item(item)
    player.unplayed_chips.append(Chip(item.color, item.value))
    money -= item.price

    return money


def reset_bag(player: Player) -> None:
    """Returns all played chips to the bag."""
    player.unplayed_chips.extend(player.played_chips)
    player.played_chips.clear()


# Master evaluation phase entry point
def execute_buying_phase(player: Player, supply_bank: SupplyBank, current_round: int) -> None:
    """Executes the buying phase in accord with the player's exploded, color, and value strategies and available money."""
    # Determine player money available for the round
    if has_exploded(player):
        chose_points = should_choose_points_on_explosion(player, current_round)
        if chose_points:
            reset_bag(player)
            return

    money = POT_BOARD_SPACES[player.current_space].money

    # Final round - instead of buying chips, buy victory points
    if current_round == FINAL_ROUND:
        player.victory_points += (money // MONEY_TO_VC_PRICE)
        reset_bag(player)

        return

    # Local imports for purchasing chips
    from game_engine.phase_3_evaluation.step_e_buy_chips.highest_single_value import buy_highest_single_value
    from game_engine.phase_3_evaluation.step_e_buy_chips.highest_value_pair import buy_highest_value_pair
    from game_engine.phase_3_evaluation.step_e_buy_chips.least_disparity import buy_least_disparity

    # Purchase chips according to value strategy. Color strategy is evaluated within each value strategy.
    if money > 0:
        # The random player chooses a random value strategy
        if player.strategy_profile.value == ValueStrat.RANDOM:
            value_strat = random.choice([ValueStrat.HIGHEST_VALUE_PAIR, ValueStrat.HIGHEST_SINGLE_VALUE,
                                         ValueStrat.LEAST_DISPARITY])
        else:
            value_strat = player.strategy_profile.value

        match value_strat:

            case ValueStrat.HIGHEST_VALUE_PAIR:
                buy_highest_value_pair(player, supply_bank, money, current_round)

            case ValueStrat.HIGHEST_SINGLE_VALUE:
                buy_highest_single_value(player, supply_bank, money, current_round)

            case ValueStrat.LEAST_DISPARITY:
                buy_least_disparity(player, supply_bank, money, current_round)

    reset_bag(player)