import unittest
import os
from unittest.mock import patch

from ui.custom_wizard import handle_custom_sim_file_exists_warning, handle_custom_sim, handle_edit_custom_strat_profile, \
    handle_edit_color_strat, STRATEGY_CATALOG, handle_edit_strategy, handle_edit_num_matches, \
    handle_confirm_run_custom_sim, handle_custom_sim_gatekeeper, handle_run_custom_sim


class TestCustomWizard(unittest.TestCase):

    def setUp(self):
        self.profile = {
            "colors": [],
            "value": "RANDOM",
            "ruby": "RANDOM",
            "flask": "RANDOM",
            "explosion_prob": "RANDOM",
            "explosion_round": "RANDOM",
            "exploded": "RANDOM"
        }

    @patch('builtins.print')
    @patch('builtins.input')
    def test_navigation_return_gates(self, mock_input, _):
        """Verify backward navigation handles."""
        mock_input.return_value = "2"
        handle_custom_sim_file_exists_warning()

        mock_input.return_value = "4"
        handle_custom_sim()

        mock_input.return_value = "8"
        current_strats = handle_edit_custom_strat_profile(self.profile)
        self.assertEqual(current_strats, self.profile)

        mock_input.return_value = "8"
        colors = ["RED"]
        result_colors = handle_edit_color_strat(colors)
        self.assertEqual(result_colors, ["RED"])

        mock_input.return_value = "6" # There are 5 ruby strategies, so 6 is the exit option
        active_selection = handle_edit_strategy(current_strat="SAVE", strategy_key="ruby")
        self.assertEqual(active_selection, "SAVE")

        mock_input.return_value = "5"
        active_selection = handle_edit_num_matches("100")
        self.assertEqual(active_selection, "100")

        mock_input.return_value = "2"
        handle_confirm_run_custom_sim(self.profile, "100")


    @patch('builtins.print')
    @patch('builtins.input')
    def test_wildcard_catchment_baskets(self, mock_input, mock_print):
        """Feeds bad inputs into menus to verify validation."""
        mock_input.side_effect = ["w", "2"]
        handle_custom_sim_file_exists_warning()
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')

        mock_input.side_effect = ["w", "4"]
        handle_custom_sim()
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 4.')

        mock_input.side_effect = ["w", "8"]
        result = handle_edit_custom_strat_profile(self.profile)
        self.assertEqual(result, self.profile)
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 8.')

        mock_input.side_effect = ["w", "8"]
        result = handle_edit_color_strat(["RED"])
        self.assertEqual(result, ["RED"])
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 8.')

        mock_input.side_effect = ["w", "6"] # There are 5 ruby strategies, so 6 is the exit option
        result = handle_edit_strategy(current_strat="SAVE", strategy_key="ruby")
        self.assertEqual(result, "SAVE")
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 6.')

        mock_input.side_effect = ["w", "5"]
        result = handle_edit_num_matches("100")
        self.assertEqual(result, "100")
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 5.')

        mock_input.side_effect = ["w", "2"]
        result = handle_confirm_run_custom_sim(self.profile, "100")
        self.assertFalse(result)
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')


    def test_gatekeeper_routing(self):
        """Ensures gatekeeper function correctly routes the user to the appropriate warning."""
        with (
            patch('os.path.exists') as mock_path_exists,
            patch('ui.custom_wizard.handle_custom_sim_file_exists_warning') as mock_warning,
            patch('ui.custom_wizard.handle_custom_sim') as mock_custom_sim
        ):
            # Custom sim results file already exists
            mock_path_exists.return_value = True
            handle_custom_sim_gatekeeper()
            mock_warning.assert_called_once()
            mock_custom_sim.assert_not_called()

            mock_path_exists.reset_mock()
            mock_warning.reset_mock()

            # Custom sim results file does not exist
            mock_path_exists.return_value = False
            handle_custom_sim_gatekeeper()
            mock_warning.assert_not_called()
            mock_custom_sim.assert_called_once()


    @patch('builtins.print')
    @patch('ui.custom_wizard.start_custom_simulation')
    def test_engine_handoff(self, mock_custom_sim, _):
        """Verifies the function passes user data to the simulation engine."""
        handle_run_custom_sim(self.profile, "100")
        mock_custom_sim.assert_called_once_with(self.profile, "100")


    @patch('builtins.print')
    @patch('builtins.input')
    def test_handle_add_remove_color(self, mock_input, _):
        """Verifies colors are successfully added and removed from the custom color list."""
        # Add a color
        mock_input.side_effect = ["2", "8"] # 2 adds BLUE, 8 returns
        results = handle_edit_color_strat(["RED", "GREEN"])
        self.assertEqual(results, ["RED", "GREEN", "BLUE"])

        # Remove a color
        mock_input.side_effect = ["1", "8"]  # 1 removes GREEN, 8 returns
        results = handle_edit_color_strat(["RED", "GREEN"])
        self.assertEqual(results, ["RED"])


if __name__ == '__main__':
    unittest.main()