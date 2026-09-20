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
# time python3 -m unittest test.reversi.lm.test_logistic_model
#

import unittest
import tempfile
import json
import os
from io import StringIO
from pathlib import Path
from types import SimpleNamespace

from unittest.mock import MagicMock, patch

import json5

from pydantic import ValidationError

from reversi.base_model import BaseModel
from reversi.lm.logistic_model import (LogisticModel, LMContext,
                                  _check_base_dir_override,
                                  _check_config_file_path,
                                  _created_down, _created_up)
from reversi.tools.state_machine import Worker, Verbosity
from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT


class TestLogisticModel(unittest.TestCase):
    """Test suite for the LogisticModel facade and LMContext."""

    @classmethod
    def setUpClass(cls):
        """Ensure the build/tmp base directory exists."""
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        """Set up a dummy config file and patch stdout and worker factories."""
        # The dummy config lives under
        # <workspace-root>/build/tmp (house rule), not the
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
        self.patcher_config = patch('reversi.lm.logistic_model.wrk_config', 
                                    return_value=Worker("CONFIG", self.config_up_mock, self.config_down_mock))
        self.patcher_positions = patch('reversi.lm.logistic_model.wrk_positions', 
                                       return_value=Worker("POSITIONS", self.positions_up_mock, self.positions_down_mock))
        # The FEATURES dummy — the string move to POSITIONS
        # crosses it, and the real FEATURES worker would hit the
        # None cfg.
        self.features_up_mock = MagicMock()
        self.features_down_mock = MagicMock()
        self.patcher_features = patch('reversi.lm.logistic_model.wrk_features',
                                      return_value=Worker("FEATURES", self.features_up_mock, self.features_down_mock))
        # The SU_ANALYSIS + the EFFECT_SIZE worker dummies.
        # Without them the real workers would cross the
        # "POSITIONS" string move and hit the None cfg (the mock
        # CONFIG never sets it).
        self.fa_up_mock = MagicMock()
        self.fa_down_mock = MagicMock()
        self.patcher_fa = patch('reversi.lm.logistic_model.wrk_su_analysis',
                                return_value=Worker("SU_ANALYSIS", self.fa_up_mock, self.fa_down_mock))
        self.es_up_mock = MagicMock()
        self.es_down_mock = MagicMock()
        self.patcher_es = patch('reversi.lm.logistic_model.wrk_effect_size',
                                return_value=Worker("EFFECT_SIZE", self.es_up_mock, self.es_down_mock))

        self.mock_config_factory = self.patcher_config.start()
        self.mock_positions_factory = self.patcher_positions.start()
        self.mock_features_factory = self.patcher_features.start()
        self.mock_fa_factory = self.patcher_fa.start()
        self.mock_es_factory = self.patcher_es.start()

        # Instantiate the model
        self.model = LogisticModel(
            config_file_path=self.dummy_config_path,
            verbosity=Verbosity.STANDARD
        )

    def tearDown(self):
        """Clean up patches and temporary files: defensive
        against mid-setup failures — stop only the patchers that
        exist, then remove the temp dir."""
        for name in ('patcher_stdout', 'patcher_config', 'patcher_positions',
                     'patcher_features', 'patcher_fa', 'patcher_es'):
            patcher = getattr(self, name, None)
            if patcher is not None:
                patcher.stop()
        temp_dir = getattr(self, 'temp_dir', None)
        if temp_dir is not None:
            temp_dir.cleanup()

    def test_context_initialization(self):
        """Test that LMContext is correctly initialized with paths."""
        self.assertIsInstance(self.model.context, LMContext)
        self.assertEqual(str(self.model.context.config_file_path), self.dummy_config_path)
        self.assertIsNone(self.model.context.base_dir_override)
        self.assertIsNone(self.model.context.cfg) # Should start empty

    def test_state_machine_initialization(self):
        """Test that the state machine is initialized at the CREATED sentinel."""
        self.assertEqual(self.model.current_step, 0)
        self.assertEqual(self.model.current_worker_name, "CREATED")

    def test_init_non_str_config_path_raises_validation_error(self):
        """The @validate_call on __init__ rejects a non-str/Path
        config_file_path with a pydantic ValidationError before any worker
        factory runs (fail-fast guard).

        Converted from the verify_logistic_model.py V6f probe
        (probe_rules.md §4: cheap deterministic unit behavior of
        one module belongs in the tests, not the probes)."""
        with self.assertRaises(ValidationError):
            LogisticModel(123)

    def test_injected_cache_closure_requires_cfg(self):
        """The injected _for_current_level closure dereferences ctx.cfg;
        before the CONFIG worker runs, cfg is None and the call must
        fail with AttributeError (the injection-order fact; a bare
        LMContext instead keeps the no-op lambda default).

        Converted from the verify_wrk_config.py E4b probe
        (probe_rules.md §4)."""
        with self.assertRaises(AttributeError):
            self.model.context.get_cache_file_path_for_current_level()

    def test_move_to_step_delegates_to_state_machine(self):
        """Test that moving to a step triggers the correct mock worker."""
        self.model.move_to_step(1) # Move to CONFIG
        
        self.assertEqual(self.model.current_step, 1)
        self.config_up_mock.assert_called_once_with(self.model.context)
        self.config_down_mock.assert_not_called()

    def test_move_to_step_by_string(self):
        """Test moving using the worker name string: the POSITIONS
        sits after the SU_ANALYSIS, which sits between FEATURES
        and POSITIONS — the string move crosses the SU_ANALYSIS
        step."""
        self.model.move_to_step("POSITIONS")

        self.assertEqual(self.model.current_step, 4)
        self.config_up_mock.assert_called_once_with(self.model.context)
        self.features_up_mock.assert_called_once_with(self.model.context)
        self.fa_up_mock.assert_called_once_with(self.model.context)
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
        """Every facade method is a pure pass-through: the
        delegation is pinned per method on the shared model's
        StateMachine."""
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

    def _new_model(self):
        """A fresh model on the shared dummy config (the patched
        factories are active for the whole test)."""
        return LogisticModel(config_file_path=self.dummy_config_path,
                             verbosity=Verbosity.STANDARD)

    def test_run_moves_to_the_explicit_target(self):
        """run(target) drives the pipeline from the sentinel: the
        first real level (CONFIG) runs first, then the levels
        up to the target, target included — the machine's own
        contract, no extra machinery."""
        self.model.run("POSITIONS")
        self.assertEqual(self.model.current_step, 4)
        self.assertEqual(self.model.current_worker_name, "POSITIONS")
        self.assertEqual([(e.step, e.worker_name, e.direction)
                          for e in self.model.sm.history],
                         [(1, "CONFIG", "up"), (2, "FEATURES", "up"),
                          (3, "SU_ANALYSIS", "up"), (4, "POSITIONS", "up")])
        self.config_up_mock.assert_called_once_with(self.model.context)
        self.features_up_mock.assert_called_once_with(self.model.context)
        self.fa_up_mock.assert_called_once_with(self.model.context)
        self.positions_up_mock.assert_called_once_with(self.model.context)
        self.positions_down_mock.assert_not_called()

    def test_run_honors_the_config_target_level(self):
        """With no argument the stop comes from the loaded config —
        LMConfig.target_level, read AFTER the CONFIG level ran."""
        self.model.context.cfg = SimpleNamespace(target_level="SU_ANALYSIS")
        self.addCleanup(setattr, self.model.context, "cfg", None)
        self.model.run()
        self.assertEqual(self.model.current_step, 3)
        self.assertEqual(self.model.current_worker_name, "SU_ANALYSIS")
        self.fa_up_mock.assert_called_once_with(self.model.context)
        self.positions_up_mock.assert_not_called()

    def test_run_last_resolution(self):
        """'last' means the whole pipeline: the field default, the
        upper/lower case, a blank value and an absent config all
        delegate to move_to_last (patched — the tail levels need the
        DB). The CONFIG level still runs first."""
        for cfg, label in [(SimpleNamespace(target_level="last"), "last"),
                           (SimpleNamespace(target_level="LAST"), "LAST"),
                           (SimpleNamespace(target_level="  "), "blank"),
                           (SimpleNamespace(), "no field"),
                           (None, "no cfg")]:
            model = self._new_model()
            model.context.cfg = cfg
            with patch.object(model.sm, "move_to_last") as m:
                model.run()
                m.assert_called_once_with()
            self.assertEqual(model.current_step, 1, label)

    def test_run_explicit_argument_wins_over_the_config(self):
        """The precedence: the explicit argument beats the field."""
        self.model.context.cfg = SimpleNamespace(target_level="FEATURES")
        self.addCleanup(setattr, self.model.context, "cfg", None)
        self.model.run("SU_ANALYSIS")
        self.assertEqual(self.model.current_step, 3)

    def test_run_resumes_without_resetting(self):
        """The motivating flow: stop after the long SU_ANALYSIS,
        inspect, then continue — the levels already done are NOT
        re-run, so their ctx artifacts stay published (no down call)."""
        self.model.run("SU_ANALYSIS")
        self.assertEqual(self.model.current_step, 3)
        self.model.run("POSITIONS")
        self.assertEqual(self.model.current_step, 4)
        self.model.run("POSITIONS")          # the same target: a no-op
        self.assertEqual(self.model.current_step, 4)
        self.config_up_mock.assert_called_once_with(self.model.context)
        self.features_up_mock.assert_called_once_with(self.model.context)
        self.fa_up_mock.assert_called_once_with(self.model.context)
        self.positions_up_mock.assert_called_once_with(self.model.context)
        self.fa_down_mock.assert_not_called()

    def test_run_backward_target_runs_the_down_steps(self):
        """A target BELOW the current step moves back, running the
        down() of the levels left behind (the rollback)."""
        self.model.run("POSITIONS")
        self.model.run("FEATURES")
        self.assertEqual(self.model.current_step, 2)
        self.positions_down_mock.assert_called_once_with(self.model.context)
        self.fa_down_mock.assert_called_once_with(self.model.context)

    def test_run_unknown_target_is_the_machine_value_error(self):
        """An unknown level name raises the machine's fail-fast
        ValueError (no new validation machinery): the CONFIG level has
        already run, so current_step stays at 1."""
        with self.assertRaisesRegex(ValueError,
                                    "Worker 'NOPE' not found in the pipeline."):
            self.model.run("NOPE")
        self.assertEqual(self.model.current_step, 1)
        self.config_up_mock.assert_called_once_with(self.model.context)

    def test_run_wrong_target_type_is_the_pinned_type_error(self):
        """A non-int / non-str target is the gate's TypeError."""
        with self.assertRaisesRegex(
                TypeError,
                "target_step must be an integer index or a string worker name."):
            self.model.run(3.5)
        self.assertEqual(self.model.current_step, 1)

    def test_run_base_default_is_the_last_step(self):
        """BaseModel.run is the GENERIC entry (every domain facade
        gets it): the base hook returns None -> the last step, and an
        explicit target still resolves. The domain hook is the only
        override (LogisticModel reads its config)."""
        workers = [Worker("CREATED", MagicMock(), MagicMock()),
                   Worker("ONLY", MagicMock(), MagicMock())]
        bare = BaseModel(workers=workers,
                         context=LMContext(
                             config_file_path=Path(self.dummy_config_path)))
        self.assertIsNone(bare._configured_target_level())
        with patch.object(bare.sm, "move_to_last") as m:
            bare.run()
            m.assert_called_once_with()
        self.assertEqual(bare.current_step, 1)
        bare2 = BaseModel(workers=workers,
                          context=LMContext(
                              config_file_path=Path(self.dummy_config_path)))
        bare2.run("ONLY")
        self.assertEqual(bare2.current_step, 1)

    def test_facade_views_and_verbosity_round_trip(self):
        """The read-only views mirror the StateMachine and the
        verbosity property round-trips through it."""
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
        """Post-construction, the context's
        *_for_current_level attributes ARE the closures StateMachine
        injected under those names (a regression to the old names
        would have left the no-op lambda defaults and returned None —
        this pin would have caught it)."""
        ctx = self.model.context
        self.assertEqual(ctx.get_cache_file_path_for_current_level.__name__,
                         "_get_cache_file_path")
        self.assertEqual(
            ctx.get_cache_file_full_path_for_current_level.__name__,
            "_get_cache_file_full_path")
        self.assertEqual(ctx.log_event.__name__, "log_event")

    def test_pre_injection_fallback_is_no_op_lambda(self):
        """A bare (un-injected) LMContext keeps the lambda no-op
        defaults — the cache helpers return None and
        log_event does nothing, without crashing."""
        bare = LMContext(config_file_path=Path(self.dummy_config_path))
        self.assertIsNone(bare.get_cache_file_path_for_current_level())
        self.assertIsNone(bare.get_cache_file_full_path_for_current_level())
        bare.log_event()

    def test_injected_cache_helper_computes_the_worker_path(self):
        """With a dummy cfg, the injected path closures compute the
        per-level cache path by filename-prefix concatenation:
        <prefix><level:02>_<worker>.dat, and the full variant
        prepends cfg.base_dir."""
        ctx = self.model.context
        ctx.cfg = SimpleNamespace(cache_files_prefix="cache",
                                  base_dir=Path("base"))
        self.addCleanup(setattr, ctx, "cfg", None)
        self.assertEqual(ctx.get_cache_file_path_for_current_level(),
                         Path("cache00_CREATED.dat"))
        self.assertEqual(ctx.get_cache_file_full_path_for_current_level(),
                         Path("base/cache00_CREATED.dat"))

    def test_created_sentinel_workers_raise(self):
        """The level-0 CREATED sentinels are explicit — a
        direct call logs ERROR then raises RuntimeError."""
        with self.assertRaisesRegex(
                RuntimeError, "Executing created step should never happen."):
            _created_up(self.model.context)
        with self.assertRaisesRegex(
                RuntimeError, "Cleaning created step should never happen."):
            _created_down(self.model.context)

    def test_config_path_helper_edge_branches(self):
        """_check_config_file_path edge branches — non-str/Path ->
        TypeError, missing -> FileNotFoundError,
        a directory -> IsADirectoryError."""
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
        """_check_base_dir_override edge branches — non-str/Path ->
        TypeError, a file -> NotADirectoryError."""
        with self.assertRaisesRegex(
                TypeError,
                "Argument base_dir_override is not an instance of str or Path"):
            _check_base_dir_override(123)
        with self.assertRaisesRegex(NotADirectoryError,
                                    "File path is not a directory:"):
            _check_base_dir_override(self.dummy_config_path)

    def test_export_history_of_moves_as_csv_pass_through(self):
        """The CSV export pass-through writes a real file (the SM's
        exporter, parent-dir creation); with an
        empty history the file is header-only. The artifact stays
        under build/tmp and the temp dir is removed in
        tearDown."""
        csv_path = Path(self.temp_dir.name) / "history.csv"
        self.model.export_history_of_moves_as_csv(csv_path)
        self.assertTrue(csv_path.is_file())
        self.assertEqual(
            csv_path.read_text().splitlines(),
            ["step,worker_name,direction,start_utc,"
             "finish_utc,duration_sec"])


class TestRunFacadeOnARealConfig(unittest.TestCase):
    """The run() facade on the REAL pipeline (no factory mocks): the
    LMConfig.target_level resolution + the explicit-argument precedence
    + the resume, exercised to FEATURES / SU_ANALYSIS — the levels that
    need no database. The config copies and the artifacts stay under
    build/tmp."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.base = Path(self.temp_dir.name)
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.patcher_stdout.start()

    def tearDown(self):
        self.patcher_stdout.stop()
        self.temp_dir.cleanup()

    def _model(self, target_level):
        """A real model on the rlm_00 fixture with target_level set
        (the config-copy idiom: the override is a CONFIG FILE,
        so the config provenance stays coherent)."""
        raw = json5.loads((WORKSPACE_ROOT / "test" / "reversi" / "data" /
                           "rlm_00.json").read_text())
        raw["target_level"] = target_level
        path = self.base / f"rlm_00_target_{target_level}.json"
        path.write_text(json.dumps(raw))
        return LogisticModel(str(path), verbosity=Verbosity.HIGH,
                             base_dir_override=self.base)

    def test_run_honors_the_config_target_level(self):
        """No argument: the field drives the stop (FEATURES)."""
        model = self._model("FEATURES")
        model.run()
        self.assertEqual(model.current_step, 2)
        self.assertEqual(model.current_worker_name, "FEATURES")
        self.assertIsNotNone(model.context.feature_set)
        self.assertIsNone(model.context.su_analysis_tables)

    def test_run_explicit_argument_wins_over_the_config(self):
        """The same config asks FEATURES; run('SU_ANALYSIS') goes
        to the SU_ANALYSIS level (the long level the config-target
        case stops at) and publishes the corpus tables."""
        model = self._model("FEATURES")
        model.run("SU_ANALYSIS")
        self.assertEqual(model.current_step, 3)
        self.assertEqual(model.current_worker_name, "SU_ANALYSIS")
        self.assertIsNotNone(model.context.su_analysis_tables)

    def test_run_resumes_on_the_real_pipeline(self):
        """Stop at the long SU_ANALYSIS, inspect, continue: a second
        run() with the same target is a no-op and the published tables
        are the SAME object (no reset, no re-run)."""
        model = self._model("SU_ANALYSIS")
        model.run()
        tables = model.context.su_analysis_tables
        self.assertEqual(model.current_step, 3)
        model.run("SU_ANALYSIS")
        self.assertEqual(model.current_step, 3)
        self.assertIs(model.context.su_analysis_tables, tables)
        self.assertEqual(
            [(e.step, e.worker_name, e.direction)
             for e in model.sm.history],
            [(1, "CONFIG", "up"), (2, "FEATURES", "up"),
             (3, "SU_ANALYSIS", "up")])


if __name__ == '__main__':
    unittest.main()
