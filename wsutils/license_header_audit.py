#!/usr/bin/env python3
#
# license_header_audit.py
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

"""license_header_audit.py — the license-header guard (a CHECK tool).

WHAT IT IS: a read-only CHECK over the tracked SOURCE files (every .py, the .sh scripts, the
data .json fixtures — the R-591 scope): each must carry the standard GPL header as its first
lines (after the shebang, when there is one), with the six marker lines in order —
the FILE_NAME line (the basename), the "part of the reversi program" line, the project URL
line, the Author line, the Copyright line (a 4-digit year) — inside the first 12 lines.
The .json fixtures use the C-style /* ... */ variant of the same markers.

USAGE (from the workspace root):
  .venv/bin/python wsutils/license_header_audit.py                # every tracked source file
  .venv/bin/python wsutils/license_header_audit.py <file> ...    # a subset (the pre-commit gate)

SAFETY: writes nothing. Exit 0 = every header is present and correct; 1 = at least one
missing / malformed (fail-closed, like notes_lint).

ORIGIN: the D-541 public-push wave — the R-591 enforcement (the D-540 migration put the
headers on every file; this guard keeps it true at every checkin).
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

URL = 'http://github.com/rcrr/reversi-v2'

#: (marker regex, label) — the ten lines every header must carry, in this ORDER, starting at the
#: first line (the shebang, when present, does not count). The template: the bare comment line,
#: the FILE_NAME line, the bare separator, the three identity lines, the bare separator, the
#: Author + Copyright lines, the bare separator, the License marker.
HASH_MARKERS = [
    (re.compile(r'^#$'), 'the opening bare # line'),
    (re.compile(r'^# [A-Za-z0-9_.-]+$'), 'the FILE_NAME line'),
    (re.compile(r'^#$'), 'the separator # line'),
    (re.compile(r'^# This file is part of the reversi program$'), 'the "part of the reversi program" line'),
    (re.compile(rf'^# {re.escape(URL)}$'), 'the project URL line'),
    (re.compile(r'^#$'), 'the separator # line'),
    (re.compile(r'^# Author Roberto Corradini mailto:rob_corradini@yahoo\.it$'), 'the Author line'),
    (re.compile(r'^# Copyright \d{4} Roberto Corradini\. All rights reserved\.$'), 'the Copyright line'),
    (re.compile(r'^#$'), 'the separator # line'),
    (re.compile(r'^# License$'), 'the License marker'),
]

C_MARKERS = [
    (re.compile(r'^/\*$'), 'the opening /* line'),
    (re.compile(r'^\s*\* [A-Za-z0-9_.-]+$'), 'the FILE_NAME line'),
    (re.compile(r'^\s*\*\s*$'), 'the separator * line'),
    (re.compile(r'^\s*\* This file is part of the reversi program$'), 'the "part of the reversi program" line'),
    (re.compile(rf'^\s*\* {re.escape(URL)}$'), 'the project URL line'),
    (re.compile(r'^\s*\*\s*$'), 'the separator * line'),
    (re.compile(r'^\s*\* Author Roberto Corradini mailto:rob_corradini@yahoo\.it$'), 'the Author line'),
    (re.compile(r'^\s*\* Copyright \d{4} Roberto Corradini\. All rights reserved\.$'), 'the Copyright line'),
    (re.compile(r'^\s*\*\s*$'), 'the separator * line'),
    (re.compile(r'^\s*\* License$'), 'the License marker'),
]


def tracked_sources():
    out = subprocess.run(
        ['git', '-C', ROOT, 'ls-files', '*.py', '*.sh', 'wsutils/hooks/*', 'test/reversi/data/*.json'],
        capture_output=True, text=True).stdout.split()
    return [f for f in out if os.path.isfile(os.path.join(ROOT, f))]


def audit(rel):
    """Return the list of problems for one file (empty = the header is correct)."""
    path = os.path.join(ROOT, rel)
    lines = open(path, encoding='utf-8').read().split('\n')
    start = 1 if lines and lines[0].startswith('#!') else 0
    window = lines[start:start + 12]
    markers = C_MARKERS if rel.endswith('.json') else HASH_MARKERS
    problems = []
    i = 0
    for rx, label in markers:
        if i >= len(window) or not rx.match(window[i]):
            problems.append(f'missing/out of order: {label} (found {window[i]!r} at line {start + i + 1})')
            return problems
        i += 1
    # the FILE_NAME line (the second line of the header) must carry THIS file's basename
    name = os.path.basename(rel)
    first = window[1].lstrip().lstrip('#* ').strip()
    if first != name:
        problems.append(f'the FILE_NAME line says {first!r}, the file is {name!r}')
    return problems


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    files = args if args else tracked_sources()
    bad = 0
    for rel in files:
        for p in audit(rel):
            bad += 1
            print(f'LICENSE HEADER RED: {rel}: {p}')
    if bad:
        print(f'{bad} problem(s) — fix the header(s), then re-run.')
        sys.exit(1)
    print(f'license header audit OK: {len(files)} source file(s), every header present and correct.')


if __name__ == '__main__':
    main()
