# Decisions log — historical record

Format rules: notes/decisions\_rules.md (rigid — follow when appending to this file).

D-426 | 2026-10-04 | tools/prng.py — the R-520 reflow of the docstrings (the user's "reflow with the line width per the
         rules, code and docstrings"): MEASURED FIRST — R-520 is a ceiling (~120, every physical line: code, comments,
         docstrings) and prng.py was already compliant (545 lines, max physical line 99 chars, 0 lines over 120, no
         trailing ws; never a line over 120 in its git history, D-201 → D-425 — the test mirror max 86 and binio.py max
         87 check the same way). The user chose the rewrap anyway (asked, after the measurement): the docstrings move
         from the ~72 house wrap to the ~120 wrap — an EXPLICIT per-file deviation (the wider wrap stays in prng.py
         only; R-520 and the ~72 house wrap of the other format-passed files are untouched). WHAT: all 20 docstrings
         (the module doc, the class doc, the 15 class methods, the 3 module-level kernels) rewrapped greedy-120 by a
         one-shot script (scratch/reflow\_prng.py, gitignored): the prose paragraphs and the Args/Returns/Raises
         descriptions re-flowed (the short entries collapse to one line; the 2 long ones wrap at +4 continuation), the
         section structure (the headings, the blank lines, the Attributes (internal) block) and the indented API table
         of the module doc preserved verbatim. The # comments, the code and EVERY non-docstring line are byte-identical
         to HEAD (verified programmatically). ONE cosmetic hand-nudge beyond the greedy fill: the module-doc line break
         that would have left "- 1, so a single seed..." at the start of a line was moved one word so "2^19937 - 1"
         stays together. NO behavior change (docstrings only; the numba kernels recompile from identical code). 545 →
         485 lines. VERIFICATION: test\_prng 30/0/0 (the bit-exact goldens included); the suite via the wrapper
         1062/0/24 (unchanged); notes\_lint + the gate green at this checkin.

D-427 | 2026-10-04 | notes/rules.md (R-520) + tools/prng.py — the line-width rule refinement + the prng reflow redo (the
         user's three-point feedback on D-426: "120 is too much — I'd like a rule that stays in 100 as the preferred
         value and may go to 120 when necessary, i.e. no break for a single word; the same rule formats the comments
         too; and the code can be on one line — e.g. the get\_double\_in returns"). R-520 REWRITTEN (the register, the
         user's wording approved as drafted): prose (docstring + comment lines) wraps to a PREFERRED 100 — a line may
         exceed 100, up to the 120 ceiling, only to avoid leaving a single word alone on the next line (if the pull-up
         would pass 120, the break stands); code has no preferred wrap — an expression split across lines that fits on
         one line within the 120 ceiling is written on one line; the ceiling still applies to every physical line.
         APPLIED to prng.py (the redo of D-426, one campaign): (1) the 20 docstrings rewrapped 100 + pull-up (the D-426
         120 wrap undone; 7 prose/entry lines land at 101-110, every one a single-word pull-up: the module-doc "The
         state (\_mt / \_mti)..." line, the seed / np.ndarray / slots entries, the random\_choice first line, the choose
         first paragraph, the pick-from-set banner's "sets."); (2) the 6 multi-line # comment blocks reflowed to 100
         (the NN block, the init block, the two kernel banners, the scalar-return-idiom block, the clear-the-picked-bit
         block — the last collapses to one line); the license banner, the section dividers and the short inline comments
         untouched; (3) the 8 expression merges (the three get\_double\_in returns — 84/84/92, the random\_string\_az
         join — 100, the three twist lines with the backslashes out — 98/105/99, the init assignment — 105; the two
         105-ers accepted by the user as within the ceiling). TWO hand-nudges beyond the greedy fill: the module-doc
         break moved one word so a line does not start with "- 1" (D-426, kept), and the NN comment breaks one word
         earlier so no line starts with a bare "/". The reflow ran through a one-shot script (scratch/reflow\_prng.py,
         gitignored) that hit two bugs on the way (the comment-pass result was dropped by a copy; the divider test was
         fooled by the space after the #) — both fixed, and the pass verified afterwards: the docstrings and the comment
         blocks are textually identical to the D-426 state, only the line breaks moved. The other files adopt the new
         R-520 at their backlog format passes (no repo-wide reorganization by initiative). NO behavior change: the
         merges are the same expressions; test\_prng 30/0/0 (the bit-exact goldens included). VERIFICATION: the suite
         via the wrapper 1062/0/24 (unchanged); notes\_lint + the gate green at this checkin.

D-428 | 2026-10-04 | wsutils/src\_reflow.py — the promotion of the session-96 one-shot (scratch/reflow\_prng.py, the
         prng.py reflow of D-426/D-427) to a workspace tool. The user asked whether the one-shot could be promoted to a
         well-done wsutil for the other files; the calibration (382 docstrings — 138 with the Google sections, 146 with
         indented lines — and 192 multi-line comment blocks across the 51 source files) made the class of work concrete.
         WHAT IT IS: the R-520 source-prose re-wrapper for the .py sources, the source sibling of notes\_format.py (that
         one does the notes/docs Markdown, this one the source prose): the docstring lines and the multi-line # comment
         blocks re-wrapped to the preferred 100 / the 120 ceiling / the single-word pull-up (the R-520 rewrite
         of D-427); the Google section structure, the typed entries, the indented fixed lines, the double-space
         paragraphs (the ASCII board diagrams), the license banner and the dividers are preserved; the CODE IS TOUCHED
         NOT AT ALL — the expression merges of R-520's code clause stay the manual format-pass sub-work, with the
         per-file tests (the user approved the prose-only scope and the name). THE API: the default is a CHECK (is the
         file the greedy fill's fixed point — a report on stdout); --write runs the reflow with the pre-write
         verification (the per-docstring/per-block logical identity, the parse of the result, the idempotence — the
         second pass a no-op) and REFUSES the file, the original untouched, when a verification fails. FOUR BUGS the
         workspace sweep found and killed (the one-shot was proven on prng.py only): the stale span coordinates (the
         docstring spans addressed the pre-pass file while the live list shifted as the runs were re-wrapped — the runs
         after the first modified run mis-grouped; fixed with the original line numbers traveling with the lines), the
         empty # separator lines consumed by the comment reflow (the paragraphs merged into one; now preserved verbatim
         and used as the segment boundary), the base-indented double-space paragraphs (the ASCII board diagrams of
         board.py) re-wrapped as prose (now preserved), and the absolute ceiling check refusing 12 files that carried
         PRE-EXISTING over-ceiling lines (the long constants, the protected fixed lines; now a DELTA check — the reflow
         must not ADD over-ceiling lines, it need not fix them: the format pass's manual sub-work). VERIFICATION: the
         workspace sweep — zero refusal/failure on all 51 source files (31 would reflow under the old wraps, 7 already
         the fixed point, the rest would reflow); the board.py round-trip (1802 -> 1711 lines, the 294 board tests
         green, the fixed point after the write; the file restored — its reflow is a backlog format-pass campaign); the
         tool self-canonical (it reflows its own header and is then the fixed point); prng.py's check reports exactly
         the D-427 hand-nudge (the NN comment — the 4-line approved version vs the 3-line pure greedy) and nothing else:
         the expected documented deviation (a file carrying hand-polished breaks is not the greedy fill's fixed point;
         the SAFETY section of the tool's docstring says: do not blindly --write such a file). The inventory row in
         wsutils.md is this commit (the same-commit rule of wsutils.md §5.2).

D-429 | 2026-10-04 | tools/opt\_lbfgs.py — the code fixes (the first D of the four-part opt\_lbfgs campaign, D-429…D-432
         — source + test + mirror docs audited against rules/docs\_rules.md at the user's request, the analysis view
         delivered, the plan approved). (1) The DEAD `debug_plot` public parameter REMOVED from the `lbfgs` signature
         (accepted but never used — never forwarded to the line search; the worker never passes it, the probe E5 does
         not check it; the private line-search functions keep their own — the user approved the removal over the
         wiring); the quadratic test's `debug_plot=False` call dropped in the same commit. (2) The empty-loop boundary
         GUARDED: `max_iters < 1` or `initial_iter >= max_iters` raised an UnboundLocalError at `'iters': k + 1` (proved
         empirically before the fix) — now a documented `ValueError` (the docstring documents it in D-431, the pin lands
         in D-430). (3) The unused `from __future__ import annotations` removed (every annotation resolves with the
         module-level imports). (4) The 133-char `save_fn` annotation line — the only line over the 120 ceiling in
         either file (R-520) — split over two signature lines. (5) 35 trailing-whitespace lines stripped (4 of them in
         the license banner). (6) The 13-line `# (D-146)` comment compressed to a 4-line WHY summary (R-540: no D
         reference in a plain `#` comment, the benchmark history — 23.2→16.9 ms, the unadopted numba variant — lives in
         decisions.md; the D-146 pointer moves to the mirror doc in D-432, where docs\_rules.md §3.2 wants it). (7) PEP8
         minors: the `size=` keyword arg, the 3-4 module-level blank lines reduced to 2, the `# FG :` comment tidied. NO
         behavior change beyond the new ValueError; test\_opt\_lbfgs 14/0/0; the guard verified empirically (two invalid
         bounds → ValueError, one valid run OK).

D-430 | 2026-10-04 | test/reversi/tools/test\_opt\_lbfgs.py — the test completion + the test-doc sync (the second D of
         the opt\_lbfgs campaign). The R-850/R-860 gaps flagged in the analysis — all of them already declared in the
         test-doc's Integration "Known open gaps" — closed: (1) TestLBFGSInputValidation +2 — the new iteration-bounds
         guard of D-429 pinned: `max_iters < 1` and `initial_iter >= max_iters` raise `ValueError`; (2) a new
         TestLBFGSInfoContract (5 tests) — the `info` dict pinned exactly (the 9-key set, `info['w']` IS the returned x,
         `f` / `g_norm` agree with a fresh `fg(x)` evaluation, `iters` within (0, max\_iters], sl/yl/rho co-length); the
         history capped at m (a Rosenbrock run with m=2: 1 ≤ len(sl) ≤ 2); x0 never mutated (the x0.copy() contract,
         probe E7); the float32 end-to-end contract (an f32 x0 stays f32 in x, the sl/yl vectors and g\_norm — the
         mirror doc's Conventions bullet, unpinned until now); the `logger` hook exercised (it receives the log lines);
         (3) a new TestLBFGSStopReasons (3 tests) — the three documented `reason` strings pinned at runtime:
         CONVERGED\_MIN\_GRAD (a quadratic), MAX\_ITERS\_REACHED (Rosenbrock, 2 iters, `iters == 2`),
         CONVERGED\_LOW\_PROGRESS (a near-flat f = 1 + 1e-12·‖x‖² — the relative decrease stagnates in f64); (4)
         cleanup: the "O2b" campaign tag out of the two-loop assert message (docs\_rules.md §4 — campaign tags do not
         belong in test text), the historical comment "Updated save\_fn signature to match opt\_lbfgs.py" out, the
         random draws unified on `np.random.default_rng` (the legacy `np.random.seed` and `default_rng` were mixed in
         the same file — the Zakharov start changed, the test still converges within atol 1e-5), 21 trailing-whitespace
         lines stripped (4 in the license banner). The test-doc is rewritten in the SAME commit (docs\_rules.md §5.1): 7
         classes / 14 tests → 9 classes / 24 tests, the two new Coverage rows, the stop-reason literals + the 9-key set
         added to Goldens pinned, and the min\_grad / min\_p\_fun\_decrease gap REMOVED from the Known open gaps (the
         restart branch, the curvature skip and the Hermite internals stay integration-only, as before). 14/0/0 → 24/0/0
         (~0.050 s, the fast tier unchanged); the docs auditor green on the rewritten test-doc.

D-431 | 2026-10-04 | tools/opt\_lbfgs.py + test/reversi/tools/test\_opt\_lbfgs.py — the docstring conversion + the R-520
         reflow pass (the third D of the opt\_lbfgs campaign, the user's "ultimo step"). The 4 numpydoc-style docstrings
         (`lbfgs`, `\_two\_loop\_recursion`, `\_hermite\_cubic\_interp`, `\_hermite\_cubic\_interp\_min`) converted to
         the Google Args:/Returns:/Raises: of R-560, and FixedSizeMaxList — previously undocumented — now carries the
         class + method docstrings (incl. the `max()` RuntimeError contract). Every function docstring has the
         imperative first line (R-560(1) — the old "Strong Wolfe line search implementation with full gradient caching."
         was HOW, R-530). The biggest gap closed: `lbfgs`'s Returns now documents the 9-key info dict that was absent
         from the source docstring (the keys, the three reason literals, the iters semantics, the warm-start usage) +
         the Raises section (the 3 TypeErrors, the D-429 ValueError). Type names follow the house convention (the prng
         precedent): bare names in the entry heads, the complex subscripts in the description prose (the tool's entry
         head cannot split a nested-bracket type without threatening the 120 ceiling). THEN THE FINAL STEP:
         wsutils/src\_reflow.py --write on the source AND the test — 13 docstrings reflowed in the source (629 lines
         total with the conversion), 9 in the test; both files verified CANONICAL fixed points of the reflow afterwards.
         The tool's pre-write verifications passed (per-docstring/per-block logical identity, the parse, the
         idempotence); test\_opt\_lbfgs 24/0/0 — NO behavior change (docstrings + comment line breaks only).

D-432 | 2026-10-04 | docs/src/reversi/tools/opt\_lbfgs.md — the mirror-doc rewrite (the fourth and last D of the
         opt\_lbfgs campaign; the test-doc was rewritten in D-430, the same commit as the test change, per
         docs\_rules.md §5.1). The source doc is REWRITTEN TO STATE (docs\_rules.md §5.2 — never appended): (1) API —
         the lbfgs line is now 16 parameters (the dead debug\_plot of D-429 gone) and, per docs\_rules.md §3.1
         (pre/post-conditions, dtypes, error types), documents the error contract for the first time: the 3 TypeErrors +
         the D-429 ValueError, plus the info-dict reason literals; (2) Architecture — the performance history REMOVED
         (docs\_rules.md §4: no before/after contrasts, no campaign narrative — "~58 MB per call, 23.2 → 16.9 ms, 1.39×"
         and the numba-variant measurement belong to decisions.md); the two-loop buffer choice now states the
         one-sentence rationale (the bit-identical out= dtype semantics — the trajectory unchanged) + the D-146 pointer,
         which §3.2 wants HERE (it lived in the source comment, where R-540 restricts it); (3) Verified invariants —
         re-synced to the D-430 suite (24 tests / 9 classes), disambiguated by class name (the three same-named
         test\_a\_optimization methods — the pins now cite TestLBFGSBaseFunction / TestLBFGSRosenbrockFunction /
         TestLBFGSZakharovFunction), the "the run matches" residue gone, the new pins added (the 9-key info dict, the 3
         runtime stop reasons, the x0 non-mutation, the float32 end-to-end, the logger, the ValueError guard, the
         history cap); (4) Open issues — "None." stands (the remaining coverage gaps — the restart branch, the curvature
         skip, the Hermite + line-search internals — are tracked in the test-doc's Integration, where they were
         declared); Conventions and Integration unchanged (still true — the 16 worker kwargs re-verified line-by-line in
         the analysis). The suite re-measured through the wsutils wrapper (LONG=1): test\_opt\_lbfgs 14/0/0 → 24/0/0
         (the suite total 1062/0/24 → 1072/0/24), the overview Suite cell updated in this commit; the docs auditor green
         on both mirror docs. Campaign closed: 4 D (429 code / 430 tests / 431 docstrings + reflow / 432 docs), the
         source and the test are canonical fixed points of wsutils/src\_reflow.py, the suite GREEN.

D-433 | 2026-10-04 | notes/analyses/work\_report.md — the redo of the 18-years vs 6-weeks work report (the user's
         request: the same report of two weeks ago, measured again). No tool in wsutils/ does this (the inventory of
         notes/wsutils.md names none — the original report was generated ad hoc, its artifact in the gitignored
         scratch/); the report is re-measured from the recorded git state of both repos (git log / git ls-files + wc /
         git log --numstat). Legacy /home/rcrr/base/prj/reversi: 3150 commits, 2009-11-29 → 2026-08-05 (6093 days), 1370
         tracked files, the current tree C 342,842 / Python 30,607 / Java 28,466 lines (the 10.6M SQL data dumps
         excluded), the source churn +607,247 / −143,463. This workspace: 772 commits, 2026-08-25 → 2026-10-04 (40
         days), 271 tracked files, Python 46,774 lines (src 15,194 / test 22,610 / probes 6,900 / wsutils 2,070) +
         Markdown 24,068 (the 96 mirror docs + the 26 governance notes), the churn +208,405 / −115,290, the suite
         1072/0/24. Headline: 19.3 vs 0.52 commits/day (37x), 1,169 vs 5.0 Python lines/day (233x) — with the reading
         caveats (the different languages and roles, the governance layer the legacy repo never had, the churn inflated
         by the format-pass rewrites).

D-434 | 2026-10-04 | tools/cache\_manager.py + its mirror doc — the source fixes (the first D of the cache\_manager
         campaign): the R-540 strip — the (D-072) references removed from the module docstring and the
         `\_verify\_checksum` docstring, the D-071 from the `is\_allowed` entry, the "(R2, D-071)" tag from the step-3
         comment; the design choices keep their non-obvious summary (the warm-cache intent, the one-try step 3) without
         any reference (the user's call: the dangling D-071/D-072 pointers — pre-notes-system decisions absent from
         decisions.md and the closed volumes, yet cited repo-wide — are dropped everywhere; the repo-wide purge over the
         remaining files is the campaign's own D). The docstring pass (R-560): the missing `\_compute\_sha3\_256\_hash`
         docstring added; the 5 docstrings Google-ized (the imperative first lines, the typed Args, the `tuple:` Returns
         entry instead of the bulleted list). Format: the unused `from \_\_future\_\_ import annotations` dropped
         (Python 3.12, the PEP 604/604 annotations native — the 22 tests confirm the pydantic gate unaffected); 12
         trailing-ws stripped; the 2 over-120 lines split (the WARN/ERROR logger f-strings, the message strings
         unchanged); the triple blank lines normalized. The mirror doc REWRITTEN IN THE SAME COMMIT (docs\_rules.md
         §5.1): the "194 lines." metadata dropped, the Imports bullet (a table of contents, not architecture) dropped,
         the R1/R2/R3/M3 campaign tags (no pointers, docs\_rules.md §4) replaced by the plain rationale, the "incl. the
         R1 note" residue gone. 22/0/0 (no behavior change); the docs auditor green.

D-435 | 2026-10-04 | test/reversi/tools/test\_cache\_manager.py — the test cleanup (the second D of the cache\_manager
         campaign): the provenance narrative dropped from the TestValidateCallCoercion docstring ("probe\_rules.md §4:
         converted from the verify\_cache\_manager.py V17 probe (the coercion is unique, no other test covered it)" —
         R-540 for test comments: the behaviour description stays, the change-history does not); the unused
         `from \_\_future\_\_ import annotations` dropped (the annotations are plain names, nothing deferred); 9
         trailing-ws stripped. The test suite itself is COMPLETE (the analysis found no R-850 gap — unlike the
         opt\_lbfgs campaign): all 4 steps + success, every failure branch (the raising load, the False and raising
         validator, the raising data checksum, the missing/mismatched/malformed/undecodable sidecars), the 5 duck-typing
         cases, the validate\_call coercion, the delete idempotency, the binio sidecar format — 22 tests pinning every
         documented behaviour. The test-doc is UNCHANGED (the fix is comment-only, its content — 3 classes / 22 tests,
         the coverage, the goldens, the probe inventory — stays true). 22/0/0 (no behavior change).

D-436 | 2026-10-04 | tools/cache\_manager.py + test/reversi/tools/test\_cache\_manager.py — the R-520 reflow pass (the
         user's "ultimo step", the third D of the cache\_manager campaign): wsutils/src\_reflow.py --write on the source
         AND the test — 6 docstrings reflowed in the source (4 re-wrapped, 210 lines), 34 in the test (21 re-wrapped,
         600 lines); both files verified CANONICAL fixed points of the reflow afterwards. The tool's pre-write
         verifications passed (per-docstring/per-block logical identity, the parse, the idempotence); 22/0/0 — NO
         behavior change (docstrings + comment line breaks only).

D-437 | 2026-10-04 | the repo-wide purge of the dangling D-071/D-072 pointers (the fourth and last D of the
         cache\_manager campaign; the user's call on the campaign's analysis: drop them everywhere, not just in
         cache\_manager). The two numbers are pre-notes-system decisions — absent from decisions.md and the closed
         volumes — yet cited in 6 files outside cache\_manager (whose own references went in D-434). The purge,
         reference by reference: probes/verify\_cache\_manager.py (the header comment, the V1 and V15 tombstone comments
         — the D-106 tombstone structure kept, the D-072 clause dropped); probes/verify\_optimize.py (the H7 comment +
         the two H7 check-name goldens — "(D-071 R1 pattern)" out of the names, the warm-cache fact kept in prose);
         probes/verify\_hlp\_indexes.py (the D5 check-name golden — "the D-072 cache wiring" to "the cache wiring");
         test/reversi/lm/test\_wrk\_su\_analysis.py (the comment); docs/src/reversi/lm/hlp\_su\_analysis.md (the two
         Architecture references, the "manager's R2" tag to plain prose, the D-303 pointer kept — a different number);
         docs/src/reversi/lm/wrk\_su\_analysis.md (the sidecar reference). The H7/D5 golden names were quoted by no doc
         (verified by grep before the cut), so the probe output change is self-contained. VERIFICATION: the
         verify\_cache\_manager probe re-run (ALL PROBES PASSED, the 6 checks), the 4 touched .py files parse,
         test\_wrk\_su\_analysis 10/0/1 (skipped=1, the pre-existing one), the docs auditor green. After this D, the
         only D-071/D-072 mentions in the workspace are this decisions entry + the D-434 bullet — the history where
         R-540 says they belong.

D-438 | 2026-10-04 | tools/state\_machine.py + its mirror doc — the source fixes (the first D of the state\_machine
         campaign): the R-540 strip — all 17 D references + 7 M tags removed from the source (6 in docstrings, 11 in the
         `#` comments; the design choices keep their non-obvious summary as plain prose — the state model, the separate
         gate, the filename-prefix concatenation, the UTC-aware rendering — and the
         dangling D-060/061/068/069/070/076/078/128/321 pointers are dropped everywhere per the user's call; the
         repo-wide purge over the 23 external files is the campaign's own D, D-441). The docstring pass (R-560): the 10
         previously undocumented functions documented (Worker.\_\_init\_\_, StateMachine.\_\_init\_\_ with the
         duplicate-name Raises, \_history\_timer, \_run\_step, current\_worker\_name, show\_event\_log,
         show\_history\_of\_moves, export\_history\_of\_moves\_as\_csv, \_validate\_target\_step, \_execute\_move), the
         M-tag `#` comments converted into the docstrings, the light one-liners (log\_event, up, down) Google-ized with
         typed Args, the "This function" bodies rewritten. Format: the unused `from \_\_future\_\_ import annotations`
         dropped (3.12 — the 50 tests confirm all 7 @validate\_call surfaces unaffected); 10 trailing-ws stripped; the
         triple blank lines normalized. The mirror doc REWRITTEN IN THE SAME COMMIT (docs\_rules.md §5.1): the 4
         dangling D-321 references to plain prose (the FINAL\_LOG\_PRINT fact kept), the stale "49 tests" → 51
         (the D-439 micro-test). 50/0/0 (no behavior change); the docs auditor green.

D-439 | 2026-10-04 | test/reversi/tools/test\_state\_machine.py + its mirror doc — the test cleanup + one micro-test
         (the second D of the state\_machine campaign; the user approved the micro-test on the analysis): the provenance
         narratives dropped from the two guard-contract docstrings ("probe\_rules.md §4: pins the FULL message,
         converted from the verify\_wrk\_config.py E2/E3 probe (the re-pinned guard contract)" — R-540 for test
         comments: the behaviour description stays, the change-history does not); the two dangling D-321 references (the
         full-replay docstring + the injection-pin comment) to plain prose (the FINAL\_LOG\_PRINT fact kept); 19
         trailing-ws stripped. NEW micro-test (the approved gap): test\_csv\_export\_accepts\_str\_filename — the
         export\_history\_of\_moves\_as\_csv(filename: str | Path) union was tested only with a Path; the str branch is
         now covered (50 → 51 tests). The suite is otherwise COMPLETE (no other R-850 gap — the state model, the
         sentinel, the failure/retry/recovery semantics, the gate (bool / np.int64 / float / unknown name /
         out-of-bounds), the constructor guards, the 6×5 verbosity matrix, the context injection, the frozen-clock
         display goldens and the CSV export are all pinned). The test-doc REWRITTEN IN THE SAME COMMIT (docs\_rules.md
         §5.1): the stale "49 tests" → 51 (the TestStateMachine row 33 → 34 + the new pin), the "R2" campaign tag, the
         "V17" probe-provenance tag and the D-321 reference dropped, the runtime estimate tightened to ~0.2 s. 51/0/0.

D-440 | 2026-10-04 | tools/state\_machine.py + test/reversi/tools/test\_state\_machine.py — the R-520 reflow pass (the
         user's "ultimo step", the third D of the state\_machine campaign): wsutils/src\_reflow.py --write on the source
         AND the test — 27 docstrings reflowed in the source (18 re-wrapped, 499 lines), 63 in the test (31 re-wrapped,
         892 lines); both files verified CANONICAL fixed points of the reflow afterwards. The tool's pre-write
         verifications passed (per-docstring/per-block logical identity, the parse, the idempotence); 51/0/0 — NO
         behavior change (docstring + comment line breaks only).

D-441 | 2026-10-04 | the repo-wide purge of the nine dangling state\_machine D numbers (the fourth and last D of the
         state\_machine campaign; the user's call on the campaign's analysis: drop them everywhere, not just in
         state\_machine). The nine numbers (D-060, D-061, D-068, D-069, D-070, D-076, D-078, D-128, D-321) are
         pre-notes-system decisions — absent from decisions.md and the closed volumes (verified: 0 hits on all nine) —
         yet cited in 22 files outside the campaign. The purge, file by file (45 citations): the 3 worker sources
         (wrk\_anova, wrk\_final\_log\_print, logistic\_model — comment-only), the FINAL\_LOG\_PRINT test
         (test\_wrk\_final\_log\_print — 4 docstring/comment spots), the 6 source mirror docs (wrk\_final\_log\_print,
         hlp\_final\_log\_print, logistic\_model, hlp\_config\_schemas, wrk\_su\_analysis, wrk\_client\_check — the
         pointers to plain prose, the FINAL\_LOG\_PRINT / failure-recovery / generic-machine facts kept), the 4 test
         mirror docs (test\_wrk\_final\_log\_print, test\_lm\_worker\_full\_chain, test\_wrk\_plot,
         test\_wrk\_client\_check — the "re-pin 18 -> 19" / "update from 18 / PLOT" / "ruling" narratives dropped), the
         6 probes (verify\_logistic\_model, verify\_final\_log\_print, verify\_wmaps, verify\_design\_matrix,
         verify\_wrk\_positions, verify\_vld\_positions — the check-name goldens C9/D9/F3/A5/V3c renamed in place; no
         doc quotes them, verified by grep before the cut). Out of the approved scope (left untouched, reported to the
         user as the next purge wave): 15 more dangling neighbors found in the same comments
         — D-065, D-074, D-075, D-079, D-080, D-081, D-083, D-097, D-142, D-157, D-186, D-187, D-287, D-289, D-318 (all
         0 hits in decisions.md + volumes). VERIFICATION: the 10 touched .py files parse, the verify\_final\_print probe
         re-run (ALL PASSED), test\_wrk\_final\_log\_print 6/0/1, the docs auditor green. After this D, the only
         9-number mentions in the workspace are the campaign's decisions entries + journal bullets — the history where
         R-540 says they belong.

D-442 | 2026-10-04 | the repo-wide purge wave 2 — the 15 dangling neighbor D numbers (the user's "purge onda 2"; the
         continuation of the D-441 wave 1, which found and reported these 15 in the same
         comments):
         D-065, D-074, D-075, D-079, D-080, D-081, D-083, D-097, D-142, D-157, D-186, D-187, D-287, D-289, D-318 — all
         verified 0 hits in decisions.md + the closed volumes. The purge, file by file (~100 citations across 24 files):
         4 worker sources (wrk\_config, logistic\_model, model\_weights, wrk\_save — comment-only: the "config
         fingerprint (D-142)" tags, the "D-142 sidecar record is RETIRED" narratives, the "(D-074/R1)" name tag); 5 test
         files (the D-287 "base\_dir override idiom" tags, the "D-289 NO-DB suite" docstring); 7 source mirror docs
         (the D-289 wrk/hlp-split tags, the "D-318 house style" references, the D-287 fixture idiom); 5 test mirror docs
         (the same idiom/split tags); 10 probes (the check-name goldens re-cut in place — V1e/V1f/V3c/V4a/V9a/V9b/V10,
         A6/E7/F1/F2/F3, A8, A1, B1, B10, C3/C4/C6/C7, E2/E3 — plus the two big re-pin-history headers of
         verify\_logistic\_model and verify\_wrk\_features de-referenced: the session numbers + dates + the behaviour
         facts kept, the D-numbers and their R1/R2/M tags dropped). Out-of-scope neighbors deliberately LEFT (verified
         present or absent independently; the next wave's candidates if the user calls
         it):
         D-082,
         D-084,
         D-085,
         D-092,
         D-096,
         D-098,
         D-099,
         D-101-D-106,
         D-105,
         D-130,
         D-139,
         D-143-D-149,
         D-175, D-258, D-278, D-279, D-295, D-298, D-312, D-313, D-314, D-315, D-317, D-326, D-327, D-328, D-331, D-332
         (a wave-3 census to be run on call — several of these, D-09x/D-10x/D-14x, may turn out to be real notes-era
         decisions). VERIFICATION: the 24 touched .py files parse; the verify\_wrk\_config probe re-run (0 mismatches —
         the golden renames are name-only, zero assertion change); the docs auditor green. After this D, the only
         15-number mentions in the workspace are the campaign's decisions entries + journal bullets.

D-443 | 2026-10-04 | tools/binio.py + its mirror doc — the post-src\_reflow consistency pass (the user's "ulteriore
         controllo sul modulo binio, dopo aver creato src\_reflow": the module was format-passed BEFORE the tool and the
         current docstring conventions existed, so it carried stale style). The sweep: NOT a src\_reflow fixed point (14
         docstrings, 734 → 703 projected); 13 method docstrings in the stale expanded form (the triple-quote + a blank
         first line) vs the house first-line-imperative on-the-quote convention; 6 R-560 Args entries untyped (file ×3,
         path ×3); 4 private helpers undocumented (\_open\_frame / \_close\_frame / \_scalar ×2 — the cache\_manager
         convention documents privates); a dead "from \_\_future\_\_ import annotations" (no string annotations in the
         file; the state\_machine precedent, D-438); 4 header trailing-ws (the separator lines with a trailing space).
         FIXED: all of the above + src\_reflow --write → 23 docstrings canonical, 689 lines. The module docstring
         (expanded form with the design choices + the byte layout + the example) ALREADY matches the house convention
         (the prng precedent) and was left untouched. 56/0/0 — NO behavior change (docstrings + one dead import only).
         The source doc REWRITTEN IN THE SAME COMMIT: the "734 lines" → "689 lines" cell. VERIFICATION: parse OK,
         56/0/0, canonical fixed point, docs auditor green.

D-444 | 2026-10-04 | test/reversi/tools/test\_binio.py — the post-src\_reflow consistency pass (the test half of the
         binio consistency check; the mirror of D-443). The sweep: NOT a src\_reflow fixed point; 8 class docstrings +
         the module docstring in the stale expanded form (the triple-quote + a blank first line) vs the house
         on-the-quote convention; 4 header trailing-ws. FIXED: all of the above + src\_reflow --write → canonical, 651
         lines (was 667). NO test added or removed (56/0/0 — NO behavior change); the test-doc needed NO sync (it
         carries no line-count or style references — only per-class counts, all still correct). COVERAGE VERDICT
         (R-850): the suite is COMPLETE for the documented contract — the byte-level hand-built goldens, the 10 scalar
         bounds + f32/f64 specials, all 10 dtypes + 0-d + F-order + big-endian, the framing error paths (MAGIC mismatch,
         wrong order, truncation, short-read stitching), the 3 empty-suffix guards (fail-fast, no file created), the LZ4
         trajectory (the empty→complete compressed digest, the decompression failure), the magic-override. The ONE gap
         found (reported to the user, NOT fixed without the call): close() idempotency (an explicit close() inside a
         with block — the \_\_exit\_\_ re-close) is guarded in code but neither documented in a docstring nor pinned by
         a test; a one-line docstring addition + a 4-line micro-test is the candidate if the user approves it (the
         state\_machine micro-test precedent, D-439).

D-445 | 2026-10-04 | the wave-3 census (CORRECTED) + one residual + the prng mirror-doc fidelity check — the user asked
         to proceed with wave 3 (the purge of the ~35 "wave-3 candidates" reported in D-442) and, before it, to check
         the prng mirror doc (it carries "(D-421)"-style references). 1. PRNG MIRROR DOC: verified line by line against
         src/reversi/tools/prng.py — FAITHFUL: the \_\_all\_\_ exact; NN=312 module-level; the twist + temper constants
         MM/UM/LM/MAG kernel-local; all 15 API entries checked for signature + semantics (the k==1 no-consume, the k<=0
         raise, the n<=1 shuffle no-consume, the IndexError on the n excess, the extract pick+remove with the
         skipped-lowest bits, the choose (0,64) empty sentinel, the pick-kernel r=(d>>11) / 2^53 scalarization, the
         batch prefix-count slots); the integration claims against random\_game.py check out too. Its three D references
         (the D-219 stream contract, the D-221 single-source technique x3, the D-421 shuffle engine) are all REAL
         decisions and the LEGITIMATE kind — the docs\_rules.md one-sentence design pointers (why the current design is
         what it is), not provenance narratives — they stay. 2. THE WAVE-3 CENSUS, CORRECTED: the ~35 "wave-3
         candidates" of D-442 do NOT exist as dangling: the full census of every D-NNN mentioned outside notes/ (98
         distinct numbers) against ALL decision volumes (hist\_decisions/decisions\_000..006 = D-001..D-425 + the
         current D-426..D-444; 443 real entries) shows ZERO dangling — every number mentioned in src/test/docs/probes is
         a real decision. THERE IS NOTHING TO PURGE in wave 3. 3. DISCLOSURE (the forward repair the iron rules
         require): the D-441/D-442 purges were executed on the FALSE premise that the 24 purged numbers (the 9 of wave 1
         + the 15 of wave 2) were "dangling / pre-notes-system". They are all REAL decisions — the existence check
         searched the current decisions.md + a bad glob (notes/hist\*.md); the closed volumes live in
         notes/hist\_decisions/decisions\_00N.md and were never searched. The edits themselves remain
         legislation-compliant — R-540 (no D-XXX provenance in docstrings / code comments) and docs\_rules.md (no
         provenance narrative, no campaign tags in the mirror docs) — the fact that the numbers are real changes
         neither; the facts were kept as plain prose throughout. No restoration is proposed (restoring the campaign tags
         would go AGAINST docs\_rules); the user is informed and decides. 4. ONE RESIDUAL FIXED (the wave-1 miss this
         check caught): hlp\_final\_log\_print.md:25 still carried "the D-321 addition" — my wave-1 verification grep
         was piped through "grep -v 'tools/state\_machine'" and that very line (which quotes the state\_machine mirror
         path) was filtered out, producing a false "0 hits" reading. Now: the campaign tag dropped, the useful
         mirror-doc pointer kept. 5. VERIFICATION: the docs auditor green; the prng module + suite untouched by this D.

D-446 | 2026-10-04 | Session close — the user's ruling (the status quo after the wave 1-2 purges) + the tools
         sub-package declared fully reviewed. After the D-445 disclosure (the 24 purged numbers are REAL decisions; the
         purges remain legislation-compliant under R-540 / docs\_rules; the facts were kept as plain prose), the user
         ruled: "No, non facciamo nulla. va bene cosi." — the current state stays as-is, NO restoration of the D
         references in the mirror docs; this closes the open item D-445 left ("the user is informed and decides"). The
         user also declares the tools sub-package FULLY REVIEWED ("i tools sono completamente revisionati"): all 5
         modules (binio, prng, state\_machine, cache\_manager, opt\_lbfgs) + their 6 test files + the mirror docs + the
         probes — every module at the src\_reflow canonical fixed point (the lone documented exception: prng.py keeps
         the D-427 hand-nudge and is never blindly reflowed), the house docstring conventions (the on-the-quote first
         line, the typed Args, no D-XXX provenance), the mirror docs in budget and faithful (the prng mirror re-verified
         line by line in D-445), the probes re-pinned with the goldens de-referenced where the legislation requires it.
         SUITE STATE AT CLOSE: 1073/0/24 (test\_state\_machine at 51 — the D-439 micro-test). NEXT SESSION: the reversi
         core zone (board / pattern / feature / mobility and the remaining Next-steps items).

D-447 | 2026-10-06 | board.py format campaign (the tools-campaign sub-work) + the src\_reflow doc-comment fix (the #:
         block mangle). 1) TOOL FIX (found by this campaign): src\_reflow MANGLED multi-line #:-doc-comment blocks — it
         stripped the #, kept the colon as text, and re-emitted the paragraph as a plain comment with the colons inline
         ("# : text : text"); the pre-write identity check still PASSED (word-level identity) and the mangled output was
         its own fixed point. First triggered by board.py, the first module carrying multi-line #: blocks. Fixed in
         reflow\_comments: a #:-prefixed paragraph is re-emitted with the "#: " prefix (the per-line marker colon
         stripped from the text), a bare #: line is a paragraph separator (preserved verbatim); seg\_words excludes the
         marker colon so the identity check stays sound. Verified: the pristine file reflows with the blocks intact, the
         6 canonical tools files stay canonical, prng.py unchanged (the D-427 flag stands). 2) BOARD SOURCE: 61
         docstrings rewritten to the house style (the on-the-quote first line, the typed Args, the Raises) + 4 MISSING
         docstrings added on public fns (square\_validate\_range, move\_validate\_range, position\_eq,
         position\_legal\_moves); R-540: the 9 D-XXX refs removed (D-111, D-140 x3, D-171, D-213 x4 — the design content
         kept, the history dropped: the "former banner note" clause, the "documented as caller's responsibility" tag);
         the dead "from \_\_future\_\_ import annotations" removed (no string annotations); the R-530 HOW clauses
         dropped where the mirror doc's Architecture already carries them; bitboard\_count's "1D array inputs" corrected
         to any shape (factual error — np.bitwise\_count is any-shape); PEP8: the 4 keyword spacings (end='' / file=) +
         the 5 one-line compounds split. src\_reflow --write → canonical, 1957 lines (was 1802). NO behavior change:
         294/0/15. 3) board.md (same commit, the mirror rule): the STALE Verified-invariant bullet removed (the "1-D
         guard (2-D → ValueError)" + the test name — neither exists since the any-shape N-D contract; the pin is the
         same-shape ValueError), the double-space pin typo fixed, the Numba kernel enumeration completed (the 2 D8 batch
         transform kernels were missing — "the 4 D8 ARRAY transform fns" were the 4 reflection array impls), the
         dual-contract intro corrected (1-D → any-shape), 2 duplicated bullets dropped (the D8 slot order and the
         little-endian notes, both stated elsewhere), size 204 → 200 (the hub budget).

D-448 | 2026-10-06 | test\_board.py format campaign (the test half of the board sub-work; the mirror of D-447). Sweep:
         not the src\_reflow fixed point (11 docstrings); 2 dead imports (unittest.mock.patch, numpy.typing); 172
         trailing-whitespace lines (4 in the GNU header — the separators are bare #, 168 in the body); 2 provenance
         class docstrings (the "session-38 scratch script" of the TestPositionHash goldens, the "session-38 scratch run"
         of the TestPositionHashLegacyParity fixture — with dangling scratch/ pointers, gitignored); the 53 "Should …"
         docstrings left AS-IS (the user is informed and decides — the imperative conversion is pending his call).
         FIXED: all of the above except the Should conversion + src\_reflow --write → canonical, 3798 lines (was 3846).
         NO test added or removed: 294/0/15 (NO behavior change). test\_board.md synced (the mirror rule): the header
         count corrected (247 → 262 concrete + 32 inherited = 294 — the doc pre-dates the N-D shape-test wave), the
         per-class counts re-measured (the 9 stale classes: FromSignedInt 5→9, ToSignedInt 6→10, FromHexStr 7→10,
         Transformations 7→10, AntiTransformations 4→7, LegalMoves 13→16, Flips 16→19, MakeMove 17→20, Hash 13→17), the
         121-row bulk corrected to 123 (re-counted twice), the stale "2-D must be 1D message verbatim" reference removed
         (the guard died with the any-shape contract; the pin is the same-shape ValueError), the campaign labels
         R1/R2/R4 removed (the behavior described in plain words), the duplicated "position print 9-line string"
         sentence fixed.

D-449 | 2026-10-06 | The four board micro-tests (the user's approval of the D-447 analysis gaps). a) position\_ro000
         identity-copy pin (test\_position\_ro000\_is\_a\_fresh\_copy — the position-layer twin of the bitboard pin; the
         mirror doc's "returns a copy" claim is now pinned, R-850). b) make\_position inputs-never-aliased pin
         (test\_make\_position\_does\_not\_alias\_inputs, arrays + lists) — the copy-then-view invariant from the mirror
         doc, now pinned in TestPositionCreation. c) The N-D rotation shape tests: 12 new tests (2-D / 3-D /
         non-contiguous / empty for ro000, ro180, ro270) closing the coverage asymmetry (the 4 reflection classes had
         them, ro090 2-D, the other three nothing). d) The square\_as\_bitboard sq>=64 wrap, documented (docstring + the
         mirror doc API row) and the dangling "open decision (docs/src/reversi/board.md)" test comment fixed — the pin
         was undocumented before; now R-850-legitimate. Suite: 294 → 308 (14 new, all green first run); the fresh LONG=1
         wrapper measurement (1087 total) is the gate input, the overview test\_board cell synced (308/0/15/0/0). Both
         .py files at the src\_reflow canonical fixed point; the mirror docs synced in the same commit (the test-doc
         counts: 274 concrete + 32 inherited = 308, the 3 new per-class increments, the two new pins named in the
         Coverage map).

D-450 | 2026-10-06 | board.py module docstring (the user-approved preview). The 5 tools modules all carry one and board
         was the first core module without; added after the GNU banner: the what-it-is (the bottom layer of the engine —
         squares, moves, bitboards, positions, D8, legal moves, flips, WOFC scoring, the legacy-compatible Zobrist hash)
         + the six design-choice bullets (uint8 squares/moves, bitboards, the dual scalar/array API, the numba hot path,
         the pydantic gates, the legacy Zobrist canon). src\_reflow --write → canonical, 1985 lines (was 1960). No
         behavior change: 308/0/15. No mirror-doc change (the header what-it-is paragraph already states the same).

D-451 | 2026-10-06 | The 53 "Should …" test docstrings converted to the imperative (the user's call on the D-447
         analysis item). Every method docstring that opened with "Should <verb> …" now opens with the imperative verb,
         capitalized: "Should convert np.int64 array to np.uint64 …" → "Convert np.int64 array to np.uint64 …". A
         mechanical prefix strip + first-letter capitalization only — no other wording touched (R-570: the test
         docstrings stay light, one line); the four "Should complete silently …" → "Complete silently …" keep the
         author's phrasing. The one pre-existing lowercase class docstring (TestPositionHashLegacyParity, a noun-phrase
         description) is left as-is. src\_reflow --write → canonical, 3949 lines. No behavior change: 308/0/15.

D-452 | 2026-10-06 | The negative phrasings removed from the board module docstring and its mirror doc (the user's
         direction: we write what the software does, not what it does not do). "No game loop, no search, no clock, no
         UI." is out (the module docstring paragraph + the board.md what-it-is paragraph), and the "no portability work"
         clause is out of the Zobrist bullet in both files — the factual "little-endian only" stays in both. No behavior
         change: 308/0/15; the module docstring stays at the src\_reflow fixed point (a no-op reflow), board.md 198
         lines, still in budget.

D-453 | 2026-10-06 | pattern.py format campaign (the pattern sub-work; the mirror of D-447). 1) The module docstring
         (the user-approved preview): the what-it-is + the six design-choice bullets. 2) All 31 docstrings to house
         style (imperative first line on the quote line); the Pattern class docstring rewritten (the 111-line 17-section
         numbered HOW list -> a compact WHAT + Attributes; the Burnside formulas kept as contract); the missing
         PatternType.from\_fingerprint docstring added; validate\_index\_array made imperative. 3) R-540: the 2
         provenance refs out ("(R1, D-020)" in \_check\_mask\_is\_principal, "D-112 M1" in PatternSet.\_repr\_); the
         design kept, the history dropped. 4) PEP8: 108 trailing-ws lines, 2 "range (" spacings, 3 indent anomalies, the
         165-char prt line split (output-identical), the "square\_from\_str,square\_to\_str" comma spacing, 4
         triple-blank module gaps. 5) The residue comments out (### End of \_init\_\_, #### End of Pattern/PatternSet
         class., the # - Symmetries/Fingerprint section markers); the \_compute\_transformed\_cells loop narration
         removed (with its dead local transformed\_masks); the "your fast pattern architecture" residue reworded. 6)
         from \_\_future\_\_ import annotations KEPT (unlike the board, where it was dead): load-bearing here (the
         Callable annotation in compute\_principal\_index\_dict is not imported; the PositionField | PositionArray
         unions over the structured dtypes are not runtime-evaluable). 7) The #: mdp.csv recipe rebuilt as per-line
         paragraphs — the first real stress test of the D-447 src\_reflow doc-comment fix (the greedy join mangled it
         once; the per-line paragraphs are a stable fixed point). src\_reflow --write → canonical, 1192 lines (was
         1370). NO behavior change: 73/0/3. pattern.md synced in the same commit (the D-452 principle applied: the "No
         search, no PDB storage, no disk I/O" sentence and the 2 "no portability work" clauses out; hlp\_su\_analysis.py
         added to the consumers; the "R2-R4" coverage claim becomes true with the R3/R4 pack tests of the micro-test D).

D-454 | 2026-10-06 | test\_pattern.py format campaign (the test half of the pattern sub-work; the mirror of D-448).
         Sweep: 3 provenance method docstrings (the "2026-08-27 minor sweep, item #16/#17/#18" campaign refs — the WHAT
         kept, the refs dropped; one of them reworded imperative), 5 dated code comments ("2026-08-28 verified /
         computed live"), 2 non-imperative "Test the ... method prints" docstrings (print\_summary / print — now the
         golden-noun form, and the hash comment's mask-order slip fixed: the comment said EDGE/ELLE/SNAKE, the
         mask-sorted order is ELLE/EDGE/SNAKE), 56 trailing-ws lines. FIXED: all of the above + src\_reflow --write →
         canonical, 1995 lines (was 2019). NO test added or removed: 73/0/3 (no behavior change). test\_pattern.md
         synced: the header count corrected (65 → 73 — the doc pre-dates the N-D shape-test wave), the 2 stale per-class
         rows (TestPatternComputeIndexes 4 → 8, TestPatternSetComputePrincipalIndexes 4 → 8, the 4 N-D shape tests named
         in both).

D-455 | 2026-10-06 | The pattern micro-tests (the user's approval of the D-453 analysis gaps). a) TestIndexArray (new
         class, 3 tests): the documented IndexArray BeforeValidator contract pinned directly (a non-uint32 ndarray
         raises ValueError, the uint32 ndarray and the non-array pass through — the "scalars pass through" clause of the
         doc line). b) The public convert array pin: convert\_to\_principal\_index with a uint32 array (value-checked
         against the dict) and a uint64 array (ValidationError). c) The R3/R4 pack tests (the doc's "R2-R4" coverage
         claim made true — same structure as test\_r2: pack-plan + the 18 bitboard packed/unpacked goldens). While
         writing (b) the empirical probe caught an error in the D-453 docstring: the public method REJECTS scalars (the
         NDArray check after the BeforeValidator), so the "scalar or array" claim is corrected to "an array ... (a
         scalar is rejected)" in the source docstring and the mirror doc contract line — disclosed here, fixed in this
         same commit. Suite: 73 → 79 (6 new, all green first run). test\_pattern.md synced (14 classes / 79;
         TestIndexArray row added; TestPatternPack 7 → 9 with R3/R4; TestPatternPrincipalIndex 1 → 2; the explicit
         import named in the Conventions).

D-456 | 2026-10-06 | Docstring section alignment (the user's observation: the lines after the first sat at column 0,
         fully left-aligned). The D-453 rewrite kept the file's legacy layout (the first line inside the method, the
         Args/Returns/Attributes sections at column 0); the house canonical (the board model, user-approved
         in D-447/D-450) is: the body paragraphs at the quote indent, the section headers at +4, the entries at +8, the
         nested continuations at +12. All 33 docstrings re-laid out to that model; the reflow fixed point holds. Two
         collateral repairs, disclosed: (1) the module docstring — the first re-indent pass mangled the design-choice
         bullets (the merged lines, the stray marker at the line ends); restored verbatim from the D-453 approved text
         (the board module carries the identical bullet structure, it is the reflow canonical for module bullet lists);
         (2) the PatternSet.print docstring — the reflow had wrapped its long single line in the wrong place after the
         mangled pass; restored to the D-453 one-line form. No behavior change: 79/0/3. 1197 lines.

D-457 | 2026-10-06 | The house docstring canonical encoded in src\\_reflow (the user-approved layout; the register
         amendment follows as the last step of the campaign). The tool now lays out EVERY docstring to the canonical:
         (1) the one-line form — a single-paragraph docstring that fits the R-520 preferred 100 (the physical line,
         indents included) is one line, three double quotes, the text, three double quotes, no spaces; the tool
         collapses the multi-line docstrings that fit and expands the one-line docstrings that do not (the single-line
         threshold moved from the 120 ceiling to the 100 preferred); (2) every other docstring opens and closes with a
         stand-alone quote line, the text starts immediately at the quote indent (no leading blank), the body paragraphs
         and the section headings (Args:/Returns:/Raises:/Yields:/Examples:/References:/Attributes: — Attributes added
         to the heading set) sit at that same indent behind a blank line, the entries at +4, a wrapped entry description
         at +8. The entries are untyped in the canonical (name: description — the Pydantic annotation in the signature
         is the type); the tool does NOT strip or add types (a parenthetical can be a gloss, not a type): the un-typing
         is the one-shot per-module migration. The rebase is by ROLE (paragraph / heading / entry / continuation /
         hand-placed deep line), so the old variants (the inline first line with the body at the quote, the D-447 board
         model at +4/+8/+12, the legacy column-0 bodies) all converge. Two bugs found and fixed during the pattern and
         board migrations, disclosed: (a) the ENTRY regex did not match a type with nested parens (np.ndarray(8,
         Bitboard)) — a user-split entry was swallowed into the previous entry as a continuation; replaced with a
         bounded single-level regex (no catastrophic backtracking); (b) the base measure included the lifted inline
         first line, which masked the old board body paragraphs (one level BELOW the quote) as deep hand-placed lines —
         the board migration was restored from git and redone with the fix (the base is now measured on the real body
         lines only). The tool's own WHAT IT IS describes the new canonical; the tool is self-canonical.

D-458 | 2026-10-06 | The pattern.py migration to the new docstring canonical (the D-453..D-456 docstrings re-laid out by
         the D-457 tool). All 33 docstrings: 23 reflowed to the stand-alone quote form (the inline first line, the D-456
         +4/+8/+12 sections, the typed entries), one collapsed to the one-line form (\\_compute\\_transformed\\_cells),
         the module docstring and the one-liners untouched (already the form). 45 entries un-typed (the one-shot
         mechanical strip of the entry-head type: the Pydantic signature is the type). Included are the user's own
         manual content edits, kept verbatim: the module docstring text rewrite, and the three inline sub-attributes of
         the Pattern class docstring split into their own entries (tmasks, mask\\_indexes, unique\\_mask\\_indexes — the
         "n\\_configurations: … tmasks (…): …" inline condition, found in three attributes; the user split them, the
         campaign un-typed them). This D supersedes the D-456 layout (the +4/+8/+12 model) for this file: the new
         canonical is the enforcer's fixed point. 1197 -> 1236 lines. NO behavior change: 79/0/3.

D-459 | 2026-10-06 | The board.py migration to the new docstring canonical (by the D-457 tool), plus the fix of 4
         PRE-EXISTING misplaced docstrings found by the user's review. All 68 docstrings (64 + the 4 newly recognized
         ones): 61 reflowed to the stand-alone quote form, the rest already the form; 84 entries un-typed (79 + the 5 of
         the four recovered docstrings). The 4 misplaced ones were DEAD string literals in the original source (already
         so in the D-452 git): a string placed AFTER the first statement (after the return) in
         square\\_validate\\_range, move\\_validate\\_range, position\\_eq and position\\_legal\\_moves — unreachable
         expression statements, not docstrings (a docstring is the body[0] string), invisible to every reflow pass (old
         and new) and to the AST docstring audits, which is why they survived in the old typed format. Moved to the top
         of the body (real docstrings now); zero behavior change (the dead literal was never executed, a docstring has
         no side effects). Migration note, disclosed: the first board pass ran before the D-457 base-measure fix (the
         old board body paragraphs, one level below the quote, would have stayed deep) — the file was restored from git
         and the migration redone with the fixed tool. 1984 -> 2042 lines. NO behavior change: 308/0/15.

D-460 | 2026-10-06 | The register: R-560 amended in place (the user-approved text, the last step of the docstring
         campaign). Title: "Docstrings: FORMAT" -> "Docstrings: the layout". The new body encodes the canonical exactly
         as src\\_reflow.py enforces it: (1) the one-line form (a single-paragraph docstring that fits the R-520
         preferred 100, the physical line indents included, is one line: three double quotes, the text, three double
         quotes, no spaces); (2) every other docstring opens and closes with a stand-alone triple-quote line, the text
         starts immediately at the quote indent (no leading blank); (3) the first text line is the imperative
         one-sentence summary, the body paragraphs at the same indent; (4) the section headings
         (Args:/Returns:/Raises:/Attributes:/…) at the same indent behind a blank line, the entries at +4, a wrapped
         entry description at +8, the Returns: key-by-key detail kept from the old clause; (5) the entries untyped (the
         Pydantic annotation in the signature is the type), and src\\_reflow.py named as the enforcer (it lays out every
         old variant to the canonical and collapses / expands the one-line form). Unchanged: R-520 (the widths are
         cited, not duplicated), R-530/540/550 (content rules), R-570 (the test light form stays coherent: a two-line
         test docstring that fits 100 is collapsed to one), R-580 (the probe). Closes the docstring campaign
         (D-457..D-460: the tool, pattern, board, the register).

D-461 | 2026-10-06 | The tools/binio.py migration to the R-560 canonical (the D-457 tool; the tools sub-work resumes
         under the new layout). 16 of 23 docstrings reflowed to the stand-alone quote form (the rest were already
         one-liners or the form); 26 entries un-typed (the one-shot mechanical strip: the Pydantic / signature
         annotations are the types). 689 -> 704 lines. NO behavior change: test\\_binio + test\\_usage\\_binio 59/0.

D-462 | 2026-10-06 | The tools/prng.py migration to the R-560 canonical (the D-457 tool). 2 of 20 docstrings reflowed to
         the stand-alone quote form; 21 entries un-typed (the one-shot strip; the internal-state attributes of MT19937
         (\\_mt / \\_mti) were already name: description form and stayed). 471 lines. NO behavior change: test\\_prng
         30/0.

D-464 | 2026-10-06 | The tools/state\_machine.py migration to the R-560 canonical (the D-457 tool). 18 of 27 docstrings
         reflowed to the stand-alone quote form; 21 entries un-typed (the one-shot strip). 499 -> 510 lines. NO behavior
         change: test\\_state\\_machine 51/0.

D-465 | 2026-10-06 | The tools/opt\_lbfgs.py migration to the R-560 canonical (the D-457 tool). 11 of 13 docstrings
         reflowed to the stand-alone quote form; 65 entries un-typed (the heaviest strip of the batch — the optimizer's
         signature is long). 629 -> 637 lines. NO behavior change: test\\_opt\\_lbfgs 24/0.

D-466 | 2026-10-06 | The feature.py source pass (the feature sub-work opens). (1) The R-560 canonical via the D-457
         tool: 11 docstrings reflowed; the 7 Attributes: entries of the FeatureSet class docstring keep their types
         FOLDED INTO THE PROSE (the plain class has no signature annotations — the docstring is the only type home; e.g.
         "name: A human-readable label (str) …"); the legacy Methods: section deleted (it duplicated the methods' own
         docstrings, R-530 one home per fact); 2 code smells fixed: the dead branch in feature\\_blocks (f.category in
         (0, 'intercept') — an IntEnum is never the string; the guard is f.name == 'INTERCEPT') and the
         \_\_init\_\_ return annotation (-> Self on a None-returning init -> -> None); trailing whitespace stripped and
         the blank-line counts normalized to the house 2 (the migrated files are at 0 / 2). 337 -> 313 lines. NO
         behavior change: test\\_feature 29/0/1. (2) TOOL FIX found in passing, disclosed: the rebase classified a
         legacy same-column entry (heading and entries sharing the base column, the pre-D-453 feature layout) as prose
         and mashed the Attributes: entries into a run-on paragraph — the first feature pass was restored from git and
         redone; the tool now recognizes a same-column entry under an active heading; all migrated files re-verified
         canonical (no regression).

D-467 | 2026-10-06 | The feature mirror-doc fidelity fix (docs\_rules §5: the doc is part of the module). The D-417 N-D
         commit ("mirrors aligned") updated the Architecture prose but not the counts and the test tables: 4 stale
         points repaired — (1) feature.md's Verified invariants header dropped the count line entirely (the pattern.md
         standard: bullets pin to test names, no counts in the source mirror); (2) feature.md's compute\_indexes bullet
         gained the four N-D invariants ((1,3) → (1,3,I), (3,1,1) → (3,1,1,I), F-order parity, empty (0,2) → (0,2,I))
         and the count 5 → 9; (3) test\_feature.md's header 25 (24+1) → 29 (28+1); (4) its Coverage row for
         TestFeatureSetComputeIndexes 5 → 9 with the N-D tests listed. Docs clean at the audit; no source change.

D-468 | 2026-10-06 | The three missing feature tests (the user-approved completion) + the test file's R-560 pass + the
         mirror docs at the final counts. (1) test\\_new\\_from\\_mobility\\_invalid\\_type (a str argument to the
         mobility factory → pydantic ValidationError — the pattern factory already had its twin);
         test\\_init\\_invalid\\_name\\_type (a non-str name blocked by the @validate\_call gate);
         test\\_print\\_summary\\_none\\_branches (the intercept-only print golden pinning the "MobilitySet is None." /
         "PatternSet is None." branches, which the full-set golden never executed; the ab7c1b64… feature hash, the same
         literal the intercept-only init test pins). (2) The test file: 7 docstrings reflowed to the canonical, trailing
         whitespace stripped (the migrated files are at 0). (3) The mirror docs: test\\_feature.md 29 → 32 (31 run + 1
         PERF), the Coverage rows (TestFeature 9, TestFeatureSet 8) + the Goldens bullet + the strict-typing line;
         feature.md's TestFeature (9) / TestFeatureSet (8) counts and the new pins. 29 → 32 tests: 32/0/1.

D-469 | 2026-10-06 | The mobility.py + test\\_mobility.py format pass (the last base-module sub-work). The R-560
         canonical via the D-457 tool: 10 of 14 docstrings reflowed in the source (the two formula blocks in the class
         and compute\_indexes docstrings preserved verbatim as hand-placed deep lines), 5 in the test; 6 Args: entries
         un-typed (the signature annotations are the types; the Returns: entries name the return types — content,
         untouched). Manual format fixes: the 142-char kernel signature split (over the R-520 120 ceiling), the 130-char
         PERF print re-wrapped, trailing whitespace stripped (both files at 0, the migrated-file state), the blank-line
         counts normalized to the house 2 (3 after \_\_all\_\_, 1 between popcount64 and the vectorized kernel); one
         wording fix in the masks property docstring (the array holds the (mask, amask) pairs, not "the mask values").
         312 -> 296 source lines, 519 -> 521 test lines. NO behavior change: test\\_mobility 30/0/1.

D-470 | 2026-10-06 | The mobility mirror-doc fidelity fix (docs\_rules §5 — the same drift class as the feature one:
         the D-417 N-D wave added the 4 shape tests to the suite without touching the docs). 4 points: (1)
         test\\_mobility.md's header 26 (25+1) → 30 (29+1) and its Coverage row TestMobilitySet 19 → 23 with the 4 N-D
         tests listed; (2) mobility.md dropped the stale "306 lines." (the file is 312; a line count in a mirror is a §4
         defect and would go stale again at the reflow); (3) the Verified invariants header rewritten without the suite
         count (the pattern.md standard) and the probe named explicitly (the 5 active sections 1,2,3,4,6 — section 5 is
         a D-106 tombstone in the probe, not in the doc); a new bullet pins the N-D shape edges from the suite side; (4)
         the API table's popcount64 row un-"Public": the docstring says "not part of the public API" (a test/inspection
         helper, OUT of \_\_all\_\_). Everything else verified faithful: the LMC/ALMC/DLMC glossary + formula, the
         n\_configurations distinct-value semantics, the underflow-safe arithmetic, the hash construction + the
         empty-set divergence, the sorted-column contract. Docs clean at the audit.

D-471 | 2026-10-06 | The one missing mobility test (the feature twin):
         test\\_compute\\_indexes\\_wrong\\_argument\\_type (None / list / str / plain int64 ndarray → pydantic
         ValidationError, the subTest idiom of test\\_feature::test\\_compute\\_indexes\\_wrong\\_argument\\_type) — the
         only gap left in the suite after the D-417 N-D wave. The mirror docs at the final counts: test\\_mobility.md 30
         → 31 (30 run + 1 PERF), the Coverage row 23 → 24 + the subTest loop listed; mobility.md's N-D bullet gains the
         strict-typing pin. 30 → 31 tests: 31/0/1.

D-472 | 2026-10-06 | The regab source + test + mirror-doc pass, one commit (the user-approved single-D plan, with the
         (b) activate\_conn test added): (1) the 10 numpydoc docstrings converted to the house Google style — the last
         numpydoc module in the tree; the two class Attributes: sections fold the types into the prose (plain classes,
         the FeatureSet precedent), the RegabDBConnection Methods: section is removed (close already has its own
         docstring; activate\_conn gained the one the Methods: entry carried); the gp\_as\_df Notes: bullets dropped
         (they duplicated the Args entries; the vague "may raise an Exception" is not a contract); (2) R-540: the D-143
         (x2) and D-139 (x4) references and the "Roberto's ruling" phrases removed from the docstrings, the decisions
         kept as facts; (3) a real doc/code mismatch fixed: regab\_load\_data\_set\_from\_file promised a ValueError on
         checksum mismatch, the code raises RuntimeError (the tests pin the RuntimeError) — the Raises: now says
         RuntimeError, extended to the description/version checks; (4) PEP8: the default-value spacing in the connection
         signature, the double space in the RegabDataSet body, the 152-char SQL string split, the two over-120 separator
         lines matched to the house separator, trailing whitespace 0; (5) test\_regab.py: the real test bug —
         test\\_invalid\\_ec \\_type called RegabDataSet without self.rc, so it passed for the wrong reason (the
         ValidationError came from the missing argument, not the ec gate) — self.rc added; 4 test docstrings now say
         ValidationError (pydantic), not TypeError, and 1 says TypeError (the dtype check does raise it); the "userbame"
         header typo fixed; the new test\\_activate\\_conn (the user-approved (b): a connection created with
         activate\\_conn=False is None, then established and closed). (6) The mirror docs: regab.md dropped the stale
         "678 lines." (the §4 defect), the V5 unpinned invariant moved out of the Verified invariants (docs \\_rules §3)
         into Conventions, the "( the" double-space refix; test\\_mobility-style counts refreshed: 48 → 49 tests (36 + 2
         + 11), the TestRegabDB row 2 → 3 with the activate\\_conn re-open listed. 48 → 49 tests: 49/0/0 at the DB-gated
         LONG=1 run. Both .py at the src\\_reflow canonical fixed point (678 → 582 source lines, 796 → 720 test lines —
         the numpydoc collapse).

D-473 | 2026-10-06 | The base\_model pass (source + one completion test + mirror-doc + the index repair), one commit
         (the user-approved (a) + (b)): (1) the 8 missing method docstrings added — \_\_init\_\_, the 2 read properties,
         the verbosity getter + setter, and the 3 show/export pass-throughs (the house convention: every public method
         documented; base\_model was the only R-560 module with bare methods); the orphan comment line "#
         reversi/base\_model.py" after the license header removed; the 3 legacy docstrings reflowed (126 → 130 lines,
         the +8 docstrings minus the rewrap gain); (2) the one un-pinned branch of run(): the "last" (any case) /
         blank-string targets — test\\_run\\_last\\_and\\_blank\\_strings\\_drive\\_the\\_last\\_step in
         test\\_logistic\\_model (the bare-BaseModel home of the V5 pin; 4 sub-targets: "last", "LAST", " ", "") — 29 →
         30 tests: 30/0/0; (3) the mirror doc: the stale "126 lines." dropped (the §4 defect), the suite count 29 → 30,
         V5 now lists the new pin; (4) the index repair: the overview Source files table had NO row for
         src/reversi/base\\_model.py — a docs\\_rules violation invisible to the overview audit (it checks existing
         rows, not index completeness); the row added (the wave). The doc was otherwise fully faithful (21 probe checks
         verified, all 5 V-pins real).

D-474 | 2026-10-06 | Correction to the D-473 record (the repair-forward + disclosure protocol, self-inflicted
         damage): D-473's "(4) the index repair" claim was WRONG. The Source files table row for
         src/reversi/base\\_model.py existed all along, escaped as base\\_model like every other row in the table; every
         investigation grep in this session used the unescaped pattern (base\_model), which cannot match an escaped row,
         so the row looked missing. The wave insertion on top of that created a DUPLICATE row, now removed. The index
         was complete: no docs\\_rules violation existed. Everything else in D-473 (the 8 added docstrings, the
         last/blank completion test 29 -> 30, the "126 lines." drop, the V5 pin) stands.

D-475 | 2026-10-06 | The random\_game source + test + mirror-doc pass, one commit (the user-approved (a) + (b)): (1)
         source: the D-221 reference removed from the \_advance\_step docstring (R-540), the random\_game\_play\_path
         docstring restructured (the two "If…" paragraphs + the "Dual scalar/array:" paragraph were nested inside the
         Returns: section — they are body paragraphs, now before the section), 7 docstrings reflowed (349 → 314 lines);
         (2) test: the 3 unused imports removed (square\_to\_str, PositionField, bitboard\_print), the 2 missing class
         docstrings added (the user-approved (b): TestRandomGameChooseMove, TestRandomGamePlayPath), the ONE real
         coverage gap closed (the user-approved (a)):
         test\\_target\\_ec\\_out\\_of\\_range\\_is\\_a\\_validation\\_error — the TargetEcInt gate (ge=0, le=60) was
         never pinned: 61 and -1 are the gate's ValidationError before any draw; 13 + 3 docstrings reflowed (963 → 958
         lines); 42 → 43 tests: 43/0/1; (3) the test mirror doc: the 3 stale counts of the N-D wave (D-417) repaired —
         ChooseMoveArray 6 → 9, MakeMoveArray 7 → 10, PlayPathArray 9 → 12 — the N-D shape cases (2, 2) / (2, 2, 1) /
         F-order / empty (0, 2) now listed, the stale "the 1-D guard" item (no such test exists) out, the scalar
         PlayPath row 4 → 5 with the new validation test. The SOURCE mirror doc is untouched: it was verified fully
         faithful (all 6 invariants pinned to real tests; the D-285 pointer is legitimate under docs\\_rules §3.2; no §4
         defects) and the source changes are docstring-only, invisible to the mirror's claims.

D-476 | 2026-10-05 | The client source + test + mirror-doc pass, one commit (the user-approved plan): (1) source:
         the D-417 reference removed from the make\_evaluation\_function\_array docstring (R-540), the 5 typed docstring
         entries untyped (R-560(5): the 3 "mw (ModelWeights):" Args entries — the signature annotation is the type — and
         the 2 \_prepare\_weights Returns sub-entries "expanded\_offsets (np.ndarray, u32):" / "z2y (Callable):"), 3
         docstrings reflowed (157 → 153 lines); (2) test: the 2 "D-422: " prefixes removed from the
         test\_2d\_structured\_corder\_parity / test\_3d\_structured\_corder\_parity docstrings (R-540), the 4
         trailing-whitespace header "# " lines cleaned (the reflow does not touch them), 8 docstrings reflowed (207 →
         211 lines); no coverage gap — all 8 tests pin the documented contract, and the scalar EF absolutes are pinned
         end-to-end by the full-chain A2030 / A2050 EF pins; 8/0/1 unchanged; (3) the source mirror doc: the "157
         lines." drop (docs\_rules §4), the 158-char header line re-wrapped, the Conventions bullet-1 provenance
         narrative removed (the "applied in D-323, the D-141 / D-111 references removed" campaign story + the stale
         "typed Google-style" wording contradicting R-560), the strict-array bullet to a single D-422 pointer; (4) the
         test mirror doc: the 2 stale counts repaired (1 class / 7 → 8 tests, the table cell 7 → 8 — the suite cell
         8/0/1 counts the total incl. the PERF skip), the phantom test\_2d\_structured\_raises\_value\_error row (the
         pre-N-D 1-D-guard test, no longer existing) replaced by test\_2d\_structured\_corder\_parity +
         test\_3d\_structured\_corder\_parity with their what-it-pins rewritten.

D-477 | 2026-10-05 | The logistic\_model source + test + mirror-doc pass, one commit (the user-approved plan incl. the
         (a) gap closure): (1) source: the D-099 reference removed from the su\_analysis\_tables field comment (R-540),
         the 5 missing top-level docstrings added (the house canonical: \_check\_config\_file\_path,
         \_check\_base\_dir\_override, \_created\_up, \_created\_down, build\_model), the 2 PEP8 E302 single blanks
         between top-level defs fixed, the orphan "# ---" marker out, 9 docstrings reflowed (331 -> 330 lines); (2)
         test: the 4 trailing-whitespace header "# " lines cleaned (the reflow does not touch them), the 2 code trailing
         spaces + the 1 all-whitespace line removed (the no-ws-lines convention, verify\_save A14), the in-class double
         blank (E502) to one, and the (a): test\_build\_model\_builds\_and\_runs\_to\_the\_last\_level — the
         build\_model script entry was not pinned anywhere (the full chain imports LogisticModel directly, no
         subprocess): with LogisticModel patched in the module namespace, the construct + the move\_to\_last are pinned;
         30 -> 31 tests: 31/0/0; (3) the source mirror doc: the 3 stale 18 -> 19 level counts repaired (the "18 active
         levels" contradicted its own pin — probe V3c says 19; the 18 `wrk_*` factory modules count and the "18 workers"
         of the Integration section), the "29 tests" -> 31 (the D-473 test was not reflected), the Conventions "(A2 +
         ec\*10)" derivation removed (it contradicted the Architecture section: both A2xxx fixtures run ec 20), the
         build\_model script entry now pinned in the Verified invariants; (4) the test mirror doc: the "29 tests" header
         count repaired + the "537 lines." drop, the class row 26 -> 27 with the D-473 last/blank-string test + the new
         build\_model pin listed, the factory-patch convention bullet extended with the LogisticModel patch. The
         src\_reflow canonical fixed point on both files (the test was already canonical).

D-478 | 2026-10-05 | The model\_weights source + mirror-doc pass, one commit (the user-approved plan; this file has no
         test module — by design): (1) source: the 3 D-144 references removed from the comments (R-540: the "D-144
         (C2):" of the config-provenance field comment, the "(D-144/C2):" of the write section-1 comment, the "(v2
         only, D-144/C2):" of the read section-1 comment), the 2 "Roberto's ruling" mentions removed (the D-472 regab
         precedent, incl. the "mettiamola in testa" quote), the 4 trailing-whitespace header "# " lines cleaned (the
         reflow does not touch them), 2 docstrings reflowed (276 -> 266 lines); (2) the mirror doc: the "276 lines."
         drop (docs\_rules §4), the 2 "the test module" pointers repaired — no test module exists for this file: the
         guard messages are pinned by test\_lm\_worker\_full\_chain (the TestModelWeightsReadGuards suite) and the
         SHA3-256 sidecar is the verify\_sha3\_256\_sidecar call in the full-chain suite (a binio function) —, the 2 O#
         references removed (the O# family is not a recognized reference family; the processed base docs carry none),
         the "Pattern/ PatternSet" spacing typo fixed. The coverage analysis found NO gap: the no-DB micro tier
         (TestModelWeightsReadGuards 2 + TestModelWeightsV2 3: the read guards, the v1 backward-compat read, the v2
         synthetic-ctx round-trip, the corruption sentinel) lives in test\_lm\_worker\_full\_chain by design (the
         base\_model precedent); the trained round-trips are pinned by the A2030/A2050 suites and the verify\_save
         A4-A6b statics (the 18-check census) carry the rest. The src\_reflow canonical fixed point on the source.

D-479 | 2026-10-05 | The hlp\_config\_schemas source + test + mirror-doc pass, one commit (the user-approved plan incl.
         the 2 R-850 completeness tests): (1) source: the 12 E302 single blanks between top-level classes fixed (the
         house canonical is 2; the 1-blank cases that survive in the canonical modules live only in the "#:" marker
         context), 16 docstrings reflowed to the R-560 canonical (the 7 one-sentence class docstrings collapsed to the
         one-line form, the 5 inline validator docstrings to standalone quote lines, the 4 multi-sentence class
         docstrings re-wrapped to 100; 438 -> 436 lines); (2) test: the R-550 violation repaired — the helper name
         \_strip\_i017 carried the closed idea I-017 inside a code identifier, renamed \_strip\_sections —, the stale
         parenthetical of test\_pattern\_mask\_0x\_prefix\_rejected dropped (it claimed a field-description / parser
         mismatch that does not exist: the description, the validator docstring and the parser agree), the 2 R-850
         completeness tests added — test\_optimization\_checkpoint\_file\_required (the documented required field was
         unpinned) + test\_log\_file\_name\_default\_none (the documented FINAL\_LOG\_PRINT no-op convention was
         unpinned); 30 -> 32 tests: 32/0/0; 28 test docstrings reflowed to the standalone quote form (441 lines); (3)
         the source mirror doc: the "27 tests" -> 32, the phantom pin test\_ec\_out\_of\_range\_rejected replaced by
         test\_empty\_count\_required\_bounded (which also covers the missing-ec case the test pins), the 3 never-named
         pins added (test\_optimization\_hi\_perf\_blocks, test\_plot\_style\_defaults\_and\_constraints,
         test\_rarity\_thresholds) + the 2 new tests pinned, the Integration fixture path repaired (the phantom
         src/reversi/test/data/ -> test/reversi/data/rlm\_00.json), the prose re-wrapped to the corpus 120 width (the
         100-wrap pushed the doc to 122, over the 60-120 budget; now 120); (4) the test mirror doc: the "30 tests" ->
         32, the phantom coverage row repaired (test\_ec\_out\_of\_range\_rejected "ec 99 and -1" ->
         test\_empty\_count\_required\_bounded "missing rejected, ec 61 and -1 rejected, the fixture's 20 accepted"),
         the goldens "ec 99" -> "ec 61", the docs\_rules §4 narrative clause of test\_client\_check\_tol\_override
         dropped ("hence the model-file size-band growth": a rationale not in the code, no pointer), "the corpus
         defaults seed 42 / 1e7 / ec 20" -> "(seed 42, 1e7)" (the ec is the root empty\_count, not a corpus default, and
         the test does not assert it), the 2 new tests listed in the Coverage table. The src\_reflow canonical fixed
         point on both files; the docs\_format\_audit finding on this module's source doc cleared.

D-480 | 2026-10-05 | The hlp\_analytics source + mirror-doc pass, one commit (the user-approved plan; no test module by
         design — the module is pinned by the probe verify\_analytics (36 checks, green) + the 14-test
         test\_wrk\_analytics worker suite (14/0/0 with LONG)): (1) source: the 4 R-540 provenance removals (D-105/M2 in
         2 docstrings — the \_format\_header three-metric-wide line + the compute\_training\_dense\_metrics
         fallback-weights line —, D-311 in the 2 pooled eta/omega comments, with their "replaces the inline SS" history
         clause), the 2 over-120 table f-strings split into fragments (the R-520 120 ceiling applies to code lines too;
         the split is byte-identical — the rlm\_02 / rlm\_01 goldens confirm), the 4 header "# " trailing-ws lines, the
         2 trailing EOF blank lines trimmed to the single \n (734 -> 732 manual, 699 at the reflow fixed point: 12
         docstrings + 2 "#:" blocks re-wrapped to 100); (2) the mirror doc: the standalone "724 lines:" line + the "724
         lines;" in the Structure bullet dropped (line counts forbidden, docs\_rules §4; stale — the file was 734), the
         4 campaign tags dropped (the D-308 / D-307 "addition" bullets, the D-311 "unification" + the D-316 "omega line"
         in the mobility bullet), "(the single source, the D-298 split)" normalized to the §3.2 "the single
         source, D-298", the stale "13-test worker suite (5 DB-gated + 8 NO-DB)" -> 14 (6 + 8) (verified against the
         file; the wrk\_analytics test doc already said 14 — the source doc was behind), the 2 ambiguous "test doc"
         pointers made explicit (the dense 4 values + the rlm\_01 exact values live in the test\_wrk\_analytics doc —
         there is no hlp\_analytics test module), "18 lines — + the Config SHA3-256 line" -> "18 lines total, incl. the
         Config SHA3-256 line" (the probe D3 pins 18 total, SHA line included), the TrainingDenseResult API row added
         (the §3.1 all-\_\_all\_\_-names rule; the ModelWeights precedent). No suite cell moves (no test touched).

D-481 | 2026-10-05 | The hlp\_anova source + test + mirror-doc pass, one commit (the user-approved plan): (1) source:
         the 17 typed Args entries de-typed to the R-560(5) untyped canonical (the corpus: the client "mw: the trained
         model"; the reflow enforces the layout only, it does not strip the type names — the D-477 "typed entries
         untyped" precedent), the 9 docstrings to the reflow fixed point (387 lines, the formulas + the key-by-key
         Returns detail kept); no D-XXX / I-XXX / over-120 / ws lines in the source. (2) test: the header module name
         repaired (test\_hlp\_feature\_analysis -> test\_hlp\_anova — the pre-D-315 rename residue), the 2 R-540 in the
         module docstring (the D-298 split provenance + the D-290 policy tag), the unexplained "(c)" tag of the
         TestAdherence docstring, the 10 split expressions joined (each fits one line within the 120 ceiling, R-520),
         the 2 R-850 completeness tests: test\_zero\_variance (the documented zero-variance degeneracy had no pin) +
         test\_degenerate\_tail (the documented "p nan when the merged result has fewer than 2 cells" had no pin); 16 ->
         18 tests, 18/0/0. (3) the source mirror doc: the provenance cleanup (the 15 D-XXX references -> 0: the header
         rename / split history rewritten to the present, the campaign-tag labels of the Verified-invariants bullet, the
         "design section 3.5" void pointer, the "typed Google-style Args / Returns" clause corrected to the post-pass
         state, the "the 120-char, no hard limit" bullet dropped — it contradicted the R-520 120 ceiling), the
         hand-computed bullet re-counted 16 -> 18 with the 2 new pins. (4) the test mirror doc: the 5 D-XXX references
         dropped, the 16 -> 18 re-count (the header + the coverage rows + the goldens), the run\_utests.sh positioning
         bullet rewritten to the actual machine order (between test\_wrk\_features and test\_hlp\_su\_analysis; the
         worker suite between test\_wrk\_indexes and test\_hlp\_wmaps). The src\_reflow canonical fixed point on both
         files. Cell: test\_hlp\_anova 16/0/0 -> 18/0/0.

D-482 | 2026-10-05 | The D-481 journal-bullet repair + the angle-bracket matter closed: (1) the D-481 wave's escape
         helper mangled 10 identifiers in the two journal bullets (a backslash before EVERY character of the identifiers
         — the 'backslash-join-over-the-letters' bug); rebuilt with the underscore-only escape, no other content change.
         (2) The user's Obsidian "red from session 94" report (the raw < in the journal — 16 lines, incl. the tag-like
         <module> / <total>… / <verbo> sequences): the user's own ruling — it was Obsidian's EDITING mode, not a
         rendering defect; the raw < in the journal stay UN-ESCAPED, no lint / log\_rules change. Leave-as-is ruling
         recorded so a future pass does not re-escape them.

D-483 | 2026-10-05 | Journal line-start protection (Obsidian): 5 journal continuation lines began with "+ " right after
         the 2-space indent — Obsidian parses a "+" after up to 3 spaces of indent as a nested list bullet (the
         right-indented bullet the user saw); the line-leading "+" escaped to "\+" (leading position only — the 386
         mid-line "+" untouched, the user's ruling). The same marker class checked and clear: no line begins at column 0
         with "\*" or a "N. " ordered-list marker; the line-leading "-" is the journal's own bullet marker (intended
         rendering).

D-484 | 2026-10-05 | notes\_lint: the new permanent code LISTMARK (the user's request after D-483): no line-leading + or
         \* after up to 3 spaces of indent, outside code spans — Obsidian renders it as a nested list bullet.
         Implemented as listmark\_issues(), wired into all seven linters; a + / \* not followed by a space (an inline
         plus, a \*\* bold opener) is not a list marker, and the line-leading - stays the journal's own bullet
         (intended). The check caught one existing line — the overview Next-steps cascade continuation " + the
         mirror-doc fidelity repair", escaped. The three decisions.md 9-space continuations beginning "+ " are not
         Obsidian list markers (9 > 3 spaces: paragraph lazy continuation) and stay as-is. The closed journal volumes
         carry 24 such lines — frozen, not re-escaped; they would flag under the new code if linted on explicit request.

D-485 | 2026-10-05 | The hlp\_design\_matrix source + test + mirror-doc + probe pass, one commit (the user-approved
         plan, incl. the new str-filename test): (1) source: the 2 R-540 D-139 tags dropped from the store/load
         docstrings (the line now reads "LZ4 whole-file compression by default."), the 4 bare header lines stripped, the
         docstrings to the reflow fixed point (139 -> 143: the 2 two-paragraph store/load docstrings expand to the
         standalone-quote form, the R-560(2) canonical); no other stains (the 4 public one-line imperatives are the
         corpus binio-I/O convention, the model\_weights precedent). (2) test: the 4 bare header lines, the mock-comment
         colon, the new test\_store\_and\_load\_with\_str\_filename (the documented str | Path form was pinned only as
         Path — the R-850 gap); 15 -> 16 tests, 16/0/0, reflow fixed point (298 -> 304). (3) probe (the same-commit pin
         set, probe\_rules section 5): A1 139 -> 143, A2 / A6 / A7 the line-number pins shifted +4 (the docstring
         expansion), A9 the pinned string updated to the de-tagged standalone-quote form, G1 279 -> 304 + G2 14 -> 16 —
         the probe was ALREADY stale on G1 / G2 before this pass (the N-D parity test landed without the probe update);
         it now passes 53/53. (4) the source mirror doc: the 14 -> 16 re-count (2 spots) + the N-D / str-filename pins
         described, the "139 lines" -> 143 (the A1 pin), the API-row order repaired (the sidecar verify precedes the
         reader open — the Architecture bullet was already right), the 2 typos (np.repeat(, dm.wmaps); the doc carried
         no D-tags (already clean-style). (5) the test mirror doc: 14 -> 16 (the header + the coverage rows 2 -> 3 /
         8 -> 9 with the 2 new test descriptions). Cell: test\_hlp\_design\_matrix 15/0/0 -> 16/0/0.

D-486 | 2026-10-05 | The hlp\_final\_log\_print source + mirror-doc pass, one commit (the user-approved plan incl. the
         no-test-module clause): (1) source: the 1 typed Args entry de-typed to the R-560(5) untyped canonical ("ctx
         (LMContext):" -> "ctx:"), the docstring to the reflow fixed point (67 -> 65); no other stains (the header was
         already canonical, the imports 5/5 used, the single-name \_\_all\_). No test module by design — the pin set is
         the probe + the 6-test worker suite (incl. the LONG-tier rlm\_00 e2e) + the full chain; the probe pins code
         strings only (no line-count / docstring pins), so the pass is probe-safe. (2) the source mirror doc: the 3
         D-tags dropped (the D-312/D-313/D-315 precedent enumeration, the 2x "the ctx idiom, D-317" pointers — the
         section 3.2 pointer is permitted but dropped for corpus uniformity with the passed hlp modules), the "the typed
         Args" clause corrected to "the untyped Args" (the post-pass state), the 154-char line split, the Verified
         invariants opened with the "No test module by design:" clause (the hlp\_analytics sibling pattern). The doc was
         otherwise faithful (the write-asymmetry, the NO-trailing-newline content + the 5/8 live-line shape verified
         against the state machine's format\_event\_log / \_format\_event\_line, the pin set A3 / B2 / B3 / B4 all real
         and green). No suite cell moves (no test touched).

D-487 | 2026-10-05 | The hlp\_generate source + test + mirror-doc pass, one commit (the user-approved plan incl. the 2
         completeness micro-tests): (1) source 229 -> 226: the 3 R-540 tags dropped (the 2x store/load "(D-139, as in
         model\_weights)" comments + the "(D-098, Roberto's ruling)" inference-semantics comment), the 124-char WARN
         line repaired (the message extracted to a msg variable + ctx.log\_event — byte-identical, the test pins the
         substring), the compute\_w\_dense docstring made imperative ("Computes" -> "Compute") with its bullets
         converted to a paragraph (the dry-run showed the reflow flattens docstring bullets into mangled prose), the 4
         bare header lines stripped, reflow fixed point. (2) test 333 -> 340: the 4 bare header lines + the 2 approved
         micro-tests — test\_store\_and\_load\_with\_str\_filename (the documented str | Path contract was pinned only
         as Path, the R-850 gap class of D-485) and test\_pattern\_logs\_weighted\_mean\_and\_fallback (the 2
         pattern-branch INFO logs were documented but pinned by no test); 16 -> 18 tests, 18/0/0, reflow fixed point.
         (3) the source mirror doc: the 2 tags dropped ("(the D-098 ruling)", "(the ruling comment)"), the pin-set count
         re-measured (the 19-test pair -> the 21-test pair: 18 no-DB + 3 DB-gated); the doc was otherwise faithful (the
         6 wide lines are exempt table rows, the "6th cache\_manager consumer" verified in pipeline order, the 3
         category branches line by line). (4) the test mirror doc: "the R2 semantics" dropped, "The 2 additions" -> "The
         compression-default pair" (the campaign-addition narrative), the re-count 16 -> 18 + the 2 coverage
         descriptions + the INFO-log goldens. (5) probe: the 18-check pin set untouched and green — it pins string
         presence only (no line counts, no docstring text), so the pass is probe-safe. Cell: test\_hlp\_generate
         16/0/0 -> 18/0/0.

D-488 | 2026-10-05 | The hlp\_indexes source + test + mirror-doc + probe pass, one commit (the user-approved plan incl.
         the repr micro-test): (1) source 228 -> 228 (the line count survives the pass): the 12 typed Args entries
         de-typed (the R-560(5) canonical: \_\_init\_\_ 3, store 3, load 3, compute 1, is\_cache\_consistent 2), the 2x
         "(as in model\_weights)" cross-refs dropped from the store/load docstrings (the exact sibling canon), the
         lowercase read comment capitalized, the docstrings to the reflow fixed point — the A1 "228 lines" probe pin and
         the doc's "Source shape" bullet stay valid untouched. (2) test 307 -> 312: the approved
         test\_repr\_one\_line\_summary micro-test (the one-line repr was documented — API row + Architecture bullet —
         but pinned by no test and no probe, the R-850 gap); 14 -> 15 tests, 15/0/0, reflow fixed point. (3) the source
         mirror doc: the load order repaired in the API row AND the Architecture bullet (the sidecar verify runs BEFORE
         the LZ4 guard + reader open — the 2nd module with this drafting order bug, after D-485), the "found. .."
         ellipsis typo, the orphan "M5" marker dropped, the 14 -> 15 re-count. (4) the test mirror doc: the PHANTOM
         probe labels dropped ("B1, B9-B11, B14, C1, C6a/C6b" — none exist in the probe; the sentence was stale), the
         14 -> 15 re-count + the repr coverage description; the documented rds\_checksum known-gap clause
         (probe-covered, left as-is) stays. (5) probe re-sync (the same-commit pin set): A8 the de-cross-ref docstring
         string, F1 307/14 -> 312/15 + the repr test pin — 52/52 green. Cell: test\_hlp\_indexes 14/0/0 -> 15/0/0.

D-489 | 2026-10-05 | The hlp\_plot source + test + mirror-doc pass, one commit (the user-approved plan incl. the
         unknown-format micro-test): (1) source 537 -> 533: the batch's main find — the corrupted GPL header ("...will
         be useful, but / WITHOUT ANY WARRANTY; or the implied warranty" vs the canonical "but WITHOUT ANY WARRANTY;
         without even the implied warranty": "without even" + "the" missing) restored; the 42 typed Args entries
         de-typed (the campaign record — the view counted 38, the regex found 42: the builder undercount); the
         docstrings to the reflow fixed point. (2) test 150 -> 166: the same corrupted GPL header restored + the
         approved test\_unknown\_format\_raises micro-test (the new TestHlpPlotSaveFigure class): save\_figure's
         unknown-format ValueError was documented in the API row but pinned by no test and no probe, the R-850 gap;
         11 -> 12 tests, 12/0/0, reflow fixed point. (3) the source mirror doc 121 -> 120 (back in budget): the 2 tail
         Integration bullets merged (the 4th repeated the 3rd), the rendering bullet compacted to 3 lines, the
         "11-test" -> "12-test" re-count + the ValueError pin in the Verified invariants. (4) the test mirror doc: "the
         18-check probe" -> 19-check (stale — the probe carries 19: A x5 + B x6 + C x7 with C4 doubled; the source doc
         already said 19), the "the pilot semantics" typo -> "the PlotConfig semantics" (the probe C section is the
         PlotConfig behaviour), the 11 -> 12 re-count + the new coverage row + the message golden. (5) probe: untouched
         (A1 pins the 7 names, not the line count; no docstring dependencies — verified before the pass). Cell:
         test\_hlp\_plot 11/0/0 -> 12/0/0.

D-490 | 2026-10-05 | The hlp\_su\_analysis source + test + mirror-doc + probe pass, one commit (the user-approved plan
         incl. the sparse micro-test): the biggest module of the campaign (1160 lines, 32 functions, 38 -> 39 tests).
         (1) source 1160 -> 1135: the 3 D-tags in the code comments de-tagged, the orphan R2 ruling tag in the load
         docstring reworded (the failure path), the 54 typed Args entries de-typed (the regex count; the view estimated
         59), the missing blank line before the TYPE\_CHECKING block, the docstrings to the reflow fixed point. (2) test
         806 -> 811: the ~20 D-tags + the 2 orphan R2 + the provenance narrative (the "moved here from the retired ..."
         sentences, the "rarity profile removed, dead in production" block) dropped from the module / class docstrings +
         the comments; the approved test\_sparse\_unique\_merge micro-test (the TestMarginalAccumulator): the
         UNIQUE-MERGE branch (n\_conf > 1e6) was documented but pinned by no test — a 14-cell pattern toy fset (n\_conf
         = 3^14), one chunk == two chunks + the independent hand count; 38 -> 39/0/0. The (R2, R2) of the tests is the
         toy fixture's pattern NAME, not a tag. (3) the source mirror doc 120 -> 111: the full de-tag (~30 D-xxx + the
         2 I-020 — the most saturated doc of the campaign), the Verified-invariants "OUTPUT-IDENTICAL against the
         superseded dict-merge" bullet (the pre/post campaign contrast) rewritten as the current-tense invariant, the
         stale "46 parameter + 4 return annotations" pin corrected to 52 + 32 (counted via ast over the 32 functions),
         "the 4 blocks" clarified to "the header + the 3 data blocks". (4) the test mirror doc 88 -> 80: the full de-tag
         + the narrative drop + the 38 -> 39 re-counts + the sparse coverage row. (5) probe: 40 checks — F4 RED
         since D-442 (the pre-existing debt, verified in git: the overview rows were underscore-escaped BEFORE D-442,
         which re-cut the golden in the unescaped form): the golden re-cut in place to the escaped form (name only, zero
         assertion change) — the probe goes from 1 mismatch to 0. Cell: test\_hlp\_su\_analysis 38/0/0 -> 39/0/0.

D-491 | 2026-10-05 | The hlp\_validate source + mirror-doc pass, one commit (the user-approved plan): the smallest
         module of the campaign (157 lines, 3 names) and the third hlp WITHOUT a test module by design (after
         hlp\_final\_log\_print): no test\_hlp\_validate, no test mirror doc, no overview row — all behaviour pinned by
         test\_wrk\_validate (9/0/0: the 3 worker tests + the 6 of the TestValidateModelUnit class) + the
         verify\_validate probe (17 checks, green) + the e2e; all four test names the doc cites exist in the worker
         suite. (1) source 157 -> 145: the 3 typed Args entries de-typed (the campaign minimum: rn, k, ctx), the formula
         block of the validate\_model docstring (the 4 standalone MAE / MSE / RMSE / ratio lines) converted to the
         single comma-joined sentence BEFORE the reflow (the reflow would have flattened it to mangled prose — the D-487
         bullet-to-paragraph genre), the docstrings to the reflow fixed point. (2) the source mirror doc 83 -> 83: the
         single D-tag ("the D-330 condensed form" -> "condensed"); the fidelity fully verified (the 7-key dict with the
         casts, the two f32 / f64 arithmetic paths, the dense-mapping formulas, the probe labels A1-A13 / C4 / C5 / D2,
         the unused rlmwf\_14 slot). (3) R-850 completeness: no gap — all 3 `__all__` names pinned. No test / probe /
         cell changes.

D-492 | 2026-10-05 | The hlp\_wmaps source + test + mirror-doc + probe pass, one commit (the user-approved plan): (1)
         source 341 -> 337: the 17 typed Args entries de-typed (the 8 of `__init__` at the 12-space indent + the 9 of
         the functions at 8), the class field list (the 8 "name (type) — description" entries) left intact by the reflow
         (the dry-run verified the SuTables precedent), the docstrings to the reflow fixed point. (2) test 368 -> 362:
         the 4 bare '# ' license-header lines stripped (line-exact), the import continuation alignment repaired (col 29
         to the canonical col 34). (3) the source mirror doc 84 -> 83: the 3 stale "15 tests" counts corrected to 16
         (the N-D test entered the suite without a doc update), the "module 338 lines (the D-331 format pass ...)" pin
         corrected to 337 + the campaign narrative rewritten current-tense, the sidecar/LZ4 order repaired (the 3rd
         occurrence: the code checks the sidecar before opening the LZ4 reader, the doc described the reverse). (4) the
         test mirror doc 34 -> 34: "4 classes / 15 tests" -> 16 + the missing test\_compute\_nd\_indexes\_matches\_1d
         coverage row (2 -> 3). (5) probe: the 8 re-pins (A1 338 -> 337, A5 L208 -> L205 moved by the pass, A10 L296 ->
         L295, A11 L309 -> L308, A12 L273 -> L272, C1 346 -> 362, C2 15 -> 16 tests with the 2-compute -> 3-compute
         split, C6 L207/L213 -> L223/L228) — 7 stale pre-pass (the files grew after the D-139/D-331 passes without a
         re-pin) + 1 moved by the pass: re-cut in place, same commit — the probe goes from 7 mismatches to 0. No cell
         changes (16/0/0).

D-493 | 2026-10-05 | The hlp\_zed source + test + mirror-doc + probe pass, one commit (the user-approved plan, S3
         included): (1) source 103 -> 129: the 4 bare '# ' license-header lines stripped (line-exact), the 2 E303 runs
         (3 blank lines) corrected to 2, and — the campaign's only docstring gap — the 4 missing docstrings added in the
         LMWMaps style: `__init__` (Initialize + the 3 Args), compute\_sha3\_256\_hash (Compute + Returns, the
         closures-explicit NOT-hashed note, no cache\_manager reference — ZED is a non-cache level), zed\_fun\_factory
         (+ Args logit\_clipping + the key-by-key Returns y2z / z2y), hlp\_zed\_compute (the first line normalized to
         Compute + Args ctx + Returns LMZed:). (2) test 157 -> 156: the 4 bare '# ' stripped, the import continuation
         alignment repaired (col 29 to 31), one E303 run, the over-indented LMZed(...) continuation (36 spaces to 18).
         (3) the source mirror doc 77 -> 77: the "clippling" typo, the stray space in stat\_model.logit\_clipping, the
         103 -> 129 line pin. (4) probe: the 15 re-pins (A1 103 -> 129, the A2-A9 line numbers, the A12/G9 trailing-ws
         pins from "header only (6,11,16,21)" to 0 lines — the pass stripped them, G1 157 -> 156, the G3 class shift,
         the F1 LMContext zed block L148-151 pre-pass-stale + the label trimmed): 1 mismatch pre-pass (the F1 shift), 0
         after. No cell changes (10/0/0, wrk 3/0/0).

D-494 | 2026-10-06 | The wrk\_analytics source + test + mirror-doc + probe pass (the worker cascade opens; the
         user-approved full plan + the 2 R-850 micro-tests): (1) source 89 -> 93: the 2 missing docstrings added (the
         worker cascade's first docstring gap — `_up` imperative + the WHAT, `_down` one-line; the hlp\_analytics house
         style: no Args section for the single ctx), the D-105/M2 tag stripped from the numbered comment (R-540), the 4
         bare '# ' license-header lines stripped, the import continuation alignment repaired (col 33 to 38), the factory
         first line normalized to the imperative "Return the ANALYTICS worker instance.", the two setUp comments'
         "15-level chain" -> "14-level chain" (the D-477 canon: CREATED is a sentinel, not an active level). (2) test
         785 -> 766: the unused `import os` dropped, the D-311 tag out of the TestEtaSquaredCrossLevel docstring
         (R-540), the header block aligned to the corpus canon (blank + 2 bare '#'), the R-570 light pass on the 16
         heavy docstrings (the class / method / helper docstrings compressed — the detail already lives in the mirror
         doc), and the 2 R-850 micro-tests pinning train\_dense\_rn (documented in the machine contract but
         runtime-unpinned: the new test\_train\_dense\_rn\_series — the ndarray of shape (199952,) with mean(|rn|) ==
         the train\_dense\_mae\_y golden, the independent cross-check — + the 4th clear assert in
         test\_down\_clears\_analytics\_attributes): 14 -> 15/0/0. (3) the source mirror doc 76 -> 74: the stale suite
         count (4-test / 2 classes / all DB-gated -> 15-test / 5 classes / 7 DB-gated + 8 NO-DB), the 17 -> 18 sibling
         factories, "step 15 of 18" -> of 19 (the 19-active-level canon), "the full 15-level chain" -> 14-level, the
         stale date-masked golden re-cut (94a4af7e... -> bda82098..., verified live — the probe C5 print), the "89
         lines." line-count drop. (4) the test mirror doc 67 -> 65: the full provenance purge (13 tag occurrences
         across D-298 / D-307 / D-308 / D-311 / D-316 + the "CHANGED with D-316" report tense — all rewritten in present
         tense), the garbled `(scipy 0.3.34, DYNAMIC_ARCH NO_AFFINITY)` corrected (it is the scipy-bundled
         OpenBLAS 0.3.34.0.0, verified via `numpy.show_config`) with the VM-move history dropped, "the 3 data rows" ->
         "the Loss data row (3 data cells)", the muddled "TWO non-cache levels' downstream data" header clarified. (5)
         probe: no re-pins (no behavior change, 36/36 green pre- and post-pass) — the hygiene edits only: the module
         docstring re-synced (the stale "step 13" -> step 15, "the 14th pipeline level" -> the 15th active level, "there
         are none — the bring-in has no test file" replaced — A11 pins the existence now) + the A2 label 12 -> 18
         siblings. Reflow last (the canonical fixed point on both files). Suite 1111 -> 1112/0/24 (the single cell move
         14 -> 15/0/0).

D-495 | 2026-10-06 | The wrk\_anova source + test + mirror-doc + probe pass (the second worker of the cascade; the
         user-approved full plan + the micro-assert): (1) source 61 -> 65: the 2 missing docstrings added (the cascade's
         second docstring gap — `_up` imperative + the WHAT with the enable guard and the 2 hlp\_anova calls, `_down`
         the pre-existing comment converted to the one-line docstring), the factory first line normalized to the
         imperative "Return the ANOVA worker instance.". (2) test 189 -> 179: the module docstring dropped (it nearly
         duplicated the class docstring verbatim; the canon majority of test files carries none — test\_hlp\_anova does,
         but it describes 5 classes), the header block aligned to the corpus canon (blank + 2 bare '#'), one
         micro-assert in test\_enable\_no\_op (the documented no-op consequence: the anova report dir is not created —
         before, only the log was pinned). (3) the source mirror doc 67 -> 67: the 6-tag provenance purge
         (D-310, D-311, D-315 x4 — all rewritten in present tense), the stale probe count 41 -> 42 (recounted with the
         build area present: 41 ok + F3). (4) the test mirror doc 37 -> 37: the orphan "The" re-wrap (otherwise clean —
         zero D-tags). (5) probe: one re-pin — F3 to the underscore-escaped overview forms (1 mismatch pre-pass, 0
         after) + the I-017 trimmed from the module header (R-550: no I-XXX in probe comments; R-580 allows I-ids in
         check labels only). (6) the runner: the "the I-017 T17;" reference trimmed from the wrk\_anova entry comment in
         `run_utests.sh`. Reflow last (the canonical fixed point on both files). No cell changes (7/0/0/0/0), suite flat
         1112/0/24.

D-496 | 2026-10-06 | The wrk\_client\_check source + test + mirror-doc pass (the third worker of the cascade; the
         user-approved full plan + the micro-test): (1) source 106 -> 109: the 2 missing docstrings added (the cascade's
         docstring gap — `_up` imperative + the WHAT: the file re-read, the Y-space residual recompute with the client's
         vectorized Evaluation Function, the comparison against the VALIDATE-published series within `client_check_tol`,
         the RuntimeError on a breach; `_down` the pre-existing comment converted to the docstring), the factory first
         line normalized to the imperative "Return the CLIENT\_CHECK worker instance.", the D-141/D-144 tags stripped
         from the numbered comments (the rationale kept), the import order swapped to the numpy-worker family (`typing`
         before `pydantic`, as wrk\_positions / wrk\_vld\_positions). (2) test 236 -> 237: the header's extra bare '#'
         dropped + the title normalized to the module-name form (the wrk\_client\_check unit tests), the R-570 light
         pass (the 7-line class docstring + the 4 heavy method docstrings compressed to 1-3 lines — the details live in
         the mirror test doc), the stale sidecar claim fixed in the `_write_model_file` comment (the sidecar record is
         RETIRED in the v2 format — the config dump + checksum are embedded in the model file; the writer opens a single
         file), one micro-test (R-850: "No context attribute is published" was documented in the source doc but unpinned
         — test\_publishes\_no\_context\_attribute: the ctx attribute set is unchanged by the up + down pair), cell 6 ->
         7/0/0/0/0. (3) the source mirror doc 76 -> 77: the header canon ("the 17th active level (step 17)" + the
         capital after the period), the 6-test -> 7-test count, the "no longer re-derives" report-tense fixed to "does
         not re-derive", the no-publishing pin added to the Verified-invariants bullet. (4) the test mirror doc 42 ->
         44: the same sidecar-claim fix in the header, "(the 17th active level)", the Coverage table 6 -> 7 with the new
         test description, the no-publishing contract added to Goldens pinned. Reflow last (the canonical fixed point on
         both files). Suite 1112 -> 1113/0/24 (the single cell move 6 -> 7/0/0).

D-497 | 2026-10-06 | The wrk\_config source + test + mirror-doc + probe pass (the fourth worker of the cascade; the
         user-approved full plan + the micro-test): (1) source 110 -> 128: the 5 missing docstrings — the cascade's
         biggest docstring gap so far (`_up`, `_down` + the 3 private helpers `_load`, `_validate`,
         `_validate_base_dir`, all imperative + the WHAT), the factory first line normalized to the imperative "Return
         the CONFIG worker instance.", the unused `Callable` import dropped (from
         `from typing import TYPE_CHECKING, Callable` — verified unused), the 5 E301 fixes (single blank -> 2 between
         the top-level defs; the 3-blank runs around `__all__` kept — the house style, as wrk\_validate /
         wrk\_positions). (2) test 329 -> 342: the header block + the title normalized ("How to use the unit tests
         wrk\_config module." -> "How to run the wrk\_config unit tests.", the corpus wrk\_X form), the 6
         trailing-whitespace blank lines dropped by the reflow, the test\_base\_dir\_missing docstring compressed (6
         lines -> 3, the verify\_wrk\_config.py D1-probe provenance dropped), one R-850 micro-test —
         test\_base\_dir\_from\_json\_is\_a\_file\_raises\_error: the worker's NotADirectoryError gate was documented
         ("the three gates") but pinned only via the facade's `__init__` (the base\_dir\_override path,
         `_check_base_dir_override` in logistic\_model.py L84-92); the JSON-base\_dir-file case (no override) is
         reachable but was uncovered — the new test on the payload idiom; cell 13 -> 14/0/0/0/0. (3) the source mirror
         doc 69 -> 70: the header canon ("the 1st active level (step 1), the first non-sentinel"), the stale fixture
         path fixed (`src/reversi/test/data/rlm\_00.json` — absent — -> `test/reversi/data/rlm\_00.json`), 13 -> 14
         tests, the failure-behaviour bullet distinguishing the a-file override (the facade) from the a-file from the
         JSON (the worker's own gate). (4) the test mirror doc 39 -> 39: the stale "ec=10" -> "ec=20" (the payload
         carries 20; the schema is ge=0 le=60, required), the Coverage row (3 -> 4, the D1 provenance dropped, both
         a-file cases), 13 -> 14 in the header. (5) the probe: the header docstring's stale sidecar claim fixed ("moved
         to the SAVE sidecar pair" -> "EMBEDDED in the v2 model file at SAVE" — the sidecar is RETIRED); zero re-pins
         (15/15 pre- and post-pass). Reflow last (the canonical fixed point on both files). Suite 1113 -> 1114/0/24 (the
         single cell move 13 -> 14/0/0).

D-498 | 2026-10-06 | The wrk\_design\_matrix source + test + mirror-doc + probe pass (a side pass — DESIGN\_MTR is not
         in the 13-pair cascade list; the 9 remaining pairs stay queued): (1) source 80 -> 87: the 2 missing docstrings
         added (`_up` imperative + the WHAT: the 4-step load-or-compute of the design matrix, the bare-X + data-checksum
         publish; `_down` one-line), the factory first line normalized to the imperative "Return the DESIGN\_MTR worker
         instance.", the 2 101-char log lines split over 2 physical lines (the R-520 ceiling 100; the message text
         unchanged — nothing pins those lines). (2) test 226 -> 218: the header's extra bare '#' dropped, the unused
         `import os` dropped (zero uses — verified), the reflow re-joins the comment blocks. (3) the source mirror doc
         70 -> 69: the header canon ("the 8th active level (step 8)" — the redundant CREATED -> ... chain dropped, it
         lives in the Integration bullet), the garbled quote fix ("Design Matrix computed/loaded. Shape:. .." -> the two
         real log messages re-quoted) + the "ctx. design\_matrix\_checksum" typo, the "the 80-line file" line-count
         claim dropped, the "+ import os" dropped from the C-tier bullet. (4) the test mirror doc: clean — zero fixes
         (no D-tags; the counts + coverage + goldens all verified against the file). (5) the probe: 5 shape-only re-pins
         — B1 80 -> 87, C1 226 -> 218, C3 (the import-os clause dropped + clause 2 re-pinned to the reflow's re-wrapped
         header text — the reflow re-joined the -1- comment block and split the pinned string), B3 (the factory line
         indices w[76]/w[77] -> w[83]/w[84] in the 87-line file), C13/C14 (the label line-number re-sync; the conditions
         were already substring/count-based and live). 0 mismatch pre- and post-pass; zero behavior re-pins (the D/F
         tiers untouched). No R-850 micro-test: the one documented-but-unpinned-at-worker behavior ("use\_cache=False:
         always recompute but still warm the cache file") is the cache\_manager's — pinned at the owning level
         (test\_cache\_manager.test\_step0\_not\_allowed\_forces\_computation: mock\_compute + mock\_store each asserted
         once). Reflow last (the canonical fixed point on both files). No cell change (3/0/0/0/0), suite flat 1114/0/24.

D-499 | 2026-10-07 | The wrk\_features source + test + mirror-doc + probe pass (the cascade's heaviest hygiene pass so
         far, but semantically healthy — probe 0 mismatch at baseline, the doc faithful, the suite consistent): (1)
         source 125 -> 155: the 6 missing docstrings added (`_up` / `_down` / `_load_features` / `_load_intercept` /
         `_load_patterns` / `_load_mobility` — the cascade's biggest docstring gap, more than wrk\_config's 5), the
         factory first line normalized to the imperative "Return the FEATURES worker instance.", the 9 100+ log lines
         split (all log\_event, max 132; the 4 longest via f-string concatenation so the messages stay byte-identical —
         A7 searches substrings in the surviving f-string, B8a-c pin the runtime output), the 5 E301 single-blank fixes.
         (2) test 202 -> 188: the header's extra bare '#' dropped, the unused `import os` dropped (the probe does NOT
         pin it, unlike design\_matrix's C3 — no re-pin needed), the 8-line guard class docstring compressed to 2 lines
         with the "probe\_rules.md §4: converted from the B11 probe" provenance dropped (R-550), the reflow re-joins the
         comment blocks. (3) the source mirror doc 77 -> 77: the header canon ("the 2nd active level (step 2)"), the
         125-line and 202-line line-count claims dropped; the verified claims left intact (the 41-check probe, the
         test\_mobility mset-hash cross-ref, SU\_ANALYSIS as first consumer via hlp\_su\_analysis's
         ctx.feature\_set.hash). (4) the test mirror doc: clean — zero fixes. (5) the probe: only 2 shape re-pins (A1
         125 -> 155, C1 202 -> 188) — 0 mismatch on the first post-pass run; all other pins survived (A6/A7/C6/C9/C10
         substrings, the B-tier runtime unchanged). No R-850 micro-test: the documented behaviors without suite pins
         (the down-cleared feature set, the no-cache-file level boundary, the second-run identity) are all
         runtime-pinned by the probe (B12, B10, B13a-c) — division of labor documented, as in D-498. Reflow last (the
         canonical fixed point on both files; the 4 code lines still over 100 were fixed by hand via the f-string
         concatenation — the reflow does not touch code). No cell change (3/0/0/0/0), suite flat 1114/0/24.

D-500 | 2026-10-07 | The wrk\_final\_log\_print source + test + mirror-doc pass (4 files — the probe untouched, zero
         re-pins: it has no title/line-count/comment pins, verified check by check): (1) source 64 -> 63: the 2 missing
         docstrings added (`_up` / `_down` — the comment blocks that stood in for docstrings were replaced, the gate +
         no-unlink semantics now in the docstrings), the factory first line normalized to the imperative. (2) test
         210 -> 184: the header canon (3 bare '#' with no blank after the license -> 1 bare '#' + blank) + the title
         canon (the stray 'module' word dropped — the first of that genre; the probe does not pin the title), the
         10-line module docstring DROPPED (it duplicated the class docstrings and carried the 'D-322' provenance —
         R-540), the 4 docstring compressions (the e2e class 11 -> 2 with the 'D-322 fix' tag out and the checksum WHY
         kept, class 1 4 -> 2, `_MockCtx` 5 -> 2, `_make_ctx` 6 -> 2), the R-850 micro-pin in `test_down_no_op` (the
         file exists AFTER the `_down` — the 'the \_down does not unlink it' documented behavior was pinned nowhere: the
         test only asserted the log, the probe has no down on its synthetic machine; consistent with the a/b/c rule —
         file existence lives in the suite). (3) the source mirror doc 64 -> 65: the header canon (the 19th active
         level, step 19), the STALE fix — 'log\_file\_name set after CONFIG' described the pre-fix behavior (the e2e
         sets it in the config from the start via the tmp fixture copy; a post-CONFIG mutation desyncs the config
         checksum fingerprinted at CONFIG), the Italian spec quote dropped (redundant with the English clause). (4) the
         test mirror doc 45 -> 45: the D-322 x3 purge (the tag out, the WHY kept). (5) the probe: 0 mismatch pre- and
         post-pass, zero re-pins. Reflow last (canonical on both files; the 4 lines over 100 it re-joins in the test are
         its own fixed point, all under the 120 ceiling). No cell change (6/0/0/0/0 — the micro-pin is an assert in an
         existing test), suite flat 1114/0/24.

D-501 | 2026-10-07 | The wrk\_generate source + test + mirror-doc pass (3 files — the probe and the test doc untouched):
         (1) source 78 -> 85: the 3 missing docstrings added (`_up` / `_down` / and the factory — the first
         docstring-LESS factory of the cascade, all the others had at least the 'Factory function that returns...'
         line), the 102-char log line split over 2 physical lines (the message unchanged). (2) test 186 -> 181: the
         header's extra bare '#' dropped, the unused `import os` dropped (the probe does not pin it), the E261
         inline-comment spacing fixed (1 -> 2 spaces before the comment on the rlm2 OPTIMIZE move), the reflow re-joins
         the comment blocks. (3) the source mirror doc 56 -> 56: the header canon (the 12th active level, step 12 — the
         level phrase was missing entirely). The suspicious 'The 6th cache\_manager consumer' claim was VERIFIED TRUE by
         an empirical grep over all 19 workers: exactly 7 cache\_manager\_load\_or\_compute consumers in pipeline order
         (SU\_ANALYSIS, POSITIONS, INDEXES, WMAPS, DESIGN\_MTR, GENERATE, VLD\_POSITIONS) — ZED/GRADIENT/OPTIMIZE do not
         use it (custom checkpoints), consistent with the design\_matrix doc's 'FIFTH consumer' claim. (4) the test
         mirror doc: clean — zero fixes. No R-850 micro-test: this is the first cascade worker with the `_down` scope
         pinned IN THE SUITE (test\_down\_clears\_generate\_attributes — move\_to\_step(11), both fields None);
         use\_cache=False is the cache\_manager's territory (pinned there), the duck-typed checksum identity is pinned
         in test 1. (5) the probe: 0 mismatch pre- and post-pass, zero re-pins (no line-count/title/import pins — as
         in D-500). Reflow last (canonical on both files; the first-drafted 101/103-char docstring line was re-wrapped
         to the fitting form). No cell change (3/0/0/0/0), suite flat 1114/0/24.

D-502 | 2026-10-07 | The wrk\_gradient source + test + mirror-doc + probe pass: (1) source 65 -> 72: the 2 missing
         docstrings added (`_up` / `_down` — the by-design comment 'GRADIENT building is a closure generation, very
         fast. No cache needed.' KEPT, the probe B tier pins it), the factory first line normalized to the imperative,
         the 104-char `hlp_gradient_compute(...)` call split over 2 lines, the E301 single-blank fix. (2) test 184 ->
         184: the header's extra bare '#' dropped, the unused `import os` dropped, the TestGradientFlagWiring class
         docstring compressed (4 -> 2), and the R-850 micro-pin in `test_generate_gradient` (the variant log line
         `Gradient function generated (high_performance: False).` — documented in the source doc as 'the log line names
         the built variant' but runtime-pinned nowhere). The micro-pin's first attempt on mock\_stdout FAILED: this
         suite runs at Verbosity.LOW, and the console verbosity gate filters the INFO lines — the corrected pin reads
         the machine's event buffer (`sm.logs`), which the StateMachine fills on every `log_event` independently of the
         gate. (3) the source mirror doc 68 -> 68: the header canon (the 10th active level, step 10), the 4 stale
         line-count claims dropped ('the 65-line file', 'the 182-line file', 'the 272-line file', 'all 8 worker files'),
         and the hlp-suite test count corrected 14 -> 15 (verified live — test\_hlp\_gradient.py has 3 classes / 15
         tests). (4) the test mirror doc: clean — zero fixes. (5) the probe: 5 re-pins — B1 (line count 65 -> 72), B5
         (the 2-line split call), B9 (the factory docstring — the probe pinned the DEVIANT 'Factory function that
         returns...' form, now the normalized imperative), C2 (clause 2 to the reflow's re-wrapped header text), C3 (the
         import-os clause dropped) — 0 mismatch on the post-pass run. Reflow last (canonical on both files). No cell
         change (4/0/0/0/0 — the micro-pin is an assert in an existing test), suite flat 1114/0/24.

D-503 | 2026-10-07 | The wrk\_indexes source + test + mirror-doc + probe pass: (1) source 80 -> 86: the 2 missing
         docstrings added (`_up` / `_down`), the factory first line normalized to the imperative, the 2 long lines split
         (the 106-char `validate_fn` line split BEFORE the call so the probe D5-pinned substring
         `hlp_indexes_is_cache_consistent(ctx, cached_hlp_indexes)` stays contiguous on one physical line; the 102-char
         checksum log line split with the message unchanged), and the unused `LMIndexes` import dropped (the first dead
         NAME import of the cascade — the worker only uses the 4 hlp functions, never the class; the probe does not pin
         the import). (2) test 155 -> 150: the header's extra bare '#' dropped, the unused `import os` dropped, reflow.
         No micro-test: the `_down` clearing is documented as probe-only in the test mirror doc (the C7 division). (3)
         the source mirror doc 60 -> 60: the header canon (the 5th active level, step 5 — the redundant worker chain
         dropped), the '80-line file' claim dropped, and the fidelity fix of the spurious space in the quoted code
         (`hlp_indexes_compute (ctx)` -> `hlp_indexes_compute(ctx)`). The 'THIRD `cache_manager` consumer (after
         `SU_ANALYSIS` and POSITIONS)' claim verified coherent with the empirical D-501 count. (4) the test mirror doc:
         clean — zero fixes. (5) the probe (verify\_hlp\_indexes.py, the worker's D/E tiers): 2 line-count-only re-pins
         — D1 (80 -> 86) and E1 (155 -> 150) — 0 mismatch on the post-pass run. Reflow last (canonical on both files).
         No cell change (2/0/0/0/0), suite flat 1114/0/24.

D-504 | 2026-10-07 | The wrk\_optimize source + test + mirror-docs + probe pass (the largest worker of the cascade, 192
         lines): (1) source 192 -> 197: the 2 missing docstrings added (`_up` / `_down`), the factory first line
         normalized to the imperative, the E261 fix (the 1-space `return # Skip optimization entirely!` -> 2 spaces),
         and the 2 E301 single-blank fixes (before `_down` and before the `@validate_call` decorator). RULE RE-READING
         (R-520): the file's 5 code lines at 104-115 chars were left UNsplit — 'Code has no preferred wrap: an
         expression split across lines that fits on one line within the 120 ceiling is written on one line'; the
         100-char preference applies to PROSE (docstrings + comments) only. The earlier cascade passes that split
         100-108-char code lines were over-strict; this pass applies the rule as written (those commits stay valid:
         legal Python, byte-identical messages, re-pinned probes). (2) test 175 -> 170: the header's extra bare '#'
         dropped, the unused `import os` dropped, reflow. No micro-test: the 6 decision paths carry a documented
         division of labor (the suite: the completed path + the `_down` scope; the probe H4-H8 + H6b: the rest),
         verified check-by-check against the H tier. (3) the source mirror doc 75 -> 75: the header canon (the 11th
         active level, step 11), the 2 line-count claims dropped, the stale 'all 18 worker factories' corrected to 19
         (19 wrk\_\*.py files counted — CREATED is built-in, no factory), the base-dir enumeration corrected 'the 4
         rlmwf\_ cache pairs (04/05/07/08)' -> 'the 5 rlmwf\_ cache pairs (03/04/05/07/08)' (rlmwf\_03\_SU\_ANALYSIS.dat
         exists — verified in its mirror doc), and the fidelity fix of the spurious space in the quoted code
         (`optimization. checkpoint_file` -> `ctx.cfg.base_dir / opt_cfg.checkpoint_file`, quoting the actual code). (4)
         the test mirror doc 36 -> 37: the Conventions chain corrected — 'the setUp's GRADIENT move runs FEATURES →
         POSITIONS → ...' was verified against the live pipeline order (logistic\_model.py) and was missing SU\_ANALYSIS
         (step 3) and ANOVA (step 6); now the full chain CONFIG → ... → GRADIENT. (5) the probe: 3 re-pins — B1 (192 ->
         197), D1 (175 -> 170), and D4 (the `import os` clause dropped AND the false 'os/Path now used' claim corrected
         to 'Path now used' — the probe pinned the dead import as if it were used; first probe-fidelity fix of the
         cascade) — 0 mismatch on the post-pass run. Reflow last (canonical on both files; it re-joined 4 comment
         blocks, the B10-pinned substring intact). No cell change (3/0/0/0/0), suite flat 1114/0/24.

D-505 | 2026-10-07 | The wrk\_wmaps source + test + mirror-docs + probe pass: (1) source 91 -> 99: the 2 missing
         docstrings added (`_up` / `_down`), the factory first line normalized to the imperative, and the 138-char log
         line (the only cascade line OVER the 120 ceiling — R-520) split over 3 lines with the message in 2 adjacent
         string literals (byte-identical; the probe does not pin that string). (2) test 315 -> 319: the header's extra
         bare '#' dropped, the unused `import os` dropped, the E261 fix (the 1-space inline comment in test 2), and the
         R-850 micro-test `test_down_clears_wmaps` — the first cascade worker whose `_down` was runtime-pinned NOWHERE
         (the probe B6 pins it at source-shape only, and verify\_wmaps has no live-DB tier) while the source doc
         documents the 7-attribute clearing. First run FAILED: `move_to_step(6)` lands on ANOVA (level 6), not INDEXES
         (level 5) — the same pipeline-order lesson as the D-504 test-doc chain fix; the worker-name pin corrected to
         ANOVA. (3) the source mirror doc 66 -> 66: the header canon (the 7th active level, step 7), the spurious-space
         fidelity fix (`hlp_wmaps_is_cache_consistent (ctx, cached)`), the '91-line file' claim dropped, the DUPLICATE
         `__all__ = ['wrk_wmaps']` mention in one bullet dropped, the 3 -> 4 test counts (the round-trip bullet gains
         the micro-test), and 'Consumes the hlp\_wmaps module (all 5 public names)' corrected to '(the 4 hlp functions —
         the LMWMaps class itself is not imported)' (the public names list has 5 — verified — but the worker imports 4).
         (4) the test mirror doc 35 -> 35: the 3 -> 4 test counts, the coverage row gains `test_down_clears_wmaps`
         (named as the R-850 runtime pin), and '3/0/3 under the gate' -> '4/0/4'. (5) the probe: 11 re-pins — the
         cascade record — B1 (91 -> 99), B3 (factory 87/88 -> 95/96), B4 (`load_fn` 55 -> 60), B6 (checksum 84 -> 92),
         D1 (315 -> 319), D2 (3 -> 4 tests), D3 (gate indices 73/175 -> 69/181), D4 (the pinned dead `import os`
         converted to a negative check, the false 'for the gate' claim dropped), D5 (81/182 -> 76/187), D6 (83/184 ->
         78/189), D7 (57 -> 54) — the probe's absolute-index style made this the heaviest re-pin of the cascade; all
         indices measured after the reflow. Cell 3/0/0 -> 4/0/0 (the first cell change of the cascade — the pre-commit
         overview auditor caught the stale 3/0/0 cell before the commit), suite 1115/0/24. Reflow last (canonical on
         both files).

D-506 | 2026-10-07 | The wrk\_plot source + test + mirror-docs pass (side pass): (1) source 130 -> 134: the 2 missing
         docstrings added (`_up` / `_down`), the factory first line normalized to the imperative, the BROKEN LICENSE
         HEADER restored ("WITHOUT ANY WARRANTY; or the implied warranty of" — the "without even" of the house GPL text
         was missing; the first header repair of the cascade), and the stale header comment ("the last active one" —
         PLOT is the 18th level, FINAL\_LOG\_PRINT is 19th). (2) test 306 -> 299: the header's 3 bare '#' collapsed to
         the house shape and the deviant title ("How to run the PLOT worker unit tests.") normalized to the wrk\_plot
         canon; the R-760 idiom conversion — `tempfile.mkdtemp` + `shutil.rmtree` to `TemporaryDirectory` with the
         defensive `getattr` cleanup (the `shutil` import became dead and was dropped). The parity rendering golden is
         the sentry: the mkdtemp name varies per run while the pinned sha3 is stable, so the path is provably NOT in the
         PNG bytes — the conversion is byte-neutral, confirmed by the suite passing. The 9-line class docstring
         compressed to 4. (3) the source mirror doc 84 -> 85: the header canon (the 18th active level, step 18 — the
         stale "the LAST active level" claim dropped), the FALSE TOP-20 extreme-outlier report claim dropped (PLOT logs
         only its five own lines — verified on the source; the TOP-20 report is CLIENT\_CHECK's behavior), the probe
         count corrected 19 -> 18 checks (counted: A1-5 + B1-6 + C1-7; the test doc already said 18), the spurious-space
         fix after the opening paren in the `hlp_plot` quote, the "the terminal level" stale claim corrected (the last
         artifact-producing level; FINAL\_LOG\_PRINT follows), and the rlmwf no-cache slot enumeration completed (/19
         added). (4) the test mirror doc 49 -> 49: the tmp-file idiom description updated to the TemporaryDirectory
         shape. (5) the probe: ZERO re-pins — all 18 checks live at the hlp\_plot level (the builders, the pdf/png pair,
         the determinism, the jitter/KDE/EGV guards, the PlotConfig defaults); none touches the worker or the test file.
         Reflow last (canonical on both files). No cell change (9/0/0/0/0), suite flat 1115/0/24.

D-507 | 2026-10-07 | The wrk\_positions source + test + mirror-doc + probe pass (side pass): (1) source 216 -> 225: the
         2 missing docstrings added (`_up` / `_down`), the factory first line normalized to the imperative, the 9
         M3-leftover trailing-ws lines swept (the 3 import-block trailing spaces + the 6 ws-only lines of the
         `is_cache_consistent` body; the probe A6 documented them as “stays as in the original file” — the M3 scope —
         and its comment was updated to the swept state; the A6 structural pins, the pinned `return` of `_up` + the 2
         blank lines before `_down`, are untouched and still green), the 5 over-120 code lines split byte-identically
         (the L75 cache-hit line, the L90 stats line, the L170 DEBUG connection line, the L204/L208 kept/removed
         duplicate lines). The L170 was the teaching moment: a f-string EXPRESSION cannot span adjacent string literals
         (each f-string token parses on its own) — the first attempt was a SyntaxError caught by the AST check; the fix
         is a plain + f + plain three-literal split around the complete tuple expression. The 2 D-143 tags dropped (the
         `_up` comment + the `extract_and_prepare` docstring; the WHY kept, the tag gone). The EOF trailing blank
         removed. (2) test 311 -> 307: the header's 2 bare '#' collapsed to 1 (the title was already canon), the 2 dead
         imports dropped (`import os`, `import numpy as np` — never referenced), the stale comment ("the slot is 03")
         corrected to 04 (the file is `rlmwf_04_POSITIONS.dat`; the test doc said 04), the 8-line
         `TestIsCacheConsistent` class docstring compressed to 4 — the `verify_wrk_positions.py` D4a-g label does
         nonexistent in that probe (D tier: D2/D3/D3b), so the provenance was reworded as a plain division-of-labor. (3)
         the source mirror doc 97 -> 99: the header canon (the 4th active level, step 4), the D-282 tag dropped (the
         `ec` / `empty_count` fact kept), and the A7/A8/D8 cross-probe references disambiguated to
         verify\_vld\_positions (they are checks of the VLD probe, not of the 21-check probe here). (4) R-850: no
         micro-test — the `_down` runtime IS pinned by the probe A3 (the 4-attribute reset) and the 12-test suite is
         comprehensive (the round-trip, the 7 in-memory semantics, the 3 policy tests). (5) the probe: zero re-pins (no
         line-count, factory, or import pins; all 21 checks still pass). Reflow last (canonical on both files). No cell
         change (12/0/0/0/0), suite flat 1115/0/24.

D-508 | 2026-10-07 | The wrk\_save source + mirror-doc pass (side pass; the third of the then-remaining three worker
         pairs): (1) source 66 -> 72: the 2 missing docstrings added (`_up` / `_down`), the factory first line
         normalized to the imperative, the 2x E301 fixed (a single blank line between the top-level defs -> 2), and
         the D-144 campaign tag dropped from the provenance comment (the WHY kept; the D-144 markers in the probe are
         `model_weights` label markers, legitimate — R-540 does not cover probes). (2) The structural finding: the
         module has NO dedicated test file — neither test\_wrk\_save.py nor its mirror doc exists (verified: no suite
         file mentions it, the overview has no test row, the suite audit has no cell). The coverage is by design: the
         18-check verify\_save probe (the only wrk\_save pins are A1-A3: the factory, no pathlib, 0 ws-lines) + the
         9-test full-chain suite (2 ungated + 3 v2 micro + 4 DB-gated, A2050 VLONG-gated). R-850 exempt: the full chain
         pins the `_down` artifact-persistence semantics (the base-dir listing after a chain), documented as the
         division of labor in the source doc. (3) the source mirror doc 91 -> 92: the '66 lines.' line-count claim
         dropped, the stale '19-worker chain runs to step 18 (move\_to\_last, PLOT)' line corrected to step 19
         (`FINAL_LOG_PRINT` — the test asserts `current_step == 19`), the non-cache slot enumeration completed (/19
         added), and the header canon. (4) the fidelity verifications that PASSED: the 'exactly 6 cache hits' is correct
         because SU\_ANALYSIS is opt-in (the SuAnalysisConfig enable default is FALSE, the rlm\_04 fixture has no
         su\_analysis key — no rlmwf\_03 materializes; the 6 files are 04/05/07/08/12/13), the 18-check / 9-test counts,
         the provenance-inside-the-model-file, the persistence subset. (5) the probe: zero re-pins, all 18 checks green
         post-pass. The reflow was a no-op (already canonical — my D-144 comment rewrite was pre-joined). No cell change
         (there is no wrk\_save cell), suite flat 1115/0/24 (the full-chain 9/0/1: the skip is the VLONG-gated A2050
         test). Two worker pairs now remain: wrk\_zed, wrk\_vld\_positions.

D-509 | 2026-10-07 | The wrk\_su\_analysis source + test + mirror-docs pass (side pass): (1) source 90 -> 97: the 2
         missing docstrings added (`_up` / `_down`), the factory docstring normalized (it was the deviant 2-line wrapped
         form — the 67-char one-line fit, the wrap was a leftover), and the `__all__` block brought from 2 to 3 blank
         lines (the corpus style, as in every other worker). (2) test 301 -> 274: the header's 2 bare '#' collapsed to 1
         + the title's 'module' word dropped (the wrk\_final\_log\_print deviation family), the 10-line MODULE docstring
         dropped (redundant with the 'How to run' header block; no corpus test file has a module docstring), the
         `_make_ctx` 7-line and the VLONG scale-class 9-line docstrings compressed to 4. (3) the source mirror doc 62 ->
         63: the header canon (the 3rd active level, step 3), the 4 D-tag references dropped (D-288 x3 + D-291 x2 — the
         binio/signature facts kept, the tags gone), the 'the worker is ~100 lines' claim dropped (the cascade praxis).
         (4) the test mirror doc 41 -> 41: the runner claim corrected — the suite sits between the hlp\_su\_analysis
         logic suite and the POSITIONS worker test (the doc cited the `hlp_anova` module; verified against
         `run_utests.sh`). (5) the cleanest module of the cascade: 0 ws lines, 0 long lines, all imports used, the suite
         complete (10 tests: the 9 no-DB mock-ctx + the VLONG 1e7; the down is pinned by `test_down_clears`, so R-850 is
         exempt — no micro-test). (6) the probe: zero re-pins (44 checks, 0 mismatches post-pass; the worker pins
         A1/A4/A5 are untouched by these edits). Reflow last (canonical on both files). No cell change (10/0/1/1/0),
         suite flat 1115/0/24.

D-510 | 2026-10-07 | The wrk\_validate source + test + mirror-docs pass (side pass): (1) source 118 -> 121: the 2
         missing docstrings added (`_up` / `_down`), the factory first line normalized to the imperative, and the
         2 D-150 tags dropped from the source (the `_outlier_records` docstring — 'the D-150 report's data' — and the
         report comment — a third D-150 sat in the test doc's coverage row and was dropped there; the outlier-report
         fact kept everywhere, the tags gone). (2) test 345 -> 332: the header's 2 bare '#' collapsed to 1, the dead
         `import os` dropped, and the module's headline finding — the `TestLMWorkerValidate` class docstring said 'the
         `rlmwf_12` slot stays unused' when VALIDATE's slot is 14 (12 is GENERATE's); corrected and the 6-line docstring
         compressed to 3. The 2 heavy provenance docstrings compressed (the 11-line outlier report: the 'MOVED to
         VALIDATE' annotation gone, 11 -> 5; the 9-line zero-guard: the state-machine line-ref gone, 9 -> 5); the
         hand-computed case's derivation docstring left as-is (it records the exact-value golden). (3) the source mirror
         doc 71 -> 72: the header canon (the 14th active level, step 14) and the orphan claim dropped — 'the docstring
         indicator is 1.253' (no 1.253 exists in any artifact; the live pin is 1.27 and the real ratio 15.463/12.162
         = 1.2715). The division-of-labor claim in the test doc was VERIFIED faithful to the current probe (the C tier
         retains exactly C4 + C5 for the live-DB tier; D2 is a no-DB D-tier check; B1-B3 / C1-C3 / D1 / D3 all migrated
         to the test file — mapped the probe's 4 tiers) — no change needed. The 6 cache-hits count is consistent with
         the D-508 SU opt-in finding. (4) the test mirror doc 37 -> 37: the D-150 tag dropped from the coverage row. (5)
         the probe: zero re-pins (18 checks, all green post-pass; A2 pins the decorator+def adjacency and A9 the 4
         assignment counts — both untouched). R-850 exempt: `test_down_clears_vld_metrics` pins the down (9-test suite.
         Reflow last (canonical on both files). No cell change (9/0/0/0/0), suite flat 1115/0/24.

D-511 | 2026-10-07 | The wrk\_vld\_positions source + test + mirror-doc + probe pass (the second of the last two worker
         pairs closes; only wrk\_zed remains): (1) source 130 -> 141: the 2 missing docstrings added (`_up` / `_down`),
         the factory first line normalized to the imperative, the 5 over-120 code lines split byte-identically (L70 via
         the PARENTHESESIZED LAMBDA BODY so the A8 pinned call text `is_cache_consistent`(ctx, `cached_vld_rds`,
         bid=..., status=...) stays intact; L80 195, L95 180, L112 229, L118 135), the single import-block ws line
         swept, and the 4 D-tag refs dropped from the comments (D-282 + D-100 M1 in the ec-root note block; D-143
         twice). (2) test 318 -> 312: the header's 2 bare '#' collapsed to 1, the 2 dead imports dropped (os + numpy as
         np — nptest is used, np is not), and the thirteenth wrong cache slot of the cascade (after wrk\_validate's
         12 -> 14): the comment said 'the `rlmwf_11` slot' but the file is `rlmwf_13`; corrected. The 2 class docstrings
         compressed (the 'probe\_rules.md §4: converted from the D2-D7 probe' provenance gone, the division-of-labor
         kept) and the 2 over-200 assertIn lines split into two adjacent literals (byte-identical messages). (3) the
         source mirror doc 93 -> 93: the header canon (the 13th active level, step 13), the D-282 tag dropped, the PROBE
         COUNT CORRECTED 18 -> 17 (measured: A1-A8 + B4/B5 + C3a-d + C4 + D1/D8), the stale 'import-block trailing ws
         stays, as in wrk\_positions' convention line dropped (the line is swept here and wrk\_positions was swept
         by D-507), and the 2 spurious spaces fixed. (4) the test mirror doc needed NO fix (the most accurate of the
         cascade: 11 tests matching the cell, the D2-D7 = the 6 migrated override branches, 'retains only C3a-C3d + C4
         for the live-DB tier' verified against the real probe). (5) ONE probe re-pin — A6: it pinned exactly 1
         remaining code-ws line (the import line, 'the M3 house scope, as in lm\_worker\_positions' — that cited file is
         already clean since D-507); re-pinned to zero (`_vld_ws` == []) with the label updated. Zero other re-pins
         (A1-A5/A7/A8 untouched; no line-count or factory-docstring pins; the C tier pins the log messages at runtime —
         the splits are byte-identical). R-850 exempt: `test_down_clears_vld_positions_attributes` pins the down in the
         11-test suite. Reflow last (canonical on both files). No cell change (11/0/0/0/0), suite flat 1115/0/24.

D-512 | 2026-10-07 | The wrk\_zed source + test + mirror-doc + probe pass (the LAST worker pair — the worker cascade is
         now COMPLETE, every worker module passed): (1) source 73 -> 75: the 2 missing docstrings added (one-line `_up`
         / `_down`), the factory first line normalized to the imperative; the cleanest source of the cascade after
         wrk\_su\_analysis (all imports used, zero ws, zero long lines, no D-tags, no bare returns). (2) test 165 ->
         160: the header's 2 bare '#' collapsed to 1, the dead `import os` dropped, and the stale comment corrected —
         'Pin the \_down clearing (live-verified, probe D12)': D12 was DELETED from the probe at D-106 (the probe's own
         note says 'D12 \_down live … deleted at D-106 … test\_down\_clears\_zed\_attributes pins exactly this scope');
         the reference now reads 'the live-verified D12 scope, now in the suite'. (3) the source mirror doc 62 -> 62:
         the header canon (the 9th active level, step 9), the line-count claims updated to the re-pinned counts (73 ->
         75, 165 -> 160), the spurious space in stat\_model.logit\_clipping fixed. (4) the test mirror doc needed NO fix
         (2 classes / 3 tests matching the cell, the goldens, the conventions, no line-count claims). (5) the heaviest
         probe re-pin of the cascade (verify\_zed.py, 51 checks — the strictest probe): dense absolute index pins on
         BOTH files. B1 73 -> 75; B3-B7 index re-pins (+1/+2 for the 2 docstrings, labels updated); C1 165 -> 160; C2-C9
         all ~20 absolute tc[i] indices RECOMPUTED PROGRAMMATICALLY on the post-edit file (the bare-# + the os drop +
         the reflow comment rejoins — the reflow also rejoined the header comment into 2 lines, C4 rebuilt accordingly).
         The interesting case: C3 pinned the PRESENCE of the dead `import os` as a structural fact ('T1 DONE: import os
         (L46) …') — re-pinned as an ABSENCE pin ('NO os import (dead, dropped in the cascade pass)'), matching the
         check's declared no-dead-imports purpose. The probe's internal note ('the 4 assertIsNone at L157-160') updated
         to L153-156. The A/F/G tiers untouched (the hlp\_zed + test\_hlp\_zed files are not touched). R-850 exempt:
         test\_down\_clears\_zed\_attributes pins the down (4 attrs None + step 8 + DESIGN\_MTR name) in the 3-test
         suite. Reflow last (the source was already canonical; the test 165 -> 160). No cell change (3/0/0/0/0), suite
         flat 1115/0/24.

D-513 | 2026-10-07 | The full probes sweep (one D for the whole sweep, per the user's call): all 24 probes in probes/
         (6.895 lines, ~787 checks) audited and house hygiene applied across 22 files (`verify_plot` +
         `verify_wrk_config` needed nothing — the 2 already-clean files). (1) Functionality: every probe runs green
         (exit 0, no FAIL, 0 mismatch) BEFORE and AFTER the fixes. (2) the ~51 over-120 code lines split (the R-520
         ceiling): label strings into adjacent string literals, read()/count() calls wrapped — no value change anywhere;
         this includes the 4 verify\_zed labels that the D-512 re-pin had left over-length (136/146/122/125 — my own
         over-length from that pass, repaired here). (3) the 19 E301 spots fixed (top-level defs with exactly 1 blank
         line: wrk\_positions 7, pidx 3, feature 2, pattern\_tests2 2, zed 2, hlp\_indexes / logistic\_model /
         wrk\_features 1 each). (4) the 10 dead imports dropped (wrk\_features 5: json5, types, Relevance, LMConfig, lwf
         — the worst file; pattern\_tests2 2: Square, `square_as_bitboard`; hlp\_indexes json5; logistic\_model
         BaseModel; save os; wrk\_positions os; mobility `bitboard_count`). (5) the 2 SyntaxWarning files fixed
         (verify\_anova + verify\_su\_analysis): the strings that pin the overview.md text (which carries the markdown
         \_ escapes) made RAW strings — the \_ is intentional content, the value is unchanged, the warning is gone. (6)
         the 11 stale 'Run: .venv/bin/python scratch/`verify_X.py`' header paths corrected to probes/ (session-20-era
         leftovers from when the files lived in scratch/; `probe_rules` §2: probes live in probes/). Non-findings
         verified and deliberately left: the verify\_mobility sections style (documented in its mirror doc: 'the 5
         active sections: 1, 2, 3, 4, 6' — no check() framework by design), the shebang/docstring header variety (no
         probe canon in `probe_rules.md` or rules.md prescribes one — a cross-cutting restyle would be an unprescribed
         change), the D-tag campaign markers in labels (probes are outside R-540 by design), the 2 E261 hits (string
         contents, not comments), the PEP 563 future imports. Post-sweep: all 24 probes re-run green; the static scan is
         clean (0 over-120, 0 E301, 0 SyntaxWarning). The suite is untouched (the probes are outside it): flat
         1115/0/24.

D-514 | 2026-10-07 | The full wsutils sweep (one D for the whole sweep, per the user's call): all 7 tools in wsutils/
         (2.164 lines) audited and the house hygiene applied in 4 files. (1) Functionality: every tool runs green (exit
         0) — the 5 light ones in check mode (docs\_format\_audit, notes\_lint, overview\_audit, notes\_format,
         src\_reflow — all reports clean) and the 2 heavy ones re-run (measure\_suite -> build/tmp/test\_durations.txt:
         1115 tests, 24 skipped; suite\_audit -> the scratch/ measurement, every module green). The
         wsutils/hooks/pre-commit script exists, is tracked, and proves itself at every checkin (it rejected the red
         notes commits during the sweeps). (2) the 3 E301 spots in src\_reflow.py fixed (the top-level defs
         docstring\_nodes / reflow\_comments / transform with exactly 1 blank line). (3) the 2 over-120 lines in
         notes\_lint.py split (the DPSPACE f-string messages at 125/124 into wrapped v.append calls). (4) the wsutils.md
         §3 header gaps closed: the explicit SAFETY section added to notes\_format.py (the DEFAULT is a report, the
         passed files rewritten ONLY with --write after the per-file verification) and the SAFETY line added to
         docs\_format\_audit.py (writes nothing — a read-only report); the Origin/ORIGIN case normalized in the 3 files
         using the older form (notes\_format, docs\_format\_audit, notes\_lint — the other 4 tools already used ORIGIN,
         the §3 label). Non-findings verified and left: the 5 src\_reflow 'E261' hits are false positives (2 docstring
         usage examples, 3 comment texts containing a hash), zero dead imports across all 7 files, the 3 tools that
         never call sys.exit have a single implicit exit code (nothing to document — §2.2 is satisfied by the documented
         USAGE), the naming is §4-clean (`snake_case` nouns, no `verify_` prefix), and the pre-existing
         non-reflow-canonical docstrings in 3 files were MEASURED on the HEAD versions (the same 13/6/1 docstrings
         before the edits — my changes shifted line counts only): no rule mandates the reflow fixpoint for wsutils
         files, so they are left as historical house style. Post-sweep: the 5 light tools re-run green, the static scan
         clean (0 over-120, 0 E301). The suite is untouched (the tools are outside it): flat 1115/0/24.

D-515 | 2026-10-11 | The parity PNG golden re-pinned (the env drift: the Ubuntu + Python upgrade). Roberto upgraded the
         platform (Ubuntu + Python 3.12.3 -> 3.14.4, the venv rebuilt, pip refresh: matplotlib 3.11.1 -> 3.11.2,
         numpy 2.5.4); the full suite (PERF=1 VVLONG=1, 1115 tests) failed exactly ONE test: `test_parity_png_golden`
         (the rendered hash 7939f3b3... != the pinned fdb8162d...). Investigation (scratch/parity\_investigate.py): the
         new hash reproduces the failed run EXACTLY; two consecutive renders are byte-identical (the in-environment
         determinism is intact, `test_up_all_seven_png` passes); the PNG's own tEXt metadata embeds "Matplotlib
         version3.11.2" — the writer's version string is part of the byte stream, so the patch bump alone moves the hash
         even at an identical rendering; the figure is visually identical to the D-158 one (the two-line title, the
         SYNTH\_PLOT subtitle, the fixed axes, the grid, the identity line, the jitter cloud). Not a bug: the documented
         env-drift mode of the version-sensitive rendering golden (the D-127 pattern, already exercised at D-158 after
         the 3.11.1 upgrade). Re-pinned to 7939f3b3dceaa959a5683baf3dc4303e6e4df4ba252d19008e1033ba730b03c0 in
         `test_wrk_plot.py` + the mirror doc (Roberto's call, option (a) — the simplest and most coherent; the golden
         stays environment-bound, the environment-independent variant stays open for his call). The journal volume
         rotated (log.md at 3086 lines > the 2000 cap: vol 004 closed at session 101, vol 005 opened at 102); the
         overview Environment bullet records Python 3.14.4. Suite via the R-210 wrapper (LONG=1, the live DB): 1115/0/24
         GREEN.

D-516 | 2026-10-11 | The 70-line campaign-log bullet removed from the overview Next steps (the format-campaign progress
         board). Roberto flagged the "Verify the format of the lm and test sources" item as completely out of norm: 70
         lines / ~8.4 KB against the 1-2 lines of the other items, dense with historical D-pointers, and no longer true.
         The git reconstruction: the bullet was born 2026-09-29 (D-337, e4b3627) as a one-line OPEN item of Roberto's
         six-point to-do; the rigid overview rules were born the same day (D-343, 0b0cbfb: "Next steps: OPEN items only,
         no Done bullets" + "NO bullet-per-campaign: the campaign lives in the session journal + the decisions log, and
         its state leaves this section when the campaign ends"); from the first campaign wave (D-476, 4816fa8, session
         99) every wave commit appended the day's module pass (45 commits between D-476 and D-512) until the item became
         the running campaign progress board — the journal records the practice openly ("il bullet Next-steps segnato —
         board COMPLETE"). Violations: "OPEN items only, no Done bullets" (the item is ~100% completion record), the
         no-bullet-per-campaign principle (the campaign ended 2026-10-10 and the record never left the overview), and
         the single-home principle (every fact already lives, more fully, in the open decisions log D-476..D-514 + the
         journal sessions 99-101 in log\_004). The guard stayed green because notes\_lint checks the overview's
         structure and the R-210 auditor the lists/tables — no mechanical check expresses the "no Done bullets"
         semantics. The same anti-pattern had been spotted and repaired on 2026-09-29 (the closed-ideas record out of
         the Next-steps backlog line) and recurred during the campaign. Roberto's call: option (A) — the item is deleted
         in full; no rewrite (no open content remains — the open test-sources scope is carried by the adjacent "Verify
         all the TEST sources" item) and no mechanical tripwire (a length cap would become an antipathetic constraint
         for a legitimate 4-line comment). Next steps is back to short, strictly open bullets. Flagged for Roberto's
         separate call: the adjacent "Verify the format of the WORKER sources" item is likewise fully covered by the
         completed worker cascade (D-494..D-512).

D-517 | 2026-10-11 | The TEST sources format sweep — the "Verify all the TEST sources" item (and, with it, the adjacent
         "Verify the format of the WORKER sources" item) closed: all 51 .py files under test/reversi/ (the 48 tracked +
         the 3 \_\_init\_\_) audited one by one (48 agents + the mechanical sweeps) and cleaned in three commits (parts
         1-3). The audit verdict: the item was NOT done — 37 of the 51 files carried real deviations (the 11 clean ones
         are exactly the files the recent campaigns had touched). Part 1 (the pilot, test\_logistic\_model, on Roberto's
         call to see the shape): the house header, the over-120 split, 9 light docstrings, 3 history prose. Part 2 (the
         mechanical pass): the 35 over-120 lines split value-identically — the golden literals by adjacent-string
         concatenation, the two multi-line triple-quoted goldens of test\_feature converted to parenthesized
         single-quoted line concatenations with explicit \n (the value asserted byte-identical) — and the 17 files
         brought to the canonical reflow fixpoint (wsutils/src\_reflow.py --write). Part 3 (the semantic pass): the 30
         long test docstrings compressed to the R-570 light form (the four carrying information absent from the mirror
         docs — the test\_pattern T9/T10 derivations, the test\_wrk\_plot parity golden — keep 3-7 lines, Roberto's
         tolerance rule); the 10 history prose removed (the "Converted from the verify\_X probe" provenance lines, the
         closecheck ULP-study header, the pre-fix narratives, the "D12" comment reference); the 6 headers normalized to
         the house shape; the 12 non-imperative docstring openings fixed. End state: 0 over-120 lines, 0 D-XXX/I-XXX in
         the .py sources, 51/51 at the reflow fixpoint; both Next-steps items removed from the overview (the worker side
         covered by the completed D-494..D-512 cascade). Suite green at every commit via the R-210 wrapper (1115/0/24).

D-518 | 2026-10-12 | The hlp\_analytics public API renamed to the hlp\_ module-prefix convention (Roberto's call): the 4
         public functions become hlp\_analytics\_{compute\_training\_metrics, compute\_training\_dense\_metrics,
         format\_console\_report, format\_file\_report} and the dataclass becomes AnalyticsTrainingDenseResult (the
         Analytics prefix keeps the class unambiguous at the use sites). All the consumers updated: wrk\_analytics (the
         import + the 4 call sites), test\_wrk\_analytics, test\_wrk\_plot, and the probe verify\_analytics (the imports
         / call sites + the check-A1 golden \_\_all\_\_ string; the check descriptions' history prose naming the
         original names stays). With it, the AnalyticsTrainingDenseResult docstring fix: the rn\_y parameter description
         wrapped leaving the "(one derivation, published by ANALYTICS)" fragment dangling on its own line — now a clean
         2-line wrap. The two mirror docs (hlp\_analytics.md + wrk\_analytics.md) carry the new names. All 4 .py files
         at the reflow fixpoint; the suite green via the R-210 wrapper (1115/0/24); the probe fully green.

D-519 | 2026-10-12 | The last unprefixed public name of hlp\_generate renamed to the module-prefix convention (Roberto's
         call, the hlp\_analytics D-518 sweep's sibling): compute\_w\_dense becomes hlp\_generate\_compute\_w\_dense
         (the 4 sibling public names already carried the prefix). Consumers updated: wrk\_generate (the import + the
         compute\_fn lambda), test\_hlp\_generate (the import + 4 call sites; the test method name
         test\_compute\_w\_dense stays — it is a test label, not a source reference), the probe verify\_generate (the
         import / call sites + the check-A1 golden \_\_all\_\_ entry + the A2 split anchor), and the two mirror docs.
         The 3 .py files at the reflow fixpoint; the suite green via the R-210 wrapper (1115/0/24); the probe fully
         green.

D-520 | 2026-10-12 | The 6 public names of hlp\_optimize renamed to the module-prefix convention (Roberto's call,
         the D-518/D-519 sweep's continuation — with shortened prefixes where the full name would be redundant):
         hlp\_optimize\_{save\_checkpoint, load\_checkpoint, is\_cache\_consistent, info\_dict, is\_status\_converged,
         weights\_compute\_hash}. Consumers updated: wrk\_optimize, test\_hlp\_optimize, the probe verify\_optimize, and
         the 5 mirror docs (incl. the two tools docs referencing the names). Accompanying reflow: hlp\_optimize.py
         brought to the canonical fixpoint — 5 prose blocks over the preferred 100 width (pre-existing since
         before D-517) re-wrapped, net -4 lines. Probe pins updated to the new reality: A1 (327 → 323), A6 (the
         canonical 2-line comment form), A16 (the phrase now spans a line break — whitespace-tolerant regex), and C1
         (347 → 348: a PRE-EXISTING stale pin from the D-517 test sweep, disclosed — the file was already 348 at HEAD).
         The 3 .py files at the reflow fixpoint; the suite green via the R-210 wrapper (1115/0/24); the probe 78/78
         green.

D-521 | 2026-10-12 | The wrk\_positions public surface reshaped (Roberto's call, after the usage audit confirmed 1 of 3
         names internal): load\_from\_db is now PRIVATE (\_load\_from\_db, dropped from \_\_all\_\_ — it is called only
         by the compute path inside the module); the two SHARED twin names take the module prefix,
         wrk\_positions\_\{extract\_and\_prepare, is\_cache\_consistent\} — they are the documented POSITIONS/VLD shared
         compute + validate path (the wrk\_vld\_positions reuse, the keyword bid/status overrides), so they stay public.
         \_\_all\_\_ is now \['wrk\_positions', 'wrk\_positions\_extract\_and\_prepare',
         'wrk\_positions\_is\_cache\_consistent'\]. Consumers updated: wrk\_vld\_positions (the import + both fns),
         test\_wrk\_positions + test\_wrk\_vld\_positions, the probes verify\_wrk\_positions (the \_\_all\_\_ golden,
         the def anchor, the F1 description) and verify\_vld\_positions (the A7 asserted source strings, the D8
         reuse-identity pins, the section import), and the 5 mirror docs (incl. regab.md + hlp\_config\_schemas.md). The
         in-function local variable named is\_cache\_consistent (the boolean + its DEBUG log line) is untouched — it
         shadows nothing anymore. The 4 .py files at the reflow fixpoint; the suite green via the R-210 wrapper; both
         probes fully green.

D-522 | 2026-10-12 | The index-type extraction: the new module src/reversi/index.py is the single home of Index (the
         np.uint32 alias) + IndexArray (the pydantic Annotated ndarray with the BeforeValidator) + the private
         validate\_index\_array — moved verbatim out of pattern.py, which no longer "owns" a generic concept. After the
         audit of the usage (Roberto's call): the current graph was already a DAG (no import cycle) — the smell was
         conceptual, mobility importing pattern for two aliases pattern does not own. New dependency shape: index is the
         leaf (numpy + pydantic only); pattern / mobility / feature all import from index; feature keeps its pattern +
         mobility imports; the lm data modules (hlp\_indexes, hlp\_su\_analysis) re-routed to index. pattern.py: the 3
         definitions + 2 \_\_all\_\_ entries out, the dead TypeAlias / Annotated / BeforeValidator imports out. Tests:
         test\_pattern (the star import no longer carries the aliases — explicit index import; the TestIndexArray class
         moved out), test\_feature (the import split), test\_mobility (Index from index); the new test\_index.py (5
         tests: the alias identity, the validator contract, the Annotated metadata). Mirror docs: the new index.md +
         test\_index.md; pattern.md (the 2 Types API rows out), mobility.md (the "deliberate reuse" notes → the index
         import), feature.md (the composition point), test\_pattern.md (13 classes / 76 tests, the import note).
         Overview: +1 source row + 1 test row. Zero probe pins broke (verify\_pattern\_tests2 is behavioral; the others
         carry no Index location pins). Zero runtime behavior change: type aliases + the validator move verbatim, the
         numba kernels use the dtype directly. The 10 .py files at the reflow fixpoint; the suite green via the R-210
         wrapper; the 6 touched probes fully green; the overview audit green (49/49 rows).

D-523 | 2026-10-12 | Two small calls from Roberto: (1) pattern.py's sample\_pattern\_data renamed to
         pattern\_sample\_data (the name-carrying-the-module convention, consistent with the D-518..D-522 prefix sweeps)
         — the 3 in-module occurrences (\_\_all\_\_, the docstring example, the definition) + the 3 mirror-doc mentions;
         no other module imports it (test\_pattern picks it up via the star import). (2) .gitignore now ignores the
         Emacs temp / lock files (the \#\* and .\#\* patterns — the literal # needs escaping, a bare # opens a gitignore
         comment); the two stray #pattern.py# / .#pattern.py lock files left by an editor session are now invisible to
         git and to the overview audit.

D-524 | 2026-10-12 | The Index-notation sweep (Roberto's convention, after the D-522 index extraction): where a variable
         HOLDS a feature-configuration index, the notation is Index / IndexArray, not the raw np.uint32; plain numbers
         (counts, offsets, the generic u32 I/O) stay np.uint32. The conversion is pure notation — Index IS np.uint32
         (the identity is pinned in test\_index.py) — zero runtime change. Src: pattern (the
         \_compute\_indexes\_on\_ss\_packed\_tensor annotation + astype, the principal-index kernel scalar casts + the
         UINT32\_MAX sentinel), mobility (the kernel output matrix + the shifts cast), hlp\_design\_matrix (the X
         allocation — the int64 iwmap cast STAYS np.uint32, Roberto: the int64 side is a later call), hlp\_analytics +
         hlp\_generate (all\_configs), hlp\_su\_analysis (the codes in the 2 private type aliases + the 4 construction
         sites). Tests: 11 files, ~39 sites (the golden config indexes, the design-matrix fixtures + dtype asserts, the
         codes, the synthetic index matrices); the offset fixtures (iwmap\_feature\_offset, the cumsum offsets) and the
         counts (iters, samples, popcount) deliberately UNCHANGED. Probes: verify\_design\_matrix re-pinned (A1 143→144,
         A2/A6/A7/A15 line-shift +1 for the new import, A11/C12/C13 the Index notation; C1 disclosed STALE pre-D-524:
         218 pinned on a 217-line file, now 218 = 217 + the import); verify\_hlp\_indexes (F1 312→313, F6 + the
         section-D data to Index, the import to the top block). Suite green via the R-210 wrapper; the 8 touched probes
         fully green; all 19 touched .py at the reflow fixpoint.

D-525 | 2026-10-12 | The ExtendedIndex type + sweep (Roberto's call, after the D-524 investigation): index.py gains
         ExtendedIndex (the np.int64 alias) + ExtendedIndexArray (the pydantic Annotated ndarray, the private
         validate\_extended\_index\_array) — the index space where the NEGATIVE values (-1, -2, ...) are LOGICAL states
         of a feature configuration (the unseen-config sentinel, the no-config placeholder), not data; \_\_all\_\_ = 4
         names. The vocabulary line goes into naming.md §Index (Roberto's explicit call). Sweep: hlp\_wmaps (the 7
         index-table sites: iwmap, w\_indices, the config-id index operands, feature\_w\_mapping, the fallback tables) +
         hlp\_generate (4 config-id sites) + hlp\_analytics (2) + hlp\_design\_matrix (the explicit cast is now
         astype(Index) — ExtendedIndex → Index, the D-524 placeholder is resolved); 11 test files (~34 sites: the iwmap
         / wmap / feature\_w\_ranges fixtures, the synthetic compute\_indexes matrices). NEW offset rule (Roberto: "an
         offset is the zero index of the feature" — agreed): the iwmap\_feature\_offset is Index in hlp\_wmaps + 7 test
         files (the uint32 fixtures: pure notation); the int64 offset fixtures (test\_wrk\_validate x3,
         test\_wrk\_analytics x1) STAY int64 — switching them to uint32 would change the synthetic pipeline's
         intermediate dtypes (a separate call). UNTOUCHED by rule: the counts (su\_analysis, egv, iters/samples), the
         bitboard signed-int domain (board.py), the generic u32/i64 I/O (binio), the pandas dtype strings (regab).
         Probes: verify\_wmaps re-pinned (27 pins: the line counts +1 for the new imports, the 2 exact-line int64 pins
         to ExtendedIndex; C1 disclosed stale since D-524: 362 pinned on a 363-line file). Mirror docs: index.md (the 2
         new rows + the consumer note), hlp\_wmaps.md (the field table), hlp\_generate.md, hlp\_design\_matrix.md (X is
         Index, the cast is ExtendedIndex → Index). test\_index: +5 mirror tests (10 total). One in-flight incident
         disclosed: the import auto-insert split a parenthesized import in test\_client.py (syntax error, caught by the
         reflow compile check, fixed) and test\_hlp\_design\_matrix needed its D-524 Index import extended to
         ExtendedIndex (3 test errors on the first suite run, fixed, suite re-run green). Suite 1122/0/24 via the R-210
         wrapper; the 7 touched probes fully green; all touched .py at the reflow fixpoint.

D-526 | 2026-10-12 | The hlp\_plot module API rename (Roberto's call, after the investigation): the 8 pipeline names
         take the module-qualified house form — PLOT\_NAMES/TITLES/BUILDERS → HLP\_PLOT\_NAMES/TITLES/BUILDERS,
         PlotData/ PlotStyle → HlpPlotData/HlpPlotStyle, collect\_plot\_data/save\_figure/ close\_figure →
         hlp\_plot\_collect\_data/hlp\_plot\_save\_figure/hlp\_plot\_close\_figure. The two general math helpers are
         PRIVATE now (Roberto: clarity): jitter → \_jitter, egv\_bins → \_egv\_bins, OUT of \_\_all\_\_ (now 8 names =
         the pipeline surface; the 7 plot\_\* builders stay un-renamed registry-dispatch targets, as agreed). Touched:
         hlp\_plot (the 10 names + the \_\_all\_\_), wrk\_plot (5), hlp\_config\_schemas (PLOT\_NAMES x4 — the
         PlotConfig whitelist), test\_hlp\_plot (17), test\_wrk\_plot (5), test\_hlp\_config\_schemas (1 prose),
         verify\_plot (32 sites incl. the single substring pin on the schemas import line — re-pinned to
         HLP\_PLOT\_NAMES; no line-count pins, no shift risk), 6 mirror docs (51 sites). The word-boundary replace kept
         the prose "jitter" common noun intact; only the code sites and the one backticked doc reference took the
         underscore. Suite green via the R-210 wrapper; verify\_plot fully green; all 7 touched .py at the reflow
         fixpoint (3 needed a re-wrap for the longer names).

D-527 | 2026-10-12 | The prng pick-kernel API (Roberto's call, after the investigation): the two module-level kernels
         take the house prefix — pick\_one\_from\_set64 → prng\_pick\_one\_from\_set64, pick\_one\_from\_set64\_batch →
         prng\_pick\_one\_from\_set64\_batch (the only function-level publics of the module; the class methods keep
         their names) — and gain the static type annotations (s/d: np.uint64 → tuple[np.uint64, np.uint8]; the batch:
         npt.NDArray [np.uint64] throughout, the first npt import in the module): INERT under numba (it infers from
         runtime values) and string-lazy via the existing \_\_future\_\_ import — zero runtime cost, pure documentation,
         no Pydantic (Roberto's perf rule). The slots array is UINT64 now (Roberto: it is a prefix count, always
         non-negative — the int64 was not ideal): the computation cumsum(needs, dtype=uint64) - needs.astype(uint64) can
         never underflow (the inclusive prefix is >= the element's own flag) and overflows only at 2^64 elements;
         VERIFIED empirically before the change — int64/uint64 slots are value-identical on 4 patterns (incl. all-True
         N=100k), the batch kernel output is bit-identical, and the stream stays aligned. Touched: prng (the renames +
         the annotations + the slots doc line), random\_game (import + 3 call sites + the 2 slots computations),
         test\_prng (import + 4 call sites + the 2 slots fixtures), 2 mirror docs (prng: 8 sites + the uint64
         prefix-count note; random\_game: 2). No probe references the names (zero re-pins); the ValueError message
         prefix follows the rename (no test asserts on it). One-time cost: numba recompiles the two kernels with the new
         uint64 specialization (cached after). Suite green via the R-210 wrapper (the random\_game LONG tests cover the
         engine path); all 3 touched .py at the reflow fixpoint.

D-528 | 2026-10-12 | The hlp\_zed factory rename (Roberto's call): zed\_fun\_factory → hlp\_zed\_fun\_factory — the last
         public name of the module without the hlp\_zed\_ prefix, completing the module scheme (LMZed /
         hlp\_zed\_compute / hlp\_zed\_fun\_factory; the LMZed class keeps its name with the LM data-object family).
         Touched: hlp\_zed (the def + the \_\_all\_\_ + the internal call; the 2-line def signature keeps its alignment,
         +4 on the continuation), client (import + call + comment — pure notation on the client hot path), 4 test files
         (17 sites, incl. the test method name test\_hlp\_zed\_fun\_factory), verify\_zed (3 pins, ALL text-only: the
         rename is in-line, 129 lines unchanged — the \_all\_ line, the def line, and the G10 substring on the test's
         parenthesized import), 2 mirror docs (6 sites). The G10 subtlety: the old substring 'zed\_fun\_factory)' is a
         SUBSTRING of the new text — without the re-pin the check would have kept passing opaquely (false green); the
         pin now carries the full new name. No probe index shifts; no suite count change. Suite green via the R-210
         wrapper; verify\_zed 51/51; all 7 touched .py at the reflow fixpoint.

D-529 | 2026-10-12 | The hlp\_validate module API (Roberto's call): the two functions take the house prefix
         (validate\_model → hlp\_validate\_model, top\_outliers → hlp\_validate\_top\_outliers) and the dataclass joins
         the LM family as LMValidate (Roberto: INTENTIONAL — it hooks the VALIDATE level name; the family's noun-form
         precedent LMValidation was discussed and his level-anchored form chosen). Touched: hlp\_validate (the class,
         the 2 defs, the \_\_all\_, the annotation + docstring), wrk\_validate (import + 2 calls + the 2
         MODULE-QUALIFIED docstring mentions hlp\_validate.top\_outliers / hlp\_validate.validate\_model — handled
         BEFORE the bulk so the double prefix hlp\_validate.hlp\_validate\_\* never forms), 3 test files (15 sites,
         incl. the 3 test method names test\_hlp\_validate\_\*), verify\_validate (the \_\_all\_substring pin re-pinned
         to the 3 new names + the live import / call + descriptions — all text-only, no index shifts, 145 lines
         unchanged), verify\_analytics (1 description prose), 3 mirror docs (11 sites). No collisions; no star imports;
         no suite count change. Suite green via the R-210 wrapper; verify\_validate + verify\_analytics fully green; all
         7 touched .py at the reflow fixpoint.

D-530 | 2026-10-12 | The exported-symbols generator becomes a wsutils tool (Roberto's call at the session close):
         wsutils/exported\_symbols.py — walks every .py under src/ (sorted), extracts the module-level \_\_all\_\_ with
         the AST (a literal string list; an annotated assignment accepted), and writes the per-file snapshot
         scratch/exported\_symbols.md (one section per file, the exported names as backticked tokens, the files without
         an \_\_all\_\_marked, the header counts). The snapshot is a REVIEW artifact (the public API surface of the
         whole package on one page), regenerated — never hand-edited — after any rename wave or \_\_all\_\_ edit.
         Motivation: the hand-kept scratch snapshot went stale across the D-518..D-529 rename wave
         (the D-526/D-528/D-529 refreshes were ad-hoc inline scripts). Verified: the tool's output is byte-identical to
         the current snapshot (52 files, 49 with \_\_all\_\_, 3 without). One row in the wsutils.md table (the
         generation category). No src/ or test/ change — no suite impact; the guard is green on the notes.

D-531 | 2026-10-12 | The test duration classification tool (Roberto's call, the overview next-step "select the tests by
         DURATION with the 5 tags"): wsutils/test\_duration.py — (1) the STATIC AST tag pass: perf (the skipUnless PERF
         decorator), db\_required (the db\_long\_gate setUp call), tier NORMAL/LONG/VLONG/VVLONG (the tier\_vlong/vvlong
         gates, method- AND class-level decorators, the highest wins) — INHERITANCE-AWARE for the Base\*Test mixin idiom
         (unittest discovers the inherited methods under every concrete class X(unittest.TestCase, Base) — the
         classifier resolves the same way, the gates of an inherited method are the OWNER's); verified EXACT against
         unittest discovery: 1122 = 1122, both diffs empty (NORMAL 1077 / LONG 43 / VLONG 2, PERF 22, DB 44). (2) N
         ISOLATED timed launches (`--runs`, default 3) with ALL tiers on (LONG/VLONG/VVLONG/PERF, live DB) — the
         measure\_suite TimedResult pattern, one TSV per launch in scratch/. (3) The aggregation: per-test MEAN +
         population VARIANCE (ddof=0), the status VERDE/ROSSO/SKIPPED (FLAKY when the N runs disagree) →
         scratch/test\_duration.csv (the English headers: module,class,test,perf,db\_required,tier,status,
         duration\_ms,variance\_ms) + scratch/test\_duration.md (summary + the table by mean duration, descending).
         Three in-flight bugs caught and fixed before the first launch: the Call.id attribute slip, the class-level (not
         method-level) VLONG decorators, the multiple-inheritance base resolution. measure\_suite.py is untouched (the
         1-run ancestor; its retirement is a separate call). One row in the wsutils.md table. The 3-launch measurement
         (≈45-60 min) runs as a background job; the reports land in scratch/ (gitignored).

D-532 | 2026-10-12 | The 21 fast DB tests re-classified LONG → NORMAL (Roberto's list, all under 0.4 s per the D-531
         duration report): the new wsutils/test\_duration.py tier column drove the pick. Mechanism: tags.py gains (1)
         db\_gate(testcase) — the DB-only gate (the SKIP\_REGAB\_DB=1 skip, NO tier requirement): the test sits in the
         DEFAULT tier and runs whenever the live regab DB is available; (2) tier\_long() — the METHOD-level LONG
         predicate for the mixed classes. Thirteen classes in eight test files move to db\_gate in setUp
         (final\_log\_print, positions, wmaps, design\_matrix, indexes, zed all-in; analytics 3 of 4 classes,
         vld\_positions 1 of 2); the six all-in file headers drop the "LONG=1" claim, the two mixed ones keep it for the
         worker class. THE MIXED CASE (disclosed): TestVldIndependenceCheck carries a SECOND test —
         test\_zero\_overlap\_is\_traced at 1.7 s, NOT on Roberto's sub-0.4-s list — which the class-level gate would
         have swept in: it now self-gates with tier\_long() FIRST in the method body and stays LONG (22 LONG tests
         remain, not 21). Three probes re-pinned (verify\_wmaps D3, verify\_zed C3+C4, verify\_design\_matrix C3); nine
         mirror docs updated (tags.md gains the db\_gate / tier\_long rows + the mixed-class convention); the
         wsutils/test\_duration.py classifier splits db → (db\_long, db) and reads the method-body tier\_long() call.
         Verified: the 8 modules at the default tier 56 run / 8 skip / OK (the 21 now RUN); LONG=1 56/0/0; full suite
         1122/0/24 (the 24 = the 22 PERF + 2 VLONG). NO COMMIT — Roberto: other adjustments follow, then the D-532
         commit with its file set.

D-533 | 2026-10-12 | The 11 SLOW NON-DB tests moved NORMAL → LONG (Roberto's list from the D-531 duration report): the 2
         plot renders (test\_wrk\_plot, 3.8 s + 1.3 s), the 2 prng equidistribution tests, the 2 test\_board tests (the
         numba overload reflection, the Zobrist no-collisions), the 2 test\_client tests (the 2-D c-order parity, the 1M
         PERF), the 4 PERF 1M benchmarks (test\_feature / test\_pattern / test\_client / test\_random\_game). Mechanism:
         the house @skipUnless DECORATOR shape with the D-532 tier\_long() predicate — @skipUnless(tier\_long(),
         "Skipping the LONG-tier test (set LONG=1 to run)") — the same idiom as the class-level VLONG/ VVLONG gates; the
         4 PERF tests stack it OVER the existing PERF gate (both must be on — the run conditions only shrink). Eight
         test files gain the from test.reversi.tags import tier\_long import (test\_random\_game: after the CLOSING
         paren of the parenthesized reversi import — the in-paren insertion broke the compile, caught and fixed).
         One-line decorator for the 7 plain methods. Seven mirror docs annotate the gated methods; the tags.md
         tier\_long row now carries both shapes (the D-532 method-BODY check for the mixed DB classes, the D-533
         DECORATOR for the slow non-DB tests). The wsutils/test\_duration.py classifier needed NO change: its
         method-body tier\_long() scan (ast.walk) already sees the decorator — verified: 33 LONG = 22 + 11, 4 of them
         PERF. Verified: test\_wrk\_plot default 9 run / 2 skip / OK, LONG=1 9/0/0; the 3 covering probes green
         (verify\_feature, verify\_pattern\_tests2, verify\_plot). NO COMMIT (the tiering wave continues; D-532 + D-533
         commit when Roberto calls it).

D-534 | 2026-10-12 | The A2050 full-chain test (96.5 s mean — the heaviest of the suite, 61% of the VLONG+LONG+NORMAL
         time with the 1e7 corpus test) moved VLONG → VVLONG (Roberto's call): the FIRST instrument of the VVLONG tier.
         One-line change in test/reversi/lm/test\_lm\_worker\_full\_chain.py — the class decorator
         @skipUnless(tier\_vlong(), …) → @skipUnless(tier\_vvlong(), …) (the skip message now "the very-long A2050 chain
         (set VVLONG=1 to run)") + the import (tier\_vlong → tier\_vvlong, the only use in the file). The cumulative
         semantics do the rest: VVLONG=1 implies VLONG → LONG, so the test runs under VVLONG=1 and is SKIPPED under
         VLONG=1 alone. The wsutils/test\_duration.py classifier needed NO change (it already reads tier\_vvlong in the
         class decorators): the shape is now NORMAL 1087 / LONG 33 / VLONG 1 (the 1e7 corpus) / VVLONG 1 (the A2050
         chain). Two mirror docs updated (the full-chain doc's gate line + the ~1.6-min runtime note; tags.md's three
         "currently uninstrumented" VVLONG claims — the tier is now instrumented). Verified: VLONG=1 alone skips the
         A2050 (1 skip); VVLONG=1 runs the module 9/0/0 in 105.8 s.

D-535 | 2026-10-13 | Fast NORMAL-tier equivalents for the LONG band — the "the simple run is exhaustive" goal
         (Roberto's): the input is the D-531 7-run report + a per-test coverage analysis of all 33 LONG tests
         (scratch/long\_tier\_coverage.md, five parallel analysis passes) asking, for each: are the same invariants
         already pinned in NORMAL, and if not, can a FAST (≤ 0.3 s, no-DB) test pin them. Verdict: 2 COVERED (the
         pattern + random-game 1M PERF prints — the substance already pinned by test\_large\_set and 11 NORMAL
         siblings), 24 PARTIAL, 7 NOT COVERED; 28 fast equivalents feasible, 3 infeasible (the A2030 end-to-end chain ×2
         — production-scale goldens only the real 14-level run can pin; the JIT array-overload test — the 0.9 s one-time
         compilation is irreducible). Implementation: 27 new UNGATED / no-DB tests over 12 test files (the 28th — the
         all-7 plot small render — was written, measured 2.9 s against the 0.3 s budget (matplotlib's ≈ 300 ms
         per-figure floor at 50 dpi), and REMOVED on Roberto's call; the all-7 render + the byte-identity pin stay
         LONG). Per file: test\_client +2 (the 10k perf smoke; the 32-board 2-D C-order parity with the STRIDED view
         base[::2,::2] + the (0,4)/(2,0) empties); lm\_worker\_full\_chain +1 (the v2 write emits NO config sidecar —
         the file-absence guarantee); wrk\_analytics +5 (the two-instance determinism at a small rlm\_00-derived config
         with the 04/13 cache slots pre-seeded no-DB; the console-report format; the direct \_up with independently
         re-derived publications; the \_down scope + the report-file survival; the hlp dense-metrics series↔MAE
         bit-exact consistency); wrk\_generate +3 (a mock-Context class: compute + sidecar + the duck-typed checksum
         identity, the two-instance hit, the \_down); wrk\_gradient +2 (TestGradientFlagWiring extended: the \_down
         scope, the exact generation log lines + the 3×2 zero-w golden through the worker-published fg); wrk\_optimize
         +3 (a REAL tiny L-BFGS over the 3×2 problem: convergence + checkpoint, the iters>=max\_iters disjunction with
         ZERO fg calls in run 2, the \_down that keeps w); wrk\_plot +1 (the small 'pdf,png' pair, ≈ 0.2 s);
         wrk\_validate +3 (the two-instance determinism at small config, the FULL four-attribute \_down scope — strictly
         stronger than the LONG test, the 10-line ordered log contract with re-derived metrics); wrk\_vld\_positions +4
         (the DB-free stand-in: the real cache-file hit, the bid=[8] / status=["CMS","CMR"] override pin, the \_down,
         BOTH independence trace lines); test\_board: test\_no\_collisions DE-GATED (its existing 10k/1M scale branch —
         10k in the default tier, 1M under LONG=1); test\_feature +1 (the 13-pattern I=51 set at N=1000 with a 51-value
         row-0 golden — a STRENGTHENING over the 1M test, which asserts no values); tools/test\_prng +2 (the 20k / 10k
         chi2 at the same per-bin scale as the 200k / 100k LONG tests — 1/10 statistical power, threshold meaning
         preserved). The worker stand-ins need a REAL base Context (Worker.up/down are @validate\_call'd — a bare
         SimpleNamespace is rejected; the mocks use Context() or class X(SimpleNamespace, Context)). Twelve mirror docs
         updated. Suite: 1149/0/24 at LONG=1 (1122 + 27). Tier shape: NORMAL 1114 / LONG 33 (UNCHANGED — the originals
         stay as the production-scale versions) / VLONG 1 / VVLONG 1. Expected: the simple run 15.3 s → ≈ 17.3 s,
         exhaustive at the invariant level. The 5 residual LONG tests (the A2030 chain ×2, the JIT array overloads, the
         2 already-covered 1M PERFs) are Roberto's call.

D-536 | 2026-10-13 | Two small items (Roberto's call): (1) the run\_utests.sh banner was missing VVLONG — the echo line
         now prints PERF / LONG / VLONG / VVLONG / SKIP\_REGAB\_DB, and the VVLONG header-comment line drops the stale
         "currently uninstrumented (D-285)" claim (the A2050 chain has been the VVLONG instrument since D-534); (2) the
         cosmetic line break in test/reversi/data/rlm\_04.json (the training\_data\_set closing brace moved to its own
         line — the user's edit) — the parsed structure is identical to HEAD (verified with json5) and an A2030 test
         runs green on the edited fixture. The overview runner bullet now names the VVLONG tier. The A2030 full-pipeline
         tests stay LONG as they are (Roberto: "vanno bene così"). Verified: the banner prints VVLONG=1; the canonical
         LONG=1 run is OK (24 skips).

D-537 | 2026-10-13 | The overview.md cleanup (Roberto's dictation, "puliamo overview.md"): (1) the Environment
         test-command entry rewritten as he drafted it (default fast ~15 s; VVLONG=1 ~15 min incl. the A2050 chain and
         implies LONG, VLONG; the DB-gated suites' requirement drops the stale "+ LONG=1" clause — the D-532 db\_gate
         already runs the DB tests in the default tier). ONE deviation from the draft, disclosed: his text said "the
         standard pre-commit run is LONG=0" — an evident slip against the R-210 gate (LONG=1), written as LONG=1. (2)
         the Current-state "suite tiers after the D-531..D-535" entry removed — the tier shape now lives in the
         decisions log + the test-duration reports, not the overview. (3) three Next-steps entries removed (the
         module-API naming sweep, the int64 offset fixtures, the register re-review / R-200 rule text) — Roberto: "per
         me non hanno senso".

D-538 | 2026-10-13 | The overview test-command entry now carries the MEASURED durations (Roberto: "usa il numero
         misurato"): default fast ~15 s → ~17 s and VVLONG=1 ~15 min → ~3.5 min, from the post-D-535 7-run report
         (scratch/test\_duration.{md,csv}): NORMAL 1115 tests at 17.5 s mean, the all-tiers 1149-test run at 208.6 s
         mean (3.5 min).

D-539 | 2026-10-13 | The docs/user/ zone — the user-facing docs that mirror NO source file (Roberto's LM-config "User
         guide" request; the placement was his call after Nia's proposal: a separate doc, not a section of the
         logistic\_model mirror doc). FIRST PAGE: docs/user/lm\_config\_guide.md — the JSON5 config file: the Rules (the
         10 required top-level keys, the ec single source 0..60, the 3-uppercase statuses, the 16-hex no-0x masks, the
         relative/absolute path resolution, the cross-field checks, the free-form properties bag, the target\_level),
         the MINIMAL working example, the per-section EXHAUSTIVE reference (root, the regab data set + the connection,
         the validation data set, the feature set + pattern/mobility, the stat model, the optimization, the analytics,
         the plot with all 19 knobs, the su analysis, the anova) with type/default/notes per option, and the complete
         example; BOTH examples were verified against the real LMConfig schema (model\_validate), and the field-level
         facts POINT to the hlp\_config\_schemas.md mirror doc instead of duplicating them. The zone is LEGISLATED in
         three places: docs\_rules.md (the opening scope sentence + the new §8 — the house format applies, the mirror
         skeleton does not; the two extra contracts: TRUTH — every claim checkable against the sources, one fact one
         home — and LIFECYCLE — the user doc is updated in the same commit as the source change that invalidates it);
         wsutils/docs\_format\_audit.py (the docs() walk skips docs/user/ — the mirror checks produced two false
         findings on the guide: the expected H1 and the size budget); the overview "Mirror docs" bullet registers the
         zone (the Source/Test tables stay 1:1).

D-540 | 2026-10-13 | The license-header wave — the public-push preparation (Roberto's GO after the plan review; the repo
         is going to github.com/rcrr/reversi-v2, PUBLIC): every tracked source carries the standard GPL header, with the
         project URL on the new repo name. The one-shot migration (scratch/migrate\_headers.py, gitignored) over 146
         files: 41 banner INSERTIONS (the 24 probes + the 9 wsutils tools AFTER the shebang, the 7 \_\_init\_\_.py
         BEFORE their docstring, run\_utests.sh after its shebang — FILE\_NAME the basename, YEARS the first-commit year
         from git, all 2026) + 105 URL-ONLY rewrites (98 .py + the 7 .json /\* \*/ fixtures — every other line
         byte-identical). One pre-existing variant NORMALIZED: random\_game.py's banner carried the FILE\_NAME on line 1
         (no leading bare #) — brought to the standard 26-line template. The root LICENSE is the OFFICIAL GPLv3 text
         from gnu.org (674 lines, 35149 bytes — byte-identical to the canonical gpl-3.0.txt, the text GitHub itself
         detects from); pyproject.toml declares license = {text = "GPL-3.0-or-later"} (the table form — compatible with
         the setuptools>=64 floor; the PEP-639 SPDX-string form needs setuptools >= 77). The local branch renamed master
         → main (zero cost while no remote exists). The .env (the DB credentials) is STILL tracked in this commit: its
         untrack + the .env.example is the next step (3a) before the push; the password stays in the history (disclosed
         + accepted by Roberto: a local-only test DB, the password is the trivially-known username/dbname — no history
         rewrite). Verified: the 138 .py py\_compile; the URL audit leaves ZERO old URLs and finds the new one in every
         one of the 146 headers; the 7 .json parse-identical to HEAD; bash -n OK; the full LONG=1 suite green (24
         skips).

D-541 | 2026-10-13 | The license-header GUARD (R-591) — D-540 made the headers true, this D makes them PERMANENTLY true:
         the new wsutils/license\_header\_audit.py (a CHECK tool, fail-closed) — over every tracked source file (147:
         the 138 .py + the 1 .sh + the pre-commit hook + the 7 .json fixtures) it requires the standard 26-line GPL
         header as the first lines (after the shebang, when there is one): the ten marker lines IN ORDER (the bare #
         opener, the FILE\_NAME = the basename, the separator, the "part of the reversi program" line, the project URL,
         the separator, the Author line, the Copyright line with a 4-digit year, the separator, the License marker); the
         .json fixtures use the C-style /\* \*/ variant of the same ten. WIRING: the pre-commit gate gains it as the
         third BLOCKING check (the STAGED source files only — a code-only checkin pays nothing, the same pattern as the
         notes guard); the hook's doc comment now says "Three BLOCKING checks". LEGISLATION: R-591 in notes/rules.md
         (the Code style section) + the tool registered in the wsutils.md table (the hook row updated to the three
         checks). Two COLLATERAL fixes the guard's first run surfaced: (1) 27 old banners carried a trailing space on
         their separator comment lines (`# `) — normalized to the bare `#` inside the header window (mechanical,
         comments-only); (2) wsutils/hooks/pre-commit itself (a tracked source WITHOUT the .sh extension — the first
         pathspec missed it) got the standard banner. Verified: the audit is GREEN on all 147 files; RED on both failure
         modes (no header at all; the FILE\_NAME carrying the wrong name); the end-to-end hook test — a headerless
         staged file BLOCKED a real commit (no commit was created); the full LONG=1 suite green.

D-542 | 2026-10-13 | Fresh-clone readiness, part 1 (Roberto's GO for step 3, the checkin authorized; the README — 3c —
         deliberately KEPT OUT of this commit, awaiting his review): the .env (the local DB credentials) leaves the
         TRACKED tree — git rm --cached (the file stays on the local disk), added to .gitignore, and the tracked
         .env.example carries the same nine keys (the five DB\_\* + the four TEST\_RDATA\_\*) with placeholder values
         and the fill-in instructions (cp .env.example .env). test/reversi/paths.py now creates build/tmp AT IMPORT TIME
         (CUSTOM\_TMP\_BASE.mkdir(parents=True, exist\_ok=True)) — the 84 test modules that write their artifacts under
         build/tmp no longer depend on the directory happening to exist: a fresh clone runs the suite with zero manual
         steps (the build/ tree stays gitignored). Verified: build/ removed on disk, the import recreates build/tmp; the
         full LONG=1 suite green (24 skips).

D-543 | 2026-10-13 | The README (the public front page of the repo; Roberto's approval after the two-round review — the
         first draft, then the single addition: the regab bullet in Requirements pointing to the github.com/rcrr/reversi
         project for the database details). Content: what it is + the license; the REQUIREMENTS (Python >= 3.12, the
         pyproject dependencies, the optional PostgreSQL/regab server with the SKIP\_REGAB\_DB=1 escape hatch); the
         five-line SETUP (clone, venv, pip install -e ., the .env from the .env.example template); the test TIERS with
         their measured durations; the pipeline FACADE command with the cross-reference to
         docs/user/lm\_config\_guide.md; the LAYOUT table (the nine top-level paths). Deliberately DRY — facts and
         commands, no marketing. The README lives at the repo root, OUTSIDE the docs/ mirror tree: the
         one-doc-per-source 1:1 rule is not affected (it is not a mirror doc, it is the front page).

D-544 | 2026-10-14 | MOBILITY rework — the difference concept is GONE (Roberto's GO after the 8-config A2050 experiment
         and the independent verification of his linearity thesis): a Mobility is now (name, mask, side) with side ∈
         {'mover', 'opponent'} selecting whose legal moves are counted over the mask; index = popcount(lms & mask)
         (mover) / popcount(alms & mask) (opponent), n\_configurations = k + 1. Rationale (verified): under the old
         additive (mask, amask) definition, DLMC = LMC + ALMC was an EXACT algebraic identity (the 64 cancels) — zero
         deviation over all 1,999,179 training positions, and at the design-matrix level (D = 19 + L + A, residual
         RMS 0.000000, rank([1,L,A,D]) = rank([1,L,A]) = 3); the experiment showed all three pairs saturating at the
         same validation RMSE (12.47–12.50) and the triple at 12.47. The opponent side is the RAW count (was 64 − A):
         span-equivalent under the intercept, same scale as the mover, better conditioning. Scope: src (mobility.py
         class/set/kernel, the feature.py wording, the MobilityFeatureConfig schema with the Literal['mover','opponent']
         side field, the wrk\_features build + debug log, the model\_weights binary layout u64 mask + u8 side-code), the
         6 rlm fixtures (rlm\_00 3 → 2 features — the DLMC entry dropped; the other five side: mover), the test suite
         (test\_mobility.py rewritten as the spec — the dedicated mover-side, opponent-side and multi-entry cases; the
         rlm\_00-derived goldens recomputed with independent derivations matching the pipeline: fset 9de406cf…, the
         rlm\_01 analytics masked report re-pinned after verifying the model content unchanged — RMSE 23.87, 16 iters;
         the rlm\_04 fset pin e9cda2ac… and the full-chain masked report re-pinned after the bit-exact 6-position EF
         pins passed; the SU/analytics feature counts 5 → 4), the 3 probes + verify\_hlp\_indexes (4 re-pins: 2 from
         this change — the (2,15)/(N,15) shapes — and 2 PRE-EXISTING drift the run surfaced: db\_long\_gate → db\_gate,
         the header run-note wording), 9 mirror docs + the user guide + the naming register (the two standard
         mobilities, the (mask, side) definition). Zero amask/DLMC left in the active zones (the sole exception is the
         deliberate 'amask' not in src guard in verify\_wrk\_features); the history lives in this log and in git only.
         Declared consequence: previously saved rglm\*.dat models and the old build/ experiment configs (untracked) are
         no longer loadable/valid — all regenerable. Verified: the full LONG=1 suite green (1151 tests, 24 skips).

D-545 | 2026-10-14 | D-544 completion — the two VVLONG-tier omissions that Roberto's VVLONG run surfaced (the standard
         LONG=1 guard does not reach that tier): (1) the test\_feature.py PERF class (TestFeatureSetComputeIndexesPerf)
         still constructed Mobility with the old three-argument form — the THIRD occurrence of the pattern the wave's
         two-replacement pass missed; now (mask, 'mover'). (2) the A2050 full-chain test (TestFullChainA2050): the
         masked analytics-report hash re-pinned to 8d609b5b… (Roberto's run value, reproduced on my own run) + the
         rlm\_03 FeatureSet hash re-pinned to f34ee409… (independently derived: sha3(b'INTERCEPT' + the single-LMC-mover
         mset hash + the unchanged 11-pattern pset hash)); ALL the content pins — the training-population statistics,
         the w\_dense sha3, the optimization info, the validation metrics, the 6-position EF, the model-file size band —
         passed UNCHANGED, confirming model identity at A2050 scale. Verified: the test\_feature PERF class OK (1M
         positions); the A2050 chain OK (110 s); the full VVLONG=1 suite green (1151 tests, 22 skips).

D-546 | 2026-10-14 | The MOBILITY definition precision (Roberto's review of the D-544 docstring): the game rules define
         the available moves ONLY for the player to move — that is the mobility; the rules define no such quantity for
         the opponent. The ANTI-mobility is a feature-level definition (ours): the moves the opponent would have if it
         were the opponent's turn to move (the "would-be moves"). The approved wording applied to all eight active-zone
         locations carrying the old imprecise phrasing: the Mobility class docstring, the \_\_init\_\_ Args line, the
         MobilitySet.compute\_indexes docstring, the Numba kernel docstring (all in mobility.py), the
         MobilityFeatureConfig.side description (hlp\_config\_schemas.py), the what-it-is paragraph
         (docs/src/reversi/mobility.md), the naming register entry (naming.md), and the opponent-side test docstring
         (test\_mobility.py). Docs-only change — zero behavior change; the two random\_game.py kernel comments ("the
         opponent's legal set on the swapped view") are engine-level descriptions of the kernel computation and were
         deliberately left. Verified: the three mobility probes green, the full LONG=1 suite green.

D-547 | 2026-10-14 | The [PERF …] print in a non-PERF run (Roberto's observation on a default-tier run): the DIAGNOSIS —
         test\_client.py's test\_performance\_1m is correctly double-gated (PERF=1 + LONG=1) and was skipped; the line
         he saw came from test\_performance\_10k\_smoke, the DELIBERATE ungated 10k-board smoke benchmark of the default
         tier, which reused the same "[PERF …]" print prefix as the house PERF pattern — cosmetic confusion, not a
         missing gate. The FIX: the smoke twin now prints the "[SMOKE make\_evaluation\_array]" prefix (the docstring
         states the rule: a non-PERF run must never show a [PERF …] line); the 1M PERF test keeps the house prefix. The
         mirror doc updated at both mentions. Verified: the module in the default tier prints [SMOKE …] with zero [PERF
         …] lines (10 tests ok, 2 skips); the full LONG=1 suite green.

D-548 | 2026-10-14 | The standard tests print nothing (Roberto's rule, tightening D-547): the 10k smoke twin in
         test\_client.py removed its print entirely — with it its benchmark-only servitors (the validation warmup and
         the perf\_counter timing, which existed solely to feed the line) — leaving the plain parity smoke check (the
         first 100 outputs bit-exact vs the scalar EF + the deterministic re-run); the docstring now states the rule.
         Scoped EXACTLY to this one test per Roberto's instruction (no tree-wide print sweep). The mirror doc updated at
         both mentions. Verified: the module in the default tier runs silent (10 tests ok, 2 skips, zero output lines);
         the full LONG=1 suite green.

D-549 | 2026-10-14 | The docstring discipline (Roberto's principle): we write what the program DOES, never what it does
         NOT — the D-548 "no print — the standard tests print nothing" sentence in the smoke test's docstring was
         useless and misleading (a negation existing only because of the past behavior) and is removed; the docstring
         now states only what the test does (the 10,000-board vectorized EF parity check + the deterministic re-run).
         The mirror doc updated at both mentions. The MOBILITY wave is CLOSED with this (D-544 → D-545 → D-546 → D-548
         → D-549); a new session opens. Verified: the full LONG=1 suite green.

D-550 | 2026-10-14 | The LOG wave, step 1 (Roberto's GO for the three agreed changes; the per-level waves follow one
         level at a time, each with its own D): (1) the StateMachine now logs a DEBUG per-step duration line after every
         "Completed UP step" ("Step <WORKER> <DIR> duration: 0.123 s" — perf\_counter); (2) FINAL\_LOG\_PRINT closes
         with a DEBUG "log written: <path> (N lines)" line (replacing the old INFO "full log written"); (3) the
         FINAL\_LOG\_PRINT file floor is now DEBUG — format\_event\_log takes a min\_relevance parameter (default TRACE
         = the old behavior) and the writer passes Relevance.DEBUG, keeping the TRACE hot-loop detail out of the file
         (the TRACE level stays reserved for the L-BFGS loop / the Numba kernels, per Roberto). The config field
         description updated. Collateral goldens: the state machine's 3 display goldens (the new DEBUG line in the
         stdout pin + the event-log table row; the frozen-clock history durations 0.003000 → 0.004000 — the extra
         log\_event per step adds a tick), the final-log test (the mock's min\_relevance parameter, the "log written"
         pins, the trailing post-write count 2 → 3), the probe B2/B4. The per-level reclassifications (the L-BFGS
         iterations, the outlier lines, the cache boilerplate, …) are the FOLLOWING waves — this one touches no worker.
         Verified: the full LONG=1 suite green.

D-551 | 2026-10-14 | The LOG wave, level 1 — CONFIG (the iterative per-level process: implement, show the log, review,
         commit): C1 the load-sequence redundancy collapsed — the "Loading … ..." INFO line removed (the DEBUG "JSON
         file read." + the INFO "loaded." + "validated." carry the sequence); C2 the operational-sections echo added —
         one DEBUG line per section (optimization with the strong-Wolfe pair + the stopping criteria +
         high\_performance\_fg, stat\_model, su\_analysis with the corpus spec + su\_pairs, anova, the regab data set
         with the dbname/user/host — never the password — and the validation data set): the log is now self-sufficient
         on WHAT THE RUN RAN WITH. The mirror doc updated. Verified on the target\_level=CONFIG artifact run (the
         18-line log reviewed by Roberto) + the full LONG=1 suite green.

D-552 | 2026-10-14 | The LOG wave, level 2 — FEATURES (iterative, reviewed on the target-level artifact): F1 the three
         DEBUG "… set object created, hash = '…'" lines removed (the name+hash live in the INFO summary); F2 the DEBUG
         "Intercept feature configuration: '…'" raw-echo removed; F3 (Roberto) the per-feature DEBUG table gains two
         cumulative columns — first\_inst\_pos (the feature's first design-matrix column) and first\_conf\_pos (its
         first w\_dense weight, the per-feature iwmapping offset): the log now shows WHERE each feature sits in the
         model vectors. The cumulative arithmetic casts the numpy uint8 fields to int (the raw product overflows uint8).
         The mirror doc updated. Verified on the target \_level=FEATURES artifact (first\_conf\_pos 0/1/66 as expected)
         + the full LONG=1 suite green.

D-553 | 2026-10-14 | The LOG wave, level 3 — SU\_ANALYSIS (iterative, reviewed on the target-level artifact): the
         per-instance / per-pair data rows are REMOVED from the log (Roberto: the report file is their canonical home —
         the log points to it, it does not duplicate it; the block is unbounded, it grows with n\_instances × n\_pairs);
         the corpus "loaded from cache / computed" line and the "tables published on the ctx" line moved to DEBUG; the
         log now carries 3 INFO (Starting / "report written" / Completed) + the DEBUG mechanism lines. Scope note: the
         "Cache successfully loaded and validated" line is the SHARED cache manager's boilerplate — it stays INFO until
         the dedicated cache wave (the 7 workers at once). The mirror doc updated. Verified on the
         target\_level=SU\_ANALYSIS artifact (18 → 8 lines) + the full LONG=1 suite green.

D-554 | 2026-10-14 | The R-595/R-600 enactment (Roberto's confirmation): the R-591 → R-595 rename (the GPL
         license-header rule — the register re-alignment, the text unchanged) and the new R-600 (gitignored is not
         disposable: the agent never deletes anything the user created — the build/ content beyond build/tmp is user
         data, the cleaning limited to build/tmp and scratch and only when asked) — the four files committed atomically
         (the register + the three reference sites), the "Pending Roberto's call" bullet out of the overview. The audit
         script re-run clean (148 files).

D-555 | 2026-10-14 | The overview Next-steps refresh (the milestone update the wave owed): the closed MOBILITY bullet
         out (its home is the decisions log) and the LOG-wave-in-progress bullet in — D-550…D-553 done, the remaining
         levels one at a time (next: POSITIONS), then the shared cache-boilerplate wave and the missing entries B3–B7.

D-556 | 2026-10-14 | The LOG wave, level 4 — POSITIONS (iterative): P1 the "Model attributes … have been set."
         publication line to DEBUG (the mechanism, like the SU\_ANALYSIS publication); the dataset identity lines stay
         INFO (the TOTAL + provenance + duplicate-policy line, the rds\_checksum, the one-line population stats). The
         shared cache-manager boilerplate stays for the dedicated cache wave. The mirror doc updated. New guard practice
         agreed with Roberto: the DEFAULT tier suite before every commit (it is now complete), LONG=1 only when the
         change touches what the long tiers cover, a closing LONG=1 at the wave-end milestone — this commit is the first
         under the new practice (default OK).

D-557 | 2026-10-14 | The test-guard policy (Roberto's process point, agreed): the standard pre-commit run is the DEFAULT
         tier (the complete fast suite) — not the blanket LONG=1 the overview carried from the earlier sessions; LONG=1
         (or higher) runs only when the change touches what the long tiers cover (the full-chain e2e, the DB-gated and
         the scale tests), plus a closing LONG=1 at each wave's end milestone. The overview Environment section updated
         (this commit).

D-558 | 2026-10-14 | The LOG wave, level 5 — INDEXES (iterative): I1 the "Model attribute hlp\_indexes has been set."
         publication line to DEBUG; I2 (the missing B-INDEXES entry, Roberto spotted the expectation) the DEBUG
         indexes-shape line — "Indexes shape: (199932, 6)." (the n\_positions × n\_feature-instances matrix: 1 INTERCEPT
         + 1 LMC + 4 EDGE). The checksum line stays INFO (the identity). The mirror doc updated. Default-tier guard
         green.

D-559 | 2026-10-16 | The LOG wave, level 6 — DESIGN\_MTR (iterative): D1 the "Model attribute design\_matrix has been
         set." publication line to DEBUG; D2 the "Design Matrix computed/loaded. Shape: …" line to DEBUG (the bounded
         detail, consistent with the INDEXES shape line). The checksum line stays INFO (the identity). The mirror doc
         updated. Default-tier guard green.

D-560 | 2026-10-17 | The LOG wave, level 7 — ANOVA (iterative, option (b) per Roberto — the SU\_ANALYSIS precedent): the
         per-feature rows (the 5 eta²/omega² + the 5 adherence) REMOVED from the log (their canonical home: the report +
         the CSV — the log carries only the two "written" artifact lines). The exhaustive anova config section (all 5
         fields, export\_csv true) verified the CSV path on the artifact run. The two tests that pinned the per-feature
         rows in the log re-pinned on the REPORT content (same data, the right home). The mirror doc updated.
         Default-tier guard green.

D-561 | 2026-10-17 | The LOG wave, level 8 — WMAPS (iterative): W1 the "Model attributes … have been set." publication
         line to DEBUG; W2 the "WMAPS computed/loaded. Total weights (W): …" line to DEBUG (the bounded detail,
         consistent with the DESIGN\_MTR shape line). The checksum line stays INFO (the identity). The mirror doc
         updated. Default-tier guard green.

D-562 | 2026-10-17 | The LOG wave, level 9 — ZED (iterative): Z1 the "Zed array computed. Shape: …" line to DEBUG; Z2
         (the missing B-ZED entry) the new DEBUG range line — "Zed array range: min 0.0100, max 0.9900." (the
         logit-clipping endpoints show at a glance). The checksum line stays INFO (the identity). The mirror doc
         updated. Default-tier guard green.

D-563 | 2026-10-17 | The LOG wave, level 10 — GRADIENT (iterative, LEAVE-AS-IS): the level is already compliant — the
         start line + the one bounded result line ("Gradient function generated (high\_performance: True)." — a run
         fact, INFO-deserving) + the machine lines. No source change.

D-564 | 2026-10-17 | The LOG wave, level 11 — OPTIMIZE (iterative, Roberto's correction to my TRACE proposal): the whole
         L-BFGS loop output (the per-iteration lines at the configured log\_every\_n cadence + the terminal
         Converged/Stopped/fgc/Restart lines) moves from INFO to DEBUG — the iteration frequency is already
         USER-THROTTLED by the config (log\_every\_n: 1/5/10/20), so it is bounded-by-choice detail that stays in the
         log file, not hot-loop TRACE. One line changed (the wrk\_optimize logger\_fn sink); the opt\_lbfgs tool and its
         tests are untouched. The level's own lines (Starting, "Optimization finished. Reason…", the w\_checksum,
         Completed) stay INFO. The mirror doc updated. Verified on a fresh run (the checkpoint removed from build/tmp):
         77 lines — 5 INFO + 72 DEBUG. Default-tier guard green.

D-565 | 2026-10-17 | The LOG wave, level 12 — GENERATE (iterative): G1 the "Dense weight vector generated/loaded. Shape:
         (6627,)" line to DEBUG (the bounded detail, the house pattern of the shape lines — DESIGN\_MTR / WMAPS / ZED).
         The checksum line stays INFO (the identity). The mirror doc updated. Default-tier guard green.

D-566 | 2026-10-17 | The LOG wave, level 13 — VLD\_POSITIONS (iterative): V1 the "Model attributes vld\_positions,
         vld\_game\_values and vld\_rds\_checksum have been set." publication line to DEBUG (the POSITIONS pattern,
         mirrored). The dataset identity lines (the TOTAL + provenance, the vld\_rds\_checksum), the population stats
         and the validation-independence check stay INFO (real facts). The shared cache-manager boilerplate stays for
         the dedicated cache wave. The mirror doc updated. Default-tier guard green.

D-567 | 2026-10-17 | The LOG wave, level 14 — VALIDATE (iterative): VA1 the whole outlier block (the "Top 20 extreme
         validation residuals (outlier report):" header + the 20 per-position lines) to DEBUG — the per-position detail
         (the roadmap's "VALIDATE outliers → DEBUG"), moved as ONE unit so the header is not left dangling at INFO. The
         6 metric lines (MSE / MAE / MAE(y) / RMSE(y) / RMSE-MAE + the completion line) stay INFO (the model quality,
         the bounded post-mortem gold). The mirror doc updated. Default-tier guard green.

D-568 | 2026-10-17 | The LOG wave, level 15 — ANALYTICS (iterative): A1 the report body (the 18 header lines, the single
         emission site in the wrk\_analytics loop) to DEBUG — it is BOUNDED report content (fixed structure, not
         per-item like the SU tables), so it stays in the log file at DEBUG; its canonical home is the file report, and
         the INFO "Analytics report saved to …" line points to it. The start / phase lines and the artifact line stay
         INFO. The mirror doc updated. Default-tier guard green.

D-569 | 2026-10-17 | The LOG wave, level 16 — SAVE (iterative): S1 the existing lines LEAVE-AS-IS (the start + the
         "Model weights saved to …" artifact line at INFO — the pattern). S2 (the missing B-SAVE entry) the new DEBUG
         integrity echo: "Model weights file: {size} bytes, checksum: {sha3-256}." — the final artifact was the ONE file
         with no checksum line, while every other artifact (indexes, design matrix, wmaps, zed, w\_dense, the data sets)
         has its; the compressed bytes hash is deterministic (lz4 per content). The mirror doc updated. Default-tier
         guard green.

D-570 | 2026-10-17 | The LOG wave, levels 17-18 — CLIENT\_CHECK + PLOT (iterative, LEAVE-AS-IS, recorded together): both
         are already compliant. CLIENT\_CHECK: the start + the one bounded verification-result line ("Client check
         passed: … max difference 0.000e+00 (tolerance 1.0e-08)" — a real fact, INFO-deserving) + the machine lines.
         PLOT: the no-op branches are clean one-liners; the enabled branch is bounded-by-choice (one "Plot 'X' saved: …"
         artifact line per requested plot name — the user's config list, the log\_every\_n logic) + the "PLOT done"
         summary — all INFO, as they should be. No source change.

D-571 | 2026-10-17 | The LOG wave — the shared CACHE boilerplate (iterative, the dedicated wave after the 19 per-level
         waves): C1 the 3 COMPUTE-PATH process lines of cache\_manager ("Executing heavy computation...", "Computation
         finished. Storing to cache '...'...", "Cache file and checksum successfully written.") from INFO to DEBUG — the
         phase chatter (the level's own Starting/Completed delimit the phase already; a cold run carried 7×3 = 21 of
         them at INFO). C2 the 3 OUTCOME lines stay INFO ("Cache successfully loaded and validated from ...", "Cache
         file not found at .... Forcing computation.", "Cache not allowed by configuration. Forcing computation.") — the
         per-level fresh-vs-cached fact, readable at a glance; the WARN/ERROR failure paths are untouched. Verified on
         the A2030 chain with one cache (GENERATE) removed: the recomputed level shows the esito at INFO + the 3 process
         lines at DEBUG; the 6 warm levels keep their single INFO esito. The cache\_manager mirror doc updated.
         Default-tier guard green.

D-572 | 2026-10-17 | The LOG wave — CLOSING (the milestone): the wave is complete — D-550 the structure (the per-step
         DEBUG duration, the closing line, the file floor at DEBUG), D-551… D-570 the 19 per-level waves (the iterative
         one-level-per-wave process, each reviewed on the target-level artifact log before the commit), D-571 the shared
         cache-boilerplate wave. The closing LONG=1 run: the FIRST close run had 1 transient failure (the test name was
         not captured in the job output — disclosed), the SECOND close run is green (1151 tests, skipped=24). The
         overview's LOG-wave bullet is flipped to COMPLETE (the milestone update).

D-573 | 2026-10-17 | The A2050 full-chain size-band fix (the new-workspace first run failure, Roberto's "not robust
         test" report — the investigation): the test is NOT broken by a library version — the embedded config dumps of
         the same run in the two workspaces are byte-identical EXCEPT the 7 path bytes (pydantic 2.14.0/2.14.1 serialize
         identically — diffed). The root cause is WORKSPACE-PATH-DEPENDENCE: the absolute base\_dir sits in the embedded
         dump, and the 7-char workspace rename (…/dsh/… → …/reversi-v2/…) changes 7 content bytes that the LZ4 match
         cascade amplifies into a ~48-byte compressed-size shift on the 517 KB file (same mkdtemp name: 517081 old /
         517129 new; the A2030 23 KB file shifts only +5 — 23559/23564, comfortable in its band). The 8-random-char
         mkdtemp tail is small (200-variant experiment on a real file: a 9-byte span, 517128-517137). The fix: the A2050
         band widened 516991-517091 → 516991-517191 (spanning both measured centers 517041/517089 with ~100-byte
         margins; still a gross-regression net) + the comment now documents the path dependence. The A2030 band is
         untouched. The mirror doc updated — and its TWO stale band values corrected in the same pass (A2050
         516692-516892 and A2030 23183-23283 predated the last re-pins). Note: yesterday's first-close-run transient
         failure in the OLD workspace was NOT this test (A2050 was in-band there) — it remains unidentified (the name
         was not captured) and never recurred.

D-574 | 2026-10-17 | The PUBLISH campaign — COMPLETE (the milestone): steps 4-5 executed by Roberto (the secret scan
         clean — the .env untracked, its values placeholders/public test data, the code references schema fields only;
         the final suite green; the first push of rcrr/reversi-v2 to GitHub). The new workspace
         /home/rcrr/base/prj/reversi-v2 (the fresh clone) is OPERATIONAL: the venv rebuilt from the pyproject manifest,
         the .env copied, the default suite green, and the D-573 size-band fix committed + pushed (the push/pull
         round-trip verified by Roberto). The old workspace /home/rcrr/base/prj/dsh stays in place (untouched — the
         R-600 ruling). The overview's PUBLISH bullet is removed (the campaign is done — the no-Done-bullets rule).

D-575 | 2026-10-17 | The forward roadmap established (the post-PUBLISH planning session): the overview Next-steps
         section populated with the seven open campaigns — FEATURE-SET, LATEX, MULTI-PLY, MOVE-PROB, ENDGAME-SOLVER,
         REGAB, TEST-BATCH (each with its scope, as recorded in the overview); and the open backlog (notes/ideas.md)
         seeded with two forward-looking ideas — I-021 (the ResNet extension of the logistic model: the Softplus-neuron
         term over the pattern-pair embeddings) and I-022 (the ANSI-C-to-Rust port). Notes-only change (overview.md +
         ideas.md); no source or test files touched. Drive-by: the overview's stale test\_mobility Suite cell corrected
         (31 → 33, the fresh gate measurement revealed the drift).
