import glob
import os
import shutil
import unittest

import pyarrow.parquet as pq

from game_engine.match_runner import run_match
from models.strategy import GameStrategyProfile, ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, \
    ExplosionRoundStrat, ExplodedStrat
from simulation_engine import run_simulation, FULL_SIM_DIR, STATE_FILE_PATH, OUTPUT_FOLDER_DIR, BATCH_SIZE


class TestSystemIntegrationAndAccuracy(unittest.TestCase):

    def setUp(self):
        self.test_root = "integration_test_output"
        self.test_data_dir = os.path.join(self.test_root, "full_simulation_data")
        self.test_state_file = os.path.join(self.test_root, "simulation_state.json")

        self.orig_root = OUTPUT_FOLDER_DIR
        self.orig_dir = FULL_SIM_DIR
        self.orig_state = STATE_FILE_PATH
        self.orig_batch_size = BATCH_SIZE

        import simulation_engine
        simulation_engine.OUTPUT_FOLDER_DIR = self.test_root
        simulation_engine.FULL_SIM_DIR = self.test_data_dir
        simulation_engine.STATE_FILE_PATH = self.test_state_file

        os.makedirs(self.test_data_dir, exist_ok=True)


    def tearDown(self):
        """Clean up and delete all physical test files generated during the integration runs."""
        if os.path.exists(self.test_root):
            shutil.rmtree(self.test_root)

        import simulation_engine
        simulation_engine.OUTPUT_ROOT_PATH = self.orig_root
        simulation_engine.FULL_SIM_DIR = self.orig_dir
        simulation_engine.STATE_FILE_PATH = self.orig_state
        simulation_engine.BATCH_SIZE = self.orig_batch_size


    def test_end_to_end_multiprocess_pipeline(self):
        """Verify that the real multiprocess pipeline spawns cores, handles queues, and writes valid Parquet chunks."""
        import simulation_engine

        simulation_engine.BATCH_SIZE = 500

        run_simulation(
            session_duration="1 hour",
            start_run_idx=0,
            total_runs=1100,
            custom_profile=None
        )

        # Verify parquet files were written
        parquet_files = glob.glob(os.path.join(self.test_data_dir, "*.parquet"))
        self.assertTrue(len(parquet_files) >= 2, f"Expected sharded parquet files, found: {parquet_files}")

        # Verify rows and columns written correctly
        dataset = pq.read_table(self.test_data_dir)
        df = dataset.to_pandas()
        self.assertIn("run_id", df.columns)
        self.assertEqual(len(df), 1100, f"Expected exactly 1100 processed rows, got {len(df)}")

        # Verify 1-index key transformation
        self.assertEqual(df["run_id"].min(), 1)
        self.assertEqual(df["run_id"].max(), 1100)


    def test_single_match_game_rules_accuracy(self):
        """Verify that a single full game match calculates scoring parameters with 100% rules compliance."""
        test_strategy = GameStrategyProfile(
            colors=(),
            value=ValueStrat.HIGHEST_SINGLE_VALUE,
            ruby=RubyStrat.SAVE,
            flask=FlaskStrat.FIFTY,
            explosion_prob=ExplosionProbabilityToleranceStrat.NEVER,
            explosion_round=ExplosionRoundStrat.ALWAYS,
            exploded=ExplodedStrat.POINTS
        )

        result = run_match(strat_prof_a=test_strategy, strat_prof_b=test_strategy)

        expected_metrics = ["player_a_vp", "player_b_vp", "explosion_count"]

        for metric in expected_metrics:
            self.assertIn(metric, result, f"Missing column: {metric}")
        self.assertGreaterEqual(result["player_a_vp"], 0)
        self.assertLessEqual(result["player_b_vp"], 150)
        self.assertLessEqual(result["explosion_count"], 0, "Strategy rules allowed excessive explosions. ")


if __name__ == '__main__':
    unittest.main()