#!/usr/bin/env python3
"""suite_audit.py — the per-module suite counter (a MEASUREMENT tool).

WHAT IT IS: a MEASUREMENT tool, the sibling of wsutils/measure_suite.py
(the timing instrument, wsutils.md §6): it makes no assertions. It runs every test module of
run_utests.sh ON ITS OWN, under the same environment as the pre-commit
(LONG=1, the live DB), and prints `<module> <ran>/<fail>/<skip>` — the
numbers the overview's Suite cells must carry. It produced the D-243
audit findings (test_board, test_client, test_hlp_random_play stale).

USAGE (from the workspace root):
  LONG=1 .venv/bin/python wsutils/suite_audit.py
  # the same output is also written to build/tmp/suite_audit.txt

Origin: D-243 (the Suite-cell audit); promoted to tools/ at D-248.
"""

import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))


def modules():
    src = open(os.path.join(ROOT, 'run_utests.sh'), encoding='utf-8').read()
    return re.findall(r'^\s*(reversi\.test\.\w+)\s*$', src, re.M)


def main():
    out = []
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
    # the artifact goes under build/tmp (the D-065 base, as the test and probe
    # artifacts do), never in the tracked tree
    dest = os.path.join(ROOT, 'build', 'tmp')
    os.makedirs(dest, exist_ok=True)
    open(os.path.join(dest, 'suite_audit.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
