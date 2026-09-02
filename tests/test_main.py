import unittest
from unittest.mock import patch
from main import main


class TestMain(unittest.TestCase):

    @patch('builtins.print')
    @patch('main.handle_main_menu')
    def test_main_(self, mock_router, mock_print):
        """Verifies that launching main() cleanly transfers control to the main menu loop."""
        # Entry gate execution
        main()

        mock_router.assert_called_once()

        # Unhandled exception
        mock_router.side_effect = Exception("Kernel out of bounds")
        main()
        mock_print.assert_called_once_with("\n[FATAL ERROR] The application encountered an unhandled system crash: "
                                           "Kernel out of bounds")


if __name__ == '__main__':
    unittest.main()