#
# test_wrk_final_log_print.py
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
# How to run the wrk_final_log_print module unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (the NO-DB class; the end-to-end class needs the
#     live regab DB + LONG=1, as in test_wrk_analytics).
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_wrk_final_log_print
#

"""
The FINAL_LOG_PRINT worker suite (the 19th level): the
factory (the worker name), the config-gate no-op (the absent
log_file_name, the file NOT generated), the full-log write
(the max-relevance replay on the machine's event buffer), the
base_dir subdir path, the down (the no-op) — and the
LONG-tier end-to-end (the rlm_00 full chain, the log_file_name
entry in the config from the start — the D-322 tmp fixture copy,
the write-asymmetry pins).
"""

import tempfile
import unittest
from pathlib import Path

import json5

from reversi.lm.logistic_model import LogisticModel
from reversi.lm.wrk_final_log_print import _down, _up, wrk_final_log_print
from reversi.tools.state_machine import Verbosity
from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT
from test.reversi.tags import db_long_gate


class _MockCtx:
    """The no-DB mock context (the worker's blackboard): the cfg
    (the real one — see _make_ctx), the event buffer, and a
    stand-in format_event_log (the machine's renderer, the
    context injection)."""

    def __init__(self, cfg, log_text):
        self.cfg = cfg
        self.events = []
        self._log_text = log_text

    def log_event(self, relevance, msg):
        self.events.append((relevance, msg))

    def format_event_log(self):
        return self._log_text


def _make_ctx(tmp, log_file_name=None):
    """A mock ctx over the REAL pipeline's cfg: the facade runs
    CREATED -> CONFIG on the rlm_00 fixture (the base_dir
    override, D-287) and the cfg (with base_dir = the tmp dir)
    comes from the real context — no parallel loader. The
    log_file_name field is set on the real cfg."""
    rlm = LogisticModel(str(WORKSPACE_ROOT / "test" / "reversi" /
                            "data" / "rlm_00.json"),
                        verbosity=Verbosity.NONE,
                        base_dir_override=tmp)
    rlm.run("CONFIG")
    rlm.context.cfg.log_file_name = log_file_name
    return _MockCtx(rlm.context.cfg, "line one\nline two")


class TestWrkFinalLogPrint(unittest.TestCase):
    """The FINAL_LOG_PRINT worker NO-DB suite: the factory, the
    config-gate no-op, the full-log write, the subdir path, the
    down (the no-op)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def test_factory(self):
        w = wrk_final_log_print()
        self.assertEqual(w.name, "FINAL_LOG_PRINT")

    def test_skipped_no_file(self):
        # The absent log_file_name (the default None): the no-op
        # (the "skipped" log), the file NOT generated.
        ctx = _make_ctx(self.tmp)
        _up(ctx)
        self.assertTrue(any("skipped" in m for (_r, m) in ctx.events))
        self.assertFalse(list(self.tmp.glob("*.log")))

    def test_full_log_written(self):
        # The configured name: the file under base_dir with the
        # full buffered log (the mock's 2 lines) + the "full log
        # written" log.
        ctx = _make_ctx(self.tmp, log_file_name="full_run.log")
        _up(ctx)
        f = self.tmp / "full_run.log"
        self.assertTrue(f.exists())
        self.assertEqual(f.read_text(encoding="utf-8"), "line one\nline two")
        self.assertTrue(any("full log written" in m for (_r, m) in ctx.events))

    def test_subdir_path(self):
        # A dir-like name: the parents are created.
        ctx = _make_ctx(self.tmp, log_file_name="sub/dir/full.log")
        _up(ctx)
        self.assertTrue((self.tmp / "sub" / "dir" / "full.log").exists())

    def test_down_no_op(self):
        # The down is a no-op (the log note).
        ctx = _make_ctx(self.tmp, log_file_name="full_run.log")
        _up(ctx)
        _down(ctx)
        self.assertTrue(any("down" in m for (_r, m) in ctx.events))


class TestFinalLogPrintEndToEnd(unittest.TestCase):
    """The LONG-tier end-to-end: the rlm_00 full chain with the
    log_file_name entry present in the config FROM THE START (the
    tmp fixture copy — the D-322 fix: the config checksum is
    fingerprinted at CONFIG, so a post-CONFIG cfg mutation desyncs
    the SAVE-embedded live dump from the fingerprint and the
    CLIENT_CHECK section check raises) — the 19th level writes the
    full run log at the maximum relevance (the verbosity is NONE —
    nothing prints, the buffer captures everything); the
    write-asymmetry pins (the file carries its own "Starting" line,
    not the "Completed" line)."""

    def setUp(self):
        db_long_gate(self)
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        # The config: the rlm_00 fixture + the log_file_name
        # entry, written to a tmp copy BEFORE the CONFIG level (the
        # same json5 loader the pipeline uses).
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
        # The file is the buffer at the moment of the write: it
        # carries its own "Starting" line (the machine logs it
        # before the worker call) but NOT the "Completed" line
        # (logged after the return).
        self.assertTrue(any("Starting worker FINAL_LOG_PRINT, UP step"
                            in ln for ln in lines))
        self.assertFalse(any("Completed UP step for FINAL_LOG_PRINT"
                             in ln for ln in lines))
        self.assertTrue(any("Completed UP step for PLOT" in ln for ln in lines))
        self.assertIn("StateMachine initialized.", lines[0])
        # No FINAL_LOG_PRINT no-op line (the enabled path) — and
        # neither the "full log written" confirmation nor the
        # "Completed" line (both logged AFTER the write). Other
        # levels' no-op notes (e.g. "PLOT skipped") are expected
        # content of the full log.
        self.assertFalse(any("FINAL_LOG_PRINT skipped" in ln for ln in lines))
        self.assertFalse(any("full log written" in ln for ln in lines))
        # The line count == the buffer at the write (the final
        # buffer minus the two trailing post-write lines).
        self.assertEqual(len(lines), len(self.rlm.sm.logs) - 2)


if __name__ == '__main__':
    unittest.main()
