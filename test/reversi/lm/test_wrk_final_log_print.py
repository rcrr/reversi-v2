#
# test_wrk_final_log_print.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi-v2
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
# How to run the wrk_final_log_print unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (the NO-DB class; the end-to-end class needs the live regab DB, as in test_wrk_analytics).
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_wrk_final_log_print
#

import tempfile
import unittest
from pathlib import Path

import json5

from reversi.lm.logistic_model import LogisticModel
from reversi.lm.wrk_final_log_print import _down, _up, wrk_final_log_print
from reversi.tools.state_machine import Verbosity
from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from test.reversi.tags import db_gate


class _MockCtx:
    """
    The no-DB mock context: the real pipeline cfg, the event buffer, the format_event_log stand-in.
    """

    def __init__(self, cfg, log_text):
        self.cfg = cfg
        self.events = []
        self._log_text = log_text

    def log_event(self, relevance, msg):
        self.events.append((relevance, msg))

    def format_event_log(self, min_relevance=None):
        return self._log_text


def _make_ctx(tmp, log_file_name=None):
    """
    A mock ctx over the real pipeline cfg: the facade runs CREATED -> CONFIG on the rlm_00 fixture
    (the base_dir override), the log_file_name field set on the real cfg.
    """
    rlm = LogisticModel(str(WORKSPACE_ROOT / "test" / "reversi" /
                            "data" / "rlm_00.json"),
                        verbosity=Verbosity.NONE,
                        base_dir_override=tmp)
    rlm.run("CONFIG")
    rlm.context.cfg.log_file_name = log_file_name
    return _MockCtx(rlm.context.cfg, "line one\nline two")


class TestWrkFinalLogPrint(unittest.TestCase):
    """
    The NO-DB suite: the factory, the config-gate no-op, the full-log write, the subdir path, the down.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_factory(self):
        w = wrk_final_log_print()
        self.assertEqual(w.name, "FINAL_LOG_PRINT")

    def test_skipped_no_file(self):
        # The absent log_file_name (the default None): the no-op (the "skipped" log), the file NOT generated.
        ctx = _make_ctx(self.tmp)
        _up(ctx)
        self.assertTrue(any("skipped" in m for (_r, m) in ctx.events))
        self.assertFalse(list(self.tmp.glob("*.log")))

    def test_full_log_written(self):
        # The configured name: the file under base_dir with the buffered log (the mock's 2 lines)
        # + the "log written" confirmation.
        ctx = _make_ctx(self.tmp, log_file_name="full_run.log")
        _up(ctx)
        f = self.tmp / "full_run.log"
        self.assertTrue(f.exists())
        self.assertEqual(f.read_text(encoding="utf-8"), "line one\nline two")
        self.assertTrue(any("log written" in m for (_r, m) in ctx.events))

    def test_subdir_path(self):
        # A dir-like name: the parents are created.
        ctx = _make_ctx(self.tmp, log_file_name="sub/dir/full.log")
        _up(ctx)
        self.assertTrue((self.tmp / "sub" / "dir" / "full.log").exists())

    def test_down_no_op(self):
        # The down is a no-op (the log note, the file NOT unlinked).
        ctx = _make_ctx(self.tmp, log_file_name="full_run.log")
        _up(ctx)
        _down(ctx)
        self.assertTrue(any("down" in m for (_r, m) in ctx.events))
        self.assertTrue((self.tmp / "full_run.log").exists())


class TestFinalLogPrintEndToEnd(unittest.TestCase):
    """
    The LONG-tier end-to-end: the rlm_00 full chain, the log_file_name in the config from the start
    (a post-CONFIG cfg mutation desyncs the config checksum fingerprinted at CONFIG).
    """

    def setUp(self):
        db_gate(self)
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        # The config: the rlm_00 fixture + the log_file_name entry, written to a tmp copy BEFORE the
        # CONFIG level (the same json5 loader the pipeline uses).
        fixture = WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_00.json"
        cfg = json5.loads(fixture.read_text(encoding="utf-8"))
        cfg["log_file_name"] = "full_run.log"
        self.cfg_file = self.tmp_dir / "rlm_00_final_log.json"
        self.cfg_file.write_text(json5.dumps(cfg), encoding="utf-8")
        self.rlm = LogisticModel(str(self.cfg_file),
                                 verbosity=Verbosity.NONE,
                                 base_dir_override=self.tmp_dir)

    def tearDown(self):
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_full_chain_writes_the_full_log(self):
        self.rlm.move_to_last()
        self.assertEqual(self.rlm.current_step, 19)
        self.assertEqual(self.rlm.current_worker_name, 'FINAL_LOG_PRINT')
        content = (self.tmp_dir / "full_run.log").read_text(encoding="utf-8")
        lines = content.splitlines()
        # The file is the buffer at the moment of the write: it carries its own "Starting" line (the
        # machine logs it before the worker call) but NOT the "Completed" line (logged after the return).
        self.assertTrue(any("Starting worker FINAL_LOG_PRINT, UP step"
                            in ln for ln in lines))
        self.assertFalse(any("Completed UP step for FINAL_LOG_PRINT"
                             in ln for ln in lines))
        self.assertTrue(any("Completed UP step for PLOT" in ln for ln in lines))
        self.assertIn("StateMachine initialized.", lines[0])
        # No FINAL_LOG_PRINT no-op line (the enabled path) — and neither the "log written"
        # confirmation nor the "Completed" line nor the step duration line (all logged AFTER the
        # write). Other levels' no-op notes (e.g. "PLOT skipped") are expected content of the log.
        self.assertFalse(any("FINAL_LOG_PRINT skipped" in ln for ln in lines))
        self.assertFalse(any("log written" in ln for ln in lines))
        # The line count == the buffer at the write (the final buffer minus the three trailing
        # post-write lines: the "log written" confirmation, the "Completed" line, the duration).
        self.assertEqual(len(lines), len(self.rlm.sm.logs) - 3)


if __name__ == '__main__':
    unittest.main()
