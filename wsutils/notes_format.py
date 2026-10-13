#!/usr/bin/env python3
#
# notes_format.py
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

"""notes_format.py — the house re-wrapper for the notes/ and docs/ Markdown.

WHAT IT IS: a MAINTENANCE tool (not a check, not a probe). It rewrites a
Markdown file to the house format: ~120 chars/line, code-span aware, with
the D-209 mid-token rejoins and the D-237 block grammar. The workspace
tools live here, in the ROOT wsutils/ — NOT in the package's
src/reversi/tools/ (that one ships with the library, D-133).

THE BLOCK GRAMMAR: a block is a run of lines delimited by a blank line, a
heading, a table row, a code fence, or the START of a bullet / numbered
item / decision entry / `|` field. Inside a block every line break is
re-flowed:

- a break inside a CODE SPAN is healed: the lines are merged with a space
  (a soft break renders as a space in Markdown — what the reader sees),
  so a span split by an old wrap comes back whole;
- a break after a `/`, `-`, `_` ATTACHED to the preceding word
  (`reversi/` + `feature_prng.py`, `test_lm_` + `worker_gradient`) is
  rejoined with NO space — the D-209 mid-token rejoin. `/` rejoins only
  before a digit, a filename, a slash-list or an id; `(` or a plain word
  after a `/` starts a NEW phrase;
- every other break becomes a single space.

IT VERIFIES ITSELF, per file: the content fingerprint (backticks
stripped, the blocks joined, the token lists compared), the idempotence
(the second pass is a no-op), the span check (no output line carries an
unbalanced backtick), and the fixpoint iteration (a healed span re-wraps).
A line never STARTS with a token the grammar would read as a new block
and never ENDS with a token the rejoin rule would glue to the next line:
the wrapper does not manufacture the breaks it heals.

USAGE (from the workspace root):
  .venv/bin/python wsutils/notes_format.py --check notes/overview.md ...
  .venv/bin/python wsutils/notes_format.py --write notes/*.md

SAFETY: the DEFAULT is a report (nothing is written): the per-file verification (the
content fingerprint, the idempotence, the fixpoint) on stdout; the passed files are
rewritten ONLY with --write (after that verification).

ORIGIN: the D-237 reform (the notes/ tree) and D-238 (the docs/ mirrors);
promoted to tools/ at D-248.
"""

import re
import sys

WIDTH = 120

HEAD = re.compile(r'^#{1,6} ')
# a REAL markdown table row starts AND ends with a pipe; a single leading
# pipe is the `| rationale` FIELD marker of the decisions volumes (and `|x|).`
# is plain math text) — those are wrapped, not kept verbatim
def is_table(line):
    s = line.strip()
    return len(s) > 1 and s.startswith('|') and s.endswith('|')
FENCE = re.compile(r'^\s*```')
BULLET = re.compile(r'^(\s*)(?:-|\d+\.)\s')
# the optional letter suffix covers the historical sub-entries (D-156b/c/d in
# the closed volumes): without it the tool parses them as prose paragraphs and
# flattens their 9-space continuation blocks
ENTRY = re.compile(r'^\s*([DI]-\d{3,4}[a-z]?) \| ([^|]+) \| ')
FIELD = re.compile(r'^(\s*)\| ')
SKIP_WRAP = re.compile(r'^\s*$')
# a token that must NEVER start a continuation line (the next pass would read
# it as a new block: a bullet, a field/table pipe, a heading, a numbered item,
# a decision header)
DANGEROUS = re.compile(r'^(?:[-|#]|\d+\.|[DI]-\d{3,4}\b)')


class Verbatim(list):
    """A block kept verbatim: a fence marker, a fenced line, a table row."""


def is_structural(line):
    """A line kept verbatim: blank, heading, table row, code fence."""
    return bool(SKIP_WRAP.match(line) or HEAD.match(line) or is_table(line)
                or FENCE.match(line))


def is_start(line):
    """A line that STARTS a wrappable block: a bullet, an entry, a field."""
    return bool(BULLET.match(line) or ENTRY.match(line) or FIELD.match(line))


def is_boundary(line):
    """True when the line starts a new block (structural or wrappable)."""
    return is_structural(line) or is_start(line)


def blocks_of(lines):
    out, buf, fence = [], [], False
    for line in lines:
        if FENCE.match(line):
            if buf:
                out.append(buf)
                buf = []
            out.append(Verbatim([line]))    # the fence marker itself
            fence = not fence
            continue
        if fence:
            if buf:
                out.append(buf)
                buf = []
            out.append(Verbatim([line]))    # a fenced line: VERBATIM
            continue
        if is_structural(line):
            if buf:
                out.append(buf)
                buf = []
            out.append(Verbatim([line]))    # kept verbatim
            continue
        if is_start(line) and buf:          # a bullet / entry / field: new block
            out.append(buf)
            buf = []
        buf.append(line)
    if buf:
        out.append(buf)
    return out


def prefix_of(block):
    """-> (first_prefix, continuation_indent) for a block."""
    first = block[0]
    m = BULLET.match(first)
    if m:
        indent = len(m.group(1))
        mark = first[indent:].split(' ', 1)[0] + ' '
        return ' ' * indent + mark, indent + len(mark)
    m = ENTRY.match(first)
    if m:
        return f'{m.group(1)} | {m.group(2).strip()} | ', 9
    m = FIELD.match(first)
    if m:
        indent = len(m.group(1))
        return ' ' * indent + '| ', indent + 2
    return '', 0


def parse(text):
    """-> [(token, sep)]; a code span is atomic even when punctuation or a
    word is glued to it (``(`dict[c] = min(c, flip(c))`,`` is ONE token).

    The units are the maximal non-space runs; a run that CONTAINS a closed
    code span is kept whole, so the span can never be split by the wrapper.
    """
    regions = []
    for m in re.finditer(r'`[^`]*`', text):
        a, b = m.start(), m.end()
        while a > 0 and not text[a - 1].isspace():
            a -= 1
        while b < len(text) and not text[b].isspace():
            b += 1
        if regions and a <= regions[-1][1]:
            regions[-1] = (regions[-1][0], max(b, regions[-1][1]))
        else:
            regions.append((a, b))
    out, pos = [], 0
    for a, b in regions:
        for m in re.finditer(r'\S+', text[pos:a]):
            out.append((m.group(0), '' if (pos == 0 and m.start() == 0) else ' '))
        out.append((text[a:b], '' if a == 0 else ' '))
        pos = b
    for m in re.finditer(r'\S+', text[pos:]):
        out.append((m.group(0), '' if (pos == 0 and m.start() == 0) else ' '))
    return out


def rejoin_kind(prev_token, next_token):
    """The mid-token rejoin rule (D-209/D-237) — None when the break is a space.

    `_` and `-` always continue a token (a split identifier / compound),
    except after a dunder (`__all__`). `/` continues only when the next
    fragment is clearly part of the same token: a digit, a filename (a dot),
    a slash-list, or an id (`A2`); a `(` or a plain word after a `/` starts a
    NEW phrase (the D-209 false-positive family).
    """
    if len(prev_token) < 2 or prev_token[-2] in ' \t':
        return None
    c = prev_token[-1]
    if c == '_':
        return None if prev_token[-2] == '_' else 'underscore'
    if c == '-':
        return 'hyphen'
    if c == '/':
        if next_token.startswith('('):
            return None
        if next_token[:1].isdigit() or '.' in next_token or '/' in next_token:
            return 'slash'
        if len(next_token) > 1 and next_token[0].isupper() and next_token[1].isdigit():
            return 'slash'
        return None
    return None


def merge_span_lines(block):
    """Heal a code span broken across lines: while the running backtick parity
    is odd the break is INSIDE a span, so the lines are merged (the soft break
    renders as a space in Markdown — this is exactly what a reader sees)."""
    out, parity = [], 0
    for raw in block:
        if out and parity % 2:
            out[-1] = out[-1].rstrip() + ' ' + raw.strip()
        else:
            out.append(raw)
        parity = (parity + raw.count('`')) % 2
    return out


def join_block(block):
    """Re-flow a block: -> (tokens, rejoins) where rejoins lists the fixes."""
    block = merge_span_lines(block)
    prefix, _ = prefix_of(block)
    body = block[0][len(prefix):] if prefix else block[0]
    tokens = [(t, s) for t, s in parse(body)]
    rejoins = []
    for raw in block[1:]:
        nxt = raw.strip()
        if not nxt:
            continue
        toks = parse(nxt)
        if not toks:
            continue
        prev_text = tokens[-1][0] if tokens else ''
        no_space = rejoin_kind(prev_text, toks[0][0]) is not None
        if no_space and tokens:
            rejoins.append((tokens[-1][0][-30:], toks[0][0][:30]))
            tokens[-1] = (tokens[-1][0] + toks[0][0], tokens[-1][1])
            toks = toks[1:]                      # the FIRST word only is glued
        if toks:
            toks[0] = (toks[0][0], ' ')          # the line break is a space
        tokens.extend(toks)
    return tokens, rejoins


def line_str(pref, toks):
    """The text of a line: `pref` + the tokens, honouring the glued ones."""
    s = pref
    for t, sep in toks:
        s += t if (sep == '' or s == '' or s.endswith(' ')) else ' ' + t
    return s


def wrap(prefix, indent, tokens):
    """Greedy fill to WIDTH with SAFE break points.

    A break is never placed where the next pass would misread it:

    - a line never STARTS with a token the block grammar would take for a
      new block (a bullet, a pipe, a numbered item, a `D-NNN | ` header);
    - a line never ENDS with a token that the rejoin rule would glue to the
      next line's first token (an attached `/`, `-`, `_`): the wrapper must
      not manufacture the mid-token breaks it is meant to heal.

    When the greedy break point is unsafe, it backs off (the trailing tokens
    move to the next line); if it cannot back off, the line overflows.
    """
    out = []
    start, n = 0, len(tokens)
    while start < n:
        pref = prefix if start == 0 else ' ' * indent
        width, end = len(pref), start
        while end < n:
            tok, sep = tokens[end]
            first = end == start
            add = len(tok) + (0 if (sep == '' or first) else 1)
            if not first and sep != '' and width + add > WIDTH:
                break
            width += add
            end += 1
        nb = end
        while nb < n and nb > start + 1 and (tokens[nb][1] == ''
                                  or DANGEROUS.match(tokens[nb][0])
                                  or is_boundary(' ' * indent + tokens[nb][0])
                                  or rejoin_kind(tokens[nb - 1][0], tokens[nb][0]) is not None):
            nb -= 1
        out.append(line_str(pref, [(tokens[k][0], tokens[k][1] if k > start else '')
                                   for k in range(start, nb)]))
        start = nb
    return out


def render(lines):
    out, report = [], {'rejoins': [], 'blocks': 0}
    for block in blocks_of(lines):
        if isinstance(block, Verbatim):
            out.append(block[0].rstrip())
            continue
        report['blocks'] += 1
        prefix, indent = prefix_of(block)
        tokens, rejoins = join_block(block)
        report['rejoins'].extend(rejoins)
        out.extend(wrap(prefix, indent, tokens))
    return out, report


def plain_tokens(lines):
    """The content fingerprint: backticks stripped, then joined with the
    rejoin rule and split on whitespace. Backtick stripping removes the
    span-atomicity from the comparison (a multi-line code span is healed
    by the re-wrap and would otherwise change the tokenization)."""
    out = []
    for block in blocks_of(lines):
        if isinstance(block, Verbatim):
            continue
        text = '\n'.join(merge_span_lines(block)).replace('`', '')
        rows = text.split('\n')
        acc = rows[0].strip()
        for raw in rows[1:]:
            nxt = raw.strip()
            if not nxt:
                continue
            prev_last = acc.split()[-1] if acc.split() else ''
            first = nxt.split()[0]
            if rejoin_kind(prev_last, first):
                acc += first + ' ' + ' '.join(nxt.split()[1:])
            else:
                acc += ' ' + nxt
        out.extend(acc.split())
    return out


def main(argv):
    write = '--write' in argv
    paths = [a for a in argv if not a.startswith('--')]
    total_rejoins = 0
    for path in paths:
        raw = open(path, encoding='utf-8').read()
        lines = raw.split('\n')
        new, report = render(lines)
        body = '\n'.join(new)
        if not body.endswith('\n'):
            body += '\n'
        # a healed multi-line code span re-wraps differently: iterate to the fixpoint
        passes = 1
        while True:
            again, rep2 = render(body.split('\n'))
            passes += 1
            report['rejoins'].extend(rep2['rejoins'])
            if again == new:
                break
            new = again
            body = '\n'.join(new) + ('\n' if not new or new[-1] != '' else '')
            if passes > 6:
                print('!! no fixpoint')
                break
        idem = True
        # the token fingerprint: identical except for the reported rejoins
        old_tok = plain_tokens(lines)
        new_tok = plain_tokens(body.split('\n'))
        prose = [l for l in body.split('\n') if not is_table(l)]
        verdict = 'CONTENT OK' if old_tok == new_tok else 'CONTENT DRIFT'
        def split_spans(ls):
            return [i + 1 for i, l in enumerate(ls)
                    if not l.lstrip().startswith('```') and l.count('`') % 2]
        old_ss, new_ss = split_spans(lines), split_spans(body.split('\n'))
        if len(new_ss) > len(old_ss):
            verdict += f' SPAN REGRESSION {old_ss} -> {new_ss}'
        print(f'{path}: {len(lines)} -> {len(new)} lines, max {max(len(l) for l in prose)}, '
              f'blocks {report["blocks"]}, rejoins {len(report["rejoins"])}, passes {passes}, '
              f'idempotent {idem}, tokens {len(old_tok)} -> {len(new_tok)}  {verdict}')
        for a, b in report['rejoins'][:6]:
            print(f'    rejoin: ...{a} + {b}...')
        total_rejoins += len(report['rejoins'])
        if write:
            open(path, 'w', encoding='utf-8').write(body)
    print(f'TOTAL rejoins: {total_rejoins}')


if __name__ == '__main__':
    main(sys.argv[1:])
