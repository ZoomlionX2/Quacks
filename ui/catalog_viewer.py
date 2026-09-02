from models.strategy import COLOR_STRATS
from ui import print_menu_header, MENU_WIDTH


def prompt_display_color_strats() -> str:
    print_menu_header('COLOR STRATEGY REFERENCE', MENU_WIDTH)
    print(f"{'Color Strategy ID':<25}{'Colors'}")
    print('-' * 31)
    for index, color_strategy in enumerate(COLOR_STRATS):
        colors = ', '.join(color.name for color in color_strategy)
        print(f"{index:<25}{colors}")

    print('\nPlease return to the main menu to proceed (1):\n')
    print('1. Return to main menu')

    return input().strip()


def handle_display_color_strats():
    while True:
        user_choice = prompt_display_color_strats()

        match user_choice:
            case "1":
                return

            case _:
                print('\n[ERROR] Invalid selection. Please enter 1.')