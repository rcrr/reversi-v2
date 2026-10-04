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
