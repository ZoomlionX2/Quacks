import unittest
from unittest.mock import patch

from ui.catalog_viewer import handle_display_color_strats


class TestCatalogViewer(unittest.TestCase):

    @patch('builtins.print')
    @patch('builtins.input')
    def test_navigation_return_gate(self, mock_input, _):
        """Verify backward navigation handle."""
        mock_input.return_value = "1"
        handle_display_color_strats()


    @patch('builtins.print')
    @patch('builtins.input')
    def test_wildcard_catchment_basket(self, mock_input, mock_print):
        """Feeds bad inputs into menu to verify validation."""
        mock_input.side_effect = ["w", "1"]
        handle_display_color_strats()
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter 1.')


if __name__ == '__main__':
    unittest.main()