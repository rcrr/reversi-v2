# Decisions log — historical record

Format rules: notes/decisions\_rules.md (rigid — follow when appending to this file).

D-333 | 2026-09-29 | the decisions.md REPAIR + the split into 4 closed volumes + the 1000-line cap (Roberto: "Da D-237
         la formattazione si ROMPE. Avendo allargato i caratteri per riga dire di emendare la regola a 1000 righe.
         Spezza il file in 4: notes/decisions\_002.md ... notes/decisions\_005.md, sistema la formattazione con gli
         escape appropriati, e partiamo con un nuovo file decisions vuoto"). (1) THE DAMAGE (pre-existing, committed in
         the original sessions — git -S: the 11-space gaps first appear in the D-304 commit itself): (a) 36 internal
         11-space runs in D-304/D-305/D-306 — a newline + 10-space indent collapsed by a bad join (the content was
         INTACT); (b) the D-307 header glued onto the D-306 last line (a mid-line entry start); (c) 55 missing blank
         separators (D-263..D-327); (d) the inconsistent continuation indents (6 / 10 / 11 spaces vs the 9 house
         continuation — the D-184/D-186/D-204 stragglers, the D-263..D-283 zone, the D-284..D-332 zone); (e) 16
         mid-token line breaks (the D-209 rejoin rule: 5 underscore — rlmwf\_materializers, principal\_index\_count,
         save\_optimization\_checkpoint, is\_optimization\_cache\_consistent, test\_wrk\_optimize — 5 hyphen —
         threshold-independent, hand-computed, "su-corpus-3", per-position, stale-boxplot-label — 4 slash —
         min\_grad/min\_p\_fun\_decrease, POSITIONS/ANALYTICS/VALIDATE, T9/T6/T4-rate, D-184/D-186 — 2 filename dots —
         hlp\_final\_log\_print.py, wrk\_optimize.py); (f) 7 first lines over 120. (2) THE REPAIR: one uniform re-wrap
         of all 174 entries (D-159..D-332) to the house format (the D-NNN | date | first line, the 9-space continuation,
         the greedy 120 fill, the code-span-aware tokens — `test_prng`.md atomic) + the 16 rejoins + the separator
         restoration + the asterisk escapes (the rules.md house rule: math multiplications + globs, 15 new — 0
         stray-italic candidates left). CONTENT-PRESERVATION PROOF: the whitespace- and backslash-stripped text of every
         entry is identical before / after. (3) THE AMENDMENT: the volume cap 2000 -> 1000 lines (the ~120 wrap made the
         old cap a 4460-line run) — rules.md + this header carry the new cap. (4) THE SPLIT: the repaired open log (3484
         lines) into 4 closed volumes — decisions\_002 (D-159…D-206, 884 lines), decisions\_003 (D-207…D-257, 865),
         decisions\_004 (D-258…D-300, 879), decisions\_005 (D-301…D-332, 870), each under 1000 — and this file restarts
         empty, D-333 as its first entry. OBSERVATION (for Roberto, no action): the closed volumes 000/001 carry 53/99
         stray `|` continuation lines + 27/52 bare `*` (the pre-D-237 table-format and math-escape remnants the D-237
         re-wrap kept as content) — the closed volumes stay verbatim; a cleanup pass is his call.

D-334 | 2026-09-29 | the overview.md RESTRUCTURE (Roberto: "La sezione Where we are cresce continuamente e non ha un
         senso: è un'altra storia del progetto. Non dobbiamo disseminare la storia ovunque, dobbiamo solo tenere quanto
         è utile a gestire il progetto" + the 4 calls: rename "Current state", the e2e bullet out, the table
         re-gymnastic now, the MAX 10 bullet rule). (1) THE FINDINGS: the section grew 18 -> 431 lines (09-15), was
         condensed back to 18 at D-235/D-236 (09-19) — the same disease cured once WITHOUT a legislative guard — and
         re-bloated to 172 lines / 35 bullets in 10 days; the bullet audit: 22 campaign-history (incl. the 9 "format
         rules land on X" D-323..D-331 + the hlp\_anova cluster D-309..D-317 + the 2 docstring removals), 9 table/mirror
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
         Next-steps closed-ideas record out (it lives in ideas-closed.md); the 11-cell table re-gymnastic (hlp\_plot,
         wrk\_optimize, client, hlp\_config\_schemas, hlp\_gradient, hlp\_indexes, hlp\_optimize, hlp\_su\_analysis,
         hlp\_validate, hlp\_wmaps + the test\_hlp\_su\_analysis row) keeping the contract facts (the 13 PlotStyle
         knobs, the hi\_perf\_blocks field, the su-corpus lineage); the 2 stale su-corpus versions corrected (the
         random\_game row su-corpus-3 -> 5, the test-row pin su-corpus-4 -> 5 — verified in the code:
         \_GENERATOR\_VERSION = "su-corpus-5", the test pins it); the board.py suite fixed 246 -> 247 (measured: Ran
         247, skipped 15). The deeper narrative clauses of the hlp\_su\_analysis State cell (the D-295..D-305 framing)
         stay — the approved scope was the format clauses; a full condensation is a separate call. Nothing is LOST:
         every stripped clause exists verbatim in the decision log (D-306..D-331) and the mirrors — only de-duplicated.
         (4) VERIFICATION: notes\_format --check clean (0 pending rejoins), the source-vs-test suite cross-check 0
         mismatches, Current state 4 bullets <= 10. NOTE: rules.md grew ~2 lines past its ~150 budget (pre-existing
         overage) — the consolidation call is Roberto's.

D-335 | 2026-09-29 | the State-column NORMALIZATION of the overview tables (Roberto: "la colonna State e' da
         revisionare: non c'e' coerenza sulla lunghezza dello stato, ci sono continui riferimenti alla storia. Se una
         cosa e' complete e' complete" + the Test files table broken after the test\_hlp\_optimize row). (1) THE BREAK:
         a pre-existing blank line — the D-295 test\_hlp\_random\_play row deletion (commit eb59a3d) left the blank
         behind — split the Markdown table, the 4 following rows rendered outside it; removed. (2) THE NORMALIZATION:
         every State cell reduced to the D-117 grammar — the status word + the open/parked items ONLY; the descriptive
         prose is the mirror's job (the Doc column points to it), the D-NNN / I-NNN campaign references and the "moved
         from / renamed from / fix / N new tests / replaces X" clauses are the decision log's. A sweep of all 95
         mirrors' Open issues sections found exactly ONE open file-level item in the whole codebase — the wrk\_anova
         adherence-header wording defect (pinned by the probe; a source change awaits Roberto's call) — now in the State
         cell; the parked PRNG passettino (the Next-steps item) is in the prng.py cell; the two helper test rows say
         "complete (helper module, 0 tests)"; test\_mobility's stale "analyzed" becomes "complete" (the mirror: 26
         tests, all pinned, no open issues — the word is a remnant of the suite's birth, flagged to Roberto). (3) THE
         ORDER: both tables were in historical addition order, violating the header + the rule ("alphabetical by full
         path") — re-sorted (48 src + 47 test rows); the stale header parenthetical ("the package path sorts future
         packages first") is out. (4) THE HIDDEN BUG: the hlp\_su\_analysis cell (2682 chars) carried a RAW inner pipe —
         the "joint | None" type-union, a D-116 escape violation the re-wrappers never saw (the row never matched the
         5-pipe row shape) — gone with the cell; the reduction is what surfaced it. (5) THE LEGISLATION (rules.md, D-117
         clarified): the State cell = a status word + the open/parked items (each with its governing D-pointer if any);
         the description is the mirror's job, the campaign history the decision log's — the old "the D-pointer range"
         phrase, which had fed the D-NNN bloat, is retired. Nothing LOST: every stripped clause exists verbatim in the
         decision log and the mirrors. VERIFICATION: both tables contiguous (0 blank lines inside, 5 unescaped pipes per
         row, full-path alphabetical order verified), notes\_format --check clean.

D-336 | 2026-09-29 | the Test-data note of overview.md became a VERIFIED bullet list (Roberto: "Via D-215, teniamo una
         lista a bullet con un commento di cosa sono. Breve. verifica la lista."). The verification found the note STALE
         on three counts: (1) the rlm\_01 / rlm\_02 "DB dump" descriptions — the files were regenerated 2026-09-21 and
         are now unit-test configs (rlm\_01: the Design Matrix data structure, rlm\_02: the gradient worker — each
         file's own description field); (2) the note omitted three of the eight directory files: prng\_golden.txt (the
         committed 18436-line PRNG golden, 20 sections — measured), rlm\_05.json + rlm\_06.json (the SU-analysis
         experiment configs, the 2M / 100M tiers, ec 20, stopping at SU\_ANALYSIS — the names + descriptions read from
         the files); (3) "the per-file mirror docs cover them" — docs/test/reversi/data/ does not exist (no mirror docs
         for the data files) — the claim is out. The D-215 pointer + the "571\_141-row log verified 100%" campaign
         verification are out; the committed sample stays pinned by its present fact (the 1002-row stride — measured:
         1003 lines incl. the header). VERIFICATION: every bullet checked against the file on disk (the names, the
         description fields, the line counts), notes\_format --check clean.

D-337 | 2026-09-29 | the Next-steps REWRITE as the NON-prioritized TO-DO list (Roberto: "La lista NON ha priorita',
         decido io l'ordine. Tu scrivi solo le cose da fare in Inglese in maniera sintetica. Quindi Opzione A" — and, on
         my over-analysis: "Nia, stiamo scrivendo una TO-DO List, non stiamo facendo tutto della TO-DO List"). (1) THE
         OLD BULLETS OUT: the VVLONG "uninstrumented/KEPT" bullet (a frozen state, not an open item — the D-285/D-286
         record lives in the decision log + the tags.py header; the work is absorbed by the new tag item); the PRNG
         passettino bullet — DROPPED (Roberto: "non serve" — the ctor's MT init is a one-shot 312-iteration Python loop,
         negligible vs the batch kernels, the numba payoff is zero); the PROFILING bullet — CLOSED (done at session 58
         / D-299: the SU\_ANALYSIS cold compute profiled + optimized, bit-identical). (2) THE LIST (his 6 items,
         English, synthetic, NO priority — he picks the next item on demand, in his enumeration order): the duration
         tags (the 5 tags VVLONG/VLONG/LONG/PERF/DB + the tag-assignment technique re-verified + the LONG/VLONG/VVLONG
         shorter-equivalent analysis), the test sources (the code + docstring format, the D-267 criteria, the history
         documentation removed), the MOBILITY rework (the difference concept out — a MASK + the mover/opponent binary
         flag), the project README (English, like everything else), the worker sources (the format verified — ALL the
         sub-works: the history out of the docstrings, the 120-char reflow, the D-318 docstring conversion — when
         directed), the core + tools sources (board, pattern, feature, mobility, tools — the same sub-works). (3) THE
         LEGISLATION (rules.md, D-117 amended): the Next-steps "the LAST bullet is the next concrete action" clause is
         replaced by "the list is NON-prioritized (Roberto picks the next item on demand)." NOTHING is started: the list
         is written, every item waits his direction.

D-338 | 2026-09-29 | the two remaining non-"complete" State cells OUT (Roberto, on the two D-335 leftovers: "Rileggili
         bene, a me NON risultano" — and, after the explanation: "1: DROP il costruttore non e' mai critico nelle
         prestazioni. DROP FOREVER ... non lo voglio piu' vedere. 2: DROP ... pulisci wrk\_anova.md. Procedi!"). (1)
         prng.py — the "parked: the last PRNG passettino" cell -> "complete": the item was already DROPPED at D-337
         (removed from Next steps) but the table cell was left behind (a bookkeeping inconsistency of mine); the ctor's
         MT init (the 312-iteration Python loop) is never performance-critical — the DROP is FOREVER (the item is not
         re-raisable without a new rationale). (2) wrk\_anova.py — the "open: the adherence header" cell -> "complete":
         my D-335 over-reading — the item was the D-259 finding (5)(b) (the report header says "top {top\_k\_adherence}"
         while the report body lists every sub-variable; the bound applies to the CONSOLE lines only) — a PINNED,
         accepted wording quirk (verify\_anova C6/D7, the D-259 ruling "left as-is"), NOT an open item; the mirror's own
         Open issues section ended with "None." (no open issues). (3) THE MIRROR CLEANUP
         (docs/src/reversi/lm/wrk\_anova.md, per Roberto): the Open issues section now reads "None." alone (docs\_rules
         §4: closed items never appear there); the console/report split moves to the Architecture adherence bullet as a
         PRESENT contract (the CONSOLE lines are top-N, the REPORT the full list, the header wording the pinned
         deliberate quirk) — the finding's record itself lives in D-259 (5)(b). VERIFICATION: all 95 State cells are now
         "complete" (the 2 helper rows "complete (helper module, 0 tests)"), notes\_format --check clean on the touched
         files.

D-339 | 2026-09-29 | the overview tables' Suite-count SIMPLIFICATION (Roberto: "la tabella Source files ha la colonna
         Suite (live DB), mentre Test files ha la stessa colonna. Non credo ci sia valore in questa duplicazione ...
         Teniamo la conta dei TESTS solo sui tests? ... Tolgo commenti inutili? ... Mi piacerebbe che il nome del DOC
         fosse un hlink al file md. Pensaci e fammi tu una proposta." — and, on the proposal: "1: approvo. 2: Totale no,
         sarebbe da modificare in continuo. 3: OK. Procedi!"). (1) SOURCE TABLE: the Suite column is GONE (File |
         State | Doc) — 46 of the 48 rows duplicated their 1:1 test row's number, and the only 2 "via" notes
         (base\_model -> test\_logistic\_model, model\_weights -> test\_lm\_worker\_full\_chain) live in the mirrors
         (the Verified invariants); the header's "Suite = ..." sentence is out. (2) TEST TABLE: the single home of the
         counts, with a STRICT semantics — "Suite (standard run)" = the module's count under the standard pre-commit run
         (LONG=1, the live DB) — fixing the old column's ambiguity (some rows were default-tier runs, some DB-tier runs:
         test\_regab 48/0/0 was a DB run, test\_wrk\_final\_log\_print "5/0/1 (LONG: 6/0/0)" a default run); the only
         micro-marker kept is (+N VLONG) — exactly 2 modules (test\_lm\_worker\_full\_chain 9/0/1, the A2050 chain;
         test\_wrk\_su\_analysis 10/0/1, the 1e7 corpus); NO total (Roberto: it would need constant updating); no PERF
         parenthetical (PERF tests skip in the standard run and sit in the skip count; the mirrors carry the detail).
         (3) THE RE-MEASURE: all 45 runner modules individually + the full standard run — all green: 968 tests, 0
         failures, 24 skipped (75 s); the only count that moved vs the old table: test\_state\_machine 49 -> 50 (a test
         added since the last verification); test\_wrk\_final\_log\_print is now simply 6/0/0. (4) DOC AS HLINK: all 95
         Doc cells are markdown links to the mirrors ([path](path) — verified the notes\_format re-wrapper keeps the
         links atomic). (5) THE LEGISLATION (rules.md, D-117 amended): the Suite count lives ONLY in the Test files
         table, under the standard pre-commit run, with the (+N VLONG) marker; the Doc cell is a markdown link to the
         mirror.

D-340 | 2026-09-29 | rules.md RESTRUCTURE — R-numbering, bold titles, blank-line spacing (Roberto: "affrontiamo la
         ristrutturazione di rules.md. Prima di tutto il titolo: ... ('corpo legislativo'). Toliamo l'Italiano. Si usa
         solo l'Inglese quindi 'legislative body'. Poi introdurrei la NUMERAZIONE. R-000, R001, R002 .... E spazierei i
         bullet con una riga vuota. R-001 e il titolo li fare BOLD. Partirei maiuscolo ... Poi ho altre idee ... ma
         prima voglio sentire il tuo parere." — and, on the options: "Quindi facciamo SENZA DASH ... 1: R-001 : OK / 2:
         OK / 3: OK / 4: ordine attuale / 5: (a) / 6: (a) / 7: (la tua raccomandazione) / 8: eliminiamo il BUDGET. Le
         RULE possono essere aggiunte solo su esplicita approvazione. Lunghezza target 1-3 linee, solo se necessario
         superiore. / 9: OK / 10: BRAVA hai capito perche' le voglio numerare, poi il reference lo mettiamo nel LOG, e
         togliamo le D dalle rules. ma per ora NON ci pensare, poi le guardiamo una per una. Procedi!"). (1) TITLE:
         "corpo legislativo" out -> "legislative body" (the only other occurrence is a quote in the closed
         decisions\_000.md — frozen history, untouched). (2) NUMBERING: the 46 rules of the 9 sections get R-001..R-046
         in reading order (dash + 3 digits, consistent with D/I); the 3 Lifecycle bullets stay unnumbered (prose, not
         rules); the numbers are never reused. (3) FORMAT — the dash-less variant (verified in scratch: the literal
         dash-bullet spec is NOT stable under notes\_format.py, which rejoins the description onto the title line): a
         bold title line (**R-NNN — the topic**), a blank line, a 1–3 line description (longer only when it must be); a
         rule that fits becomes one bold line; 46 rules, the sequence verified intact. (4) TITLES: heuristic (first " —
         " / ": ") + hand polish on the long ones (R-006 the domain rule files, R-038 Mirror rule + the rigid mirror
         format, R-040 Docstrings: WHAT, never HOW, R-042 Provenance vs design pointers, R-043 Test docs, R-044 Probe
         docs); description initial letter capitalized. (5) BUDGET GONE (Roberto): the "~150 lines" paragraph is
         replaced by a Governance paragraph — a rule is added, amended or retired only on Roberto's explicit approval;
         the R-numbers are sequential, global and NEVER reused (an amendment keeps its number, a retirement leaves the
         gap); a rule is a bold title line + a 1–3 line description (or one bold line when it fits); Lifecycle PROMOTE
         now says "its numbered line". (6) R# COLLISION: R# (no dash) stays the code-issue id of the mirrors; R-003's
         reference list now reads "R-NNN (a rule of this register) ... R# (a code issue, never an R-NNN)" — the
         clarification lives where the reference families are defined (R-003, the overview format spec), not in the
         overview's Conventions. (7) DEFERRED (Roberto): the R-references in the journal + the D-pointers removal from
         the rules — reviewed rule by rule, later. (8) HYGIENE: the 5 trailing blank lines are gone (single final
         newline); the overview Index bullet updated to the new format. VERIFICATION: notes\_format --write idempotent
         + --check clean (290 lines, 9 sections, 46 rules R-001..R-046 in order); the normalized token diff against the
         pre-restructure file shows ONLY the intended changes (title, Budget -> Governance, "numbered" in PROMOTE, the
         polished titles, the R-NNN/R# clarification) — no content lost.

D-341 | 2026-09-29 | rules.md DOUBLE SPACING + the GOVERNANCE rewrite (Roberto: "Io aggiungerei uno spazio tra la fine
         di una RULE e la seguente. Sono un po' attaccate, facciamo 2 linee vuote. ... Semplifichiamo Nia: cosa serve
         questa frase: Every notes/ Markdown file is wrapped to ~120 chars/line (D-237)...? Io la rimuoverei, a meno che
         tu mi spieghi la ragione di tenerla." — and, on my explanation, his own proposal: "Cosa ne pensi di una cosa di
         questo genere? Governance: a rule is added, amended or retired only on explicit user approval. ... Lines are
         ~120 chars. When a new rules is best placed in a specific order a notation (**R-NNN.N — the topic**) can be
         used."). (1) DOUBLE SPACING: two blank lines between one rule and the next — the 37 intra-section rule
         boundaries (the rule -> heading spacing stays one blank line); the format is now legislated in the Governance
         itself ("two blank lines between one rule and the next"). (2) THE GOVERNANCE (Roberto's text, applied with my
         two fixes — the "a new rules" typo -> "a new rule", and the title templates kept as code spans for consistency
         with the first one): "explicit user approval" (generalized from "Roberto's"); the ~120 wrap kept minimal as
         "Lines are ~120 chars." — the D-237 origin pointer is out of the active register (the rule lives in the
         historical log + the tool's WIDTH=120 + the per-domain declarations: log\_rules.md, docs\_rules.md, the ideas
         headers, R-004); the "atomic code spans; the tables and the headings stay one physical line" clause out (the
         tool enforces the verbatim grammar; R-003 states it for the overview tables). (3) NEW: the R-NNN.N
         SUB-NUMBERING notation — a rule best placed in a specific position takes a dot-suffixed number of its parent;
         the zero-padded parents make it sort right after the parent in text order (R-012.1 between R-012 and R-013), so
         the register never renumbers. (4) The overview Index bullet aligned to "explicit user approval". VERIFICATION:
         notes\_format --write idempotent + --check clean (327 lines, 9 sections, R-001..R-046 intact).

D-342 | 2026-09-29 | R-002 AMENDED — the register's PRECEDENCE (Roberto: "R-002: This file: the active legislation.
         Every rules stated in this file has precedence on other notes, documents or decisions. Departure from the rules
         is possible only with explicit consent from the user. Cosa ne pensi?"). Applied from Roberto's text with two
         grammar fixes ("Every rules stated" -> "Every rule stated"; "precedence on" -> "precedence over"). The clause
         deliberately scopes the precedence to "other notes, documents or decisions": the constitution (AGENTS.md,
         R-001) and the user's direct instructions stay above the register — the resulting hierarchy is user > AGENTS.md
         > rules.md > other notes / docs / decisions (a historical decision can no longer overrule an in-force rule).
         The second sentence COMPLEMENTS the Governance (which governs amending the register): a departure from an
         in-force rule also needs explicit user consent — an approved departure that persists is recorded as a decision
         and amended into the rule (the same R-number, a new D-number). VERIFICATION: notes\_format --write idempotent
         + --check clean; R-002's description is 3 lines (at the 1-3 target).

D-343 | 2026-09-29 | R-003 CONDENSED — the missing DOMAIN FILE (Roberto: "Ora vediamo R-003 ... Non ti sembra un po'
         lunga, prolissa ??? quale e' la REGOLA ... il resto VIA! Dai fammi una proposta!!!" — and, on the proposal:
         "OK! Via! Vai Nia!"). (1) NEW notes/overview\_rules.md — the domain rule file the overview lacked (the only
         rigid-format file without one — the reason R-003 grew to 15 of the 46 lines, one clause per format
         campaign: D-116, D-117, D-334, D-335, D-337, D-339): the eight sections in fixed order, English + dates, the
         reference families (D-NNN / I-NNN / R-NNN / T-NN / R# / M#, with the "never an R-NNN" disambiguation), the
         two-table grammar (alphabetical by full path, one physical line per row, the \| escape, D-116), the State cell
         (D-117, clarified D-335), the Suite count in the Test table only (the standard pre-commit run + the (+N VLONG)
         marker, D-117, amended D-339), the Doc cell as a markdown link (D-339), the Current-state constraints (MAX 10
         bullets, NO bullet-per-campaign, D-334), the Next-steps constraints (open, non-prioritized, D-337), the Index
         rule (one bullet per notes/ file). (2) R-003 -> the 3-line pointer: the entry-point rule + "The format is RIGID
         in notes/overview\_rules.md" — the pattern R-005 / R-038 already use for log\_rules.md / docs\_rules.md. (3)
         CONSISTENCY (one line each): R-006's domain list + notes/overview\_rules.md; the overview's own header pointer
         (was "notes/rules.md — the overview bullet") -> notes/overview\_rules.md; the overview Index + the file's
         bullet; the AGENTS.md Layout enumeration + overview\_rules.md. VERIFICATION: notes\_format --write idempotent
         + --check clean (rules.md 314 lines, R-003 = 3 lines at the 1-3 target; overview\_rules.md 42 lines; every
         D-pointer moved with its text).

D-344 | 2026-09-29 | R-004 CONDENSED — the DECISIONS DOMAIN FILE (Roberto: "R-004 — notes/decisions.md Riusciamo a
         semplificare ?" — on the proposal: "procedi!"). (1) NEW notes/decisions\_rules.md (21 lines) — the domain rule
         file the decisions log lacked (the last rigid-format collaboration file without one): the entry grammar (one
         entry per decision including "leave as-is for now", append-only, a blank line before every entry, the
         `D-NNN | YYYY-MM-DD | the rationale` header on one line, the continuation lines indented EXACTLY 9 spaces — now
         written down for the first time: the grammar was practiced on every entry but legislated nowhere), the
         global/monotonic/never-reused D-numbers across open log + closed volumes, the D-209 style clauses (code spans
         for paths / names, escaped asterisks for the math multiplications), and the volumes & rotation (the open volume
         keeps its name; past 1000 lines — the D-118 cap, amended at D-333 — it closes at a session boundary as
         decisions\_NNN.md, zero-padded; a volume jump never cuts an entry). (2) R-004 -> the 2-line pointer: the
         identity (the OPEN historical decision log, append-only, the "why", consulted on demand) + "The format is RIGID
         in notes/decisions\_rules.md (the entry grammar, the volumes and rotation)" — R-004 is now the slimmest rule of
         the register (with R-005). (3) CONSISTENCY (one line each): R-006's domain list + the file; the decisions.md
         header ("Format: D-NNN | date | decision | rationale") -> the domain-file pointer; the overview Index + the
         file's bullet; the AGENTS.md Layout enumeration + the file. (4) SIDE EFFECT: the header edit required a --write
         on decisions.md, which normalized the whole open volume to the tool's canonical ~120 wrap (content-neutral: the
         token fingerprint identical, idempotent) — the post-D-333 hand-wrap drift is healed. VERIFICATION:
         notes\_format --write idempotent + --check clean (rules.md 312 lines, R-004 = 2 lines; decisions\_rules.md 21
         lines).

D-345 | 2026-09-29 | R-007 CONDENSED — the IDEAS PREAMBLES (Roberto: "R-007 le regole sono duplicate nel preambolo di
         ideas.md. Propongo di rimuoverle da rules, e scrivere solo che sono nel preambolo del file. Cosa ne pensi?").
         Verified first: the two preambles (notes/ideas.md + notes/ideas-closed.md, both "Format (D-235)") are the
         SUPERSET of the R-007 clauses — the format grammar (the `I-NNN | status | idea` header, the 9-space
         continuation, the blank line before every entry, the code spans), the status legend (idea / follow-up /
         in-progress, WITH definitions — the register never had those), the closure lifecycle (a closed idea MOVES to
         ideas-closed.md, compacted to the statement + the D-pointer + the outcome, in the same commit as the closing
         decision, "it never stays here"; the campaign history stays in decisions.md / the journal, the closed file is
         "the I-NNN index into it, never a narrative"), and the I-numbers (global, never reused or renumbered) — all of
         it in the preambles; the register carried the weaker copy. R-007 -> the 2-line pointer: the identity (the OPEN
         backlog I-NNN; ideas-closed.md the CLOSED ideas, done | dropped) + "The format (D-235), the status legend, the
         closure lifecycle and the I-numbering are in each file's preamble." No new file needed — the preambles ARE the
         domain files (self-contained, D-235, in both files). VERIFICATION: notes\_format --write idempotent + --check
         clean (rules.md 309 lines, R-007 = 2 description lines).

D-346 | 2026-09-29 | R-007 MICRO-AMENDMENT (Roberto: the pointer without the D-235 reference — "The format (D-235), the
         status legend, ..." -> "The format, the status legend, ..."). The origin pointer is redundant in the register:
         the preambles themselves carry it ("Format (D-235)" in both files) — the reference lives where it belongs.
         Amendment keeps the R-007 number (per the Governance). VERIFICATION: notes\_format --write idempotent + --check
         clean (rules.md 309 lines, R-007 = 2 description lines).

D-347 | 2026-09-29 | the LANGUAGE & COLLABORATION section, per Roberto's text (and: "Nel caso volessi spiegare il D-111
         pattern, spieghiamolo qui. ma no a REFERENCES to D-XXX."). (1) R-008 generalized: "Replies to the user:
         Italian." -> "Replies to the user: his own language (e.g. Italian)." — the register states the principle; the
         constitution (AGENTS.md rule 4) still pins the current instance ("Italian") — coherent, and per R-002's
         hierarchy the constitution sits above the register, so nothing is overridden; if the language ever changes, the
         constitution line changes with it. (2) R-010: the D-111 reference out — "One commit per item + a notes-wave
         commit at the campaign close." Nia's call on the offered inline explanation: NOT needed — the rule is
         self-contained (one D-number per fix campaign; one commit per fix item; the notes-wave commit = the batched
         notes updates — decisions / journal / overview — that closes the campaign); the D-pointer was pure provenance
         (the same principle as D-346: no D-XXX references in the rules; explain inline only when the rule is not
         self-contained — here it is). (3) R-009 / R-011: untouched, exactly as proposed. VERIFICATION:
         notes\_format --write idempotent + --check clean (rules.md 309 lines).

D-348 | 2026-09-29 | R-008 / R-009 / R-011 — the last D-pointers of the LANGUAGE & COLLABORATION section (Roberto: "Non
         hai rimosso (D-002), (D-004; AGENTS rules 2–3), (D-154). Vanno rimossi!"): my D-347 oversight — I removed only
         the D-111 we had discussed explicitly and left the three that were already in his proposed text. Removed:
         (D-002) from R-008, (D-004; AGENTS rules 2–3) from R-009 (the AGENTS pointer with it), (D-154) from R-011 — the
         three rules are now pure: the principle, no references. Counted after this commit: 46 D-XXX references remain
         in the register (Layout & tree, Naming & platform, Test discipline, Pipeline contracts, Docs, Code style) —
         awaiting Roberto's ruling on the full sweep (the D-340-deferred "poi le guardiamo una per una"). VERIFICATION:
         notes\_format --write idempotent + --check clean (rules.md 309 lines).

D-349 | 2026-09-29 | the JOURNAL section RETIRED — R-046 removed (Roberto: "La sezione 'Journal' contiene solo la R-046.
         ... Che e' ridondante con la R-005. Rimuoviamo completamente la sezione 'Journal'. Grazie!"). Verified before
         removing: 3 of R-046's 4 facts are in log\_rules.md (the global session numbering — Session entries item 1; one
         volume per 25 sessions or 2000 lines, whichever first, and rotation ONLY at a session boundary — the Volumes
         and rotation section); the 4th ("the step-N entries") is an ABANDONED practice — measured: 48 occurrences in
         log\_001 only, 0 in log\_000/002/003/004 (the current volume), and not legislated in log\_rules.md — the
         current journal practice is the flat bullet. R-005 already carries the pointer ("The session journals (rotating
         volumes; the format is rigid in notes/log\_rules.md)."). Retirement per the Governance: R-046's number leaves a
         gap (no renumbering); the register is now 45 rules in 8 sections (rules.md 302 lines; R-045 is the last rule).
         VERIFICATION: notes\_format --write idempotent + --check clean; no live R-046 reference outside the historical
         decision entries (which record the state at their time).

D-350 | 2026-09-29 | the PER-RULE D-POINTER REVIEW starts — item 1, R-012 (Roberto: "Proseguiamo con la review per
         regola. R-012 ... Diventa: [the rule without (D-003), (D-009), (AGENTS rule 7)]. Grazie!"): his text applied —
         the title loses (D-003), the description loses (D-009) and the AGENTS rule 7 pointer; the rule is now pure (the
         workspace is a git repo; the minimal .gitignore list; scratch/ disposable, never tracked). The three pointers
         were pure provenance — the AGENTS.md standing rules 1/7 and the .gitignore itself carry the operative facts.
         D-XXX references in the register: 44 (was 46 at D-348). VERIFICATION: notes\_format --write idempotent
         + --check clean (rules.md 301 lines).

D-351 | 2026-09-29 | the per-rule D-pointer review — item 2, R-013 (Roberto: "Proseguiamo con la review per regola.
         R-013 ... Diventa: [the rule without (D-006), (D-008; D-133: ...), (D-273)]. Grazie!"): his text applied with
         ONE declared fix — a stray closing parenthesis left over from the "(D-008; D-133: ...)" removal (the line reads
         "the tools/ and lm/ subpackages; the unit tests ..."), and `reversi` kept as a code span (the file's form). The
         rule is now pure: all Python sources under src/; the package `reversi` under src/reversi/, the core at the top
         level, the tools/ and lm/ subpackages; the unit tests in test/, a root tree mirroring src/ one file to one
         file. D-XXX references in the register: 41 (was 44 at D-350). VERIFICATION: notes\_format --write idempotent
         + --check clean (rules.md 301 lines).

D-352 | 2026-09-29 | the per-rule D-pointer review — items 3+4, R-014 + R-015 (Roberto: "Proseguiamo con R-014 e R-015.
         ... Diventano: [R-014 without (gitignored) in the title and without (D-010, D-011); R-015 without (D-007) and
         (D-273)]. Grazie!"): both rules applied from his text. R-014 is now: the .venv at the workspace root;
         pyproject.toml the minimal editable-install form, implicit requirements declared as they are hit — the
         "(gitignored)" note out of the title too (the .gitignore itself carries the fact, same logic as R-012); R-015
         is now the mirror rule in its purest form: src/reversi/X.py -> docs/src/reversi/X.md, the test files mirror the
         same way (the (D-007) / (D-273) origin pointers out — the mirror rule lives in AGENTS.md rule 5 and in the
         docs/ tree itself). D-XXX references in the register: 38 (was 41 at D-351). VERIFICATION: notes\_format --write
         idempotent + --check clean (rules.md 300 lines).

D-353 | 2026-09-29 | the per-rule D-pointer review — item 5, R-016 (Roberto: "Proseguiamo con R-016. ... Diventa:
         [tools/ holds the maintenance tools — the three tools, the NOT-package-tools / NOT-probes distinction, the
         a/b/c test, the pointer to notes/tools.md — without (D-248), (D-133) and the four-requirements parenthetical].
         Grazie!"): his text applied. The title loses "(workspace root)" (the fact is carried by AGENTS.md's Layout line
         and by the rule's own "It is NOT the package's src/reversi/tools/" clause) and "MAINTENANCE" is lowercased; the
         description drops the (D-248) and (D-133) origin pointers and the "(the four requirements — ...)" summary of
         notes/tools.md — the domain file carries its own four requirements, the register points (the R-003/R-004/R-007
         pattern). D-XXX references in the register: 36 (was 38 at D-352). VERIFICATION: notes\_format --write
         idempotent + --check clean (rules.md 299 lines).

D-354 | 2026-09-29 | the per-rule D-pointer review — item 6, R-017 (Roberto: "Proseguiamo con R-017. ... Diventa: [the
         rule without the trailing (D-176)]. Grazie!"): his text applied — the only change is the (D-176) origin pointer
         out of the description's end; the title keeps "(gitignored)" (unlike R-014's title, the gitignored-ness of
         build/ is part of the rule's reasoning: the data lives there BECAUSE the folder is gitignored — the
         self-contained-clone contract). The Layout & tree section is now fully pure: R-012..R-017 carry no D-pointers.
         D-XXX references in the register: 35 (was 36 at D-353). VERIFICATION: notes\_format --write idempotent
         + --check clean (rules.md 299 lines).

D-355 | 2026-09-29 | the per-rule D-pointer review — R-020 and R-021 RETIRED (Roberto: "Proseguiamo con R-020 and R-021.
         I le eliminerei. Non mi sembrano piu' attuali. Grazie!"): both rules removed from the register; the R-020 and
         R-021 gaps are permanent (R-numbers are never reused). VERIFIED before acting: the two TOPICS are still in
         force in the code — A2030/A2050 are live test-class labels (TestFullChainA2030 / TestFullChainA2050 in
         test/reversi/lm/test\_lm\_worker\_full\_chain.py) and the `*_for_current_level` helpers are injected by the
         StateMachine and consumed by 7 workers — but both conventions are already canonized in their canonical home,
         the Conventions section of docs/src/reversi/lm/logistic\_model.md (the A2xxx "intentional, not a typo — do not
         'fix'" clause; the injected-cache-helper contract with the R1-trap note), so the retirement loses nothing: the
         register was duplicating code-level conventions that the mirror doc owns. What was actually stale was the
         pointer: "the session-21 review" (a one-shot campaign session) and (D-069). Rules in force: 45 -> 43. D-XXX
         references in the register: 34 (was 35 at D-354). VERIFICATION: notes\_format --write idempotent + --check
         clean (rules.md 290 lines).

D-356 | 2026-09-29 | the per-rule D-pointer review — R-018 and R-019, closing the Naming & platform section (Roberto:
         "Proseguiamo con la sezione 'Naming & platform'. [the current R-018/R-019 text]. Diventa: [R-018 as 'Reversi
         (othello), NOT chess' with the column (A-H)/row (1-8) vocabulary, A1 = bit 0, H8 = bit 63, without
         (D-013, D-014) and without 'do not reorder or rename'; R-019 without (D-022)]. Grazie!"): his text applied.
         R-018: the title gains "(othello)"; the description gains the A-H/1-8 ranges and the H8 = bottom-right = bit 63
         clause, and loses the (D-013, D-014) pointer and the "do not reorder or rename" imperative (that convention is
         owned by notes/naming.md, which the rule points at). R-019: (D-022) out. One declared spacing fix: his
         "row(1-8)" became "row (1-8)" (consistent with "column (A-H)"). The Naming & platform section is now fully pure
         (R-018/R-019; R-020/R-021 retired at D-355). D-XXX references in the register: 32 (was 34 at D-355).
         VERIFICATION: notes\_format --write idempotent + --check clean (rules.md 290 lines).

D-357 | 2026-09-29 | the per-rule D-pointer review — R-029 SPLIT into three rules (Roberto: "FAmmi una prosta lean and
         clean per R-029 per favore. Poi la valuto e ti dico come procedere. Grazie!" — after my 7-line lean proposal:
         "E se facessimo tre RULES ??? [R-029 Suite tiers / R-029.1 Canonical order / R-029.2 Before git commit, full
         text]. Cosa ne pendi ?" — after my endorsement: "Procedi!"): the monster was three independent contracts fused
         in one rule (the tier semantics; the canonical module order of the runner; the pre-commit obligation) — each
         can be violated and checked independently, so it is three rules. His text applied verbatim, zero declared
         fixes: R-029 keeps its number and the tier contract (out: the A2050/1e6/1e7 examples, the predicate names, the
         order enumeration, and the (D-130; D-256)/(D-036) pointers — the tier content and the canonical order are
         carried by the run\_utests.sh header + the MODULES array, and the tier semantics by test.reversi.tags, both
         named in the rule); R-029.1 and R-029.2 are NEW rules using the R-NNN.N sub-numbering created at D-341, placed
         adjacent to the parent (the zero-padded parent sorts textually before R-030, so the placement at the end of the
         Test discipline section is correct). Rules in force: 43 -> 45. D-XXX references in the register: 30 (was 32
         at D-356). VERIFICATION: notes\_format --write idempotent + --check clean (rules.md 296 lines).

D-358 | 2026-09-29 | the per-rule D-pointer review — Test discipline R-022..R-027 (Roberto: "Proseguiamo con la sezione
         'Test discipline'. Mi fai una proposta di semplificazione, pulizia, revisione per R-022..R-028. La valuto e ti
         do indicazioni poi su come procedere." — after my 7-rule proposal: "R-022, R-023, R-024, R-025: OK. ... R-026:
         Ok, ma e' davvero applicata? ... R-027: OK. R-028: Ma perche' dobbiamo dire 'The multi-threaded OpenBLAS ddot
         is not bit-portable...'? tutti i float hanno il problema — scriviamo che i golden sui float per essere robusti
         devono usare assert\_close. Procedi con gli OK, e fammi una proposta migliore per la R-028."): applied the OK'd
         six verbatim — R-022 title-only ((D-065) out); R-023 title ((D-085) out), description untouched (already lean);
         R-024 (D-080, D-130: ...) out but the semantic hint kept — "the SKIP\_REGAB\_DB + LONG-tier check" is the
         contract, not provenance (verified against the db\_long\_gate body in test/reversi/tags.py); R-025 merged into
         one bold line (title + description said the same thing); R-026 (D-100) out; R-027 (D-124) out. R-028 UNTOUCHED,
         awaiting his verdict on the improved proposal (all floats, assert\_close for robustness, no OpenBLAS sentence —
         the full rationale already lives in the closecheck.py module header). His R-026 question verified in the code:
         the uniform @validate\_call(config=ConfigDict(arbitrary\_types\_allowed=True)) gate IS applied — 38 gate
         applications across src/reversi/lm/wrk\_\*.py (plus arbitrary\_types\_allowed in base\_model.py and
         pattern.py), and test/reversi/lm/test\_logistic\_model.py patches the factories by name in the importing
         module's namespace (patch('reversi.lm.logistic\_model.wrk\_config', ...), wrk\_positions, wrk\_features, ...).
         D-XXX references in the register: 24 (was 30 at D-357). VERIFICATION: notes\_format --write idempotent
         + --check clean (rules.md 294 lines).

D-359 | 2026-09-29 | the per-rule D-pointer review — R-028, closing the Test discipline section (Roberto, after my
         improved proposal: "Ho capito Nia, quindi R-025 va benissimo come e'. OK. R-026: ho capito, benissimo. OK!
         R-028: OK la tua proposta. Ottimo!"): R-028 applied verbatim from the approved proposal — title: "Float64
         pipeline-metric goldens" becomes "Float goldens" (his point: all floats have the problem, not just float64);
         the tolerances (rel 1e-9 / abs 1e-12) out of the title (they are the REL\_TOL/ABS\_TOL constants in
         closecheck.py — the code owns them); (D-127) out. Description: the OpenBLAS ddot sentence out (the mechanism is
         not the rule — the full rationale, the thread-count ULP study, the <=4e-14 drift, the enumeration of the pins
         that stay exact, already lives in the closecheck.py module header) and the example enumeration "(train\_loss,
         g\_norm, the tps read-back truncations)" out (the classes stay). Kept: the WHAT (float goldens must use
         assert\_close to be robust; the tolerances live in closecheck.py) and the boundary (what stays bit-exact
         assertEqual — without it, someone could "fix" the int/sha3 goldens to tolerant comparison). R-025 and R-026
         confirmed after the explanations (gate = a boolean condition deciding whether a test runs/fails; no performance
         gate = no test fails on a timing measurement, PERF is print-only; R-026 verified in the code at 38
         @validate\_call applications in src/reversi/lm/wrk\_\*.py). The Test discipline section is now FULLY PURE:
         R-022..R-029.2 carry no D-pointers. D-XXX references in the register: 23 (was 24 at D-358). VERIFICATION:
         notes\_format --write idempotent + --check clean (rules.md 294 lines).

D-360 | 2026-09-29 | the per-rule D-pointer review — the whole Pipeline contracts (RLM) section RETIRED, R-030..R-037
         (Roberto: "Ora affrontiamo la sezione 'Pipeline contracts (RLM)'. Ho una idea radicale, secondo me nulla di
         questa sezione deve rimanere nel file rules.md. Ogni regola e' documentazione che deve essere specificata in
         uno dei tre moduli: state\_machine, base\_model, logistic\_module. Fai una analisi accurata, dettagliata. dammi
         il tuo parere in merito. E se sei d'accordo, fammi una proposta delle modifiche alla documentazione dei
         sorgenti python o dei mirror docs. Procedi per favore." — after my per-rule verification + endorsement: "Via,
         procedi! Ottimo."): my radical idea was ENDORSED, and the analysis showed something stronger — ALL EIGHT
         invariants are ALREADY canonized in the mirror docs, so no source or doc change is needed: R-030 sentinel
         (state\_machine.md Architecture + Verified invariants + logistic\_model.md "The CREATED sentinels"); R-031
         failure semantics (state\_machine.md Architecture + invariants); R-032 unique names (state\_machine.md API
         table + invariants); R-033 gate split (state\_machine. md "The move gate is separate from execution" + the
         state\_machine.py:373 comment + logistic\_model.md "the gate split"); R-034 blackboard pre-declaration
         (logistic\_model.md Architecture "LMContext is the shared blackboard" + Conventions "Blackboard fields are
         pre-declared on LMContext..."); R-035 cache flow (cache\_manager.md load-or-compute + .SHA3-256 sidecar "a bad
         sidecar invalidates, never crashes" + state\_machine.md "Cache path" prefix-CONCATENATED verbatim + the
         state\_machine.py:178 comment); R-036 bool not a valid step (state\_machine.md Architecture + invariants);
         R-037 target-driven stop (base\_model.md "run(), the target-driven driver... a deeper target is a RESUME" +
         logistic\_model.md the CONFIG-first half). Three grounds: (1) the house pattern — R-006 "the register points at
         them, never duplicates them", the D-355 precedent (R-020/R-021) applied to all eight; (2) the invariants are
         module-specific, they do not bind outside state\_machine/base\_model/logistic\_model/cache\_manager; (3) the
         register copy was already DRIFTING — "the 8192-chunk verify" in R-035 is stale (8192 appears nowhere in the
         code; binio. compute\_sha3\_256 uses chunk\_size = 1 << 20, documented in binio.md), while the docs stay
         current per the docs\_rules.md current-state contract. Correction to Roberto's framing: the invariants are
         owned by FIVE docs (state\_machine.md x5, base\_model.md, logistic\_model.md x2, cache\_manager.md, binio.md),
         not three modules. Action: R-030..R-037 RETIRED and the "## Pipeline contracts (RLM)" heading removed (the
         empty section leaves, like the Journal section at D-349); the R-030..R-037 gaps are permanent. Rules in force:
         45 -> 37. D-XXX references in the register: 14 (was 23 at D-359). VERIFICATION: notes\_format --write
         idempotent + --check clean (rules.md 248 lines).

D-361 | 2026-09-29 | the per-rule D-pointer review — R-045, closing the Code style section (Roberto: "Proseguiamo con la
         sezione 'Code style'. Una sola regola, la R-045. Sono del parere che vada mantenuta, ma semplificata. Diciamo
         come devono essere le linee di codice. fine. Mi fai una proposta di semplificazione, pulizia, revisione." —
         after my proposal that KEPT the local 72–76 convention: "credo ci sia un fraintendimento. Io voglio le righe a
         circa 120 caratteri... non circa 72-76. Scriviamo semplicemnte questo. Le righe hanno una larghezza di circa
         120 caratteri. Semplice no? Riformula la proposta per favore." — then "Proposta accettata. la regola va bene
         come da te proposta."): R-045 AMENDED (a content change, not a pointer removal) to the one-line rule "Code
         lines have a width of about 120 characters." The target wrap width for code is now ~120 (a workspace-wide
         single width: code = docs = notes, consistent with the Governance paragraph "Lines are ~120 chars." and
         notes\_format's WIDTH=120), REPLACING "match the local file's wrap convention (the lm zone ~72–76) / default
         <=79 (PEP8) when convention-less". Out: the linter-context sentence, the (D-314) precedent, the docs/notes ~120
         (D-237) sentence (out of scope — the Governance paragraph + notes\_format carry it), and the reflow guard (the
         protection already lives in AGENTS.md rule 3: sources are modified only on explicit request, so an unrequested
         reflow stays prohibited; a full-file reflow of the still 72–76-wrapped files to ~120 remains a user-directed,
         deliberate act, the D-314 pattern). Code style is now a single one-line rule; the per-rule review (D-340) is
         down to its LAST section, Docs (R-038..R-044). Rules in force: 37 (unchanged — an amendment). D-XXX references
         in the register: 12 (was 14 at D-360) — all remaining refs now sit in the Docs section. VERIFICATION:
         notes\_format --write idempotent + --check clean (rules.md 243 lines).

D-362 | 2026-09-29 | the per-rule D-pointer review — the Docs section, CLOSING the review (Roberto: "Proseguiamo con la
         sezione 'Docs'. R-038 to R-044. Servono ? Non sono un duplicazione di quanto scritto in docs\_rules ? Non
         sarebbe meglio avere una sola entry che prescrive di applicare i docs\_rules ai docs ? Mi fai una proposta di
         semplificazione, pulizia, revisione." — after my per-rule mapping + proposal: "Applica la tua proposta. E' un
         ottimo passo in avanti. Non sono sicuro sia definitivo. Poi rivedo tutto e ti dico. Intanto applicala per
         favore."): the mapping was verified against docs\_rules.md (read in full — "format rules for the mirror docs
         (docs/)") and probe\_rules.md: R-038/R-039 are the mirror-doc-format side (duplicated by docs\_rules.md), while
         R-040..R-044 are NOT — they govern the docstrings/comments INSIDE the .py files (src/, test/, probes/), which
         docs\_rules.md does not cover, and probe\_rules.md carries no docstring rules (verified). Applied: R-038
         becomes the single identity + pointer "The mirror docs (docs/)" — one doc per source file, mirroring the source
         tree (AGENTS.md rule 5; the mapping is already carried by R-015) + the R-003-pattern pointer to
         notes/docs\_rules.md (the header, the 7 fixed sections, the forbidden-history list, the same-commit lifecycle,
         the test-doc variant); R-039 RETIRED — 100% duplication of docs\_rules.md §3.4 word for word ("OPEN R/M/T items
         only, with their pointers. If none: one line, None. Closed items never appear.") and its "(docs\_rules.md
         §4, D-114)" pointer was STALE anyway (current file: §3.4; §4 = "Forbidden in a mirror doc"); the R-039 gap is
         permanent. R-040..R-044 KEPT as pure code-style rules (the same genre as the R-045 just amended at D-361),
         D-refs removed: R-040 (D-224, D-226); R-041 (D-267/D-270 becomes "the test and probe docstrings keep their own
         rules, below", the "like the D-314 reflow" and D-317/D-318 out); R-042 (the D-150/D-146 examples + D-269/D-270
         out — the quoted "the D-106 re-pin" stays, it is the rule's example of what provenance IS, not a pointer of the
         rule itself); R-043 (D-267); R-044 (D-270). R-043/R-044 stay separate (R-044 carries its own exception and
         refers to "the test-doc rules"; rules in force 37 -> 36). D-XXX lines in the register: 12 -> 1, and that one is
         the R-042 quoted example — the register carries NO real provenance pointer anymore: the per-rule review (D-340)
         is COMPLETE. Roberto: not necessarily final — he will re-review the whole register and direct the follow-up.
         VERIFICATION: notes\_format --write idempotent + --check clean (rules.md 236 lines).

D-363 | 2026-09-29 | the escape REPAIR of decisions.md (Roberto: "per favore sistema intanto che decido come procedere
         il file decision. Nel testo di D-334 | 2026-09-29 ... si perde la formattazione e tutto diventa corsivo dalla
         parola hlp\_anova, mancano gli escape. Ma non lo abbiamo messo nelle regole di editing che devi usare gli
         escape ?"): ROOT CAUSE — not the asterisks, but the UNDERSCORES: the D-209 escape rule (decisions\_rules.md,
         the Entries bullet: "backslash-escaped asterisks for the math multiplications, so the Markdown renders without
         stray italics") covers the asterisks only; the BARE snake\_case identifiers in the prose toggle the renderer's
         emphasis (an unescaped underscore opens/closes italics) — D-334 carries 12 bare underscores, and the first pair
         (the one in hlp\_anova ... the one in hlp\_plot) is the long italic stretch Roberto saw. FIX: across the open
         volume, all bare underscores (222) and the two bare asterisks (the wrk\_\*.py of D-358/D-359) escaped (\_, \*);
         the two deliberate **R-NNN** template quotes (D-341) kept; the backticked identifiers untouched. DISCLOSED SIDE
         EFFECTS: (1) the canonical re-wrap normalized the hand-wrapped D-355..D-362 entries (content-neutral,
         token-identical 7846, idempotent); (2) the re-wrap exposed a BULLET TRAP — a continuation line starting with
         "36. D-XXX..." was parsed by the tool's numbered-bullet regex as a new bullet, producing a 13-space hanging
         indent; fixed by rewording the clause into parentheses ("...rules in force 37 -> 36). D-XXX lines in the
         register..."), the only content-level change. VERIFICATION: 0 lines with a 10+ space indent, 0 lines starting
         with digit+dot, notes\_format --write idempotent + --check clean (489 lines). OPEN: the rule gap — the
         decisions\_rules.md escape bullet covers asterisks only; extending it to the snake\_case underscores awaits
         Roberto's call. The closed volumes (decisions\_000..005) and the journals carry the same bare-underscore
         disease — untouched (a parked call).

D-364 | 2026-09-29 | the missing-BLANK-LINE REPAIR (Roberto: "Mancano le spaziature ora. Ogni Decision e' preceduta da
         una riga vuota. mancano ... Sono stanco Nia di fare il 'cane da guardia', come facciamo a essere sicuri che fai
         le cose bene? Possiamo scrivere un PROGRAMMA in Python che testa i formati. Dopo ogni editing lo lanci per
         controllo. Proponi tu qualcosa di definitivo. Perdiamo ore su queste stupidaggini."): the open volume was
         missing the mandatory blank line before 29 entry headers (D-335..D-363) — a SYSTEMATIC append bug of this
         session: every entry I appended (D-335..D-362 pre-checkpoint included, and D-363 today) was joined to the
         previous entry with a single newline instead of a blank line (verified in git: the D-362 commit already carried
         28 of the 29); notes\_format --check does NOT test the blank-line structure, so it passed green every time —
         that is the gap. FIX: one blank line re-inserted before each of the 29 headers; VERIFIED: 0 headers without a
         preceding blank line, 0 double blank lines, canonical re-wrap + --check clean (537 lines). PROPOSAL ON THE
         TABLE (awaiting his call — it is code, AGENTS rule 3): a read-only format-TEST program tools/notes\_lint.py,
         the definitive guard — the session's three bug classes become lint codes: (1) BLANK-LINE structure (a blank
         line before every D-NNN header, no doubles) [the D-364 class]; (2) ESCAPE discipline (no bare \_ and no
         unpaired \* outside code spans — the D-209 rule, extended to the snake\_case underscores) [the D-363 class];
         (3) BULLET traps (no continuation line starting with digit+dot, pipe, hash, or dash-space — the 13-space
         mis-parse class); plus the entry grammar (the header regex, the 9-space continuation, the monotonous
         D-numbers), the line width <= 120, and the idempotence against notes\_format --write; the same checks, tuned,
         for rules.md (the R-NNN headers, the 2-blank rule spacing, the real D-pointers flagged) and the journals (the
         session-block grammar, the 2-space continuation, the escapes). Run after every notes edit — red means no
         commit.

D-365 | 2026-09-29 | the FORMAT GUARD (Roberto: "Ok, PROCEDI." to the D-364 proposal): tools/notes\_lint.py — the
         read-only format test for the notes files, to run after every notes edit (red means no commit). The session's
         three bug classes are the permanent codes: BLANK (one blank line before every D-NNN header, no doubles —
         the D-364 class), ESC (no bare underscore and no unpaired asterisk outside code spans — the D-209 rule extended
         to the snake\_case identifiers, the D-363 class), TRAP (no continuation starting with digit+dot, dash, hash,
         pipe, or D-NNN-pipe — the 13-space mis-parse class); plus HEADER/INDENT/SEQ (decisions),
         RHEAD/RTITLE/RSPACE/DPOINTER/RSEQ (rules; the R-NNN.N sub-numbers sort inside their parent),
         JH1/JPOINTER/JSESSION/JINDENT/JBLANK (journals), WIDTH, EOF and CANON (the file must be its own
         notes\_format --write rendering — the tool's --check alone cannot serve: it passes even on non-canonical files,
         discovered during the build). DOGFOOD (scratch/lint\_fixtures, disposable): the fixture reproduces the
         session's bugs and every planted code fires; the real files pass. FIRST CATCHES ON THE REAL FILES (repaired in
         this same commit): rules.md 34 bare underscores escaped (the domain-files pointers, the code identifiers); the
         open journal 196 underscores + 2 asterisks escaped (the known disease — the open volume is now clean) + one
         1-space continuation line fixed to 2 (the D-362 turn hand-wrap slip, line 516). The closed volumes
         (decisions\_000..005) and the closed journals are out of the default lint set — they keep the same disease, a
         parked call. RULE: the decisions\_rules.md escape bullet extended (backslash-escaped asterisks AND
         underscores; D-209 extended at D-365) — the rule and its enforcer born together. VERIFICATION: notes\_lint
         green on the default set (exit 0), the fixture red on every planted code, notes\_format --write idempotent on
         the touched files. OPEN CALL: codify "notes\_lint green before commit" as a standing rule in AGENTS.md, and add
         the linter to the AGENTS.md tools/ layout bullet — both his territory.

D-366 | 2026-09-29 | the standing guard RULE (Roberto: "Prima di tutto OTTIMO! ben FATTO. Ora a me pare che dovrebbe
         andare in rules.md piuttosto che in AGENTS.md ... ma la regola VA MESSA. Poi ti chiedo ... tools/notes\_lint
         ... serve solo per decisions ... corretto ? Non per logs o per overview ... o rules .... Corretto ? Non sarebbe
         meglio dargli un NOME APPROPRIATO pre\_checkin\_guard\_decisions.py ??? E scrivere nella sua documentazione che
         IMPLEMENTA I CONTROLLI GRAMMATICALI per decisions .... E poi non dovremmo farne uno equivalente per ogni altro
         FORMATO (overview, rules, ...) ... cosa ne pensi ?"): R-047 "The notes format guard" PROMOTED to rules.md (his
         placement: rules.md, not AGENTS.md — his standing-instruction file stays his territory). Placement: a new final
         section, "Notes format guard" (one rule, its own section — the Code style precedent, R-045), NOT the Roles
         section: the guard is a process rule, not a file's role, and the end placement preserves the register's
         file-order == number-order invariant (the RSEQ check). The tool's docstring now says it explicitly: it
         IMPLEMENTS THE GRAMMATICAL CHECKS of the three notes formats (the decisions log per notes/decisions\_rules.md,
         the register per its Governance block, the journals per notes/log\_rules.md). CLARIFICATION of his three
         questions: (1) SCOPE — the guard is NOT decisions-only: the default set already covers the open decisions log +
         the register + the open journal (the closed volumes on explicit request); what it does NOT cover yet: the
         overview and the domain rule files. (2) NAME — a decisions-only name (pre\_checkin\_guard\_decisions.py) would
         bake in the wrong scope; Nia's recommendation: keep notes\_lint.py (short, accurate, the notes\_format.py
         family) — his call. (3) PER-FORMAT GUARDS — one guard, per-format linters inside (the lint\_decisions /
         lint\_rules / lint\_journal functions are the modular unit, not the file): the planned extension is the
         overview linter (the rigid grammar in notes/overview\_rules.md: the eight sections, the table grammar, the
         reference families) + the domain rule files — in this same tool, never N tools; his call on when. VERIFICATION:
         notes\_lint green on the whole default set (exit 0) after the R-047 addition; the register now 37 rules, 8
         sections, 246 lines.

D-367 | 2026-09-29 | the guard extended to EVERY notes format (Roberto: "Lo hai messo in rules, e' il posto giusto. In
         fondo: non mi convince ... La rule e' troppo complicata. SBAGLIATISSIMO. Devi dire lancia la guardia. FINE. La
         REGOLA e': 'LANCIA LA GUARDIA. Se fail no checkin.' Ma di tutto questo NON fare NULLA. Ci sto pensando a cosa
         fare. (a) OK (b) costruisci ora i controlli grammaticali stringenti per tutti i files in notes. TUTTI. Procedi
         per favore."): NOTHING was touched of the R-047 rule, its placement, the RSEQ invariant or the tool name —
         frozen pending his decision, exactly as ordered. (a) = the name stays notes\_lint.py. (b) EXECUTED: the guard
         now implements the grammatical checks of EVERY notes format, one tool, per-format linters. The NEW linters:
         overview (the OV- codes: the H1, the Format rules pointer section, the EIGHT sections in exactly the canonical
         order, the two tables with one physical line per row + alphabetical by full path, Current state MAX 10 bullets,
         Next steps no Done bullets), rulefile (the RF-codes for the seven domain rule files: the H1, the sections, the
         bullet grammar with the numbered 'N. ' continuations at 2+len(digits), the fenced blocks verbatim), ideas (the
         IA- codes: the D-235 entries I-NNN | status | text, the status legend, the 9-space continuation, the blank line
         before every entry, the monotone I-numbers). First-run grammar refinements: table rows exempt from the WIDTH
         limit (one physical line per row IS the table grammar), fenced code blocks verbatim (no checks inside), the H1
         exempt from the ESC check (it carries the file name: docs\_rules.md). FIRST-RUN REPAIRS on the current files
         (same commit): 553 bare underscores + 6 asterisks escaped (overview.md 475, ideas-closed.md 33, probe\_rules.md
         16, tools.md 14, docs\_rules.md 7, naming.md 3, log\_rules.md 3, decisions\_rules.md 2) + the canonical re-wrap
         of the four files that crossed 120 with the escapes (overview.md, ideas-closed.md, docs\_rules.md,
         probe\_rules.md — content-neutral, token-identical). VERIFICATION: the guard green on all 13 current notes
         files (exit 0); the fixture regression still fires on every planted code (14 violations). The closed volumes
         (decisions\_000..005, log\_000..003) stay out of the default set — the closed history; the parked escape
         cleanup remains his call; they are linted on explicit request.

D-368 | 2026-09-29 | the closed volumes linted and repaired to GREEN — no exceptions (Roberto: "Linta tutti i file
         chiusi, e correggili. Devono TUTTI passere. senza eccezioni. vai!!!"). The guard was first extended to the
         structures the closed history uses (the current strict grammar would have flagged them as bugs): the decisions
         linter now accepts the D-237 FIELD blocks (the 9sp pipe line + the 11sp continuations) and the inline 9sp
         bullets with their 11sp continuations (the tool's own canonical form — the last TRAP false positives); the TRAP
         code is narrowed to the real mis-parse tokens (a numbered start, a "# " heading, a D/I-NNN | header lookalike);
         the historical D-152 gap (a lost number) is legal — the SEQ check is now strictly increasing (a reuse or a
         reorder still fires). The journal linter accepts the historical "### " sub-sections with their column-0 prose,
         the 1-space " - " sub-bullets with their 3-space continuations, and the nested 2-space numbered items with
         their 5-space continuations. The tool itself: the ENTRY regex of notes\_format.py gains the letter suffix — the
         three D-156b/c/d sub-entries of decisions\_001.md, which the tool otherwise parses as prose and flattens (a
         one-character-class change, backward compatible, the only way to make the volumes canonical without destroying
         the entries). THE REPAIRS (same commit): decisions\_000.md — the old FIELD blocks normalized to the 9/11
         grammar (376 lines, bases 6/7/8/10) + 24 missing blank lines before headers; decisions\_001.md — the 8/10-space
         field region shifted to 9/11 (560 lines), 10 missing blanks, the D-156b/c/d column-0 prose block (58 lines)
         indented to 9, two raw math stars escaped by hand (the escaper pairs a raw \*\* with an already-escaped one);
         13208 bare underscores + 161 asterisks escaped across all ten volumes (the parked escape disease — executed and
         closed); log\_001.md — the historical "Steps 1+2" column-0 marker bulletized; every volume re-canonicalized
         with notes\_format --write (content-neutral, token-identical on all ten). VERIFICATION: the guard green on all
         10 closed volumes + all 13 current files (exit 0); the fixture suite still fires on every planted code (the gap
         case is now legal by design; a reuse case plants the SEQ). The closed volumes stay out of the default set
         (append-frozen history, explicit request).

D-369 | 2026-09-29 | the change-closure rules enter the register (Roberto: "Si procedi. Grazie." — approving the
         reformulated P2+P3 after the diagnostic of the tools.md gap, which this session exposed: the guard's own D-365
         commit had left notes/tools.md AND the overview Source table stale — notes\_lint.py appears in neither). New
         section "Change discipline", parallel to "Test discipline". R-049 the impact set (documents per change class):
         a closed table — a new tool in tools/ -> notes/tools.md (the requirements + the inventory) and the overview
         Source table (it tracks src/, tools/, probes/); a new probe -> the Source table; a new file in notes/ or
         docs/ -> the overview Index + the docs mirror; a notes-format grammar change -> the matching rules file + the
         format tool; a rule promoted or retired -> the register; any milestone -> the decision log + the journal; a
         multi-class change carries the union, a modification of an existing artifact carries the set of its class (the
         two soft points Roberto's "si o no" question exposed, now closed in the text). R-050 the pre-commit consistency
         check: before the final commit of a milestone, which class, which documents, are they all updated in the same
         commit; a deliberately untouched document is named in the entry with its reason. Roberto's rulings baked in: no
         D-pointers or AGENTS references inside the rule texts, the commit semantics live only in R-050, the section
         name is his to keep. The first milestone to run R-050 is this one: its impact set (a rule promoted) = the
         register + the decision entry + the journal — all updated. The stale tools.md/overview registration of
         notes\_lint.py stays open until Roberto orders the repair (his explicit call: not now).

D-370 | 2026-09-29 | the first exercise of R-050, executed (Roberto: "Hai aggiunto un nuovo tool: tools/notes\_lint.py.
         Ora aggiorniamo tutti i documenti in notes, consistentemente con le rules."): the impact set of "a tool in
         tools/" verified document by document. notes/tools.md — the inventory row for notes\_lint.py was MISSING
         (the D-365 commit carried the tool without its row, the tools.md GRADUATION gap): added now (category check;
         the per-format codes; read-only, exit 0/1; origin D-365/D-367/D-368). The overview Source table — verified to
         track src/ ONLY (all 48 rows are src/, the package src/reversi/tools/ subpackage being a different zone); no
         row to add: the Doc cell links the docs/ mirror, which exists only for src/ and test/, and the overview carries
         no guard mention to refresh. The Index bullet for tools.md ("the four requirements + the inventory") stays
         accurate. The verification found a FACTUAL ERROR in the R-049 text itself, corrected in the same commit: the
         tool line (the Source table tracks src/ only, not tools/probes) and the probe line (probe\_rules.md, if a rule
         changed — the probes carry no inventory; there is no overview table for them). The error had a known cause: the
         table zone census was misread (the 48-row count was all src/). The tool's own docstring deviates from the
         tools.md header grammar in two cosmetic points (the Usage line says python instead of .venv/bin/python; the
         SAFETY statement is implicit) — a source-file matter, left for Roberto's call. VERIFICATION: the guard green on
         the default set + tools.md + rules.md individually; the inventory now lists all five tracked tools of tools/.

D-371 | 2026-09-29 | the docstring of tools/notes\_lint.py aligned to the tools.md header grammar (Roberto: "Metti a
         posto il file sorgente. Approvato." — the explicit call for the two cosmetic points flagged at D-370): the four
         parts in the fixed order, in the idiom of the sibling tools (notes\_format, suite\_audit): WHAT IT IS (the
         check + the per-format mapping), USAGE (the .venv/bin/python command lines, from the workspace root, with the
         true default-set comment — the old one still said "decisions + rules + the open journal"), SAFETY (explicit
         now: writes nothing, a read-only report on stdout, exit 0/1), ORIGIN (D-365 born directly in tools/, D-367 the
         full-format extension, D-368 the closed volumes). Behavior unchanged (docstring only). VERIFICATION:
         py\_compile clean, the guard green on the default set.

D-372 | 2026-09-29 | the R-038 reformulation (Roberto proposed the text, and the approval was given before the commit,
         with two observations on the record): "One doc per source file, mirroring the source tree and the test tree;
         the rigid format is in notes/docs\_rules.md." (1) "and the test tree" lifts the test mirror to the rule level —
         before it was implicit only inside the format pointer; (2) the dropped parenthesis was a self-description of
         docs\_rules.md (a staleness hazard of the R-049 class — a document enumerating another document), and nothing
         normative is lost: the same-commit lifecycle it cited lives, and stays binding, in docs\_rules.md. The
         AGENTS.md reference goes with it, consistent with the standing decision that the rules do not reference
         AGENTS.md. The rule now states the scope (the 1:1 mirror of src/ and test/) and delegates the rigidity to the
         format file.

D-373 | 2026-09-29 | R-040 divided and moved, on Roberto's text: the two new rules land in the Code style section as
         R-045.1 (Docstrings: WHAT, never HOW — the content rule) and R-045.2 (Docstrings: no D-XXX, no reference to the
         decisions — the provenance rule; a #: code comment carries it only if fundamental — his text, without the R-042
         pointer). The renumbering under R-045 is what makes the move legal under the RSEQ invariant (file order ==
         number order): R-045, R-045.1, R-045.2 sit in the right section, strictly increasing — the collision I had
         flagged (a move as R-040 would have been red) is solved by his numbering. The R-040 number is retired by the
         division (a permanent gap, never reused) — consistent with the D-361 classification, which had already called
         R-040..R-044 "pure code-style rules" kept in place only for the number order. R-041's positional pointer ("the
         WHAT-only rule above") is now an explicit cross-reference (R-045.1 / R-045.2). R-041..R-044 stay in the Docs
         section (their migration is Roberto's call, in the pending reorganization). VERIFICATION: the guard green, the
         register canonical (268 lines, 39 rules + 2 sub-rules).

D-374 | 2026-09-29 | R-045 made its scope explicit (Roberto: "Bene Nia! Secondo te la R-045 comprende le docstring o
         dobbiamo renderlo esplicito ?" — and then: "Va bene Nia, aggiorna la R-045. Procedi!"). The title "Code lines
         have a width of about 120 characters" was readable as excluding the docstrings (code vs documentation); the
         house practice has always wrapped them at ~120, and now that R-045.1/R-045.2 (the docstring rules) sit directly
         below, the scope question would arise anyway. One-line description added, the title untouched: the limit
         applies to every physical line of a source file — code, comments, and docstring lines alike; docstrings are
         wrapped, not exempt.

D-375 | 2026-09-30 | R-041 retired, its format core reborn as R-045.3 (Roberto: "Procedi come lo ho scritto io. Le
         regole sulle docstring sono valide anche per i tests." — approving the retirement + the rule text he proposed
         the turn before, after my split proposal R-041 + R-041.1). The four-part descriptive format moves to the Code
         style cluster as R-045.3 (Docstrings: FORMAT), a sibling of R-045.1 (WHAT, never HOW) and R-045.2 (no D-XXX):
         the cluster is now complete and self-evident (width, content, provenance, format), and the Docs section no
         longer carries any docstring rule — the frozen emigration question shrinks from R-041..R-044 to R-042/043/044,
         of which R-043/R-044 (test, probe) fit Docs and only R-042 is open. Rulings on the record: (1) scope — the
         docstring rules are valid for the tests too, hence the unscoped title (no "(src/)"); R-043/R-044 remain the
         zone content rules, in the R-044 exception pattern. (2) The exemplar (hlp\_anova) drops with the rule: a
         pointer to a live file (it is on the format-pass to-do); the four parts are self-contained. (3) The
         past-management clause (retroactive conversion user-directed, one module at a time, never an agent initiative)
         is deliberately NOT legislated: it is campaign-execution state, and the "never an agent initiative" protection
         already lives in R-009 (source files are modified only on explicit request). (4) R-041 leaves a permanent gap
         (joins R-040, retired by division at D-373); no other live reference to it exists (verified tree-wide: only the
         rule title itself). VERIFICATION: the guard green on the default set, the register canonical (267 lines, 35
         rules + 5 sub-rules).

D-376 | 2026-09-30 | R-042 (Provenance vs design pointers) retired as redundant (Roberto: "R-042, secondo il mio
         giudizio e' ridondante con le altre regole. Io la ritirerei." — approved after my 70% analysis, then
         reformulated the surviving clause himself; "Procedi!"). Coverage map verified item by item: provenance OUT in
         the mirror docs is docs\_rules.md §4 (forbidden by name, with its examples), design pointers in the mirror docs
         are §3.2 (prescribed, with its example), provenance OUT in docstrings is R-045.2 (verbatim), tests and probes
         are R-043/R-044 — and R-042 mirror-docs clause was a pointer to a domain file the register must not duplicate
         (R-006), the same R-049 class staleness D-372 removed from R-038. The two non-redundant residues move into
         R-045.2 on the tighter text of Roberto: the definition ("the file's own change history") and the source-comment
         clause — his tightening ("as a summary, not a reference") is stricter than my "design pointer" formulation,
         which would have left a D-NNN reference legal in comments; now: no D-XXX, mai, the two in-text exceptions being
         the `#:` fundamental-provenance valve and the non-obvious summary, numberless. Resulting asymmetry with the
         mirror docs: the reference lives in the document (§3.2 prescribes it), the summary lives in the code. No live
         reference to R-042 (verified tree-wide: only the title; R-045.2 had already lost its R-042 pointer at D-373).
         Docs is now R-038 + R-043 + R-044 (the three doc zones); R-042 leaves a permanent gap (third after R-040 and
         R-041); the frozen block loses its last open item (the R-042 emigration) — only the text, placement and
         ordering invariants remain. VERIFICATION: the guard green on the default set, the register canonical (262
         lines, 34 rules + 5 sub-rules).

D-377 | 2026-09-30 | R-043 (Test docs) retired, the test zone absorbed into the docstring cluster (Roberto: "Capisco la
         obiezione e la accolgo, in parte. Io ritirerei la R-043, e introdurrei al suo posto una R-045.4 — Test
         docstrings: DEVIATIONS" — after my analysis showed R-043 was a zone-deviation rule, not a R-042 class
         duplication: verified on the tree, the test docstrings are light 1-2 lines carrying the mechanism (the
         "optionally how it is realized" vs the cluster never-HOW), the I-xxx ban lived only there (the cluster says D
         only), the light format was the only shield from the four-part format, and R-044 anchors on it). R-045.4 (Test
         docstrings: DEVIATIONS) — his skeleton, my fill, his approval of the full text: the same docstring rules bind
         the test docstrings (the D-375 ruling made explicit text), one deviation (the docstring may state how the check
         is realized: the mechanism, the preconditions, the postconditions), one specifica (the format is light, one or
         two lines — the four-part descriptive format is for functions with a contract). R-045.5 (No I-XXX in the code)
         — his text: no I-XXX reference in any docstring or comment of the Python code (src, test, or probe); it closes
         a real hole — the I-xxx ban never bound src, it lived only in R-043 (tests); the probe check-labels boundary is
         carried by the R-044 exception itself (the general rule stays clean). Rulings on the record: (1) the
         level-ordinal clause ("name the level, no drifting ordinals") is NOT re-enacted — Roberto:
         code-structure-specific, not legislation (the D-267 template is campaign material, the executed instance); the
         test format-pass to-do loses that one criterion, the rest (no D/I refs, no history) stays covered. (2) No
         internal rule references in the rule texts: R-045.4 is self-contained, "the four-part descriptive format"
         described by shape, no R-NNN / D-XXX anywhere in the two new texts. R-044 is left as-is this turn (Roberto:
         "come e' scritta non va tanto bene" — its rework is next turn). R-043 leaves the fourth permanent gap (after
         R-040, R-041, R-042); no live reference to it (verified tree-wide: none outside the append-only history). Docs
         is now R-038 + R-044 (the two doc zones). VERIFICATION: the guard green on the default set, the register
         canonical (267 lines, 33 rules + 7 sub-rules).

D-378 | 2026-09-30 | R-044 (Probe docs) retired, the probe zone absorbed into the docstring cluster (Roberto proposed
         R-045.6 as the mirror of R-045.4 — "La farei diventare: R-045.6 — Probe docstrings: DEVIATIONS" — and:
         "Procedi!" after my comments). R-045.6 (Probe docstrings: DEVIATIONS) — his text, with my one fix: "with one
         deviation: one exception:" was a duplication (the deviation IS the exception, one phrase suffices): probe
         docstrings are bound by the same docstring rules applied to the code, with one deviation: the probe's own check
         labels and item ids ("C5 … (I-013 …)") are the probe's vocabulary and stay. Rulings on the record: (1) the
         exception is deliberately unqualified by place — it saves the labels wherever they appear (docstrings,
         separator comments, asserted text) from the I-XXX ban of R-045.5; the boundary registered at D-377 now lives in
         R-045.6. (2) The one semantic loss, accepted: R-044's third sentence ("the text asserted and the surrounding
         comments follow the test-doc rules") is gone — the asserted text (assert messages) is now pure data, no longer
         bound by the no-D/I-refs duty; data is not documentation, consistent with R-045.5's "docstring or comment"
         scope. (3) Probe comments need no rule of their own: the general code-comment rules (the D-ref policy, the
         I-XXX ban) plus the label exception — symmetric with the test comments after D-377. The dangling "follow the
         test-doc rules" pointer (R-043 is gone) dies with R-044; no other live reference (verified tree-wide: only the
         title). The cluster is now complete and symmetric: the general rules (.1 WHAT, .2 no D-XXX, .3 FORMAT, .5 no
         I-XXX) plus the two zone rules (.4 test, .6 probe); Docs is left with R-038 alone (the docs/ territory); R-044
         leaves the fifth permanent gap (after R-040, R-041, R-042, R-043). VERIFICATION: the guard green on the default
         set, the register canonical (266 lines, 32 rules + 8 sub-rules).

D-379 | 2026-09-30 | six new rules enter the register (Roberto: "Le accetto tutte. Inseriscile per favore. Poi commit!"
         — accepting the six proposed on the sessantasettesima richiesta, after his summary of the code-writing and
         test-coverage discussion: "100% d'accordo ... queste regole le hai embedded" for the generic part, his four
         items for the rest). Code style (4): R-039 (PEP 8 is the base style; the code is readable — one-line rule);
         R-040 (the desirable size of a function is 20-30 lines — his number, framed "auspicabile", a norm not a
         sentence); R-046 (a new external dependency needs the user's explicit permission; the declaration in
         pyproject.toml follows the approval, never precedes it — R-014's "declared as they are hit" governs the timing
         of the declaration, this rule the decision, no conflict); R-051 (a new function is checked for duplication
         before it is introduced — the package, the test helpers, the standard library). Test discipline (2, my judgment
         on his delegation "mi rimetto al tuo giudizio"): R-030 (the documented contract is the specification of the
         tests — every documented behavior has a pinning test: return keys, the nan/None/0 conventions, exception types;
         a documented behavior without a pin is an Open issue — the docstring promises, the test pins, and the mirror
         pin principle extended from the docs to the docstring contract); R-031 (the three shapes of a test set — happy
         path, error cases (each documented error type raises), boundary and degenerate inputs; coverage by cases, not
         by percentages: no coverage tool in the house). PROVISIONAL NUMBERING (the agreed workflow: the rules are
         committed now, then the physical reorder WITHOUT commit on the current names, then Roberto's final numbers,
         then the final commit): placed in the existing gaps to keep RSEQ green — R-030/R-031 at the end of Test
         discipline, R-039/R-040 at the start of Code style, R-046 at its end, R-051 at the end of the register; the
         reordering settles the sections. Rulings on the record: (1) the dot notation is POSITIONAL, not a structural
         parent-child (Roberto's correction of my abbaglio: R-NNN.N sits after R-NNN and before the next top-level rule,
         at its most appropriate place — no hierarchy); (2) history is WISDOM, not a CONSTRAINT — no old-to-new number
         map will be recorded with the renumbering, the historical entries describe the world of their time. The
         intermediate reordered state will be RSEQ-red by design (no commit exists between the reorder and the final
         numbering, R-047 untouched). VERIFICATION: the guard green on the default set, the register canonical (296
         lines, 38 rules + 8 sub-rules).

D-380 | 2026-10-01 | the register is reordered and renumbered (Roberto's scheme: "Procederei secondo questo schema ...
         per il resto OK. Procedi con il commit!"). The sections stand in the natural order — the notes system (Roles,
         Language & collaboration, Notes format guard, Change discipline), then the artifact (Layout & tree, Naming &
         platform, Code style, Docs, Test discipline) — with the two moves settled in his review: the no I-XXX rule sits
         right after the no D-XXX one (the two no-reference rules side by side), and the pre-commit gate question closed
         with his table: the thematic sections stay, no "Before the commit" section, R-010 stays in Language. The
         renumbering: 46 title lines retitled, zero bodies (the no-internal-references ruling of D-377 pays off). The
         allocation is his: the numbers are ordered by value, within a section they step by ten, with wider margins at
         the section boundaries, the gaps reserve room for the section's future rules, the register starts at R-010
         (room for rules before the current first) and ends at R-860; the dot notation leaves the daily use (the
         docstring cluster is now the consecutive 520-590) and is reserved for the extreme cases. The Governance is
         amended on his lean text: "ordered from the smallest to the largest" replaces "sequential", with his by-value
         sequence as the explanation (R-510 < R-511 < R-511.1 < R-511.3 < R-511.17 < R-512 < R-600 < R-999); my step-10
         sentence and the R-010 rationale were cut by his "stiamo asciutti" (the R-010 rationale would go stale: a
         future first rule takes R-005 or R-008) — they live here, in the entry, not in the Governance. The old-to-new
         conversion table is recorded in the journal only (his ruling). VERIFICATION: the guard green on the default
         set, the register canonical (297 lines, 46 rules, no sub-rules).

D-381 | 2026-10-01 | the preamble of the register is corrected (Roberto: "Non mi pare sia corretta vista la campagna di
         changes" — he proposed the trimmed text; "Ok! Procedi."): the final clause "; the D-number on each line is the
         origin pointer into it" is removed. It is stale in two independent ways: (1) the rule lines carry no D-numbers
         at all any more — verified: zero occurrences in the register; the no-D-pointers and no-internal-references
         rulings of this campaign removed them; (2) after the D-380 renumbering the R-number itself no longer points at
         the origin — it encodes position (step-10 by value), and the number-to-decision pointer died with the scheme.
         The origin traceability now lives in the Lifecycle block below (PROMOTE and RETIRE happen in the same commit:
         every decision entry that adds or retires a rule is its origin record) — the pointer runs decisions to
         register, not the other way. One clause cut, three self-standing sentences. VERIFICATION: the guard green on
         the default set, the register canonical (297 lines, 46 rules).

D-382 | 2026-10-01 | the hist mechanism (Roberto: "vorrei cambiare entrambi i meccanismi ... Sviluppa una analisi
         approfondita, la presenti, poi ti do istruzioni su come continuare" — then the rulings: "1: (a) 2: (i) 3: si 4:
         OK 5: me lo proponi dopo il commit"). notes/decisions.md and notes/log.md are the two fixed current files; the
         closed volumes live in notes/hist\_decisions/ (decisions\_000…005) and notes/hist\_log/ (log\_000…003). Eleven
         git mvs, content-free: the current journal log\_004.md became log.md — the fixed path returns (its ancestor was
         the original log.md, rotated at D-055; the archives move to the folders). Rulings on the record: (1) the
         journal volume number is assigned at BIRTH (the H1 carries it; the unnumbered name is the address, the number
         is the identity of the session range); (2) the H1 is unchanged while the journal is current (content-free
         rename, the linters untouched); (3) the decisions-at-close / journals-at-birth asymmetry kept; (4) one D, one
         commit, the full impact set. Impact set: the 11 git mvs; tools/notes\_lint.py (the default set is now the fixed
         notes/log.md in the explicit list, kind\_of accepts log.md, the docstring paths to the hist folders; the stale
         R-047 docstring ref and the stale R-042 comment ref closed — behavior unchanged); the register R-040 (the
         closed volumes in hist\_decisions) + R-050 (title notes/log.md, the archived volumes in hist\_log);
         decisions\_rules.md + log\_rules.md (the scope lines + the Volumes-and-rotation sections); the three
         renumbering leftovers closed (overview\_rules.md R-003 to R-030, tools.md R-047 to R-200, decisions\_rules.md
         R-004 to R-040); the overview (the Current-state preamble + the Index volume bullets to the hist paths).
         Deliberately untouched, named per the pre-commit check: AGENTS.md — its layout bullet stays on the old
         mechanism; its rewording is proposed after this commit, his call. No history back-rewrite: the closed volumes
         and the old journals cite the paths of their time. VERIFICATION: the guard green on the default set (13 files,
         incl. notes/log.md), the register canonical (298 lines, 46 rules).

D-383 | 2026-10-01 | AGENTS.md aligned to the hist mechanism (Roberto: "Procedi con change di AGENTS come proposto. OK"
         — the approved symmetric proposal from D-382). The Layout bullet now pairs the two history artifacts —
         decisions.md (the open decision log; the closed volumes in hist\_decisions/) and log.md (the open session
         journal; the archived volumes in hist\_log/) — and it is shorter than the old one. The D-382 impact set had
         missed a second old-mechanism reference in the same file: standing rule 6 sent the session summary to
         notes/log\_NNN.md — now notes/log.md (same change, same commit). Named and left pending his call: rule 6's
         "promoted ... with its D-number" is a D-381 residue (the rule lines carry no D-number any more after the
         preamble fix; the number lives in the decision entry) — its rewording is his. VERIFICATION: the bullet per the
         approved text, consistent with the register (R-040/R-050) and the two rule files; the guard green on the
         default set.

D-384 | 2026-10-01 | the D-number cleanup of decisions\_rules.md + the four-digit pre-emption (Roberto, on my analysis:
         "1: OK 2: (a) 3: (B) 4: NO solo D-NNN ha il problema, le rules sono stabili ... 5: OK solo una. Procedi!").
         decisions\_rules.md: the last two D-provenance pointers removed — the escape bullet (D-209, extended at D-365)
         and the rotation bullet (the D-118 cap, amended at D-333); both texts stay self-contained (the why and the
         threshold are in the sentence), and the file now carries zero D-refs. Scope ruling: decisions\_rules only for
         this pass; the class-1 refs of the family (log\_rules, overview\_rules, docs\_rules, ideas, the tools.md
         preamble) wait for their own walk-through turn, and class 2 (functional examples) and class 3 (registry data)
         stay by design. The four-digit pre-emption: the D-number grows to four digits at D-1000, so the six D patterns
         of the two tools are widened from three to three-or-four digits (DEC\_ID, DEC\_HEADER, TRAP, D\_REF in
         notes\_lint.py; ENTRY, DANGEROUS in notes\_format.py) — zero behavior change on existing content (every
         D-number is three-digit today), and it removes the only hard deadline of the notes format: without it,
         at D-1000 the guard would go false-red (the header unparseable, an INDENT violation) and the re-wrapper would
         flatten the 9-space entry as prose. The R and I patterns are deliberately untouched (his ruling: the rules are
         stable, the ideas are far away). VERIFICATION: the guard green on the default set; a scratch fixture with a
         long D-1000 entry lints clean and survives notes\_format --write with the 9-space structure intact
         (idempotent); py\_compile clean on both tools.

D-385 | 2026-10-01 | the decisions.md PREAMBLE trim (Roberto, on my analysis: "1:OK 2:rimuovere 3:Procedi!" — the 3-item
         ruling on the header analysis). The 9-line functioning paragraph (the historical-log charter, the
         promotion/retirement mechanics, the D-number invariants, the volumes paragraph with the closed-volume history)
         is REMOVED: the header is now the H1 + the format pointer line, symmetric to notes/log.md. The analysis found
         the paragraph (a) STALE in two facts — the closed-volume path notes/decisions\_NNN.md is pre-D-382 (the D-382
         impact set updated every document but this file's own preamble) and "it grows without bound" contradicts the
         1000-line close — and (b) a pure duplication of canon that lives elsewhere: the charter in R-040, the
         promotion/retirement mechanics in AGENTS.md rule 6, the D-number invariants in decisions\_rules.md (the
         stronger global-across-volumes form), the volumes mechanics in the same file's rotation section. NOTHING moves
         to decisions\_rules.md: it is already self-sufficient (zero D-refs since D-384), and a growing volume registry
         would not belong in a stable format file. The volume history data (000: D-001…D-116, 001: D-117…D-158,
         002-005: D-159…D-332) is duplicated in the overview Index (each volume individually) and in each closed
         volume's own header — removed here, nothing lost (ruling 2: rimuovere). The two D-118/D-333 provenance refs
         disappear with the paragraph; the provenance stays in the entries themselves. Deliberately untouched: the
         closed volumes (volume 000 still carries its old preamble — frozen history), the D-333 entry's quote of the old
         paths (a frozen quote, correct at the time). VERIFICATION: the new entry is canonical under
         notes\_format --write (re-wrapped, idempotent), the guard green on the default set.

D-386 | 2026-10-01 | the ideas.md + ideas-closed.md HEADER trim (Roberto, on my analysis: "1: OK! 2: OK! 2: (i)
         Procedi!" — the (i) is the next-I ruling). ideas.md header: two annotations out — "Format (D-235)" (provenance,
         the same pattern as D-384/D-385) and "(I-008 is dropped: see ideas-closed.md)" (a one-off footnote on a
         specific number — I-008, the papers-collection extension, dropped at D-125; the record lives in
         ideas-closed.md, and the header's general closed-idea rule already answers the case, so the annotation was
         redundant). His proposed text applied with the code spans kept (his paste stripped the backticks — rendering
         artifact, confirmed in the ruling). ideas-closed.md header: the same "Format (D-235)" out (his ruling: in this
         commit; my class-1 census had missed it — the walk-through list grows by one). The next-I-number question
         (his): NOT tracked explicitly anywhere, and it stays that way (ruling (i)): the next code is derived — the max
         over ideas.md + ideas-closed.md plus one (today: I-021) — the same regime as the D-numbers; the guard keeps its
         per-file IA-SEQ, the cross-file collision check stays out of scope. VERIFICATION: notes\_format --write applied
         (idempotent), the guard green on the default set.

D-387 | 2026-10-01 | the ideas-closed.md HEADER trim — the last functioning sentence out (Roberto, on my analysis: "La
         togliamo!"). The move-mechanics sentence ("An idea MOVES here from notes/ideas.md, compacted to its statement +
         the execution (or drop) pointer + the outcome, in the same commit as the decision that closes it") is removed:
         the same rule already lives in the ideas.md header (the canon home — the file where the close action happens),
         and it was the only functioning in this header. The four remaining sentences are identity (Role + the done |
         dropped membership), the scope contract (the I-NNN index into the campaign history, never a narrative), the
         file's own format, and the cross-file invariant that licenses the next-I derivation. The wording nuance ("the
         execution (or drop) pointer" vs the open header's "the D-pointer") is not load-bearing: a dropped idea carries
         its D-pointer too (I-008: dropped at D-125). R-070 stays true without amendment ("the format, the status
         legend, the closure lifecycle and the I-numbering are in each file's preamble" — each preamble carries its own
         share). VERIFICATION: notes\_format --write applied (idempotent), the guard green on the default set.

D-388 | 2026-10-01 | the ideas-closed.md -> ideas\_closed.md RENAME (Roberto: "e' l'unico file con un dash nel nome
         invece che un underscore ... l'estetica inspira ordine, che va perseguito" — my analysis: the dash is an
         accident (no naming rationale recorded at D-235), and a mixed spelling leaves a class of wrong-ref errors the
         guard cannot see (the lint checks format, not path existence); ruling: "Procedi!"). git mv with rename history
         preserved (the D-382 pattern) + the 10 live refs in the SAME commit — the R-250 impact set, mandatory: the
         guard's default set carries the name literally, so a separate-commit tool update would kill the guard. The 10:
         the H1, ideas.md (the MOVES sentence), the overview Index, the register R-070, AGENTS.md (standing rule 8 + the
         Layout bullet), notes\_lint.py (module docstring, lint\_ideas docstring, kind\_of, default set);
         notes\_format.py has zero refs (path-agnostic). No collision: "ideas\_closed" existed nowhere before
         (verified). Frozen by design: the 47 historical refs (11 open decisions log, 13 journal, 12 closed decision
         volumes, 11 log\_003) cite the name of their time, and the 4 ODP-9 archive files stay hyphenated (frozen
         history, outside the living convention). VERIFICATION: the guard green on the default set (13 files, now incl.
         notes/ideas\_closed.md); the live-ref census re-verified after the commit.

D-389 | 2026-10-01 | the log\_rules.md WALK-THROUGH pass (the first class-1 file of the D-ref walk-through; Roberto: "Mi
         pare che vada tutto bene. Tuo parere?" — then: "Procedi come da tua raccomandazione."). Two surgical edits: (1)
         the "(D-237)" provenance pointer out of the scope line — "the prose is wrapped to ~120 chars/line" stands
         alone, the why lives in D-237 in the log; (2) the rotation bullet 5 clause "The current journal is
         notes/log.md" trimmed — the third occurrence of the same fact in the file (scope line + rotation bullet 1) —
         leaving the bullet as its own rule: "The archived volumes are read-only except factual corrections."
         Deliberately KEPT (named in the analysis, his ruling confirms): the "One-off 2026-08-29 renumbering" bullet of
         the Session-entries section — it is not a provenance pointer but the reading key for the
         frozen-but-inconsistent history: the old commit messages keep their original labels (08-29 "session 11") while
         the volumes were rewritten with the global numbers (sections 14-17), and the 08-28/29 entries count RUN tests
         in the first slot, a real deviation from the bullet-3 grammar (D-054 records the action, not the key); class-3
         interpretive data, the data-stays discipline. The file is otherwise clean: the D-382 update is correct (hist
         paths, birth-assigned numbers, verbatim H1 + pointer), nothing stale. VERIFICATION: the guard green on the
         default set.

D-390 | 2026-10-01 | the log\_rules.md bullet-4 DEPERSONALIZATION (Roberto, on my analysis: "Procedi, usa la variante
         lowercase."). The close-session rule no longer carries a personal name: "A session Roberto closed ends with a
         'Session closed (Roberto).' bullet" becomes "A session closed by the user ends with a 'Session closed by the
         user.' bullet" — the legislation's "the user" (lowercase, the 4 normative places: the register preamble, R-100,
         the dependency rule, AGENTS rule 4) instead of the last personal name in normative text. Mapped impact,
         verified: the guard enforces no such text (neither tool references "Session closed" — unlike the JPOINTER
         pointer line and the J\_H1 volume header, the close bullet is not a verbatim-forced element), so no tool
         change; the 8 historical close bullets (log\_000: 3, log\_001: 1, log\_003: 3, log.md session 90: 1; log\_002:
         0) keep their text — frozen history, the D-382/D-388 discipline; the next close writes the new text.
         VERIFICATION: the guard green on the default set.

D-391 | 2026-10-01 | the naming.md DEPROVENANCE pass (Roberto, on my analysis; rulings: the title = his first option,
         the header keeps "and replies" per my lean, the new verification sentence as proposed, AGENTS.md deferred). Six
         edits, one file: (1) the H1 — "Naming convention (canonical, read once, apply always)" (tone, not content:
         "canonical" is already the header's single-source-of-truth clause) becomes "Reversi domain naming convention";
         the guard does not force rule-file H1s verbatim (RF-H1 only asks for "# "), so the title is free. (2) The
         header paragraph — "Recorded 2026-08-26 on Roberto's explicit instruction, after rejecting T08 (report §5.8):
         ..." (date, personal name, T08, report reference: all of it lives in D-013, volume 000) is reduced to the
         charter: "This file is the single source of truth for board vocabulary in this workspace — code, docs, notes,
         and replies all follow it." — the four-media form kept on purpose: the failure mode that created this file was
         an agent analysis importing chess vocabulary, so "replies" is the medium where the problem happened. (3) The D8
         section header loses "(canonical, fixed 2026-08-26)". (4) The D8 body loses "by Roberto's decision (D-014)" and
         the third occurrence of the A1/H8 facts — verified that nothing is lost: the bit mapping stays in the
         Board-vocabulary and Bitboard sections. (5) The verification paragraph: the "(T16, D-014)" provenance out, and
         — a correction to his proposal, verified — there is NO probe of the independent derivation (probes/ carries no
         board/D8 probe): the independent anchor is in the tests — the literal golden constants `ar_*` of
         test/reversi/test\_board.py pin `bitboard_transformations` / `bitboard_anti_transformations` cell-by-cell
         against values independent of the implementation under test; the sentence now names that anchor. (6) The
         reading-rule paragraph loses the "report §6 item T16" tail. The D-013/D-014 Index pointers in the overview stay
         (class 3); the two class-1 refs in the AGENTS.md Naming section are named and deferred (his file, alongside the
         rule-6 pending item). VERIFICATION: the guard green on the default set.

D-392 | 2026-10-01 | the probe\_rules.md DEPROVENANCE + cleanup pass (Roberto, on my analysis: "Procedi con pulizia come
         da tua proposta lean"). Eleven edits to probe\_rules.md (92 -> 80 lines): (1) the D-104 O1 anecdote out of §1 —
         "It exists because tests can be tautological" stands alone, the story lives in D-104; (2) (D-006) out of the
         NOT-list; (3) the scratch/ bullet: the tools/ inventory list out (canon: tools.md + R-340) and the
         pre-session-30 decay anecdote out; (4) (the D-065 base) out of the artifacts bullet; (5) the MEASUREMENT-tools
         bullet compressed to the probe-domain fact (the §5.2 sweep is the verify\_\* probes only; their artifacts under
         build/tmp) — names, the durations/counts descriptions and D-250/D-132/D-243 out (inventory canon: tools.md; the
         a/b/c boundary: R-340); (6) "(the D tiers)" out of the §4 table — unexplained jargon, the house concept is
         "suite tiers" (R-820); (7) §5 item 1: "docs\_rules.md §5.1" -> "docs\_rules.md" (that file has numbered items,
         no 5.1 — the pointer stays, the notation is fixed); (8) §5 item 4: the "(docs\_rules.md §5.4)" ref out — the
         sentence is complete alone; (9) the §5 pre-session-30 nine-probes anecdote out — the hub-centralization rule
         stands; (10) "(the o1\* family)" out of §6 — the files no longer exist anywhere (only
         notes/analyses/classification.md mentions them); (11) section 7 "Baseline (session 30)" deleted whole: a
         historical snapshot with no normative force, canon home the frozen session-30 journal, no cross-ref points at
         it, and its "awaiting ruling" item (verify\_lm\_worker\_config E2/E3) was stale. Plus the overview Index
         bullet: "the baseline" out (a pointer into the void after (11)). VERIFIED before the cut: the hub probe still
         pins the active-level count / commented imports / worker-list shape (docstring: "PIPELINE COMPLETE"); 24
         probes, all verify\_<module>.py; the tests write build/tmp; no external ref to §7 (AGENTS x3, tools.md,
         R-060/R-250 and docs\_rules.md §5 point at §1/§5/§6 only). ADJACENT, named and not touched: R-340's enumeration
         names 3 of the 5 live tools (measure\_suite.py, notes\_lint.py unnamed) — for the register re-review. CENSUS:
         this file was not on the 3-file remaining class-1 list (that list was zone-scoped, not whole-file); a
         whole-file census of the live notes now reads: overview 25 (class 3), overview\_rules 6, docs\_rules 6,
         tools.md 13, probe\_rules 7 (0 after this pass). VERIFICATION: the guard green on the default set.

D-393 | 2026-10-01 | the tools.md DEPROVENANCE pass (Roberto, on my analysis; he singled out the table — "La tabella,
         colonna origin. Serve?" — and approved the lean: "Procedi con il tuo lean"). The origin column deleted (5
         columns -> 4): it is 100% provenance (10 of the file's 13 D-refs), its data has two canon homes (the mandatory
         docstring Origin item of §3 — verified present in all five tools — and the graduation decision+journal entry of
         §5.2), and it serves no function of the table, which is the at-a-glance spec (what it does, what it writes —
         the safety data of §2.4 and the R-250 impact set). The asymmetry is deliberate: the what-it-does /
         what-it-writes columns stay because they are spec, not history. Nine edits total: (1) the origin column out;
         (2) (D-248) out of §1; (3) (D-133) out of §1 — the five subpackage names stay, verified exact against
         src/reversi/tools/; (4) §2.4: "the D-237 wrapper" -> "the re-wrapper"; (5) §2.4: (the D-065 base) out; (6)
         §5.3: "(the docs\_rules §5.1 same-commit spirit)" -> "(the docs\_rules.md §5 same-commit rule)" — the same
         notation bug fixed in probe\_rules at D-392 (that file's §5 is a numbered list, no 5.1); (7) the table:
         "the D-237 block grammar" -> "the block grammar"; (8) the table: "(D-132)" and "the baseline of the D-130
         tiering" -> "the baseline of the tiering"; (9) the table: the notes\_lint row's per-format code enumeration out
         — verified stale against the code: RTITLE no longer exists (the register codes are RHEAD/RSEQ/RSPACE/DPOINTER)
         and the journals are missing JH1/JBLANK (the code carries five journal codes); the functional description stays
         (the six format families + WIDTH/EOF/CANON; the R-200 pointer kept — a register cross-ref, not provenance). The
         §3 ORIGIN header item stays: it is the rule that gives the origin data its home in the docstrings — the rule
         stays, the table's copy goes. VERIFIED: five rows = five tracked tools, the what-it-writes cells match every
         docstring; the file's D-ref count 13 -> 0. ADJACENT, named and not touched (source files, Roberto's territory):
         measure\_suite.py's docstring carries "on Roberto's GO", docs\_format\_audit.py's the "D-239 campaign"
         narrative, notes\_lint.py's the stale RTITLE. VERIFICATION: the guard green on the default set.

D-394 | 2026-10-01 | the overview\_rules.md DEPROVENANCE + de-personalization + grammar-completeness pass (Roberto, on
         my analysis: "Procedi con il tuo lean!"). Seven edits: (1) the "eight sections" bullet corrected — the file
         said "Exactly the eight sections, in exactly this order", but the overview carries NINE H2s and the guard
         (OV-SECS) forces the FIRST to be the pointer section "Format rules (rigid ...)" before the eight; the rules
         file had never documented it — the guard's own docstring says "the Format rules pointer section, then EXACTLY
         the eight sections"; the bullet now states both facts (pointer section first, then the eight in order) —
         additive: nothing changes in overview.md or in the guard, the rules file aligns to the grammar the guard
         already enforces; (2) (D-116) out of the table-escape rule; (3) (D-117, clarified D-335) out of the State cell;
         (4) the Suite-count (D-117, amended D-339) out; (5) the Doc-cell (D-117, amended D-339) out; (6) (D-334) out of
         the no-bullet-per-campaign rule; (7) the Next-steps (D-117, amended D-337) out AND de-personalized per D-390:
         "(Roberto picks the next item on demand)" -> "(the user picks the next item on demand)" (the register and
         AGENTS use "the user" in the normative places). All the rule sentences are self-sufficient without the refs:
         the "amended D-NNN" forms are genealogy, and genealogy has its home in the decision log — unlike the log\_rules
         renumbering bullet, which is a reading key explaining a deviant form actually met in the frozen volumes. KEPT:
         the R-030 pointer (a live legislation cross-ref, the class kept in tools.md) and the reference-families line
         (class-3 reading key: it defines the permitted id vocabulary — T-NN, M# and session N are dormant in the
         current overview, verified, but a family definition lives independently of current use). VERIFIED: the actual
         overview.md carries the nine H2s in the exact order (pointer + the eight); the guard's SECTIONS tuple matches
         the bullet's list; the overview Index bullet for this file stays accurate ("the eight sections, the table
         grammar, the cell rules, the reference families"), no change needed. The file's D-ref count 10 -> 0, personal
         names 1 -> 0. VERIFICATION: the guard green on the default set.

D-395 | 2026-10-01 | the overview.md FIRST-PASS DEPROVENANCE (Roberto: "Controlla overview.md ... ci sono piccole
         referenze alla storia qui e la'" — on my analysis: "Procedi con il tuo lean. Poi vediamo altre cose ...
         Procedi!"). This file is not a rules file: it is the entry point, and by design it CARRIES the class-3
         registries (the Index with its D-pointers, the Source/Test tables, the test data) — the D-391 ruling
         ("the D-013/D-014 Index pointers in the overview stay (class 3)") keeps all of it untouched. The pass touches
         only the four prose sections (Conventions, Environment, Current state, Next steps): nine edits — (1) the
         Conventions naming bullet: (D-013) out, the live pointer "Full text: notes/naming.md" stays; (2) the D8
         slot-order convention: (D-014) out — the technical fact stays (a code convention, not just vocabulary); (3) the
         test-artifacts bullet: (D-065) out; (4) the Environment venv bullet: D-010 out, "(gitignored)" stays; (5) the
         Current state intro loses its third sentence, "MAX 10 bullets, no bullet-per-campaign (D-334)." — a format
         reminder whose canon home is overview\_rules.md (and the guard's OV-CUR); the first two sentences stay — the
         reading key (where the session-by-session history and the file-by-file state live); verified: the guard counts
         only the "- " bullets (4 today, MAX 10), so trimming the intro cannot affect it; (6) the docstring-style
         bullet: (D-318) out, the live pointer "(rules.md)" stays; (7) the TEST-sources item: (D-267) out — ruling on
         the flagged nuance: the item is a work label, the criteria live in the decision log; (8) the WORKER-sources
         item: "the D-318 docstring conversion" -> "the docstring conversion"; (9) the register item: "after the D-380
         renumbering" out (provenance) and de-personalized per D-390 — "The register re-review (the user); the guard
         rule text (R-200) awaits the user's call." (R-200) kept: a register cross-ref. Ruling on the second nuance:
         "the D-333 rotation" x4 in the Index STAYS (class-3 registry annotation, the D-391 discipline). VERIFIED: the
         "19-level pipeline" fact is current — the hub pins "V3c 19 active levels" (the "18 active levels" lines in its
         docstring are re-pin history); 968 tests matches the canonical LONG run. The four prose sections: 9 D-refs + 1
         personal name -> 0; the class-3 registries (Index, tables, test data) untouched. VERIFICATION: the guard green
         on the default set.

D-396 | 2026-10-01 | the overview/overview\_rules ROLE-SPLIT, first section (Roberto: the two files have two natures —
         "uno dovrebbe avere i fatti dello stato, l'altro le regole"; "ogni regola espressa in overview debba essere
         rimossa, con l'unica eccezione di: [the pointer sentence]"; on the title: "secondo me e' incorretto e
         ridondante con la rule. Io starei semplice con: 'Format rules'" — "Ok, procedi!"). The first section loses its
         prescriptive title: "Format rules (rigid — follow when editing this file)" -> "Format rules" — the title was a
         rule in disguise ("follow when editing this file") and redundant with the body, which is already exactly the
         sole surviving sentence: "The rigid format rules for this file live in notes/overview\_rules.md. Consult it
         before editing." The ruling is a three-file, one-commit change — the critical finding: OV-SECS had the old
         title HARD-CODED (prefix "Format rules (rigid"), so title without guard = red = no commit: (1) the overview.md
         title; (2) tools/notes\_lint.py — source, on his explicit direction via the title ruling (the only source file
         touched in the whole deprovenance arc): the check is now an EXACT match (secs[0][1] != 'Format rules'), not a
         prefix — a prefix would still accept the old title (the point of the change), and OV-H1 in the same function is
         already exact; error message updated to 'the first section must be "Format rules"'; (3) overview\_rules.md:
         the D-394 bullet that quoted the title verbatim in a code span follows. Verified: the guard checks only the
         pointer section's TITLE, never its body (the sentence is not verbatim-forced — unlike the journal J\_POINTER);
         no other live file references the old title (the frozen D-394 decision/journal entries quote it — frozen
         history, untouched). VERIFICATION: the guard green on the default set; a negative test in scratch/ (old
         title -> red OV-SECS with the new message, new title -> green); the standard pre-commit run.

D-397 | 2026-10-01 | the overview.md INDEX MINIMALIZATION + the overview\_rules.md amendment (Roberto: the Index bullets
         carry the file's identity and nothing else — six worked examples + "E avanti cosi" — and on the amendment: "Va
         bene la tua proposta di emendamento della overview\_rules!"). Fourteen edits to the Index: (1) the intro
         sentence deleted — "The docs/ mirrors (one per source/test file, D-007) are NOT listed here…" is the verbatim
         duplicate of the second bullet of the overview\_rules.md Index section, whose canon home it already has; (2)
         the naming bullet: the D-013/D-014 pointers out, "row/column, D8 symmetries" kept; (3) the rules bullet:
         "active legislation: the register of the rules in force." — the "legislative body" label, the R-NNN pattern,
         the bold-title grammar and the explicit-user-approval clause all out — verified verbatim in the rules.md
         Governance block, their canon home; (4) the decisions bullet: "open historical decision log (append-only)" —
         the D-NNN pattern, the rules.md cross-ref and the closed-volumes pointer out (the five volume bullets are right
         below); (5) the four "the D-333 rotation" annotations out of the decisions\_002-005 bullets — the open question
         from the D-395 analysis, now ruled: range + dates (the identifying data) stay, the campaign annotation goes;
         (6) the analyses bullet: "archived one-off documentation (investigations, reviews, performance baseline, and
         more)." — the I-017, the file names and the ODP-9 material out (canon homes: ideas\_closed.md + the historical/
         directory); micro-call: his "performances baseline" -> "performance baseline" (the real file is
         performance\_baseline.md). (7)-(14) The eight remaining bullets (ideas, ideas\_closed, the five rule files,
         tools, probe\_rules) reduced to the uniform minimal form — the content/grammar parentheticals out, "rigid" out
         (it lives in every rule file's H1), and with them the last Index D-pointers (D-235 x2, D-248/D-249, I-NNN).
         Net: the Index loses the intro + 11 D-pointers (D-007, D-013, D-014, D-333 x4, D-235 x2, D-248/D-249) + the
         family patterns (D-NNN, I-NNN, R-NNN) + I-017 + all the grammar/governance detail; overview.md now carries ZERO
         D-pointer refs — the only D-figures left are the six closed-volume range+date data, which this ruling
         explicitly keeps. This ruling SUPERSEDES the D-391 ruling ("the D-013/D-014 Index pointers in the overview stay
         (class 3)"): the Index remains a registry (class 3), but its entries are minimal identity descriptions from now
         on. The overview\_rules.md amendment (approved): a third bullet in its Index section — "The description is the
         file's identity — no D pointers, no grammar details, no cross-references: those live in the files themselves."
         — codifies the principle so the next Index update does not re-fatten the bullets. Verified: no live file
         depends on the cut strings (only frozen entries + the rules.md H1 itself); the guard has no Index-content check
         (the OV- codes: H1/SECS/TABLE/CUR/NEXT/INDENT), so no guard change. VERIFICATION: the guard green on the
         default set.

D-398 | 2026-10-01 | the overview.md TEST FILES + SOURCE FILES sections (Roberto: the intros are rules, they live in
         overview\_rules.md; the state-cell parenthetical is a justification, not a state; the Suite column becomes the
         compact 5-part "Suite/std\_run" — "1: OK. 2: va bene come proposto. Elimina anche la intro di 'Source files',
         e' l'unica modifica da fare per la sezione. Procedi!"). Three moves: (1) both section intros deleted — the Test
         files intro ("One row per test file, alphabetical by full path. Suite (standard run) = … a (+N VLONG) marks …")
         and the Source files intro ("One row per source file, … the campaign history lives in the decision log.") are
         duplicates of the overview\_rules.md "Source files / Test files (the two tables)" section, whose canon home
         they already have — zero loss; (2) the two state cells "complete (helper module, 0 tests)" -> "complete" — the
         parenthetical is a description, and the EXISTING state-cell rule ("a status word + the open/parked items; the
         description is the mirror's job") already forbids it: the table now conforms to the rule, no rule change
         needed; the "0 tests" fact is carried by the suite cell; (3) the Suite column: header "Suite (standard run)" ->
         "Suite/std\_run" (the underscore escaped — the overview linter runs esc\_issues on every line but the H1), and
         all 47 data rows reformatted to `<total>/<failures>/<skipped>/<vlong>/<vvlong>`. Content truth (derived from
         the test sources, not guessed): the totals sum to 968 (in sync with the last green pre-commit run); exactly TWO
         real VLONG gates exist in the code — the class-level @skipUnless(tier\_vlong()) in
         test\_lm\_worker\_full\_chain.py (the A2050 chain, 1 test) and test\_wrk\_su\_analysis.py (the 1e7 corpus, 1
         test) — hence 9/0/1/1/0 and 10/0/1/1/0; the other 11 modules that MENTION "VLONG" do so only in docstrings;
         VVLONG is "currently uninstrumented" (the tags.py docstring, verified: no tier\_vvlong usage in any test) — the
         fifth slot is future-proofing, all zero; the PERF-gated skips (1 in test\_board, 1 in test\_feature) stay
         inside the skipped slot, not vlong. The two helper rows (paths.py, tags.py): the dash -> "0/0/0/0/0" (uniform,
         per his approval). The overview\_rules.md rule (approved as drafted): "Suite/std\_run (Test files table ONLY):
         `<total>/<failures>/<skipped>/<vlong>/<vvlong>` under the standard pre-commit run (LONG=1, the live DB): total
         = unittest's 'Ran N' (the skips included); the failures, the skips, and — of those — the VLONG- and
         VVLONG-gated counts." — it fixes the header, defines the five slots, and states the two containment relations
         (total includes the skips; vlong/vvlong are shares OF the skips). The (+N VLONG) marker convention dies with
         the column. VERIFICATION: the guard green on the default set; the 47/47 cells are 5-part; the totals still sum
         to 968.

D-399 | 2026-10-01 | the overview.md CONVENTIONS section, round 1 — the naming.md duplicates out (Roberto: naming.md is
         itself a misplacement — "tutto quanto descritto in naming dovrebbe essere la descrizione tecnica del doc mirror
         di board. Qui aggiungiamo le position, le moves ... e pattern .... Poi ci sono cose un po' piu generali come
         pydantic e numba. Io credo che nulla debba rimaner qui. Ma cedo anche che si debba organizzare questi concetti
         in maniera che siano poi fruibili dall'Agente in nuove sessioni di lavoro. Per ora procedi a rimuovere i
         duplicati. Poi decidiamo per il resto."). Scope: exactly what is duplicated in notes/naming.md (the subject of
         his objection) — (1) the vocabulary/bitboard bullet out in full: 100% duplicated (naming.md declares itself
         "single source of truth for board vocabulary" and is more complete — the square-name order, the corner labels,
         the scope statement "code, docs, notes, and replies all follow it"); (2) in the D8 bullet, the "slot order is
         fixed and load-bearing: anti-transform slot s = T\_s^{-1}" half out (duplicated: naming.md's full slot + anti
         tables, "arbitrary but fixed — do not reorder, rename, or alter it", the defining property, the
         golden-constants pinning); the bullet keeps only the pattern.py half — "In pattern.py instance 0 = the ro000
         image, and trans\_fs/anti\_trans\_fs are indexed by instance (length = n\_instances), not by slot." — a pattern
         concept (documented in pattern.md), on his "poi" list, not a naming duplicate. The other seven bullets (the
         dual scalar/array API, @validate\_call, the numba rules, the Position dtype, the move codes, the pattern base-3
         indexes, the test artifacts) stay for now: each has a verified home (the module mirrors; the register's R-750
         for the test artifacts), but their destination is the deferred organizational question — as are the title, the
         section's fate, and the naming.md dissolution into the board mirror. Advisory note (journal): the vocabulary +
         the diagram-reading rule are cross-cutting (they govern notes and replies too, not only board.py) — if
         naming.md is dissolved, that slice must survive in AGENTS.md (which already carries its summary). REPAIR
         (self-inflicted, disclosed): the D-398 insertion left D-397's final wrap line dangling — the rewrap absorbed
         "on the default set." into D-398's last line and truncated D-397's final sentence; both restored to their
         intended text (D-397 as in commit 40c097f; D-398 ending at "to 968."). VERIFICATION: the guard green on the
         default set.

D-400 | 2026-10-01 | naming.md grows the Position / Bitboard / move-codes canon; the overview Conventions section sheds
         two more bullets (Roberto's direct instruction: the move codes go to the end of the naming.md Board vocabulary
         section; a new "Position" section after "Bitboard" carrying the structured-dtype definition; the Bitboard alias
         of numpy.uint64 as the first line of the Bitboard section — and his question: "nella definizione di Position e'
         giusto usare u64, o meglio usare uint64?"). Source-verified answer: NEITHER — the code (src/reversi/board.py)
         defines Position as np.dtype([('mover', Bitboard), ('opponent', Bitboard)]) (line 142) over "Bitboard:
         TypeAlias = np.uint64" (line 127); u64 is no code symbol anywhere in src/ (verified: only descriptive docstring
         phrases in regab.py / prng.py and the unrelated binio write\_u64 / \_U64 binary-I-O names) — it is a
         documentation shorthand in the overview bullet and the board.md mirror. The definition therefore uses Bitboard,
         the actual field type, with the alias spelled out. Changes: (1) naming.md Bitboard section, first line:
         "Bitboard is an alias of numpy.uint64."; (2) naming.md new "Position" section after Bitboard: the
         structured-dtype definition, each field a Bitboard (the numpy.uint64 alias above); (3) naming.md Board
         vocabulary: the move-codes line appended at the end (verbatim from the overview bullet: "Move codes: 0..63 =
         squares, 64 = PA (pass), 65 = NA, 66 = UN."); (4) overview.md Conventions: the Position and the move-codes
         bullets out (moved, not lost) — the section now has 6 bullets. VERIFICATION: the guard green on the default
         set.

D-401 | 2026-10-01 | naming.md — three new sections appended at the end, in his order: Features, Mobility, Pattern (the
         "oculata sintesi" of the three domain modules, for agent use in new sessions — his preamble: all of this could
         live in the board.md mirror, but a careful synthesis in a notes file, later exploited by AGENTS, is very
         useful; that will be the last step of the governance review). Studied: the three modules (feature.py 334,
         mobility.py 306, pattern.py 1331 lines), the three mirrors in full, the class docstrings (the LMC/ALMC/DLMC
         glossary is verbatim in the Mobility docstring), the PatternType table (12 members) and the 29 sample pattern
         names. His ruling on my proposal: "Va molto bene in generale, i riferimenti alle colonne li toglierei, non sono
         costitutivi e sono solo in relazione alla Design\_Matrix, Indexes, che qui non introduciamo realmente. Se non
         parliamo di colonne, feature diventa brevissimo (come deve essere, e' il wrapper dei 3 tipi). Rimuoverei anche
         i sample patterns." Applied cuts: (1) Features — no index-matrix / column-layout bullets at all (the
         sorted-order contract, the (N, I) shape, the per-feature column blocks): the section is now the wrapper
         statement + the 3 categories + the FeatureSet line; (2) Pattern — the PatternSet bullet reduced to "a named
         collection of patterns, stored sorted by mask" (the fused-pass / output-shape detail is architecture, mirror
         territory) and the sample-pattern name family removed from the PatternType bullet. Content sources: Mobility's
         index formula + n\_configurations = k + a + 1 + n\_instances = 1 from the class docstring; the DLMC formula
         popcount(lms) + 64 − popcount(alms) verified against the mirror's golden (13 + 53 = 66); the principal-mask
         rule, the instances/stabilizers, the base-3 configurations and the principal index from the pattern.md
         architecture bullets (domain facts, not API). VERIFICATION: the guard green on the default set.

D-402 | 2026-10-01 | the naming.md Features section reformulated, verbatim per Roberto ("La sezione 'Feature' la
         riformuliamo cosi: [his exact text]"): the opening gains the domain definition "A Feature is an observable
         characteristic of a game position."; the category bullets lose their enum values (0/1/2) and the
         cross-references, taking his one-line glosses — INTERCEPT: the constant term; MOBILITY: a measure of the
         options to move; PATTERN: a selection of squares on the board; the FeatureSet line becomes "a named collection
         of features chosen at will among the intercept, mobilities and patterns." Formatting normalization (disclosed):
         his chat hyphen separators became the em-dash separators used by the sibling Mobility/Pattern bullets. REPAIR
         (second wrap-split, self-inflicted, disclosed): the D-401 insertion used a mid-line anchor at D-400's end and
         left its wrap remainder dangling — absorbed by the rewrap into D-401's last line ("…on the default set. default
         set."); removed. D-400's end verified intact. VERIFICATION: the guard green on the default set.

D-403 | 2026-10-01 | the naming.md Pattern section — the mask definition tightened, verbatim per Roberto ("A mask is a
         64-bit integer / cambiamolo in: A mask is Bitboard"): the first bullet now reads "A mask is `Bitboard`; the
         principal mask is the numerically LOWEST of its 8 D8 transforms…" — the mask is now defined by its actual type
         (the Bitboard alias defined in the section above: numpy.uint64), completing the definitional chain mask ->
         Bitboard -> numpy.uint64 instead of restating "64-bit integer". Formatting normalization (disclosed):
         `Bitboard` in a code span, as in the Bitboard and Position sections. VERIFICATION: the guard green on the
         default set.

D-404 | 2026-10-01 | the overview "Conventions in the code" section dissolved — the radical option (b), per Roberto: the
         four surviving bullets withdrawn (the two pattern bullets are already fully in the pattern.md mirror — instance
         0 = ro000 at line 57, the base-3 indexing at lines 3/12/62, verified; the Test artifacts bullet duplicates
         R-750 in the register, notes/rules.md:232), the three design bullets move to a new synthesis file, and the
         section itself is deleted — the overview now has seven sections. Guard: the SECTIONS tuple 8 → 7 (OV-SECS), the
         "eight sections" rule and enumeration in overview\_rules.md amended to "the seven sections", the docstrings and
         the "beyond the eight" message updated. notes/design\_principles.md born — the house design policy,
         cross-cutting (it binds any new code in the pipeline, not one module), three entries in the deprovenance style
         (no D-pointers, no examples): (1) the dual scalar/array API — an architectural fact, not a style choice: public
         functions accept a scalar or a 1-D array and return the input kind, following the numpy design on which the
         solution's performance is built; (2) Pydantic — `@validate_call` on public functions, when the function is
         public, has no specific performance problem, and has no convoluted backstory (the state-machine Context is the
         standing exception); (3) Numba — when performance is the goal and the benefit is proven, hot loops run as
         `njit(cache=True)` kernels, the best performance the objective; the kernel is always embedded in a normal
         Python function, scalar or vectorized — it never leaks into the API. The mechanism detail (is\_scalar →
         atleast\_1d → ndim → dispatch → reshape) stays in the mirrors: module territory. Index: one bullet for the new
         file, after naming.md (the description = the file's identity, no D pointers). Guard: the new file added to the
         default set (now 14 files) and to the rulefile grammar (kind\_of). VERIFICATION: the guard green on the default
         set.

D-405 | 2026-10-01 | notes/design\_principles.md restructured from the three-entry note into the DP register (Roberto's
         draft — "in linea con gli altri artefatti, e pronta per un eventuale uso piu articolato" — with the agreed
         corrections): the rules.md register shape (the H1, the workspace policy intro, the Lifecycle block RECORD /
         PROMOTE / RETIRE, the Governance block: explicit user approval, the DP-numbers global and never reused, order
         by value, the bold title line + 1-3 line description, two blank lines between principles), then the three
         principles: **DP-010** the dual scalar/array API — "like `Bitboard`, `Position`, or `Index`, accept a scalar or
         array and return the input kind" (the 1-D qualifier deliberately dropped, per Roberto, after the
         investigation); **DP-020** the pydantic validation, with the standing case named (the state-machine Context,
         whose validation gate is deliberately separate from the move execution); **DP-030** the numba njit compilation,
         with the cross-module kernel-consumption exception. INVESTIGATION (his "fai questa investigazione" before the
         change — his reading confirmed): the board.py 1-D guard is 13 ndim sites over 9 functions in 3 families — the
         cast family (bitboard\_from\_signed\_int / bitboard\_to\_signed\_int / bitboard\_from\_hex\_str) is
         shape-agnostic under the guard (pure formalism); the D8 family (bitboard\_transformations / anti) and the
         kernel family (legal\_moves, position\_flips / make\_move / hash) guard 1-D numba kernels, converting a
         TypingError crash into a clean ValueError (D-111 M5); the pipeline feeds the board boundary only scalar
         (pattern construction) and 1-D batches (feature.py:331), while the 2-D lives at the pattern / wmaps /
         design-matrix layer (the NxF design matrix). The N-D path is standard: flatten, kernel, reshape back. FACTS
         verified: the Context DOES use `@validate_call` (7 decorators in state\_machine.py) — the "convoluted
         backstory" is the separate-gate pattern (D-076 / D-069), so the conditional phrasing is fact-safe; the DP-030
         exception is real (the random\_game fused engine consumes the board D8 kernels, board.md:33); `Index` is a
         canonical type alias (pattern.py:65, in the `__all__`). CORRECTIONS to his draft (disclosed): the "worspace"
         typo, "applyed" -> "applied", "doesn't leaks" -> "doesn't leak", the redundant "Pydantic:" prefix, the code
         spans (ESC), the backtick form of the title-notation example (house style, as in rules.md). CONSEQUENCES: a DP
         linter added to the guard (mirror of lint\_rules — DPH1 / DPSPACE / DPOINTER / DPSEQ, the '## ' sections
         optional, principles allowed at top level) with kind\_of mapping design\_principles.md to it; DP-NNN added to
         the reference-families bullet in overview\_rules.md (the single definition site); the 1-D guard removal + N-D
         verification registered in the overview Next steps (the board.py source change awaits the explicit GO);
         naming.md's Pattern section gains the "Index is an alias of numpy.uint32" line. VERIFICATION: the guard green
         on the default set.

D-406 | 2026-10-01 | naming.md — the Index promoted from the inline Pattern bullet (D-405) to its own section, placed
         immediately after Position, per Roberto ("Piu' chiaro, piu' evidente. E poi gli Indexes sono i protagonisti
         della PIPELINE"): the D-405 bullet removed from the Pattern section, the new "## Index" section in the Position
         style (heading + one bullet, no blank between them) — "Index = a numpy uint32 alias — the base-3 configuration
         index (the Pattern section below).", the forward reference mirroring the Position bullet's "the numpy.uint64
         alias above" backward one. VERIFICATION: the guard green on the default set.

D-407 | 2026-10-01 | naming.md — two amendments, per Roberto: (1) the Index bullet reformulated — the "the base-3
         configuration index (the Pattern section below)" wording implied the definition lives in the Pattern section,
         but the concept is cross-cutting across all the feature sources (his "E' una lunga storia, che al momento non
         ha valore": pattern predates mobility and feature, hence the historical placement; verified: mobility.py and
         feature.py both import Index / IndexArray and expose compute\_indexes -> IndexArray) — now "used to identify
         feature configurations (base-3 in particular for patterns)."; (2) the file intro broadened from "board
         vocabulary" to "the domain vocabulary" — naming.md has grown beyond the board domain (Features, Mobility,
         Pattern, Index), aligning the intro with the H1 that already says "Reversi domain naming convention".
         VERIFICATION: the guard green on the default set.
