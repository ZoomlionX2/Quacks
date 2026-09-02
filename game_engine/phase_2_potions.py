import random

from config.chip_config import ChipColor
from config.pot_config import FINAL_SCORING_SPACE
from models.chip import Chip
from models.player import Player
from models.strategy import ExplosionProbabilityToleranceStrat, ExplosionRoundStrat, FlaskStrat

EXPLOSION_THRESHOLD = 7


def calc_nonwhite_chip_percentage(player: Player) -> float:
    """ Calculate the percentage of non-white chips in your bag relative to the total quantity of non-white chips you
    own."""
    played_nonwhite_chip_count = sum(1 for chip in player.played_chips if chip.color != ChipColor.WHITE)
    unplayed_nonwhite_chip_count = sum(1 for chip in player.unplayed_chips if chip.color != ChipColor.WHITE)
    total_nonwhite_chip_count = played_nonwhite_chip_count + unplayed_nonwhite_chip_count

    if total_nonwhite_chip_count == 0:
        return 0.0

    return unplayed_nonwhite_chip_count / total_nonwhite_chip_count


def calculate_explosion_probability(player: Player) -> float:
    """Calculates the probability that the next drawn chip will explode the pot."""
    # Guard against division by zero if the bag is empty
    if not player.unplayed_chips:
        return 0.0

    # Calculate safety margin based on current pot composition
    current_white_total = sum(chip.value for chip in player.played_chips if chip.color == ChipColor.WHITE)
    allowed_white_margin = EXPLOSION_THRESHOLD - current_white_total

    # Count how many remaining white chips would exceed safety margin
    explodable_chip_count = 0
    for chip in player.unplayed_chips:
        if chip.color == ChipColor.WHITE and chip.value > allowed_white_margin:
            explodable_chip_count += 1

    return explodable_chip_count / len(player.unplayed_chips)


def should_flask(player: Player, drawn_chip: Chip, current_round: int) -> bool:
    """Check if flask should be used based on flask strategy."""
    if current_round == 9:
        return True

    match player.strategy_profile.flask:
        case FlaskStrat.ALWAYS_THREE:
            return drawn_chip.value == 3

        case FlaskStrat.AT_RISK:
            return calculate_explosion_probability(player) > 0

        case FlaskStrat.NO_RUBY:
            from game_engine.phase_3_evaluation.step_c_rubies import award_ruby
            return not award_ruby(player)

        case FlaskStrat.SEVENTY:
            return calc_nonwhite_chip_percentage(player) > 0.7 and calculate_explosion_probability(player) > 0

        case FlaskStrat.FIFTY:
            return calc_nonwhite_chip_percentage(player) > 0.5 and calculate_explosion_probability(player) > 0

        case FlaskStrat.RANDOM:
            return random.choice([True, False])

        case _:
            return False


def use_flask(player: Player, drawn_chip: Chip) -> None:
    """Return the last drawn white chip to the bag and update flask state."""
    player.played_chips.pop()
    player.unplayed_chips.append(drawn_chip)
    player.flask_full = False


def calculate_red_chip_boost(player) -> int:
    """Calculates the movement bonus for red chips based on placed orange chips."""
    num_orange = sum(1 for chip in player.played_chips if chip.color == ChipColor.ORANGE)

    if num_orange >= 3:
        return 2
    if num_orange >= 1:
        return 1

    return 0


def update_current_space(player: Player, chip: Chip, is_first_draw: bool) -> None:
    """Updates the player's current space based on the drawn chip."""
    movement_spaces = chip.value
    if chip.color == ChipColor.RED:
        movement_spaces += calculate_red_chip_boost(player)

    if is_first_draw:
        player.current_space = player.rat_token + player.droplet + movement_spaces
    else:
        player.current_space += movement_spaces

    # Ensures the current space can not go beyond the final scoring space
    if player.current_space > FINAL_SCORING_SPACE:
        player.current_space = FINAL_SCORING_SPACE


def check_probability_tolerance(strat: ExplosionProbabilityToleranceStrat, explosion_prob: float) -> bool:
    """Checks the player's strategy profile to determine if drawing a chip aligns with the explosion probability
    tolerance."""
    match strat:
        case ExplosionProbabilityToleranceStrat.HIGH:
            return explosion_prob <= 0.8

        case ExplosionProbabilityToleranceStrat.MEDIUM:
            return explosion_prob <= 0.6

        case ExplosionProbabilityToleranceStrat.LOW:
            return explosion_prob <= 0.4

        case ExplosionProbabilityToleranceStrat.VERY_LOW:
            return explosion_prob <= 0.2

        case ExplosionProbabilityToleranceStrat.NEVER:
            return explosion_prob <= 0.0

        case ExplosionProbabilityToleranceStrat.RANDOM:
            return random.choice([True, False])

        case _:
            return False


def check_round_context(strat: ExplosionRoundStrat, current_round: int) -> bool:
    """Checks the player's strategy profile to determine if drawing a chip aligns with the explosion round strategy."""
    match strat:
        case ExplosionRoundStrat.ALWAYS:
            return True

        case ExplosionRoundStrat.EARLY:
            return current_round <= 3

        case ExplosionRoundStrat.EARLY_MID:
            return current_round <= 6

        case ExplosionRoundStrat.MID:
            return 4 <= current_round <= 6

        case ExplosionRoundStrat.MID_LATE:
            return 4 <= current_round <= 9

        case ExplosionRoundStrat.LATE:
            return 7 <= current_round <= 9

        case ExplosionRoundStrat.RANDOM:
            return True # The round should not influence the random player's decision

        case _:
            return False


def should_draw(player: Player, current_round: int) -> bool:
    """Determines if a player should draw a chip based on their explosion probability tolerance and their round
    strategy."""
    if not player.unplayed_chips or player.current_space >= FINAL_SCORING_SPACE:
        return False

    probability = calculate_explosion_probability(player)
    if probability == 0.0:
        return True

    # If there is a chance of exploding, consult the risk tolerance strategies
    probability_tolerance = check_probability_tolerance(player.strategy_profile.explosion_prob, probability)
    round_tolerance = check_round_context(player.strategy_profile.explosion_round, current_round)

    return probability_tolerance and round_tolerance


def draw_chip(player: Player) -> Chip:
    """Draws a random chip from the player's bag."""
    idx = random.randrange(len(player.unplayed_chips))
    player.unplayed_chips[idx], player.unplayed_chips[-1] = player.unplayed_chips[-1], player.unplayed_chips[idx]
    drawn_chip = player.unplayed_chips.pop()
    player.played_chips.append(drawn_chip)

    return drawn_chip


def execute_yellow_special_action(player: Player) -> None:
    """Executes special action of yellow chip: if previous chip was white, return it to bag."""
    if len(player.played_chips) >= 2:
        if player.played_chips[-2].color == ChipColor.WHITE:
            chip_to_return = player.played_chips.pop(-2)
            player.unplayed_chips.append(chip_to_return)

    return


def select_chip(player: Player, drawn_chips: list[Chip]) -> Chip | None:
    """Helper function to execute_immediate_chip_action. Selects a chip to play from the pool created by a blue chip's
    special action. YELLOW-2 and YELLOW-1 are not considered suitable chips to play as their special ability would be
    wasted. However, the high advancement value of YELLOW-4 is considered adequate compensation making it suitable."""

    target_chip = Chip(ChipColor.BLUE, 4)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.RED, 4)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    sum_orange = sum(1 for _ in player.played_chips if _.color == ChipColor.ORANGE)
    if sum_orange > 0:
        target_chip = Chip(ChipColor.RED, 2)
        if target_chip in drawn_chips:
            drawn_chips.remove(target_chip)
            return target_chip

    if sum_orange > 2:
        target_chip = Chip(ChipColor.RED, 1)
        if target_chip in drawn_chips:
            drawn_chips.remove(target_chip)
            return target_chip

    target_chip = Chip(ChipColor.GREEN, 4)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.YELLOW, 4)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.BLUE, 2)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.BLUE, 1)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.BLACK, 1)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.ORANGE, 1)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.RED, 2)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.RED, 1)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.GREEN, 2)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.GREEN, 1)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    target_chip = Chip(ChipColor.PURPLE, 1)
    if target_chip in drawn_chips:
        drawn_chips.remove(target_chip)
        return target_chip

    return None


def execute_blue_special_action(player: Player, chip: Chip) -> None:
    """Execute special action of blue chip: draw qty of chips equal to value of the blue; you may play one of
    these chips and return the rest to the bag.
    """
    # Draw as many random chips as the value of the blue chip
    drawn_chips: list[Chip] = []
    for _ in range(chip.value):
        if len(player.unplayed_chips) > 0:
            idx = random.randrange(len(player.unplayed_chips))
            player.unplayed_chips[idx], player.unplayed_chips[-1] = player.unplayed_chips[-1], player.unplayed_chips[
                idx]
            drawn_chips.append(player.unplayed_chips.pop())

    # Select chip to play
    selected_chip = select_chip(player, drawn_chips)

    # Return remaining chips to bag
    for unchosen_chip in drawn_chips:
        player.unplayed_chips.append(unchosen_chip)

    if selected_chip is not None:
        # Place chip
        player.played_chips.append(selected_chip)
        update_current_space(player, selected_chip, False)

        if selected_chip.color == ChipColor.BLUE:
            execute_blue_special_action(player, selected_chip)


def has_exploded(player: Player) -> bool:
    """Determines if a player's pot has exploded due to excessive white chips."""
    return sum(chip.value for chip in player.played_chips if chip.color == ChipColor.WHITE) > EXPLOSION_THRESHOLD


def run_potions_phase(player: Player, current_round: int) -> None:
    """Main drawing loop that consults player's strategy profile."""
    is_first_draw = True

    while should_draw(player, current_round):
        # Draw chip
        drawn_chip = draw_chip(player)
        player_exploded = False

        # Actions for white chips only
        if drawn_chip.color == ChipColor.WHITE:
            player_exploded = has_exploded(player)

            # Use flask if appropriate
            if not player_exploded and player.flask_full and should_flask(player, drawn_chip, current_round):
                use_flask(player, drawn_chip)
                continue

        # Place chip
        update_current_space(player, drawn_chip, is_first_draw)
        is_first_draw = False

        # Apply special effects of yellow and blue chips
        if drawn_chip.color == ChipColor.YELLOW:
            execute_yellow_special_action(player)

        if drawn_chip.color == ChipColor.BLUE:
            execute_blue_special_action(player, drawn_chip)

        if player_exploded:
            player.explosion_count += 1
            break