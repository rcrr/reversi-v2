# tools.md — rules for the workspace tools (tools/)

Prescriptive. Follow when creating, migrating, retiring or using any tool in tools/. Language: English. Rigid, like the
companion rule files.

Companions: notes/probe_rules.md (the verification apparatus — what a tool is NOT), notes/docs_rules.md (the mirror
format the doc auditor checks), notes/rules.md (the register that points here).

## 1. What a tool IS (and is not)

A tool is a WORKSPACE UTILITY: it serves the maintenance of this repository — the notes and the docs format, the suite
measurement, the audits no test can express. It lives in tools/ at the workspace root (D-248), tracked in git.

A tool is NOT:

- part of the shipped package: src/reversi/tools/ (D-133) is the LIBRARY's subpackage (binio, prng, cache_manager,
  opt_lbfgs, state_machine) — a development utility never lands there;
- a probe: probes/ is the CAMPAIGN-LEVEL verification apparatus, with the a/b/c checks and the sweep (probe_rules §1,
  §5). A tool makes no campaign check and is NOT in the sweep. A tool MAY check something (the doc auditor does): the
  difference is the SCOPE and the LIFE — a probe pins a module's facts and dies with its campaign, a tool serves the
  workspace and lives as long as the workspace does;
- a test: nothing in tools/ is discovered or run by run_utests.sh;
- a home for a one-off: a finished investigation moves to notes/analyses/ (probe_rules §6), a throwaway dies in
  scratch/.

## 2. The four requirements

Every tool in tools/ satisfies all four. A tool that fails one is not a tool yet — it is still a scratch experiment.

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
  when the content would change beyond what it declares (the D-237 wrapper: the token-level fingerprint, the
  idempotence, the fixpoint — a bug cannot silently lose content);
- it touches ONLY the paths it was given, inside the workspace: no recursion into unrelated trees, no absolute path
  outside, no symlink followed out;
- the ARTIFACTS go under build/tmp (the D-065 base), never in the tracked tree (probe_rules §2);
- it never runs a git WRITE command (no commit, no checkout, no reset, no stash): the repository state is Roberto's;
- it never DELETES: the only deletions allowed are the tool's own artifacts under build/tmp;
- the docstring states the exact scope of what it writes.

## 3. The header (fixed)

The module docstring carries, in this order:

1. **WHAT IT IS** — the category (a check / a measurement / a maintenance tool) + the one-line purpose;
2. **USAGE** — the command line, from the workspace root, with `.venv/bin/python tools/<name>.py`;
3. **SAFETY** — what it writes, and under which flag (or "writes nothing");
4. **ORIGIN** — the D-number of the campaign that produced it and of the promotion to tools/.

## 4. Naming

- `snake_case`, a noun describing WHAT IT DOES: `notes_format.py`, `docs_format_audit.py`, `suite_audit.py`.
- A checker may carry the `_audit` / `_check` suffix; the `verify_` prefix is RESERVED to the probes (probe_rules §2).
- No dependency beyond the venv: a new one is a decision, not a tool's private choice.

## 5. Lifecycle

1. **BIRTH** — in scratch/ (gitignored; probe_rules §2).
2. **GRADUATION** — when it proves generally useful: ONE commit carrying the tool (with the header of §3), its inventory
   row here, the rules line when it opens a new category, and the D-number in notes/decisions.md + the journal entry.
3. **MAINTENANCE** — a tool follows what it serves: a format change, a path change or a new fixture updates the tool in
   the SAME commit (the docs_rules §5.1 same-commit spirit). A tool that checks something is run when its target
   changes.
4. **RETIREMENT** — delete the file, remove the row here, log the retirement with a new D-number. A tool is never left
   in scratch/ to die.

## 6. Inventory

One row per tracked tool. Updated in the same commit as the tool it describes.

| tool | category | what it does | what it writes | origin |
|---|---|---|---|---|
| `notes_format.py` | maintenance | the house re-wrapper: the D-237 block grammar (~120 chars, code-span aware, the mid-token rejoins, the span healing) + the per-file verification (the content fingerprint, the idempotence, the fixpoint) | the files passed on the command line, ONLY with `--write`; nothing by default | D-237/D-238, promoted at D-248 |
| `docs_format_audit.py` | check | audits every docs/**/*.md against notes/docs_rules.md: the H1 ↔ the source path, the sections and their order, the §4 forbidden patterns, the size budget, the width, the split code spans, the ragged tables | nothing (a report on stdout) | D-239, promoted at D-248 |
| `measure_suite.py` | measurement | the per-test TIMING instrument (D-132): every test's duration in milliseconds + the per-module aggregate + the skip census, the baseline of the D-130 tiering | `build/tmp/test_durations.txt` | D-132, moved to tools/ at D-250 |
| `suite_audit.py` | measurement | runs every test module of run_utests.sh on its own (LONG=1, the live DB) and prints `<module> <ran>/<fail>/<skip>` — the numbers the overview's Suite cells must carry | `build/tmp/suite_audit.txt` | D-243, promoted at D-248 |
