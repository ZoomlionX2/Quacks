MENU_WIDTH = 130

def print_menu_header(current_page: str, width: int = MENU_WIDTH) -> None:
    """Prints the header for the current menu page."""
    # Clear screen
    print("\033[H\033[2J", end="")

    # Header
    print('-' * width)
    print(f'{"THE QUACKS OF QUEDLINBURG SIMULATOR":^{width}}')
    print(f'{"-" + current_page + "-":^{width}}')
    print('-' * width, '\n')