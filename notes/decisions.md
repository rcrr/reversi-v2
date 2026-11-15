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
