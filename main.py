from ui.router import handle_main_menu

def main() -> None:
    try:
        handle_main_menu()
    except Exception as e:
        print(f"\n[FATAL ERROR] The application encountered an unhandled system crash: {e}")

if __name__ == "__main__":
    main()
