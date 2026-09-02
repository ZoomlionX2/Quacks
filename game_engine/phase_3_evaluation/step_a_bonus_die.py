import random

from config.chip_config import ChipColor
from config.pot_config import FINAL_SCORING_SPACE
from config.shop_config import SHOP_CATALOG
from game_engine.phase_2_potions import has_exploded
from models.chip import Chip
from models.player import Player
from models.supply_bank import SupplyBank


def execute_bonus_die_reward(player: Player, roll: int, supply_bank: SupplyBank) -> None:
    """Gives the reward as dictated by the bonus die roll."""
    match roll:
        # 1 victory point
        case 1:
            player.victory_points += 1
            return

        # 1 droplet move
        case 2:
            player.droplet += 1
            return

        # 1 pumpkin chip
        case 3:
            orange_chip = next(shop_item for shop_item in SHOP_CATALOG if shop_item.color == ChipColor.ORANGE and
                               shop_item.value == 1)
            if supply_bank.purchase_item(orange_chip):
                player.unplayed_chips.append(Chip(ChipColor.ORANGE, 1))
            return

        # 1 ruby
        case 4:
            player.ruby += 1
            return

        # 2 victory points
        case 5:
            player.victory_points += 2
            return

        # 1 victory point
        case 6:
            player.victory_points += 1
            return

        case _:
            return


def roll_bonus_die(player_a: Player, player_b: Player, supply_bank: SupplyBank) -> None:
    """Determines who qualifies to roll the bonus die and then does so."""
    eligible_players = []
    if not has_exploded(player_a):
        eligible_players.append(player_a)
    if not has_exploded(player_b):
        eligible_players.append(player_b)

    if not eligible_players:
        return

    max_space_reached = max(player.current_space for player in eligible_players)

    if max_space_reached >= FINAL_SCORING_SPACE:
        for player in eligible_players:
            if player.current_space >= FINAL_SCORING_SPACE:
                roll = random.randint(1, 6)
                execute_bonus_die_reward(player, roll, supply_bank)

    else:
        for player in eligible_players:
            if player.current_space == max_space_reached:
                roll = random.randint(1, 6)
                execute_bonus_die_reward(player, roll, supply_bank)