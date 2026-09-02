import unittest
from unittest.mock import patch

from ui.standard_wizard import (
    handle_new_sim, handle_set_new_sim_duration, handle_confirm_begin_sim,
    handle_existing_sim, handle_confirm_continue_sim, handle_full_sim_file_exists_warning, handle_no_file_found,
    handle_set_cont_sim_duration, handle_new_sim_gatekeeper, handle_existing_sim_gatekeeper, handle_begin_sim,
    handle_continue_sim
)


class TestMenuNavigationMatrix(unittest.TestCase):

    @patch('builtins.print')
    @patch('builtins.input')
    def test_navigation_return_gates(self, mock_input, _):
        """Verify backward navigation handles."""
        mock_input.return_value = "2"
        handle_full_sim_file_exists_warning()

        mock_input.return_value = "3"
        handle_new_sim()

        mock_input.return_value = "2"
        self.assertFalse(handle_confirm_begin_sim("Until interrupted"))

        mock_input.return_value = "7"
        final_duration = handle_set_new_sim_duration("Until interrupted")
        self.assertEqual(final_duration, "Until interrupted")

        mock_input.return_value = "1"
        handle_no_file_found()

        mock_input.return_value = "3"
        handle_existing_sim()

        mock_input.return_value = "2"
        self.assertFalse(handle_confirm_continue_sim("Until interrupted"))

        mock_input.return_value = "7"
        self.assertEqual(handle_set_cont_sim_duration("1 hour"), "1 hour")


    @patch('builtins.input')
    @patch('builtins.print')
    def test_wildcard_catchment_baskets(self, mock_print, mock_input):
        """Feeds bad inputs into menus to verify validation."""
        mock_input.side_effect = ["w", "2"]
        handle_full_sim_file_exists_warning()
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')

        mock_input.side_effect = ["w", "3"]
        handle_new_sim()
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 3.')

        mock_input.side_effect = ["w", "2"]
        handle_confirm_begin_sim("Until interrupted")
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')

        mock_input.side_effect = ["9", "7"]
        handle_set_new_sim_duration("1 hour")
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 7.')

        mock_input.side_effect = ["w", "1"]
        handle_no_file_found()
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter 1.')

        mock_input.side_effect = ["w", "3"]
        handle_existing_sim()
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 3.')

        mock_input.side_effect = ["w", "2"]
        handle_confirm_continue_sim("Until interrupted")
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 2.')

        mock_input.side_effect = ["w", "7"]
        handle_set_cont_sim_duration("Until interrupted")
        mock_print.assert_any_call('\n[ERROR] Invalid selection. Please enter a number between 1 and 7.')


    def test_gatekeeper_routing(self):
        """Ensures gatekeeper functions correctly route the user to the appropriate warnings."""
        with (
            patch('os.path.exists') as mock_exists,
            patch('ui.standard_wizard.read_resume_point') as mock_resume_pt,
            patch('ui.standard_wizard.handle_new_sim') as mock_new_sim,
            patch('ui.standard_wizard.handle_full_sim_file_exists_warning') as mock_existing_file,
            patch('ui.standard_wizard.handle_existing_sim') as mock_existing_sim,
            patch('ui.standard_wizard.handle_no_file_found') as mock_no_file
        ):

            # New simulation - results file already exists
            mock_exists.return_value = True
            mock_resume_pt.return_value = 1
            handle_new_sim_gatekeeper()
            mock_existing_file.assert_called_once()
            mock_new_sim.assert_not_called()

            mock_existing_file.reset_mock()
            mock_new_sim.reset_mock()

            # New simulation - no results file exists
            mock_exists.return_value = False
            mock_resume_pt.return_value = 0
            handle_new_sim_gatekeeper()
            mock_existing_file.assert_not_called()
            mock_new_sim.assert_called_once()

            # Continue simulation - results file already exists
            mock_exists.return_value = True
            mock_resume_pt.return_value = 1
            handle_existing_sim_gatekeeper()
            mock_existing_sim.assert_called_once()
            mock_no_file.assert_not_called()

            mock_existing_sim.reset_mock()
            mock_no_file.reset_mock()

            # Continue simulation - no results file exists
            mock_exists.return_value = False
            mock_resume_pt.return_value = 0
            handle_existing_sim_gatekeeper()
            mock_existing_sim.assert_not_called()
            mock_no_file.assert_called_once()


    @patch('builtins.print')
    @patch('ui.standard_wizard.start_full_simulation')
    @patch('ui.standard_wizard.continue_full_simulation')
    def test_engine_handoffs(self, mock_continue_sim, mock_begin_sim, _):
        """Verifies the functions that pass user data to the simulation engine."""
        # New simulation launch
        handle_begin_sim("8 hours")
        mock_begin_sim.assert_called_once_with("8 hours")

        # Continue simulation launch
        handle_continue_sim("8 hours")
        mock_continue_sim.assert_called_once_with("8 hours")


if __name__ == '__main__':
    unittest.main()