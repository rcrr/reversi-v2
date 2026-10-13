#!/usr/bin/env python3
#
# measure_suite.py
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

"""measure_suite.py — the suite-level TIMING measurement tool.

WHAT IT IS: a MEASUREMENT tool (wsutils.md §1) — it makes NO a/b/c
checks and no assertions. It
runs the whole unit-test suite (test.reversi, a live regab DB is required
for the full picture) with a custom TestResult and records
every test's duration in milliseconds. The builtin
`unittest --durations` cannot be used for this: it hides
sub-1 ms entries and reports seconds.

Why it exists: the D-130 tiering (the <10 s fast-tier target,
LONG = the DB-gated pipeline) needs a per-test timing baseline
to see where the suite's time actually goes (the 2026-09-07
measurement: 40.6 s of 44.5 s in the 14 DB-dependent files).
Run it whenever a timing question comes up (a slow-tier
change, a new heavy test, the <10 s budget check).

USAGE (from the workspace root):
  .venv/bin/python wsutils/measure_suite.py

SAFETY: writes NOTHING in the tracked tree — the single artifact is
build/tmp/test_durations.txt (the D-065 base): the per-test ms (sorted
descending), the per-module aggregate table, and the skip census with
reasons.

ORIGIN: D-132 (the timing instrument of the D-130 tiering, graduated
from scratch/ to probes/ on Roberto's GO); moved to tools/ at D-250,
with the artifact path (scratch/ -> build/tmp).
"""

import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))


class TimedResult(unittest.TestResult):
    """TestResult that records (ms, test-id, status) per test."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self._t0 = 0.0
        self._cur = None

    def startTest(self, test):
        super().startTest(test)
        self._cur = test
        self._t0 = time.perf_counter()

    def _record(self, status):
        if self._cur is None:
            return
        ms = (time.perf_counter() - self._t0) * 1000.0
        self.rows.append((ms, self._cur.id(), status))

    def addSuccess(self, test):
        self._record("ok")
        super().addSuccess(test)

    def addError(self, test, err):
        self._record("error")
        super().addError(test, err)

    def addFailure(self, test, err):
        self._record("fail")
        super().addFailure(test, err)

    def addSkip(self, test, reason):
        self._record("skip")
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self._record("xfail-ok")
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self._record("unexpected")
        super().addUnexpectedSuccess(test)


def main():
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "test"), top_level_dir=str(ROOT))
    result = TimedResult()
    t0 = time.perf_counter()
    suite.run(result)
    wall = (time.perf_counter() - t0) * 1000.0

    rows = sorted(result.rows, key=lambda r: -r[0])
    modules = {}
    for ms, tid, status in rows:
        # tid = "test.reversi[.zone].test_x.Class.test_y"
        parts = tid.split(".")
        mod = next((p for p in parts if p.startswith("test_")), "?")
        agg = modules.setdefault(mod, [0.0, 0, 0])
        agg[0] += ms
        agg[1] += 1
        if status != "ok":
            agg[2] += 1

    out = []
    out.append("# test suite (test.reversi) — per-test durations")
    out.append("# Full run (regab DB live when available), "
               "no PERF/LONG env vars")
    out.append(f"# Total: {len(rows)} tests, wall {wall:.0f} ms")
    out.append(f"# Result: failures={len(result.failures)} "
               f"errors={len(result.errors)} "
               f"skipped={len(result.skipped)}")
    out.append("")
    out.append("## Per-test (ms, descending)")
    out.append("rank  ms       status  test-id")
    for i, (ms, tid, status) in enumerate(rows, 1):
        out.append(f"{i:<5} {ms:>9.1f}  {status:<4}  {tid}")
    out.append("")
    out.append("## Per-module aggregates (ms total, tests, non-ok)")
    for mod, (ms, n, bad) in sorted(modules.items(),
                                    key=lambda kv: -kv[1][0]):
        out.append(f"{ms:>10.1f}  {n:>4}  {bad:<3}  {mod}")
    out.append("")
    out.append("## Skip census")
    for test, reason in result.skipped:
        out.append(f"{test.id()}  ->  {reason}")
    out.append("")

    dest = ROOT / "build" / "tmp" / "test_durations.txt"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out) + "\n")
    print(f"written: {dest} ({len(rows)} tests, wall {wall:.0f} ms, "
          f"skipped {len(result.skipped)})")


if __name__ == "__main__":
    main()
