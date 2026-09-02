import random

from config.pot_config import POT_BOARD_SPACES
from game_engine.phase_2_potions import has_exploded
from models.player import Player
from models.strategy import ExplodedStrat


def should_choose_points_on_explosion(player: Player, current_round: int) -> bool:
    """Evaluates the player's strategy profile to decide if an exploded player should choose victory points. """
    match player.strategy_profile.exploded:
        case ExplodedStrat.POINTS:
            return True

        case ExplodedStrat.MONEY:
            if current_round == 9:
                return True
            else:
                return False

        case ExplodedStrat.ROUND_BASED_EARLY:
            return current_round > 3

        case ExplodedStrat.ROUND_BASED_MID:
            return current_round > 6

        case ExplodedStrat.RANDOM:
            return random.choice([True, False])

        case _:
            return True


def award_victory_points(player: Player, current_round: int) -> None:
    """Awards victory points based on the scoring space and player eligibility."""
    # Check player eligibility
    if has_exploded(player):
        take_points = should_choose_points_on_explosion(player, current_round)
        if not take_points:
            return

    # Award victory points on scoring space
    scoring_space = POT_BOARD_SPACES[player.current_space]
    player.victory_points += scoring_space.victory_points