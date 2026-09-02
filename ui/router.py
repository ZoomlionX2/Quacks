import sys

from ui import print_menu_header, MENU_WIDTH
from ui.catalog_viewer import handle_display_color_strats
from ui.custom_wizard import handle_custom_sim_gatekeeper
from ui.standard_wizard import handle_new_sim_gatekeeper, handle_existing_sim_gatekeeper


def prompt_main_menu() -> str:
    print_menu_header('MAIN MENU', MENU_WIDTH)
    print('Please select one of the following options (1-5):\n')

    # Options
    print('1. Initiate new full simulation')
    print('2. Continue existing simulation')
    print('3. Create custom simulation')
    print('4. Display color strategies')
    print('5. Quit')

    return input().strip()


def handle_main_menu():
    dispatch_table = {
        "1": handle_new_sim_gatekeeper,
        "2": handle_existing_sim_gatekeeper,
        "3": handle_custom_sim_gatekeeper,
        "4": handle_display_color_strats,
        "5": handle_confirm_quit
    }

    while True:
        user_choice = prompt_main_menu()
        if user_choice in dispatch_table:
            target_function = dispatch_table[user_choice]
            target_function()
        else:
            print('\n[ERROR] Invalid selection. Please enter a number between 1 and 5.')


def prompt_confirm_quit() -> str:
    print_menu_header('QUIT?', MENU_WIDTH)
    print('Are you sure you want to quit? (1-2):\n')

    # Options
    print('1. Yes')
    print('2. No - Return to main menu')

    return input().strip()


def handle_confirm_quit():
    while True:
        user_choice = prompt_confirm_quit()

        if user_choice == "1":
            handle_quit()

        elif user_choice == "2":
            return

        else:
            print('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')


def handle_quit():
    print("\n Thank you for using the Quacks Simulator. Goodbye!")
    sys.exit(0)