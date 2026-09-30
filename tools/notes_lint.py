#!/usr/bin/env python3
"""tools/notes_lint.py — the format guard for the notes files (read-only, D-365).

Lints the workspace notes files against their rigid grammars:
  notes/decisions.md + the closed volumes (decisions_NNN.md) -> notes/decisions_rules.md
  notes/rules.md                                             -> the Governance block inside it
  notes/log_NNN.md                                           -> notes/log_rules.md
It exits 1 on any violation. Run it after every notes edit — red means no commit.

Usage:
    python tools/notes_lint.py              # decisions.md + rules.md + the open journal
    python tools/notes_lint.py FILES...     # any notes files (the closed volumes included)

The session's three bug classes are permanent codes:
    BLANK   one blank line before every D-NNN header, no double blank lines     [the D-364 class]
    ESC     no bare _ and no unpaired * outside code spans — the D-209 escape
            rule, extended to the snake_case identifiers (D-365)                [the D-363 class]
    TRAP    no continuation line starting with a token that notes_format would
            misread as a new block (digit+dot, dash, hash, pipe, D-NNN |)      [the 13-space class]
Plus: HEADER / INDENT / SEQ (decisions), RHEAD / RTITLE / RSPACE / DPOINTER /
RSEQ (rules), JH1 / JPOINTER / JSESSION / JINDENT / JBLANK (journals), WIDTH,
CANON (idempotence under notes_format --write) and EOF.
"""
import re
import subprocess
import sys
from pathlib import Path

WIDTH = 120
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

DEC_ID = re.compile(r'^D-(\d{3}) \| ')
DEC_HEADER = re.compile(r'^D-\d{3} \| \d{4}-\d{2}-\d{2} \| \S')
R_TITLE = re.compile(r'^\*\*R-(\d{3})(?:\.(\d+))? — .+\*\*$')
J_H1 = re.compile(r'^# Session journal — volume \d{3} \(sessions .+\)$')
J_POINTER = 'Format rules: notes/log_rules.md (rigid — follow when editing this file).'
J_SESSION = re.compile(r'^## \d{4}-\d{2}-\d{2} — session (\d+) \(.+\)$')
TRAP = re.compile(r'(?:\d+\.\s|[-|#]\s|\|\s|[DI]-\d{3}\s+\|)')
D_REF = re.compile(r'D-\d{3}')


def plain_of(line):
    """The line with every backtick code span removed."""
    return ''.join(line.split('`')[0::2])


def esc_issues(line):
    """Count the ESC violations in one line: bare underscores and unpaired
    asterisks OUTSIDE code spans (a balanced **pair** is the deliberate bold
    quote; an escaped \\_ or \\* is the D-209 form)."""
    plain = plain_of(line)
    n = len(re.findall(r'(?<!\\)_', plain))
    leftover = re.sub(r'\*\*[^*]*\*\*', '', plain)
    n += len(re.findall(r'(?<!\\)\*', leftover))
    return n


def canon_ok(path):
    """True when the file IS its own canonical rendering: notes_format --write
    applied to a temp copy must reproduce the file byte-for-byte. (The tool's
    --check is idempotence-of-the-canonical-form only — it passes even on a
    non-canonical file, so it cannot serve as the guard here.)"""
    import tempfile
    text = path.read_text()
    with tempfile.NamedTemporaryFile('w', suffix='.md', delete=False) as tf:
        tf.write(text)
        tmp = tf.name
    try:
        subprocess.run([sys.executable, str(HERE / 'notes_format.py'), '--write', tmp],
                       capture_output=True, text=True)
        return Path(tmp).read_text() == text
    finally:
        Path(tmp).unlink(missing_ok=True)


def common_tail(path, lines, text, v):
    """The WIDTH / EOF checks shared by every grammar."""
    for n, line in enumerate(lines, 1):
        if len(line) > WIDTH:
            v.append((n, 'WIDTH', f'{len(line)} chars (max {WIDTH})'))
    if not text.endswith('\n'):
        v.append((len(lines), 'EOF', 'the file must end with a newline'))
    elif lines and lines[-1].strip() == '':
        v.append((len(lines), 'EOF', 'trailing blank line at EOF'))


def lint_decisions(path, lines, text):
    """notes/decisions_rules.md: one entry per decision; the header
    D-NNN | YYYY-MM-DD | the rationale; the continuation lines indented exactly
    9 spaces; a blank line before every entry; the D-numbers sequential."""
    v = []
    prev_num = None
    blanks = 0
    for n, line in enumerate(lines, 1):
        if line == '':
            blanks += 1
            if blanks > 1:
                v.append((n, 'BLANK', 'double blank line'))
            continue
        blanks = 0
        if DEC_ID.match(line):
            if lines[n - 2].strip() != '':
                v.append((n, 'BLANK', 'no blank line before the entry header'))
            if not DEC_HEADER.match(line):
                v.append((n, 'HEADER', 'malformed entry header'))
            num = int(DEC_ID.match(line).group(1))
            if prev_num is not None and num != prev_num + 1:
                v.append((n, 'SEQ', f'D-number not sequential (previous {prev_num})'))
            prev_num = num
        else:
            ind = len(line) - len(line.lstrip(' '))
            if prev_num is None:  # the file intro: column 0 only
                if ind > 0:
                    v.append((n, 'INDENT', f'indented line in the file intro ({ind} spaces)'))
            elif ind == 9:
                if TRAP.match(line[9:]):
                    v.append((n, 'TRAP', 'continuation starts with a block-start token'))
            elif ind != 0:
                v.append((n, 'INDENT', f'continuation indent is {ind} spaces (must be 9)'))
            else:
                v.append((n, 'INDENT', 'stray column-0 line inside an entry'))
        e = esc_issues(line)
        if e:
            v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
    common_tail(path, lines, text, v)
    if not canon_ok(path):
        v.append((0, 'CANON', 'not idempotent under notes_format --write'))
    return v


def lint_rules(path, lines, text):
    """The Governance block: a rule is a bold title line **R-NNN — the topic**
    (or **R-NNN.N — ...**), a blank line, and the description — or one bold
    line; two blank lines between one rule and the next, one before a section.
    The D-numbers in prose are the quoted examples only."""
    v = []
    if not lines or not lines[0].startswith('# rules.md'):
        v.append((1, 'RHEAD', 'the first line must be the rules.md H1'))
    in_intro = True
    last_kind = None    # 'title' | 'desc' | 'section'
    last_n = 0
    blanks = 0
    rnums = []
    for n, line in enumerate(lines, 1):
        if line == '':
            blanks += 1
            continue
        b = blanks  # the run just closed — consumed by the spacing check below
        blanks = 0
        if in_intro:
            if line.startswith('## '):
                in_intro = False
                kind = 'section'
            elif line[0] == ' ':
                v.append((n, 'INDENT', 'indented line in the file intro'))
                kind = 'desc'
            else:
                kind = 'desc'
        else:
            if line.startswith('## '):
                kind = 'section'
            elif R_TITLE.match(line):
                kind = 'title'
            else:
                if line[0] == ' ':
                    v.append((n, 'INDENT', 'indented line in a rule block'))
                kind = 'desc'
        if not in_intro:
            if kind == 'desc':
                if last_kind is None:
                    v.append((n, 'RSPACE', 'a description line before any rule'))
                elif last_kind == 'section':
                    v.append((n, 'RSPACE', 'a description line before the first rule of its section'))
                elif last_kind == 'desc' and b != 0:
                    v.append((n, 'RSPACE', f'{b} blank line(s) inside a rule description'))
                elif last_kind == 'title' and b != 1:
                    v.append((n, 'RSPACE', f'{b} blank line(s) between a title and its description (must be 1)'))
            elif kind == 'title':
                if last_kind is None:
                    v.append((n, 'RSPACE', 'a rule before any section'))
                elif last_kind == 'desc' and b != 2:
                    v.append((n, 'RSPACE', f'{b} blank line(s) between two rules (must be 2)'))
                elif last_kind == 'title' and b != 2:
                    v.append((n, 'RSPACE', f'{b} blank line(s) between two one-line rules (must be 2)'))
                elif last_kind == 'section' and b != 1:
                    v.append((n, 'RSPACE', f'{b} blank line(s) after a section header (must be 1)'))
                m = R_TITLE.match(line)
                rnums.append((int(m.group(1)), int(m.group(2) or 0)))
            elif kind == 'section':
                if last_kind is None:
                    pass  # the first section, right after the intro
                elif last_kind == 'section':
                    v.append((n, 'RSPACE', 'a section header directly follows another (empty section)'))
                elif last_kind == 'title' and b != 2:
                    v.append((n, 'RSPACE', f'{b} blank line(s) before a section after a one-line rule (must be 2)'))
                elif last_kind == 'desc' and b != 1:
                    v.append((n, 'RSPACE', f'{b} blank line(s) before a section header (must be 1)'))
        last_kind, last_n = kind, n
        e = esc_issues(line)
        if e:
            v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
    # the DPOINTER pass: a D-number in prose is a provenance leak — allowed only
    # inside a quoted example (the R-042 family) or a code span.
    for n, line in enumerate(lines, 1):
        s = re.sub(r'"[^"]*"', '', re.sub(r"'[^']*'", '', plain_of(line)))
        if D_REF.search(s):
            v.append((n, 'DPOINTER', 'a D-number outside a quoted example or code span'))
    for a, b in zip(rnums, rnums[1:]):
        if b <= a:
            v.append((0, 'RSEQ', f'R-numbers not increasing ({a} then {b})'))
    # the R-NNN.N sub-numbers sort inside their parent: (29, 0) < (29, 1) < (30, 0)
    common_tail(path, lines, text, v)
    if not canon_ok(path):
        v.append((0, 'CANON', 'not idempotent under notes_format --write'))
    return v


def lint_journal(path, lines, text):
    """notes/log_rules.md: the volume H1 + the pointer line; one
    '## YYYY-MM-DD — session N (title)' per session, N monotone; top-level
    '- ' bullets with their continuations at exactly 2 spaces, sub-bullets at
    2 (' - ') with their continuations at 4. Hand-wrapped by convention: no
    WIDTH and no CANON checks."""
    v = []
    if not J_H1.match(lines[0]):
        v.append((1, 'JH1', 'the first line must be the volume H1'))
    if len(lines) < 3 or lines[2] != J_POINTER:
        v.append((3, 'JPOINTER', 'missing or wrong format pointer line'))
    session = None
    in_sub = False
    for n, line in enumerate(lines, 1):
        if line == '':
            continue
        if line.startswith('## '):
            m = J_SESSION.match(line)
            if not m:
                v.append((n, 'JSESSION', 'malformed session header'))
            else:
                num = int(m.group(1))
                if session is not None and num <= session:
                    v.append((n, 'JSESSION', f'session number not increasing (previous {session})'))
                session = num
            in_sub = False
        elif line.startswith('# '):
            if n != 1:
                v.append((n, 'JH1', 'stray heading'))
        elif line == J_POINTER:
            pass  # the mandated verbatim pointer line (log_rules.md)
        elif line.startswith('  - '):
            in_sub = True
        elif line.startswith('- '):
            in_sub = False
        else:
            ind = len(line) - len(line.lstrip(' '))
            if ind == 2:
                in_sub = False
            elif ind == 4:
                if not in_sub:
                    v.append((n, 'JINDENT', 'a 4-space line outside a sub-bullet'))
            elif ind == 0:
                v.append((n, 'JINDENT', 'stray column-0 line (not a heading or a bullet)'))
            else:
                v.append((n, 'JINDENT', f'unsupported indent ({ind} spaces)'))
        # the H1 and the pointer line are mandated verbatim by log_rules.md —
        # their underscores (log_NNN) are not prose escapes
        if line != lines[0] and line != J_POINTER:
            e = esc_issues(line)
            if e:
                v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
    for n in range(1, len(lines) - 1):
        if lines[n] == '' and lines[n - 1] == '' and lines[n + 1] == '':
            v.append((n + 1, 'JBLANK', 'double blank line'))
    if not text.endswith('\n'):
        v.append((len(lines), 'EOF', 'the file must end with a newline'))
    return v


def kind_of(name):
    b = Path(name).name
    if b == 'rules.md':
        return 'rules'
    if re.fullmatch(r'decisions(_\d{3})?\.md', b):
        return 'decisions'
    if re.fullmatch(r'log_\d{3}\.md', b):
        return 'journal'
    return None


def main(argv):
    if len(argv) > 1:
        files = [Path(a) for a in argv[1:]]
    else:
        logs = [p for p in ROOT.glob('notes/log_*.md') if re.fullmatch(r'log_\d{3}\.md', p.name)]
        open_log = max(logs, key=lambda p: int(p.name[4:7])) if logs else None
        files = [ROOT / 'notes/decisions.md', ROOT / 'notes/rules.md']
        if open_log:
            files.append(open_log)
    linters = {'decisions': lint_decisions, 'rules': lint_rules, 'journal': lint_journal}
    total = 0
    for f in files:
        k = kind_of(f)
        if k is None:
            print(f'{f}: SKIP — not a recognized notes file')
            continue
        if not f.is_file():
            print(f'{f}: FAIL — missing')
            total += 1
            continue
        text = f.read_text()
        lines = text.split('\n')
        if lines and lines[-1] == '':
            lines = lines[:-1]
        v = linters[k](f, lines, text)
        if v:
            for ln, code, msg in sorted(v):
                print(f'{f}:{ln}: {code} — {msg}')
            print(f'{f}: FAIL ({len(v)} violations)')
            total += len(v)
        else:
            print(f'{f}: OK')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
