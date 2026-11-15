# Session journal — volume 006 (sessions 128–...)

Format rules: notes/log_rules.md (rigid — follow when editing this file).

## 2026-11-15 — session 128 (housekeeping — the overview trim + the journal / decisions volume rotation)

- notes/overview.md — the two editorial removals per the user: the "Current state" entry "The USO (FEATURE-SET)
  campaign stands at ec20 …" (not a realization milestone in itself — its substance is 100% documented in the LaTeX
  book named by the entry just above it) and the "Next steps" entry "The FEATURE-SET campaign (the scope): …" — the
  campaign list now opens at MULTI-PLY. (D-628)
- notes/log.md + notes/decisions.md — the two volume rotations at the session boundary (the user's end-of-session
  housekeeping): the journal volume 005 (sessions 102–127, 26 sessions > the 25-session cap, 728 lines) closed as
  notes/hist\_log/log\_005.md with the H1 range final 102–127, the new volume 006 opening at session 128; the
  decisions log (D-426…D-627, 2811 lines > the 1000-line cap) closed as notes/hist\_decisions/decisions\_007.md, the
  new log opening at D-628. (D-629)
- notes/overview.md — the Index updated for the three rotated files (decisions\_007, log\_005, log.md at volume 006).
- notes/decisions.md + notes/overview.md — the record-integrity disclosure (the rules-compliance audit, zone A):
  D-627 and D-463 are cited in the journals, the D-629 entry and the Index, yet exist in no decisions volume (D-627
  was never written to the log at the session-127 close); the gaps are disclosed, the Index range corrected forward
  to D-426…D-626, the frozen volume untouched. The audit file joins the Index. (D-630)
- src/reversi/pattern.py + the 5 lm modules + probes/verify\_wmaps.py + run\_utests.sh — the R-520 rewrap: the 21
  lines over the 120-char ceiling split back under it, no semantic change (0 lines over 120 in the tracked
  sources; test\_pattern + verify\_wmaps green). (D-631)
- the 7 probe files — the R-550 reword: the 8 I-XXX references in probe COMMENTS now name the change in words
  ("the level reordering", "the backlogged item realized" …), the R-580-allowed check labels untouched; 0 I-XXX in
  probe comment lines. (D-632)
- notes/rules.md (R-330) + notes/docs\_rules.md §7 + notes/overview.md — the `__init__.py` mirror-doc exception
  legislated (the user's choice (b)): the 6 package `__init__.py` files are exempt from the one-file-one-doc rule,
  declared conformant; the overview's 1:1 claim is now true again. (D-633)
- docs/test/reversi/test\_index.md — rewritten to the test-doc skeleton (the auditor's 4 sections) and un-staled:
  4 classes / 10 tests, not the 2 / 5 the old doc claimed. (D-634)
- docs/ — the batch rewrap: all 38 docs with a format finding rewrapped to the house form (the 58 over-120 lines,
  the 3 split code spans healed), the 3 ragged Coverage tables repaired (escaped pipes), wrk\_vld\_positions.md
  back under 120; the docs audit now reports ZERO non-size findings (the 9 size-budget items disclosed, not
  padded). (D-635)
- wsutils/notes\_lint.py + notes/log\_rules.md — the R-200 historical exception: the LISTMARK guard (born D-484,
  after the D-368 cleaning) no longer reaches into the frozen hist\_\* corpus — the 26 documented residue markers in
  closed journal volumes 000–003 stand; the check stays fully active on the open files. (D-638)
- notes/hist\_log/log\_000.md + log\_003.md + log\_004.md — the three H1 factual corrections (the one class the
  archive freeze allows): "1–24"→"1–23", "38–89"→"38–78", "90–101"→"90–101, 98 missing" — the 13 phantom session
  numbers resolved, no session content touched (logged as D-639: the D-636/D-637 numbers stand skipped by the
  mid-campaign renumber). (D-639)
- notes/decisions.md — the R-130/R-100 disclosure + forward ruling: the post-rule DSH/vLLM/DeepSeek infra notes
  and the Italian journal prose in the closed volumes are disclosed (with the file:line inventory); going forward
  the prose is English (verbatim user quotes exempt) and the publication edit pass is the sole sanctioned strip of
  the infra notes; the credential detail in log\_000 is noted as publication-sensitive. The frozen corpus is
  untouched. (D-640)
- the 7 test modules — the R-750/R-760 anchoring: every TemporaryDirectory / mkdtemp now under the shared
  CUSTOM\_TMP\_BASE (6 modules out of the system /tmp; test\_state\_machine drops its self-derived TMP\_DIR for the
  same anchor); 136 tests, 0 failures. (D-641)
- notes/rules.md — the R-060 re-sync: the domain rule-file list now names wsutils.md (not the non-existent
  tools.md) and adds latex\_rules.md + design\_principles.md; the reported missing L62 blank line re-verified as a
  false positive (it is present at HEAD). (D-642)
- The rules-compliance fix campaign CLOSES here (D-630…D-642, 11 items, the user's item-by-item approvals): 40
  violation-class findings from the audit are fixed or legislated; what stands open by decision: the 9 docs
  size-budget items (disclosed, not padded), the 19 over-long test docstrings (R-570, minor), the R-560 backlog
  reflow (8 files), the 24 W291 banner lines, the .gitignore R-300 amendment and the R-310 mirror clause (the
  user's open question), the 3 stale verify\_gradient pins, and the zone-F probe naming / headers / DP-010 (the
  user asked for a fuller explanation first).
