# Decisions log — historical record

Format rules: notes/decisions_rules.md (rigid — follow when appending to this file).

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
D-335 | 2026-09-29 | the State-column NORMALIZATION of the overview tables (Roberto: "la colonna State e' da
         revisionare: non c'e' coerenza sulla lunghezza dello stato, ci sono continui riferimenti alla storia. Se una
         cosa e' complete e' complete" + the Test files table broken after the test_hlp_optimize row). (1) THE BREAK: a
         pre-existing blank line — the D-295 test_hlp_random_play row deletion (commit eb59a3d) left the blank behind —
         split the Markdown table, the 4 following rows rendered outside it; removed. (2) THE NORMALIZATION: every State
         cell reduced to the D-117 grammar — the status word + the open/parked items ONLY; the descriptive prose is the
         mirror's job (the Doc column points to it), the D-NNN / I-NNN campaign references and the "moved from / renamed
         from / fix / N new tests / replaces X" clauses are the decision log's. A sweep of all 95 mirrors' Open issues
         sections found exactly ONE open file-level item in the whole codebase — the wrk_anova adherence-header wording
         defect (pinned by the probe; a source change awaits Roberto's call) — now in the State cell; the parked PRNG
         passettino (the Next-steps item) is in the prng.py cell; the two helper test rows say "complete (helper module,
         0 tests)"; test_mobility's stale "analyzed" becomes "complete" (the mirror: 26 tests, all pinned, no open
         issues — the word is a remnant of the suite's birth, flagged to Roberto). (3) THE ORDER: both tables were in
         historical addition order, violating the header + the rule ("alphabetical by full path") — re-sorted (48 src +
         47 test rows); the stale header parenthetical ("the package path sorts future packages first") is out. (4) THE
         HIDDEN BUG: the hlp_su_analysis cell (2682 chars) carried a RAW inner pipe — the "joint | None" type-union,
         a D-116 escape violation the re-wrappers never saw (the row never matched the 5-pipe row shape) — gone with the
         cell; the reduction is what surfaced it. (5) THE LEGISLATION (rules.md, D-117 clarified): the State cell = a
         status word + the open/parked items (each with its governing D-pointer if any); the description is the mirror's
         job, the campaign history the decision log's — the old "the D-pointer range" phrase, which had fed the D-NNN
         bloat, is retired. Nothing LOST: every stripped clause exists verbatim in the decision log and the mirrors.
         VERIFICATION: both tables contiguous (0 blank lines inside, 5 unescaped pipes per row, full-path alphabetical
         order verified), notes_format --check clean.
D-336 | 2026-09-29 | the Test-data note of overview.md became a VERIFIED bullet list (Roberto: "Via D-215, teniamo una
         lista a bullet con un commento di cosa sono. Breve. verifica la lista."). The verification found the note STALE
         on three counts: (1) the rlm_01 / rlm_02 "DB dump" descriptions — the files were regenerated 2026-09-21 and are
         now unit-test configs (rlm_01: the Design Matrix data structure, rlm_02: the gradient worker — each file's own
         description field); (2) the note omitted three of the eight directory files: prng_golden.txt (the committed
         18436-line PRNG golden, 20 sections — measured), rlm_05.json + rlm_06.json (the SU-analysis experiment configs,
         the 2M / 100M tiers, ec 20, stopping at SU_ANALYSIS — the names + descriptions read from the files); (3) "the
         per-file mirror docs cover them" — docs/test/reversi/data/ does not exist (no mirror docs for the data files) —
         the claim is out. The D-215 pointer + the "571_141-row log verified 100%" campaign verification are out; the
         committed sample stays pinned by its present fact (the 1002-row stride — measured: 1003 lines incl. the
         header). VERIFICATION: every bullet checked against the file on disk (the names, the description fields, the
         line counts), notes_format --check clean.
D-337 | 2026-09-29 | the Next-steps REWRITE as the NON-prioritized TO-DO list (Roberto: "La lista NON ha priorita',
         decido io l'ordine. Tu scrivi solo le cose da fare in Inglese in maniera sintetica. Quindi Opzione A" — and, on
         my over-analysis: "Nia, stiamo scrivendo una TO-DO List, non stiamo facendo tutto della TO-DO List"). (1) THE
         OLD BULLETS OUT: the VVLONG "uninstrumented/KEPT" bullet (a frozen state, not an open item — the D-285/D-286
         record lives in the decision log + the tags.py header; the work is absorbed by the new tag item); the PRNG
         passettino bullet — DROPPED (Roberto: "non serve" — the ctor's MT init is a one-shot 312-iteration Python loop,
         negligible vs the batch kernels, the numba payoff is zero); the PROFILING bullet — CLOSED (done at session 58
         / D-299: the SU_ANALYSIS cold compute profiled + optimized, bit-identical). (2) THE LIST (his 6 items, English,
         synthetic, NO priority — he picks the next item on demand, in his enumeration order): the duration tags (the 5
         tags VVLONG/VLONG/LONG/PERF/DB + the tag-assignment technique re-verified + the LONG/VLONG/VVLONG
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
         prestazioni. DROP FOREVER ... non lo voglio piu' vedere. 2: DROP ... pulisci wrk_anova.md. Procedi!"). (1)
         prng.py — the "parked: the last PRNG passettino" cell -> "complete": the item was already DROPPED at D-337
         (removed from Next steps) but the table cell was left behind (a bookkeeping inconsistency of mine); the ctor's
         MT init (the 312-iteration Python loop) is never performance-critical — the DROP is FOREVER (the item is not
         re-raisable without a new rationale). (2) wrk_anova.py — the "open: the adherence header" cell -> "complete":
         my D-335 over-reading — the item was the D-259 finding (5)(b) (the report header says "top {top_k_adherence}"
         while the report body lists every sub-variable; the bound applies to the CONSOLE lines only) — a PINNED,
         accepted wording quirk (verify_anova C6/D7, the D-259 ruling "left as-is"), NOT an open item; the mirror's own
         Open issues section ended with "None." (no open issues). (3) THE MIRROR CLEANUP
         (docs/src/reversi/lm/wrk_anova.md, per Roberto): the Open issues section now reads "None." alone (docs_rules
         §4: closed items never appear there); the console/report split moves to the Architecture adherence bullet as a
         PRESENT contract (the CONSOLE lines are top-N, the REPORT the full list, the header wording the pinned
         deliberate quirk) — the finding's record itself lives in D-259 (5)(b). VERIFICATION: all 95 State cells are now
         "complete" (the 2 helper rows "complete (helper module, 0 tests)"), notes_format --check clean on the touched
         files.
D-339 | 2026-09-29 | the overview tables' Suite-count SIMPLIFICATION (Roberto: "la tabella Source files ha la colonna
         Suite (live DB), mentre Test files ha la stessa colonna. Non credo ci sia valore in questa duplicazione ...
         Teniamo la conta dei TESTS solo sui tests? ... Tolgo commenti inutili? ... Mi piacerebbe che il nome del DOC
         fosse un hlink al file md. Pensaci e fammi tu una proposta." — and, on the proposal: "1: approvo. 2: Totale no,
         sarebbe da modificare in continuo. 3: OK. Procedi!"). (1) SOURCE TABLE: the Suite column is GONE (File |
         State | Doc) — 46 of the 48 rows duplicated their 1:1 test row's number, and the only 2 "via" notes
         (base_model -> test_logistic_model, model_weights -> test_lm_worker_full_chain) live in the mirrors (the
         Verified invariants); the header's "Suite = ..." sentence is out. (2) TEST TABLE: the single home of the
         counts, with a STRICT semantics — "Suite (standard run)" = the module's count under the standard pre-commit run
         (LONG=1, the live DB) — fixing the old column's ambiguity (some rows were default-tier runs, some DB-tier runs:
         test_regab 48/0/0 was a DB run, test_wrk_final_log_print "5/0/1 (LONG: 6/0/0)" a default run); the only
         micro-marker kept is (+N VLONG) — exactly 2 modules (test_lm_worker_full_chain 9/0/1, the A2050 chain;
         test_wrk_su_analysis 10/0/1, the 1e7 corpus); NO total (Roberto: it would need constant updating); no PERF
         parenthetical (PERF tests skip in the standard run and sit in the skip count; the mirrors carry the detail).
         (3) THE RE-MEASURE: all 45 runner modules individually + the full standard run — all green: 968 tests, 0
         failures, 24 skipped (75 s); the only count that moved vs the old table: test_state_machine 49 -> 50 (a test
         added since the last verification); test_wrk_final_log_print is now simply 6/0/0. (4) DOC AS HLINK: all 95 Doc
         cells are markdown links to the mirrors ([path](path) — verified the notes_format re-wrapper keeps the links
         atomic). (5) THE LEGISLATION (rules.md, D-117 amended): the Suite count lives ONLY in the Test files table,
         under the standard pre-commit run, with the (+N VLONG) marker; the Doc cell is a markdown link to the mirror.
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
         decisions_000.md — frozen history, untouched). (2) NUMBERING: the 46 rules of the 9 sections get R-001..R-046
         in reading order (dash + 3 digits, consistent with D/I); the 3 Lifecycle bullets stay unnumbered (prose, not
         rules); the numbers are never reused. (3) FORMAT — the dash-less variant (verified in scratch: the literal
         dash-bullet spec is NOT stable under notes_format.py, which rejoins the description onto the title line): a
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
         newline); the overview Index bullet updated to the new format. VERIFICATION: notes_format --write idempotent
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
         historical log + the tool's WIDTH=120 + the per-domain declarations: log_rules.md, docs_rules.md, the ideas
         headers, R-004); the "atomic code spans; the tables and the headings stay one physical line" clause out (the
         tool enforces the verbatim grammar; R-003 states it for the overview tables). (3) NEW: the R-NNN.N
         SUB-NUMBERING notation — a rule best placed in a specific position takes a dot-suffixed number of its parent;
         the zero-padded parents make it sort right after the parent in text order (R-012.1 between R-012 and R-013), so
         the register never renumbers. (4) The overview Index bullet aligned to "explicit user approval". VERIFICATION:
         notes_format --write idempotent + --check clean (327 lines, 9 sections, R-001..R-046 intact).
D-342 | 2026-09-29 | R-002 AMENDED — the register's PRECEDENCE (Roberto: "R-002: This file: the active legislation.
         Every rules stated in this file has precedence on other notes, documents or decisions. Departure from the rules
         is possible only with explicit consent from the user. Cosa ne pensi?"). Applied from Roberto's text with two
         grammar fixes ("Every rules stated" -> "Every rule stated"; "precedence on" -> "precedence over"). The clause
         deliberately scopes the precedence to "other notes, documents or decisions": the constitution (AGENTS.md,
         R-001) and the user's direct instructions stay above the register — the resulting hierarchy is user > AGENTS.md
         > rules.md > other notes / docs / decisions (a historical decision can no longer overrule an in-force rule).
         The second sentence COMPLEMENTS the Governance (which governs amending the register): a departure from an
         in-force rule also needs explicit user consent — an approved departure that persists is recorded as a decision
         and amended into the rule (the same R-number, a new D-number). VERIFICATION: notes_format --write idempotent
         + --check clean; R-002's description is 3 lines (at the 1-3 target).
D-343 | 2026-09-29 | R-003 CONDENSED — the missing DOMAIN FILE (Roberto: "Ora vediamo R-003 ... Non ti sembra un po'
         lunga, prolissa ??? quale e' la REGOLA ... il resto VIA! Dai fammi una proposta!!!" — and, on the proposal:
         "OK! Via! Vai Nia!"). (1) NEW notes/overview_rules.md — the domain rule file the overview lacked (the only
         rigid-format file without one — the reason R-003 grew to 15 of the 46 lines, one clause per format
         campaign: D-116, D-117, D-334, D-335, D-337, D-339): the eight sections in fixed order, English + dates, the
         reference families (D-NNN / I-NNN / R-NNN / T-NN / R# / M#, with the "never an R-NNN" disambiguation), the
         two-table grammar (alphabetical by full path, one physical line per row, the \| escape, D-116), the State cell
         (D-117, clarified D-335), the Suite count in the Test table only (the standard pre-commit run + the (+N VLONG)
         marker, D-117, amended D-339), the Doc cell as a markdown link (D-339), the Current-state constraints (MAX 10
         bullets, NO bullet-per-campaign, D-334), the Next-steps constraints (open, non-prioritized, D-337), the Index
         rule (one bullet per notes/ file). (2) R-003 -> the 3-line pointer: the entry-point rule + "The format is RIGID
         in notes/overview_rules.md" — the pattern R-005 / R-038 already use for log_rules.md / docs_rules.md. (3)
         CONSISTENCY (one line each): R-006's domain list + notes/overview_rules.md; the overview's own header pointer
         (was "notes/rules.md — the overview bullet") -> notes/overview_rules.md; the overview Index + the file's
         bullet; the AGENTS.md Layout enumeration + overview_rules.md. VERIFICATION: notes_format --write idempotent
         + --check clean (rules.md 314 lines, R-003 = 3 lines at the 1-3 target; overview_rules.md 42 lines; every
         D-pointer moved with its text).
D-344 | 2026-09-29 | R-004 CONDENSED — the DECISIONS DOMAIN FILE (Roberto: "R-004 — notes/decisions.md Riusciamo a
         semplificare ?" — on the proposal: "procedi!"). (1) NEW notes/decisions_rules.md (21 lines) — the domain
         rule file the decisions log lacked (the last rigid-format collaboration file without one): the entry grammar
         (one entry per decision including "leave as-is for now", append-only, a blank line before every entry, the
         `D-NNN | YYYY-MM-DD | the rationale` header on one line, the continuation lines indented EXACTLY 9 spaces —
         now written down for the first time: the grammar was practiced on every entry but legislated nowhere), the
         global/monotonic/never-reused D-numbers across open log + closed volumes, the D-209 style clauses (code
         spans for paths / names, escaped asterisks for the math multiplications), and the volumes & rotation (the
         open volume keeps its name; past 1000 lines — the D-118 cap, amended at D-333 — it closes at a session
         boundary as decisions_NNN.md, zero-padded; a volume jump never cuts an entry). (2) R-004 -> the 2-line
         pointer: the identity (the OPEN historical decision log, append-only, the "why", consulted on demand) +
         "The format is RIGID in notes/decisions_rules.md (the entry grammar, the volumes and rotation)" — R-004 is
         now the slimmest rule of the register (with R-005). (3) CONSISTENCY (one line each): R-006's domain list +
         the file; the decisions.md header ("Format: D-NNN | date | decision | rationale") -> the domain-file
         pointer; the overview Index + the file's bullet; the AGENTS.md Layout enumeration + the file. (4) SIDE
         EFFECT: the header edit required a --write on decisions.md, which normalized the whole open volume to the
         tool's canonical ~120 wrap (content-neutral: the token fingerprint identical, idempotent) — the post-D-333
         hand-wrap drift is healed. VERIFICATION: notes_format --write idempotent + --check clean (rules.md 312
         lines, R-004 = 2 lines; decisions_rules.md 21 lines).
D-345 | 2026-09-29 | R-007 CONDENSED — the IDEAS PREAMBLES (Roberto: "R-007 le regole sono duplicate nel preambolo
         di ideas.md. Propongo di rimuoverle da rules, e scrivere solo che sono nel preambolo del file. Cosa ne
         pensi?"). Verified first: the two preambles (notes/ideas.md + notes/ideas-closed.md, both "Format (D-235)")
         are the SUPERSET of the R-007 clauses — the format grammar (the `I-NNN | status | idea` header, the 9-space
         continuation, the blank line before every entry, the code spans), the status legend (idea / follow-up /
         in-progress, WITH definitions — the register never had those), the closure lifecycle (a closed idea MOVES to
         ideas-closed.md, compacted to the statement + the D-pointer + the outcome, in the same commit as the closing
         decision, "it never stays here"; the campaign history stays in decisions.md / the journal, the closed file
         is "the I-NNN index into it, never a narrative"), and the I-numbers (global, never reused or renumbered) —
         all of it in the preambles; the register carried the weaker copy. R-007 -> the 2-line pointer: the identity
         (the OPEN backlog I-NNN; ideas-closed.md the CLOSED ideas, done | dropped) + "The format (D-235), the status
         legend, the closure lifecycle and the I-numbering are in each file's preamble." No new file needed — the
         preambles ARE the domain files (self-contained, D-235, in both files). VERIFICATION: notes_format --write
         idempotent + --check clean (rules.md 309 lines, R-007 = 2 description lines).
D-346 | 2026-09-29 | R-007 MICRO-AMENDMENT (Roberto: the pointer without the D-235 reference — "The format (D-235),
         the status legend, ..." -> "The format, the status legend, ..."). The origin pointer is redundant in the
         register: the preambles themselves carry it ("Format (D-235)" in both files) — the reference lives where it
         belongs. Amendment keeps the R-007 number (per the Governance). VERIFICATION: notes_format --write idempotent
         + --check clean (rules.md 309 lines, R-007 = 2 description lines).
D-347 | 2026-09-29 | the LANGUAGE & COLLABORATION section, per Roberto's text (and: "Nel caso volessi spiegare il
         D-111 pattern, spieghiamolo qui. ma no a REFERENCES to D-XXX."). (1) R-008 generalized: "Replies to the user:
         Italian." -> "Replies to the user: his own language (e.g. Italian)." — the register states the principle; the
         constitution (AGENTS.md rule 4) still pins the current instance ("Italian") — coherent, and per R-002's
         hierarchy the constitution sits above the register, so nothing is overridden; if the language ever changes,
         the constitution line changes with it. (2) R-010: the D-111 reference out — "One commit per item + a
         notes-wave commit at the campaign close." Nia's call on the offered inline explanation: NOT needed — the
         rule is self-contained (one D-number per fix campaign; one commit per fix item; the notes-wave commit = the
         batched notes updates — decisions / journal / overview — that closes the campaign); the D-pointer was pure
         provenance (the same principle as D-346: no D-XXX references in the rules; explain inline only when the rule
         is not self-contained — here it is). (3) R-009 / R-011: untouched, exactly as proposed. VERIFICATION:
         notes_format --write idempotent + --check clean (rules.md 309 lines).
D-348 | 2026-09-29 | R-008 / R-009 / R-011 — the last D-pointers of the LANGUAGE & COLLABORATION section (Roberto:
         "Non hai rimosso (D-002), (D-004; AGENTS rules 2–3), (D-154). Vanno rimossi!"): my D-347 oversight — I removed
         only the D-111 we had discussed explicitly and left the three that were already in his proposed text. Removed:
         (D-002) from R-008, (D-004; AGENTS rules 2–3) from R-009 (the AGENTS pointer with it), (D-154) from R-011 —
         the three rules are now pure: the principle, no references. Counted after this commit: 46 D-XXX references
         remain in the register (Layout & tree, Naming & platform, Test discipline, Pipeline contracts, Docs, Code
         style) — awaiting Roberto's ruling on the full sweep (the D-340-deferred "poi le guardiamo una per una").
         VERIFICATION: notes_format --write idempotent + --check clean (rules.md 309 lines).
D-349 | 2026-09-29 | the JOURNAL section RETIRED — R-046 removed (Roberto: "La sezione 'Journal' contiene solo la
         R-046. ... Che e' ridondante con la R-005. Rimuoviamo completamente la sezione 'Journal'. Grazie!"). Verified
         before removing: 3 of R-046's 4 facts are in log_rules.md (the global session numbering — Session entries
         item 1; one volume per 25 sessions or 2000 lines, whichever first, and rotation ONLY at a session boundary —
         the Volumes and rotation section); the 4th ("the step-N entries") is an ABANDONED practice — measured: 48
         occurrences in log_001 only, 0 in log_000/002/003/004 (the current volume), and not legislated in
         log_rules.md — the current journal practice is the flat bullet. R-005 already carries the pointer ("The
         session journals (rotating volumes; the format is rigid in notes/log_rules.md)."). Retirement per the
         Governance: R-046's number leaves a gap (no renumbering); the register is now 45 rules in 8 sections
         (rules.md 302 lines; R-045 is the last rule). VERIFICATION: notes_format --write idempotent + --check clean;
         no live R-046 reference outside the historical decision entries (which record the state at their time).
D-350 | 2026-09-29 | the PER-RULE D-POINTER REVIEW starts — item 1, R-012 (Roberto: "Proseguiamo con la review per
         regola. R-012 ... Diventa: [the rule without (D-003), (D-009), (AGENTS rule 7)]. Grazie!"): his text applied —
         the title loses (D-003), the description loses (D-009) and the AGENTS rule 7 pointer; the rule is now pure
         (the workspace is a git repo; the minimal .gitignore list; scratch/ disposable, never tracked). The three
         pointers were pure provenance — the AGENTS.md standing rules 1/7 and the .gitignore itself carry the
         operative facts. D-XXX references in the register: 44 (was 46 at D-348). VERIFICATION: notes_format --write
         idempotent + --check clean (rules.md 301 lines).
D-351 | 2026-09-29 | the per-rule D-pointer review — item 2, R-013 (Roberto: "Proseguiamo con la review per regola.
         R-013 ... Diventa: [the rule without (D-006), (D-008; D-133: ...), (D-273)]. Grazie!"): his text applied with
         ONE declared fix — a stray closing parenthesis left over from the "(D-008; D-133: ...)" removal (the line
         reads "the tools/ and lm/ subpackages; the unit tests ..."), and `reversi` kept as a code span (the file's
         form). The rule is now pure: all Python sources under src/; the package `reversi` under src/reversi/, the
         core at the top level, the tools/ and lm/ subpackages; the unit tests in test/, a root tree mirroring src/
         one file to one file. D-XXX references in the register: 41 (was 44 at D-350). VERIFICATION: notes_format
         --write idempotent + --check clean (rules.md 301 lines).
D-352 | 2026-09-29 | the per-rule D-pointer review — items 3+4, R-014 + R-015 (Roberto: "Proseguiamo con R-014 e
         R-015. ... Diventano: [R-014 without (gitignored) in the title and without (D-010, D-011); R-015 without
         (D-007) and (D-273)]. Grazie!"): both rules applied from his text. R-014 is now: the .venv at the workspace
         root; pyproject.toml the minimal editable-install form, implicit requirements declared as they are hit —
         the "(gitignored)" note out of the title too (the .gitignore itself carries the fact, same logic as
         R-012); R-015 is now the mirror rule in its purest form: src/reversi/X.py -> docs/src/reversi/X.md, the
         test files mirror the same way (the (D-007) / (D-273) origin pointers out — the mirror rule lives in
         AGENTS.md rule 5 and in the docs/ tree itself). D-XXX references in the register: 38 (was 41 at D-351).
         VERIFICATION: notes_format --write idempotent + --check clean (rules.md 300 lines).
D-353 | 2026-09-29 | the per-rule D-pointer review — item 5, R-016 (Roberto: "Proseguiamo con R-016. ... Diventa:
         [tools/ holds the maintenance tools — the three tools, the NOT-package-tools / NOT-probes distinction, the
         a/b/c test, the pointer to notes/tools.md — without (D-248), (D-133) and the four-requirements
         parenthetical]. Grazie!"): his text applied. The title loses "(workspace root)" (the fact is carried by
         AGENTS.md's Layout line and by the rule's own "It is NOT the package's src/reversi/tools/" clause) and
         "MAINTENANCE" is lowercased; the description drops the (D-248) and (D-133) origin pointers and the
         "(the four requirements — ...)" summary of notes/tools.md — the domain file carries its own four
         requirements, the register points (the R-003/R-004/R-007 pattern). D-XXX references in the register: 36
         (was 38 at D-352). VERIFICATION: notes_format --write idempotent + --check clean (rules.md 299 lines).
D-354 | 2026-09-29 | the per-rule D-pointer review — item 6, R-017 (Roberto: "Proseguiamo con R-017. ... Diventa:
         [the rule without the trailing (D-176)]. Grazie!"): his text applied — the only change is the (D-176)
         origin pointer out of the description's end; the title keeps "(gitignored)" (unlike R-014's title, the
         gitignored-ness of build/ is part of the rule's reasoning: the data lives there BECAUSE the folder is
         gitignored — the self-contained-clone contract). The Layout & tree section is now fully pure: R-012..R-017
         carry no D-pointers. D-XXX references in the register: 35 (was 36 at D-353). VERIFICATION: notes_format
         --write idempotent + --check clean (rules.md 299 lines).
D-355 | 2026-09-29 | the per-rule D-pointer review — R-020 and R-021 RETIRED (Roberto: "Proseguiamo con R-020 and
         R-021. I le eliminerei. Non mi sembrano piu' attuali. Grazie!"): both rules removed from the register; the
         R-020 and R-021 gaps are permanent (R-numbers are never reused). VERIFIED before acting: the two TOPICS are
         still in force in the code — A2030/A2050 are live test-class labels (TestFullChainA2030 /
         TestFullChainA2050 in test/reversi/lm/test_lm_worker_full_chain.py) and the `*_for_current_level` helpers
         are injected by the StateMachine and consumed by 7 workers — but both conventions are already canonized in
         their canonical home, the Conventions section of docs/src/reversi/lm/logistic_model.md (the A2xxx
         "intentional, not a typo — do not 'fix'" clause; the injected-cache-helper contract with the R1-trap
         note), so the retirement loses nothing: the register was duplicating code-level conventions that the
         mirror doc owns. What was actually stale was the pointer: "the session-21 review" (a one-shot campaign
         session) and (D-069). Rules in force: 45 -> 43. D-XXX references in the register: 34 (was 35 at D-354).
         VERIFICATION: notes_format --write idempotent + --check clean (rules.md 290 lines).
D-356 | 2026-09-29 | the per-rule D-pointer review — R-018 and R-019, closing the Naming & platform section
         (Roberto: "Proseguiamo con la sezione 'Naming & platform'. [the current R-018/R-019 text]. Diventa: [R-018
         as 'Reversi (othello), NOT chess' with the column (A-H)/row (1-8) vocabulary, A1 = bit 0, H8 = bit 63,
         without (D-013, D-014) and without 'do not reorder or rename'; R-019 without (D-022)]. Grazie!"): his text
         applied. R-018: the title gains "(othello)"; the description gains the A-H/1-8 ranges and the H8 =
         bottom-right = bit 63 clause, and loses the (D-013, D-014) pointer and the "do not reorder or rename"
         imperative (that convention is owned by notes/naming.md, which the rule points at). R-019: (D-022) out. One
         declared spacing fix: his "row(1-8)" became "row (1-8)" (consistent with "column (A-H)"). The Naming &
         platform section is now fully pure (R-018/R-019; R-020/R-021 retired at D-355). D-XXX references in the
         register: 32 (was 34 at D-355). VERIFICATION: notes_format --write idempotent + --check clean (rules.md
         290 lines).
D-357 | 2026-09-29 | the per-rule D-pointer review — R-029 SPLIT into three rules (Roberto: "FAmmi una prosta lean
         and clean per R-029 per favore. Poi la valuto e ti dico come procedere. Grazie!" — after my 7-line lean
         proposal: "E se facessimo tre RULES ??? [R-029 Suite tiers / R-029.1 Canonical order / R-029.2 Before git
         commit, full text]. Cosa ne pendi ?" — after my endorsement: "Procedi!"): the monster was three independent
         contracts fused in one rule (the tier semantics; the canonical module order of the runner; the pre-commit
         obligation) — each can be violated and checked independently, so it is three rules. His text applied
         verbatim, zero declared fixes: R-029 keeps its number and the tier contract (out: the A2050/1e6/1e7
         examples, the predicate names, the order enumeration, and the (D-130; D-256)/(D-036) pointers — the tier
         content and the canonical order are carried by the run_utests.sh header + the MODULES array, and the tier
         semantics by test.reversi.tags, both named in the rule); R-029.1 and R-029.2 are NEW rules using the
         R-NNN.N sub-numbering created at D-341, placed adjacent to the parent (the zero-padded parent sorts
         textually before R-030, so the placement at the end of the Test discipline section is correct). Rules in
         force: 43 -> 45. D-XXX references in the register: 30 (was 32 at D-356). VERIFICATION: notes_format
         --write idempotent + --check clean (rules.md 296 lines).
D-358 | 2026-09-29 | the per-rule D-pointer review — Test discipline R-022..R-027 (Roberto: "Proseguiamo con la
         sezione 'Test discipline'. Mi fai una proposta di semplificazione, pulizia, revisione per R-022..R-028. La
         valuto e ti do indicazioni poi su come procedere." — after my 7-rule proposal: "R-022, R-023, R-024, R-025:
         OK. ... R-026: Ok, ma e' davvero applicata? ... R-027: OK. R-028: Ma perche' dobbiamo dire 'The
         multi-threaded OpenBLAS ddot is not bit-portable...'? tutti i float hanno il problema — scriviamo che i
         golden sui float per essere robusti devono usare assert_close. Procedi con gli OK, e fammi una proposta
         migliore per la R-028."): applied the OK'd six verbatim — R-022 title-only ((D-065) out); R-023 title
         ((D-085) out), description untouched (already lean); R-024 (D-080, D-130: ...) out but the semantic hint
         kept — "the SKIP_REGAB_DB + LONG-tier check" is the contract, not provenance (verified against the
         db_long_gate body in test/reversi/tags.py); R-025 merged into one bold line (title + description said the
         same thing); R-026 (D-100) out; R-027 (D-124) out. R-028 UNTOUCHED, awaiting his verdict on the improved
         proposal (all floats, assert_close for robustness, no OpenBLAS sentence — the full rationale already lives
         in the closecheck.py module header). His R-026 question verified in the code: the uniform
         @validate_call(config=ConfigDict(arbitrary_types_allowed=True)) gate IS applied — 38 gate applications
         across src/reversi/lm/wrk_*.py (plus arbitrary_types_allowed in base_model.py and pattern.py), and
         test/reversi/lm/test_logistic_model.py patches the factories by name in the importing module's namespace
         (patch('reversi.lm.logistic_model.wrk_config', ...), wrk_positions, wrk_features, ...). D-XXX references in
         the register: 24 (was 30 at D-357). VERIFICATION: notes_format --write idempotent + --check clean
         (rules.md 294 lines).
D-359 | 2026-09-29 | the per-rule D-pointer review — R-028, closing the Test discipline section (Roberto, after my
         improved proposal: "Ho capito Nia, quindi R-025 va benissimo come e'. OK. R-026: ho capito, benissimo.
         OK! R-028: OK la tua proposta. Ottimo!"): R-028 applied verbatim from the approved proposal — title:
         "Float64 pipeline-metric goldens" becomes "Float goldens" (his point: all floats have the problem, not
         just float64); the tolerances (rel 1e-9 / abs 1e-12) out of the title (they are the REL_TOL/ABS_TOL
         constants in closecheck.py — the code owns them); (D-127) out. Description: the OpenBLAS ddot sentence out
         (the mechanism is not the rule — the full rationale, the thread-count ULP study, the <=4e-14 drift, the
         enumeration of the pins that stay exact, already lives in the closecheck.py module header) and the example
         enumeration "(train_loss, g_norm, the tps read-back truncations)" out (the classes stay). Kept: the WHAT
         (float goldens must use assert_close to be robust; the tolerances live in closecheck.py) and the boundary
         (what stays bit-exact assertEqual — without it, someone could "fix" the int/sha3 goldens to tolerant
         comparison). R-025 and R-026 confirmed after the explanations (gate = a boolean condition deciding whether
         a test runs/fails; no performance gate = no test fails on a timing measurement, PERF is print-only; R-026
         verified in the code at 38 @validate_call applications in src/reversi/lm/wrk_*.py). The Test discipline
         section is now FULLY PURE: R-022..R-029.2 carry no D-pointers. D-XXX references in the register: 23 (was
         24 at D-358). VERIFICATION: notes_format --write idempotent + --check clean (rules.md 294 lines).
D-360 | 2026-09-29 | the per-rule D-pointer review — the whole Pipeline contracts (RLM) section RETIRED,
         R-030..R-037 (Roberto: "Ora affrontiamo la sezione 'Pipeline contracts (RLM)'. Ho una idea radicale,
         secondo me nulla di questa sezione deve rimanere nel file rules.md. Ogni regola e' documentazione che deve
         essere specificata in uno dei tre moduli: state_machine, base_model, logistic_module. Fai una analisi
         accurata, dettagliata. dammi il tuo parere in merito. E se sei d'accordo, fammi una proposta delle
         modifiche alla documentazione dei sorgenti python o dei mirror docs. Procedi per favore." — after my
         per-rule verification + endorsement: "Via, procedi! Ottimo."): my radical idea was ENDORSED, and the
         analysis showed something stronger — ALL EIGHT invariants are ALREADY canonized in the mirror docs, so no
         source or doc change is needed: R-030 sentinel (state_machine.md Architecture + Verified invariants +
         logistic_model.md "The CREATED sentinels"); R-031 failure semantics (state_machine.md Architecture +
         invariants); R-032 unique names (state_machine.md API table + invariants); R-033 gate split (state_machine.
         md "The move gate is separate from execution" + the state_machine.py:373 comment + logistic_model.md
         "the gate split"); R-034 blackboard pre-declaration (logistic_model.md Architecture "LMContext is the
         shared blackboard" + Conventions "Blackboard fields are pre-declared on LMContext..."); R-035 cache flow
         (cache_manager.md load-or-compute + .SHA3-256 sidecar "a bad sidecar invalidates, never crashes" +
         state_machine.md "Cache path" prefix-CONCATENATED verbatim + the state_machine.py:178 comment); R-036 bool
         not a valid step (state_machine.md Architecture + invariants); R-037 target-driven stop (base_model.md
         "run(), the target-driven driver... a deeper target is a RESUME" + logistic_model.md the CONFIG-first
         half). Three grounds: (1) the house pattern — R-006 "the register points at them, never duplicates them",
         the D-355 precedent (R-020/R-021) applied to all eight; (2) the invariants are module-specific, they do not
         bind outside state_machine/base_model/logistic_model/cache_manager; (3) the register copy was already
         DRIFTING — "the 8192-chunk verify" in R-035 is stale (8192 appears nowhere in the code; binio.
         compute_sha3_256 uses chunk_size = 1 << 20, documented in binio.md), while the docs stay current per the
         docs_rules.md current-state contract. Correction to Roberto's framing: the invariants are owned by FIVE
         docs (state_machine.md x5, base_model.md, logistic_model.md x2, cache_manager.md, binio.md), not three
         modules. Action: R-030..R-037 RETIRED and the "## Pipeline contracts (RLM)" heading removed (the empty
         section leaves, like the Journal section at D-349); the R-030..R-037 gaps are permanent. Rules in force:
         45 -> 37. D-XXX references in the register: 14 (was 23 at D-359). VERIFICATION: notes_format --write
         idempotent + --check clean (rules.md 248 lines).
D-361 | 2026-09-29 | the per-rule D-pointer review — R-045, closing the Code style section (Roberto: "Proseguiamo
         con la sezione 'Code style'. Una sola regola, la R-045. Sono del parere che vada mantenuta, ma
         semplificata. Diciamo come devono essere le linee di codice. fine. Mi fai una proposta di
         semplificazione, pulizia, revisione." — after my proposal that KEPT the local 72–76 convention: "credo ci
         sia un fraintendimento. Io voglio le righe a circa 120 caratteri... non circa 72-76. Scriviamo
         semplicemnte questo. Le righe hanno una larghezza di circa 120 caratteri. Semplice no? Riformula la
         proposta per favore." — then "Proposta accettata. la regola va bene come da te proposta."): R-045 AMENDED
         (a content change, not a pointer removal) to the one-line rule "Code lines have a width of about 120
         characters." The target wrap width for code is now ~120 (a workspace-wide single width: code = docs =
         notes, consistent with the Governance paragraph "Lines are ~120 chars." and notes_format's WIDTH=120),
         REPLACING "match the local file's wrap convention (the lm zone ~72–76) / default <=79 (PEP8) when
         convention-less". Out: the linter-context sentence, the (D-314) precedent, the docs/notes ~120 (D-237)
         sentence (out of scope — the Governance paragraph + notes_format carry it), and the reflow guard (the
         protection already lives in AGENTS.md rule 3: sources are modified only on explicit request, so an
         unrequested reflow stays prohibited; a full-file reflow of the still 72–76-wrapped files to ~120 remains a
         user-directed, deliberate act, the D-314 pattern). Code style is now a single one-line rule; the per-rule
         review (D-340) is down to its LAST section, Docs (R-038..R-044). Rules in force: 37 (unchanged — an
         amendment). D-XXX references in the register: 12 (was 14 at D-360) — all remaining refs now sit in the
         Docs section. VERIFICATION: notes_format --write idempotent + --check clean (rules.md 243 lines).
D-362 | 2026-09-29 | the per-rule D-pointer review — the Docs section, CLOSING the review (Roberto:
         "Proseguiamo con la sezione 'Docs'. R-038 to R-044. Servono ? Non sono un duplicazione di quanto
         scritto in docs_rules ? Non sarebbe meglio avere una sola entry che prescrive di applicare i
         docs_rules ai docs ? Mi fai una proposta di semplificazione, pulizia, revisione." — after my
         per-rule mapping + proposal: "Applica la tua proposta. E' un ottimo passo in avanti. Non sono
         sicuro sia definitivo. Poi rivedo tutto e ti dico. Intanto applicala per favore."): the mapping was
         verified against docs_rules.md (read in full — "format rules for the mirror docs (docs/)") and
         probe_rules.md: R-038/R-039 are the mirror-doc-format side (duplicated by docs_rules.md), while
         R-040..R-044 are NOT — they govern the docstrings/comments INSIDE the .py files (src/, test/,
         probes/), which docs_rules.md does not cover, and probe_rules.md carries no docstring rules
         (verified). Applied: R-038 becomes the single identity + pointer "The mirror docs (docs/)" — one
         doc per source file, mirroring the source tree (AGENTS.md rule 5; the mapping is already carried by
         R-015) + the R-003-pattern pointer to notes/docs_rules.md (the header, the 7 fixed sections, the
         forbidden-history list, the same-commit lifecycle, the test-doc variant); R-039 RETIRED — 100%
         duplication of docs_rules.md §3.4 word for word ("OPEN R/M/T items only, with their pointers. If
         none: one line, None. Closed items never appear.") and its "(docs_rules.md §4, D-114)" pointer was
         STALE anyway (current file: §3.4; §4 = "Forbidden in a mirror doc"); the R-039 gap is permanent.
         R-040..R-044 KEPT as pure code-style rules (the same genre as the R-045 just amended at D-361),
         D-refs removed: R-040 (D-224, D-226); R-041 (D-267/D-270 becomes "the test and probe docstrings keep
         their own rules, below", the "like the D-314 reflow" and D-317/D-318 out); R-042 (the D-150/D-146
         examples + D-269/D-270 out — the quoted "the D-106 re-pin" stays, it is the rule's example of what
         provenance IS, not a pointer of the rule itself); R-043 (D-267); R-044 (D-270). R-043/R-044 stay
         separate (R-044 carries its own exception and refers to "the test-doc rules"). Rules in force: 37 ->
         36. D-XXX lines in the register: 12 -> 1, and that one is the R-042 quoted example — the register
         carries NO real provenance pointer anymore: the per-rule review (D-340) is COMPLETE. Roberto: not
         necessarily final — he will re-review the whole register and direct the follow-up. VERIFICATION:
         notes_format --write idempotent + --check clean (rules.md 236 lines).
