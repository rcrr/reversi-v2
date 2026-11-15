# rules_compliance_audit_2026-11-15.md — the capillary rules-compliance audit

A one-off analysis (the notes/analyses/ home): the workspace-wide audit of the consistent application of every rule
in notes/rules.md and of the rules carried by the notes/ domain rule files. Requested by the user at the end of
session 128 (2026-11-15).

METHOD: six parallel READ-ONLY audit zones (A-F) run with the house audit tools (notes_lint, overview_audit,
docs_format_audit, license_header_audit, src_reflow) plus targeted static checks; three further rules (R-410, R-780,
R-120) checked directly by the session agent. NO fix was applied: this document is analysis + proposals only.

## Severity legend

- **violation** — the rule is broken as written; a fix is proposed.
- **minor** — a deviation from the letter of the rule with limited impact (or an exception not recorded as such); a
  fix is proposed where sensible.
- **info** — an observation (a desire not met, a tool gap, a historical residue); no fix required.

## The rule inventory and zone assignment

Status: P = passed (evidence in the zone section), F = findings (in the zone section), — = not tree-verifiable
(behavioral / process rule), PENDING = the zone report has not arrived yet.

| Rule | Topic | Zone | Status |
| --- | --- | --- | --- |
| R-010 | AGENTS.md the constitution | A | P (no findings) |
| R-020 | rules.md the register format | A | F (minor: missing blank line before the L62 heading; info: 8 rules >3 lines) |
| R-030 | overview.md the entry point | A | F (minor: the new analyses file unindexed) |
| R-040 | decisions.md the open log | A | F (violation: D-627 + D-463 missing from vol 007 while cited in 4+1 places) |
| R-050 | log.md the session journal | A | F (violation: 13 phantom session numbers in 3 H1 ranges; minor: log_005 26 > 25 cap) |
| R-060 | the domain rule files | A/F | F (minor: register dangles notes/tools.md, omits latex_rules + design_principles) |
| R-070 | ideas.md the OPEN backlog | A | P (I-001…I-022 unique, legend statuses, closure placement) |
| R-100 | notes English, replies in the user's language | A | F (violation: the journal's own Italian prose in closed vols 003/004/005) |
| R-110 | the notes are autonomous | — | — (behavioral) |
| R-120 | one D-number per fix campaign | direct | P (spot: the last 30 commits all carry a D-number prefix) |
| R-130 | the notes are the publication material (no DSH/vLLM/harness) | A | F (violation: post-rule infra notes in frozen vols 006/002/004) |
| R-200 | the notes format guard | A | F (violation: 4/6 closed journal vols RED on explicit request, 26 LISTMARK) |
| R-210 | the pre-commit gate | A | P (overview audit green, twice) |
| R-250 | the impact set (documents per change class) | A/E | F (violation: latex_lint.py unlisted in wsutils.md; the analyses file unindexed) |
| R-260 | the pre-commit consistency check | — | — (behavioral) |
| R-270 | new function duplication check | — | — (behavioral, historical) |
| R-300 | the workspace is a git repo (minimal .gitignore) | E | F (minor: 5 extra .gitignore entries) |
| R-310 | all Python sources under src/ | E | F (minor: 6 src modules lack a 1:1 test mirror) |
| R-320 | .venv at the workspace root (pyproject) | E | P |
| R-330 | docs/ mirrors src/ one file to one file | C | F (violation: 6 `__init__.py` without mirror docs) |
| R-340 | wsutils/ holds the workspace utilities | A | F (violation: latex_lint.py absent from the wsutils.md inventory) |
| R-350 | expensive generated data in build/ | E | P |
| R-360 | the models/ zone | E | P (all five sub-checks a-e) |
| R-400 | Reversi (othello), NOT chess | B | P (all 947 file/rank hits reviewed; zero board-context) |
| R-410 | little-endian only (native tobytes) | direct | P (no big-endian dtype specifier anywhere in src/; the native tobytes() usages in pattern.py, regab.py, mobility.py, binio.py, hlp_*.py are the sanctioned form; binio.py:426 documents the little-endian intent) |
| R-500 | PEP 8 the base style | B | F (minor: 24 W291 trailing-ws banner lines in 12 files) |
| R-510 | the desirable function size 20-30 lines | B | P (info: top-10 long functions, max 213) |
| R-520 | prose 100 preferred, 120 ceiling | B | F (violation: 21 lines over the 120 ceiling in 8 files) |
| R-530 | docstrings: WHAT, never HOW | B | P (info: 2 borderline HOW-sentences in the sample) |
| R-540 | docstrings: no D-XXX | B | P (zero occurrences in src/) |
| R-550 | no I-XXX in the code | B | F (violation: 8 I-XXX in probe COMMENTS, 7 files) |
| R-560 | docstrings: the layout | B | F (minor: 8 files / 15 docstrings off the fixed point — the D-427 backlog) |
| R-570 | test docstrings: DEVIATIONS | direct | F (minor: 19/541 test docstrings exceed the light 1-2-line format — 3 lines mostly, max 7: test_pattern 3x, test_wrk_vld_positions 2x, test_wrk_optimize 2x, test_wrk_plot 2x, test_state_machine 2x, the rest 1x each) |
| R-580 | probe docstrings: DEVIATIONS | F | P |
| R-590 | a new external dependency needs explicit permission | E | P (info: python-dotenv is test-only) |
| R-595 | every source file carries the GPL header | B | P (369/369 tracked source files) |
| R-600 | gitignored is not disposable | — | — (behavioral) |
| R-700 | the mirror docs (docs/) | C | F (same root cause as R-330; + the test_index.md skeleton break, 3 unbalanced spans) |
| R-750 | tests write only under build/tmp | D | F (violation: 6 modules write to /tmp, no `dir=` anchor) |
| R-760 | test-file idiom | D | F (minor: test_state_machine bypasses the shared idiom; + the 6 R-750 modules) |
| R-770 | DB-dependent tests (the gate first in setUp) | D | P (all 14 gated modules) |
| R-780 | PERF=1 print-only (no performance gates) | direct | P (the 15 PERF-gated test files carry zero timing assertions; the PERF bodies are print-only) |
| R-790 | worker factories (@validate_call) | D | P (19/19 factories + 3 patch-by-name spot-checks) |
| R-800 | the test runner is unittest (no pytest) | D | P |
| R-810 | float goldens use assert_close | D | P (every float-literal assertEqual is sanctioned) |
| R-820 | suite tiers (single source: tags.py) | D | P (info: the A2050 VLONG/VVLONG wording) |
| R-830 | canonical order (run_utests.sh) | D | P (info: the anova pair split, documented) |
| R-840 | before git commit (the full pre-commit) | — | — (behavioral; observed followed in this session: the 8f877a4 checkin ran the wrapper suite LONG=1 first) |
| R-850 | the documented contract is the test specification | D (sample) | P (info: the anova FLOW functions pinned by the probe) |
| R-860 | the three shapes of a test set | D (sample) | P |

The domain rule files (each audited inside its zone): overview_rules.md (A) · decisions_rules.md (A) · log_rules.md
(A) · wsutils.md (A inventory + F tool docs) · docs_rules.md (C) · probe_rules.md (F) · naming.md (B, the R-400
vocabulary source) · design_principles.md (F) · latex_rules.md (F) · the ideas.md / ideas_closed.md preambles (A).

## Zone A — notes governance (COMPLETE)

Checks performed: R-020 (the register read in full, 50 rules extracted) · R-200 (notes_lint default set green +
explicit runs on all 14 closed volumes) · R-030 (overview_rules.md first, then the full 235-line overview: section
order, table grammar, bullet caps, the Index cross-check vs find notes/ — 31 files) · R-210 (overview_audit run
twice, both green) · R-040 (decisions_rules.md; all 626 D-headers extracted: header-form regex, 9-space indent
profile per file, gap analysis) · R-050 (log_rules.md; H1 + pointer lines of all 7 volumes; all 115 session headers
extracted: global monotonicity, dups, gaps) · R-070 (both ideas preambles + all 22 I-entries) · R-130 (39
dsh/vllm/harness/deepseek hits, each classified) · R-340+R-250 (wsutils.md inventory vs the 11-tool tree) ·
probe_rules (the 24-probe tree structure) · R-100 (Italian-prose scan over all 31 notes files).

### Findings

- **[R-040] violation — D-627 is missing from closed volume 007, though cited as its last entry in four
  places.** decisions_007.md ends at D-626 (line 2794; `grep -c "^D-627 "` = 0 — VERIFIED by the session agent),
  but: notes/decisions.md:16 (the D-629 rotation entry: "had 2811 lines (D-426…D-627)"), notes/overview.md:218
  (Index: "volume 007 (D-426…D-627)"), notes/log.md:14 and notes/hist_log/log_005.md:728 (session 127 closes
  "(D-627)"). Root cause: the session-127 close recorded D-627 in the journal and the commit message (2268ac7) but
  NEVER appended the D-627 entry to the decisions log — a pre-existing record gap, amplified by the rotation's
  Index range. Proposed fix: disclose via a new open-log decision entry (the closed volume is append-frozen, iron
  rule 3) + correct the overview Index range to D-426…D-626 in the same commit (forward repair of the open file).
- **[R-040] violation — D-463 missing from closed volume 007.** Entries run …D-462 (line 582), D-464 (line 587)
  with no D-463, yet notes/hist_log/log_004.md:2194 cites it as a real decision. Zero mentions in any decisions
  file (VERIFIED: count 0). Proposed fix: same disclosure-entry remedy.
- **[R-200] violation — 4 of 6 closed journal volumes are RED on explicit request.** log_000 (2 LISTMARK: 845,
  1103 — VERIFIED), log_001 (3: 148, 312, 1603), log_002 (6), log_003 (15) — all "line-leading + / * (the
  Obsidian nested-bullet trap)", 26 hits total. notes_lint.py's own docstring claims the closed volumes were
  "cleaned and green at D-368" — no longer true. All 8 closed decisions volumes and log_004/005 are green.
  Proposed fix: the closed volumes are frozen (iron rule 3) — document the historical exception in log_rules.md /
  the lint docstring (the explicit closed-volume mode is already "on request" per R-200), and/or re-run the
  cleaner if the house deems the D-368 claim worth restoring.
- **[R-050] violation — 13 session numbers claimed in H1 ranges have no section in any volume.** log_000 H1
  "sessions 1–24" but the last section is 23; log_003 H1 "38–89" but the last section is 78 (79–89 absent);
  log_004 H1 "90–101" but session 98 is absent. Missing: 24, 79–89, 98 (verified exhaustively — no header
  variant, no prose section). Proposed fix: factual correction of the three H1 ranges — explicitly permitted by
  log_rules.md ("archived volumes are read-only EXCEPT factual corrections") — or a disclosure entry.
- **[R-130] violation — DSH/vLLM/DeepSeek infrastructure behavior recorded AFTER the rule was in force** (D-154,
  2026-09-11): notes/hist_decisions/decisions_006.md:1409-1410; notes/hist_log/log_002.md:354,966;
  notes/hist_log/log_004.md:666,678,1511-1512. (A larger PRE-rule body exists as history — decisions_000,
  log_000 (incl. a DEEPSEEK_API_KEY credential + endpoint details at 447-449), log_001, log_002 — plus justified
  hits (D-154 itself), false positives (test "harness"), borderline external-model mentions, and path-name "dsh"
  provenance. The OPEN files are clean.) Proposed fix: the post-rule hits sit in frozen volumes — disclosure + a
  forward ruling that the publication edit pass (when the notes become the GitHub material) strips them; the
  credential detail in log_000 is worth an explicit note.
- **[R-100] violation — the journal's OWN prose in Italian in three closed volumes.** log_004 (worst: session
  titles at 6, 2394, 2468 …), log_003 (titles at 1576, 1707, 1740), log_005 (line 5 — the session-102 title).
  In the decisions/ideas files Italian appears only as verbatim user quotes (acceptable, info). The open files are
  all English. Proposed fix: a language ruling going forward (journal prose in English, user quotes exempt); the
  closed volumes cannot be rewritten (iron rule 3) — disclosure only.
- **[R-340/R-250] violation — wsutils/latex_lint.py (17.6 KB, on disk) has NO row in the wsutils.md §6
  inventory** ("latex" appears nowhere in notes/wsutils.md — VERIFIED: 0 mentions); it is referenced in the
  history (decisions_007.md:2328) and governs the latex/ zone. Secondary: its docstring lacks the §3 fixed
  header's USAGE/SAFETY/ORIGIN labeled sections. Proposed fix: add the inventory row (category, purpose, write
  scope, ORIGIN D-number) to notes/wsutils.md + the docstring header sections.
- **[R-020] minor — missing blank line before a section heading in the register.** notes/rules.md:62 "## Language
  & collaboration" immediately follows R-070's description (line 61) with no blank line; all 8 other section
  headings have one. Not flagged by the guard. Proposed fix: insert the blank line.
- **[R-050] minor — log_005 holds 26 sessions vs the 25-session cap** (log_rules.md:11). Disclosed in D-629; a
  consequence of rotate-only-at-session-boundary (the 26th session started before the cap was checked). No fix
  beyond the disclosure.
- **[R-030] minor — a new unindexed analyses file.** notes/analyses/rules_compliance_audit_2026-11-15.md (created
  during this audit) is not named in the overview Index; the Index's analyses/ directory bullet names only
  work_report.md. R-250 wants an Index entry for a new notes/ file in the same commit; the R-210 auditor stays
  green because the directory bullet satisfies it. Proposed fix: extend the directory bullet to name both files
  (or list the new one) when the report is committed.
- **[R-020] info — 8 register rules with >3-line descriptions** (allowed "longer only when it must be"): R-200
  (4), R-210 (6), R-250 (8), R-360 (7), R-520 (5), R-560 (11), R-595 (6), R-820 (4). Guard green.
- **[R-040] info — documented legacy forms in the closed decisions volumes** (the guard explicitly accepts them;
  documented in decisions_006's lint-tolerance entry): 11-space FIELD-block continuations (vol 000: 324 lines,
  001: 468, 002: 6, 004: 2) and letter-suffixed headers D-156b/c/d (decisions_001.md:934,954,977); the D-152 gap
  is documented as a legal lost number (decisions_006.md:622).
- **[probe_rules] info — not tree-verifiable beyond structure:** the a/b/c per-check classification and the R-580
  docstring conventions are code-content checks (covered by zone F). The tree structure itself: 24 probes, all
  verify_*.py, all git-tracked, the hub present, none in scratch/ — compliant.

### Passed

R-010 (no findings) · R-020 core (50 rules R-010…R-860, strictly ascending by value, no duplicates; the bold-title
+ blank + description form; the single-bold-line form used correctly by R-100/R-410/R-500/R-510/R-750/R-780;
guard green) · R-210 (overview audit OK twice: "49 source rows, 49 test rows, 9 data bullets, 30 index
references, 46 suite measurements — all consistent") · R-030 core (the pointer section + exactly the seven
sections in exact order; the table grammar; Current state 3 bullets ≤ 10, no bullet-per-campaign; Next steps 6
open items; the Index covers every notes/ file and every entry resolves) · R-040 format (the header form on all
626 entries; 9-space continuations in the open log + volumes 003/005/006/007; a blank line before every entry;
D-numbers globally unique and strictly increasing) · R-050 format (the H1 + pointer line in all 7 volumes; the
115 session headers globally unique and strictly monotonic) · R-070 (I-001…I-022 unique across both files, no
gaps; statuses from the legend; no closed idea in the open file) · R-340 inventory→disk (all 11 listed tools
exist on disk with documented purpose + write scope).

### Summary

Violations: 7 · Minor: 3 · Info: 5. Most important: (1) RECORD INTEGRITY (R-040) — D-627 and D-463 are cited in
the journals, the rotation entry and the Index but absent from the closed volume (D-627 was never written to the
decisions log at session 127; the Index range overstates the volume); (2) FORMAT GUARD RED ON CLOSED HISTORY
(R-200) — 4 of 6 closed journal volumes fail the explicit check with 26 LISTMARK hits, contradicting the
"cleaned and green at D-368" claim; (3) PUBLICATION-MATERIAL CONTAMINATION (R-130 + R-100) — post-rule
DSH/vLLM/DeepSeek infra notes and the journal's own Italian prose survive in frozen volumes: the remedy is
disclosure + forward rulings, not rewriting.

## Zone B — source code style (COMPLETE)

Checks performed: R-595 (license_header_audit over the full scope: 141 .py + 1 .sh + 21 .tex + 1 hook + 205 .json
= 369 tracked source files; the 205 .json verified as exactly the test/reversi/data + models/ sets) · R-520 (awk
physical-length scan over all 142 tracked .py + .sh) · R-540 (D-XXX census in src/) · R-550 (I-XXX census in
src/ test/ probes/, every hit classified check-label vs comment vs data file, cross-checked against the house
interpretation in the decisions log) · R-400 (947 file/rank hits reviewed for board-context usage) · R-560
(src_reflow.py check mode over all 52 src files, read-only) · R-500 (pycodestyle/flake8 absent from the .venv —
R-590 — so a light manual spot-check) · R-510 (ast function-length scan) · R-530 (light 3-file docstring sample).

### Findings

- **[R-520] violation — 21 physical lines exceed the 120-char hard ceiling, in 8 files:**
  `src/reversi/pattern.py` (14 lines: the pattern-table dict literals L93/97/101/105/109/113/117/121/125/129/133/
  137 at 128-131 chars each, e.g. L97 `{"type": "1", "sample_mask": 0x0000000c30000000, "sample_name": "SNAKE",
  "level": 2, "n_instances": 4, "n_stabilizers": 2}`, plus L379 (130) and L700 (149));
  `src/reversi/lm/hlp_config_schemas.py:324` (173 — the `side` Field description string);
  `src/reversi/lm/wrk_optimize.py:159` (148 — a `ctx.log_event(...)` call);
  `src/reversi/lm/hlp_zed.py:86` (122 — the `Callable[[npt.NDArray[np.float32]], ...]` annotation);
  `src/reversi/lm/model_weights.py:161` (121 — a `raise ValueError(...)` line);
  `src/reversi/lm/wrk_vld_positions.py:94` (121 — a `ctx.log_event(...)` line);
  `probes/verify_wmaps.py:207` (124 — a check-label string wrapping a pinned test line);
  `run_utests.sh:52` (122 — the `echo "run_utests: PERF=..."` banner).
  Proposed fix: wrap/split each to ≤120 (for pattern.py the table literals split across two lines per entry — the
  value pins in the probe and test_pattern.py pin the mask/name VALUES, not the physical layout, so it is safe;
  for verify_wmaps.py:207 split the quoted string; for the .sh echo, two echo args or a shorter banner). No
  documented per-file exception covers any of these. A SOURCE change — explicit user request required.
- **[R-550] violation — 8 I-XXX references in probe comments (7 files):** R-550 bans I-XXX in any docstring or
  comment of Python code in src/test/probes; R-580's deviation covers check labels and item ids ONLY, and the
  decisions log confirms this interpretation (decisions_007.md:1046: an I-017 in a probe header was trimmed as an
  R-550 repair). Evidence: `probes/verify_gradient.py:294`; `probes/verify_validate.py:218`;
  `probes/verify_wrk_features.py:41`; `probes/verify_logistic_model.py:84,93,232`; `probes/verify_save.py:209`;
  `probes/verify_su_analysis.py:32` (which also carries D-258/D-295/D-298 in the banner — plain `#` comments;
  R-540's mechanical scope was src/ only, noted as an observation). Proposed fix: reword each comment to drop the
  I-NNN id (name the change in words, e.g. "the level reordering"), keeping the check labels untouched
  (R-580-allowed). The 18 other I-XXX hits are R-580-allowed check labels, and 4 more sit in the JSON data files
  test/reversi/data/rlm_05.json / rlm_06.json (data fields — not Python code, out of R-550 scope). A SOURCE change
  — explicit user request required.
- **[R-560] minor — 8 of 52 src files are not at the canonical docstring fixed point** (src_reflow.py check
  mode): `src/reversi/__init__.py` (1 docstring), `src/reversi/feature.py` (1), `src/reversi/lm/__init__.py` (1),
  `src/reversi/lm/hlp_final_log_print.py` (1), `src/reversi/lm/hlp_gradient.py` (2), `src/reversi/lm/
  wrk_analytics.py` (0 docstrings — 1 comment block), `src/reversi/mobility.py` (8), `src/reversi/tools/
  __init__.py` (1) — 15 docstrings + 1 comment block. No per-file documented deviation exists; D-427
  (decisions_007.md:44-45) records them as "backlog format passes" (deliberately not a repo-wide reorganization)
  — hence minor, not violation. Proposed fix: one `src_reflow.py --write` format pass per file at its next
  scheduled campaign (the tool verifies logical identity + idempotence pre-write and refuses on failure).
  `src/reversi/tools/prng.py` is at the fixed point, WITHIN its documented D-426/D-427 ~120-wrap exception (max
  line 110) — a documented exception, not a finding.
- **[R-500] minor — 24 trailing-whitespace lines in 12 files (PEP 8 W291):** in 12 files the bare `#` separator
  lines at positions 16 and 21 of the 26-line GPL banner are `# ` (trailing space) instead of `#` —
  `base_model.py`, `lm/wrk_config.py`, `wrk_design_matrix.py`, `wrk_features.py`, `wrk_generate.py`,
  `wrk_gradient.py`, `wrk_positions.py`, `wrk_save.py`, `wrk_validate.py`, `wrk_vld_positions.py`, `wrk_wmaps.py`,
  `wrk_zed.py` (e.g. base_model.py:16). These lines sit just outside the license audit's 10-marker window, so
  R-595 passes while W291 technically does not. Proposed fix: strip the one trailing space on those 24 banner
  lines (pure whitespace, zero behavior change). (An earlier grep-based count of 437 was a false positive —
  `[ \t]` in POSIX ERE brackets matches a literal `t`; the authoritative Python scan finds exactly 24.)
- **[R-510] info — the 10 longest functions** (desirable 20-30 lines; no ceiling): 213 `pattern.py __init__`; 196
  `tools/opt_lbfgs.py lbfgs`; 170 `lm/hlp_analytics.py _format_pattern_feature_table`; 151
  `_format_mobility_feature_table`; 130 `lm/wrk_optimize.py _up`; 118 `lm/hlp_generate.py
  hlp_generate_compute_w_dense`; 114 `lm/model_weights.py model_weights_read_file`; 114 `lm/hlp_wmaps.py
  hlp_wmaps_compute`; 104 `pattern.py compute_principal_indexes`; 101 `lm/hlp_su_analysis.py
  hlp_su_analysis_statistics`. No fix required (a desire); candidates for future decomposition.
- **[R-530] info — 2 borderline HOW-leaks in a 3-file sample:** `mobility.py:263`
  (`_numba_popcount64_kernel` — "LLVM often replaces this implementation with native CPU popcnt instructions")
  and `random_game.py:87` (`random_game_make_move` — "Asks random_game_choose_move for the move to play, executes
  it on p via position_flips"). Optional rewording to the observable contract at the files' next format pass.
- **[R-520] info — 728 lines exceed the preferred 100-char width** (707 in the 101-120 band, 21 over 120 as
  above) across the 142 tracked .py/.sh files; heaviest: hlp_config_schemas.py 57, test_pattern.py 53,
  verify_design_matrix.py 39, notes_lint.py 37, pattern.py 36, test_board.py 32. No fix required (exceeding 100 is
  allowed up to 120 for single-word pull-ups; the bulk is code lines, which have no preferred wrap).

### Passed

R-595 (369/369 tracked source files carry the standard 26-line GPL header, correct marker order and FILE_NAME
basenames; exit 0) · R-540 (zero D-XXX occurrences anywhere in src/) · R-400 (no board-context "file"/"rank"
usage in src/, test/ or docs/ — all 5 "rank" hits legitimate, all "file" hits ordinary English) · R-500 base style
(no tabs, naming clean — `_MarginalAccumulator` / `_JointAccumulator` correctly CamelCase).

### Summary

Violations: 29 (21× R-520 over-120 lines in 8 files; 8× R-550 I-XXX in probe comments across 7 files) · Minor: 2
families (R-560: 8 files / 15 docstrings + 1 comment block off the fixed point, the D-427 backlog; R-500: 24 W291
banner lines in 12 files) · Info: 3 (R-510 top-10; R-520 728 over-100; R-530 2 borderline). Passed: R-595, R-540,
R-400, R-500 base. Top 3: (1) the 21 over-120 lines — the only hard-ceiling breach in the zone, 14 of them in
pattern.py; (2) the 8 I-XXX probe comments — an explicit rule break under the house's own recorded
interpretation, a cheap rewording; (3) the 8 files off the R-560 fixed point — already the D-427 backlog, closed
by a scheduled src_reflow pass per file.

## Zone C — docs mirror (COMPLETE)

Checks performed: R-330/R-700/R-250 1:1 mirror completeness both directions (git ls-files directory pathspecs +
path-mapped diff; note: the `src/reversi/**/*.py` pathspec silently drops top-level files in this git — the
directory pathspec is the reliable form) · docs_rules.md format audit (wsutils/docs_format_audit.py, summary +
--verbose, both read-only) · docs_rules §8 user zone (contents, trailing whitespace, wrap rule, a 7-field Truth
spot-check, the non-indexing requirement) · the overview Doc column (10-row sample, 10/10 resolve) · R-250 impact
set (merged with check 1; clean tree, no new file lacks a doc).

### Findings

- **[R-330/R-700/R-250] violation** — six `__init__.py` files have no mirror doc (3 src + 3 test); the rule text has
  no `__init__` exception (docs_rules §7 lists only `test/reversi/data/*.json` as fixture-exempt). Evidence: 52
  tracked src .py vs 49 docs .md, 52 tracked test .py vs 49 docs .md; missing: `src/reversi/__init__.py`,
  `src/reversi/lm/__init__.py`, `src/reversi/tools/__init__.py`, `test/reversi/__init__.py`, `test/reversi/lm/
  __init__.py`, `test/reversi/tools/__init__.py` (none exist on disk). Mitigating: all six are docstring-only
  package markers (30-35 lines: GPL header + a package docstring), so the gap is arguably intentional. Proposed fix —
  a user/decision call: (a) create six small mirror docs (the docstring content is the natural body), OR (b) add an
  explicit `__init__.py` exception to R-330 / docs_rules §7 with a D-entry (iron rule 4) — then the overview
  rewording below becomes true.
- **[overview consistency, tied to R-330] minor** — the overview "Mirror docs" bullet overclaims 1:1 completeness.
  Evidence: `notes/overview.md:37` "docs/ mirrors the tracked sources one-to-one — every source and test file has
  its doc" is false while the six `__init__` docs are missing. Proposed fix: reword to "every module file has its
  doc (package `__init__` files excepted)" once the exception is legislated, or let fix (a) make the claim true.
- **[docs_rules §3/§6] violation** — `docs/test/reversi/test_index.md` breaks the fixed section skeleton: missing
  "Goldens pinned", "Conventions", "Integration"; unexpected "Notes"; size 14 lines (the budget is 25-120). The
  only structurally non-conforming doc in the tree. Proposed fix: rewrite to the test-doc skeleton (Coverage /
  Architecture / Goldens pinned / Open issues / Conventions / Integration), folding "Notes" into the right section.
- **[docs_rules format] violation** — unbalanced code spans in 3 docs ("code spans are never split across lines" is
  a hard rule): `docs/src/reversi/lm/hlp_final_log_print.md` [lines 9,10], `docs/src/reversi/lm/wrk_design_matrix.md`
  [24,25], `docs/src/reversi/tools/opt_lbfgs.md` [23,24]. Proposed fix: re-wrap the offending spans (one span per
  line, unsplit).
- **[docs_rules format] minor** — 27 docs carry 58 lines over 120 chars (the ~120 wrap is soft; concentrated in the
  lm/ workers and their test mirrors). Examples: `docs/src/reversi/feature.md:77`; `lm/hlp_analytics.md:3,53,97,98`;
  `hlp_config_schemas.md:25,45`; `hlp_design_matrix.md:27`; `hlp_generate.md:22`; `hlp_plot.md:10,79`;
  `hlp_zed.md:3,17,21`; `model_weights.md:25`; `wrk_analytics.md:2,17,18,19,20`; `wrk_config.md:3` (remaining 17:
  wrk_generate, wrk_optimize, wrk_plot, wrk_positions, wrk_vld_positions, random_game, regab, tools/prng,
  test/lm/test_hlp_plot, test_hlp_design_matrix, test_wrk_analytics, test_wrk_gradient, test_wrk_indexes,
  test_wrk_plot, test_wrk_vld_positions, test_wrk_zed, tags, test_pattern). Proposed fix: one batch re-wrap via the
  wsutils prose re-wrapper in a docs-only commit.
- **[docs_rules format] minor** — 3 test docs have ragged table rows (inconsistent pipe counts):
  `docs/test/reversi/lm/test_hlp_design_matrix.md` (pipes [4,5]), `test_hlp_generate.md` ([4,5]),
  `test_wrk_analytics.md` ([4,6]). Proposed fix: fix the broken row(s) so each table has uniform column counts.
- **[docs_rules §5] info** — 8 docs outside the (explicitly "Target") size budget: under 60-120 —
  `docs/src/reversi/index.md` (46), `lm/wrk_generate.md` (56), `docs/test/reversi/closecheck.md` (46), `paths.md`
  (54), `test_index.md` (14); over — `hlp_config_schemas.md` (121); under the 150-200 hub budget —
  `logistic_model.md` (139), `pattern.md` (148), `state_machine.md` (109). No fix mandatory (target, not rule).

### Passed

R-330 orphan direction (ZERO orphan docs in both trees) · R-330 non-`__init__` coverage (all 46 non-`__init__` src
files and 46 test files have their 1:1 mirror doc, tracked and on disk) · R-250 impact set (no new/untracked
source/test file) · docs_rules §8 user zone (`docs/user/` carries exactly the two §8-named docs; English; 0
trailing-whitespace lines; the 12 over-120 lines in the guide are 11 table rows + 1 unbreakable code span —
compliant as written; the 7-field Truth spot-check passed; the user docs are NOT indexed in the overview tables,
the sole mention being the zone-registration bullet) · the overview Doc column (10/10 sampled rows resolve) · the
format census (59/98 mirror docs fully clean).

### Summary

Violations: 3 (six missing `__init__` mirror docs; the test_index.md skeleton break; 3 unbalanced code spans) ·
Minor: 3 (the overview 1:1 overclaim; 27 docs / 58 lines over 120; 3 ragged tables) · Info: 1 (8 docs outside the
soft size budget). Top 3: (1) the six `__init__.py` docs — a letter-of-rule R-330/R-700 breach that also falsifies
the overview claim; needs a user decision (create 6 docs vs legislate an exception), not a silent drift; (2)
test_index.md — the only skeleton break in 98 docs, a rewrite not a patch; (3) the cosmetic drift is real but
bounded — a good candidate for one batch re-wrap commit.

## Zone D — test discipline (COMPLETE)

Checks performed: R-750 (write side-effect census over test/, every temp-dir definition traced to its anchor) ·
R-760 (the 5 idiom elements per temp-file module) · R-770 (the 14 db-gate modules: gate FIRST in setUp + header
states the gated state) · R-810 (every float-literal assertEqual classified vs closecheck.py's sanctioned
stays-exact categories) · R-820 (tier semantics across tags.py, the runner header, rules.md, overview.md) · R-830
(the runner module order) · R-800 (pytest census) · R-790 (the 19 wrk_* factories + 3 patch-by-name spot-checks) ·
R-850/R-860 (sample-based pin coverage on hlp_anova / hlp_wmaps / hlp_zed).

### Findings

- **[R-750] violation** — 6 test modules write test artifacts to the SYSTEM temp dir (/tmp) instead of
  workspace_root/build/tmp: they call `TemporaryDirectory()` / `mkdtemp()` with NO `dir=`. Evidence:
  `test/reversi/lm/test_wrk_anova.py:112`; `test/reversi/lm/test_hlp_su_analysis.py:110`;
  `test/reversi/tools/test_usage_binio.py:68,131,167` (`mkdtemp(prefix="binio_usage_")`);
  `test/reversi/lm/test_wrk_analytics.py:502,904,1054,1097`;
  `test/reversi/lm/test_wrk_final_log_print.py:92`; `test/reversi/lm/test_wrk_su_analysis.py:111`. Proposed fix:
  add `dir=str(CUSTOM_TMP_BASE)` to each (importing CUSTOM_TMP_BASE from test.reversi.paths), matching the ~20
  conforming modules. Note: all 6 DO clean up afterwards (addCleanup / tearDown / rmtree) — only the location is
  wrong; low practical harm, but a clear breach of the "ONLY under build/tmp" clause. A SOURCE change — explicit
  user request required (iron rule 2).
- **[R-760] minor** — `test/reversi/tools/test_state_machine.py:57` re-derives its own
  `TMP_DIR = Path(__file__).resolve().parents[3] / "build" / "tmp"` instead of importing CUSTOM_TMP_BASE from the
  shared paths module, and writes directly to TMP_DIR (mkdir inside the test method at :431, no per-test
  TemporaryDirectory, no setUpClass). The location is correct (build/tmp) so R-750 is satisfied, but the shared
  idiom is bypassed. Proposed fix: import CUSTOM_TMP_BASE and use the `TemporaryDirectory(dir=…)` idiom like the
  other tools tests. (The 6 R-750 modules are also R-760 deviations on the anchor element — same root cause.)
- **[R-820] info** — the "A2050 chain" is attributed to VLONG in tags.py but surfaced under VVLONG in the
  overview's time note — descriptive wording only, not a semantic conflict.
- **[R-830] info** — the anova pair is split (test_hlp_anova early, test_wrk_anova at "step 6, after INDEXES") —
  documented in-runner as intentional machine-order placement.
- **[R-850] info** — the two hlp_anova FLOW functions (compute_analysis, generate_report) are pinned by the probe
  (verify_anova), not the unit micro-suite — as the mirror doc states.

### Passed

R-770 (all 14 db-gate modules: the gate is the FIRST setUp statement and each header states the gated state, e.g.
test_regab.py:36) · R-810 (every float-literal assertEqual is a sanctioned exact value — f32-quantized
train_loss, hand-computed toy metrics, deterministic pure fns, config echoes, degenerate zeros, a deterministic
integer mean; the genuine non-bit-reproducible goldens correctly use assert_close — 77 hits) · R-820 (tier names,
cumulative implications, env-var names consistent across all four locations) · R-830 (canonical stable order:
tools → board/pattern concepts → infrastructure → DB → pipeline in machine order, each hlp_ before its wrk_, the
17-level end-to-end chain LAST by explicit design) · R-800 (no pytest in test/, pyproject.toml, run_utests.sh —
occurrences only in notes/ prose) · R-790 (all 19 wrk_* factories carry the uniform
`@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` gate; patch-by-name confirmed in 3 spot-checks) ·
R-850/R-860 sample (hlp_wmaps FULLY pinned, 11/11; hlp_zed FULLY pinned, 9/9; hlp_anova fully pinned at kernel
level, the 2 FLOW functions pinned by the probe per the doc).

### Summary

Violations: 1 (R-750) · Minor: 1 (R-760) · Info: 3. 7 of 9 checks pass clean; the overall test-discipline health is
strong. The R-750 breach is the only true rule violation in the zone and is an easy mechanical fix.

## Zone E — layout, models, dependencies (COMPLETE)

Checks performed: R-300 (.gitignore read, compared to the documented minimal set) · R-310 (git ls-files '*.py' zone
check + src/test mirror diff) · R-320 (pyproject.toml read) · R-590 (import census over src/ vs the declared
dependencies, lazy imports re-checked with a broader grep) · R-350 (tracked data-file census) · R-360 a-e (the 198
config paths, ec20 numbering continuity, the 21 index.md tables 1:1 vs disk, base_dir relativity, the name-only-in-
config spot check) · the build/ mirror (5 sampled models) · R-600 (not tree-verifiable, skipped).

### Findings

- **[R-300] minor** — .gitignore carries 5 entries beyond the documented minimal set (all 4 required entries are
  present, none missing). Evidence: `.gitignore:5,7,10,11,20` → `__pycache__/`, `*.egg-info/`, `\#*`, `.\#*`, `.env`
  (the required set at lines 2/6/14/17). Proposed fix: trim to the 4-entry minimal set, OR amend R-300 to explicitly
  sanction the extras (`.env` is referenced by the configs + test_regab.py, so it is likely intentional — the
  amendment is the sensible direction).
- **[R-310] minor** — 6 tracked src modules have no 1:1 test mirror (the rule states test/ mirrors src/ "one file to
  one file"); 1 extra integration test has no src counterpart. Evidence: `src/reversi/base_model.py`,
  `src/reversi/lm/hlp_analytics.py`, `hlp_final_log_print.py`, `hlp_validate.py`, `model_weights.py`, `wrk_save.py`
  (no matching test file); extra: `test/reversi/lm/test_lm_worker_full_chain.py`. Proposed fix: add the 6 mirror test
  files, OR record the intentional exception (the abstract base class + the full-chain integration coverage) in the
  rule / the overview. NOTE: the PRIMARY R-310 mandate (all .py under the allowed zones) passes cleanly — no stray
  .py at root/notes/docs; this finding is only the secondary mirror clause.
- **[R-590] info** — `python-dotenv` is declared in pyproject.toml (`pyproject.toml:18`) but imported nowhere in
  src/ — it is used only in test/ (`test/reversi/test_regab.py:82`). No undeclared third-party import exists: all 9
  src/ third-party modules (numpy, pydantic, numba, lz4, psycopg2, pandas, json5, scipy, matplotlib) are declared
  (matplotlib is a lazy in-function import in hlp_plot.py / opt_lbfgs.py). Proposed fix: none required; optionally
  annotate the declaration as test-only.

### Passed

R-300 (core: the 4 minimal entries present) · R-310 (core: every tracked .py under an allowed zone) · R-320 (the
minimal editable setuptools form, src layout) · R-350 (all tracked data files in the sanctioned homes:
latex/figures/*.png, test/reversi/data/ffo_12_log_sample.csv; no tracked .dat/.npy/.npz/.bin/.pdf) · R-360 a-e (all
198 config paths conform; ec20 0000-0177 fully sequential, no gaps/dups; the 20 single-model levels each carry
0108; all 21 index.md rigid and 1:1 with zero dangling links; all 198 base_dir relative; the name in the config
only, spot-checked on 4 configs) · the build/ mirror (gitignored; 5 sampled models carry the local mirror).

### Summary

Violations: 0 · Minor: 2 (R-300, R-310) · Info: 2 (R-590 dead declaration; R-600 not tree-verifiable). The models/
zone (R-360) is fully compliant across all five sub-checks; R-320 and R-350 are clean.

## Zone F — LaTeX book, probes, design principles (COMPLETE)

Checks performed: latex_rules G1/G5 (zone tracking: git ls-files latex/ + wsutils/) · G2 (the Makefile read in full,
NOT executed: all five documented targets present) · G3 (main.tex: documentclass, the 20 \include units, the
naming scheme, \includeonly, \part) · G4 (latex/.gitignore) · G6 (Italian, babel) · G8 (tex2txt.py, the spell /
pdf2png tools, wsutils/latex_lint.py interfaces; dict.txt 632 lines tracked) · R-595 (license_header_audit over all
21 tracked .tex: every header present and correct) · probe_rules + R-580 (all 24 probes: license audit, headers,
labeled check() calls, the retired class-c documentation, the hub-only pipeline-wide pins, no probe in scratch/,
build/tmp + atexit cleanup) · design_principles (DP-010 duality sampled on board/feature/mobility; DP-020 pydantic
on the schemas + hlp modules + state_machine; DP-030 njit inventory) · R-060 (the register list vs the tree vs the
overview Index).

### Findings

- **[R-060] minor** — the register's domain-rule-files list is out of sync with the tree: it references
  `notes/tools.md`, which does not exist (the real file is `notes/wsutils.md`), and it omits `notes/latex_rules.md`
  and `notes/design_principles.md` — even though latex_rules.md §7 (L84) explicitly claims the R-060
  one-domain-one-file pattern. Evidence: `notes/rules.md:54` "notes/probe\_rules.md, notes/tools.md (rigid; …)";
  `ls notes/` shows wsutils.md, no tools.md. Proposed fix: amend the R-060 line to list notes/wsutils.md (replacing
  notes/tools.md) and add notes/latex_rules.md + notes/design_principles.md (user approval per the register
  Governance).
- **[DP-010] minor (borderline)** — class-level batch compute APIs are array-only while the principle names
  `Position` as a vectorizable input: `Feature.compute_indexes(self, positions: PositionArray) -> IndexArray` and
  `MobilitySet.compute_indexes(...)` accept no scalar Position; the module-level primitives in the same modules ARE
  dual (`popcount64(b: Bitboard | BitboardArray) -> Index | IndexArray`). Evidence: `src/reversi/feature.py:272`,
  `src/reversi/mobility.py:203` vs `mobility.py:254` and `board.py:472`. Proposed fix: accept the array-only batch
  scope as a documented DP-010 scoping note, or record a "leave as-is" decision.
- **[probe_rules §2] minor** — two probe filenames do not follow `verify_<module>.py`: `verify_pattern_tests2.py`
  (named after the test file, with a legacy "tests2" suffix) and `verify_pidx.py` (an abbreviation, not a module
  name). Proposed fix: rename to verify_pattern.py / verify_principal_index.py (or record a leave-as-is decision).
- **[probe header convention] minor** — stale self-description: the header claims the file is gitignored, but it is
  tracked. Evidence: `probes/verify_zed.py:28-29` "scratch probe (gitignored) for the ZED level";
  `git ls-files probes/` lists verify_zed.py. Proposed fix: drop "(gitignored)" from the header.
- **[probe header convention] minor** — stale header prose (no live check affected; the level-count pin was deleted
  as class c and lives in the hub): "full 18-level chain" while the pipeline is 19 levels. Evidence:
  `probes/verify_save.py:35-37` vs the hub pin `probes/verify_logistic_model.py:184` "V3c 19 active levels".
  Proposed fix: re-word the header to "full chain (19 levels)".
- **[latex_rules G3] info** — the two-level file scheme (large chapters `\input` their sections) is currently
  unused: no chapter file `\input`s anything; the 86 KB appendix is a single flat file. Not a violation (the scheme
  is conditional); just observed.

### Passed

latex_rules G2 (the Makefile build door, all five targets) · G3 (documentclass{book}, the master main.tex, 20
\include chapters, the naming scheme with the legitimate gap inserts, \includeonly, \part) · G4 (all build
artifacts gitignored) · G6 (Italian book, babel) · G8 (tex2txt.py, spell + dict.txt, pdf2png, latex_lint.py all
where the rules say, interfaces matching) · R-595 (all 21 .tex headers correct; othelloboard.sty exempt) ·
probe_rules §2 (24 tracked probes at the root, one per module modulo the two naming findings; none in scratch/) ·
§3/§4 + R-580 (every probe header descriptive; every check() labeled; the retired class-c checks documented inline;
the R-580 vocabulary used as documented, e.g. verify_save.py:209 "(I-013 …)") · §5.3 (pipeline-wide state pinned by
the hub only) · DP-020 (sampled, consistent: pydantic schemas, 8 hlp modules, the state_machine standing case) ·
DP-030 (sampled, consistent: the njit(cache=True) hot kernels in board/pattern/random_game/mobility/prng) ·
R-060/overview Index (all three zone rule files listed with non-stale descriptions).

### Summary

Violations: 0 · Minor: 6 (R-060 register out of sync; DP-010 borderline; 2 probe filenames; 2 stale probe headers) ·
Info: 1 (the unused two-level latex file scheme). Top 3: (1) the R-060 register dangles a non-existent
notes/tools.md and omits two real rule files; (2) the DP-010 partial deviation on the sampled class-level batch
APIs; (3) the stale probe header descriptions — documentation drift only, no live check affected.

## Cross-zone summary

DRAFT (zones C and E complete; A, B, D, F final reports pending — the counts below are partial).

### Proposed interventions (aggregated, in suggested priority order)

1. **The six `__init__.py` mirror docs** (R-330/R-700 violation, zone C) — a USER DECISION is required first:
   (a) create the six small mirror docs (the docstring content is the natural body), or (b) legislate an explicit
   `__init__.py` exception in R-330 / docs_rules §7 (a rule amendment, user approval per the register Governance,
   with a D-entry). Whichever is chosen, the overview line-37 bullet ("every source and test file has its doc") is
   reworded or made true in the same commit.
2. **The test temp-dir re-anchoring** (R-750/R-760, zone D) — 6 test modules create UNANCHORED temp dirs (the
   system /tmp instead of build/tmp): test_wrk_anova, test_hlp_su_analysis, test_usage_binio, test_wrk_analytics
   (4 spots), test_wrk_final_log_print, test_wrk_su_analysis. Fix: adopt the R-760 idiom (CUSTOM_TMP_BASE via
   test.reversi.paths). A SOURCE change — on explicit user request only (iron rule 2).
3. **The docs batch re-wrap** (docs_rules, zone C) — one docs-only commit via the wsutils prose re-wrapper: 3
   unbalanced code spans (hard rule: hlp_final_log_print.md [9,10], wrk_design_matrix.md [24,25], opt_lbfgs.md
   [23,24]) + 58 over-120 lines across 27 docs + 3 ragged table rows. Independent of intervention 1.
4. **The test_index.md skeleton rewrite** (docs_rules §3/§6, zone C) — the only structurally non-conforming doc in
   98: rewrite to the test-doc skeleton (Coverage / Architecture / Goldens pinned / Open issues / Conventions /
   Integration), folding the unexpected "Notes" section into the right place.
5. **The 21 over-120 source lines** (R-520 VIOLATION, zone B) — wrap/split each line to ≤120: pattern.py (14
   lines — the table literals split across two lines per entry; the value pins are unaffected), hlp_config_
   schemas.py:324, wrk_optimize.py:159, hlp_zed.py:86, model_weights.py:161, wrk_vld_positions.py:94,
   verify_wmaps.py:207, run_utests.sh:52. A SOURCE change — on explicit user request only.
6. **The 8 I-XXX probe comments** (R-550 VIOLATION, zone B) — reword each of the 8 plain-`#` comments to drop
   the I-NNN id (name the change in words), keeping the R-580-allowed check labels untouched. The house's recorded
   interpretation (decisions_007.md:1046) confirms comments are in scope — so the fix is the rewording, NOT an
   R-550 amendment. A SOURCE change — on explicit user request only.
7. **The GPL-banner trailing space** (R-500 minor, zone B) — strip the one trailing space on the 24 `# ` banner
   lines in the 12 affected files (pure whitespace, zero behavior change; R-595 is unaffected).
8. **The R-560 backlog format passes** (zone B minor) — one `src_reflow.py --write` pass per file (8 files, the
   D-427 backlog) at each file's next scheduled campaign; the tool self-verifies before writing.
7. **The R-300 .gitignore amendment** (zone E, minor) — the 5 extra entries (`__pycache__/`, `*.egg-info/`, `\#*`,
   `.\#*`, `.env`) are intentional practice; amend R-300 to sanction them explicitly (user approval) rather than
   trimming the file (the `.env` ignore is load-bearing).
8. **The R-310 mirror clause** (zone E, minor) — record the intentional exception for the 6 src modules without a
   1:1 test mirror (the abstract base + the hlp/wrk modules covered by the full-chain integration test) in the
   rule / the overview, or add the 6 mirror test files.
9. **The closed-volume historical residue** (zone A, early signal) — the closed journal volumes log_000..003 are
   RED under the explicit lint (26 LISTMARK hits), the closed decisions volumes carry 11-space continuation
   indents, letter-suffixed D-156b/c/d entries exist, and D-number gaps are present (D-152 documented as a legal
   lost number). IRON RULE 3 forbids rewriting closed volumes, so the resolution is a DOCUMENTED historical
   exception in the matching rules files (the lint's closed-volume mode is already "on explicit request" per
   R-200) — a rules-amendment decision, the volumes stay byte-identical.
10. **The probe naming + header drift** (zone F) — rename `verify_pattern_tests2.py` → verify_pattern.py and
    `verify_pidx.py` → verify_principal_index.py (or record leave-as-is decisions); drop "(gitignored)" from
    verify_zed.py's header (it is tracked); re-word verify_save.py's "18-level chain" to "19 levels". A SOURCE
    change — on explicit user request only; documentation drift, no live check affected.
11. **The R-060 register re-sync** (zone F) — amend the R-060 line: replace the dangling notes/tools.md with
    notes/wsutils.md, and add notes/latex_rules.md + notes/design_principles.md to the list (a rule amendment,
    user approval per the register Governance).
12. **The DP-010 scoping note** (zone F, borderline) — document that the class-level batch compute APIs
    (Feature/MobilitySet.compute_indexes) are intentionally array-only, or record a "leave as-is" decision.
13. **The 19 over-long test docstrings** (R-570, direct check) — trim the 19 test docstrings that exceed the light
    1-2-line format (3 lines mostly, max 7) back to the light form. Low priority; a SOURCE change on explicit
    request.
14. **The record-integrity disclosure** (R-040 VIOLATION, zone A — the most important finding of the audit) —
    D-627 and D-463 are cited in the journals, the D-629 rotation entry and the overview Index, but absent from
    the closed volume 007 (D-627 was never written to the decisions log at session 127; D-463 is a historical
    gap). Fix: a new open-log decision entry DISCLOSING both gaps (the closed volume is append-frozen, iron rule
    3) + correct the overview Index range to "D-426…D-626" in the same commit (forward repair of the open file).
15. **The H1 factual corrections** (R-050 violation, zone A) — correct the three overstated closed-volume H1
    ranges (log_000 "1–24" → "1–23"; log_003 "38–89" → "38–78"; log_004 "90–101" → "90–97, 99–101" or the
    equivalent) — explicitly permitted by log_rules.md ("archived volumes are read-only EXCEPT factual
    corrections").
16. **The publication-material ruling** (R-130 + R-100 violations, zone A) — the post-rule DSH/vLLM/DeepSeek
    infra notes and the journal's own Italian prose sit in frozen volumes: disclose them in a decision entry,
    rule the forward practice (journal prose in English, user quotes exempt; the publication edit pass strips the
    infra notes when the notes become the GitHub material), and note the DEEPSEEK_API_KEY credential detail in
    log_000:447-449.
17. **The wsutils.md inventory row** (R-340/R-250 violation, zone A) — add the latex_lint.py row (category,
    purpose, write scope, ORIGIN D-number) to notes/wsutils.md §6 + the missing USAGE/SAFETY/ORIGIN sections in
    its docstring (a SOURCE change on explicit request for the docstring part).
18. **The register blank line** (R-020 minor, zone A) — insert the missing blank line before the "## Language &
    collaboration" heading (notes/rules.md:62).

### Severity counts (FINAL — all six zones + the four direct checks)

violation: 40 (A: 7 — D-627/D-463 record gaps, the 4 RED closed journal volumes, 13 phantom session numbers,
post-rule R-130 notes, R-100 Italian prose, the wsutils inventory gap; B: 29 — 21× R-520 over-120 lines, 8×
R-550 I-XXX probe comments; C: 3 — six missing `__init__` docs, the test_index.md skeleton break, 3 unbalanced
code spans; D: 1 — R-750 six modules writing to /tmp) · minor: 25 (A: 3, B: 9, C: 3, D: 1, E: 2, F: 6, R-570
direct: 1) · info: 15 (A: 5, B: 3, C: 1, D: 3, E: 2, F: 1). Rules passing clean: R-010, R-070, R-210, R-320,
R-350, R-360 (a-e), R-400, R-410, R-540, R-590, R-595, R-700 (orphan direction), R-770, R-780, R-790, R-800,
R-810, R-820, R-830, R-850/R-860 (sample), R-580, the latex_rules G2/G3/G4/G6/G8, the probe_rules tree
structure, DP-020/DP-030 (sampled).

### The three most important findings of the whole audit

1. **Record integrity (zone A, R-040)** — D-627 (the session-127 close) and D-463 are cited everywhere but exist
   in no decisions volume; the rotation's Index range overstates the closed volume. The fix is a disclosure
   entry + the Index correction — and it is partly the rotation's own footprint, disclosed here with full
   candor.
2. **The hard-ceiling source breaches (zone B)** — 21 lines over the 120-char R-520 ceiling (14 in pattern.py)
   and 8 I-XXX probe comments (R-550): 29 unambiguous, mechanically fixable violations in tracked sources.
3. **The mirror-doc gap (zone C, R-330/R-700)** — six `__init__.py` files without mirror docs, falsifying the
   overview's "every source and test file has its doc" claim: a user decision is needed (create the 6 docs vs
   legislate the exception), not a silent drift.
