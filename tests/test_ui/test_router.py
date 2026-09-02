import unittest
from unittest.mock import patch

from ui.router import handle_confirm_quit, handle_main_menu, handle_quit


class TestRouter(unittest.TestCase):

    @patch('builtins.print')
    @patch('builtins.input')
    def test_navigation_return_gate(self, mock_input, _):
        """Verify backward navigation handle."""
        mock_input.return_value = "2"
        handle_confirm_quit()


    @patch('builtins.print')
    @patch('builtins.input')
    def test_wildcard_catchment_baskets(self, mock_input, mock_print):
        """Feed bad inputs to confirm validation."""
        mock_input.side_effect = ["w", "5", "1"]

        try:
            handle_main_menu()
        except SystemExit:
            pass

        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 5.')

        mock_input.side_effect = ["w", "2"]
        handle_confirm_quit()
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')


    @patch('builtins.print')
    @patch('builtins.input')
    @patch('ui.router.handle_new_sim_gatekeeper')
    def test_main_menu_navigation_gates(self, mock_gatekeeper, mock_input, _):
        """Verify that selecting option 1 dispatches control to the standard simulation wizard."""
        mock_input.side_effect = ["1", "5", "1"]

        try:
            handle_main_menu()
        except SystemExit:
            pass

        mock_gatekeeper.assert_called_once()


    @patch('builtins.print')
    @patch('sys.exit')
    def test_handle_quit(self, mock_exit, _):
        """Verify the program exits successfully."""
        handle_quit()
        mock_exit.assert_called_once()


if __name__ == '__main__':
    unittest.main()