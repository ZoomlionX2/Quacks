from config.chip_config import ChipColor
from config.shop_config import SHOP_CATALOG
from game_engine import play_single_round
from models.chip import Chip
from models.player import Player
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat, COLOR_STRATS
from models.supply_bank import SupplyBank

TOTAL_ROUND_COUNT = 9
ADD_WHITE_ROUND = 6 # All players receive an extra white-1 chip this round


def generate_results(player_a: Player, player_b: Player) -> dict:
    """Generates a dictionary of the results of the match formatted to be suitable for machine learning."""
    color_strat_id = None
    if player_a.strategy_profile.colors in COLOR_STRATS:
        color_strat_id = COLOR_STRATS.index(player_a.strategy_profile.colors) + 1
    else:
        color_strat_id = 0 # Indicates no color strategy / random

    results = {
        # Color strategy
        "color_strat_all": color_strat_id,
        "color_strat_green": int(ChipColor.GREEN in player_a.strategy_profile.colors),
        "color_strat_blue": int(ChipColor.BLUE in player_a.strategy_profile.colors),
        "color_strat_red": int(ChipColor.RED in player_a.strategy_profile.colors),
        "color_strat_yellow": int(ChipColor.YELLOW in player_a.strategy_profile.colors),
        "color_strat_orange": int(ChipColor.ORANGE in player_a.strategy_profile.colors),
        "color_strat_purple": int(ChipColor.PURPLE in player_a.strategy_profile.colors),
        "color_strat_black": int(ChipColor.BLACK in player_a.strategy_profile.colors),

        # Value strategy
        "value_strat_pair": int(player_a.strategy_profile.value == ValueStrat.HIGHEST_VALUE_PAIR),
        "value_strat_single": int(player_a.strategy_profile.value == ValueStrat.HIGHEST_SINGLE_VALUE),
        "value_strat_disparity": int(player_a.strategy_profile.value == ValueStrat.LEAST_DISPARITY),

        # Ruby strategy
        "ruby_strat_save": int(player_a.strategy_profile.ruby == RubyStrat.SAVE),
        "ruby_strat_droplet": int(player_a.strategy_profile.ruby == RubyStrat.DROPLET),
        "ruby_strat_flask": int(player_a.strategy_profile.ruby == RubyStrat.FLASK),
        "ruby_strat_balanced": int(player_a.strategy_profile.ruby == RubyStrat.BALANCED),

        # Flask strategy
        "flask_strat_three": int(player_a.strategy_profile.flask == FlaskStrat.ALWAYS_THREE),
        "flask_strat_risk": int(player_a.strategy_profile.flask == FlaskStrat.AT_RISK),
        "flask_strat_ruby": int(player_a.strategy_profile.flask == FlaskStrat.NO_RUBY),
        "flask_strat_seventy": int(player_a.strategy_profile.flask == FlaskStrat.SEVENTY),
        "flask_strat_fifty": int(player_a.strategy_profile.flask == FlaskStrat.FIFTY),

        # Explosion risk tolerance probability-based strategy
        "ex_prob_strat_high": int(player_a.strategy_profile.explosion_prob == ExplosionProbabilityToleranceStrat.HIGH),
        "ex_prob_strat_medium": int(player_a.strategy_profile.explosion_prob == ExplosionProbabilityToleranceStrat.MEDIUM),
        "ex_prob_strat_low": int(player_a.strategy_profile.explosion_prob == ExplosionProbabilityToleranceStrat.LOW),
        "ex_prob_strat_very_low": int(player_a.strategy_profile.explosion_prob == ExplosionProbabilityToleranceStrat.VERY_LOW),
        "ex_prob_strat_never": int(player_a.strategy_profile.explosion_prob == ExplosionProbabilityToleranceStrat.NEVER),

        # Explosion risk tolerance round-based strategy
        "ex_round_strat_always": int(player_a.strategy_profile.explosion_round == ExplosionRoundStrat.ALWAYS),
        "ex_round_strat_early": int(player_a.strategy_profile.explosion_round == ExplosionRoundStrat.EARLY),
        "ex_round_strat_early_mid": int(player_a.strategy_profile.explosion_round == ExplosionRoundStrat.EARLY_MID),
        "ex_round_strat_mid": int(player_a.strategy_profile.explosion_round == ExplosionRoundStrat.MID),
        "ex_round_strat_mid_late": int(player_a.strategy_profile.explosion_round == ExplosionRoundStrat.MID_LATE),
        "ex_round_strat_late": int(player_a.strategy_profile.explosion_round == ExplosionRoundStrat.LATE),

        # Exploded strategy
        "exploded_strat_points": int(player_a.strategy_profile.exploded == ExplodedStrat.POINTS),
        "exploded_strat_money": int(player_a.strategy_profile.exploded == ExplodedStrat.MONEY),
        "exploded_strat_early": int(player_a.strategy_profile.exploded == ExplodedStrat.ROUND_BASED_EARLY),
        "exploded_strat_mid": int(player_a.strategy_profile.exploded == ExplodedStrat.ROUND_BASED_MID),

        # Chip distribution
        "green-1": 0, "green-2": 0, "green-4": 0,
        "blue-1": 0, "blue-2": 0, "blue-4": 0,
        "red-1": 0, "red-2": 0, "red-4": 0,
        "yellow-1": 0, "yellow-2": 0, "yellow-4": 0,
        "orange-1": 0, "purple-1": 0, "black-1": 0,

        # Color distribution
        "green_count": 0, "blue_count": 0,"red_count": 0, "yellow_count": 0, "orange_count": 0, "purple_count": 0,
        "black_count": 0,

        # Value distribution
        "one_count": 0, "two_count": 0, "four_count": 0,

        # Milestones
        "final_droplet_position": player_a.droplet,
        "farthest_space_reached": player_a.farthest_space_reached,
        "explosion_count": player_a.explosion_count,

        # Outcome
        "player_a_vp": player_a.victory_points,
        "player_b_vp": player_b.victory_points,
        "margin": player_a.victory_points - player_b.victory_points,
        "percent_dif": round((player_a.victory_points + 1) / (player_b.victory_points + 1), 2),
        "tie": int(player_a.victory_points == player_b.victory_points),
        "player_a_won": int(player_a.victory_points > player_b.victory_points)
    }

    # Update the chip, color, and value counts
    for chip in player_a.unplayed_chips:
        if chip.color != ChipColor.WHITE:
            color_str = chip.color.name.lower()
            chip_key = f"{color_str}-{chip.value}"
            results[chip_key] += 1

            results[f"{color_str}_count"] += 1

            if chip.value == 1:
                results["one_count"] += 1
            elif chip.value == 2:
                results["two_count"] += 1
            elif chip.value == 4:
                results["four_count"] += 1

    return results


def run_match(strat_prof_a: GameStrategyProfile, strat_prof_b: GameStrategyProfile) -> dict:
    """Runs a complete match and records the results."""
    # Instantiate match objects
    supply_bank = SupplyBank(SHOP_CATALOG)
    player_a = Player(strat_prof_a)
    player_b = Player(strat_prof_b)

    player_a.setup_starting_bag()
    player_b.setup_starting_bag()

    # Run each round
    for current_round in range(1, TOTAL_ROUND_COUNT + 1):
        if current_round == ADD_WHITE_ROUND:
            player_a.unplayed_chips.append(Chip(ChipColor.WHITE, 1))
            player_b.unplayed_chips.append(Chip(ChipColor.WHITE, 1))
        play_single_round(player_a, player_b, supply_bank, current_round)

    return generate_results(player_a, player_b)