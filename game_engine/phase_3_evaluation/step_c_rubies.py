from config.pot_config import POT_BOARD_SPACES
from models.player import Player

def award_ruby(player: Player) -> None:
    """Awards rubies based upon the scoring space."""
    # The scoring space is the space AFTER the space your last chip was placed. However, because the scoring spaces
    # are saved in a tuple and the first index is 0, the space after your last chip has an index matching your
    # current space (which starts at 1)!
    scoring_space = POT_BOARD_SPACES[player.current_space]
    if scoring_space.ruby:
        player.ruby += 1
