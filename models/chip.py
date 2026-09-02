from dataclasses import dataclass
from config.chip_config import ChipColor

@dataclass(frozen=True)
class Chip:
    # An ingredient that can be played
    color: ChipColor
    value: int
