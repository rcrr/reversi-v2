#!/usr/bin/env python3
#
# latex_lint.py
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

"""latex_lint.py — a robust linter (and safe auto-fixer) for the latex/ book zone.

WHAT IT IS: a maintenance / gate tool for the LaTeX chapters (latex/reversi_*.tex
and main.tex). Unlike the build (which stops at the first fatal error) it walks
every file and reports a whole class of the recurring, mostly SILENT pitfalls of
this book, each tied to a real defect hit while writing the pipeline chapters:

  1  accent     an ASCII-apostrophe accent (e' a' i' o' u' + uppercase) in PROSE
                must be the Unicode vowel (è à ì ò ù …). Context-aware: it ignores
                the primes in math and the quotes in code, and never touches the
                Italian elisions (l' d' un' … are consonant + quote).
  2  code-ascii a non-ASCII (multi-byte) character inside a lstlisting/verbatim
                block breaks pdftex ("Invalid UTF-8 byte …").
  3  texttt     an unescaped special (_ ^ $ # % & ~) inside \\texttt{…} (text mode)
                — a bare _ is a subscript, a bare ^ an accent, a bare $ opens math.
  4  bar-sub    a \\bar{X} immediately followed by a _ / ^ subscript: under the book's
                sans-serif math (sfmath) the bar is mis-positioned to the left.
                The fix is \\overline{X} (verified to centre correctly).
  5  xref       a \\ref/\\eqref/\\pageref/\\autoref whose label is never \\label'ed
                anywhere in the book (a dangling cross-reference).
  6  usepackage a \\usepackage inside a chapter file (the preamble lives only in
                main.tex; the chapters must not add packages).
  7  math-end   an unterminated display math: \\[ with no \\], \\( with no \\), or a
                top-level math environment with no \\end.
  8  lstlang    a \\begin{lstlisting}[language=X] with an X the listings package does
                not define here (the classic one is language=json).

THE CORE IS A CONTEXT SCANNER: it tiles the raw text into spans tagged prose / math /
code / comment, honouring \\$ escapes, \\[ \\] and \\( \\) and the math environments,
the verbatim (lstlisting) blocks (read raw, no comment inside), and % comments. That
context awareness is exactly what makes the accent check robust — a plain global
regex is what corrupts \\varphi' (a prime) and kind='stable' (a code quote).

MODES (from the workspace root):
  python3 wsutils/latex_lint.py latex/reversi_*.tex            # report only (the gate)
  python3 wsutils/latex_lint.py --write latex/reversi_*.tex    # report + apply the SAFE fixes
  python3 wsutils/latex_lint.py --fix=accent,texttt …          # restrict --write to some checks

The SAFE auto-fixes are: accent (1), code-ascii (2, de-accent to ASCII), texttt (3),
bar-sub (4, \\bar→\\overline). The structural checks (5,6,7,8) are report-only — a
dangling ref, a stray \\usepackage, an unclosed \\[ or an unknown language need a human
call, so --write never touches them. The fixpoint is applied per file; a file is
rewritten only if at least one safe edit landed.

EXIT STATUS: 0 when clean (or --write applied and re-scanned clean of the fixed
classes), 1 when violations remain. Suitable as a pre-commit gate for the latex zone.
"""

import re
import sys
import unicodedata

# ---------------------------------------------------------------- the contexts

VERBATIM_ENVS = {'lstlisting', 'verbatim', 'verbatim*'}
# top-level math environments (a \\begin of one opens a math span to its \\end).
# aligned / matrix / cases / pmatrix … are SUB-structures inside an already-open
# math span, so they are deliberately NOT listed here.
MATH_ENVS = {'equation', 'align', 'gather', 'eqnarray', 'flalign', 'math', 'displaymath'}

BEGIN = re.compile(r'\\begin\{([A-Za-z*]+)\}')
INLINECODE = re.compile(r'\\(texttt|mbox|url|path)\{')
ACCENT_MAP = {'e': 'è', 'a': 'à', 'i': 'ì', 'o': 'ò', 'u': 'ù',
              'E': 'È', 'A': 'À', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'}
# a vowel immediately followed by a single quote that is NOT a closing '' pair.
ACCENT_RE = re.compile(r"([aeiouAEIOU])'(?!')")
# only \\bar mis-positions with a following _ / ^ under sfmath (\\hat, \\vec, … are
# fine — verified on a test doc), so the check (and the safe fix) is \\bar-only.
BAR_RE = re.compile(r'\\bar\{[^}]*\}[_^]')
TEXTTT_RE = re.compile(r'\\texttt')
# specials that must be escaped inside a text-mode \texttt{…} argument.
TEXTTT_SPECIALS = {'_': r'\_', '^': r'\textasciicircum', '$': r'\$',
                   '#': r'\#', '%': r'\%', '&': r'\&', '~': r'\textasciitilde'}
# the listings languages this book's setup actually defines (language=json is not).
LISTINGS_LANGS = {'python', 'bash', 'sh', 'c', 'cpp', 'java', 'sql', 'ruby',
                  'perl', 'javascript', 'scheme', 'lisp', 'octave', 'none'}
REF_RE = re.compile(r'\\(ref|eqref|pageref|autoref|cref)\{([^}]+)\}')
LABEL_RE = re.compile(r'\\label\{([^}]+)\}')
LSTLANG_RE = re.compile(r'\\begin\{lstlisting\}\[([^\]]*)\]')


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def scan(text):
    """Tile the raw text into (start, end, ctx) spans; ctx in prose/math/code/comment.

    The spans are contiguous and cover [0, len(text)). A verbatim block is read raw
    (its % are literal, not comments); math spans cover $…$, \\[ … \\], \\( … \\) and
    the top-level math environments; a % in prose/math runs to the end of the line.
    """
    spans = []
    n = len(text)
    i = 0
    p0 = 0

    def emit(ctx, a, b):
        if b > a:
            spans.append((a, b, ctx))

    while i < n:
        c = text[i]
        m = BEGIN.match(text, i)
        if m:
            env = m.group(1)
            base = env.rstrip('*')
            if base in VERBATIM_ENVS:
                emit('prose', p0, i)
                close = re.search(r'\\end\{' + re.escape(env) + r'\}', text[i:])
                j = (i + close.end()) if close else n
                emit('code', i, j)
                i, p0 = j, j
                continue
            if base in MATH_ENVS:
                emit('prose', p0, i)
                close = re.search(r'\\end\{' + re.escape(env) + r'\}', text[i:])
                if close:
                    j = i + close.end()
                    emit('math', i, j)
                    i, p0 = j, j
                else:                              # unterminated math env (check 7)
                    emit('math', i, n)
                    i = n
                continue
        # a \\[len] line-break is NOT display math: the [ is preceded by a second \
        if c == '\\' and i + 1 < n and text[i + 1] in '[(' \
                and (i == 0 or text[i - 1] != '\\'):
            opener = text[i + 1]
            closer = '\\]' if opener == '[' else '\\)'
            emit('prose', p0, i)
            j = text.find(closer, i + 2)
            if j == -1:                            # unterminated (check 7)
                emit('math', i, n)
                i = n
            else:
                j += 2
                emit('math', i, j)
                i, p0 = j, j
            continue
        if c == '$' and (i == 0 or text[i - 1] != '\\'):
            emit('prose', p0, i)
            j = i + 1
            while j < n and not (text[j] == '$' and (j == 0 or text[j - 1] != '\\')):
                j += 1
            if j >= n:
                emit('math', i, n)
                i = n
            else:
                j += 1
                emit('math', i, j)
                i, p0 = j, j
            continue
        # inline code in prose: \texttt{…} \mbox{…} \url{…} \path{…} — the argument
        # is code-style (a quoted char like \texttt{'O'} is legitimate), so it is
        # tagged inlinecode: excluded from the accent check, and (unlike a verbatim
        # listing) it is NOT subject to the ASCII rule (text mode takes UTF-8).
        mc = INLINECODE.match(text, i)
        if mc:
            emit('prose', p0, i)
            e, d = mc.end(), 1
            while e < n and d:
                if text[e] == '{':
                    d += 1
                elif text[e] == '}':
                    d -= 1
                e += 1
            emit('inlinecode', i, e)
            i, p0 = e, e
            continue
        if c == '%' and (i == 0 or text[i - 1] != '\\'):
            emit('prose', p0, i)
            j = text.find('\n', i)
            j = n if j == -1 else j
            emit('comment', i, j)
            i, p0 = j, j
            continue
        i += 1
    emit('prose', p0, n)
    return spans


def deaccent(ch):
    """The ASCII base of an accented character (è→e), or '' if it has none."""
    d = unicodedata.normalize('NFD', ch)
    base = ''.join(c for c in d if not unicodedata.combining(c))
    return base if (base and ord(base[0]) < 128) else ''


# ---------------------------------------------------------------- the checks
# each returns (violations, edits); violations are human strings, edits are
# (start, end, replacement) over the raw text.

def check_accent(text, spans):
    viol, edits = [], []
    for a, b, ctx in spans:
        if ctx != 'prose':
            continue
        for m in ACCENT_RE.finditer(text, a, b):
            v = m.group(1)
            pos = m.start(1)
            viol.append(f'{line_of(text, pos)}: accent {v}\' → {ACCENT_MAP[v]} (ASCII apostrophe in prose)')
            edits.append((pos, pos + 2, ACCENT_MAP[v]))
    return viol, edits


def check_code_ascii(text, spans):
    viol, edits = [], []
    for a, b, ctx in spans:
        if ctx != 'code':
            continue
        for k in range(a, b):
            ch = text[k]
            if ord(ch) > 127:
                base = deaccent(ch)
                what = f'→ {base}' if base else f'(no ASCII base, {unicodedata.name(ch, "?")})'
                viol.append(f'{line_of(text, k)}: non-ASCII {ch!r} in lstlisting {what}')
                if base:
                    edits.append((k, k + 1, base))
    return viol, edits


def _texttt_args(text):
    """Yield (arg_start, arg_end) for each \\texttt{…} (one brace level)."""
    for m in TEXTTT_RE.finditer(text):
        s = m.end()
        if s < len(text) and text[s] == '{':
            d, e = 1, s + 1
            while e < len(text) and d:
                if text[e] == '{':
                    d += 1
                elif text[e] == '}':
                    d -= 1
                e += 1
            yield s + 1, e - 1


def check_texttt(text, spans):
    viol, edits = [], []
    # a \texttt in prose / inlinecode is a real command; one inside a listing
    # (code) or a comment is literal text — so exclude only code + comment.
    blocked = [(a, b) for a, b, c in spans if c in ('code', 'comment')]

    def blocked_pos(p):
        return any(a <= p < b for a, b in blocked)

    for s, e in _texttt_args(text):
        if blocked_pos(s):
            continue
        for k in range(s, e):
            ch = text[k]
            if ch not in TEXTTT_SPECIALS or (k != s and text[k - 1] == '\\'):
                continue
            # a # followed by a digit is a macro parameter (#1 … #9), not a literal
            if ch == '#' and k + 1 < e and text[k + 1].isdigit():
                continue
            viol.append(f'{line_of(text, k)}: unescaped {ch!r} in \\texttt '
                        f'→ {TEXTTT_SPECIALS[ch]}')
            edits.append((k, k + 1, TEXTTT_SPECIALS[ch]))
    return viol, edits


def check_bar_sub(text, spans):
    viol, edits = [], []
    for a, b, ctx in spans:
        if ctx != 'math':
            continue
        for m in BAR_RE.finditer(text, a, b):
            pos = m.start()
            viol.append(f'{line_of(text, pos)}: \\bar{{…}} + sub/superscript '
                        f'mis-renders under sfmath → \\overline')
            edits.append((pos, pos + 4, r'\overline'))   # \bar -> \overline
    return viol, edits


def check_xref(labels, refs):
    """refs: list of (file, line, kind, name). Report-only (no safe fix)."""
    viol = []
    for f, ln, kind, name in refs:
        if name not in labels:
            viol.append(f'{f}:{ln}: \\{kind}{{{name}}} — no matching \\label in the book')
    return viol, []


def check_usepackage(text, is_chapter):
    if not is_chapter:
        return [], []
    viol = [f'{line_of(text, m.start())}: \\usepackage in a chapter file '
            f'(packages belong to main.tex)' for m in re.finditer(r'\\usepackage', text)]
    return viol, []


def check_math_end(text):
    """An opener with no closer, scanned over the WHOLE raw text (a real defect)."""
    viol = []
    # (?<!\\) excludes the \\[len] line-break (a [ preceded by a second \)
    for m in re.finditer(r'(?<!\\)\\\[', text):
        if '\\]' not in text[m.end():]:
            viol.append(f'{line_of(text, m.start())}: \\[ with no matching \\]')
            break
    for m in re.finditer(r'(?<!\\)\\\(', text):
        if '\\)' not in text[m.end():]:
            viol.append(f'{line_of(text, m.start())}: \\( with no matching \\)')
            break
    for m in BEGIN.finditer(text):
        if m.group(1).rstrip('*') in MATH_ENVS and \
                not re.search(r'\\end\{' + re.escape(m.group(1)) + r'\}', text[m.end():]):
            viol.append(f'{line_of(text, m.start())}: \\begin{{{m.group(1)}}} with no \\end')
            break
    return viol, []


def check_lstlang(text):
    viol = []
    for m in LSTLANG_RE.finditer(text):
        for opt in m.group(1).split(','):
            opt = opt.strip()
            if opt.startswith('language='):
                lang = opt.split('=', 1)[1].strip()
                if lang.lower() not in LISTINGS_LANGS:
                    viol.append(f'{line_of(text, m.start())}: lstlisting language={lang} '
                                 f'is not defined in this setup')
    return viol, []


# ---------------------------------------------------------------- the driver

ALL = ['accent', 'code-ascii', 'texttt', 'bar-sub', 'xref',
       'usepackage', 'math-end', 'lstlang']
FIXABLE = {'accent', 'code-ascii', 'texttt', 'bar-sub'}


def lint_file(path, text, labels, fix=False):
    spans = scan(text)
    refs = [(path, line_of(text, m.start()), m.group(1), m.group(2))
            for m in REF_RE.finditer(text)]
    plan = []
    plan.append(('accent', check_accent(text, spans)))
    plan.append(('code-ascii', check_code_ascii(text, spans)))
    plan.append(('texttt', check_texttt(text, spans)))
    plan.append(('bar-sub', check_bar_sub(text, spans)))
    plan.append(('xref', check_xref(labels, refs)))
    plan.append(('usepackage', check_usepackage(text, path.startswith('latex/reversi_')
                                                 and path != 'latex/main.tex')))
    plan.append(('math-end', check_math_end(text)))
    plan.append(('lstlang', check_lstlang(text)))
    return plan


def apply_edits(text, edits):
    out = text
    for start, end, repl in sorted(edits, key=lambda e: e[0], reverse=True):
        out = out[:start] + repl + out[end:]
    return out


def main(argv):
    fix = False
    only = set(ALL)
    paths = []
    for a in argv:
        if a == '--write':
            fix = True
        elif a.startswith('--fix='):
            fix = True
            only = set(a.split('=', 1)[1].split(','))
        elif not a.startswith('--'):
            paths.append(a)
    if not paths:
        print(__doc__.strip().splitlines()[-1])
        print('usage: latex_lint.py [--write | --fix=a,b,…] FILE …')
        return 2

    # the label universe is book-wide (a ref may point to any chapter).
    labels = set()
    corpus = {}
    for p in paths:
        t = open(p, encoding='utf-8').read()
        corpus[p] = t
        labels.update(LABEL_RE.findall(t))

    total_viol = 0
    for p in paths:
        text = corpus[p]
        plan = lint_file(p, text, labels, fix)
        file_viol = [v for _, (vs, _) in plan for v in vs]
        total_viol += len(file_viol)
        tag = 'FAIL' if file_viol else 'ok  '
        print(f'{p}: {tag} ({len(file_viol)})')
        for v in file_viol:
            print(f'    {v}')
        if fix and file_viol:
            edits = []
            for name, (vs, es) in plan:
                if name in only and name in FIXABLE:
                    edits.extend(es)
            if edits:
                new = apply_edits(text, edits)
                open(p, 'w', encoding='utf-8').write(new)
                print(f'    --write: applied {len(edits)} safe fix(es) '
                      f'[{",".join(n for n, _ in plan if n in only and n in FIXABLE)}]')
    print(f'---\ntotal violations: {total_viol}')
    return 1 if total_viol else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
