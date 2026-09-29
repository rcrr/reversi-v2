# rules.md — active rules ("legislative body")

The register of every RULE in force right now — the contracts that must outlive the campaign that created them.
Consulted whenever a standing rule is in question. This is NOT a place for narrative: the history and the rationale live
in notes/decisions.md (the append-only historical log); the D-number on each line is the origin pointer into it.

Lifecycle (same commit as the decision it records):
- RECORD — every decision (including "leave as-is for now") goes to notes/decisions.md with date and rationale.
- PROMOTE — a decision that establishes an enduring rule adds its numbered line here, in the same commit.
- RETIRE — a rule no longer in force is removed here, and the retirement is logged in decisions.md with a new D-number.

Governance: a rule is added, amended or retired only on explicit user approval. The R-numbers are sequential, global and
NEVER reused (an amendment keeps its number; a retirement leaves the gap). A rule is a bold title line
(`**R-NNN — the topic**`), a blank line, and a 1–3 line description (longer only when it must be) — or, when the rule
fits, one bold line; two blank lines between one rule and the next. Lines are ~120 chars. When a new rule is best placed
in a specific order a notation (`**R-NNN.N — the topic**`) can be used.

## Roles of the notes files

**R-001 — AGENTS.md**

The constitution: the standing instructions, auto-injected, kept small.


**R-002 — notes/rules.md**

This file: the active legislation. Every rule stated in this file has precedence over other notes, documents or
decisions. Departure from the rules is possible only with explicit consent from the user.


**R-003 — notes/overview.md**

The entry point (read first; updated after each milestone and at the end of each work session): the current state, the
next steps, the index. The format is RIGID in notes/overview_rules.md (the eight sections in fixed order, the table
grammar, the cell rules, the reference families).


**R-004 — notes/decisions.md**

The OPEN historical decision log (append-only; the "why"; consulted on demand). Format (D-209): ~120 chars/line; a blank
line before every entry; code spans for the paths and the function / file names; backslash-escaped asterisks for the
math multiplications, so the Markdown renders without stray italics. Volume rotation (D-118, the cap amended to 1000
lines at D-333): the open volume keeps this name; past 1000 lines it closes at a session boundary as decisions_NNN.md
and a new decisions.md is opened — the D-numbers stay global and immutable across the volumes.


**R-005 — notes/log_NNN.md**

The session journals (rotating volumes; the format is rigid in notes/log_rules.md).


**R-006 — The domain rule files**

notes/naming.md, notes/docs_rules.md, notes/log_rules.md, notes/overview_rules.md, notes/probe_rules.md, notes/tools.md
(rigid; each owns its domain — this register points at them, never duplicates them).


**R-007 — notes/ideas.md**

The OPEN backlog (I-NNN); notes/ideas-closed.md — the CLOSED ideas (done | dropped). Format (D-235):
`I-NNN | status | idea`, a 9-space continuation indent, a blank line before every entry, code spans for the paths /
identifiers; the statuses are idea | follow-up | in-progress (closed: done | dropped). A closed idea MOVES to
ideas-closed.md, compacted to the statement + the D-pointer + the outcome, in the same commit as the closing decision;
the campaign history stays in decisions.md / the journal. The I-numbers are global, never reused or renumbered.

## Language & collaboration

**R-008 — Notes and workspace comments: English. Replies to the user: Italian. (D-002)**


**R-009 — Notes are autonomous**

After each milestone and at the end of a work session, update notes/overview.md and the relevant notes/ files without
being asked; the source files are modified only on explicit user request. (D-004; AGENTS rules 2–3)


**R-010 — One D-number per fix campaign**

One commit per item + a notes-wave commit at the campaign close (the D-111 pattern).


**R-011 — The notes are the Reversi portfolio (the GitHub publication material)**

Never record DSH/vLLM/harness infrastructure behavior in decisions.md or the journals. (D-154)

## Layout & tree

**R-012 — The workspace is a git repo (D-003)**

Minimal .gitignore: .venv/, build/, scratch/, .obsidian/ (D-009); scratch/ is a disposable session area, never tracked
(AGENTS rule 7).


**R-013 — All Python sources under src/ (D-006)**

The package is `reversi` under src/reversi/ (D-008; D-133: the core at the top level, the tools/ and lm/ subpackages);
the unit tests in test/, a root tree mirroring src/ one file to one file (D-273).


**R-014 — .venv at the workspace root (gitignored)**

pyproject.toml is the minimal editable-install form, with the implicit requirements declared as they are hit
(D-010, D-011).


**R-015 — docs/ mirrors src/ one file to one file**

src/reversi/X.py → docs/src/reversi/X.md (D-007); the test files mirror the same way: test/reversi/X.py →
docs/test/reversi/X.md (D-273).


**R-016 — tools/ (workspace root) holds the MAINTENANCE tools**

The notes/docs format re-wrapper, the mirror-doc auditor, the suite counter (D-248). It is NOT the package's
src/reversi/tools/ (that one ships, D-133) and NOT probes/ (the per-module verification apparatus): a tool that makes no
a/b/c check belongs here, outside the campaign sweep. The rules for creating, documenting and retiring one:
notes/tools.md (the four requirements — general utility, a clear API, reproducible + testable, does no damage).


**R-017 — Code-generated data that is expensive to replicate goes in build/ (gitignored)**

NEVER inside src/, notes/ or any other code folder: a git clone must be self-contained (the cloner recomputes it once);
the persistent data is a DB/campaign artifact, decided explicitly. (D-176)

## Naming & platform

**R-018 — Reversi, NOT chess**

The column/row vocabulary; A1 = top-left = bit 0; the D8 symmetries are canonized in notes/naming.md — the order is
arbitrary but fixed: do not reorder or rename. (D-013, D-014)


**R-019 — The platform is little-endian only: the hashes use native tobytes, no portability work. (D-022)**


**R-020 — A2xxx = the legacy production model family**

Do NOT "fix" these names (the session-21 review; the conventions in docs/src/reversi/lm/logistic_model.md).


**R-021 — The injected cache helpers are named `*_for_current_level`**

The workers must use them in lockstep with the StateMachine injection; never reintroduce the legacy names (D-069).

## Test discipline

**R-022 — Tests write files only under workspace_root/build/tmp, and clean up afterwards (D-065)**


**R-023 — Test-file idiom (D-085)**

CUSTOM_TMP_BASE derived via __file__ (the shared test.reversi.paths module), setUpClass mkdir, TemporaryDirectory FIRST
in setUp, defensive tearDown, WORKSPACE_ROOT-anchored paths.


**R-024 — DB-dependent tests**

db_long_gate(self) (test/reversi/tags.py) first in setUp (D-080, D-130: the SKIP_REGAB_DB gate plus the LONG tier); the
header must state the gated state.


**R-025 — PERF=1 performance tests are print-only**

No performance gates in any suite (D-036).


**R-026 — Worker factories**

A uniform @validate_call gate (the arbitrary_types_allowed config); the tests patch the factory by name in the importing
module's namespace. (D-100)


**R-027 — The test runner is unittest (stdlib), deliberate**

pytest is not a dependency; do not propose a migration to pytest or another runner. (D-124)


**R-028 — Float64 pipeline-metric goldens use assert_close (test/reversi/closecheck.py, rel 1e-9 / abs 1e-12)**

The multi-threaded OpenBLAS ddot is not bit-portable across thread counts or CPUs. Bit-exact assertEqual stays for the
int/uint counts, the f32-quantized values (train_loss, g_norm, the tps read-back truncations), the sha3 hashes and the
in-run determinism tests. (D-127)


**R-029 — Suite tiers (D-130; the VVLONG tier at D-256)**

Default = the fast tier (no DB); LONG=1 adds the DB-gated pipeline tests; VLONG=1 adds the long instruments (the A2050
end-to-end chain); VVLONG=1 adds the very-long ones (the 1e6 corpus benchmark, the 1e7 corpus test) — the tiers are
CUMULATIVE (each implies the previous ones), and the single source of the semantics is `test.reversi.tags` (tier_vlong /
tier_vvlong / db_long_gate); PERF=1 (D-036) and SKIP_REGAB_DB=1 are orthogonal. A new tier means: a predicate in
tags.py, the runner header, this bullet, the overview. Before every commit run the FULL pre-commit: LONG=1
./run_utests.sh (the live regab DB is the normal environment) — VLONG=1 only when it is useful, and the gated run
(SKIP_REGAB_DB=1) is not a substitute. The canonical runner is run_utests.sh: the modules in canonical order — the
tools, the board/pattern concepts, the infrastructure, the DB access, then the pipeline in machine order with each data
module immediately before its worker, the end-to-end chain last; a new test module is inserted at its logical position,
never appended at the end.

## Pipeline contracts (RLM)

**R-030 — Worker 0 (CREATED) is an intentional sentinel**

The machine never invokes its up()/down() — the domain's first worker runs outside the machine. (D-059)


**R-031 — Failure semantics**

After a failure at step k, current_step stays at k (the failed step); a same-target retry executes only the steps above
k; the machine re-raises and is domain-agnostic — the recovery (move_to_step(k-1), then up) and any failure handling is
the domain worker's responsibility. (D-060)


**R-032 — Worker names are UNIQUE**

Enforced fail-fast in StateMachine.__init__ (a case-insensitive duplicate check → ValueError before any state is
touched). (D-061)


**R-033 — Gate split**

The domain pydantic ValidationErrors are NOT converted to the gate's TypeError — the gate passes the domain errors
through. (D-076)


**R-034 — Blackboard: the LMContext fields are pre-declared before a worker consumes or publishes them. (D-099)**


**R-035 — Cache flow**

The cache_manager load-or-compute with the .SHA3-256 sidecar and the 8192-chunk verify (D-071/D-072); the
rlmwf_NN_ names are flat filename-prefix concatenations, not pathlib joins (D-069, D-076).


**R-036 — bool is not a valid step (D-069).**


**R-037 — The stop is TARGET-DRIVEN**

The facade's `run(target_level=None)` runs the first real level (CONFIG) first, then stops at the explicit argument,
else at the domain's configured target (`LMConfig.target_level`), else at the last step; "last" (any case) and a blank
value mean the whole pipeline, and ANY level name (case-insensitive) or int index is a legal stop. The target step IS
executed, and a second `run()` with a deeper target RESUMES — the levels already done are not re-run (their ctx
artifacts survive, the caches stay hot). (D-260)

## Docs

**R-038 — Mirror rule + the rigid mirror format**

Mirror rule (D-007) + the rigid mirror format in notes/docs_rules.md (the header — the H1 + the what-it-is paragraph,
the D-109 `> State:` line RETIRED at D-240 —, the 7 sections, the forbidden-history list, the same-commit lifecycle, the
test-doc variant).


**R-039 — The "Open issues" section**

OPEN R/M/T items with pointers only; if none, one line, `None.`; closed items never appear (docs_rules.md §4, D-114).


**R-040 — Docstrings: WHAT, never HOW**

Docstrings explain WHAT (the observable contract: the semantics, the shapes, the stream/consumption promises), never HOW
— the mechanism lives in the mirror doc's Architecture section and in the code comments; and no D-XXX provenance in the
docstrings (decisions.md is its home; a `#:` code comment only if fundamental). (D-224, D-226)


**R-041 — The src/ docstring style (the descriptive format)**

(1) the imperative first line (one sentence, a verb: Calculate / Compute / Run / Generate); (2) the body paragraph —
what is measured or computed and why (the observable contract; the formulas defining the output values stay in the
docstring, they ARE the WHAT); (3) the Args: section, the Google 8-space indent, each argument typed in parentheses +
described (the types mirror the real annotations); (4) the Returns: section, the key-by-key detail (the dict keys, the
degenerate behaviors — the nan / None / 0 conventions, the exceptions). It completes the WHAT-only rule above: that rule
constrains the CONTENT (no HOW, no D-XXX), this one the FORMAT. Scope: public + private functions in src/ (the test /
the probe docs keep their own rules, D-267/D-270); it binds the NEW docstrings and any REWRITTEN one; the retroactive
conversion of the existing modules is user-directed, one module at a time (like the D-314 reflow), never an agent
initiative. The exemplar: hlp_anova (D-317). (D-318)


**R-042 — Provenance vs design pointers**

Provenance means the file's OWN change history ("before I-018", "the D-106 re-pin", "fix campaign CLOSED") — that is
OUT. Design POINTERS to other decisions explaining a current choice stay: prescribed in mirror docs (docs_rules.md
§3.2), and in source comments when the choice is non-obvious (the D-150 report pointer, the D-146 two-loop note).
(D-269, D-270)


**R-043 — Test docs (the docstrings + the comments in test/)**

State what is tested, optionally how it is realized (the mechanism, the preconditions, the postconditions); no D-xxx /
I-xxx references, no evolution history, and no level ordinals that drift as levels come and go (name the level:
CLIENT_CHECK, PLOT). (D-267)


**R-044 — Probe docs**

The same rules apply to the probes/ docstrings and comments; one exception: the probe's own check labels and item ids
("C5 … (I-013 …)") are the probe's vocabulary and stay — the text asserted and the surrounding comments follow the
test-doc rules. (D-270)

## Code style

**R-045 — Source line length**

No linter gate, no hard limit (pyproject carries no flake8/ruff config). New or EDITED lines match the local file's wrap
convention (the lm zone historically wraps at ~72–76); a convention-less file defaults to <= 79 (PEP8). A full-file
reflow to 120 is a deliberate, user-directed act (the wrk_anova.py reflow is its precedent — D-314), never an agent
side-effect, and untouched lines are never re-wrapped. The docs/notes stay at ~120 (D-237). (D-314)

## Journal

**R-046 — The journal format is rigid in notes/log_rules.md**

The global session numbering across the volumes, the step-N entries, one volume per 25 sessions or 2000 lines (whichever
first), the rotation only at a session boundary.
