from config.tails_config import RAT_TAIL_LOCATIONS
from models.player import Player

SCORE_TRACK_LENGTH = 50

def calculate_rat_tails(player_a: Player, player_b: Player) -> None:
    """Calculates rat tails at the start of a round based on the point gap and updates the trailing player's rat
    token position."""
    # Reset both rat tokens
    player_a.rat_token = 0
    player_b.rat_token = 0

    # Prevent token moves if score is tied
    if player_a.victory_points == player_b.victory_points:
        return

    # Identify leading and trailing player
    if player_a.victory_points > player_b.victory_points:
        leader, trailer = player_a, player_b
    else:
        leader, trailer = player_b, player_a

    # Count tails between players
    tails_earned = 0
    for score in range(trailer.victory_points, leader.victory_points):
        board_space = score % SCORE_TRACK_LENGTH

        if board_space in RAT_TAIL_LOCATIONS:
            tails_earned += 1

    # Update the trailing player's rat token
    trailer.rat_token = tails_earned