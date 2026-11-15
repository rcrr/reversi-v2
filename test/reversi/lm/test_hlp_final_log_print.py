#
# test_hlp_final_log_print.py
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

# How to run the hlp_final_log_print unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.lm.test_hlp_final_log_print
#

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from reversi.lm.hlp_final_log_print import hlp_final_log_print_write_log
from reversi.tools.state_machine import Relevance
from test.reversi.paths import CUSTOM_TMP_BASE


class TestWriteLog(unittest.TestCase):
    """The run-log writer on a mock ctx (the NO-DB idiom): the file, the parent dir, the echo event."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        # The base_dir sits in a NON-EXISTENT subdirectory: the writer must create it.
        self.base = Path(self._tmp.name) / "sub"
        self.events = []
        self.ctx = SimpleNamespace(
            cfg=SimpleNamespace(base_dir=str(self.base), log_file_name="run.log"),
            format_event_log=lambda rel: "L1\nL2\n",
            log_event=lambda rel, msg: self.events.append((rel, msg)),
        )

    def tearDown(self):
        self._tmp.cleanup()

    def test_writes_the_rendered_log(self):
        path = hlp_final_log_print_write_log(self.ctx)
        self.assertEqual(path, self.base / "run.log")
        self.assertEqual(path.read_text(encoding="utf-8"), "L1\nL2\n")

    def test_creates_the_parent_dir(self):
        hlp_final_log_print_write_log(self.ctx)
        self.assertTrue(self.base.is_dir())

    def test_logs_the_write_event(self):
        hlp_final_log_print_write_log(self.ctx)
        self.assertEqual(len(self.events), 1)
        rel, msg = self.events[0]
        self.assertEqual(rel, Relevance.DEBUG)
        self.assertIn("log written", msg)
        self.assertIn("2 lines", msg)


if __name__ == "__main__":
    unittest.main()
