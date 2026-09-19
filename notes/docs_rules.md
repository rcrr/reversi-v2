# docs_rules.md — format rules for the mirror docs (docs/)

Prescriptive. Follow when creating, updating, or migrating any doc under docs/ that mirrors a source file (the D-007
mirror rule, AGENTS.md standing rule 5). Language: English. The prose is wrapped to ~120 chars/line (D-238); the tables
stay one physical line per row.

Companions: notes/probe_rules.md (the verification apparatus), notes/log_rules.md (the session journal).

## 1. What a mirror doc IS (and is not)

A mirror doc is a SNAPSHOT of the current state of its module: what it does NOW, consistent with the code. It is
rewritten to state; it is never appended to.

The history of how the module got here lives elsewhere, each in its canonical home:

- what/when a change happened (granular): git log
- session narrative: the journal (notes/log_NNN.md)
- why a decision was taken: decisions.md (D-NNN)
- parked ideas: ideas.md

A mirror doc that carries history is a defect (bloat + drift + internal contradiction). A mirror doc that contradicts
its own appendix (the board.md session-1 case: R1 "RESOLVED" in the body, "the most important flaw" in the verbatim
appendix) is the failure mode these rules exist to prevent.

## 2. Header (fixed, 4 lines)

```
# reversi/<module>.py
<What it is: 2-4 sentences, present tense, no history.> > State: D-NNN · <short-hash> · YYYY-MM-DD · suite <n>/<f>/<s>
[gated: <n>/<f>/<s>]
```

The `> State:` line is the ONLY time permitted in the file: no "Analysis date", no "brought in by Roberto (commit …)",
no "post D-xxx". The suite cell is the MODULE'S OWN suite (or its gated form), never the global discover. The cells mark
the snapshot: D-NNN = the last decision that changed the module; `<short-hash>` = the last commit touching the module's
source; `YYYY-MM-DD` = that commit's date (established at the board.md migration, D-109).

## 3. Sections (fixed order; only the appendix is optional)

1. **API** — every `__all__` name: signature + one contract line (pre/post-conditions, dtypes, error types). Data
   modules: a field table (name, type, meaning, constraint) instead.
2. **Architecture** — internal structure, data flow, and design choices AS THEY ARE NOW. A design choice with a
   rationale gets one sentence + a D-NNN pointer ("the ridge gate is in the consistency fn — D-096 R1"). Never "it was
   X, now it is Y".
3. **Verified invariants** — one property per bullet, each pinned to WHAT pins it: a test or a probe ("pinned by
   `test_board::test_…`" / "`probes/verify_…`"). Never "checked by hand, 2026-08-25". An invariant without a pin is an
   Open issue, not a Verified invariant.
4. **Open issues** — OPEN R/M/T items only, with their pointers. If none: one line, `None.` Closed items never appear.
5. **Conventions** — the module-specific bullets to respect in new work on this file.
6. **Integration** — consumers/producers: the ctx fields read and written, the adjacent pipeline levels, the modules
   whose names are reused.
7. **Appendix — line reference** (OPTIONAL, default OFF) — only for the most intricate files; every line number in it is
   updated in the same commit as the code change. Default: no line numbers in the doc.

## 4. Forbidden in a mirror doc

- provenance narrative ("brought in by…", "session N", "analysis date", "fix campaign … CLOSED")
- campaign tags inside architecture prose ("(D-103 T2: the dead import removed)")
- FIXED / RESOLVED lists, "pre/post D-xxx" contrasts, line-count deltas ("453 → 522 lines")
- verbatim appendices of original analyses: they move losslessly to notes/analyses/ (one file per artifact, original
  language kept), with a pointer recorded in the journal
- the GLOBAL suite status: it lives exactly once, in notes/overview.md → Environment
- report tenses ("Status: analyzed in depth, untouched") — the doc describes a present, it does not report a past

## 5. Lifecycle (how a mirror doc stays true)

1. The doc is part of the module: every commit that changes X.py updates X.md in the SAME commit (code + doc + probe
   together — see probe_rules.md §5).
2. The State line is updated in that same commit; the doc body is rewritten to the new state, never appended.
3. When an issue is closed: its line leaves the doc in the closing commit. The closure narrative belongs to journal /
   commit message / decisions.md.
4. Every "pinned by" must point at a tracked, currently-passing test or probe. A pointer into the void (untracked,
   deleted, or stale) is a defect in the same commit.
5. Target size: 60-120 lines; the hubs (board, pattern, logistic_model, state_machine) 150-200. A doc that cannot state
   its module in that budget is hiding history or is a hub.

## 6. Test-doc variant (docs/src/reversi/test/test_X.md)

Same skeleton, two substitutions:

- section 1 = **Coverage**: the suite's classes and what each pins — a map, not a method-by-method enumeration (the
  method list already exists in the .py file).
- section 3 = **Goldens pinned**: the pinned literals (hashes, exact values) and what each protects; the re-pin history
  of a golden (which D-NNN moved it) does NOT go here — the commit that moved it already says so.

The State line uses the test file's own suite counts.

## 7. Scope exceptions

- src/reversi/test/data/*.json are fixtures, not source: no mirror doc; their doc line is the Test files data note in
  notes/overview.md.
- notes/analyses/ holds moved-out historical artifacts (verbatim analyses, retired one-off investigations): they are
  frozen records, never updated — a changed fact gets a NEW analysis, the old one keeps its date and its errors.

## 8. Migration state (session 30 onward)

Pre-migration docs (all 70) are grandfathered: they stay as-is until their file's migration commit. The migration
itself: lossless extraction of the historical material (to the journal / notes/analyses/), rewrite to this schema, one
commit per file or per pipeline batch, board.md first (schema validation), then pattern.md, then the C-class hubs, then
B batches, then A. After the last file, this section is deleted.
