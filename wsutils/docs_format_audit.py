#!/usr/bin/env python3
"""docs_format_audit.py — the mirror-doc format AUDITOR.

WHAT IT IS: a CHECK over the docs/ tree (a cross-tree one, like the hub
probe is for the pipeline). It audits every docs/**/*.md against
notes/docs_rules.md: the H1 against the source path, the prescribed
sections and their order (the source variant vs the test-doc variant),
the §4 forbidden patterns (provenance narrative, campaign tags,
FIXED/RESOLVED lists, line-count deltas, the global suite status, report
tenses), the size budget (60-120 lines; the hubs 150-200), the 120-char
width, the trailing whitespace, the split code spans and the per-table
ragged rows.

It lives in the ROOT wsutils/ (the workspace utilities) — NOT in the package's
src/reversi/tools/ (that one ships with the library, D-133), and NOT in
probes/ (which holds the per-module verification apparatus). Run it when
the mirrors change: the D-239 campaign used it to find the stale cells,
the split spans and the ragged tables.

USAGE (from the workspace root):
  .venv/bin/python wsutils/docs_format_audit.py             summary by kind
  .venv/bin/python wsutils/docs_format_audit.py --verbose   per file

Origin: D-239 (the mirror-format audit); promoted to tools/ at D-248.
"""

import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC_SECTIONS = ['API', 'Architecture', 'Verified invariants', 'Open issues', 'Conventions', 'Integration']
TEST_SECTIONS = ['Coverage', 'Goldens pinned', 'Conventions', 'Integration']
HUBS = {'reversi/board.py', 'reversi/pattern.py', 'reversi/lm/logistic_model.py',
        'reversi/tools/state_machine.py'}

FORBIDDEN = [
    (re.compile(r'\bbrought in\b', re.I), 'provenance: "brought in"'),
    (re.compile(r'[Aa]nalysis date'), 'provenance: "analysis date"'),
    (re.compile(r'\bsession \d+\b'), 'provenance: "session N"'),
    (re.compile(r'\b(pre|post)[- ]D-\d{3}'), 'provenance: "pre/post D-NNN"'),
    (re.compile(r'^\s*-?\s*(FIXED|RESOLVED)\b|\b(FIXED|RESOLVED)\s*:'), 'a FIXED/RESOLVED list'),
    (re.compile(r'\d+\s*(?:→|->)\s*\d+\s*lines'), 'a line-count delta'),
    (re.compile(r'\bSuite status\b'), 'the global suite status'),
    (re.compile(r'\bStatus:\s*(analyzed|untouched)'), 'a report tense'),
    (re.compile(r'\bD-\d{3}\s+T\d+\b'), 'a campaign tag in prose'),
]


def docs():
    out = []
    for base, _dirs, files in os.walk(os.path.join(ROOT, 'docs')):
        for f in files:
            if f.endswith('.md'):
                out.append(os.path.relpath(os.path.join(base, f), ROOT))
    return sorted(out)


def source_of(path):
    """docs/src/reversi/X.md -> reversi/X.py; docs/test/reversi/X.md -> test/reversi/X.py"""
    if path.startswith('docs/src/'):
        rel = path[len('docs/src/'):]
    else:
        rel = path[len('docs/'):]
    return rel[:-3] + '.py'


def sections(lines):
    return [l[3:].strip() for l in lines if l.startswith('## ')]


def audit(path, verbose=False):
    lines = open(path, encoding='utf-8').read().split('\n')
    body = [l for l in lines if not l.startswith('|')]
    issues = []
    h1 = lines[0] if lines else ''
    want = '# ' + source_of(path)
    if h1 != want:
        issues.append(f'H1 is {h1[:60]!r}, expected {want!r}')
    # the `> State:` line was RETIRED (D-240): the header is the H1 + the what-it-is paragraph
    secs = sections(lines)
    is_test = '/test/' in path and os.path.basename(path).startswith('test_')
    expected = TEST_SECTIONS if is_test else SRC_SECTIONS
    missing = [s for s in expected if s not in secs]
    unknown = [s for s in secs if s not in expected and s != 'Appendix — line reference']
    if missing:
        issues.append('missing sections: ' + ', '.join(missing))
    if unknown:
        issues.append('unexpected sections: ' + ', '.join(unknown))
    # the order must follow the prescribed one
    order = [s for s in secs if s in expected]
    if order != [s for s in expected if s in order]:
        issues.append('sections out of order: ' + ' · '.join(order))
    for rx, what in FORBIDDEN:
        for i, l in enumerate(lines):
            if rx.search(l):
                issues.append(f'{what} at line {i + 1}: {l.strip()[:70]!r}')
                break
    n = len(lines) - 1
    lo, hi = (150, 200) if source_of(path) in HUBS else (60, 120)
    if is_test:
        lo = 25          # the test mirrors are maps, not prose: the 60-line floor does not apply
    if not (lo <= n <= hi):
        issues.append(f'size {n} lines (the budget is {lo}-{hi})')
    wide = [i + 1 for i, l in enumerate(body) if len(l) > 120]
    if wide:
        issues.append(f'{len(wide)} line(s) over 120 chars: {wide[:5]}')
    tw = [i + 1 for i, l in enumerate(lines) if l != l.rstrip()]
    if tw:
        issues.append(f'trailing whitespace at lines {tw[:5]}')
    unbal = [i + 1 for i, l in enumerate(lines)
             if not l.lstrip().startswith('```') and l.count('`') % 2]
    if unbal:
        issues.append(f'unbalanced code span at lines {unbal[:5]}')
    # the rows of ONE table must share the pipe count (a table = a run of rows)
    def pipes(l):
        return len(re.findall(r'(?<!\\)\|', l))       # the escaped \| is not a separator
    runs, run = [], []
    for l in lines:
        if l.strip().startswith('|') and l.strip().endswith('|'):
            run.append(pipes(l))
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    for i, r in enumerate(runs):
        if len(set(r)) > 1:
            issues.append(f'table {i + 1} has ragged rows: pipe counts {sorted(set(r))}')
    return issues, n


def main():
    verbose = '--verbose' in sys.argv
    rows = []
    for path in docs():
        issues, n = audit(path)
        rows.append((path, n, issues))
    clean = [r for r in rows if not r[2]]
    print(f'{len(rows)} mirror docs audited — {len(clean)} with no finding, {len(rows) - len(clean)} with findings')
    kinds = Counter()
    for _p, _n, issues in rows:
        for i in issues:
            kinds[re.sub(r'(line \d+|lines \[[^\]]*\]|: .*)$', '', i).strip()] += 1
    print('\nfindings by kind:')
    for k, v in kinds.most_common():
        print(f'  {v:3d}  {k}')
    if verbose:
        print('\nper file:')
        for path, n, issues in rows:
            if issues:
                print(f'  {path} ({n} lines)')
                for i in issues:
                    print(f'      - {i}')


if __name__ == '__main__':
    main()
