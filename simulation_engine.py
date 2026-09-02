import csv
import glob
import os
import json
import signal
import time
import queue
import threading
import multiprocessing as mp
import pyarrow as pa
import pyarrow.parquet as pq

from config.chip_config import ChipColor
from game_engine.match_runner import run_match
from models.strategy import (
    ValueStrat, RubyStrat, FlaskStrat, ExplosionProbabilityToleranceStrat, ExplosionRoundStrat,
    ExplodedStrat, GameStrategyProfile, COLOR_STRATS
)

# Global environmental storage coordinates
OUTPUT_FOLDER_DIR = "simulation_output"
FULL_SIM_DIR = os.path.join(OUTPUT_FOLDER_DIR, "full_simulation_results")
STATE_FILE_PATH = os.path.join(OUTPUT_FOLDER_DIR, "simulation_state.json")
CUSTOM_SIM_RESULTS_FILE = os.path.join(OUTPUT_FOLDER_DIR, "custom_simulation_results.csv")

RANDOM_STRATEGY_PROFILE = GameStrategyProfile(
    colors=(), value=ValueStrat.RANDOM,
    ruby=RubyStrat.RANDOM,
    flask=FlaskStrat.RANDOM,
    explosion_prob=ExplosionProbabilityToleranceStrat.RANDOM,
    explosion_round=ExplosionRoundStrat.RANDOM,
    exploded=ExplodedStrat.RANDOM
)

# Constants for strategy generation via coordinate unpacking
VALUE_OPTIONS = tuple(strat for strat in ValueStrat if strat.name != "RANDOM")
RUBY_OPTIONS = tuple (strat for strat in RubyStrat if strat.name != "RANDOM")
FLASK_OPTIONS = tuple(strat for strat in FlaskStrat if strat.name != "RANDOM")
PROB_OPTIONS = tuple(strat for strat in ExplosionProbabilityToleranceStrat if strat.name != "RANDOM")
ROUND_OPTIONS = tuple(strat for strat in ExplosionRoundStrat if strat.name != "RANDOM")
EXPLODED_OPTIONS = tuple(strat for strat in ExplodedStrat if strat.name != "RANDOM")

LEN_EXPLODED = len(EXPLODED_OPTIONS)
LEN_ROUND = len(ROUND_OPTIONS)
LEN_PROB = len(PROB_OPTIONS)
LEN_FLASK = len(FLASK_OPTIONS)
LEN_RUBY = len(RUBY_OPTIONS)
LEN_VALUE = len(VALUE_OPTIONS)

# Standard configurations
TOTAL_RUNS_PER_STRATEGY = 100 # Limit this number as there are ~1 million strategies
BATCH_SIZE = 1_000_000

TOTAL_STRATEGIES = (
    len(COLOR_STRATS) * len(VALUE_OPTIONS) * len(RUBY_OPTIONS) * len(FLASK_OPTIONS) * len(PROB_OPTIONS)
    * len(ROUND_OPTIONS) * len(EXPLODED_OPTIONS)
)
TOTAL_RUNS = TOTAL_RUNS_PER_STRATEGY * TOTAL_STRATEGIES


# Global thread-safety controls
shutdown_requested = False

def handle_signal(_signum, _frame) -> None:
    """Changes the global flag when ctrl+C is pressed."""
    global shutdown_requested
    print("\n[INFO] Shutdown requested - Completing currently running simulations and saving data. Please do not turn"
          "off your computer.")
    shutdown_requested = True


def format_time(seconds: int) -> str:
    """Converts float of seconds into more readable string format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"

    return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m"


def update_resume_point(completed_run_id: int) -> None:
    """Updates the state file with the next run ID that should be used to continue the simulation."""
    os.makedirs(OUTPUT_FOLDER_DIR, exist_ok=True)
    state_data = {
        "last_completed_run_id": completed_run_id,
        "next_run_id": completed_run_id + 1,
        "last_updated_timestamp": time.time()
    }

    # Protection against corruption of the actual file
    temp_state_path = STATE_FILE_PATH + ".tmp"
    with open(temp_state_path, "w", encoding="utf-8") as f:
        json.dump(state_data, f, indent=4)
    os.replace(temp_state_path, STATE_FILE_PATH)


def generate_strategy_by_index(strategy_index: int) -> GameStrategyProfile:
    """Generates the next strategy to simulate based on the given strategy index."""
    # Multi-dimensional remainder math unpacking
    strategy_index, exploded_idx = divmod(strategy_index, LEN_EXPLODED)
    strategy_index, round_idx = divmod(strategy_index, LEN_ROUND)
    strategy_index, prob_idx = divmod(strategy_index, LEN_PROB)
    strategy_index, flask_idx = divmod(strategy_index, LEN_FLASK)
    strategy_index, ruby_idx = divmod(strategy_index, LEN_RUBY)
    color_idx, value_idx = divmod(strategy_index, LEN_VALUE)

    return GameStrategyProfile(
        colors=COLOR_STRATS[color_idx],
        value=VALUE_OPTIONS[value_idx], # type: ignore
        ruby=RUBY_OPTIONS[ruby_idx], # type: ignore
        flask=FLASK_OPTIONS[flask_idx], # type: ignore
        explosion_prob=PROB_OPTIONS[prob_idx], # type: ignore
        explosion_round=ROUND_OPTIONS[round_idx], # type: ignore
        exploded=EXPLODED_OPTIONS[exploded_idx] # type: ignore
    )


def simulation_worker(global_run_counter, global_queue: mp.Queue, shutdown_event: mp.Event,
                      custom_profile: GameStrategyProfile | None=None, total_runs: int=TOTAL_RUNS) -> None:
    """Runs simulation in a separate process."""
    while not shutdown_event.is_set():
        # Obtain and increment the global run counter
        with global_run_counter.get_lock():
            start_run_index = global_run_counter.value
            if start_run_index >= total_runs:
                break
            global_run_counter.value += TOTAL_RUNS_PER_STRATEGY

        # Select a strategy to simulate
        if custom_profile is not None:
            current_strategy = custom_profile
        else:
            strategy_index = start_run_index // TOTAL_RUNS_PER_STRATEGY
            current_strategy = generate_strategy_by_index(strategy_index)

        # Run simulated matches
        for offset in range(TOTAL_RUNS_PER_STRATEGY):
            current_match_index = start_run_index + offset
            result = run_match(strat_prof_a=current_strategy, strat_prof_b=RANDOM_STRATEGY_PROFILE)

            # Inject the run id tag into the output
            result["run_id"] = current_match_index + 1
            global_queue.put(result)

    global_queue.put(None)  # None signals to the writer thread that the worker has finished


def print_performance_dashboard(current_run_id: int, batch_duration: float, total_runs: int=TOTAL_RUNS) -> None:
    """Calculates continuous telemetry metrics and prints progress."""
    runs_remaining = total_runs - current_run_id
    runs_per_second = BATCH_SIZE / max(batch_duration, 0.001)
    eta_seconds = int(runs_remaining // runs_per_second)
    percent = (current_run_id / total_runs) * 100

    print(f"\n--- Simulation Odometer Progress ---")
    print(f"Completion Gauge  : {percent:.1f}%")
    print(f"Last Saved Run ID : {current_run_id:,} / {total_runs:,}")
    print(f"Simulation speed  : {int(runs_per_second):,} games/s")
    print(f"Time remaining    : {format_time(eta_seconds)}")
    print(f"------------------------------------")


def write_batch_to_parquet(batch_container: list) -> None:
    """Writes a list to a parquet file."""
    schema = pa.RecordBatch.from_pylist(mapping=batch_container).schema  # type: ignore

    os.makedirs(FULL_SIM_DIR, exist_ok=True)

    session_file = os.path.join(FULL_SIM_DIR, f"chunk_start_{batch_container[0]['run_id']}.parquet")
    with (pq.ParquetWriter(session_file, schema, compression='snappy')) as writer:
        batch_container.sort(key=lambda x: x["run_id"])
        table = pa.Table.from_pylist(batch_container, schema)
        writer.write_table(table)


def full_sim_results_writer(global_queue: mp.Queue, num_workers: int) -> None:
    """Consumer thread that coordinates pulling from queue and writing to a parquet file."""
    active_workers = num_workers
    batch_container = []
    batch_start_time = time.time()
    while active_workers > 0 or not global_queue.empty():
        try:
            next_row = global_queue.get(timeout=0.5)
            if next_row is None:
                active_workers -= 1
                continue

            batch_container.append(next_row)

        except queue.Empty:
            continue

        if len(batch_container) >= BATCH_SIZE:
            write_batch_to_parquet(batch_container)
            update_resume_point(batch_container[-1]["run_id"])
            print_performance_dashboard(batch_container[-1]["run_id"], time.time() - batch_start_time)
            batch_container.clear()
            batch_start_time = time.time()

    # Straggler cleanup
    if batch_container:
        write_batch_to_parquet(batch_container)
        update_resume_point(batch_container[-1]["run_id"])
        print_performance_dashboard(batch_container[-1]["run_id"], time.time() - batch_start_time)
        batch_container.clear()


def custom_sim_results_writer(global_queue: mp.Queue, num_workers: int) -> None:
    """Consumer that writes data from the queue to a csv file."""
    active_workers = num_workers
    batch_container = []

    while active_workers > 0 or not global_queue.empty():
        try:
            next_row = global_queue.get(timeout=0.5)
            if next_row is None:
                active_workers -= 1
                continue

            batch_container.append(next_row)

        except queue.Empty:
            continue

    if batch_container:
        batch_container.sort(key=lambda x: x["run_id"])
        print(f"[INFO] Writing {len(batch_container):,} sorted rows to CSV...")

        os.makedirs(OUTPUT_FOLDER_DIR, exist_ok=True)

        with open(CUSTOM_SIM_RESULTS_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=batch_container[0].keys())
            writer.writeheader()
            writer.writerows(batch_container)

        print(f"[INFO] Custom simulation dataset written to: {CUSTOM_SIM_RESULTS_FILE}")
        batch_container.clear()


def convert_duration_to_seconds(session_duration: str) -> int | None:
    """Converts the user's duration selection from a string to a number or None."""
    duration_options = {
        "1 hour": 3600,
        "2 hours": 7200,
        "4 hours": 14400,
        "8 hours": 28800,
        "12 hours": 43200,
        "Until interrupted": None
    }

    return duration_options[session_duration]


def run_simulation(session_duration: str, start_run_idx: int=0, custom_profile: GameStrategyProfile | None=None,
                   total_runs: int=TOTAL_RUNS) -> None:
    """Runs a complete simulation using every combination of strategies."""
    max_seconds = convert_duration_to_seconds(session_duration)
    session_start_time = time.time()

    # Initialize shared thread-safe communication structures
    global_run_counter = mp.Value('i', start_run_idx)
    num_workers = max(1, mp.cpu_count() -1)
    global_queue = mp.Queue(maxsize=50_000)
    shutdown_event = mp.Event()

    # Set up interrupt handling
    def local_interrupt_handler(_signum, _frame) -> None:
        print("\n[INFO] Initiating shutdown. Please do not turn off your computer.")
        shutdown_event.set()

    signal.signal(signal.SIGINT, local_interrupt_handler)

    # Initialize writer
    if custom_profile is not None:
        writer_thread = threading.Thread(
            target=custom_sim_results_writer,
            args=(global_queue, num_workers)
        )
    else:
        writer_thread = threading.Thread(
            target=full_sim_results_writer,
            args=(global_queue, num_workers)
        )

    writer_thread.start()

    # Initialize workers
    worker_pool = []
    for _ in range(num_workers):
        p = mp.Process(
            target=simulation_worker,
            args=(global_run_counter, global_queue, shutdown_event, custom_profile, total_runs)
        )
        worker_pool.append(p)
        p.start()

    # Session shutdown monitoring
    try:
        while (any(p.is_alive() for p in worker_pool) or writer_thread.is_alive()) and not shutdown_event.is_set():
            time.sleep(0.5) # Free up compute power for other tasks
            # Session duration check
            if max_seconds is not None:
                if (time.time() - session_start_time) >= max_seconds:
                    print(f"[INFO] Session limit of {format_time(max_seconds)} reached. Initiating shutdown. Please "
                          f"do not turn off your computer.")
                    shutdown_event.set()

    except KeyboardInterrupt:
        print("\n[INTERRUPT] Keyboard interrupt detected.")
        shutdown_event.set()

    # Closing sequence
    for p in worker_pool:
        p.join()
    writer_thread.join()
    print("[INFO] All parallel processes safely decommissioned.")


def read_resume_point() -> int:
    """Checks the state file and returns the resume point."""
    try:
        with open(STATE_FILE_PATH, "r", encoding="utf-8") as f:
            state_data = json.load(f)
            return int(state_data.get("next_run_id", 0))
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def start_full_simulation(simulation_duration: str) -> None:
    """Entry point handler that starts a fresh simulation from row 0."""
    # Remove old state file
    if os.path.exists(STATE_FILE_PATH):
        os.remove(STATE_FILE_PATH)

    # Remove old parquet files
    parquet_pattern = os.path.join(FULL_SIM_DIR, "*.parquet")
    for file_path in glob.glob(parquet_pattern):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"[WARNING Could not clear old file {file_path}: {e}")
    print("[INFO] Output directory sanitized. Starting clean simulation.")

    run_simulation(simulation_duration, start_run_idx=0, total_runs=TOTAL_RUNS)


def continue_full_simulation(simulation_duration: str) -> None:
    """Entry point handler that reads state and resumes the simulation."""
    resume_point_run_id = read_resume_point()
    print(f"[INFO] Resuming processing beginning with run ID {resume_point_run_id:,}")
    run_simulation(simulation_duration, start_run_idx=resume_point_run_id, total_runs=TOTAL_RUNS)


def build_profile_from_menu_strings(strategy_dictionary: dict) -> GameStrategyProfile:
    """Translate the user's game strategy profile menu choices from strings to a GameStrategyProfile object."""
    chip_color_objects = tuple(ChipColor[color] for color in strategy_dictionary["colors"])

    strategy_profile = GameStrategyProfile(
        colors=chip_color_objects, # type: ignore
        value=ValueStrat[strategy_dictionary["value"]], # type: ignore
        ruby=RubyStrat[strategy_dictionary["ruby"]], # type: ignore
        flask=FlaskStrat[strategy_dictionary["flask"]], # type: ignore
        explosion_prob=ExplosionProbabilityToleranceStrat[strategy_dictionary["explosion_prob"]], # type: ignore
        explosion_round=ExplosionRoundStrat[strategy_dictionary["explosion_round"]], # type: ignore
        exploded=ExplodedStrat[strategy_dictionary["exploded"]] # type: ignore
    )

    return strategy_profile


def start_custom_simulation(strategy_profile: dict, num_matches: str):
    """Runs a limited simulation using custom parameters supplied by the user."""
    total_custom_runs = int(num_matches)
    custom_profile = build_profile_from_menu_strings(strategy_profile)

    if os.path.exists(CUSTOM_SIM_RESULTS_FILE):
        os.remove(CUSTOM_SIM_RESULTS_FILE)

    run_simulation(
        session_duration="Until interrupted",
        start_run_idx=0,
        total_runs=total_custom_runs,
        custom_profile=custom_profile
    )
