#!/usr/bin/env python3
"""
src_reflow.py — the R-520 source-prose re-wrapper for the .py sources.

WHAT IT IS: a MAINTENANCE tool, the source sibling of wsutils/notes_format.py (that one re-wraps the
notes/ + docs/ Markdown; this one re-wraps the SOURCE PROSE of the .py files): it re-wraps the
docstring lines and the multi-line `#` comment blocks to the R-520 widths — a PREFERRED 100
characters per line, and a line may exceed 100, up to the 120-character ceiling, only to avoid
leaving a single word alone on the next line (the pull-up; if the pull-up would pass 120, the break
stands). The docstring layout is the house canonical: a single-paragraph docstring that fits the
preferred width is one line (\"\"\"text\"\"\"); every other docstring stands alone on its opening
and closing quotes, the text starts immediately at the quote's indent, the section headings
(Args:/Returns:/Raises:/Attributes:/…) sit at that same indent behind a blank line, the entries at
+4, and a wrapped entry description at +8 — the entries are untyped (the Pydantic annotation in the
signature is the type). The tool re-lays out any old variant to that canonical (the inline first
line, the section indents, the legacy column-0 bodies) and collapses the multi-line docstrings that
fit the one-line form. Structure is preserved otherwise: the indented "fixed" lines (the API tables,
the code samples), the base-indented paragraphs that carry a double space (ASCII art, the aligned
board diagrams), the license banner (the `#` run containing 'Copyright'), the divider lines, and the
single-line docstrings that already fit. CODE IS TOUCHED NOT AT ALL: the expression merges of
R-520's code clause are a manual format-pass sub-work, with the per-file tests.

USAGE (from the workspace root):
  .venv/bin/python wsutils/src_reflow.py FILE [FILE …]         # the default: a check (a report)
  .venv/bin/python wsutils/src_reflow.py --write FILE [FILE …] # the reflow, with the pre-write verification
Exit codes: 0 = every file is the reflow's fixed point (check) / was written (write); 1 = a file
would be reflowed (check) / was refused or failed a verification (write); 2 = usage error.

SAFETY: the DEFAULT is a report (nothing is written). With --write every file is verified BEFORE the
write: the logical (whitespace-insensitive) identity of every docstring and every comment block, the
parse of the result, and the idempotence (the second pass is a no-op); a file that fails any
verification is REFUSED, the original untouched. It touches only the files it is given, never runs a
git command, and never deletes. A file carrying hand-polished breaks (the documented D-426/D-427
nudges in prng.py) is NOT wrong — but it is not the greedy fill's fixed point either: the check
reports it as "would reflow". Re-reading such a file by hand is the format pass's job; do not
blindly --write it.

ORIGIN: D-428 (2026-10-04) — the R-520 refinement (D-427) promoted the session-96 one-shot
(scratch/reflow_prng.py, the prng.py reflow of D-426/D-427) to a workspace tool: the check mode, the
docstring-aware comment pass, and the pre-write verification are the additions.
"""

import argparse
import ast
import re
import sys
import textwrap

PREF = 100  # R-520: the preferred prose width
CEIL = 120  # R-520: the ceiling of every physical line

HEADING = re.compile(
    r'^(Args|Returns|Raises|Yields|Examples|References|Attributes)( \(internal\))?:$')
# entry start: identifier (optionally a [bracketed] generic), optional (type), the colon right after
# the word or the closing paren/bracket.
ENTRY = re.compile(r'^[A-Za-z_][A-Za-z0-9_\.]*(\[[^\]]*\])?\s*(\((?:[^()]*|\([^()]*\)[^()]*)\))?:\s+\S')
COMMIT_COMMENT = re.compile(r'^(\s*)#(.*?)\s*$')
DIVIDER = re.compile(r'^-+$')


class ReflowError(Exception):
    """A file (or one of its docstrings/blocks) is not safe to reflow."""


def greedy(text, width):
    return textwrap.wrap(text, width, break_long_words=False,
                         break_on_hyphens=False) or ['']


def wrap_prose(text, width, ceil):
    """
    Greedy fill at `width`; the single-word pull-up: if the final line is one word and merging stays
    within `ceil`, merge it.
    """
    lines = greedy(text, width)
    if len(lines) >= 2 and ' ' not in lines[-1]:
        merged = lines[-2] + ' ' + lines[-1]
        if len(merged) <= ceil:
            lines = lines[:-2] + [merged]
    return lines


def indent_of(line):
    return len(line) - len(line.lstrip())


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


# ---------------------------------------------------------------------
# The docstring pass
# ---------------------------------------------------------------------


def docstring_nodes(tree):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef)):
            if (n.body and isinstance(n.body[0], ast.Expr)
                    and isinstance(n.body[0].value, ast.Constant)
                    and isinstance(n.body[0].value.value, str)):
                out.append(n.body[0].value)
    return sorted(out, key=lambda c: c.lineno)


def build_groups(content, base):
    """
    Split the docstring content lines into groups: ('blank', None), ('prose', [stripped lines]),
    ('heading', line), ('entry', [raw lines]), ('fixed', raw line) — the indented non-entry lines
    (the API tables, the code samples) are preserved verbatim.
    """
    groups = []
    i = 0
    n = len(content)
    while i < n:
        l = content[i]
        if l.strip() == '':
            groups.append(('blank', None))
            i += 1
            continue
        rel = indent_of(l) - base
        s = l.strip()
        if rel < 0:
            raise ReflowError(f'negative relative indent: {l!r}')
        if rel == 0:
            if HEADING.match(s):
                groups.append(('heading', s))
                i += 1
            else:
                run = [s]
                i += 1
                while i < n:
                    m = content[i]
                    if m.strip() == '' or HEADING.match(m.strip()):
                        break
                    if indent_of(m) - base != 0:
                        break
                    run.append(m.strip())
                    i += 1
                # a paragraph carrying a double space is not prose — ASCII art, the aligned board
                # diagrams — preserve it
                if any('  ' in l for l in run):
                    groups.append(('fixed', run))
                else:
                    groups.append(('prose', run))
        else:
            if ENTRY.match(s):
                run = [l]
                i += 1
                while i < n:
                    m = content[i]
                    if m.strip() == '':
                        break
                    mrel = indent_of(m) - base
                    # a continuation: deeper, or same-level non-entry
                    if mrel > rel or (mrel == rel and not ENTRY.match(m.strip())):
                        run.append(m)
                        i += 1
                    else:
                        break
                groups.append(('entry', run))
            elif groups and groups[-1][0] == 'entry' and \
                    indent_of(groups[-1][1][-1]) == indent_of(l):
                groups[-1][1].append(l)
                i += 1
            else:
                groups.append(('fixed', l))
                i += 1
    return groups


def emit(groups, base, first_inline=False):
    out = []
    first_prose_done = False
    for kind, payload in groups:
        if kind == 'blank':
            out.append('')
        elif kind == 'heading':
            out.append(' ' * base + payload)
        elif kind == 'fixed':
            if isinstance(payload, list):
                out.extend(' ' * base + l for l in payload)
            else:
                out.append(payload)
        elif kind == 'prose':
            # an inline-opening docstring loses 3 chars on its first line to the quote itself
            pen = 3 if (first_inline and not first_prose_done) else 0
            for line in wrap_prose(' '.join(payload), PREF - base - pen,
                                   CEIL - base - pen):
                out.append(' ' * base + line)
            first_prose_done = True
        else:  # entry
            lines = payload
            txt = ' '.join(l.strip() for l in lines)
            entry_indent = indent_of(lines[0])
            if entry_indent + len(txt) <= PREF:
                out.append(' ' * entry_indent + txt)
                continue
            m = re.match(r'^(\S+\[[^\]]*\]|\S+)(\s*\([^)]*\))?:\s*(.*)$', txt)
            if not m:
                raise ReflowError(f'unreadable entry head: {txt!r}')
            head = m.group(1) + (m.group(2) or '') + ':'
            desc = m.group(3)
            cont_indent = entry_indent + 4
            chunks = greedy(desc, PREF - entry_indent - len(head) - 1)
            rest = desc[len(chunks[0]):].lstrip()
            first = ' ' * entry_indent + head + ' ' + chunks[0]
            cont_lines = []
            if rest:
                cont_lines = [' ' * cont_indent + c for c in
                              wrap_prose(rest, PREF - cont_indent,
                                         CEIL - cont_indent)]
            # the single-word pull-up across the entry boundary: a lone final continuation word
            # merges into its predecessor when the merged line stays within the ceiling
            if cont_lines and ' ' not in cont_lines[-1].strip():
                word = cont_lines[-1].strip()
                if len(cont_lines) >= 2 and \
                        len(cont_lines[-2]) + 1 + len(word) <= CEIL:
                    cont_lines = cont_lines[:-2] + [
                        cont_lines[-2] + ' ' + word]
                elif len(first) + 1 + len(word) <= CEIL:
                    first = first + ' ' + word
                    cont_lines = cont_lines[:-1]
            out.append(first)
            out.extend(cont_lines)
    while out and out[-1] == '':
        out.pop()
    return out


def reformat_docstring(raw):
    """
    Reformat one docstring literal (the full line span, quotes included) to the house canonical. A
    single-paragraph body that fits the preferred width becomes the one-line form: \"\"\"text\"\"\".
    Otherwise the quotes stand alone on the first and last line, the text starts immediately at the
    quote's indent, the section headings sit at that same indent behind a blank line, the entries at
    +4, and a wrapped entry description at +8.
    """
    i = raw.find('"""')
    j = raw.rfind('"""')
    if i == -1 or j <= i:
        raise ReflowError('no double-triple-quote span in the literal')
    quote_indent = indent_of(raw.split('\n', 1)[0])
    body = raw[i + 3:j]
    frags = body.split('\n')
    first_inline = bool(frags[0].strip())
    # a leading blank (the old stand-alone form) drops with the quote line.
    real_body = frags[1:]
    if real_body and real_body[-1].strip() == '':
        real_body = real_body[:-1]
    if first_inline:
        # the old canonical: the first line shares the quote's line; lift it to a body line. The
        # base is measured on the REAL body lines only: in that old canonical the body paragraphs
        # sit one level BELOW the quote (the lifted first line would mask them).
        content = [' ' * quote_indent + frags[0].strip()] + real_body
    else:
        content = real_body
    if not any(l.strip() for l in content):
        raise ReflowError('empty docstring body')
    real_nob = [l for l in real_body if l.strip()]
    base0 = min(indent_of(l) for l in real_nob) if real_nob else quote_indent
    # Rebase to the house relative structure by ROLE, not by arithmetic: every old variant (the
    # inline first line with the body at the quote / +4 / +8 / +12, the legacy body at column 0 with
    # the headings at the base and the entries at +4, the new stand-alone form) classifies cleanly.
    # Paragraphs and headings land at the quote, entries at +4, wrapped entry descriptions at +8; a
    # deeper hand-placed line (a code sample, a table) stays.
    rebased = []
    entry_indent = None
    under_heading = False
    for l in content:
        s = l.strip()
        if not s:
            rebased.append('')
            entry_indent = None
            continue
        ind = indent_of(l)
        if entry_indent is not None and (ind > entry_indent or (ind == entry_indent
                and not ENTRY.match(s))):
            rebased.append(' ' * (quote_indent + 8) + s)
            continue
        entry_indent = None
        if HEADING.match(s):
            under_heading = True
            rebased.append(' ' * quote_indent + s)
        elif under_heading and ind <= base0 and ENTRY.match(s):
            # a legacy same-column entry (the heading and the entries share the base column).
            entry_indent = ind
            rebased.append(' ' * (quote_indent + 4) + s)
        elif ind > base0 and ENTRY.match(s):
            entry_indent = ind
            rebased.append(' ' * (quote_indent + 4) + s)
        elif ind > base0 and under_heading:
            # a section description (a plain sentence under Returns:/Raises:/…) sits at +4.
            rebased.append(' ' * (quote_indent + 4) + s)
        elif ind > base0:
            rebased.append(l)
        else:
            under_heading = False
            rebased.append(' ' * quote_indent + s)
    groups = build_groups(rebased, quote_indent)
    # The collapse: one prose group that fits the preferred width is the one-line form.
    if len(groups) == 1 and groups[0][0] == 'prose':
        line = ' ' * quote_indent + '"""' + ' '.join(groups[0][1]) + '"""'
        if len(line) <= PREF:
            return line
    body_lines = emit(groups, quote_indent)
    lines = [' ' * quote_indent + '"""'] + body_lines + [' ' * quote_indent + '"""']
    return '\n'.join(lines)


# ---------------------------------------------------------------------
# The comment pass (docstring-aware: the # lines INSIDE a docstring — e.g. an Examples: block — are
# never touched)
# ---------------------------------------------------------------------


def reflow_comments(lines, doc_lines):
    # The spans address the ORIGINAL line numbers; the live list shifts as the runs are re-wrapped,
    # so the numbers travel with the lines.
    out = list(lines)
    orignum = list(range(1, len(lines) + 1))
    i = 0
    while i < len(out):
        if orignum[i] in doc_lines or not COMMIT_COMMENT.match(out[i]):
            i += 1
            continue
        j = i
        while j < len(out) and orignum[j] not in doc_lines and \
                COMMIT_COMMENT.match(out[j]):
            j += 1
        run = out[i:j]
        contents = [COMMIT_COMMENT.match(l).group(2) for l in run]
        if any('Copyright' in c for c in contents):
            i = j
            continue
        new_run = []
        seg_orig = []
        seg_text = []
        seg_doc = []

        def flush():
            if len(seg_orig) >= 2:
                first_indent = len(seg_orig[0]) - len(seg_orig[0].lstrip())
                # a doc-comment (#:-prefixed) paragraph keeps its prefix: re-emitted with #: and the
                # per-line leading colon stripped from the text (the marker is not content).
                doc = all(seg_doc)
                prefix = ' ' * first_indent + ('#: ' if doc else '# ')
                text = ' '.join((c.strip().lstrip(':').strip() if doc else c.strip())
                                for c in seg_text)
                w_off = 3 if doc else 2
                wrapped = wrap_prose(text, PREF - first_indent - w_off,
                                     CEIL - first_indent - w_off)
                new_run.extend(prefix + w for w in wrapped)
            else:
                new_run.extend(seg_orig)
            seg_orig.clear()
            seg_text.clear()
            seg_doc.clear()

        for orig, c in zip(run, contents):
            # group(2) keeps the space after the #; strip before the divider test. A bare # line
            # (the empty separator inside a block) and a bare #: line (the empty doc-comment
            # separator) keep their paragraph apart: preserved verbatim.
            s = c.strip()
            is_doc = orig.lstrip().startswith('#:')
            if s == '' or (is_doc and s == ':') or DIVIDER.match(s):
                flush()
                new_run.append(orig)
            else:
                seg_orig.append(orig)
                seg_text.append(c)
                seg_doc.append(is_doc)
        flush()
        out[i:j] = new_run
        orignum[i:j] = [orignum[i]] * len(new_run)
        i = j + (len(new_run) - len(run))
    return out


# ---------------------------------------------------------------------
# The per-file transform + verification
# ---------------------------------------------------------------------


def transform(source):
    """
    Reflow the source text. Returns (new_text, stats). Raises ReflowError when the content could not
    be verified safe.
    """
    lines = source.split('\n')
    tree = ast.parse(source)
    docs = docstring_nodes(tree)
    changed = 0
    for c in reversed(docs):
        raw = '\n'.join(lines[c.lineno - 1:c.end_lineno])
        old = norm(raw[raw.find('"""') + 3:raw.rfind('"""')])
        if c.lineno == c.end_lineno and len(lines[c.lineno - 1]) <= PREF:
            continue  # a single-line docstring that fits the preferred width: a fixed point
        if c.lineno == c.end_lineno:
            # a single-line docstring over the ceiling: expand it to the standard multi-line form
            m = re.match(r'^(\s*)"""(.*?)"""\s*$', lines[c.lineno - 1])
            ind = m.group(1)
            text = m.group(2)
            wrapped = wrap_prose(text, PREF - len(ind), CEIL - len(ind))
            new_raw = '\n'.join([ind + '"""']
                                + [ind + w for w in wrapped]
                                + [ind + '"""'])
        else:
            new_raw = reformat_docstring(raw)
        ni = new_raw.find('"""')
        nj = new_raw.rfind('"""')
        if norm(new_raw[ni + 3:nj]) != old:
            raise ReflowError(f'docstring content changed at line {c.lineno}')
        if new_raw != raw:
            changed += 1
        lines[c.lineno - 1:c.end_lineno] = new_raw.split('\n')
    new_src = '\n'.join(lines)
    # the comment pass on the NEW line list (the docstring spans moved); the spans used HERE must
    # address this pre-pass line list
    doc_lines = set()
    for c in docstring_nodes(ast.parse(new_src)):
        doc_lines.update(range(c.lineno, c.end_lineno + 1))
    new_src = '\n'.join(reflow_comments(new_src.split('\n'), doc_lines))
    # the FINAL spans, on the final file: the comment pass moved lines, so the pre-pass spans no
    # longer address it
    final_spans = set()
    for c in docstring_nodes(ast.parse(new_src)):
        final_spans.update(range(c.lineno, c.end_lineno + 1))
    doc_lines = final_spans
    # the comment-block identity: join every comment segment's words, excluding the # lines that
    # live INSIDE docstring spans
    def seg_words(src, spans):
        seg = []
        out = []
        for n, l in enumerate(src.split('\n'), 1):
            m = COMMIT_COMMENT.match(l)
            if m and m.group(2).strip() and n not in spans:
                c = m.group(2).strip()
                if l.lstrip().startswith('#:'):
                    c = c.lstrip(':').strip()  # the doc-comment marker is not content
                seg.append(norm(c))
            else:
                if seg:
                    out.append(' '.join(seg))
                    seg = []
        if seg:
            out.append(' '.join(seg))
        return out
    old_doc_lines = set()
    for c in docstring_nodes(tree):
        old_doc_lines.update(range(c.lineno, c.end_lineno + 1))
    if seg_words(new_src, doc_lines) != seg_words(source, old_doc_lines):
        raise ReflowError('comment block content changed')
    # the ceiling is a DELTA check: a file may carry pre-existing over-ceiling lines (the long
    # constants, the protected fixed lines) that the reflow must not ADD to, but it does not have to
    # fix them (the format pass's manual sub-work)
    over_old = sum(len(l) > CEIL for l in source.split('\n'))
    over_new = sum(len(l) > CEIL for l in new_src.split('\n'))
    if over_new > over_old:
        raise ReflowError('the result adds lines over the ceiling')
    stats = {'docstrings': len(docs), 'changed': changed}
    return new_src, stats


def idempotent(source):
    once = transform(source)[0]
    return transform(once)[0] == once


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog='src_reflow.py',
        description='the R-520 source-prose re-wrapper (the .py sources)')
    ap.add_argument('files', nargs='+', help='the .py files to check / reflow')
    ap.add_argument('--write', action='store_true',
                    help='write the reflow (the default is a check)')
    args = ap.parse_args(argv)

    rc = 0
    for path in args.files:
        try:
            src = open(path, encoding='utf-8').read()
            new_src, stats = transform(src)
            if args.write:
                if new_src == src:
                    print(f'{path}: already canonical (no-op)')
                    continue
                if not idempotent(src):
                    raise ReflowError('not idempotent (the second pass differs)')
                open(path, 'w', encoding='utf-8').write(new_src)
                print(f'{path}: reflowed — {stats["docstrings"]} docstrings, '
                      f'{stats["changed"]} re-wrapped, now '
                      f'{len(new_src.splitlines())} lines')
            else:
                if new_src == src:
                    print(f'{path}: canonical (the reflow fixed point)')
                else:
                    rc = 1
                    print(f'{path}: WOULD REFLOW — '
                          f'{stats["changed"]} docstring(s) re-wrapped '
                          f'({len(src.splitlines())} -> '
                          f'{len(new_src.splitlines())} lines)')
        except (ReflowError, SyntaxError, AssertionError, AttributeError) as e:
            rc = 1
            kind = 'REFUSED' if args.write else 'CHECK FAILED'
            print(f'{path}: {kind} — {e}')
    return rc


if __name__ == '__main__':
    sys.exit(main())
