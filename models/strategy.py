from dataclasses import dataclass
import itertools
from enum import StrEnum
from config.chip_config import ChipColor

GREEN   = ChipColor.GREEN
BLUE    = ChipColor.BLUE
RED     = ChipColor.RED
YELLOW  = ChipColor.YELLOW
ORANGE  = ChipColor.ORANGE
PURPLE  = ChipColor.PURPLE
BLACK   = ChipColor.BLACK

# Color strategy
PURCHASABLE_COLORS = (GREEN, BLUE, RED, YELLOW, ORANGE, PURPLE, BLACK)
COLOR_STRATS = tuple(
    itertools.chain.from_iterable(itertools.combinations(PURCHASABLE_COLORS, i) for i in range(1, 8))
)

# Value strategy
class ValueStrat(StrEnum):
    HIGHEST_VALUE_PAIR = "highest value pair"       # Buy the highest value you can afford followed by second-highest value
    HIGHEST_SINGLE_VALUE = "highest single value"   # Buy the highest value you can afford even if you can't afford a second chip
    LEAST_DISPARITY = "least disparity"             # Favor two chips of medium value over one high and one low
    RANDOM = "random"                               # Pick a random value strategy out of the others

# Ruby strategy
class RubyStrat(StrEnum):
    SAVE = "save"           # Save rubies for victory points
    DROPLET = "droplet"     # Buy only droplet advances
    FLASK = "flask"         # Buy only flask refreshes
    BALANCED = "balanced"   # Alternate between flask refreshes and droplet advances
    RANDOM = "random"       # Make a random choice to buy a droplet advance, flask refresh, or to save the rubies

# Flask strategy
class FlaskStrat(StrEnum):
    # Regardless of strategy, always flask round nine since there's no benefit in saving it
    ALWAYS_THREE = "always three"   # Flask as soon as a three is pulled
    AT_RISK = "at risk"             # Always flask as soon as there is a risk of exploding
    NO_RUBY = "no ruby"             # You're on a space that won't award a ruby or don't have a spider on the previous space
    SEVENTY = "seventy"             # You might explode but have >70% of your non-white chips left
    FIFTY = "fifty"                 # You might explode but have >50% of your non-white chips left
    RANDOM = "random"               # Randomly decide whether to use the flask

# Risk strategies
class ExplosionProbabilityToleranceStrat(StrEnum):
    HIGH = "high"           # Continue even if <= 80% probability to explode
    MEDIUM = "medium"       # Continue even if <= 60% probability to explode
    LOW = "low"             # Continue even if <= 40 % probability to explode
    VERY_LOW = "very low"   # Continue even if <= 20% probability to explode
    NEVER = "never"         # Continue only if 0% probability to explode
    RANDOM = "random"       # Randomly decide whether to continue

class ExplosionRoundStrat(StrEnum):
    ALWAYS = "1-9"      # Risk exploding during all nine rounds
    EARLY = "1-3"       # Risk exploding during the first three rounds
    EARLY_MID = "1-6"   # Risk exploding during the first six rounds
    MID = "4-6"         # Risk exploding during the middle three rounds
    MID_LATE = "4-9"    # Risk exploding during the last 6 rounds
    LATE = "7-9"        # Risk exploding during the last three rounds
    RANDOM = "random"   # Randomly decide whether to risk exploding

# Exploded strategy
class ExplodedStrat(StrEnum):
    POINTS = "points"                           # Always choose victory points
    MONEY = "money"                             # Always choose money
    ROUND_BASED_EARLY = "round-based (early)"   # Choose money if the round is 3 or less
    ROUND_BASED_MID = "round-based (mid)"       # Choose money if the round is 6 or less
    RANDOM = "random"                           # Randomly choose between money or victory points

@dataclass(frozen=True)
class GameStrategyProfile:
    colors: tuple[ChipColor, ...]
    value: ValueStrat
    ruby: RubyStrat
    flask: FlaskStrat
    explosion_prob: ExplosionProbabilityToleranceStrat
    explosion_round: ExplosionRoundStrat
    exploded: ExplodedStrat
