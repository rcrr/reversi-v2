# wsutils.md — rules for the workspace utilities (wsutils/)

Prescriptive. Follow when creating, migrating, retiring or using any tool in wsutils/. Language: English. Rigid, like
the companion rule files.

Companions: notes/probe\_rules.md (the verification apparatus — what a tool is NOT), notes/docs\_rules.md (the mirror
format the doc auditor checks), notes/rules.md (the register that points here).

## 1. What a tool IS (and is not)

A tool is a WORKSPACE UTILITY: it serves the maintenance of this repository — the notes and the docs format, the suite
measurement, the audits no test can express. It lives in wsutils/ at the workspace root, tracked in git.

A tool is NOT:

- part of the shipped package: src/reversi/tools/ is the LIBRARY's subpackage (binio, prng, cache\_manager, opt\_lbfgs,
  state\_machine) — a development utility never lands there;
- a probe: probes/ is the CAMPAIGN-LEVEL verification apparatus, with the a/b/c checks and the sweep (probe\_rules §1,
  §5). A tool makes no campaign check and is NOT in the sweep. A tool MAY check something (the doc auditor does): the
  difference is the SCOPE and the LIFE — a probe pins a module's facts and dies with its campaign, a tool serves the
  workspace and lives as long as the workspace does;
- a test: nothing in wsutils/ is discovered or run by run\_utests.sh;
- a home for a one-off: a finished investigation moves to notes/analyses/ (probe\_rules §6), a throwaway dies in
  scratch/.

## 2. The four requirements

Every tool in wsutils/ satisfies all four. A tool that fails one is not a tool yet — it is still a scratch experiment.

**1. GENERAL UTILITY.** It solves a CLASS of problems, not one instance. The test: would it still be useful next
session, on a different file / module / fixture? If not, it is a one-off: archive it (notes/analyses/) or drop it.

**2. A CLEAR API.** A documented CLI in the module docstring — the usage line, the arguments, the exit codes; explicit
arguments; no interactive prompts; no hidden global state; no configuration file. The input → output contract is stated.
A function that another tool imports is small and pure.

**3. REPRODUCIBLE AND TESTABLE.** The same input gives the same output: no timestamps, no unseeded randomness, no
environment-dependent ordering. The tool prints a VERIFIABLE report (the counts, a content fingerprint, the list of the
changes) so the result can be checked by eye or by a diff. The write path is exercised by running the tool twice: an
idempotent tool is a no-op the second time, and says so.

**4. IT DOES NO DAMAGE.** The hard safety rules:

- the DEFAULT is a report: the destructive action needs an EXPLICIT flag (`--write`, `--apply`), never a bare
  invocation;
- a WRITE is verified BEFORE it happens: the tool computes the fingerprint of the intended result and refuses to write
  when the content would change beyond what it declares (the re-wrapper: the token-level fingerprint, the idempotence,
  the fixpoint — a bug cannot silently lose content);
- it touches ONLY the paths it was given, inside the workspace: no recursion into unrelated trees, no absolute path
  outside, no symlink followed out;
- the ARTIFACTS go under build/tmp (the suite measurement is the gate input and goes to scratch/ — R-210), never in the
  tracked tree (probe\_rules §2);
- it never runs a git WRITE command (no commit, no checkout, no reset, no stash): the repository state is Roberto's;
- it never DELETES: the only deletions allowed are the tool's own artifacts under build/tmp;
- the docstring states the exact scope of what it writes.

## 3. The header (fixed)

The module docstring carries, in this order:

1. **WHAT IT IS** — the category (a check / a measurement / a maintenance tool) + the one-line purpose;
2. **USAGE** — the command line, from the workspace root, with `.venv/bin/python wsutils/<name>.py`;
3. **SAFETY** — what it writes, and under which flag (or "writes nothing");
4. **ORIGIN** — the D-number of the campaign that produced it and of the promotion to wsutils/.

## 4. Naming

- `snake_case`, a noun describing WHAT IT DOES: `notes_format.py`, `docs_format_audit.py`, `suite_audit.py`.
- A checker may carry the `_audit` / `_check` suffix; the `verify_` prefix is RESERVED to the probes (probe\_rules §2).
- No dependency beyond the venv: a new one is a decision, not a tool's private choice.

## 5. Lifecycle

1. **BIRTH** — in scratch/ (gitignored; probe\_rules §2).
2. **GRADUATION** — when it proves generally useful: ONE commit carrying the tool (with the header of §3), its inventory
   row here, the rules line when it opens a new category, and the D-number in notes/decisions.md + the journal entry.
3. **MAINTENANCE** — a tool follows what it serves: a format change, a path change or a new fixture updates the tool in
   the SAME commit (the docs\_rules.md §5 same-commit rule). A tool that checks something is run when its target
   changes.
4. **RETIREMENT** — delete the file, remove the row here, log the retirement with a new D-number. A tool is never left
   in scratch/ to die.

## 6. Inventory

One row per tracked tool. Updated in the same commit as the tool it describes.

| tool | category | what it does | what it writes |
|---|---|---|---|
| `notes_format.py` | maintenance | the house re-wrapper: the block grammar (~120 chars, code-span aware, the mid-token rejoins, the span healing) + the per-file verification (the content fingerprint, the idempotence, the fixpoint) | the files passed on the command line, ONLY with `--write`; nothing by default |
| `src_reflow.py` | maintenance | the R-520 source-prose re-wrapper for the .py sources: the docstring lines + the multi-line `#` comment blocks (the preferred 100 / the 120 ceiling / the single-word pull-up; the section structure, the typed entries, the fixed lines, the ASCII-art paragraphs, the license banner and the dividers preserved; the code untouched) + the check mode as the default + the pre-write verification (the per-docstring/per-block logical identity, the parse, the idempotence — a failing file is refused) | the passed .py files, ONLY with `--write`; nothing by default |
| `docs_format_audit.py` | check | audits every docs/\*\*/\*.md against notes/docs\_rules.md: the H1 ↔ the source path, the sections and their order, the §4 forbidden patterns, the size budget, the width, the split code spans, the ragged tables | nothing (a report on stdout) |
| `measure_suite.py` | measurement | the per-test TIMING instrument: every test's duration in milliseconds + the per-module aggregate + the skip census, the baseline of the tiering | `build/tmp/test_durations.txt` |
| `suite_audit.py` | measurement | the suite wrapper of the R-210 gate: runs every test module of run\_utests.sh on its own (LONG=1, the live DB), prints `<module> <ran>/<fail>/<skip>`, and writes the timestamped measurement the overview auditor reads | `scratch/suite_audit.txt` (gitignored, the gate input) |
| `overview_audit.py` | check | the overview bookkeeping auditor: the four lists (Source files, Test files, Test data, Index) agree with the tracked tree both ways, the Doc links resolve, and the Suite column agrees with the latest measurement (absent file = red) | nothing (a report on stdout, exit 0/1) |
| `hooks/pre-commit` | check | the R-210 checkin gate: the format guard on the staged notes files + the overview auditor; red = no commit; installed via `git config core.hooksPath wsutils/hooks` (one local line per clone) | nothing (read-only) |
| `notes_lint.py` | check | the notes format guard (R-200): the grammatical checks of every notes format, one linter per format — the decisions log, the register, the journals, the overview, the domain rule files, the ideas entries, plus WIDTH, EOF, CANON (idempotence under the re-wrapper) | nothing (read-only: a report on stdout, exit 0/1) |
