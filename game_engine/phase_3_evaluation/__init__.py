from models.player import Player
from models.supply_bank import SupplyBank

FINAL_ROUND = 9

def run_evaluation_phase(player_a: Player, player_b: Player, supply_bank: SupplyBank, current_round: int):
    """Executes the 6 official evaluation steps (A through F) in chronological order at the end of a round."""
    # Step A
    from game_engine.phase_3_evaluation.step_a_bonus_die import roll_bonus_die
    roll_bonus_die(player_a, player_b, supply_bank)

    # Step B
    from game_engine.phase_3_evaluation.step_b_chip_actions import execute_chip_actions
    execute_chip_actions(player_a, player_b)

    # Step C
    from game_engine.phase_3_evaluation.step_c_rubies import award_ruby
    award_ruby(player_a)
    award_ruby(player_b)

    # Step D
    from game_engine.phase_3_evaluation.step_d_points import award_victory_points
    award_victory_points(player_a, current_round)
    award_victory_points(player_b, current_round)

    # Step E
    from game_engine.phase_3_evaluation.step_e_buy_chips import execute_buying_phase
    execute_buying_phase(player_a, supply_bank, current_round)
    execute_buying_phase(player_b, supply_bank, current_round)

    # Step F
    from game_engine.phase_3_evaluation.step_f_end_of_turn import execute_end_of_turn_actions
    execute_end_of_turn_actions(player_a, current_round)
    execute_end_of_turn_actions(player_b, current_round)
