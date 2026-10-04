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
