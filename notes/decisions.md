# Decisions log

Format: D-NNN | date | decision | rationale

D-001 | 2026-08-25 | Incremental staging workflow: copy one source file at a
       time into this workspace and develop here; no full-repo work now.
       | The full repo is 18 years old with many used/unused files; bringing it
       all in would be too dispersivo. The workflow must be proven here first.
       Full-repo restructure stays a later goal (I-001).

D-002 | 2026-08-25 | Notes and workspace comments: English.
       | User choice; code comments in the repo are English.
       Conversational replies to the user remain in Italian.

D-003 | 2026-08-25 | `git init` in the staging workspace.
       | Safety net for 18-year-old source files and for the notes. Verified in
       the dsh-agent-instructions source (findProjectRoot, files.ts) that
       AGENTS.md injection works with or without git (fallback root = cwd).

D-004 | 2026-08-25 | Autonomy: the agent updates NOTES.md and notes/
       autonomously after each milestone/end of work; source files are touched
       ONLY on explicit user request.
       | User choice. Keeps the knowledge layer current without waiting, and
       keeps 18-year-old code under strict human control.

D-005 | 2026-08-25 | Three-layer memory: AGENTS.md (standing instructions,
       auto-injected every session by the dsh-agent-instructions plugin) +
       NOTES.md (state/next steps, read first) + notes/ (knowledge, on demand).
       | Makes "read the state first" structural instead of relying on either
       party remembering. AGENTS.md stays small (prompt byte budget applies);
       content lives in NOTES.md/notes/.

D-006 | 2026-08-25 | All Python sources live under `src/` (src layout);
       never in the project root.
       | Python best practice: no accidental in-tree imports during tests,
       clean path to packaging at the later full restructure. Test location
       still open — to be decided when test_board.py arrives (candidates:
       top-level `tests/` or `src/tests/`). All notes must stay consistent
       with this tree.

D-007 | 2026-08-25 | Code documentation lives under `docs/` and mirrors the
       source tree: `src/X.py` → `docs/src/X.md`. `notes/` keeps only
       collaboration content (decisions, ideas, log).
       | docs/ is the universal convention for code documentation, is assumed
       by doc tooling, and migrates as-is into the restructured repo
       (I-001). Mirroring keeps the lookup rule trivial as the file count
       grows. Code knowledge and process journal are different natures and
       get different homes.

D-008 | 2026-08-25 | Sources live in the `twolm` package under src/
       (src/twolm/); unit tests inside the package at src/twolm/test/
       (resolves the open test-location item in D-006).
       | Prescribed by the code itself: test_board.py does
       `from twolm.board import *` and its header documents
       `python3 -m unittest twolm.test.test_board` (old repo: PYTHONPATH=./py).
       In staging the same invocation uses PYTHONPATH=./src. Both packages
       (twolm, twolm.test) got minimal `__init__.py` scaffolding.

D-009 | 2026-08-25 | Obsidian local vault state (`.obsidian/`) is gitignored
       at the workspace root; `logistello-papers/.obsidian/` was untracked
       (files kept on disk).
       | Obsidian rewrites workspace.json on every open, dirtying the working
       tree constantly. .gitignore only affects untracked files, so the
       already-tracked copy had to be untracked (git rm --cached).
       .gitignore is deliberately minimal for now ("per cominciare"); more
       entries (e.g. __pycache__/, .venv/) when needed.

D-010 | 2026-08-25 | Virtualenv `.venv/` at the workspace root
       (gitignored) with the minimal dependency set for the board module:
       numpy, pydantic, numba.
       | User choice: only what is necessary, nothing else. The set is
       derived from the actual third-party imports of src/twolm/board.py
       and src/twolm/test/test_board.py (none beyond these three).
       Installed 2026-08-25: numpy 2.5.2, pydantic 2.13.4, numba 0.67.0
       (llvmlite 0.49.0 transitive). Tests are NOT run yet — execution
       happens together with the user.

D-011 | 2026-08-25 | Project packaging: minimal `pyproject.toml` (setuptools,
       src layout) with twolm installed editable into .venv.
       | User request ("installa il python .venv"): make the project
       importable from the venv without PYTHONPATH. Editable install
       (PEP 660) keeps a single source of truth in src/ — no copies, no
       reinstall after edits. `dependencies` (numpy>=2.0, pydantic>=2,
       numba>=0.60) reproduces the D-010 set in a fresh venv. Test command
       becomes `.venv/bin/python -m unittest twolm.test.test_board` (the
       old PYTHONPATH=./src invocation still works as a fallback).

D-012 | 2026-08-25 | Test-suite analysis is doc-only: all defects and gaps
       are catalogued in docs/src/twolm/test/test_board.md; nothing in
       src/twolm/test/test_board.py is changed.
       | User scope for this task: analysis + completeness feedback, no
       fixes. Source/test edits only on explicit request (D-004). The 11
       defects (incl. one broken 2-D test, two NameError landmines in
       failure paths, one dead assertion) and the P0/P1/P2 priority list
       are the ready input for a follow-up fix session.

D-013 | 2026-08-26 | T08 (report §5.8) REJECTED: the 8 header constants in
       test_board.py (row_1, row_8, column_a, column_h, half_left,
       half_right, half_top, half_bottom) are NOT renamed; the code is
       correct as-is. No code change, no commit of sources.
       | The report finding used chess vocabulary ("file a", "rank 1") and
       called the constants "transposed"; the project convention is
       row/column, not file/rank — this is Reversi, not chess. Roberto
       (2026-08-26): the error was the analysis, not the code. The
       canonical convention is now recorded in notes/naming.md, with a
       standing rule in AGENTS.md and a pointer in NOTES.md, so the
       vocabulary error cannot recur in future sessions.
