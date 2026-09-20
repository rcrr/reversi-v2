#
# test_state_machine.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi
# 
# Author Roberto Corradini mailto:rob_corradini@yahoo.it
# Copyright 2026 Roberto Corradini. All rights reserved.
#
# License
# 
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

#
#
# How to use the unit tests state_machine module.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest reversi.test.test_state_machine
#

import unittest

from contextlib import redirect_stdout
from dataclasses import asdict, FrozenInstanceError
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from io import StringIO
from datetime import datetime, timezone, timedelta

from reversi.tools.state_machine import StateMachine, Worker, Context, Relevance, Verbosity

# House rule: test artifacts are written ONLY under
# workspace_root/build/tmp and removed afterwards. The workspace
# root is 3 levels up from this file (src/reversi/test/).
TMP_DIR = Path(__file__).resolve().parents[3] / "build" / "tmp"



class TestStateMachine(unittest.TestCase):
    """Test suite for the generic StateMachine infrastructure."""

    def setUp(self):
        """Set up a fresh state machine with 3 mock workers and patch stdout."""
        # Patch stdout globally for all tests in this class to keep output clean
        self.patcher = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher.start()

        self.context = Context()
        
        # Create mock callables for up and down
        self.up_callables = [MagicMock() for _ in range(3)]
        self.down_callables = [MagicMock() for _ in range(3)]
        
        self.workers = [
            Worker("CREATED", self.up_callables[0], self.down_callables[0]),
            Worker("CONFIG", self.up_callables[1], self.down_callables[1]),
            Worker("POSITIONS", self.up_callables[2], self.down_callables[2])
        ]
        
        self.sm = StateMachine(self.workers, self.context)

    def tearDown(self):
        """Stop patching stdout."""
        self.patcher.stop()

    def test_initialization(self):
        """Test that the state machine initializes correctly at step 0."""
        self.assertEqual(self.sm.current_step, 0)
        self.assertEqual(self.sm.current_worker_name, "CREATED")
        self.assertEqual(len(self.sm.workers), 3)
        self.assertEqual(len(self.sm.logs), 1)  # The init debug log

    def test_move_up_single_step(self):
        """Test moving up a single step."""
        self.sm.move_to_step(1)
        
        self.assertEqual(self.sm.current_step, 1)
        self.up_callables[1].assert_called_once_with(self.context)
        self.down_callables[1].assert_not_called()
        self.assertEqual(len(self.sm.history), 1)
        self.assertEqual(self.sm.history[0].direction, 'up')

    def test_move_up_multiple_steps(self):
        """Test moving up multiple steps in one call."""
        self.sm.move_to_step(2)
        
        self.assertEqual(self.sm.current_step, 2)
        self.up_callables[1].assert_called_once_with(self.context)
        self.up_callables[2].assert_called_once_with(self.context)
        self.down_callables[1].assert_not_called()
        self.down_callables[2].assert_not_called()
        self.assertEqual(len(self.sm.history), 2)

    def test_move_down_single_step(self):
        """Test moving down a single step."""
        # First go up to step 2
        self.sm.move_to_step(2)
        # Reset mocks to only observe the downward movement
        for mock in self.up_callables + self.down_callables:
            mock.reset_mock()
            
        self.sm.move_to_step(1)
        
        self.assertEqual(self.sm.current_step, 1)
        self.down_callables[2].assert_called_once_with(self.context)
        self.up_callables[2].assert_not_called()
        self.assertEqual(len(self.sm.history), 3)
        self.assertEqual(self.sm.history[-1].direction, 'down')

    def test_move_down_to_zero(self):
        """Test moving down to the first step (index 0)."""
        self.sm.move_to_step(2)
        for mock in self.up_callables + self.down_callables:
            mock.reset_mock()
            
        self.sm.move_to_step(0)
        
        self.assertEqual(self.sm.current_step, 0)
        self.down_callables[2].assert_called_once_with(self.context)
        self.down_callables[1].assert_called_once_with(self.context)
        self.assertEqual(len(self.sm.history), 4)

    def test_move_to_same_step(self):
        """Test that moving to the current step does nothing."""
        self.sm.move_to_step(0)
        
        self.assertEqual(self.sm.current_step, 0)
        for mock in self.up_callables + self.down_callables:
            mock.assert_not_called()
        self.assertEqual(len(self.sm.history), 0)

    def test_move_to_last_happy_path(self):
        """move_to_last dispatches by the last worker's name and
        runs the up chain."""
        self.sm.move_to_last()

        self.assertEqual(self.sm.current_step, 2)
        self.up_callables[1].assert_called_once_with(self.context)
        self.up_callables[2].assert_called_once_with(self.context)
        for mock in self.down_callables:
            mock.assert_not_called()
        self.assertEqual(len(self.sm.history), 2)
        self.assertEqual(self.sm.history[-1].direction, 'up')

    def test_move_to_last_from_intermediate_position(self):
        """From step 1, only the remaining step executes."""
        self.sm.move_to_step(1)
        for mock in self.up_callables + self.down_callables:
            mock.reset_mock()

        self.sm.move_to_last()

        self.assertEqual(self.sm.current_step, 2)
        self.up_callables[2].assert_called_once_with(self.context)
        self.up_callables[1].assert_not_called()  # already executed
        self.assertEqual(len(self.sm.history), 2)  # step 1 up + step 2 up

    def test_move_to_last_single_worker_noop(self):
        """A single-worker machine: the only worker is the sentinel
        at step 0, so move_to_last is a no-op."""
        up = MagicMock()
        down = MagicMock()
        sm = StateMachine([Worker("ONLY", up, down)], Context())
        sm.move_to_last()
        up.assert_not_called()
        down.assert_not_called()
        self.assertEqual(sm.current_step, 0)
        self.assertEqual(sm.history, [])

    def test_duplicate_worker_names_raise(self):
        """Duplicate names are rejected at construction."""
        with self.assertRaises(ValueError) as ctx:
            StateMachine([
                Worker("A", MagicMock(), MagicMock()),
                Worker("B", MagicMock(), MagicMock()),
                Worker("A", MagicMock(), MagicMock()),
            ], Context())
        self.assertIn("Duplicate worker name", str(ctx.exception))

    def test_duplicate_worker_names_case_insensitive(self):
        """'CONFIG' and 'config' are the same name for moves."""
        with self.assertRaises(ValueError):
            StateMachine([
                Worker("CONFIG", MagicMock(), MagicMock()),
                Worker("config", MagicMock(), MagicMock()),
            ], Context())

    def test_retry_after_failure_skips_failed_step(self):
        """A retry of a higher target does NOT re-execute the
        failed step; recovery is down-then-up."""
        self.up_callables[1].side_effect = RuntimeError("boom")
        with self.assertRaises(RuntimeError):
            self.sm.move_to_step(2)
        self.assertEqual(self.sm.current_step, 1)
        # clear the failure and retry the same target
        self.up_callables[1].side_effect = None
        for mock in self.up_callables + self.down_callables:
            mock.reset_mock()
        self.sm.move_to_step(2)
        self.up_callables[2].assert_called_once_with(self.context)
        self.up_callables[1].assert_not_called()  # skipped
        self.assertEqual(self.sm.current_step, 2)
        # recovery: roll back (runs down of 2 and the failed 1) ...
        for mock in self.up_callables + self.down_callables:
            mock.reset_mock()
        self.sm.move_to_step(0)
        self.down_callables[2].assert_called_once_with(self.context)
        self.down_callables[1].assert_called_once_with(self.context)
        # ... then move up: the failed step 1 re-executes
        self.sm.move_to_step(2)
        self.up_callables[1].assert_called_once_with(self.context)
        self.up_callables[2].assert_called_once_with(self.context)
        self.assertEqual(self.sm.current_step, 2)

    def test_worker_zero_is_sentinel_never_executed(self):
        """Worker 0 is the sentinel initial state: its up()/down()
        are never invoked by the machine."""
        self.sm.move_to_step(2)
        self.up_callables[0].assert_not_called()
        self.down_callables[0].assert_not_called()
        for mock in self.up_callables + self.down_callables:
            mock.reset_mock()
        self.sm.move_to_step(0)
        self.up_callables[0].assert_not_called()
        self.down_callables[0].assert_not_called()

    def test_move_to_step_by_string(self):
        """Test moving to a step using the worker's name (case-insensitive)."""
        self.sm.move_to_step("positions")
        
        self.assertEqual(self.sm.current_step, 2)
        self.up_callables[1].assert_called_once_with(self.context)
        self.up_callables[2].assert_called_once_with(self.context)

    def test_move_to_step_by_invalid_string(self):
        """Test that providing an invalid string name raises ValueError.

        probe_rules.md §4: pins the FULL message, converted from
        the verify_wrk_config.py E2 probe (the re-pinned guard
        contract)."""
        with self.assertRaises(ValueError) as context:
            self.sm.move_to_step("NON_EXISTENT_WORKER")

        self.assertEqual(str(context.exception),
                         "Worker 'NON_EXISTENT_WORKER' not found in the pipeline.")

    def test_move_to_step_out_of_bounds_high(self):
        """Test that providing an index >= len(workers) raises IndexError.

        probe_rules.md §4: pins the FULL message, converted from
        the verify_wrk_config.py E3 probe (the re-pinned guard
        contract)."""
        with self.assertRaises(IndexError) as context:
            self.sm.move_to_step(3)

        self.assertEqual(str(context.exception), "Target step 3 is out of bounds.")

    def test_move_to_step_out_of_bounds_negative(self):
        """Test that providing a negative index raises IndexError."""
        with self.assertRaises(IndexError):
            self.sm.move_to_step(-1)

    def test_move_to_step_invalid_type(self):
        """Test that providing an invalid type raises TypeError."""
        with self.assertRaises(TypeError):
            self.sm.move_to_step(3.14)

    def test_worker_exception_propagation_and_logging(self):
        """Test that exceptions in workers are logged and re-raised."""
        # Make the 'up' callable of step 1 raise an exception
        self.up_callables[1].side_effect = RuntimeError("Simulated computation failure")
        
        with self.assertRaises(RuntimeError):
            self.sm.move_to_step(2)
            
        # The state machine should still be at step 1 because step 1 failed during execution
        self.assertEqual(self.sm.current_step, 1)
        
        # Check that an error log was generated (the typed record)
        error_logs = [log for log in self.sm.logs if log.relevance == Relevance.ERROR]
        self.assertEqual(len(error_logs), 1)
        self.assertIn("Simulated computation failure", error_logs[0].message)
        self.assertEqual(error_logs[0].worker_name, "CONFIG")
        self.assertEqual(error_logs[0].step, 1)
        
        # History should still record the attempted move
        self.assertEqual(len(self.sm.history), 1)
        self.assertEqual(self.sm.history[0].worker_name, "CONFIG")

    def test_bool_rejected_as_int_step(self):
        """bool is NOT a valid step: True/False raise
        TypeError (the strict gate rejects bool, which a bare
        isinstance(..., int) would have accepted) and the machine
        stays untouched."""
        for bad in (True, False):
            with self.assertRaises(TypeError) as ctx:
                self.sm.move_to_step(bad)
            self.assertIn("integer index or a string worker name",
                          str(ctx.exception))
        self.assertEqual(self.sm.current_step, 0)
        self.assertEqual(len(self.sm.history), 0)
        self.assertEqual(len(self.sm.logs), 1)  # init log only

    def test_numpy_int64_rejected(self):
        """np.int64 is NOT a Python int subclass: TypeError (V7)."""
        import numpy as np
        with self.assertRaises(TypeError) as ctx:
            self.sm.move_to_step(np.int64(1))
        self.assertIn("integer index or a string worker name",
                      str(ctx.exception))

    def test_constructor_rejects_non_worker_entry(self):
        """__init__ is @validate_call: a non-Worker
        list entry raises pydantic ValidationError instead of a raw
        AttributeError deep in the name check."""
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            StateMachine([42], Context())

    def test_constructor_rejects_non_context(self):
        """__init__ is @validate_call: a non-Context
        object raises ValidationError; Context subclasses still
        pass."""
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            StateMachine([Worker("A", MagicMock(), MagicMock())], 42)

        class LMContext(Context):
            pass
        sm = StateMachine([Worker("A", MagicMock(), MagicMock())],
                          LMContext())
        self.assertIsInstance(sm.context, LMContext)

    def test_current_worker_name_tracks_current_step(self):
        """current_worker_name is a live view of (workers,
        current_step)."""
        self.assertEqual(self.sm.current_worker_name, "CREATED")
        self.sm.move_to_step(1)
        self.assertEqual(self.sm.current_worker_name, "CONFIG")
        self.sm.move_to_step(2)
        self.assertEqual(self.sm.current_worker_name, "POSITIONS")
        self.sm.move_to_step(0)
        self.assertEqual(self.sm.current_worker_name, "CREATED")

    def test_current_worker_name_empty_workers_undefined(self):
        """With no workers the name is 'UNDEFINED'."""
        sm = StateMachine([], Context())
        self.assertEqual(sm.current_worker_name, "UNDEFINED")

    def test_step_move_fields_up(self):
        """StepMove field content for up moves:
        aware-UTC start/finish and duration == finish - start."""
        self.sm.move_to_step(2)
        expected = [(1, "CONFIG", "up"), (2, "POSITIONS", "up")]
        for entry, (step, name, direction) in zip(
                self.sm.history, expected):
            self.assertEqual(entry.step, step)
            self.assertEqual(entry.worker_name, name)
            self.assertEqual(entry.direction, direction)
            self.assertIsInstance(entry.start, datetime)
            self.assertIsInstance(entry.finish, datetime)
            self.assertIsNotNone(entry.start.tzinfo)
            self.assertIsNotNone(entry.finish.tzinfo)
            self.assertEqual(entry.start.utcoffset(), timedelta(0))
            self.assertEqual(entry.finish.utcoffset(), timedelta(0))
            self.assertGreaterEqual(entry.finish, entry.start)
            self.assertEqual(entry.duration, entry.finish - entry.start)

    def test_step_move_fields_down(self):
        """StepMove field content for down moves: the target is
        excluded, so the last entry is the step above it."""
        self.sm.move_to_step(2)
        self.sm.move_to_step(0)
        tail = self.sm.history[2:]
        self.assertEqual(
            [(e.step, e.worker_name, e.direction) for e in tail],
            [(2, "POSITIONS", "down"), (1, "CONFIG", "down")])
        for e in tail:
            self.assertEqual(e.duration, e.finish - e.start)

    def test_step_move_recorded_on_failure(self):
        """A failed step is still recorded (the timer's finally) —
        pinning the field content, not just the len."""
        self.up_callables[1].side_effect = RuntimeError("boom")
        with self.assertRaises(RuntimeError):
            self.sm.move_to_step(2)
        self.assertEqual(len(self.sm.history), 1)
        e = self.sm.history[0]
        self.assertEqual(e.step, 1)
        self.assertEqual(e.worker_name, "CONFIG")
        self.assertEqual(e.direction, "up")
        self.assertIsNotNone(e.finish.tzinfo)
        self.assertEqual(e.duration, e.finish - e.start)

    def test_history_export_csv(self):
        """Test exporting history to a CSV file: header
        names, ISO-8601 +00:00 timestamps, duration identity, and the
        artifact under workspace_root/build/tmp, removed afterwards."""
        import csv

        self.sm.move_to_step(2)
        self.sm.move_to_step(0)

        TMP_DIR.mkdir(parents=True, exist_ok=True)
        test_filename = TMP_DIR / "test_history_export.csv"
        try:
            self.sm.export_history_of_moves_as_csv(test_filename)

            self.assertTrue(test_filename.exists())

            with open(test_filename, "r") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                rows = list(reader)

            # header row: the exact field names
            self.assertEqual(fieldnames, [
                "step", "worker_name", "direction",
                "start_utc", "finish_utc", "duration_sec"])

            # We made 2 move_to_step calls, resulting in 4 individual steps
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]['step'], "1")
            self.assertEqual(rows[0]['worker_name'], "CONFIG")
            self.assertEqual(rows[0]['direction'], "up")
            # When moving down to 0, the last worker to execute 'down' is step 1 (CONFIG)
            self.assertEqual(rows[3]['step'], "1")
            self.assertEqual(rows[3]['worker_name'], "CONFIG")
            self.assertEqual(rows[3]['direction'], "down")
            for row in rows:
                # ISO-8601 with explicit +00:00 (aware UTC)
                self.assertTrue(row['start_utc'].endswith("+00:00"))
                self.assertTrue(row['finish_utc'].endswith("+00:00"))
                start = datetime.fromisoformat(row['start_utc'])
                finish = datetime.fromisoformat(row['finish_utc'])
                self.assertIsNotNone(start.tzinfo)
                self.assertIsNotNone(finish.tzinfo)
                # duration_sec == finish - start (the dataclass identity)
                self.assertAlmostEqual(
                    float(row['duration_sec']),
                    (finish - start).total_seconds(),
                    places=6)
        finally:
            if test_filename.exists():
                test_filename.unlink()

    def test_run_step_rejects_unknown_direction(self):
        """The direction dispatch is explicit: only 'up' and 'down'
        are valid; anything else raises ValueError without executing
        the worker."""
        with self.assertRaises(ValueError) as ctx:
            self.sm._run_step(self.workers[1], "sideways")
        self.assertIn("sideways", str(ctx.exception))
        self.up_callables[1].assert_not_called()
        self.down_callables[1].assert_not_called()

    def test_worker_repr(self):
        """Worker's repr shows the name."""
        self.assertEqual(repr(self.workers[1]), "Worker('CONFIG')")

    def test_state_machine_repr_tracks_state(self):
        """StateMachine's repr is lightweight (no context, no logs,
        no history) and tracks the current step."""
        self.assertEqual(
            repr(self.sm),
            "StateMachine(workers=3, current_step=0, "
            "verbosity=STANDARD)")
        self.sm.move_to_step(2)
        self.assertEqual(
            repr(self.sm),
            "StateMachine(workers=3, current_step=2, "
            "verbosity=STANDARD)")
        # a custom verbosity is reflected by name
        sm = StateMachine(
            [Worker("A", MagicMock(), MagicMock())],
            Context(), Verbosity.NONE)
        self.assertEqual(
            repr(sm),
            "StateMachine(workers=1, current_step=0, verbosity=NONE)")

    def test_csv_export_creates_missing_parent_dirs(self):
        """Missing parent directories are created; the
        artifact stays under workspace_root/build/tmp and is removed
        afterwards (house rule)."""
        self.sm.move_to_step(1)

        TMP_DIR.mkdir(parents=True, exist_ok=True)
        nested_dir = TMP_DIR / "nested" / "deeper"
        csv_path = nested_dir / "history.csv"
        try:
            self.assertFalse(csv_path.parent.exists())
            self.sm.export_history_of_moves_as_csv(csv_path)
            self.assertTrue(csv_path.is_file())
            with open(csv_path) as f:
                lines = f.read().splitlines()
            self.assertEqual(
                lines[0],
                "step,worker_name,direction,start_utc,"
                "finish_utc,duration_sec")
            self.assertEqual(len(lines), 2)  # header + the 1 executed step
        finally:
            csv_path.unlink(missing_ok=True)
            if nested_dir.exists():
                nested_dir.rmdir()
                nested_dir.parent.rmdir()


class TestLogEntry(unittest.TestCase):
    """Log records are typed frozen dataclasses."""

    def setUp(self):
        """Fresh machine (3 workers); the init log is logs[0]."""
        self.patcher = patch('sys.stdout', new=StringIO())
        self.patcher.start()
        self.context = Context()
        self.up_callables = [MagicMock() for _ in range(3)]
        self.down_callables = [MagicMock() for _ in range(3)]
        self.workers = [
            Worker("CREATED", self.up_callables[0], self.down_callables[0]),
            Worker("CONFIG", self.up_callables[1], self.down_callables[1]),
            Worker("POSITIONS", self.up_callables[2], self.down_callables[2])
        ]
        self.sm = StateMachine(self.workers, self.context)

    def tearDown(self):
        self.patcher.stop()

    def test_init_log_is_typed_record(self):
        """logs[0] is a LogEntry with the 5 expected field values."""
        entry = self.sm.logs[0]
        self.assertIsInstance(entry, StateMachine.LogEntry)
        self.assertIsInstance(entry.time, datetime)
        self.assertEqual(entry.step, 0)
        self.assertEqual(entry.worker_name, "CREATED")
        self.assertEqual(entry.relevance, Relevance.DEBUG)
        self.assertEqual(entry.message, "StateMachine initialized.")

    def test_log_entry_is_immutable(self):
        """Frozen dataclass: mutating a field raises."""
        entry = self.sm.logs[0]
        with self.assertRaises(FrozenInstanceError):
            entry.message = "tampered"

    def test_asdict_form_for_dump(self):
        """dataclasses.asdict() yields the 5-key dict (file/DB dump)."""
        entry = self.sm.logs[0]
        as_dict = asdict(entry)
        self.assertEqual(
            set(as_dict),
            {"time", "step", "worker_name", "relevance", "message"})


class TestVerbosityGating(unittest.TestCase):
    """Pins the `relevance >= verbosity` print gate."""

    EXPECTED_PRINTING = {
        Verbosity.HIGH: {
            Relevance.TRACE, Relevance.DEBUG, Relevance.INFO,
            Relevance.WARN, Relevance.ERROR},
        Verbosity.MODERATE: {
            Relevance.DEBUG, Relevance.INFO, Relevance.WARN,
            Relevance.ERROR},
        Verbosity.STANDARD: {
            Relevance.INFO, Relevance.WARN, Relevance.ERROR},
        Verbosity.LOW: {Relevance.WARN, Relevance.ERROR},
        Verbosity.VERY_LOW: {Relevance.ERROR},
        Verbosity.NONE: set(),
    }

    def setUp(self):
        """Patch stdout to keep the init log line out of the test output."""
        self.patcher = patch('sys.stdout', new=StringIO())
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()

    def test_gating_matrix(self):
        """All 6 verbosity levels x 5 relevance levels: print iff >=."""
        for verbosity, printing in self.EXPECTED_PRINTING.items():
            for relevance in Relevance:
                machine = StateMachine(
                    [Worker("A", MagicMock(), MagicMock())],
                    Context(), verbosity)
                buffer = StringIO()
                with redirect_stdout(buffer):
                    machine.log_event(relevance, "probe")
                did_print = buffer.getvalue() != ""
                self.assertEqual(
                    did_print, relevance in printing,
                    f"{verbosity.name}/{relevance.name}")
                # logs accumulate even when nothing is printed
                self.assertEqual(len(machine.logs), 2)

    def test_enum_values(self):
        """Level values, incl. the two lowest: VERY_LOW = 4, NONE = 5."""
        self.assertEqual(Verbosity.HIGH, 0)
        self.assertEqual(Verbosity.MODERATE, 1)
        self.assertEqual(Verbosity.STANDARD, 2)
        self.assertEqual(Verbosity.LOW, 3)
        self.assertEqual(Verbosity.VERY_LOW, 4)
        self.assertEqual(Verbosity.NONE, 5)


class TestContextInjection(unittest.TestCase):
    """The context injection layer (T2): __init__ binds live
    infrastructure helpers onto the shared Context, which is the
    module's main integration surface with domain workers."""

    def setUp(self):
        """Fresh machine (3 workers); cfg simulated as a domain worker
        (e.g., the ConfigWorker) would populate it."""
        self.patcher = patch('sys.stdout', new=StringIO())
        self.patcher.start()
        self.context = Context()
        self.up_callables = [MagicMock() for _ in range(3)]
        self.down_callables = [MagicMock() for _ in range(3)]
        self.workers = [
            Worker("CREATED", self.up_callables[0], self.down_callables[0]),
            Worker("CONFIG", self.up_callables[1], self.down_callables[1]),
            Worker("POSITIONS", self.up_callables[2], self.down_callables[2])
        ]
        self.sm = StateMachine(self.workers, self.context)
        self.context.cfg = SimpleNamespace(
            cache_files_prefix="cache/", base_dir=Path("base"))

    def tearDown(self):
        self.patcher.stop()

    def test_injected_log_event_is_live_machine_binding(self):
        """context.log_event is this machine's bound method: a call
        through it records a LogEntry in this machine's logs."""
        self.assertIs(self.context.log_event.__self__, self.sm)
        self.assertEqual(len(self.sm.logs), 1)  # the init log only
        self.context.log_event(Relevance.INFO, "injected")
        self.assertEqual(len(self.sm.logs), 2)
        entry = self.sm.logs[-1]
        self.assertEqual(entry.step, 0)
        self.assertEqual(entry.worker_name, "CREATED")
        self.assertEqual(entry.relevance, Relevance.INFO)
        self.assertEqual(entry.message, "injected")

    def test_cache_file_path_tracks_current_step(self):
        """{prefix}{level:02}_{name}.dat with level = current_step at
        call time (the pre-execution update makes it the active
        worker)."""
        self.assertEqual(
            self.context.get_cache_file_path_for_current_level(),
            Path("cache/00_CREATED.dat"))
        self.sm.move_to_step(2)
        self.assertEqual(
            self.context.get_cache_file_path_for_current_level(),
            Path("cache/02_POSITIONS.dat"))
        self.sm.move_to_step(1)
        self.assertEqual(
            self.context.get_cache_file_path_for_current_level(),
            Path("cache/01_CONFIG.dat"))

    def test_cache_file_full_path_joins_base_dir(self):
        """A relative prefix is joined under cfg.base_dir."""
        self.sm.move_to_step(1)
        self.assertEqual(
            self.context.get_cache_file_full_path_for_current_level(),
            Path("base/cache/01_CONFIG.dat"))

    def test_absolute_cache_prefix_drops_base_dir(self):
        """An absolute cache_files_prefix silently drops base_dir
        (pathlib '/' semantics, V9)."""
        self.context.cfg = SimpleNamespace(
            cache_files_prefix="/abs/cache/", base_dir=Path("base"))
        self.sm.move_to_step(1)
        self.assertEqual(
            self.context.get_cache_file_full_path_for_current_level(),
            Path("/abs/cache/01_CONFIG.dat"))

    def test_cache_prefix_is_concatenated_verbatim(self):
        """The prefix is a *filename* prefix, concatenated verbatim
        onto the level
        name — a bare prefix 'cache' glues to 'cache01_CONFIG.dat';
        a directory-like prefix must end with a separator (as in the
        other tests of this class, 'cache/')."""
        self.context.cfg = SimpleNamespace(
            cache_files_prefix=Path("cache"), base_dir=Path("base"))
        self.sm.move_to_step(1)
        self.assertEqual(
            self.context.get_cache_file_path_for_current_level(),
            Path("cache01_CONFIG.dat"))
        self.assertEqual(
            self.context.get_cache_file_full_path_for_current_level(),
            Path("base/cache01_CONFIG.dat"))

    def test_missing_cfg_raises_attribute_error(self):
        """Without a populated cfg, both helpers raise AttributeError
        naming 'cfg' (bare getattr, no default — the documented
        contract)."""
        bare = Context()
        StateMachine([Worker("A", MagicMock(), MagicMock())], bare)
        with self.assertRaises(AttributeError) as ctx:
            bare.get_cache_file_path_for_current_level()
        self.assertIn("cfg", str(ctx.exception))
        with self.assertRaises(AttributeError):
            bare.get_cache_file_full_path_for_current_level()

    def test_empty_workers_degenerate_paths(self):
        """Empty pipeline: Path() cache path, 'UNDEFINED' worker name,
        move_to_last no-op (V9)."""
        bare = Context()
        sm = StateMachine([], bare)
        self.assertEqual(bare.get_cache_file_path_for_current_level(), Path())
        self.assertEqual(sm.current_worker_name, "UNDEFINED")
        sm.move_to_last()  # guarded no-op, must not raise
        self.assertEqual(sm.current_step, 0)
        self.assertEqual(sm.history, [])

    def test_shared_context_rebinds_to_last_machine(self):
        """A shared context re-binds to the LAST machine built on it:
        the injection is a side effect (V17)."""
        shared = Context()
        shared.cfg = SimpleNamespace(
            cache_files_prefix="cache/", base_dir=Path("base"))
        sm1 = StateMachine([
            Worker("A", MagicMock(), MagicMock()),
            Worker("B", MagicMock(), MagicMock())
        ], shared)
        self.assertEqual(shared.get_cache_file_path_for_current_level(),
                         Path("cache/00_A.dat"))
        sm2 = StateMachine([Worker("C", MagicMock(), MagicMock())], shared)
        # the helpers now reflect the last machine built
        self.assertEqual(shared.get_cache_file_path_for_current_level(),
                         Path("cache/00_C.dat"))
        shared.log_event(Relevance.INFO, "via shared ctx")
        self.assertEqual(len(sm2.logs), 2)  # init + this one
        self.assertEqual(len(sm1.logs), 1)  # its own init only
        self.assertEqual(sm2.logs[-1].message, "via shared ctx")


class TestDisplayGoldens(unittest.TestCase):
    """Display goldens for the print paths (T3): the live
    log_event line, show_event_log, show_history_of_moves. The
    module clock is frozen (advancing 1ms per now() call), so the
    goldens are exact — no wall-clock dependence."""

    T0 = datetime(2026, 8, 29, 12, 34, 56, tzinfo=timezone.utc)

    @staticmethod
    def _frozen_datetime():
        """Fake module datetime: now() advances 1ms on every call."""
        state = {"n": 0}

        class FakeDT:
            @staticmethod
            def now(tz=None):
                state["n"] += 1
                return TestDisplayGoldens.T0 + timedelta(
                    microseconds=state["n"] * 1000)

        return FakeDT

    def _machine(self):
        """3-worker machine, verbosity HIGH (everything prints)."""
        context = Context()
        workers = [
            Worker("CREATED", MagicMock(), MagicMock()),
            Worker("CONFIG", MagicMock(), MagicMock()),
            Worker("POSITIONS", MagicMock(), MagicMock())
        ]
        return StateMachine(workers, context, Verbosity.HIGH)

    def test_log_event_live_print_format(self):
        """[ts UTC] [step][name       ] [rel:verb] message — full
        golden line per event (the enum-name rendering and the UTC
        marker are pinned too)."""
        with patch('reversi.tools.state_machine.datetime',
                   self._frozen_datetime()):
            buf = StringIO()
            with redirect_stdout(buf):
                sm = self._machine()  # DEBUG init line
                sm.move_to_step(1)    # 2x INFO for CONFIG
        lines = buf.getvalue().splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0],
            "[2026-08-29 12:34:56 UTC] [00][CREATED        ] "
            "[DEBUG:    HIGH] StateMachine initialized.")
        self.assertEqual(lines[1],
            "[2026-08-29 12:34:56 UTC] [01][CONFIG         ] "
            "[ INFO:    HIGH] Starting worker CONFIG, UP step")
        self.assertEqual(lines[2],
            "[2026-08-29 12:34:56 UTC] [01][CONFIG         ] "
            "[ INFO:    HIGH] Completed UP step for CONFIG")

    def test_show_event_log_golden(self):
        """End-to-end golden: the move's live lines, then the table —
        banner, 66-underscore separator, header (UTC timestamp,
        2-digit step, relevance name), one row per log entry."""
        with patch('reversi.tools.state_machine.datetime',
                   self._frozen_datetime()):
            buf = StringIO()
            with redirect_stdout(buf):
                sm = self._machine()
                sm.move_to_step(1)
                sm.show_event_log()
        expected = (
            "[2026-08-29 12:34:56 UTC] [00][CREATED        ] "
            "[DEBUG:    HIGH] StateMachine initialized.\n"
            "[2026-08-29 12:34:56 UTC] [01][CONFIG         ] "
            "[ INFO:    HIGH] Starting worker CONFIG, UP step\n"
            "[2026-08-29 12:34:56 UTC] [01][CONFIG         ] "
            "[ INFO:    HIGH] Completed UP step for CONFIG\n"
            "\n--- --- --- --- --- - EVENT LOG - --- --- --- --- ---\n"
            "__________________________________________________________________\n"
            "TIMESTAMP (UTC)     | STEP | WORKER          | RELEVANCE | "
            "MESSAGE\n"
            "2026-08-29 12:34:56 | 00   | CREATED         | DEBUG     | "
            "StateMachine initialized.\n"
            "2026-08-29 12:34:56 | 01   | CONFIG          | INFO      | "
            "Starting worker CONFIG, UP step\n"
            "2026-08-29 12:34:56 | 01   | CONFIG          | INFO      | "
            "Completed UP step for CONFIG\n"
        )
        self.assertEqual(buf.getvalue(), expected)

    def test_show_history_of_moves_golden(self):
        """End-to-end golden: the move's live lines, then the table —
        header (Dur (s) right-aligned over its values),
        80-dash rule, one row per executed step (start at
        microsecond precision; duration = finish - start, pinned at
        0.003000 by the frozen clock)."""
        with patch('reversi.tools.state_machine.datetime',
                   self._frozen_datetime()):
            buf = StringIO()
            with redirect_stdout(buf):
                sm = self._machine()
                sm.move_to_step(2)
                sm.show_history_of_moves()
        expected = (
            "[2026-08-29 12:34:56 UTC] [00][CREATED        ] "
            "[DEBUG:    HIGH] StateMachine initialized.\n"
            "[2026-08-29 12:34:56 UTC] [01][CONFIG         ] "
            "[ INFO:    HIGH] Starting worker CONFIG, UP step\n"
            "[2026-08-29 12:34:56 UTC] [01][CONFIG         ] "
            "[ INFO:    HIGH] Completed UP step for CONFIG\n"
            "[2026-08-29 12:34:56 UTC] [02][POSITIONS      ] "
            "[ INFO:    HIGH] Starting worker POSITIONS, UP step\n"
            "[2026-08-29 12:34:56 UTC] [02][POSITIONS      ] "
            "[ INFO:    HIGH] Completed UP step for POSITIONS\n"
            "Step   | Worker          | Dir   | Start (UTC)                | "
            "        Dur (s)\n"
            "--------------------------------------------------------------------------------\n"
            "1      | CONFIG          | up    | 2026-08-29 12:34:56.002000 | "
            "       0.003000\n"
            "2      | POSITIONS       | up    | 2026-08-29 12:34:56.006000 | "
            "       0.003000\n"
        )
        self.assertEqual(buf.getvalue(), expected)


if __name__ == '__main__':
    unittest.main()
