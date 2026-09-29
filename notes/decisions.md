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

D-334 | 2026-09-29 | the overview.md RESTRUCTURE (Roberto: "La sezione Where we are cresce continuamente e non ha un
         senso: è un'altra storia del progetto. Non dobbiamo disseminare la storia ovunque, dobbiamo solo tenere quanto
         è utile a gestire il progetto" + the 4 calls: rename "Current state", the e2e bullet out, the table
         re-gymnastic now, the MAX 10 bullet rule). (1) THE FINDINGS: the section grew 18 -> 431 lines (09-15), was
         condensed back to 18 at D-235/D-236 (09-19) — the same disease cured once WITHOUT a legislative guard — and
         re-bloated to 172 lines / 35 bullets in 10 days; the bullet audit: 22 campaign-history (incl. the 9 "format
         rules land on X" D-323..D-331 + the hlp_anova cluster D-309..D-317 + the 2 docstring removals), 9 table/mirror
         duplicates, 4 genuine state, 2+ stale (the su-corpus-2 / su-corpus-3 / su-corpus-5 contradiction, the
         965-vs-968 suite counts); the Next-steps backlog line carried the closed-ideas record (the "OPEN items only"
         rule violation); 11 table State cells carried "(the D-NNN format pass: ...)" campaign clauses (the D-117
         grammar violation) + the board.py src-row suite 246/0/15 stale vs the measured 247/0/15. (2) THE LEGISLATION
         (rules.md): the section RENAMED "Where we are" -> "Current state" (the eight-section order unchanged); new
         definition — CURRENT STATE only, MAX 10 bullets, each a present fact NOT in the tables and NOT in the mirrors
         (the pipeline-wide state, the in-flight campaigns with their horizon, the cross-file contracts); NO
         bullet-per-campaign: the campaign lives in the journal + the decisions log, and its state leaves the section
         when the campaign ends; the D-pointer names a rule in force, never a campaign provenance. (3) THE REWRITE:
         Where we are 172 lines / 35 bullets -> Current state 4 bullets (the 19-level pipeline live and green; the D-318
         docstring rule + the user-directed retroactive conversion; the LM facade script entry + the target-driven stop;
         the ec consolidation in ONE required root field — the e2e real-pipeline bullet DROPPED per Roberto); the
         Next-steps closed-ideas record out (it lives in ideas-closed.md); the 11-cell table re-gymnastic (hlp_plot,
         wrk_optimize, client, hlp_config_schemas, hlp_gradient, hlp_indexes, hlp_optimize, hlp_su_analysis,
         hlp_validate, hlp_wmaps + the test_hlp_su_analysis row) keeping the contract facts (the 13 PlotStyle knobs, the
         hi_perf_blocks field, the su-corpus lineage); the 2 stale su-corpus versions corrected (the random_game row
         su-corpus-3 -> 5, the test-row pin su-corpus-4 -> 5 — verified in the code: _GENERATOR_VERSION = "su-corpus-5",
         the test pins it); the board.py suite fixed 246 -> 247 (measured: Ran 247, skipped 15). The deeper narrative
         clauses of the hlp_su_analysis State cell (the D-295..D-305 framing) stay — the approved scope was the format
         clauses; a full condensation is a separate call. Nothing is LOST: every stripped clause exists verbatim in the
         decision log (D-306..D-331) and the mirrors — only de-duplicated. (4) VERIFICATION: notes_format --check clean
         (0 pending rejoins), the source-vs-test suite cross-check 0 mismatches, Current state 4 bullets <= 10. NOTE:
         rules.md grew ~2 lines past its ~150 budget (pre-existing overage) — the consolidation call is Roberto's.
