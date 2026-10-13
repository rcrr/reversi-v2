#!/usr/bin/env python3
#
# suite_audit.py
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

"""suite_audit.py — the per-module suite counter (a MEASUREMENT tool).

WHAT IT IS: a MEASUREMENT tool, the sibling of wsutils/measure_suite.py
(the timing instrument, wsutils.md §6): it makes no assertions. It runs every test module of
run_utests.sh ON ITS OWN, under the same environment as the pre-commit
(LONG=1, the live DB), and prints `<module> <ran>/<fail>/<skip>` — the
numbers the overview's Suite cells must carry. It is the SUITE WRAPPER of
the pre-commit gate (R-210): the only path that writes the timestamped
measurement file the overview auditor reads. It produced the D-243 audit
findings (test_board, test_client, test_hlp_random_play stale).

USAGE (from the workspace root):
  LONG=1 .venv/bin/python wsutils/suite_audit.py
  # the same output is also written to scratch/suite_audit.txt (a
  # timestamp line + the table; gitignored, the gate input)

SAFETY: it writes the measurement artifact under scratch/ (gitignored; never the tracked tree).

ORIGIN: D-243 (the Suite-cell audit); promoted to wsutils/ at D-248; the pre-commit gate wave
(D-417/D-419 review): the module-regex fix for the runner reformat, the timestamp, the scratch
home, the gate input.
"""

import os
import re
import sys
import unittest
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))  # the `reversi` package
sys.path.insert(0, ROOT)  # the `test.reversi.*` modules (workspace root)


def modules():
    src = open(os.path.join(ROOT, 'run_utests.sh'), encoding='utf-8').read()
    # the current runner format (test.reversi.NAME — the reformat broke the
    # original reversi.test.NAME pattern, which silently matched nothing)
    return re.findall(r'^\s*(test\.reversi\.[\w.]+)\s*$', src, re.M)


def main():
    out = [f'# {datetime.now().astimezone().isoformat(timespec="seconds")}']
    for name in modules():
        mod = __import__(name, fromlist=['x'])
        suite = unittest.defaultTestLoader.loadTestsFromModule(mod)
        runner = unittest.TextTestRunner(stream=open(os.devnull, 'w'), verbosity=0)
        res = runner.run(suite)
        ran = res.testsRun
        fail = len(res.failures) + len(res.errors)
        skip = len(res.skipped)
        out.append(f'{name} {ran}/{fail}/{skip}')
        print(out[-1], flush=True)
    # the artifact is the gate input: scratch/ (gitignored, never the tracked
    # tree) — wsutils/overview_audit.py reads it
    dest = os.path.join(ROOT, 'scratch')
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, 'suite_audit.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
