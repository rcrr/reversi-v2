# Decisions log — historical record

Format rules: notes/decisions\_rules.md (rigid — follow when appending to this file).

D-628 | 2026-11-15 | notes/overview.md — the two editorial removals (the user's call): (1) the "Current state" entry
         "The USO (FEATURE-SET) campaign stands at ec20 …" — it is not a realization milestone in itself (using the
         software one develops is self-evident), and its substance is fully documented in the LaTeX book named by the
         entry just above it; (2) the "Next steps" entry "The FEATURE-SET campaign (the scope): …" — with it the
         campaign list opens at MULTI-PLY. "Current state" keeps its three entries (the 19-level pipeline, the LM
         facade, the LaTeX book); "Next steps" keeps six (MULTI-PLY, MOVE-PROB, ENDGAME-SOLVER, REGAB, TEST-BATCH, the
         LaTeX book improvements).

D-629 | 2026-11-15 | The two volume rotations at the session boundary (the user's end-of-session housekeeping): (1) the
         journal — notes/log.md volume 005 had 26 sessions (102–127, 728 lines), past its 25-session cap: it closes as
         notes/hist\_log/log\_005.md (the H1 range final 102–127) and the new notes/log.md opens volume 006 at session
         128; (2) the decisions log — notes/decisions.md had 2811 lines (D-426…D-627), past its 1000-line cap: it closes
         as notes/hist\_decisions/decisions\_007.md and the new notes/decisions.md opens at D-628. The overview Index is
         updated for the three files.

D-630 | 2026-11-15 | Record-integrity disclosure (the capillary rules-compliance audit, zone A): two D-numbers are cited
         in the journals, the D-629 rotation entry and the overview Index, yet exist in no decisions volume. (1) D-627
         (the session-127 close) was recorded in the journal (hist\_log/log\_005.md:728) and the commit message
         (2268ac7) but was never appended to the decisions log: the closed volume 007 in fact ends at D-626 (line 2794)
         — so the D-629 entry's "D-426…D-627" range and the Index range overstate the volume by one; the Index is
         corrected forward to "D-426…D-626" in this same commit (the open file is repaired forward, iron rule 3; the
         closed volume stays append-frozen). (2) D-463 is cited by hist\_log/log\_004.md:2194 ("il refuso del marker #:
         … in cache\_manager (D-463)") but has no entry in volume 007 (the entries run …D-462, D-464…). Both gaps are
         DISCLOSED, not back-filled: the numbers stand lost, as D-152 is documented as a legal lost number
         (hist\_decisions/decisions\_006.md:622).

D-631 | 2026-11-15 | R-520 rewrap (the rules-compliance fix campaign, the user's item 2): the 21 physical lines over the
         120-char hard ceiling, in 8 files, are split back under the ceiling with zero semantic change:
         src/reversi/pattern.py (14 lines — the 12 PatternType table literals each split over two lines, plus the two
         long expressions at L379/L700), src/reversi/lm/hlp\_config\_schemas.py (the `side` Field description split),
         src/reversi/lm/wrk\_optimize.py (the log\_event f-string split), src/reversi/lm/hlp\_zed.py (the
         hlp\_zed\_fun\_factory return annotation split over lines), src/reversi/lm/model\_weights.py (the raise split),
         src/reversi/lm/wrk\_vld\_positions.py (the log\_event split), probes/verify\_wmaps.py (the quoted check string
         split — the string content is unchanged), run\_utests.sh (the banner echo split into two arguments — the
         printed output is unchanged). Verified: 0 lines over 120 in the tracked .py/.sh set, test\_pattern 76/0/0,
         verify\_wmaps all checks pass.

D-632 | 2026-11-15 | R-550 reword (the rules-compliance fix campaign, the user's item 2): the 8 I-XXX references in
         PROBE COMMENTS (R-550 bans I-XXX in any docstring or comment of the probe Python code; R-580 sanctions them in
         check labels only, per the house interpretation recorded in decisions\_007) are reworded to name the change in
         words, the check labels untouched: probes/verify\_gradient.py:294 ("the I-017 reordering" → "the level
         reordering"), probes/verify\_validate.py:218 (same), probes/verify\_wrk\_features.py:41 ("I-012 realized,
         the I-017 T1" → "the backlogged item realized, the reordering T1"), probes/verify\_logistic\_model.py:84/93
         (the two dated banner lines) and :232 (the bare "I-019:" dropped), probes/verify\_save.py:209 ("I-013:"
         dropped), probes/verify\_su\_analysis.py:32 ("the I-017 step 3" → "the reordering step 3", the D-258 citation
         kept). Verified: 0 I-XXX in probe comment lines, the 6 probes compile. Observation (pre-existing, not touched):
         verify\_gradient.py carries 3 stale structural pins (C1 line count 184 vs the current 225, C5 class/test
         counts) — a re-pin candidate for the next probe-maintenance pass.
