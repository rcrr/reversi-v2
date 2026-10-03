# rules.md — active rules ("legislative body")

The register of every RULE in force right now — the contracts that must outlive the campaign that created them.
Consulted whenever a standing rule is in question. This is NOT a place for narrative: the history and the rationale live
in notes/decisions.md (the append-only historical log).

Lifecycle (same commit as the decision it records):
- RECORD — every decision (including "leave as-is for now") goes to notes/decisions.md with date and rationale.
- PROMOTE — a decision that establishes an enduring rule adds its numbered line here, in the same commit.
- RETIRE — a rule no longer in force is removed here, and the retirement is logged in decisions.md with a new D-number.

Governance: a rule is added, amended or retired only on explicit user approval. The R-numbers are global, ordered from
the smallest to the largest, and NEVER reused (an amendment keeps its number; a retirement leaves the gap); the order is
by value: R-510 < R-511 < R-511.1 < R-511.3 < R-511.17 < R-512 < R-600 < R-999. A rule is a bold title line
(`**R-NNN — the topic**`), a blank line, and a 1–3 line description (longer only when it must be) — or, when the rule
fits, one bold line; two blank lines between one rule and the next. Lines are ~120 chars. When a new rule is best placed
in a specific order a notation (`**R-NNN.N — the topic**`) can be used.

## Roles of the notes files

**R-010 — AGENTS.md**

The constitution: the boot protocol (the context pointers + the iron rules), auto-injected, kept small.


**R-020 — notes/rules.md**

This file: the active legislation. Every rule stated in this file has precedence over other notes, documents or
decisions. Departure from the rules is possible only with explicit consent from the user.


**R-030 — notes/overview.md**

The entry point (read first; updated after each milestone and at the end of each work session): the current state, the
next steps, the index. The format is RIGID in notes/overview\_rules.md (the eight sections in fixed order, the table
grammar, the cell rules, the reference families).


**R-040 — notes/decisions.md**

The OPEN historical decision log (append-only; the "why"; consulted on demand); the closed volumes live in
notes/hist\_decisions/. The format is RIGID in notes/decisions\_rules.md (the entry grammar, the volumes and rotation).


**R-050 — notes/log.md**

The session journal (the current one is notes/log.md, the archived volumes are notes/hist\_log/log\_NNN.md; the format
is rigid in notes/log\_rules.md).


**R-060 — The domain rule files**

notes/naming.md, notes/decisions\_rules.md, notes/docs\_rules.md, notes/log\_rules.md, notes/overview\_rules.md,
notes/probe\_rules.md, notes/tools.md (rigid; each owns its domain — this register points at them, never duplicates
them).


**R-070 — notes/ideas.md**

The OPEN backlog (I-NNN); notes/ideas\_closed.md — the CLOSED ideas (done | dropped). The format, the status legend, the
closure lifecycle and the I-numbering are in each file's preamble.

## Language & collaboration

**R-100 — Notes and workspace comments: English. Replies to the user: his own language (e.g. Italian).**


**R-110 — Notes are autonomous**

After each milestone and at the end of a work session, update notes/overview.md and the relevant notes/ files without
being asked; the source files are modified only on explicit user request.


**R-120 — One D-number per fix campaign**

One commit per item + a notes-wave commit at the campaign close.


**R-130 — The notes are the Reversi portfolio (the GitHub publication material)**

Never record DSH/vLLM/harness infrastructure behavior in decisions.md or the journals.

## Notes format guard

**R-200 — The notes format guard**

After every edit of a notes file, the notes format guard must pass GREEN before the commit (red = no commit):
wsutils/notes\_lint.py, read-only, exit 0/1, default set the open decisions log + the register + the open journal (the
closed volumes on explicit request). It implements the grammatical checks of the notes formats (the decisions log per
notes/decisions\_rules.md, the register per its Governance block, the journals per notes/log\_rules.md).


**R-210 — The pre-commit gate**

Every checkin passes wsutils/hooks/pre-commit (tracked, installed via git config core.hooksPath wsutils/hooks): the
format guard on the staged notes files (a file becomes clean when it is touched) + the overview bookkeeping auditor (the
four lists agree with the tree, and the Suite column agrees with the latest suite measurement). The suite is run ONLY
through the wsutils wrapper, which writes the timestamped measurement to scratch/ — no measurement file, no green. Red =
no commit; --no-verify only on the user's explicit request. The suite run itself stays the R-840 discipline (it is slow
and DB-bound); the gate checks its bookkeeping.

## Change discipline

**R-250 — the impact set (documents per change class)**

Every change touches a class of artifacts, and a closed set of notes documents enumerates or constrains that class: a
new tool in wsutils/ -> notes/wsutils.md (the requirements + the inventory; the overview Source table tracks src/ only,
package src/reversi/tools/ subpackage being a different zone); a new probe in probes/ -> probe\_rules.md, if a rule
changed (the probes carry no inventory); a new file in notes/ or docs/ -> the overview Index (plus the docs mirror, for
source and test files); a notes-format grammar change -> the matching notes/\*\_rules.md (plus wsutils/notes\_format.py,
if the tool implements that grammar); a rule promoted or retired -> the register; any milestone -> the decision log and
the session journal. A change touching several classes carries the union of their document sets; a modification of an
existing artifact carries the set of its class.


**R-260 — the pre-commit consistency check**

Before the final commit of a milestone, the agent checks the impact set: (1) which class of artifacts did this change
touch; (2) which documents does the impact set name for that class; (3) are all of them updated in the same commit. A
document of the impact set deliberately left untouched is named in the decision entry, with its reason.


**R-270 — A new function is checked for duplication before it is introduced**

Before introducing a new function, the agent verifies it is not a duplicate of an existing one — in the package, in the
test helpers, or in the standard library.

## Layout & tree

**R-300 — The workspace is a git repo**

Minimal .gitignore: .venv/, build/, scratch/, .obsidian/; scratch/ is a disposable session area, never tracked.


**R-310 — All Python sources under src/**

The package is `reversi` under src/reversi/; the core at the top level, the tools/ and lm/ subpackages; the unit tests
in test/, a root tree mirroring src/ one file to one file.


**R-320 — .venv at the workspace root**

pyproject.toml is the minimal editable-install form, with the implicit requirements declared as they are hit.


**R-330 — docs/ mirrors src/ one file to one file**

src/reversi/X.py → docs/src/reversi/X.md; the test files mirror the same way: test/reversi/X.py →
docs/test/reversi/X.md.


**R-340 — wsutils/ holds the workspace utilities**

The notes/docs format re-wrapper, the mirror-doc auditor, the suite counter. It is NOT probes/ (the per-module
verification apparatus): a tool that makes no a/b/c check belongs here, outside the campaign sweep. The rules for
creating, documenting and retiring one: notes/wsutils.md.


**R-350 — Code-generated data that is expensive to replicate goes in build/ (gitignored)**

NEVER inside src/, notes/ or any other code folder: a git clone must be self-contained (the cloner recomputes it once);
the persistent data is a DB/campaign artifact, decided explicitly.

## Naming & platform

**R-400 — Reversi (othello), NOT chess**

The column (A-H)/row (1-8) vocabulary; A1 = top-left = bit 0, H8 = bottom-right = bit 63; the D8 symmetries are
canonized in notes/naming.md — the order is arbitrary but fixed.


**R-410 — The platform is little-endian only: the hashes use native tobytes, no portability work.**


## Code style

**R-500 — PEP 8 is the base style; the code is readable.**


**R-510 — The desirable size of a function is 20-30 lines.**


**R-520 — Code lines have a width of about 120 characters**

The limit applies to every physical line of a source file — code, comments, and docstring lines alike; docstrings are
wrapped, not exempt.


**R-530 — Docstrings: WHAT, never HOW**

Docstrings explain WHAT (the observable contract: the semantics, the shapes, the stream/consumption promises), never HOW
— the mechanism lives in the mirror doc's Architecture section and in the code comments.


**R-540 — Docstrings: no D-XXX (no reference to the decisions)**

No D-XXX provenance (the file's own change history) in the docstrings (decisions.md is its home); a `#:` code comment
carries it only if fundamental. A design decision explaining a current choice (not history) may stay in a source comment
when the choice is non-obvious, as a summary, not a reference.


**R-550 — No I-XXX in the code (no reference to the ideas)**

No I-XXX reference in any docstring or comment of the Python code — src, test, or probe; ideas.md is their home.


**R-560 — Docstrings: FORMAT**

(1) the imperative first line (one sentence, a verb: Calculate / Compute / Run / Generate); (2) the body paragraph —
what is measured or computed and why (the observable contract; the formulas defining the output values stay in the
docstring, they ARE the WHAT); (3) the Args: section, the Google 8-space indent, each argument typed in parentheses +
described (the types mirror the real annotations); (4) the Returns: section, the key-by-key detail (the dict keys, the
degenerate behaviors — the nan / None / 0 conventions, the exceptions).


**R-570 — Test docstrings: DEVIATIONS**

Test docstrings are bound by the same docstring rules applied to the code, with one deviation: the docstring may state
how the check is realized (the mechanism, the preconditions, the postconditions). The format is light: one or two lines
stating what is tested; the four-part descriptive format is for functions with a contract.


**R-580 — Probe docstrings: DEVIATIONS**

Probe docstrings are bound by the same docstring rules applied to the code, with one deviation: the probe's own check
labels and item ids ("C5 … (I-013 …)") are the probe's vocabulary and stay.


**R-590 — A new external dependency needs explicit permission**

Every new external library dependency needs the user's explicit permission before it is added; the declaration in
pyproject.toml follows the approval, it does not precede it.

## Docs

**R-700 — The mirror docs (docs/)**

One doc per source file, mirroring the source tree and the test tree; the rigid format is in notes/docs\_rules.md.

## Test discipline

**R-750 — Tests write files only under workspace\_root/build/tmp, and clean up afterwards**


**R-760 — Test-file idiom**

CUSTOM\_TMP\_BASE derived via \_\_file\_\_ (the shared test.reversi.paths module), setUpClass mkdir, TemporaryDirectory
FIRST in setUp, defensive tearDown, WORKSPACE\_ROOT-anchored paths.


**R-770 — DB-dependent tests**

db\_long\_gate(self) (test/reversi/tags.py — the SKIP\_REGAB\_DB + LONG-tier check) first in setUp; the module header
must state the gated state.


**R-780 — PERF=1 performance tests are print-only: no performance gates in any suite**


**R-790 — Worker factories**

A uniform @validate\_call gate (the arbitrary\_types\_allowed config); the tests patch the factory by name in the
importing module's namespace.


**R-800 — The test runner is unittest (stdlib), deliberate**

pytest is not a dependency; do not propose a migration to pytest or another runner.


**R-810 — Float goldens use assert\_close (test/reversi/closecheck.py)**

Float golden tests must use assert\_close to be robust: float results are not bit-reproducible across machines. The
rel/abs tolerances live in closecheck.py; bit-exact assertEqual stays for the int/uint counts, the f32-quantized values,
the sha3 hashes and the in-run determinism tests.


**R-820 — Suite tiers**

Default = the fast tier (no DB); LONG=1 adds the DB-gated pipeline tests; VLONG=1 adds the long instruments; VVLONG=1
adds the very-long ones — the tiers are CUMULATIVE (each implies the previous ones); PERF=1 and SKIP\_REGAB\_DB=1 are
orthogonal. The single source of the tier semantics is test.reversi.tags — a new tier means: a predicate there, the
runner header, this bullet, the overview.


**R-830 — Canonical order**

The canonical runner is run\_utests.sh: the modules in canonical order, a new test module inserted at its logical
position, never appended at the end.


**R-840 — Before git commit**

Before every commit run the FULL pre-commit: the suite through the wsutils wrapper (LONG=1, the live DB — it writes the
measurement the R-210 gate reads) — VLONG=1 only when it is useful, and the gated run is not a substitute.


**R-850 — The documented contract is the specification of the tests**

Every documented behavior of a public API has a pinning test: each documented return key, each documented convention
(the nan/None/0), each documented exception type. A documented behavior without a pin is an Open issue.


**R-860 — The three shapes of a test set**

The tests of a function cover the three shapes of its contract: the happy path, the error cases (each documented error
type raises), and the boundary and degenerate inputs (the documented conventions: empty, extreme, nan/None/0).
