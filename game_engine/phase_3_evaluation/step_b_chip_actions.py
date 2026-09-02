from config.chip_config import ChipColor
from models.player import Player


def execute_black_special_action(player_a: Player, player_b: Player) -> None:
    """Grants rewards based on number of black chips in pot relative to other player."""
    num_black_a = sum(1 for chip in player_a.played_chips if chip.color == ChipColor.BLACK)
    num_black_b = sum(1 for chip in player_b.played_chips if chip.color == ChipColor.BLACK)

    # Prevent a tie of 0 from granting a reward
    if num_black_a == num_black_b and num_black_a == 0:
        return

    if num_black_a == num_black_b:
        player_a.droplet += 1
        player_b.droplet += 1

        return

    if num_black_a > num_black_b:
        player_a.droplet += 1
        player_a.ruby += 1

    else:
        player_b.droplet += 1
        player_b.ruby += 1


def execute_green_special_action(player: Player) -> None:
    """Grants a ruby if a green chip is on last or second-to-last space (or both)."""
    if player.played_chips[-1].color == ChipColor.GREEN:
        player.ruby += 1

    if len(player.played_chips) >= 2:
        if player.played_chips[-2].color == ChipColor.GREEN:
            player.ruby += 1


def execute_purple_special_action(player: Player) -> None:
    """Grants rewards based on number of purple chips in pot."""
    num_purple_chips = sum(1 for chip in player.played_chips if chip.color == ChipColor.PURPLE)

    if num_purple_chips < 1:
        return

    if num_purple_chips == 1:
        player.victory_points += 1
        return

    if num_purple_chips == 2:
        player.victory_points += 1
        player.ruby += 1
        return

    if num_purple_chips >= 3:
        player.victory_points += 2
        player.droplet += 1


def execute_chip_actions(player_a: Player, player_b: Player):
    """Runs the chip actions phase."""
    execute_black_special_action(player_a, player_b)
    execute_green_special_action(player_a)
    execute_green_special_action(player_b)
    execute_purple_special_action(player_a)
    execute_purple_special_action(player_b)