from models.strategy import GameStrategyProfile
from config.chip_config import ChipColor
from models.chip import Chip


class Player:
    def __init__(self, strategy_profile: GameStrategyProfile) -> None:
        # Permanent tracking stats
        self.victory_points: int = 0
        self.droplet: int = 1 # Current position of starting token
        self.ruby: int = 1
        self.explosion_count: int = 0
        self.farthest_space_reached: int = 0 # Counted starting at 1

        # Strategy assignment
        self.strategy_profile: GameStrategyProfile = strategy_profile

        # Dynamic mid-round containers
        self.unplayed_chips: list[Chip] = []    # The chips in the bag
        self.played_chips: list[Chip] = []     # The chips in the pot

        # Changing mid-round variables
        self.flask_full: bool = True
        self.current_space: int = 0 # Counted starting at 1

        # Round state flags
        self.rat_token: int = 0


    def setup_starting_bag(self):
        self.unplayed_chips.clear()

        starting_composition = [
            (ChipColor.WHITE, 1, 4), # (color, value, quantity)
            (ChipColor.WHITE, 2, 2),
            (ChipColor.WHITE, 3, 1),
            (ChipColor.GREEN, 1, 1),
            (ChipColor.ORANGE, 1, 1),
        ]

        for color, value, quantity in starting_composition:
            for _ in range(quantity):
                self.unplayed_chips.append(Chip(color=color, value=value))



