#!/usr/bin/env python3
"""exported_symbols.py — the `__all__` snapshot generator for the src/ tree.

WHAT IT IS: a GENERATOR tool: it walks every .py under src/ (sorted), extracts the module-level
`__all__` with the AST (a plain list of string constants; an annotated assignment is accepted),
and writes the per-file snapshot scratch/exported_symbols.md — one section per file, the exported
names as backticked tokens, the files without an `__all__` (or with one that is not a literal
string list — none in the tree today) marked as such, and the header counts (files / with
`__all__` / without).

The snapshot is a REVIEW artifact (the public API surface of the whole package on one page) —
refresh it after any rename wave or `__all__` edit. It lives in scratch/ (gitignored) and is
regenerated, never hand-edited.

USAGE (from the workspace root):
  .venv/bin/python wsutils/exported_symbols.py

SAFETY: writes ONLY scratch/exported_symbols.md.

ORIGIN: D-530 — the hand-kept scratch snapshot went stale across the D-518..D-529 rename wave;
promotion to wsutils/ so the refresh is a one-liner.
"""

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
OUT = os.path.join(ROOT, 'scratch', 'exported_symbols.md')


def all_of(path):
    """The module-level `__all__` as a list of strings, or None (absent / not a literal list)."""
    with open(path, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    for node in tree.body:
        value = None
        if isinstance(node, ast.AnnAssign) and getattr(node.target, 'id', None) == '__all__':
            value = node.value
        elif isinstance(node, ast.Assign) and any(getattr(t, 'id', None) == '__all__'
                                                   for t in node.targets):
            value = node.value
        if value is None:
            continue
        if isinstance(value, ast.List):
            try:
                return [ast.literal_eval(e) for e in value.elts]
            except ValueError:
                return None
    return None


def main():
    files = []
    for dirpath, _dirnames, filenames in os.walk(SRC):
        for fn in filenames:
            if fn.endswith('.py'):
                files.append(os.path.join(dirpath, fn))
    files.sort()

    with_all, without, sections = [], [], []
    for path in files:
        rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
        names = all_of(path)
        section = [f'## {rel}', '']
        if names is None:
            section.append('_No `__all__`._')
            without.append(rel)
        else:
            section.append(', '.join(f'`{n}`' for n in names))
            with_all.append(rel)
        section.append('')
        sections.append('\n'.join(section))
    header = ['# Exported symbols per source file (`__all__`)', '',
              'Generated from the `src/` tree. A file without an `__all__` exports nothing by name '
              '(its public names are all top-level names).', '',
              f'Files: {len(files)}; with `__all__`: {len(with_all)}; without: {len(without)}.', '']
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(header) + '\n'.join(sections))
    print(f'{OUT}: {len(files)} files, {len(with_all)} with __all__, {len(without)} without')
    return 0


if __name__ == '__main__':
    sys.exit(main())
