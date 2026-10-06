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
