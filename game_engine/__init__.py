from game_engine import phase_1_prep
from game_engine import phase_2_potions
from game_engine import phase_3_evaluation
from models.player import Player
from models.supply_bank import SupplyBank


def play_single_round(player_a: Player, player_b: Player, supply_bank: SupplyBank, current_round: int) -> None:
    """Orchestrates the entire lifecycle of a single game round in chronological order."""

    # Phase 1: Prep phase (calculate rat tails)
    phase_1_prep.calculate_rat_tails(player_a, player_b)

    # Phase 2: Potions phase (both players draw chips)
    phase_2_potions.run_potions_phase(player_a, current_round)
    phase_2_potions.run_potions_phase(player_b, current_round)

    # Phase 3: Evaluation phase (process the 6 steps)
    phase_3_evaluation.run_evaluation_phase(player_a, player_b, supply_bank, current_round)