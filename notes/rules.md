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
next steps, the index. The format is RIGID in notes/overview\_rules.md (the eight sections in fixed order, the table
grammar, the cell rules, the reference families).


**R-004 — notes/decisions.md**

The OPEN historical decision log (append-only; the "why"; consulted on demand). The format is RIGID in
notes/decisions\_rules.md (the entry grammar, the volumes and rotation).


**R-005 — notes/log\_NNN.md**

The session journals (rotating volumes; the format is rigid in notes/log\_rules.md).


**R-006 — The domain rule files**

notes/naming.md, notes/decisions\_rules.md, notes/docs\_rules.md, notes/log\_rules.md, notes/overview\_rules.md,
notes/probe\_rules.md, notes/tools.md (rigid; each owns its domain — this register points at them, never duplicates
them).


**R-007 — notes/ideas.md**

The OPEN backlog (I-NNN); notes/ideas-closed.md — the CLOSED ideas (done | dropped). The format, the status legend, the
closure lifecycle and the I-numbering are in each file's preamble.

## Language & collaboration

**R-008 — Notes and workspace comments: English. Replies to the user: his own language (e.g. Italian).**


**R-009 — Notes are autonomous**

After each milestone and at the end of a work session, update notes/overview.md and the relevant notes/ files without
being asked; the source files are modified only on explicit user request.


**R-010 — One D-number per fix campaign**

One commit per item + a notes-wave commit at the campaign close.


**R-011 — The notes are the Reversi portfolio (the GitHub publication material)**

Never record DSH/vLLM/harness infrastructure behavior in decisions.md or the journals.

## Layout & tree

**R-012 — The workspace is a git repo**

Minimal .gitignore: .venv/, build/, scratch/, .obsidian/; scratch/ is a disposable session area, never tracked.


**R-013 — All Python sources under src/**

The package is `reversi` under src/reversi/; the core at the top level, the tools/ and lm/ subpackages; the unit tests
in test/, a root tree mirroring src/ one file to one file.


**R-014 — .venv at the workspace root**

pyproject.toml is the minimal editable-install form, with the implicit requirements declared as they are hit.


**R-015 — docs/ mirrors src/ one file to one file**

src/reversi/X.py → docs/src/reversi/X.md; the test files mirror the same way: test/reversi/X.py →
docs/test/reversi/X.md.


**R-016 — tools/ holds the maintenance tools**

The notes/docs format re-wrapper, the mirror-doc auditor, the suite counter. It is NOT the package's src/reversi/tools/
(that one ships) and NOT probes/ (the per-module verification apparatus): a tool that makes no a/b/c check belongs here,
outside the campaign sweep. The rules for creating, documenting and retiring one: notes/tools.md.


**R-017 — Code-generated data that is expensive to replicate goes in build/ (gitignored)**

NEVER inside src/, notes/ or any other code folder: a git clone must be self-contained (the cloner recomputes it once);
the persistent data is a DB/campaign artifact, decided explicitly.

## Naming & platform

**R-018 — Reversi (othello), NOT chess**

The column (A-H)/row (1-8) vocabulary; A1 = top-left = bit 0, H8 = bottom-right = bit 63; the D8 symmetries are
canonized in notes/naming.md — the order is arbitrary but fixed.


**R-019 — The platform is little-endian only: the hashes use native tobytes, no portability work.**


## Test discipline

**R-022 — Tests write files only under workspace\_root/build/tmp, and clean up afterwards**


**R-023 — Test-file idiom**

CUSTOM\_TMP\_BASE derived via \_\_file\_\_ (the shared test.reversi.paths module), setUpClass mkdir, TemporaryDirectory
FIRST in setUp, defensive tearDown, WORKSPACE\_ROOT-anchored paths.


**R-024 — DB-dependent tests**

db\_long\_gate(self) (test/reversi/tags.py — the SKIP\_REGAB\_DB + LONG-tier check) first in setUp; the module header
must state the gated state.


**R-025 — PERF=1 performance tests are print-only: no performance gates in any suite**


**R-026 — Worker factories**

A uniform @validate\_call gate (the arbitrary\_types\_allowed config); the tests patch the factory by name in the
importing module's namespace.


**R-027 — The test runner is unittest (stdlib), deliberate**

pytest is not a dependency; do not propose a migration to pytest or another runner.


**R-028 — Float goldens use assert\_close (test/reversi/closecheck.py)**

Float golden tests must use assert\_close to be robust: float results are not bit-reproducible across machines. The
rel/abs tolerances live in closecheck.py; bit-exact assertEqual stays for the int/uint counts, the f32-quantized values,
the sha3 hashes and the in-run determinism tests.


**R-029 — Suite tiers**

Default = the fast tier (no DB); LONG=1 adds the DB-gated pipeline tests; VLONG=1 adds the long instruments; VVLONG=1
adds the very-long ones — the tiers are CUMULATIVE (each implies the previous ones); PERF=1 and SKIP\_REGAB\_DB=1 are
orthogonal. The single source of the tier semantics is test.reversi.tags — a new tier means: a predicate there, the
runner header, this bullet, the overview.


**R-029.1 — Canonical order**

The canonical runner is run\_utests.sh: the modules in canonical order, a new test module inserted at its logical
position, never appended at the end.


**R-029.2 — Before git commit**

Before every commit run the FULL pre-commit: LONG=1 ./run\_utests.sh (the live regab DB is the normal environment) —
VLONG=1 only when it is useful, and the gated run is not a substitute.

## Docs

**R-038 — The mirror docs (docs/)**

One doc per source file, mirroring the source tree and the test tree; the rigid format is in notes/docs\_rules.md.


**R-041 — The src/ docstring style (the descriptive format)**

(1) the imperative first line (one sentence, a verb: Calculate / Compute / Run / Generate); (2) the body paragraph —
what is measured or computed and why (the observable contract; the formulas defining the output values stay in the
docstring, they ARE the WHAT); (3) the Args: section, the Google 8-space indent, each argument typed in parentheses +
described (the types mirror the real annotations); (4) the Returns: section, the key-by-key detail (the dict keys, the
degenerate behaviors — the nan / None / 0 conventions, the exceptions). It completes the WHAT-only rule (R-045.1) and
its provenance rule (R-045.2): they constrain the CONTENT (no HOW, no D-XXX), this one the FORMAT. Scope: public +
private functions in src/ (the test and probe docstrings keep their own rules, below); it binds the NEW docstrings and
any REWRITTEN one; the retroactive conversion of the existing modules is user-directed, one module at a time, never an
agent initiative. The exemplar: hlp\_anova.


**R-042 — Provenance vs design pointers**

Provenance means the file's OWN change history ("before I-018", "the D-106 re-pin", "fix campaign CLOSED") — that is
OUT. Design POINTERS to other decisions explaining a current choice stay: prescribed in mirror docs (docs\_rules.md
§3.2), and in source comments when the choice is non-obvious.


**R-043 — Test docs (the docstrings + the comments in test/)**

State what is tested, optionally how it is realized (the mechanism, the preconditions, the postconditions); no D-xxx /
I-xxx references, no evolution history, and no level ordinals that drift as levels come and go (name the level:
CLIENT\_CHECK, PLOT).


**R-044 — Probe docs**

The same rules apply to the probes/ docstrings and comments; one exception: the probe's own check labels and item ids
("C5 … (I-013 …)") are the probe's vocabulary and stay — the text asserted and the surrounding comments follow the
test-doc rules.

## Code style

**R-045 — Code lines have a width of about 120 characters**


**R-045.1 — Docstrings: WHAT, never HOW**

Docstrings explain WHAT (the observable contract: the semantics, the shapes, the stream/consumption promises), never HOW
— the mechanism lives in the mirror doc's Architecture section and in the code comments.


**R-045.2 — Docstrings: no D-XXX (no reference to the decisions)**

No D-XXX provenance in the docstrings (decisions.md is its home); a `#:` code comment carries it only if fundamental.

## Notes format guard

**R-047 — The notes format guard**

After every edit of a notes file, the notes format guard must pass GREEN before the commit (red = no commit):
tools/notes\_lint.py, read-only, exit 0/1, default set the open decisions log + the register + the open journal (the
closed volumes on explicit request). It implements the grammatical checks of the notes formats (the decisions log per
notes/decisions\_rules.md, the register per its Governance block, the journals per notes/log\_rules.md).

## Change discipline

**R-049 — the impact set (documents per change class)**

Every change touches a class of artifacts, and a closed set of notes documents enumerates or constrains that class: a
new tool in tools/ -> notes/tools.md (the requirements + the inventory; the overview Source table tracks src/ only, the
package src/reversi/tools/ subpackage being a different zone); a new probe in probes/ -> probe\_rules.md, if a rule
changed (the probes carry no inventory); a new file in notes/ or docs/ -> the overview Index (plus the docs mirror, for
source and test files); a notes-format grammar change -> the matching notes/\*\_rules.md (plus tools/notes\_format.py,
if the tool implements that grammar); a rule promoted or retired -> the register; any milestone -> the decision log and
the session journal. A change touching several classes carries the union of their document sets; a modification of an
existing artifact carries the set of its class.


**R-050 — the pre-commit consistency check**

Before the final commit of a milestone, the agent checks the impact set: (1) which class of artifacts did this change
touch; (2) which documents does the impact set name for that class; (3) are all of them updated in the same commit. A
document of the impact set deliberately left untouched is named in the decision entry, with its reason.
