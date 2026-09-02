import json
import multiprocessing as mp
import os
import unittest
from unittest.mock import patch, mock_open, MagicMock, ANY

from config.chip_config import ChipColor
from models.strategy import (
    COLOR_STRATS, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, ExplosionRoundStrat,
    ExplodedStrat
)
from simulation_engine import generate_strategy_by_index, TOTAL_STRATEGIES, update_resume_point, read_resume_point, \
    STATE_FILE_PATH, simulation_worker, run_simulation, convert_duration_to_seconds, full_sim_results_writer, \
    custom_sim_results_writer, CUSTOM_SIM_RESULTS_FILE, start_full_simulation, TOTAL_RUNS, continue_full_simulation, \
    build_profile_from_menu_strings, start_custom_simulation


class TestSimulationEngine(unittest.TestCase):

    @patch('os.replace')
    @patch('os.makedirs')
    def test_resume_point(self, mock_makedirs, mock_replace):
        """Verifies that the state ledger writes atomically and reads back correctly."""
        import simulation_engine

        m_write = mock_open()
        with patch('builtins.open', m_write):
            update_resume_point(completed_run_id=5000)

        mock_makedirs.assert_called_once_with(simulation_engine.OUTPUT_FOLDER_DIR, exist_ok=True)
        mock_replace.assert_called_once_with(STATE_FILE_PATH + ".tmp", STATE_FILE_PATH)

        fake_json_data = json.dumps({"next_run_id": 5001})
        m_read = mock_open(read_data=fake_json_data)

        with patch('builtins.open', m_read):
            resume_id = read_resume_point()

        self.assertEqual(resume_id, 5001)


    def test_generate_strategy_by_index(self):
        """Verify indices map to the correct strategy combination.

        MATHEMATICAL DERIVATION OF THE 71287 TEST CASE:
        ----------------------------------------------
        You can select any random combination of strategies and derive the strategy index number using a concept similar
        to converting between number systems. The right-most column (exploded strat) is the 1's (units) place. Because
        that column can fit four units, overflow happens on the fifth unit. You must then carry over to the next column,
        explosion round strat. That means each digit of the explosion round column represents four units. This same
        pattern continues as you move to the left. So, the explosion probability column represents 6 explosion rounds,
        which is 24 units. So, this is the 24's column. We next have the 120's, 600's, 2400, and 7200's. If you
        multiply each of these column values by the digits of that column (i.e. the length of the enums (remember to
        exclude RANDOM and to always start the counts at 0)), and then add the results, you end up with the total number
        of combinations. Thus, to convert a given strategy combination into its corresponding strategy index, multiply
        the digit representing the strategy by the value of that column. Add these products to create the index. For our
        test case it works like this:

        (GREEN, YELLOW) = 9 * 7200 = 64800
        LEAST_DISPARITY = 2 * 2400 = 4800
        FLASK = 2 * 600 = 1200
        FIFTY = 4 * 120 = 480
        HIGH = 0 * 24 = 0
        EARLY = 1 * 4 = 4
        ROUND_BASED_MID = 3 * 1 = 3

        Strategy index = 64800 + 4800 + 1200 + 480 + 0 + 4 + 3 = 71287
        """
        # Index of 0 should pick first strategy from each group
        profile = generate_strategy_by_index(0)

        self.assertEqual(profile.colors, COLOR_STRATS[0])
        self.assertEqual(profile.value, list(ValueStrat)[0])
        self.assertEqual(profile.ruby, list(RubyStrat)[0])
        self.assertEqual(profile.flask, list(FlaskStrat)[0])
        self.assertEqual(profile.explosion_prob, list(ExplosionProbabilityToleranceStrat)[0])
        self.assertEqual(profile.explosion_round, list(ExplosionRoundStrat)[0])
        self.assertEqual(profile.exploded, list(ExplodedStrat)[0])

        # Last index should pick the last strategy from each group (excluding RANDOM)
        last_index = TOTAL_STRATEGIES - 1
        profile = generate_strategy_by_index(last_index)

        non_random_value_strats = (strat for strat in list(ValueStrat) if strat != ValueStrat.RANDOM)
        non_random_ruby_strats = (strat for strat in list(RubyStrat) if strat != RubyStrat.RANDOM)
        non_random_flask_strats = (strat for strat in list(FlaskStrat) if strat != FlaskStrat.RANDOM)
        non_random_ex_prob_strats = (strat for strat in list(ExplosionProbabilityToleranceStrat) if strat
                                     != ExplosionProbabilityToleranceStrat.RANDOM)
        non_random_ex_round_strats = (strat for strat in list(ExplosionRoundStrat) if strat
                                      != ExplosionRoundStrat.RANDOM)
        non_random_exploded_strats = (strat for strat in list(ExplodedStrat) if strat != ExplodedStrat.RANDOM)

        self.assertEqual(profile.colors, COLOR_STRATS[-1])
        self.assertEqual(profile.value, list(non_random_value_strats)[-1])
        self.assertEqual(profile.ruby, list(non_random_ruby_strats)[-1])
        self.assertEqual(profile.flask, list(non_random_flask_strats)[-1])
        self.assertEqual(profile.explosion_prob, list(non_random_ex_prob_strats)[-1])
        self.assertEqual(profile.explosion_round, list(non_random_ex_round_strats)[-1])
        self.assertEqual(profile.exploded, list(non_random_exploded_strats)[-1])

        # Index is 71287 - see docstring for how to choose an expected result and generate an index from it to test
        profile = generate_strategy_by_index(71287)

        self.assertEqual(profile.colors, (ChipColor.GREEN, ChipColor.YELLOW))
        self.assertEqual(profile.value, ValueStrat.LEAST_DISPARITY)
        self.assertEqual(profile.ruby, RubyStrat.FLASK)
        self.assertEqual(profile.flask, FlaskStrat.FIFTY)
        self.assertEqual(profile.explosion_prob, ExplosionProbabilityToleranceStrat.HIGH)
        self.assertEqual(profile.explosion_round, ExplosionRoundStrat.EARLY)
        self.assertEqual(profile.exploded, ExplodedStrat.ROUND_BASED_MID)


    def test_simulation_worker(self):
        """Verifies that workers claim chunks, run matches, and queue data accurately."""
        global_run_counter = mp.Value('i', 0)
        global_queue = mp.Queue(maxsize=200)
        shutdown_event = mp.Event()
        dummy_match_output = {"victory_points_a": 25, "victory_points_b": 18}

        with patch('simulation_engine.run_match') as mock_run_match:
            mock_run_match.side_effect = lambda *args, **kwargs: dummy_match_output.copy()
            simulation_worker(
                global_run_counter=global_run_counter,
                global_queue=global_queue,
                shutdown_event=shutdown_event,
                custom_profile=None,
                total_runs=100
            )

        # Worker advances global run counter correctly
        self.assertEqual(global_run_counter.value, 100)

        # Worker runs 100 matches
        self.assertEqual(mock_run_match.call_count, 100)

        # Move items from global queue to a results list
        results_in_queue = []
        while not global_queue.empty():
            item = global_queue.get()
            if item is not None:
                results_in_queue.append(item)

        # Exactly 100 match records were pushed
        self.assertEqual(len(results_in_queue), 100)

        # Results are 1-indexed
        self.assertEqual(results_in_queue[0]["run_id"], 1)
        self.assertEqual(results_in_queue[-1]["run_id"], 100)

        # Game engine attributes preserved
        self.assertEqual(results_in_queue[0]["victory_points_a"], 25)


    def test_full_sim_results_writer(self):
        """Verifies that the full simulation writer drains rows, chops batches, and flushes stragglers."""
        sample_row_1 = {"run_id": 1, "score": 42}
        sample_row_2 = {"run_id": 2, "score": 45}

        mock_queue = MagicMock()
        mock_queue.get.side_effect = [sample_row_1, sample_row_2, None]

        with (
            patch('builtins.print'),
            patch('simulation_engine.print_performance_dashboard') as mock_dash,
            patch('simulation_engine.update_resume_point') as mock_resume_point,
            patch('simulation_engine.write_batch_to_parquet') as mock_write_parquet,
        ):

            # Normal run with stragglers (batch list is smaller than TOTAL_RUNS, so it must use the exception gate)
            full_sim_results_writer(global_queue=mock_queue, num_workers=1)

            mock_write_parquet.assert_called_once()
            mock_resume_point.assert_called_once_with(2)
            mock_dash.assert_called_once_with(2, ANY)

            # Verify batch boundary splits
            mock_write_parquet.reset_mock()
            mock_resume_point.reset_mock()
            mock_dash.reset_mock()

            with patch('simulation_engine.BATCH_SIZE', 1):
                mock_queue.get.side_effect = [sample_row_1, sample_row_2, None]

                full_sim_results_writer(global_queue=mock_queue, num_workers=1)

                self.assertEqual(mock_write_parquet.call_count, 2)
                self.assertEqual(mock_resume_point.call_count, 2)


    @patch('builtins.print')
    @patch('builtins.open')
    def test_custom_sim_results_writer(self, mock_file_open, _):
        """Verify the custom writer drains rows, sorts by ID, and writes CSVs."""
        sample_row_1 = {"run_id": 2, "score": 45}
        sample_row_2 = {"run_id": 1, "score": 50}

        mock_queue = MagicMock()
        mock_queue.get.side_effect = [sample_row_2, sample_row_1, None]
        m_csv_file = mock_open()
        mock_file_open.side_effect = m_csv_file

        custom_sim_results_writer(global_queue=mock_queue, num_workers=1)

        # Custom file configuration targeted
        m_csv_file.assert_called_once_with(CUSTOM_SIM_RESULTS_FILE, mode="w", newline="", encoding="utf-8")

        mock_handle = m_csv_file()
        write_calls_list = [call_args[0][0] for call_args in mock_handle.write.call_args_list]
        data_dump_string = "".join(write_calls_list)

        # Sorting
        self.assertTrue(data_dump_string.find("run_id") != -1)
        self.assertTrue(data_dump_string.find("1") < data_dump_string.find("2"))


    def test_convert_duration_to_seconds(self):
        """Verify the human-readable durations map correctly to their respective durations."""
        test_cases = [
            ("1 hour", 3600),
            ("2 hours", 7200),
            ("4 hours", 14400),
            ("8 hours", 28800),
            ("12 hours", 43200),
            ("Until interrupted", None)
        ]

        for input_string, expected_seconds in test_cases:
            with self.subTest(duration=input_string):
                result = convert_duration_to_seconds(input_string)
                self.assertEqual(result, expected_seconds)



    def test_run_simulation(self):
        """Verifies that the necessary processes are spawned and time-limits are enforced."""
        fake_timeline = [0, 0.5, 10, 11]

        with (
            patch('builtins.print'),
            patch('simulation_engine.convert_duration_to_seconds') as mock_duration,
            patch('multiprocessing.Process') as mock_process,
            patch('threading.Thread') as mock_thread,
            patch('multiprocessing.Queue') as _,
            patch('multiprocessing.Value') as _,
            patch('multiprocessing.Event') as mock_event,
            patch('time.time') as mock_time
        ):

            mock_duration.return_value = 5
            mock_time.side_effect = fake_timeline

            captured_event = MagicMock()
            mock_event.return_value = captured_event
            event_is_tripped = False

            def fake_set_trigger():
                nonlocal event_is_tripped
                event_is_tripped = True

            captured_event.set.side_effect = fake_set_trigger
            captured_event.is_set.side_effect = lambda: event_is_tripped

            mock_proc_instance = MagicMock()
            mock_proc_instance.is_alive.side_effect = lambda: not event_is_tripped
            mock_process.return_value = mock_proc_instance

            run_simulation(session_duration="1 hour", start_run_idx=0)

            mock_thread.assert_called_once()
            self.assertTrue(mock_process.call_count > 0)
            mock_event.return_value.set.assert_called_once()


    @patch('simulation_engine.run_simulation')
    @patch('glob.glob')
    @patch('os.remove')
    def test_start_full_simulation(self, mock_remove, mock_glob, mock_run_sim):
        """Verifies that starting a fresh simulation purges old JSON states, clears old parquet chunks and launches
        from 0."""
        fake_old_chunk_1 = os.path.join("simulation_output", "full_simulation_data", "old_chunk_0.parquet")
        fake_old_chunk_2 = os.path.join("simulation_output", "full_simulation_data", "old_chunk_1000000.parquet")
        mock_glob.return_value = [fake_old_chunk_1, fake_old_chunk_2]

        with (
            patch('builtins.print'),
            patch('os.path.exists') as mock_exists
        ):
            mock_exists.return_value = True
            start_full_simulation(simulation_duration="4 hours")

            # Remove old state ledger file
            mock_remove.assert_any_call(STATE_FILE_PATH)

            # Found all the parquet files
            expected_glob_pattern = os.path.join("simulation_output", "full_simulation_results", "*.parquet")
            mock_glob.assert_called_once_with(expected_glob_pattern)

            mock_remove.assert_any_call(fake_old_chunk_1)
            mock_remove.assert_any_call(fake_old_chunk_2)

            # Control handed over to run_simulation
            mock_run_sim.assert_called_once_with("4 hours", start_run_idx=0, total_runs=TOTAL_RUNS)


    @patch('simulation_engine.run_simulation')
    @patch('simulation_engine.read_resume_point')
    @patch('builtins.print')
    def test_continue_full_simulation(self, _, mock_read_resume, mock_run_sim):
        """Verify continuing a simulation reads the state ledger and forwards the correct resume index to
        run_simulation()."""
        mock_read_resume.return_value = 4200001

        continue_full_simulation(simulation_duration="8 hours")

        mock_read_resume.assert_called_once()
        mock_run_sim.assert_called_once_with("8 hours", start_run_idx=4200001, total_runs=TOTAL_RUNS)


    def test_build_profile_from_menu_strings(self):
        """Ensures a dictionary of strings representing strategies is correctly converted into a strategy profile
        object with corresponding strategy objects as attributes."""
        fake_strategy_dict = {
            "colors": ["RED", "GREEN"],
            "value": "LEAST_DISPARITY",
            "ruby": "SAVE",
            "flask": "FIFTY",
            "explosion_prob": "HIGH",
            "explosion_round": "ALWAYS",
            "exploded": "MONEY"
        }

        result_strategy_profile = build_profile_from_menu_strings(fake_strategy_dict)

        self.assertEqual(result_strategy_profile.colors, (ChipColor.RED, ChipColor.GREEN))
        self.assertEqual(result_strategy_profile.value, ValueStrat.LEAST_DISPARITY)
        self.assertEqual(result_strategy_profile.ruby, RubyStrat.SAVE)
        self.assertEqual(result_strategy_profile.flask, FlaskStrat.FIFTY)
        self.assertEqual(result_strategy_profile.explosion_prob, ExplosionProbabilityToleranceStrat.HIGH)
        self.assertEqual(result_strategy_profile.explosion_round, ExplosionRoundStrat.ALWAYS)
        self.assertEqual(result_strategy_profile.exploded, ExplodedStrat.MONEY)


    def test_start_custom_simulation(self):
        """Verifies that starting a custom run purges old CSV files, converts the profile, and dispatches to the
        engine."""
        fake_menu_dict = {"colors": ["RED"], "value": "FIFTY"}
        fake_matches_string = "5000"

        with (
            patch('os.path.exists') as mock_exists,
            patch('os.remove') as mock_remove,
            patch('simulation_engine.run_simulation') as mock_run_sim,
            patch('simulation_engine.build_profile_from_menu_strings') as mock_build_profile
        ):
            fake_compiled_profile = MagicMock()
            mock_build_profile.return_value = fake_compiled_profile
            mock_exists.return_value = True

            start_custom_simulation(fake_menu_dict, num_matches=fake_matches_string)

            mock_build_profile.assert_called_once_with(fake_menu_dict)
            mock_remove.assert_called_once_with(CUSTOM_SIM_RESULTS_FILE)
            mock_run_sim.assert_called_once_with(
                session_duration="Until interrupted",
                start_run_idx=0,
                total_runs=5000,
                custom_profile=fake_compiled_profile
            )

if __name__ == '__main__':
    unittest.main()