# Decisions log — historical record

Format: D-NNN | date | decision | rationale

This is the append-only HISTORICAL LOG: the "why" of every action and commit in this workspace. It grows without bound
and is consulted only when needed or for historical research. The rules in force right now live in notes/rules.md (the
active legislation): when a decision establishes an enduring rule, the rule is promoted there with this D-number as the
origin pointer (same commit); a retirement removes the line from rules.md and is logged here with a new D-number.
D-numbers are sequential and never reused or renumbered (the docs' State lines and the cross-references depend on them).
Volumes (D-118, the cap amended at D-333): the open log keeps this name (notes/decisions.md); when it exceeds 1000 lines
it closes at a session boundary as notes/decisions_NNN.md and a new open log is opened — the D-numbers stay global
across volumes (volume 000: D-001…D-116, closed 2026-09-06; volume 001: D-117…D-158, closed 2026-09-11; volumes
002-005: D-159…D-332, closed 2026-09-29 at the D-333 rotation).

D-333 | 2026-09-29 | the decisions.md REPAIR + the split into 4 closed volumes + the 1000-line cap (Roberto: "Da D-237
         la formattazione si ROMPE. Avendo allargato i caratteri per riga dire di emendare la regola a 1000 righe.
         Spezza il file in 4: notes/decisions_002.md ... notes/decisions_005.md, sistema la formattazione con gli escape
         appropriati, e partiamo con un nuovo file decisions vuoto"). (1) THE DAMAGE (pre-existing, committed in the
         original sessions — git -S: the 11-space gaps first appear in the D-304 commit itself): (a) 36 internal
         11-space runs in D-304/D-305/D-306 — a newline + 10-space indent collapsed by a bad join (the content was
         INTACT); (b) the D-307 header glued onto the D-306 last line (a mid-line entry start); (c) 55 missing blank
         separators (D-263..D-327); (d) the inconsistent continuation indents (6 / 10 / 11 spaces vs the 9 house
         continuation — the D-184/D-186/D-204 stragglers, the D-263..D-283 zone, the D-284..D-332 zone); (e) 16
         mid-token line breaks (the D-209 rejoin rule: 5 underscore — rlmwf_materializers, principal_index_count,
         save_optimization_checkpoint, is_optimization_cache_consistent, test_wrk_optimize — 5 hyphen —
         threshold-independent, hand-computed, "su-corpus-3", per-position, stale-boxplot-label — 4 slash —
         min_grad/min_p_fun_decrease, POSITIONS/ANALYTICS/VALIDATE, T9/T6/T4-rate, D-184/D-186 — 2 filename dots —
         hlp_final_log_print.py, wrk_optimize.py); (f) 7 first lines over 120. (2) THE REPAIR: one uniform re-wrap of
         all 174 entries (D-159..D-332) to the house format (the D-NNN | date | first line, the 9-space continuation,
         the greedy 120 fill, the code-span-aware tokens — `test_prng`.md atomic) + the 16 rejoins + the separator
         restoration + the asterisk escapes (the rules.md house rule: math multiplications + globs, 15 new — 0
         stray-italic candidates left). CONTENT-PRESERVATION PROOF: the whitespace- and backslash-stripped text of every
         entry is identical before / after. (3) THE AMENDMENT: the volume cap 2000 -> 1000 lines (the ~120 wrap made the
         old cap a 4460-line run) — rules.md + this header carry the new cap. (4) THE SPLIT: the repaired open log (3484
         lines) into 4 closed volumes — decisions_002 (D-159…D-206, 884 lines), decisions_003 (D-207…D-257, 865),
         decisions_004 (D-258…D-300, 879), decisions_005 (D-301…D-332, 870), each under 1000 — and this file restarts
         empty, D-333 as its first entry. OBSERVATION (for Roberto, no action): the closed volumes 000/001 carry 53/99
         stray `|` continuation lines + 27/52 bare `*` (the pre-D-237 table-format and math-escape remnants the D-237
         re-wrap kept as content) — the closed volumes stay verbatim; a cleanup pass is his call.
