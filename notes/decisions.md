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
