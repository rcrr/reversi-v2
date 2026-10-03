# probe_rules.md — rules for the verification apparatus (probes)

Prescriptive. Follow when creating, migrating, re-pinning, or retiring any probe. Language: English.

Companions: notes/docs\_rules.md (the mirror docs a probe's "pinned by" feeds), notes/log\_rules.md (the journal that
records each sweep).

## 1. What a probe IS (and is not)

A probe is the CAMPAIGN-LEVEL verification apparatus: it re-derives facts INDEPENDENTLY of the test files (different
code path, different precision, hand-computed cases, cross-file state) and checks them against the workspace. It exists
because tests can be tautological — a golden imported from observed behavior passes even when code and test share the
same misunderstanding.

A probe is NOT:
- a second copy of a test (see §4, the test/probe line)
- a permanent home for investigation one-offs (see §6)
- part of the shipped package: probes live in probes/ at the workspace root — src/ is the reversi package only

## 2. Location and tracking

- probes/ (workspace root) — tracked in git, one file per module: verify\_<module>.py. The hub probe
  verify\_logistic\_model.py additionally owns the pipeline-wide state (see §5).
- scratch/ — gitignored DISCARD AREA for temporary session code. Nothing permanent ever lives there: a check that proves
  worth keeping graduates to probes/ (or to a test), a MAINTENANCE tool to wsutils/, a finished investigation moves to
  notes/analyses/. A probe or a tool found in scratch/ is a defect.
- probe artifacts go under build/tmp and are removed afterwards, like test artifacts.
- The MEASUREMENT tools in wsutils/ are outside the campaign sweep of §5.2 — the sweep is the verify\_\* probes. Their
  artifacts go under build/tmp, removed afterwards.

## 3. Classification of every probe check (a / b / c)

Every check in every probe is one of:

- **a — independent invariant**: the fact is verified by a method independent of the tests (hand-computed math,
  alternative formula, cross-file re-derivation) and is NOT already asserted by a test through the same path. KEEP — the
  epistemic core.
- **b — obsolete**: the check asserts a fact that is no longer true. Two sub-cases:
  - b1 — the fact legitimately EVOLVED (a pipeline count, a renamed API): RE-PIN — but if the fact is a pipeline-wide
    one, re-pin it ONCE in the hub (§5), not in N copies.
  - b2 — the fact no longer matters (investigation purpose served): RETIRE to notes/analyses/ (§6). Never "fix to green"
    what should be archived.
- **c — overlap**: the check asserts the same fact, through the same path, that a test already pins. DELETE. THE TRAP:
  overlap is not redundancy. Same target, INDEPENDENT method = category a, not c. The operational test: would this check
  still have value if the test it duplicates were wrong together with the code? If yes → a. If no → c.

## 4. The test / probe line (which checks convert to tests)

A check becomes a TEST when it is: (i) a behavior of ONE module, (ii) deterministic input → output, (iii) cheap enough
to run on every suite run (the no-DB tier, or DB-gated per the house convention). Everything else stays a PROBE:

| becomes a test | stays a probe |
|---|---|
| hand-computed unit math | source-TEXT inspections ("0 commented imports", "the factory has @validate\_call") — tests verify behavior, not text |
| fail-fast guards a probe discovered (exception type + message) | heavy end-to-end re-derivations (live DB + full pipeline) — campaigns, not module contracts |
| | the pipeline-wide state (hub only, §5) |
| | investigation evidence (archived, §6) |

Conversion is done one file at a time, each with its own commit that keeps the suite green (see §5, the sweep).

## 5. Maintenance (the sweep rule)

1. A probe is maintained whenever a change would compromise it: the same-commit rule of docs\_rules.md applies (code +
   doc + probe in one commit).
2. Every CAMPAIGN, before the notes commit: a FULL sweep — the whole test suite (gated + live) AND every probe in
   probes/ (gated + live). A campaign commit on a red sweep is a defect. The sweep result (n probes, all green / the
   exceptions) goes into the session journal entry.
3. Pipeline-wide state (active-level count, commented imports, worker-list shape) is pinned by the HUB probe
   verify\_logistic\_model.py ONLY. Module probes pin their own module's structure and behavior, never the pipeline's.
4. Re-pinning a golden or a count changes the probe AND every doc bullet that cites it, in the same commit.

## 6. Retiring and archiving

- Finished investigation one-offs: move to notes/analyses/ with a header
  `# ARCHIVED — <what it investigated>, <date>, results quoted in <commit(s)>`. Archived scripts are frozen records: not
  maintained, not run in the sweep, citable as evidence.
- A retired probe is deleted from probes/ in the same commit that records its retirement in the journal (b2) — or
  converted per §4. A probe is never left in scratch/ to die.
