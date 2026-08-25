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
