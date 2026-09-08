#
# test_logistic_model.py
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
# How to use the unit tests logistic_model module.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest twolm.test.test_logistic_model
#

import unittest
import tempfile
import os
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from unittest.mock import MagicMock, patch

from pydantic import ValidationError

from twolm.logistic_model import (LogisticModel, RLMContext,
                                  _check_base_dir_override,
                                  _check_config_file_path,
                                  _created_down, _created_up)
from reversi.tools.state_machine import Worker, Verbosity
from reversi.test.paths import CUSTOM_TMP_BASE


class TestLogisticModel(unittest.TestCase):
    """Test suite for the LogisticModel facade and RLMContext."""

    @classmethod
    def setUpClass(cls):
        """Ensure the build/tmp base directory exists (T2, D-075)."""
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        """Set up a dummy config file and patch stdout and worker factories."""
        # T2 (D-075): the dummy config lives under
        # <workspace-root>/build/tmp (the D-065 house rule), not the
        # system temp dir. Created first, so a mid-setup failure
        # still leaves a temp_dir that tearDown (or the GC) cleans.
        self.temp_dir = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))

        # Patch stdout to keep test output clean
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # Create a dummy config file
        self.dummy_config_path = os.path.join(self.temp_dir.name, "dummy_config.json")
        with open(self.dummy_config_path, "w") as f:
            f.write("{}") # Empty JSON is enough for path validation

        # Mock the callables for the dummy workers
        self.config_up_mock = MagicMock()
        self.config_down_mock = MagicMock()
        self.positions_up_mock = MagicMock()
        self.positions_down_mock = MagicMock()

        # Patch the factory functions to return our dummy workers
        self.patcher_config = patch('twolm.logistic_model.wrk_config', 
                                    return_value=Worker("CONFIG", self.config_up_mock, self.config_down_mock))
        self.patcher_positions = patch('twolm.logistic_model.wrk_positions', 
                                       return_value=Worker("POSITIONS", self.positions_up_mock, self.positions_down_mock))
        
        self.mock_config_factory = self.patcher_config.start()
        self.mock_positions_factory = self.patcher_positions.start()

        # Instantiate the model
        self.model = LogisticModel(
            config_file_path=self.dummy_config_path,
            verbosity=Verbosity.STANDARD
        )

    def tearDown(self):
        """Clean up patches and temporary files. T2 (D-075):
        defensive against mid-setup failures — stop only the
        patchers that exist, then remove the temp dir."""
        for name in ('patcher_stdout', 'patcher_config', 'patcher_positions'):
            patcher = getattr(self, name, None)
            if patcher is not None:
                patcher.stop()
        temp_dir = getattr(self, 'temp_dir', None)
        if temp_dir is not None:
            temp_dir.cleanup()

    def test_context_initialization(self):
        """Test that RLMContext is correctly initialized with paths."""
        self.assertIsInstance(self.model.context, RLMContext)
        self.assertEqual(str(self.model.context.config_file_path), self.dummy_config_path)
        self.assertIsNone(self.model.context.base_dir_override)
        self.assertIsNone(self.model.context.cfg) # Should start empty

    def test_state_machine_initialization(self):
        """Test that the state machine is initialized at step 0 (CREATED)."""
        self.assertEqual(self.model.current_step, 0)
        self.assertEqual(self.model.current_worker_name, "CREATED")

    def test_init_non_str_config_path_raises_validation_error(self):
        """The @validate_call on __init__ (D-074 R3) rejects a non-str/Path
        config_file_path with a pydantic ValidationError before any worker
        factory runs (fail-fast guard).

        Converted from the verify_logistic_model.py V6f probe at D-106
        step 3 (probe_rules.md §4: cheap deterministic unit behavior of
        one module belongs in the tests, not the probes)."""
        with self.assertRaises(ValidationError):
            LogisticModel(123)

    def test_injected_cache_closure_requires_cfg(self):
        """The injected _for_current_level closure dereferences ctx.cfg;
        before the CONFIG worker runs, cfg is None and the call must
        fail with AttributeError (the injection-order fact; a bare
        RLMContext instead keeps the no-op lambda default, D-074 R1).

        Converted from the verify_wrk_config.py E4b probe at D-106
        step 3 (probe_rules.md §4)."""
        with self.assertRaises(AttributeError):
            self.model.context.get_cache_file_path_for_current_level()

    def test_move_to_step_delegates_to_state_machine(self):
        """Test that moving to a step triggers the correct mock worker."""
        self.model.move_to_step(1) # Move to CONFIG
        
        self.assertEqual(self.model.current_step, 1)
        self.config_up_mock.assert_called_once_with(self.model.context)
        self.config_down_mock.assert_not_called()

    def test_move_to_step_by_string(self):
        """Test moving using the worker name string."""
        self.model.move_to_step("POSITIONS")
        
        self.assertEqual(self.model.current_step, 2)
        self.config_up_mock.assert_called_once_with(self.model.context)
        self.positions_up_mock.assert_called_once_with(self.model.context)

    def test_invalid_config_path(self):
        """Test that providing a non-existent config file raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            LogisticModel(config_file_path="non_existent_file.json")

    def test_base_dir_override_validation(self):
        """Test that an invalid base_dir_override raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            LogisticModel(
                config_file_path=self.dummy_config_path,
                base_dir_override="non_existent_dir"
            )

    def test_facade_delegates_to_state_machine(self):
        """T1 (D-075): every facade method is a pure pass-through —
        pin the delegation per method on the shared model's
        StateMachine (replaces the old try/except smoke test)."""
        with patch.object(self.model.sm, "show_event_log") as m:
            self.model.show_event_log()
            m.assert_called_once_with()
        with patch.object(self.model.sm, "show_history_of_moves") as m:
            self.model.show_history_of_moves()
            m.assert_called_once_with()
        with patch.object(self.model.sm, "move_to_step") as m:
            self.model.move_to_step(1)
            m.assert_called_once_with(1)
        with patch.object(self.model.sm, "move_to_step") as m:
            self.model.move_to_step("CONFIG")
            m.assert_called_once_with("CONFIG")
        with patch.object(self.model.sm, "move_to_last") as m:
            self.model.move_to_last()
            m.assert_called_once_with()
        with patch.object(self.model.sm,
                          "export_history_of_moves_as_csv") as m:
            self.model.export_history_of_moves_as_csv("history.csv")
            m.assert_called_once_with("history.csv")

    def test_facade_views_and_verbosity_round_trip(self):
        """T1 (D-075): the read-only views mirror the StateMachine
        and the verbosity property round-trips through it."""
        self.assertEqual(self.model.current_step, self.model.sm.current_step)
        self.assertEqual(self.model.current_worker_name,
                         self.model.sm.current_worker_name)
        self.assertEqual(self.model.verbosity, self.model.sm.verbosity)
        self.model.verbosity = Verbosity.HIGH
        self.assertIs(self.model.sm.verbosity, Verbosity.HIGH)
        self.assertIs(self.model.verbosity, Verbosity.HIGH)
        # Leave the shared model at its default.
        self.model.verbosity = Verbosity.STANDARD


    def test_injected_cache_helpers_are_the_machine_closures(self):
        """T4 (D-075): post-construction, the context's
        *_for_current_level attributes ARE the closures StateMachine
        injected under the D-069 names (pre-D-074 a regression to
        the old names would have left the no-op lambda defaults and
        returned None — this pin would have caught R1)."""
        ctx = self.model.context
        self.assertEqual(ctx.get_cache_file_path_for_current_level.__name__,
                         "_get_cache_file_path")
        self.assertEqual(
            ctx.get_cache_file_full_path_for_current_level.__name__,
            "_get_cache_file_full_path")
        self.assertEqual(ctx.log_event.__name__, "log_event")

    def test_pre_injection_fallback_is_no_op_lambda(self):
        """T4 (D-075): a bare (un-injected) RLMContext keeps the
        lambda no-op defaults — the cache helpers return None and
        log_event does nothing, without crashing."""
        bare = RLMContext(config_file_path=Path(self.dummy_config_path))
        self.assertIsNone(bare.get_cache_file_path_for_current_level())
        self.assertIsNone(bare.get_cache_file_full_path_for_current_level())
        bare.log_event()

    def test_injected_cache_helper_computes_the_worker_path(self):
        """T4 (D-075, re-pinned D-078): with a dummy cfg, the injected
        path closures compute the per-level cache path by
        filename-prefix concatenation (D-078, replacing the D-069 M8
        pathlib join): <prefix><level:02>_<worker>.dat, and the full
        variant prepends cfg.base_dir."""
        ctx = self.model.context
        ctx.cfg = SimpleNamespace(cache_files_prefix="cache",
                                  base_dir=Path("base"))
        self.addCleanup(setattr, ctx, "cfg", None)
        self.assertEqual(ctx.get_cache_file_path_for_current_level(),
                         Path("cache00_CREATED.dat"))
        self.assertEqual(ctx.get_cache_file_full_path_for_current_level(),
                         Path("base/cache00_CREATED.dat"))

    def test_created_sentinel_workers_raise(self):
        """T4 (D-075): the level-0 CREATED sentinels are explicit
        (D-059) — a direct call logs ERROR then raises RuntimeError."""
        with self.assertRaisesRegex(
                RuntimeError, "Executing created step should never happen."):
            _created_up(self.model.context)
        with self.assertRaisesRegex(
                RuntimeError, "Cleaning created step should never happen."):
            _created_down(self.model.context)

    def test_config_path_helper_edge_branches(self):
        """T4 (D-075): _check_config_file_path edge branches —
        non-str/Path -> TypeError, missing -> FileNotFoundError,
        a directory -> IsADirectoryError (M3, D-074)."""
        with self.assertRaisesRegex(
                TypeError,
                "Argument config_file_path is not an instance of str or Path"):
            _check_config_file_path(123)
        with self.assertRaisesRegex(
                FileNotFoundError, "No such file: 'ghost.json'"):
            _check_config_file_path("ghost.json")
        with self.assertRaisesRegex(IsADirectoryError,
                                    "File path is not a file:"):
            _check_config_file_path(self.temp_dir.name)

    def test_base_dir_helper_edge_branches(self):
        """T4 (D-075): _check_base_dir_override edge branches —
        non-str/Path -> TypeError, a file -> NotADirectoryError."""
        with self.assertRaisesRegex(
                TypeError,
                "Argument base_dir_override is not an instance of str or Path"):
            _check_base_dir_override(123)
        with self.assertRaisesRegex(NotADirectoryError,
                                    "File path is not a directory:"):
            _check_base_dir_override(self.dummy_config_path)

    def test_export_history_of_moves_as_csv_pass_through(self):
        """T4 (D-075): the CSV export pass-through writes a real file
        (the SM's exporter, parent-dir creation M10/D-068); with an
        empty history the file is header-only. The artifact stays
        under build/tmp (D-065) and the temp dir is removed in
        tearDown."""
        csv_path = Path(self.temp_dir.name) / "history.csv"
        self.model.export_history_of_moves_as_csv(csv_path)
        self.assertTrue(csv_path.is_file())
        self.assertEqual(
            csv_path.read_text().splitlines(),
            ["step,worker_name,direction,start_utc,"
             "finish_utc,duration_sec"])


if __name__ == '__main__':
    unittest.main()
