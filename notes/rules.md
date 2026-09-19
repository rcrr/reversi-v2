# rules.md — active rules ("corpo legislativo")

The register of every RULE in force right now — the contracts that must outlive the campaign that created them.
Consulted whenever a standing rule is in question. This is NOT a place for narrative: the history and the rationale live
in notes/decisions.md (the append-only historical log); the D-number on each line is the origin pointer into it.

Lifecycle (same commit as the decision it records):
- RECORD — every decision (including "leave as-is for now") goes to notes/decisions.md with date and rationale.
- PROMOTE — a decision that establishes an enduring rule adds its line here, in the same commit.
- RETIRE — a rule no longer in force is removed here, and the retirement is logged in decisions.md with a new D-number.

Budget: ~150 lines; past that, prune or consolidate with Roberto's approval. A rule is one or two lines, grouped by
theme, with its origin D-number. Every notes/ Markdown file is wrapped to ~120 chars/line (D-237), with atomic code
spans; the tables and the headings stay one physical line.

## Roles of the notes files

- AGENTS.md — the constitution: the standing instructions, auto-injected, kept small.
- notes/rules.md — this file: the active legislation.
- notes/overview.md — the entry point (read first; updated after each milestone and at the end of each work session):
  the current state, the next steps, the index. Rigid format: exactly the eight sections in this order — Project ·
  Conventions in the code · Environment · Where we are · Next steps · Source files · Test files · Index. English; dates
  YYYY-MM-DD; suite numbers `<total>/<failures>/<skipped>` (total = unittest's "Ran N"); references D-NNN (the
  decisions), I-NNN (the ideas), session N (the journals), T-NN (a test defect), R# (a code issue), M# (a minor note).
  Source files / Test files: one table per kind, one row per tracked file, alphabetical by full path; the State cell is
  ONE line — a status word + the open/parked items + the D-pointer range, never the campaign history (D-117); the Suite
  cell carries the file's current verified suite (live DB); the Doc cell the mirror path. One physical line per row; a
  literal `|` inside a cell is escaped `\|` (D-116). Where we are: the non-file state only — the plan and the
  collaboration memory, no session narrative (D-117). Next steps: OPEN items only, no "Done" bullets; the LAST bullet is
  the next concrete action. Index: one bullet per notes/ file, a one-line description; the docs/ mirrors are not listed
  (their paths are the Doc column of the tables).
- notes/decisions.md — the OPEN historical decision log (append-only; "the why"; consulted on demand). Format (D-209):
  ~120 chars/line; a blank line before every entry; code spans for the paths and the function / file names;
  backslash-escaped asterisks for the math multiplications, so the Markdown renders without stray italics. Volume
  rotation (D-118, the journal rhythm): the open volume keeps this name; past 2000 lines it closes at a session boundary
  as decisions_NNN.md and a new decisions.md is opened — the D-numbers stay global and immutable across the volumes.
- notes/log_NNN.md — the session journals (rotating volumes; the format is rigid in notes/log_rules.md).
- notes/naming.md, notes/docs_rules.md, notes/log_rules.md, notes/probe_rules.md — the domain rule files (rigid; each
  owns its domain — this register points at them, never duplicates them).
- notes/ideas.md — the OPEN backlog (I-NNN); notes/ideas-closed.md — the CLOSED ideas (done | dropped). Format (D-235):
  `I-NNN | status | idea`, a 9-space continuation indent, a blank line before every entry, code spans for the paths /
  identifiers; the statuses are idea | follow-up | in-progress (closed: done | dropped). A closed idea MOVES to
  ideas-closed.md, compacted to the statement + the D-pointer + the outcome, in the same commit as the closing decision;
  the campaign history stays in decisions.md / the journal. The I-numbers are global, never reused or renumbered.

## Language & collaboration

- Notes and workspace comments: English. Replies to the user: Italian. (D-002)
- Notes are autonomous: after each milestone and at the end of a work session, update notes/overview.md and the relevant
  notes/ files without being asked; the source files are modified only on explicit user request. (D-004; AGENTS rules
  2–3)
- One D-number per fix campaign; one commit per item + a notes-wave commit at the campaign close (the D-111 pattern).
- The notes are the Reversi portfolio (the GitHub publication material): never record DSH/vLLM/harness infrastructure
  behavior in decisions.md or the journals. (D-154)

## Layout & tree

- The workspace is a git repo (D-003); minimal .gitignore: .venv/, build/, scratch/, .obsidian/ (D-009); scratch/ is a
  disposable session area, never tracked (AGENTS rule 7).
- All Python sources under src/ (D-006); the package is `reversi` under src/reversi/ (D-008; D-133: the core at the top
  level, the tools/ and lm/ subpackages); the unit tests in src/reversi/test/.
- .venv at the workspace root (gitignored); pyproject.toml is the minimal editable-install form, with the implicit
  requirements declared as they are hit (D-010, D-011).
- docs/ mirrors src/ one file to one file: src/reversi/X.py → docs/src/reversi/X.md (D-007).
- Code-generated data that is expensive to replicate goes in build/ (gitignored) — NEVER inside src/, notes/ or any
  other code folder: a git clone must be self-contained (the cloner recomputes it once); the persistent data is a
  DB/campaign artifact, decided explicitly. (D-176)

## Naming & platform

- Reversi, NOT chess: the column/row vocabulary; A1 = top-left = bit 0; the D8 symmetries are canonized in
  notes/naming.md — the order is arbitrary but fixed: do not reorder or rename. (D-013, D-014)
- The platform is little-endian only: the hashes use native tobytes, no portability work. (D-022)
- A2xxx = the legacy production model family — do NOT "fix" these names (the session-21 review; the conventions in
  docs/src/reversi/lm/logistic_model.md).
- The injected cache helpers are named `*_for_current_level`: the workers must use them in lockstep with the
  StateMachine injection; never reintroduce the legacy names (D-069).

## Test discipline

- Tests write files only under workspace_root/build/tmp, and clean up afterwards (D-065).
- Test-file idiom (D-085): CUSTOM_TMP_BASE derived via __file__ (the shared reversi.test.paths module), setUpClass
  mkdir, TemporaryDirectory FIRST in setUp, defensive tearDown, WORKSPACE_ROOT-anchored paths.
- DB-dependent tests: db_long_gate(self) (reversi/test/tags.py) first in setUp (D-080, D-130: the SKIP_REGAB_DB gate
  plus the LONG tier); the header must state the gated state.
- PERF=1 performance tests are print-only — no performance gates in any suite (D-036).
- Worker factories: a uniform @validate_call gate (the arbitrary_types_allowed config); the tests patch the factory by
  name in the importing module's namespace. (D-100)
- The test runner is unittest (stdlib), deliberate — pytest is not a dependency; do not propose a migration to pytest or
  another runner. (D-124)
- Float64 pipeline-metric goldens use assert_close (reversi/test/closecheck.py, rel 1e-9 / abs 1e-12): the
  multi-threaded OpenBLAS ddot is not bit-portable across thread counts or CPUs. Bit-exact assertEqual stays for the
  int/uint counts, the f32-quantized values (train_loss, g_norm, the tps read-back truncations), the sha3 hashes and the
  in-run determinism tests. (D-127)
- Suite tiers (D-130): default = the fast tier (no DB); LONG=1 adds the DB-gated pipeline tests; VLONG=1 adds the A2050
  end-to-end chain and implies LONG; PERF=1 (D-036) and SKIP_REGAB_DB=1 are orthogonal. Before every commit run the FULL
  pre-commit: LONG=1 ./run_utests.sh (the live regab DB is the normal environment) — VLONG=1 only when it is useful, and
  the gated run (SKIP_REGAB_DB=1) is not a substitute. The canonical runner is run_utests.sh: the modules in canonical
  order — the tools, the board/pattern concepts, the infrastructure, the DB access, then the pipeline in machine order
  with each data module immediately before its worker, the end-to-end chain last; a new test module is inserted at its
  logical position, never appended at the end.

## Pipeline contracts (RLM)

- Worker 0 (CREATED) is an intentional sentinel: the machine never invokes its up()/down() — the domain's first worker
  runs outside the machine. (D-059)
- Failure semantics: after a failure at step k, current_step stays at k (the failed step); a same-target retry executes
  only the steps above k; the machine re-raises and is domain-agnostic — the recovery (move_to_step(k-1), then up) and
  any failure handling is the domain worker's responsibility. (D-060)
- Worker names are UNIQUE: enforced fail-fast in StateMachine.__init__ (a case-insensitive duplicate check → ValueError
  before any state is touched). (D-061)
- Gate split: the domain pydantic ValidationErrors are NOT converted to the gate's TypeError — the gate passes the
  domain errors through. (D-076)
- Blackboard: the LMContext fields are pre-declared before a worker consumes or publishes them. (D-099)
- Cache flow: the cache_manager load-or-compute with the .SHA3-256 sidecar and the 8192-chunk verify (D-071/D-072); the
  rlmwf_NN_ names are flat filename-prefix concatenations, not pathlib joins (D-069, D-076).
- bool is not a valid step (D-069).

## Docs

- Mirror rule (D-007) + the rigid mirror format in notes/docs_rules.md (the 4-line header with the `> State:` line, the
  7 sections, the forbidden-history list, the same-commit lifecycle, the test-doc variant).
- The "Open issues" section: OPEN R/M/T items with pointers only; if none, one line, `None.`; closed items never appear
  (docs_rules.md §4, D-114).
- Docstrings explain WHAT (the observable contract: the semantics, the shapes, the stream/consumption promises), never
  HOW — the mechanism lives in the mirror doc's Architecture section and in the code comments; and no D-XXX provenance
  in the docstrings (decisions.md is its home; a `#:` code comment only if fundamental). (D-224, D-226)

## Journal

- The journal format is rigid in notes/log_rules.md: the global session numbering across the volumes, the step-N
  entries, one volume per 25 sessions or 2000 lines (whichever first), the rotation only at a session boundary.





