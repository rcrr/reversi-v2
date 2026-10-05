#!/usr/bin/env python3
"""wsutils/notes_lint.py — the format guard for the notes files (a CHECK tool, read-only).

WHAT IT IS: a CHECK tool — the notes format guard (R-200). It IMPLEMENTS THE GRAMMATICAL CHECKS of the notes
formats, each per its rigid grammar:
  notes/decisions.md + notes/hist_decisions/decisions_NNN.md — the entry grammar (notes/decisions_rules.md)
  notes/rules.md — the register grammar (the Governance block inside it)
  notes/design_principles.md — the DP register grammar (the design principles in force)
  notes/log.md + notes/hist_log/log_NNN.md — the session-block grammar (notes/log_rules.md)
  notes/overview.md — the seven-section + table grammar (notes/overview_rules.md)
  the domain rule files (overview_rules.md, decisions_rules.md, log_rules.md, docs_rules.md,
  probe_rules.md, wsutils.md, naming.md) — the H1 + section + bullet grammar
  notes/ideas.md + notes/ideas_closed.md — the D-235 entry grammar (I-NNN | status | ...)
One guard, one entry point, per-format linters — never one tool per format. The default set covers every CURRENT
notes file; the closed volumes (notes/hist_decisions/decisions_000..005, notes/hist_log/log_000..003) are linted
on explicit request (the append-frozen closed history, cleaned and green at D-368). Run it after every notes edit —
red means no commit (R-200).

The session's bug classes are permanent codes:
    BLANK   one blank line before every D-NNN header, no double blank lines     [the D-364 class]
    ESC     no bare _ and no unpaired * outside code spans — the D-209 escape
            rule, extended to the snake_case identifiers (D-365)                [the D-363 class]
    TRAP    no continuation line starting with a token that notes_format would
            misread as a new block (digit+dot, dash, hash, pipe, D-NNN |)      [the 13-space class]
    LISTMARK no line-leading + / * after up to 3 spaces of indent — Obsidian
            renders it as a nested list bullet (escape it: \\+ / \\*)          [the D-483 class]
Plus: HEADER / INDENT / SEQ (decisions), RHEAD / RTITLE / RSPACE / DPOINTER /
RSEQ (rules), DPH1 / DPSPACE / DPOINTER / DPSEQ (design), JH1 / JPOINTER / JSESSION / JINDENT / JBLANK
(journals), WIDTH,
CANON (idempotence under notes_format --write) and EOF.

USAGE (from the workspace root):
  .venv/bin/python wsutils/notes_lint.py               # the default set: every current notes file
  .venv/bin/python wsutils/notes_lint.py FILES...      # any notes files (the closed volumes included)

SAFETY: writes nothing. A read-only per-file report on stdout; exit 0 (green) / 1 (red).

Origin: D-365 (born directly in tools/ — the decisions, register and journal linters); D-367 (the full-format
extension: the overview, the domain rule files, the ideas); D-368 (the closed volumes green, the historical
linter extensions); D-484 (the LISTMARK line-start code).
"""
import re
import subprocess
import sys
from pathlib import Path

WIDTH = 120
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

DEC_ID = re.compile(r'^D-(\d{3,4})([a-z]?) \| ')
DEC_HEADER = re.compile(r'^D-\d{3,4}[a-z]? \| \d{4}-\d{2}-\d{2} \| \S')
R_TITLE = re.compile(r'^\*\*R-(\d{3})(?:\.(\d+))? — .+\*\*$')
DP_TITLE = re.compile(r'^\*\*DP-(\d{3})(?:\.(\d+))? — .+\*\*$')
J_H1 = re.compile(r'^# Session journal — volume \d{3} \(sessions .+\)$')
J_POINTER = 'Format rules: notes/log_rules.md (rigid — follow when editing this file).'
J_SESSION = re.compile(r'^## \d{4}-\d{2}-\d{2} — session (\d+) \(.+\)$')
TRAP = re.compile(r'(?:\d+\.\s|#\s|[DI]-\d{3,4}\s+\|)')
D_REF = re.compile(r'D-\d{3,4}')


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


LISTMARK = re.compile(r'^\s{0,3}[+*](?=\s|$)')


def listmark_issues(line):
    """Count the LISTMARK violations in one line: a line-leading + or * after
    up to 3 spaces of indent, OUTSIDE code spans — Obsidian renders it as a
    nested list bullet (the D-483 class; escape it to \\+ / \\*). A + or *
    not followed by a space (an inline plus, a ** bold opener) is not a list
    marker; the line-leading - is the journal's own bullet (intended)."""
    return len(LISTMARK.findall(plain_of(line)))


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
    """The WIDTH / EOF checks shared by every grammar. Table rows are exempt:
    one physical line per row is the table grammar itself (a markdown row
    cannot be wrapped), and the ~120 limit applies to the prose."""
    for n, line in enumerate(lines, 1):
        if line.startswith('|'):
            continue
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
    prev_key = None
    blanks = 0
    in_block = False
    for n, line in enumerate(lines, 1):
        if line == '':
            blanks += 1
            in_block = False
            if blanks > 1:
                v.append((n, 'BLANK', 'double blank line'))
            continue
        blanks = 0
        if DEC_ID.match(line):
            in_block = False
            if lines[n - 2].strip() != '':
                v.append((n, 'BLANK', 'no blank line before the entry header'))
            if not DEC_HEADER.match(line):
                v.append((n, 'HEADER', 'malformed entry header'))
            m = DEC_ID.match(line)
            key = (int(m.group(1)), m.group(2))  # D-156 < D-156b < D-157
            # strictly increasing: a historical gap (a D-number lost, D-152) is
            # allowed, a reuse or an out-of-order entry is not
            if prev_key is not None and key <= prev_key:
                v.append((n, 'SEQ', f'D-number not increasing (previous {prev_key[0]}{prev_key[1] or ""})'))
            prev_key = key
        else:
            ind = len(line) - len(line.lstrip(' '))
            if prev_key is None:  # the file intro: column 0 only
                if ind > 0:
                    v.append((n, 'INDENT', f'indented line in the file intro ({ind} spaces)'))
            elif ind == 9:
                if line.startswith('         | '):
                    in_block = True  # the D-237 FIELD line: the pipe is the marker
                elif line.startswith('         - '):
                    in_block = True  # an inline bullet: the tool's canonical form
                    # keeps its continuations at 11, so it is not a trap
                else:
                    in_block = False
                    if TRAP.match(line[9:]):
                        v.append((n, 'TRAP', 'continuation starts with a block-start token'))
            elif ind == 11:
                if not in_block:
                    v.append((n, 'INDENT', 'an 11-space line outside a block'))
            elif ind != 0:
                v.append((n, 'INDENT', f'continuation indent is {ind} spaces (must be 9)'))
            else:
                in_block = False
                v.append((n, 'INDENT', 'stray column-0 line inside an entry'))
        e = esc_issues(line)
        if e:
            v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
        lm = listmark_issues(line)
        if lm:
            v.append((n, 'LISTMARK', f'{lm} line-leading + / * (the Obsidian nested-bullet trap)'))
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
    # inside a quoted example or a code span.
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


def lint_design(path, lines, text):
    """notes/design_principles.md: the DP register — the rules.md grammar with
    the '## ' sections optional: an H1, the intro prose (the Lifecycle and
    Governance blocks), then one or more design principles, each a bold title
    line, a blank line, the description; two blank lines between principles;
    the DP-numbers sequential by value."""
    v = []
    if not lines or not lines[0].startswith('# design_principles.md'):
        v.append((1, 'DPH1', 'the first line must be the design_principles.md H1'))
    in_intro = True
    seen = False
    last_kind = None    # 'title' | 'desc' | 'section'
    blanks = 0
    dpnums = []
    for n, line in enumerate(lines, 1):
        if line == '':
            blanks += 1
            continue
        b = blanks  # the run just closed — consumed by the spacing check below
        blanks = 0
        if in_intro:
            if line.startswith('## ') or DP_TITLE.match(line):
                in_intro = False
                kind = 'section' if line.startswith('## ') else 'title'
            elif line[0] == ' ':
                v.append((n, 'INDENT', 'indented line in the file intro'))
                kind = 'desc'
            else:
                kind = 'desc'
        else:
            if line.startswith('## '):
                kind = 'section'
            elif DP_TITLE.match(line):
                kind = 'title'
            else:
                if line[0] == ' ':
                    v.append((n, 'INDENT', 'indented line in a principle block'))
                kind = 'desc'
        if not in_intro:
            if kind == 'desc':
                if last_kind is None:
                    v.append((n, 'DPSPACE', 'a description line before any principle'))
                elif last_kind == 'section':
                    v.append((n, 'DPSPACE', 'a description line before the first principle of its section'))
                elif last_kind == 'desc' and b != 0:
                    v.append((n, 'DPSPACE', f'{b} blank line(s) inside a principle description'))
                elif last_kind == 'title' and b != 1:
                    v.append((n, 'DPSPACE', f'{b} blank line(s) between a title and its description (must be 1)'))
            elif kind == 'title':
                if not seen:
                    if b != 1:
                        v.append((n, 'DPSPACE', f'{b} blank line(s) between the intro and the first principle (must be 1)'))
                elif last_kind == 'desc' and b != 2:
                    v.append((n, 'DPSPACE', f'{b} blank line(s) between two principles (must be 2)'))
                elif last_kind == 'title' and b != 2:
                    v.append((n, 'DPSPACE', f'{b} blank line(s) between two one-line principles (must be 2)'))
                elif last_kind == 'section' and b != 1:
                    v.append((n, 'DPSPACE', f'{b} blank line(s) after a section header (must be 1)'))
                m = DP_TITLE.match(line)
                dpnums.append((int(m.group(1)), int(m.group(2) or 0)))
            elif kind == 'section':
                if last_kind == 'section':
                    v.append((n, 'DPSPACE', 'a section header directly follows another (empty section)'))
                elif last_kind == 'title' and b != 2:
                    v.append((n, 'DPSPACE', f'{b} blank line(s) before a section after a one-line principle (must be 2)'))
                elif last_kind == 'desc' and b != 1:
                    v.append((n, 'DPSPACE', f'{b} blank line(s) before a section header (must be 1)'))
        if kind in ('title', 'section'):
            seen = True
        last_kind = kind
        if n != 1:  # the H1 carries the file name (design_principles.md): not prose
            e = esc_issues(line)
            if e:
                v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
            lm = listmark_issues(line)
            if lm:
                v.append((n, 'LISTMARK', f'{lm} line-leading + / * (the Obsidian nested-bullet trap)'))
    # the DPOINTER pass: a D-number in prose is a provenance leak — allowed only
    # inside a quoted example or a code span.
    for n, line in enumerate(lines, 1):
        s = re.sub(r'"[^"]*"', '', re.sub("'[^']*'", '', plain_of(line)))
        if D_REF.search(s):
            v.append((n, 'DPOINTER', 'a D-number outside a quoted example or code span'))
    for a, b in zip(dpnums, dpnums[1:]):
        if b <= a:
            v.append((0, 'DPSEQ', f'DP-numbers not increasing ({a} then {b})'))
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
    state = {'sub': False, 'num': None, 'fence': False}
    free = False  # a historical "### " sub-section: column-0 prose is legal there
    for n, line in enumerate(lines, 1):
        if line.startswith('```'):
            state['fence'] = not state['fence']
            continue
        if state['fence']:
            continue
        if line == '':
            continue
        if line.startswith('### '):
            free = True  # the old journals used "### Step N" / "### I-NNN" sections
            state['sub'] = False
            state['num'] = None
        elif line.startswith('## '):
            free = False
            m = J_SESSION.match(line)
            if not m:
                v.append((n, 'JSESSION', 'malformed session header'))
            else:
                num = int(m.group(1))
                if session is not None and num <= session:
                    v.append((n, 'JSESSION', f'session number not increasing (previous {session})'))
                session = num
            state['sub'] = False
            state['num'] = None
        elif line.startswith('# '):
            free = False
            if n != 1:
                v.append((n, 'JH1', 'stray heading'))
            state['sub'] = False
            state['num'] = None
        elif line == J_POINTER:
            pass  # the mandated verbatim pointer line (log_rules.md)
        else:
            ind = len(line) - len(line.lstrip(' '))
            if ind == 0 and not (line.startswith('- ') or line.startswith(' - ')):
                if not free:
                    v.append((n, 'JINDENT', 'stray column-0 line (not a heading or a bullet)'))
            else:
                msg = prose_state_check(line, state)
                if msg:
                    v.append((n, 'JINDENT', msg))
        # the H1 and the pointer line are mandated verbatim by log_rules.md —
        # their underscores (log_NNN) are not prose escapes
        if n != 1 and line != J_POINTER:
            e = esc_issues(line)
            if e:
                v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
            lm = listmark_issues(line)
            if lm:
                v.append((n, 'LISTMARK', f'{lm} line-leading + / * (the Obsidian nested-bullet trap)'))
    for n in range(1, len(lines) - 1):
        if lines[n] == '' and lines[n - 1] == '' and lines[n + 1] == '':
            v.append((n + 1, 'JBLANK', 'double blank line'))
    if not text.endswith('\n'):
        v.append((len(lines), 'EOF', 'the file must end with a newline'))
    return v


NUM_ITEM = re.compile(r'^(\d+)\. ')


def prose_state_check(line, state):
    """The shared prose indent discipline for the rule files, the journals and
    the overview: top-level '- ' bullets with continuations at 2, sub-bullets
    at 2 with continuations at 4, numbered 'N. ' items with continuations at
    2+len(digits) (3 for a single digit). state = {'sub': bool, 'num': int or
    None, 'fence': bool} — updated in place. Fenced code blocks are verbatim:
    no check at all inside them. -> violation message or None."""
    if line.startswith('```'):
        state['fence'] = not state['fence']
        return None
    if state['fence']:
        return None
    if line.startswith('  - '):
        state['sub'] = True
        state['num'] = None
        return None
    if line.startswith(' - '):
        # a historical 1-space sub-bullet: its continuations sit at 3
        state['sub'] = True
        state['num'] = 3
        return None
    if line.startswith('- '):
        state['sub'] = False
        state['num'] = None
        return None
    ind = len(line) - len(line.lstrip(' '))
    if ind == 0:
        state['sub'] = False
        m = NUM_ITEM.match(line)
        # the continuation aligns under the first text char: "1. " = 3, "10. " = 4
        state['num'] = (len(m.group(1)) + 2) if m else None
        return None
    if ind == 2:
        state['sub'] = False
        m = re.match(r'^  (\d+)\. ', line)  # a nested numbered item: "  1. " -> 5
        state['num'] = (4 + len(m.group(1))) if m else None
        return None
    if ind == 4:
        if state['num'] == 4:
            return None  # a "10. " numbered continuation
        return None if state['sub'] else 'a 4-space line outside a sub-bullet'
    if state['num'] is not None and ind == state['num']:
        return None
    if ind > 0:
        return f'unsupported indent ({ind} spaces)'
    return None


SECTIONS = ('Project', 'Environment', 'Current state', 'Next steps',
            'Source files', 'Test files', 'Index')


def lint_overview(path, lines, text):
    """notes/overview.md (notes/overview_rules.md): the H1, the Format rules
    pointer section, then EXACTLY the seven sections in exactly this order
    (Project ... Index); the two tables (Source files / Test files) with one
    physical line per row, alphabetical by full path; Current state MAX 10
    bullets; Next steps OPEN items only (no “Done” bullets)."""
    v = []
    if lines[0] != '# overview.md — entry point':
        v.append((1, 'OV-H1', 'the first line must be the overview H1'))
    secs = [(n, line[3:].strip()) for n, line in enumerate(lines, 1) if line.startswith('## ')]
    if not secs or secs[0][1] != 'Format rules':
        v.append((1, 'OV-SECS', 'the first section must be “Format rules”'))
    body = secs[1:]
    for i, (n, title) in enumerate(body):
        if i < len(SECTIONS) and not title.startswith(SECTIONS[i]):
            v.append((n, 'OV-SECS', f'section out of order: “{title}” (expected “{SECTIONS[i]} ...”)'))
    if len(body) > len(SECTIONS):
        v.append((body[len(SECTIONS)][0], 'OV-SECS', 'a section beyond the seven'))
    elif len(body) < len(SECTIONS):
        v.append((0, 'OV-SECS', f'{len(SECTIONS) - len(body)} missing section(s)'))
    spans = {}
    for n, title in body:
        for canon in SECTIONS:
            if title.startswith(canon):
                spans[canon] = n
                break
    ends = {}
    for i, (n, title) in enumerate(body):
        for canon in SECTIONS:
            if title.startswith(canon):
                ends[canon] = body[i + 1][0] - 1 if i + 1 < len(body) else len(lines)
                break
    for canon in ('Source files', 'Test files'):
        if canon not in spans:
            continue
        rows = [(k + 1, l) for k, l in enumerate(lines[spans[canon] - 1:ends[canon]])
                if l.startswith('|')]
        for k, l in rows:
            if not l.rstrip().endswith('|'):
                v.append((k, 'OV-TABLE', 'a table row must start and end with a pipe'))
        prev = ''
        for k, l in rows[2:]:
            cell = l.strip().strip('|').split('|')[0].strip()
            if cell and cell <= prev:
                v.append((k, 'OV-TABLE', f'table row not alphabetical: “{cell}” after “{prev}”'))
            if cell:
                prev = cell
    if 'Current state' in spans:
        cnt = sum(1 for l in lines[spans['Current state'] - 1:ends['Current state']]
                  if l.startswith('- '))
        if cnt > 10:
            v.append((spans['Current state'], 'OV-CUR', f'Current state has {cnt} bullets (MAX 10)'))
    if 'Next steps' in spans:
        for l in lines[spans['Next steps'] - 1:ends['Next steps']]:
            if l.startswith(('- Done', '- done')):
                v.append((0, 'OV-NEXT', 'a “Done” bullet in Next steps (OPEN items only)'))
    state = {'sub': False, 'num': None, 'fence': False}
    for n, line in enumerate(lines, 1):
        if line.startswith('```'):
            state['fence'] = not state['fence']
            continue
        if state['fence']:
            continue
        if line == '':
            continue
        if line.startswith('# '):
            state['sub'] = False
            state['num'] = None
        elif line.startswith('|'):
            ok = any(canon in spans and spans[canon] <= n <= ends[canon]
                     for canon in ('Source files', 'Test files'))
            if not ok:
                v.append((n, 'OV-TABLE', 'a table row outside the two tables'))
        else:
            msg = prose_state_check(line, state)
            if msg:
                v.append((n, 'OV-INDENT', msg))
        if n != 1:  # the H1 is the file identity: its underscores are not prose
            e = esc_issues(line)
            if e:
                v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
            lm = listmark_issues(line)
            if lm:
                v.append((n, 'LISTMARK', f'{lm} line-leading + / * (the Obsidian nested-bullet trap)'))
    common_tail(path, lines, text, v)
    if not canon_ok(path):
        v.append((0, 'CANON', 'not idempotent under notes_format --write'))
    return v


def lint_rulefile(path, lines, text):
    """The domain rule files (overview_rules.md, decisions_rules.md, log_rules.md,
    docs_rules.md, probe_rules.md, wsutils.md, naming.md): an H1, the intro prose,
    the '## Section' headers, the top-level '- ' bullets with their continuations
    at exactly 2 spaces (sub-bullets at 2, continuations at 4)."""
    v = []
    if not lines[0].startswith('# '):
        v.append((1, 'RF-H1', 'the first line must be an H1'))
    state = {'sub': False, 'num': None, 'fence': False}
    for n, line in enumerate(lines, 1):
        if line.startswith('```'):
            state['fence'] = not state['fence']
            continue
        if state['fence']:
            continue
        if line == '':
            continue
        if line.startswith('## '):
            state['sub'] = False
            state['num'] = None
        elif line.startswith('# '):
            if n != 1:
                v.append((n, 'RF-H1', 'stray heading'))
            state['sub'] = False
            state['num'] = None
        else:
            msg = prose_state_check(line, state)
            if msg:
                v.append((n, 'RF-INDENT', msg))
        if n != 1:  # the H1 carries the file name (docs_rules.md ...): not prose
            e = esc_issues(line)
            if e:
                v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
            lm = listmark_issues(line)
            if lm:
                v.append((n, 'LISTMARK', f'{lm} line-leading + / * (the Obsidian nested-bullet trap)'))
    common_tail(path, lines, text, v)
    if not canon_ok(path):
        v.append((0, 'CANON', 'not idempotent under notes_format --write'))
    return v


IA_STATUS = re.compile(r'(idea|follow-up|in-progress|done|dropped)')
IA_ENTRY = re.compile(r'^I-(\d{3}) \| ([^|]*) \| ')


def lint_ideas(path, lines, text):
    """notes/ideas.md + notes/ideas_closed.md (the D-235 preamble format): an
    H1, the preamble prose, then the entries `I-NNN | status | idea` with a
    9-space continuation indent and a blank line before every entry; the
    I-numbers are global, never reused."""
    v = []
    if not lines[0].startswith('# '):
        v.append((1, 'IA-H1', 'the first line must be an H1'))
    prev_i = None
    blanks = 0
    fence = False
    for n, line in enumerate(lines, 1):
        if line.startswith('```'):
            fence = not fence
            continue
        if fence:
            continue
        if line == '':
            blanks += 1
            if blanks > 1:
                v.append((n, 'IA-BLANK', 'double blank line'))
            continue
        blanks = 0
        m = IA_ENTRY.match(line)
        if m:
            if lines[n - 2].strip() != '':
                v.append((n, 'IA-BLANK', 'no blank line before the entry'))
            if not IA_STATUS.fullmatch(m.group(2)):
                v.append((n, 'IA-HEADER', f'unknown status “{m.group(2).strip()}” in an entry header'))
            num = int(m.group(1))
            if prev_i is not None and num <= prev_i:
                v.append((n, 'IA-SEQ', f'I-number not increasing (previous {prev_i})'))
            prev_i = num
        else:
            if line.startswith('# '):
                if n != 1:
                    v.append((n, 'IA-H1', 'stray heading'))
            else:
                ind = len(line) - len(line.lstrip(' '))
                if ind not in (0, 9):
                    v.append((n, 'IA-INDENT', f'indent is {ind} spaces (preamble 0, continuation 9)'))
        if n != 1:  # the H1 carries the file name: not prose
            e = esc_issues(line)
            if e:
                v.append((n, 'ESC', f'{e} bare _ / unpaired * outside code spans'))
            lm = listmark_issues(line)
            if lm:
                v.append((n, 'LISTMARK', f'{lm} line-leading + / * (the Obsidian nested-bullet trap)'))
    common_tail(path, lines, text, v)
    if not canon_ok(path):
        v.append((0, 'CANON', 'not idempotent under notes_format --write'))
    return v


def kind_of(name):
    b = Path(name).name
    if b == 'rules.md':
        return 'rules'
    if re.fullmatch(r'decisions(_\d{3})?\.md', b):
        return 'decisions'
    if b == 'log.md' or re.fullmatch(r'log_\d{3}\.md', b):
        return 'journal'
    if b == 'overview.md':
        return 'overview'
    if b == 'design_principles.md':
        return 'design'
    if b in ('overview_rules.md', 'decisions_rules.md', 'log_rules.md', 'docs_rules.md',
             'probe_rules.md', 'wsutils.md', 'naming.md'):
        return 'rulefile'
    if b in ('ideas.md', 'ideas_closed.md'):
        return 'ideas'
    return None


def main(argv):
    if len(argv) > 1:
        files = [Path(a) for a in argv[1:]]
    else:
        # every CURRENT notes file (the closed volumes are linted on explicit request)
        files = [ROOT / f'notes/{n}' for n in
                 ('rules.md', 'decisions.md', 'log.md', 'overview.md', 'ideas.md', 'ideas_closed.md',
                  'naming.md', 'design_principles.md', 'wsutils.md', 'overview_rules.md', 'decisions_rules.md',
                  'log_rules.md', 'docs_rules.md', 'probe_rules.md')]
    linters = {'decisions': lint_decisions, 'rules': lint_rules, 'design': lint_design,
               'journal': lint_journal, 'overview': lint_overview, 'rulefile': lint_rulefile, 'ideas': lint_ideas}
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
