import os

from models.strategy import ValueStrat, RubyStrat, ExplosionProbabilityToleranceStrat, ExplosionRoundStrat, FlaskStrat, \
    ExplodedStrat
from simulation_engine import CUSTOM_SIM_RESULTS_FILE, start_custom_simulation
from ui import print_menu_header, MENU_WIDTH


STRATEGY_CATALOG = {
    "value": [strat.name for strat in ValueStrat],
    "ruby": [strat.name for strat in RubyStrat],
    "flask": [strat.name for strat in FlaskStrat],
    "explosion probability-based": [strat.name for strat in ExplosionProbabilityToleranceStrat],
    "explosion round-based": [strat.name for strat in ExplosionRoundStrat],
    "exploded": [strat.name for strat in ExplodedStrat]
}


def handle_custom_sim_gatekeeper():
    if os.path.exists(CUSTOM_SIM_RESULTS_FILE):
        handle_custom_sim_file_exists_warning()
    else:
        handle_custom_sim()


def prompt_custom_sim_file_exists_warning() -> str:
    print_menu_header('CUSTOM SIMULATION', MENU_WIDTH)
    print('[WARNING] A custom simulation results file already exists. Running a custom simulation will REPLACE this '
          'file. Are you sure you wish to continue? (1-2)\n')

    # Options
    print('1. Yes')
    print('2. No - keep existing file and return to main menu')

    return input().strip()


def handle_custom_sim_file_exists_warning():
    while True:
        user_choice = prompt_custom_sim_file_exists_warning()

        match user_choice:
            case "1":
                handle_custom_sim()
                return

            case "2":
                return

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')


def prompt_custom_sim() -> str:
    print_menu_header('CUSTOM SIMULATION', MENU_WIDTH)
    print('Please select from the options below (1-4):\n')

    # Options
    print('1. Edit custom strategy profile')
    print('2. Edit number of matches to simulate')
    print('3. Run custom simulation')
    print('4. Return to main menu')

    return input().strip()


def handle_custom_sim():
    custom_strategy_profile = {
        "colors": [],
        "value": "RANDOM",
        "ruby": "RANDOM",
        "flask": "RANDOM",
        "explosion_prob": "RANDOM",
        "explosion_round": "RANDOM",
        "exploded": "RANDOM"
    }

    num_matches = "1000"

    while True:
        user_choice = prompt_custom_sim()
        match user_choice:
            case "1":
                custom_strategy_profile = handle_edit_custom_strat_profile(custom_strategy_profile)

            case "2":
                num_matches = handle_edit_num_matches(num_matches)

            case "3":
                was_sim_executed = handle_confirm_run_custom_sim(custom_strategy_profile, num_matches)
                if was_sim_executed:
                    return

            case "4":
                return

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 4.')


def prompt_edit_custom_strat_profile(current_profile: dict) -> str:
    print_menu_header('CUSTOM SIMULATION', MENU_WIDTH)
    print("   Current Simulation Settings   ")
    print("---------------------------------")

    if current_profile["colors"]:
        color_text = ", ".join(current_profile["colors"])
    else:
        color_text = "ALL COLORS, BUT RANDOM ORDER"

    print(f"Colors: {color_text}")
    print(f"Value: {current_profile["value"]}")
    print(f"Ruby: {current_profile["ruby"]}")
    print(f"Flask: {current_profile["flask"]}")
    print(f"Explosion (probability): {current_profile["explosion_prob"]}")
    print(f"Explosion (round): {current_profile["explosion_round"]}")
    print(f"Exploded: {current_profile["exploded"]}")

    print('Please select the strategy you would like to edit (1-8):\n')

    # Options
    print('1. Color')
    print('2. Value')
    print('3. Ruby')
    print('4. Flask')
    print('5. Explosion risk tolerance (probability-based)')
    print('6. Explosion risk tolerance (round-based)')
    print('7. Exploded')
    print('8. Return to custom simulation menu')

    return input().strip()


def handle_edit_custom_strat_profile(custom_strategy_profile: dict):
    current_strats = custom_strategy_profile

    while True:
        user_choice = prompt_edit_custom_strat_profile(current_strats)

        match user_choice:
            case "1":
                current_strats["colors"] = handle_edit_color_strat(current_strats["colors"])

            case "2":
                current_strats["value"] = handle_edit_strategy(current_strats["value"], "value")

            case "3":
                current_strats["ruby"] = handle_edit_strategy(current_strats["ruby"], "ruby")

            case "4":
                current_strats["flask"] = handle_edit_strategy(current_strats["flask"], "flask")

            case "5":
                current_strats["explosion_prob"] = handle_edit_strategy(current_strats["explosion_prob"],
                                                                        "explosion probability-based")

            case "6":
                current_strats["explosion_round"] = handle_edit_strategy(current_strats["explosion_round"],
                                                                         "explosion round-based")

            case "7":
                current_strats["exploded"] = handle_edit_strategy(current_strats["exploded"], "exploded")

            case "8":
                return current_strats

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 8.')


def prompt_edit_color_strat(colors: list) -> str:
    print_menu_header('CUSTOM SIMULATION', MENU_WIDTH)

    if colors:
        color_text = ", ".join(colors)
    else:
        color_text = "ALL COLORS, BUT RANDOM ORDER"

    print(f"Current color strategy: {color_text}\n")
    print('Please select a color to add or remove it (1-8):\n')

    # Options
    print('1. GREEN')
    print('2. BLUE')
    print('3. RED')
    print('4. YELLOW')
    print('5. ORANGE')
    print('6. PURPLE')
    print('7. BLACK')
    print('8. Return to custom strategy editor menu')

    return input().strip()


def handle_edit_color_strat(colors: list) -> list:
    current_colors = colors

    while True:
        user_choice = prompt_edit_color_strat(current_colors)

        match user_choice:
            case "1":
                current_colors = handle_add_remove_color("GREEN", current_colors)

            case "2":
                current_colors = handle_add_remove_color("BLUE", current_colors)

            case "3":
                current_colors = handle_add_remove_color("RED", current_colors)

            case "4":
                current_colors = handle_add_remove_color("YELLOW", current_colors)

            case "5":
                current_colors = handle_add_remove_color("ORANGE", current_colors)

            case "6":
                current_colors = handle_add_remove_color("PURPLE", current_colors)

            case "7":
                current_colors = handle_add_remove_color("BLACK", current_colors)

            case "8":
                return current_colors

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 8.')


def handle_add_remove_color(color: str, colors: list) -> list:
    if color in colors:
        colors.remove(color)
    else:
        colors.append(color)

    return colors


def prompt_edit_strategy(current_strat: str, strategy_key: str, strategy_list: list, exit_option_num: str) -> str:
    print_menu_header('CUSTOM SIMULATION', MENU_WIDTH)
    print(f"Current {strategy_key} strategy: {current_strat}\n")
    print(f"Please select a strategy (1-{exit_option_num})")

    # Options
    for index, strategy in enumerate(strategy_list, start=1):
        print(f"{index}. {strategy}")
    print(f"{exit_option_num}. Return to previous menu")

    return input().strip()


def handle_edit_strategy(current_strat: str, strategy_key: str):
    active_selection = current_strat
    strategy_list = STRATEGY_CATALOG[strategy_key]
    exit_option_num = str(len(strategy_list) + 1)
    valid_numeric_keys = [str(i) for i in range (1, len(strategy_list) + 1)]

    while True:
        user_choice = prompt_edit_strategy(active_selection, strategy_key, strategy_list, exit_option_num)

        if user_choice == exit_option_num:
            return active_selection

        elif user_choice in valid_numeric_keys:
            selected_index = int(user_choice) - 1
            return strategy_list[selected_index]

        else:
            print(f"\n[ERROR] Invalid selection. Please enter a number between 1 and {exit_option_num}.")


def prompt_edit_num_matches(num_matches: str) -> str:
    print_menu_header('CUSTOM SIMULATION', MENU_WIDTH)
    print(f"Number of matches to simulate: {num_matches}")
    print('Please select the number of matches to simulate from the options below (1-5):\n')

    # Options
    print('1. 100')
    print('2. 1000')
    print('3. 5000')
    print('4. 10,000')
    print('5. Return to custom simulation menu')

    return input().strip()


def handle_edit_num_matches(current_num: str):
    active_selection = current_num

    while True:
        user_choice = prompt_edit_num_matches(active_selection)

        match user_choice:
            case "1":
                active_selection = "100"

            case "2":
                active_selection = "1000"

            case "3":
                active_selection = "5000"

            case "4":
                active_selection = "10000"

            case "5":
                return active_selection

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 5.')


def prompt_confirm_run_custom_sim() -> str:
    print_menu_header('CUSTOM SIMULATION', MENU_WIDTH)

    print('Commence simulation? (1-2):\n')

    # Options
    print('1. Yes')
    print('2. No - return to custom simulation menu')

    return input().strip()


def handle_confirm_run_custom_sim(strategy_profile: dict, num_matches: str) -> bool:
    while True:
        user_choice = prompt_confirm_run_custom_sim()

        match user_choice:
            case "1":
                handle_run_custom_sim(strategy_profile, num_matches)
                return True

            case "2":
                return False

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 2')


def handle_run_custom_sim(strategy_profile: dict, num_matches: str):
    print("[LAUNCH] Starting simulation engine...")
    print("Simulating matches. Press Ctrl+C at any time to pause and exit.")

    start_custom_simulation(strategy_profile, num_matches)

    return