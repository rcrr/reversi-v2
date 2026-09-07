# rules.md — active rules ("corpo legislativo")

Role: the register of every RULE in force right now — the
contracts that must outlive the campaign that created them.
Consulted whenever a standing rule is in question. This is NOT a
place for narrative: history and rationale live in
notes/decisions.md (the append-only historical log); the D-number
on each line below is the origin pointer into that log.

Lifecycle (same commit as the decision it records):
- RECORD — every decision (including "leave as-is for now") goes
  to notes/decisions.md with date and rationale.
- PROMOTE — a decision that establishes an enduring rule adds its
  line here, in the same commit.
- RETIRE — a rule no longer in force is removed here and the
  retirement is logged in notes/decisions.md with a new D-number.
Budget: ~150 lines. If it grows past that, prune/consolidate
(with Roberto's approval). A rule is one line or two, grouped by
theme, with its origin D-number.

## Roles of the notes files

- AGENTS.md — the constitution: standing instructions,
  auto-injected, kept small.
- notes/rules.md — this file: the active legislation.
- notes/overview.md — state, next steps, index: current state
  only (entry point; read first; updated after each milestone
  and at the end of each work session; D-117: renamed from
  NOTES.md). Rigid format: exactly the eight sections, in this
  order — Project · Conventions in the code · Environment ·
  Where we are · Next steps · Source files · Test files ·
  Index; English; dates YYYY-MM-DD; suite numbers
  `<total>/<failures>/<skipped>` (total = unittest's "Ran N");
  references D-NNN (decisions.md), I-NNN (ideas.md), session N
  (journal volumes), T-NN (test defect), R# (code issue),
  M# (minor note). Source files / Test files: one table per
  kind, one row per tracked file, alphabetical by full path;
  the State cell is ONE line — a status word + the open/parked
  items (if any) + the D-pointer range (the campaign history
  lives in the decision log, never in the row; D-117); the
  Suite cell carries the file's current verified suite (live
  DB); the Doc cell the mirror path. Table cells: one physical
  line per row; a literal `|` inside a cell is escaped `\|`
  (D-116). Where we are: the non-file state only (the plan, the
  collaboration memory) — the per-file state lives in the
  tables (D-117); no session narrative (that lives in the
  journal volumes + the decision log). Next steps: OPEN items
  only (no "Done" bullets); the LAST bullet is the next
  concrete action. Index: one bullet per notes/ file, one-line
  description; the docs/ mirrors are NOT listed (their paths
  are the Doc column of the tables).
- notes/decisions.md — the OPEN historical decision log
  (append-only; "the why"; consulted on demand or for
  historical research). Volume rotation (D-118, same rhythm as
  the journals): the open volume keeps this name; when it
  exceeds 2000 lines it closes at a session boundary as
  decisions_NNN.md and a new decisions.md is opened; the
  D-numbers stay global and immutable across volumes.
- notes/log_NNN.md — the session journals (rotating volumes;
  format rules in notes/log_rules.md).
- notes/naming.md, notes/docs_rules.md, notes/log_rules.md,
  notes/probe_rules.md — the domain rule files (rigid; each owns
  its domain — this register points at them, never duplicates
  them).
- notes/ideas.md — the backlog of future-evolution ideas (I-NNN).

## Language & collaboration

- Notes and workspace comments: English. Replies to the user:
  Italian. (D-002)
- Notes are autonomous: after each milestone and at the end of a
  work session, update notes/overview.md and the relevant
  notes/ files without being asked; source files are modified
  only on explicit user request. (D-004; AGENTS rules 2–3)
- One D-number per fix campaign; one commit per item + a
  notes-wave commit at the campaign close (the D-111 pattern).

## Layout & tree

- The workspace is a git repo (D-003); minimal .gitignore:
  .venv/, build/, scratch/, .obsidian/ (D-009); scratch/ is a
  disposable session area, never tracked (AGENTS rule 7).
- All Python sources under src/ (D-006); the package is `twolm`
  under src/twolm/ (D-008); unit tests in src/twolm/test/.
- .venv at the workspace root (gitignored), minimal pinned deps
  (D-010); pyproject.toml is the minimal editable-install form
  with the implicit requirements declared as they are hit —
  NumPy ≥ 2.0, lz4, psycopg2, pandas, python-dotenv, scipy,
  json5 (D-011/D-051/D-052/D-094).
- docs/ mirrors src/ one file to one file: src/twolm/X.py →
  docs/src/twolm/X.md (D-007).

## Naming & platform

- Reversi, NOT chess: column/row vocabulary; A1 = top-left =
  bit 0; the D8 symmetries are canonized in notes/naming.md —
  the order is arbitrary but fixed: do not reorder or rename.
  (D-013, D-014)
- The platform is little-endian only: hashes use native tobytes,
  no portability work. (D-022)
- A2xxx = the legacy production model family — do NOT "fix"
  these names (session 21 review; docs/src/twolm/logistic_model.
  md conventions).
- The injected cache helpers are named *_for_current_level —
  workers must use them in lockstep with the StateMachine
  injection; never reintroduce the legacy names (D-069; the
  D-074 R1 trap re-introduced twice: D-097 R1, D-099 R1).

## Test discipline

- Tests write files only under workspace_root/build/tmp, and
  clean up afterwards (D-065).
- Test-file idiom (D-085): CUSTOM_TMP_BASE derived via __file__
  (the shared twolm.test.paths module), setUpClass mkdir,
  TemporaryDirectory FIRST in setUp, defensive tearDown,
  WORKSPACE_ROOT-anchored paths.
- DB-dependent tests: SKIP_REGAB_DB gate at the top of setUp
  (the D-080 T2 shape); the header must state the gated state.
- PERF=1 performance tests are print-only — no performance gates
  in any suite (D-036).
- Worker factories: a uniform @validate_call gate (the
  arbitrary_types_allowed config); tests patch the factory by
  name in the importing module's namespace. (D-100 T2)
- The test runner is unittest (stdlib), deliberate — pytest is
  not a dependency; do not propose a migration to pytest or
  other runners. (D-124)
- Float64 pipeline-metric goldens use assert_close
  (twolm/test/closecheck.py, rel 1e-9 / abs 1e-12): the
  multi-threaded OpenBLAS ddot is not bit-portable across
  thread counts or CPUs (last-ULP drift, measured 2–301 ULP
  after a 4 → 8 vCPU move). Bit-exact assertEqual stays for
  int/uint counts, f32-quantized values (train_loss, g_norm,
  the tps read-back truncations), sha3 hashes and the
  in-run determinism tests. (D-127)

## Pipeline contracts (RLM)

- Worker 0 (CREATED) is an intentional sentinel: the machine
  never invokes its up()/down() — the domain's first worker runs
  outside the machine. (D-059)
- Failure semantics: after a failure at step k, current_step
  stays at k (the failed step); a same-target retry executes
  only the steps above k; the machine re-raises and is
  domain-agnostic — recovery (move_to_step(k-1), then up) and
  any failure handling is the domain worker's responsibility.
  (D-060)
- Worker names are UNIQUE: enforced fail-fast in
  StateMachine.__init__ (case-insensitive duplicate check →
  ValueError before any state is touched). (D-061)
- Gate split: domain pydantic ValidationErrors are NOT converted
  to the gate's TypeError — the gate passes domain errors
  through. (D-076)
- Blackboard: RLMContext fields are pre-declared before a worker
  consumes or publishes them. (D-099)
- Cache flow: the cache_manager load-or-compute with the
  .SHA3-256 sidecar and the 8192-chunk verify (D-071/D-072);
  the rlmwf_NN_ names are flat filename-prefix concatenations,
  not pathlib joins (D-069 M8, D-076).
- bool is not a valid step (D-069 M3).

## Docs

- Mirror rule (D-007) + the rigid mirror format in
  notes/docs_rules.md (the 4-line header with the `> State:`
  line, the 7 sections, the forbidden-history list, the same-
  commit lifecycle, the test-doc variant).
- The "Open issues" section: OPEN R/M/T items with pointers
  only; if none, one line, `None.`; closed items never appear.
  (docs_rules.md §4, D-114)

## Journal

- Journal format is rigid in notes/log_rules.md: global session
  numbering across volumes, step-N entries, one volume per 25
  sessions or 2000 lines (whichever first), rotation only at a
  session boundary.
