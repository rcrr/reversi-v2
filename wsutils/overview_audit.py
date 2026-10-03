#!/usr/bin/env python3
"""overview_audit.py — the overview bookkeeping auditor (a CHECK tool).

WHAT IT IS: a CHECK tool, the sibling of wsutils/docs_format_audit.py: it verifies that the four
overview bookkeeping lists in notes/overview.md agree with the tracked tree, in BOTH directions.
It makes no assertions on content (the State cell prose, the Current state bullets are out of scope):
- Source files table:  one row for every .py under src/ (no more, no less), each Doc cell resolves.
- Test files table:    one row for every .py under test/ (no more, no less), each Doc cell resolves.
- Test data bullets:   one bullet for every file under test/reversi/data/ (no more, no less).
- Index bullets:       every notes/-path reference resolves, and every open top-level notes/ file
                       (or its directory) is listed.
Writes nothing (a report on stdout). Exit 0 = clean, 1 = at least one mismatch.

USAGE (from the workspace root):
  .venv/bin/python wsutils/overview_audit.py

SAFETY: writes nothing.

ORIGIN: the D-417/D-419 governance review — the overview table drift found by user audit (D-419)
was the motivating case; promotion to wsutils/ in the same governance wave.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVERVIEW = os.path.join(ROOT, 'notes', 'overview.md')
TEST_DATA_DIR = os.path.join(ROOT, 'test', 'reversi', 'data')


def tracked():
    out = set()
    for line in os.popen(f'git -C {ROOT} ls-files').read().splitlines():
        if line:
            out.add(line)
    return out


def region(lines, start, ends):
    """The lines after the H2 `start`, up to the first following H2 in `ends` (or EOF)."""
    out, on = [], False
    for ln in lines:
        if ln.startswith('## '):
            if on:
                break
            if ln.startswith(start):
                on = True
                continue
        if on:
            out.append(ln)
    return out


def data_region(lines):
    """The Test data block: the plain paragraph opener under the Test files table, up to the next H2."""
    out, on = [], False
    for ln in lines:
        if ln.startswith('Test data (test/reversi/data/):'):
            on = True
            continue
        if on and ln.startswith('## '):
            break
        if on:
            out.append(ln)
    return out


def unescape(name):
    return name.replace('\\_', '_')


def doc_target(cell):
    m = re.search(r'\(([^)]+)\)', cell)
    return unescape(m.group(1)) if m else None


def overview_lists():
    lines = open(OVERVIEW, encoding='utf-8').read().splitlines()
    src_rows, test_rows = [], []
    for ln in region(lines, '## Source files', None):
        m = re.match(r'^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$', ln)
        if m and m.group(1) != 'File' and set(m.group(1)) != {'-'}:
            src_rows.append((m.group(1), m.group(3)))
    for ln in region(lines, '## Test files', None):
        m = re.match(r'^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$', ln)
        if m and m.group(1) != 'File' and set(m.group(1)) != {'-'}:
            test_rows.append((m.group(1), m.group(3), m.group(4)))
    data_bullets = [m.group(1) for ln in data_region(lines) if (m := re.match(r'^- `([^`]+)`', ln))]
    idx_refs = [unescape(r) for r in re.findall(r'notes/[\w./\\-]*', '\n'.join(region(lines, '## Index', None)))]
    return src_rows, test_rows, data_bullets, idx_refs


def main():
    issues = []
    tree = tracked()

    src_rows, test_rows, data_bullets, idx_refs = overview_lists()

    src_over = {unescape(p) for p, _ in src_rows}
    test_over = {unescape(p) for p, _, _ in test_rows}

    src_tree = {p for p in tree if p.startswith('src/') and p.endswith('.py') and not p.endswith('__init__.py')}
    test_tree = {p for p in tree if p.startswith('test/') and p.endswith('.py') and not p.endswith('__init__.py')}
    data_tree = {n for n in os.listdir(TEST_DATA_DIR) if os.path.isfile(os.path.join(TEST_DATA_DIR, n))}

    for p in sorted(src_tree - src_over):
        issues.append(f'Source files: tracked {p} has no overview row')
    for p in sorted(src_over - src_tree):
        issues.append(f'Source files: overview row {p} is not a tracked file')
    for p, doc in src_rows:
        d = doc_target(doc)
        if d is None or d not in tree:
            issues.append(f'Source files: {p} doc link {doc} does not resolve')

    for p in sorted(test_tree - test_over):
        issues.append(f'Test files: tracked {p} has no overview row')
    for p in sorted(test_over - test_tree):
        issues.append(f'Test files: overview row {p} is not a tracked file')
    for p, _, doc in test_rows:
        d = doc_target(doc)
        if d is None or d not in tree:
            issues.append(f'Test files: {p} doc link {doc} does not resolve')

    data_over = {unescape(b) for b in data_bullets}
    for p in sorted(data_tree - data_over):
        issues.append(f'Test data: tracked test/reversi/data/{p} has no overview bullet')
    for p in sorted(data_over - data_tree):
        issues.append(f'Test data: overview bullet {p} is not a tracked file')

    listed_dirs = {r for r in idx_refs if r.endswith('/')}
    for r in sorted(set(idx_refs)):
        if os.path.exists(os.path.join(ROOT, r)):
            continue
        parent = r.rsplit('/', 1)[0]
        if any(ld for ld in listed_dirs if r.startswith(ld) and ld != r):
            continue  # inside a listed directory (e.g. the hist volumes)
        issues.append(f'Index: reference {r} does not resolve')
    for name in sorted(os.listdir(os.path.join(ROOT, 'notes'))):
        if name.endswith('.md') and os.path.isfile(os.path.join(ROOT, 'notes', name)):
            if not any(r == f'notes/{name}' or r.startswith(f'notes/{name}/') or r == f'notes/{name}'
                       for r in idx_refs):
                issues.append(f'Index: notes/{name} is not listed')

    # The Suite column vs the latest suite measurement (the R-210 gate input):
    # the file is written by the suite wrapper (wsutils/suite_audit.py). Absent
    # = red (fail-closed); a count that does not agree with the measurement = red.
    measure = os.path.join(ROOT, 'scratch', 'suite_audit.txt')
    counts = {}
    if os.path.isfile(measure):
        for ln in open(measure, encoding='utf-8').read().splitlines():
            m = re.match(r'^(test\.reversi\.[\w.]+)\s+(\d+/\d+/\d+)$', ln.strip())
            if m:
                counts[m.group(1)] = m.group(2)
    if not os.path.isfile(measure):
        issues.append('Suite: scratch/suite_audit.txt is missing — run the suite wrapper '
                      '(wsutils/suite_audit.py) first')
    elif not counts:
        issues.append('Suite: the measurement file has no table lines — re-run the suite wrapper')
    else:
        row_by_module = {}
        for p, suite, _ in test_rows:
            parts = suite.split('/')
            if len(parts) == 5:
                row_by_module[unescape(p)[:-3].replace('/', '.')] = '/'.join(parts[:3])
        for mod in sorted(counts):
            got = row_by_module.get(mod)
            if got is None:
                issues.append(f'Suite: measurement module {mod} has no overview row with counts')
            elif got != counts[mod]:
                issues.append(f'Suite: overview says {got} for {mod} but the measurement says {counts[mod]}')
        for mod in sorted(row_by_module):
            if mod not in counts and row_by_module[mod] != '0/0/0':
                issues.append(f'Suite: row for {mod} claims counts but the module is not in the measurement')

    if issues:
        for i in issues:
            print(f'OVERVIEW AUDIT RED: {i}')
        print(f'{len(issues)} mismatch(es) — fix the overview lists, then re-run.')
        sys.exit(1)
    print(f'overview audit OK: {len(src_over)} source rows, {len(test_over)} test rows, '
          f'{len(data_over)} data bullets, {len(set(idx_refs))} index references, '
          f'{len(counts)} suite measurements — all consistent.')


if __name__ == '__main__':
    main()
