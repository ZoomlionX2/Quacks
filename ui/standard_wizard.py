import os

from simulation_engine import TOTAL_RUNS, continue_full_simulation, STATE_FILE_PATH, read_resume_point, \
    start_full_simulation
from ui import print_menu_header, MENU_WIDTH


# New simulation
def handle_new_sim_gatekeeper():
    if os.path.exists(STATE_FILE_PATH):
        handle_full_sim_file_exists_warning()
    else:
        handle_new_sim()


def prompt_full_sim_file_exists_warning() -> str:
    print_menu_header('NEW SIMULATION', MENU_WIDTH)
    print('[WARNING] A previous simulation session was already run. Continuing will REPLACE any existing output files.'
          ' Are you sure you wish to continue? (1-2)\n')

    # Options
    print('1. Yes - replace the existing file(s)')
    print('2. No - keep existing file(s) and return to main menu')

    return input().strip()


def handle_full_sim_file_exists_warning():
    while True:
        user_choice = prompt_full_sim_file_exists_warning()

        match user_choice:
            case "1":
                handle_new_sim()
                return

            case "2":
                return

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')


def prompt_new_sim() -> str:
    print_menu_header('NEW SIMULATION', MENU_WIDTH)
    print('Please select one of the following options (1-3):\n')

    # Options
    print('1. Begin new simulation')
    print('2. Set simulation session duration')
    print('3. Return to main menu')

    return input().strip()


def handle_new_sim():
    session_duration = "Until interrupted"

    while True:
        user_choice = prompt_new_sim()

        match user_choice:

            case "1":
                was_sim_executed = handle_confirm_begin_sim(session_duration)
                if was_sim_executed:
                    return

            case "2":
                session_duration = handle_set_new_sim_duration(session_duration)

            case "3":
                return

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 3.')


def prompt_confirm_begin_sim() -> str:
    print_menu_header('NEW SIMULATION', MENU_WIDTH)
    print('Begin simulation? (1-2):\n')

    # Options
    print('1. Yes')
    print('2. No - return to main menu')

    return input().strip()


def handle_confirm_begin_sim(session_duration: str):
    while True:
        user_choice = prompt_confirm_begin_sim()

        match user_choice:
            case "1":
                handle_begin_sim(session_duration)
                return True

            case "2":
                return False

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 2')


def handle_begin_sim(session_duration: str):
    print("[LAUNCH] Starting simulation engine. Press Ctrl+C at any time to pause and exit.")
    start_full_simulation(session_duration)

    return True


def prompt_set_new_sim_duration(active_duration: str) -> str:
    print_menu_header('NEW SIMULATION', MENU_WIDTH)
    print(f"Current simulation session duration: {active_duration}\n")
    print('Please select a simulation session duration (1-7):')

    # Options
    print('1. 1 hour')
    print('2. 2 hours')
    print('3. 4 hours')
    print('4. 8 hours')
    print('5. 12 hours')
    print('6. Until interrupted')
    print('7. Return to new simulation menu')

    return input().strip()


def handle_set_new_sim_duration(current_duration: str):
    active_selection = current_duration

    while True:
        user_choice = prompt_set_new_sim_duration(active_selection)
        match user_choice:
            case "1":
                active_selection = "1 hour"

            case "2":
                active_selection = "2 hours"

            case "3":
                active_selection = "4 hours"

            case "4":
                active_selection = "8 hours"

            case "5":
                active_selection = "12 hours"

            case "6":
                active_selection = "Until interrupted"

            case "7":
                return active_selection

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 7.')


# Continue simulation
def handle_existing_sim_gatekeeper():
    if os.path.exists(STATE_FILE_PATH) and read_resume_point() > 0:
        handle_existing_sim()
    else:
        handle_no_file_found()


def prompt_no_file_found() -> str:
    print_menu_header('CONTINUE SIMULATION', MENU_WIDTH)
    print('[INFO] No state file found. Please return to main menu (1):\n')

    # Options
    print('1. Return to main menu')

    return input().strip()


def handle_no_file_found():
    while True:
        user_choice = prompt_no_file_found()
        if user_choice == "1":
            return
        else:
            print('\n[ERROR] Invalid selection. Please enter 1.')


def prompt_existing_sim(simulation_duration: str, next_strat_id: int) -> str:
    print_menu_header('CONTINUE SIMULATION', MENU_WIDTH)
    # Current simulation statistics
    print(f"Last match number: {next_strat_id}")
    print(f"Matches remaining to complete: {TOTAL_RUNS - next_strat_id}")
    print(f"Percent complete: {(next_strat_id / TOTAL_RUNS) * 100:.1f}%\n")
    print(f"Simulation session duration: {simulation_duration}\n")

    print('Please select one of the following options (1-3):\n')

    # Options
    print('1. Continue simulation')
    print('2. Set simulation session duration')
    print('3. Return to main menu')

    return input().strip()


def handle_existing_sim():
    simulation_duration = "Until interrupted"
    next_strat_id = read_resume_point()

    while True:
        user_choice = prompt_existing_sim(simulation_duration, next_strat_id)

        match user_choice:
            case "1":
                was_sim_executed = handle_confirm_continue_sim(simulation_duration)
                if was_sim_executed:
                    return

            case "2":
                simulation_duration = handle_set_cont_sim_duration(simulation_duration)

            case "3":
                return

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 3.')


def prompt_confirm_continue_sim() -> str:
    print_menu_header('CONTINUE SIMULATION', MENU_WIDTH)

    print('Continue simulation? (1-2):\n')

    # Options
    print('1. Yes')
    print('2. No - return to previous menu')

    return input().strip()


def handle_confirm_continue_sim(session_duration: str):
    while True:
        user_choice = prompt_confirm_continue_sim()

        match user_choice:
            case "1":
                handle_continue_sim(session_duration)
                return True

            case "2":
                return False

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 2')


def handle_continue_sim(session_duration: str):
    print("[LAUNCH] Starting simulation engine. Press Ctrl+C at any time to pause and exit.")
    continue_full_simulation(session_duration)

    return


def prompt_set_cont_sim_duration(simulation_duration: str) -> str:
    print_menu_header('CONTINUE SIMULATION', MENU_WIDTH)
    print(f"Current simulation session duration: {simulation_duration}\n")

    print('Please select a simulation session duration (1-7):')

    # Options
    print('1. 1 hour')
    print('2. 2 hours')
    print('3. 4 hours')
    print('4. 8 hours')
    print('5. 12 hours')
    print('6. Until interrupted')
    print('7. Return to continue simulation menu')

    return input().strip()


def handle_set_cont_sim_duration(simulation_duration: str) -> str:
    active_selection = simulation_duration
    while True:
        user_choice = prompt_set_cont_sim_duration(active_selection)
        match user_choice:
            case "1":
                active_selection = "1 hour"

            case "2":
                active_selection = "2 hours"

            case "3":
                active_selection = "4 hours"

            case "4":
                active_selection = "8 hours"

            case "5":
                active_selection = "12 hours"

            case "6":
                active_selection = "Until interrupted"

            case "7":
                return active_selection

            case _:
                print('\n[ERROR] Invalid selection. Please enter a number between 1 and 7.')