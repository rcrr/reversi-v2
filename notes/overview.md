# overview.md — entry point

## Format rules (rigid — follow when editing this file)

The rigid format rules for this file live in notes/rules.md —
the "Roles of the notes files" section, the notes/overview.md
bullet. Consult it before editing.

## Project

This workspace is dedicated to the research and development of
evaluation functions for Reversi positions. The methods employed
focus on machine learning techniques that leverage solved
positions generated from random gameplay paths.

## Conventions in the code (respect them in any new work)

- Board vocabulary is canonical: **row** (1–8, top→bottom) and
  **column** (A–H, left→right) — never file/rank (chess). A1 =
  top-left (N-W) = bit 0; H8 = bottom-right (S-E) = bit 63.
  row_1 = [A1..H1]; column_a = [A1..A8]. Full text: notes/naming.md
  (D-013).
- Dual scalar/array API: public functions accept scalar OR 1-D array,
  return the input kind. Same validation pattern everywhere
  (is_scalar → atleast_1d → ndim check → dispatch → reshape back).
- `@validate_call` (pydantic, arbitrary_types_allowed) on all public
  functions.
- Numba `njit(cache=True)` + `prange` for hot loops; numba overloads
  for the four D8 primitives (fa1h8, fh1a8, fhori, fvert).
- Position = numpy structured dtype `[('mover', u64), ('opponent',
  u64)]`.
- Move codes: 0..63 = squares, 64 = PA (pass), 65 = NA, 66 = UN.
- D8 slot order is fixed and load-bearing (D-014): anti-transform
  slot s = T_s^{-1}; in pattern.py instance 0 = the ro000 image, and
  trans_fs/anti_trans_fs are indexed by instance (length =
  n_instances), not by slot.
- Pattern config indexes are base-3 uint32 over ≤ 18 squares
  (S ≤ 18); packed bit k ↔ the k-th square of `Pattern.squares`
  (ascending board order); principal index = min over the
  induced-stabilizer orbit.
- Test artifacts (D-065): unit tests write files ONLY under
  `workspace_root/build/tmp` and remove them afterwards (a
  `finally`/cleanup unlink, so a failing test leaves no garbage);
  no test writes anywhere else (notably: not the CWD). `build/` is
  gitignored.


## Environment

- Venv: `.venv/` (gitignored, D-010), Python 3.12.3, created
  2026-08-25.
- Packaging: `pyproject.toml` (setuptools, src layout) with the
  `reversi` package (name, D-133) installed editable in .venv
  (`pip install -e .`, D-011) — `import reversi` works without
  PYTHONPATH, resolving to src/.
- Dependencies (pyproject.toml, minimal set, kept in step with the
  modules brought in): numpy ≥ 2.0 (bitboards / structured dtypes;
  the code requires NumPy ≥ 2.0 — board.md R5), pydantic ≥ 2
  (@validate_call), numba ≥ 0.60 (njit / prange / overload; pulls
  llvmlite), lz4 (binio, D-051), psycopg2 / pandas / python-dotenv
  (regab, D-052). Installed in .venv: numpy 2.5.2, pydantic 2.13.4,
  numba 0.67.0, llvmlite 0.49.0.
- Test command: `./run_utests.sh` (the canonical runner, D-130:
  venv activation + the modules in canonical order; tiers:
  default fast ~5 s, LONG=1 ~45 s, VLONG=1 ~10 min incl. the
  A2050 chain and implies LONG; PERF=1 adds the print-only perf
  tests). The standard pre-commit run is LONG=1 ./run_utests.sh
  (D-129/D-131); VLONG=1 only when useful. A single module:
  `.venv/bin/python -m unittest reversi.test.<module>`. The
  DB-gated suites (test_regab + the worker suites) need a live
  PostgreSQL + .env + LONG=1, or
  `SKIP_REGAB_DB=1` to skip the 70 DB tests (2 mocked run). The
  runner is unittest by design (D-124): pytest is not a
  dependency (and not in the venv).
- Suite status (verified 2026-09-10, live DB, D-130 tiers,
  D-150): 771 tests / 0 failures. Default tier: 675 run in
  ~9 s / 96 skipped (76 DB-gated + 20 PERF print-only; the
  D-149 PLOT modules added the ~5 s of the synthetic renderings).
  LONG=1: 750 run in ~52 s / 21 skipped (20 PERF + 1 VLONG-gated
  A2050). VLONG=1: 751 run in ~2 min / 20 skipped (the A2050
  class alone: ~1 min, the seven 200k-point plots + the
  top-20 outlier report included).
  Gated run (SKIP_REGAB_DB=1): 96 skipped = 20 PERF + 76 DB
  (35 regab + 41 worker-level). Per-file suites: the Suite
  column of the Source files / Test files tables below.
- Probes: 22 tracked under probes/ (hub:
  verify_logistic_model.py owns the pipeline-wide state;
  measure_suite.py is the D-132 timing-measurement tool, no
  checks; rules: notes/probe_rules.md); 21/21 verify probes
  green in both gated and live modes (the D-149 sweep: the new
  verify_plot.py 16-check probe + the re-pinned
  verify_logistic_model V3c / verify_zed F1 / verify_save).

## Where we are
Current state only — the session-by-session history lives in the
journal volumes (notes/log_NNN.md) and the decision log
(notes/decisions.md); the D-pointers index that history. The
file-by-file state lives in the Source files / Test files tables
at the end of this file.

- The plan (confirmed by Roberto, 2026-08-28): port the ENTIRE
  pipeline — the original repo brought in module by module —
  with VERIFIED code and COMPLETE tests as the goal: a solid
  base before further evolution (his list of future changes is
  out of scope). DONE: all 15 pipeline levels active (15/15);
  the game-loop module is NOT in the plan (I-005 resolved).
- THE REORGANIZATION CAMPAIGN (I-001, D-133/D-134, 2026-09-08):
  CLOSED — twolm → reversi with the core/tools/lm split per
  Roberto's approved mapping: the 36 modules moved + renamed
  (2 commits each), twolm/ removed, editable reinstall, probes
  re-pinned, the Source/Test tables carry the reversi paths.
  Verification regime while the local DB was down (restored
  2026-09-08, D-135): SKIP_REGAB_DB=1 ./run_utests.sh per
  commit; post-restore the full LONG=1 suite + the 21/21 probe
  sweep are green.
- CACHE consistency (D-139, 2026-09-08): every cache file
  function now defaults to the LZ4 whole-file compression, as
  model_weights did (Roberto: "usiamola consistentemente"):
  the 10 store/load functions across hlp_indexes / hlp_wmaps /
  hlp_design_matrix / hlp_generate + the checkpoint pair + the
  2 regab rds functions. A2050 measured: 868.1 → 690.8 MB
  (79.58%, ~177 MB saved). Self-healing against legacy
  uncompressed files (the LZ4 guard at load → the
  delete+recompute paths). The CONFIG ad-hoc flow remains the
  only open cache oddity (D-078 R1, deferred — Next steps).
- BOARD (D-140, 2026-09-08): position_flips +
  position_make_move are now dual scalar/array, the same
  technique as legal_moves (D-111): the 2 prange kernels +
  the shared _kogge_stone_mm (njit inline); the former "PASS
  as a special case" note is resolved per-element in the
  kernel; array illegal moves keep the input position
  (Roberto's ruling). Board suite 221/0/14.
- VECTORIZED EF CLIENT (D-141, 2026-09-09):
  make_evaluation_function_array sits alongside
  make_evaluation_function — strict array (PositionArray ->
  (N,) float32), bit-exact per position vs the scalar EF
  (Roberto's rulings: strict array, the name, @validate_call
  on the scalar factory too, the dedicated no-DB test
  module, the A2030 batch pin). No new numba kernel
  (compute_indexes is already a batch API; the tail is
  element-wise NumPy); the closure setup is factored in
  _prepare_weights; the 1-D guard (D-111 M5) closes the
  2-D structured gap of the PositionArray validator. New
  no-DB module test_client.py (7 tests: the bit-exact
  1000-position parity on a synthetic rlm_04-mirror
  ModelWeights — iwmap [0,1,66,6627] = the production pin —
  the u64 coercion, the guards, the N=0 edge + the PERF 1M
  test, measured 5,640,701 b/s ≈ 1100× the scalar 5,117
  b/s); the A2030 batch pin (bit-exact on the same 6 pins
  over the full 199932-position set + vld[42]). Collateral:
  the runner insertion (D-130) + the verify_save A8 re-pin.
  Suite 707/0/21 (LONG, live DB).
- CONFIG CACHE REMOVED (D-142, 2026-09-09): the D-078 R1 /
  I-011 revisit — the trigger met (15/15), Roberto: "…la
  cache del LEVEL CONFIG, come e' fatta non va bene, non
  serve a nulla. Va ripensata" → ruling A+C1: the ad-hoc
  cache flow is GONE
  (write-only, ad-hoc duplicative, unconditional, parked in
  the ephemeral base_dir; the downstream invalidation chain
  is already config-aware without it — the file contributed
  nothing to correctness); the CONFIG level is now a pure
  load+validate step computing the fingerprint
  ctx.config_checksum (the sha3_256 of the normalized dump —
  the effective config, the base_dir override included); at
  SAVE the provenance travels with the model file — D-144:
  EMBEDDED in the v2 file (the D-142 sidecar record
  retired); the
  "Config SHA3-256" line in the common analytics header
  block (18 lines, both reports); the versioned-history
  option B is dropped (the JSON evolution stays in the
  file's VCS; stamping the downstream caches would
  duplicate the lineage on ephemeral artifacts). 8 probe
  re-pins (verify_wrk_config 29 → 15 checks); wrk_config
  15 → 13 tests; the 4 file-report goldens re-pinned.
  Suite 706/0/91 default + 706/0/21 LONG (live DB) + the
  20 verify-probe sweep green.
- DUPLICATE GAME POSITIONS (D-143, 2026-09-09): the
  post-extraction duplicate policy + the validation
  independence trace. Roberto: "…i record doppi ci sono, non
  sono pochi, e sono strutturali. Non altererei la query al
  db. Farei post una verifica in Python … la chiave e' mover,
  opponent" — the analysis measured the DB: every duplicate
  (mover, opponent) key appears exactly twice (one CMS + one
  CMR row, identical game_value/player — 0 conflicting
  groups), ~5.1–5.5% of every fixture set; the approved
  proposal's rulings: (1) `regab_allow_duplicate` top-level
  LMConfig flag, default True = keep = today's behaviour
  (zero golden impact), false = remove; both log the absolute
  count + the percentage; (2) post-extraction pandas
  `drop_duplicates(subset=['mover','opponent'], keep='first')`
  — hash-based O(n), order-preserving, NO sort (a global sort
  would reorder every row and perturb the goldens); "first" =
  lowest seq (the extraction is ORDER BY seq); the SQL
  untouched; (3) the dedup lives in the COMPUTE flow — the
  cache file stores the post-policy data set, so a flag flip
  changes the rds_checksum and cascades through the existing
  checksum lineage (no format change); (4) the VLD↔POSITIONS
  independence check is LOG ONLY, no action — Roberto:
  "calcoliamo l'overlap, e lo mettiamo come LOG. Nessuna
  azione di nessun tipo. Rimane scritto. … per ora teniamo
  traccia e basta" (no raise, no threshold parameter, no
  quality family); (5) the P6 sentinel (same key, different
  game_value) is NOT included — "la pipeline NON valida i
  dati … non aprirei il tema verifiche" (the keep-first
  behaviour is simply pinned). New: the 2 pure regab helpers
  (regab_dedup_mogv + regab_count_position_overlap, u64
  top-bit safe), wrk_positions.extract_and_prepare (the
  SHARED compute path, reused by VLD with the bid/status
  overrides) + the cache-hit duplicate line at both levels +
  the independence INFO trace at VLD. Tests +16: 11 no-DB
  micro (test_regab) + 3 DB (bid 8: 200/11/189, the post-
  policy cache content) + 2 DB (rlm_02 0% / rlm_00 100%
  overlap, traced not raised). 2 probe re-pins (wrk_positions
  A1 the __all__ 2→3; vld_positions A5/A7/A8 + D8 the reuse
  identity now includes extract_and_prepare).
  Suite 722/0/96 default + 722/0/21 LONG (live DB) + VLONG
  A2050 6/6 (the goldens INTACT — the default flag keeps
  today's behaviour byte-for-byte) + the 20 verify-probe
  sweep green.
- C2 (the D-142 parked follow-up, executed at
  Roberto's "Parti pure!") = D-144: the configuration
  provenance EMBEDDED in the model file — format v2
  (the config section LEADS the body: the checksum
  sentinel + the normalized dump, the v1 sections
  renumbered 2-9, the header prefix RGLM_BINARY_
  WEIGHTS untouched, the version 1 → 2) + the
  backward-compat reader (v1 loads with the config
  fields None; v2 recompute + raise on a checksum
  mismatch) + ModelWeights 10 → 12 fields (the
  trailing defaulted config_dump/config_checksum).
  The D-142 sidecar record is ELIMINATED (Roberto's
  ruling — the model file is the single source; the
  analytics "Config SHA3-256" report line untouched).
  The v2 file-level goldens retired by design: the
  embedded dump carries the run's base_dir → the bytes
  are legitimately run-specific (the 5 archived v1
  A2050 files are all exactly 515042 B; the raw v2
  content is 100% constant apart from the 8 random
  base_dir chars, which shift LZ4's match structure
  by a few bytes — the same content compresses to
  516459 or 516455) → the size literal becomes a band
  (A2030 22700-22800 B, A2050 516400-516500 B) + the
  determinism pins move to the same-base-dir byte
  identity + the read-back provenance (mw.config_dump
  == the live normalized dump, mw.config_checksum ==
  the ctx fingerprint). Tests 6 → 9 (+TestModelWeights
  V2 no-DB: v1 compat, v2 round-trip, the corruption
  sentinel; the D-142 record test converted to the
  single-source pin). verify_save A5/A6 re-pinned +
  A6b new (18 checks).
  Suite 725/0/96 default + 725/0/21 LONG + VLONG
  A2050 9/9 + the 20 verify-probe sweep green.
- I-013 O1 (the GRADIENT fg performance, executed at
   Roberto's "Procedi!") = D-145: the fg is THE
   bottleneck (96-99% of the A2050 OPTIMIZE time; the
   two M×P 384 MB temporaries per call) — the K3 numba
   block-parallel single-pass kernel (8 fixed row-
   blocks, private f64 buffers — race-free + run-
   deterministic; 46 ms/call vs 735 ms classic, 16.1×)
   now lives behind the high_performance_fg config flag
   (default false — the classic path kept verbatim,
   Roberto's ruling; rlm_03/rlm_04 opt in). The A2050
   re-baseline: OPTIMIZE 26.9 s (11.9×), chain 52.0 s
   (6.7×); the A2050 trajectory 356 iters / f
   1.4453826e-03 (Δrel 0.07% vs the classic); the two-
   loop is now the second cost center (≈ 8.2 s ≈ 30% —
   the O2 target). Full re-pin of the A2030/A2050
   goldens (position-based untouched). Suite 734/0
   (VLONG) + the re-pinned verify sweep. The analysis
   stays at notes/analyses/optimize_performance.md.
   O2 = D-146 (the two-loop, the second cost center): the
   numba variant was MEASURED 1.00-1.02x (NEGATIVE result —
   memory-bandwidth bound + the serial two-loop recurrence
   resists prange) and NOT adopted; O2b (Roberto's ruling) is
   in: the two-loop's per-op product temporaries (~58 MB
   allocated per call at A2050 scale) replaced by ONE
   pre-allocated f64 out= buffer — BIT-FOR-BIT the same math
   (no golden re-pin; the VLONG suite is green on the exact
   D-145 goldens) and 1.39x on the two-loop (23.2 -> 16.9 ms/
   call). The A2050 re-baseline: OPTIMIZE 22.8 s, chain 48.5 s.
   I-013 total: OPTIMIZE 321.3 s -> 22.8 s (14.1x), chain
   ~350 s -> 48.5 s (7.2x) — the fg + two-loop are now the
   measured optimum of this module family; I-013 closes as
   done after this campaign.
- CLIENT_CHECK (I-015, D-148, 2026-09-10): the 16th pipeline
  level — the saved-model file acceptance test after SAVE: the
  file is re-read, the client's array EF is built on the FILE
  weights, and the validation residuals are recomputed in Y
  space (Roberto's ruling: Y is the only cross-model comparable
  space — the future minimax PLY=6/PLY=8 EF comparisons will
  land on models with different ECs; the Z values are distorted
  per model). They must coincide with the in-memory VALIDATE
  residuals within client_check_tol (the new LMConfig field,
  default 1e-8, Roberto: "valore del config JSON. Pulito!"; his
  1e-8 for 1e-9: "non cadiamo dentro problemi di ordine delle
  somme"). A1a: the reference is recomputed from ctx (VALIDATE
  untouched); the chain is bit-identical by construction —
  measured max|diff| = 0.0 at every scale (synthetic 2000,
  A2030 20000, A2050 199932); the tolerance is a
  drift/corruption guard (the 1e-3 perturbation case measures
  1.959e-01 — ~10^7 above). Suite 744/0 (VLONG, live DB) + the
  20/20 probe sweep green.
- D-149 (2026-09-10): PLOT — the 17th and LAST level, the
  matplotlib diagnostics after CLIENT_CHECK (I-016; Roberto
  "PLOT = livello 17 (dopo CLIENT_CHECK): OK" — the gate first,
  the figures are drawn for a verified model file). Seven
  figures in Y space: the three R classics (the three-line
  residual density — Reference/Training/Validation with the
  sd/mean/min/max margin labels + the training-mean vline; the
  residual-vs-fitted cloud; the residual-vs-game-value cloud
  with the 0.7-range "cloud" jitter — ported from the [0,1]
  target space to the [-64, +64] scale, the D-148
  comparability ruling) + the four extensions (the per-EGV box
  plot, the per-EGV mean-residual error bars, the parity plot,
  the normal QQ plot — Roberto "falli tutti sono molto
  curioso!"). Pilot: the PlotConfig sub-section (the
  AnalyticsConfig pattern) — the enable master switch, the
  format "png"|"pdf"|"pdf,png" (PNG-DEFAULT, Roberto's
  correction), dpi, the dir_name (absolute as-is / relative
  under base_dir, default "plots"), and the plot-name
  WHITELIST (a listed name is generated, an unlisted one is
  skipped, an empty list is a no-op, enable=false does nothing
  even with names — Roberto "se i nomi ci sono ma enable è
  falso ... non fa nulla"). The seeded jitter (42) + the 100k
  seeded KDE subsample (43) replace the R unseeded jitter —
  the figures are reproducible and the Agg PNG output is
  byte-deterministic (the parity rendering golden). No cache
  file (the 8th non-cache deviation, the rlmwf_16 slot),
  stateless down, the D-060 failure semantics, the matplotlib
  lazy import (the schema imports PLOT_NAMES on every run).
  rlm_03/rlm_04 gain the plot section (all seven names): the
  chains exercise the generation end-to-end (A2050 VLONG: 7
  PNGs 68-429 KB in 58.8 s). Suite 768/0 (VLONG, live DB) +
  the 21/21 probe sweep green. Re-pins: the full-chain
  15/CLIENT_CHECK → 16/PLOT + the plot log/file pins; BOTH
  size bands re-centered (the D-147 procedure — the plot
  section in the embedded dump): A2030 22940-23040 (measured
  22990/22994), A2050 516500-516700 (measured 516551); the
  hub V3c 16 → 17; verify_zed F1 L135-138; the verify_save
  header + band comments.
- D-150 (2026-09-10): the PLOT styling v2 — Roberto looked at
  the seven A2050 figures and ruled: the FIXED axes (the
  game-value axes always [-64, +64] regardless of the data — the
  box plot both axes, the two clouds' x; the density ALWAYS
  centered on zero on the [-72, +72] window, "in teoria ±128,
  chi sbaglia di più di 100 ha un modello tanto sbagliato"; the
  QQ y on [-64, +64]), the step-8 tick labels ("0, 8, 16, ..."),
  the two-line title (the name BOLD, the description ITALIC
  smaller, spaced), the Reference label moved up (it overlapped
  its line). His verdict on the new diagnostics: the
  mean-residual-by-EGV "questo grafico è stupendo ... ci dice
  che la sigmoid introduce una distorsione ... che si vede !!!"
  and the QQ "bellissimo, come sopra la distorsione si vede".
  New: the top-20 extreme-outlier report in the PLOT log (the
  position's bitboards included — "uno spunto capire come mai il
  modello sbarella cosi"). The resid_vs_gv "swapped labels":
  they were NOT swapped — the 0.7 jitter smear (±44.8) stretched
  the data-driven x axis to ±108; the pinned domain fixes it.
  Suite 768 → 771, the parity golden re-pinned, no config
  change (log-only report, the size bands stand). D-151
  followed the same day (Roberto's look at the restyled
  figure): the mean-by-EGV y axis now hugs the ACTUAL data
  (the |mean|+sd extent, symmetric, rounded up to the step-8
  grid — "se il valore è nel range -16,+16 teniamolo in questo
  range"), the tick labels drop to fontsize 8, the x axis
  untouched ("perfetto").
- D-153 (2026-09-11): the boxplot stale-label bug (boxplot
  leaves the 62 categorical bin labels, the positions-only
  set_xticks printed the first 17 under the step-8 positions —
  fixed with explicit labels; the data was always correct, found
  by Roberto). D-154: the notes are the Reversi portfolio only
  (no harness/vLLM infrastructure entries — the GitHub
  publication target). D-155: the PLOT label standardization
  ("Evaluated game value" everywhere — the two "Fitted" titles
  renamed; the bare "(Y)" removed; the binned axes carry the
  italic "(binned every 2)" note at the axis font size, the
  ruling's accepted fallback — this matplotlib has no mathtext
  size commands), the density Training label moved to ~x = +25
  (clearing the peak it covered), and the A2050 config writes
  PNG + PDF (the preserved run: 7 of each) — the PLOT campaign
  closes here (D-149 → D-155): Roberto's final verdict "I
  grafici vanno ora tutti bene. Lavoro grafici: finito."
- FEATURE ANALYSIS (I-017, D-156 + D-156b + D-156c, all
   2026-09-11): the project document
   notes/analytical_properties_of_features.md (CONFIRMED v2,
   D-156d T0c close — the plan locked; ODP-9 the lookup table
   adopted, ODP-10 the C source delivered in scratch). Design v2 (Roberto's redesign,
   confirmed): the pipeline REORDERING (FEATURES before
   POSITIONS — realizes his parked I-012) + the new
   FEATURE_ANALYSIS level (step 3): the SYNTHETIC random-play
   corpus — seeded with the PORTED MT19937 PRNG (Roberto's C
   library, the Matsumoto/Nishimura Mersenne Twister — the
   bit-exact C comparison is the hard verification gate), the
   games ARRESTED at the model's ec (the same window as the DB —
   "mele con mele"), the configuration-frequency accumulation
   (CACHED, the first feature-set-keyed cache, the corpus
   default 1e7) — + the SU statistics on the ideal frequencies
   (the instance×instance matrices over the EXPLICIT su_pairs)
   + the never-observed audit (the stop-and-inspect before
   training) + the new EFFECT_SIZE level (step 6, before
   OPTIMIZE): the eta²/omega² per feature + the adherence of
   the DB set to the ideal same-window population (chi-square
   + KL + TV) + the JSON target_level parameter (default
   "last"). The (feature, instance) sub-variable is the
   analysis unit (the design-matrix unit). Tasks T1..T19 (the
   granular split), one per session. T1 DONE (D-157,
   2026-09-11): the reordering is in (FEATURES step 2 /
   POSITIONS step 3, the rlmwf_03 slot, I-012 realized; the
   test_wrk_features suite now DB-free) — 771/0/94 + VLONG
   771/0/20 + the 22-probe sweep green; D-158 the parity
   golden re-pin (the env drift). T2 DONE (D-159): the 64-bit
   MT-19937 ported line-by-line from Roberto's C (the
   strict-typing ruling: NUMPY, the np.uint64 data path) —
   bit-exact vs the C build, 781/0/94 + LONG 781/0/21). T3 DONE
   (D-161): the C-oracle golden suite (the committed 13003-line
   golden, 20/0 tests) — 791/0/94 + LONG 791/0/21. T4 DONE
   (D-162): the single-game random play (the ODP-9 pick table,
   the no-PRNG pick, the ec arrest, the 12/0 micro-suite) —
   803/0/94 + LONG 803/0/21. The ODP-9 equivalence document
   (D-163) passed the first peer review (DeepSeek V4 Pro) and
   is revised to v2 (D-164: the oracle Theorem 1, the corpus-
   level claims reclassified to the T6 gate, the gate
   extended); the SECOND, INDEPENDENT peer review (Kimi K3,
   D-165) is in — verdict PASS WITH REQUIRED AMENDMENTS: the
   design and the v2 scope discipline are confirmed, but three
   gate-design amendments are required before the T5 build
   (the per-stratum marginal comparison + the sampling unit,
   the focused tests 4-5 as the primary joint gate, the
   absolute-bias bound against the 1e7 noise floor with
   family-wise error control and a stated power) — the v3
   document is DONE (D-166: all three amendments folded into
   the T6 gate — the 1e6 scale, the absolute delta* = 2e-3
   bound, the focused TV/KL primary tests, the sampling-unit
   pin, the family-wise control; v3.1 D-167) and the
   document reached v4 FINAL after the THIRD review (GLM
   5.3, D-168: the v3.1 D0 noise formula was wrong — the
   table-aware cap delta*_unit, the phase term demoted to
   GATED + the new phase-occupancy scan, the corrected
   certification schedule 1e6 + 1e7 build gate) — FROZEN.
   T4 FIX (D-169, Roberto's OK): the non-full double pass
   now stops the game (the pre-fix loop spun passes to the
   MAX_PLIES guard on the rare deadlock — < 0.2% of games)
   — 13/0. T5 DONE (D-170): the concurrent wave engine —
   Roberto's option A refined, the LOCKSTEP (step = one
   real move, the pass folded into the step, the double-
   pass discard, the boundary harvest + respawn) — 11/0/1,
   the harvest bit-exact vs the T4 (LAW-1/2, the pinned
   pass-carrying slot 712), the 1e6 benchmark 5.3 s
   (188k games/s; the 1e7 extrapolation ~50 s). Open
   finding RULED (D-171, Roberto): documented as the
   caller's responsibility (the docstrings + the board.md
   mirror; the kernel untouched, the 2-line fix stays
   available). T6 GATE BUILT (D-172): hlp_gate.py (the
   v4 tests 1-6 — the phase scan, the per-ec + pooled
   marginals, the focused joints on the 18 sampled SU
   pairs, the demoted chi-square, the phase continuity — +
   the 20 D0 G0-vs-G0 pairs @ 1e5, the parametric q95
   criterion; suite 14/0/0) — the 1e6 design gate
   VERDICT FAIL (D-173): the E1-corpus finding (the LMC
   marginal 47x the G0-G0 noise, the phase scan p ~= 0,
   the phase-locked corpus, seed-independent; the
   path-coupling signature — the doc section 6.4) — G0
   APPROVED as the corpus generator (D-174, Roberto's
   design call): the engine in hlp_wave (14/0/2); the
   doc addendum section 11 FINALIZED (D-175 + the GLM
   Round-2 audit — the FAIL is the design's, "it died of
   evidence"; the corrections A-G folded in); the 1e7
   corpus build ACCEPTED (D-176: in memory, NO file —
   35.3 s = 282,911 games/s, integrity + determinism +
   D0-scale spot check OK).

- Sources live in the `reversi` package under src/ (D-008;
  D-133: core top-level + tools/ + lm/ subpackages); unit tests
  in src/reversi/test/. Environment: .venv with the pinned deps
  (D-010/D-051/D-052), reversi installed editable (D-011, D-133).
  Git repo on master (D-003). Collaboration memory: AGENTS.md
  (constitution) + notes/rules.md (active rules) + this file
  (state) + notes/ (the log: decisions.md the open decision log
  + journal volumes, format rules in log_rules.md) +
  notes/performance_baseline.md (the wave-tier
  OPTIMIZATION-phase reference, D-175/D-176).

## Next steps

- Feed notes/ideas.md with Roberto's future-evolution ideas.
- C2 (the D-142 parked follow-up): DONE (D-144) — the
  config dump is now INSIDE the model file (v2, the
  backward-compat v1 reader, the D-142 record retired);
  the model is fully self-describing.
- I-013 the GRADIENT fg performance study: DONE — O1 (D-145,
  2026-09-09) + O2 (D-146, 2026-09-09; notes/
  analyses/optimize_performance.md kept as the pipeline
  documentation reference). O1: the fg was THE bottleneck
  (96-99% of the A2050 OPTIMIZE time; the two M×P 384 MB
  temporaries per call the waste); the K3 numba block-parallel
  single-pass kernel (8 fixed row-blocks, private f64 buffers —
  race-free + run-deterministic, numba 0.67 has no CPU atomics)
  is behind the high_performance_fg config flag (default false;
  the classic path kept verbatim per Roberto; rlm_03/rlm_04 opt
  in) — OPTIMIZE 321.3 -> 26.9 s (11.9×), chain ~350 -> 52.0 s
  (6.7×); the A2050 trajectory 356 iters / f 1.4453826e-03
  (Δrel 0.07% vs the classic, same CONVERGED_MIN_GRAD). O2: the
  numba two-loop MEASURED 1.00-1.02× (negative result — memory-
  bandwidth bound + the serial recurrence resists prange), NOT
  adopted; O2b in: the two-loop's 2m per-op product temporaries
  (~58 MB/call) replaced by ONE pre-allocated f64 out= buffer —
  bit-for-bit the same math (no golden re-pin) at 1.39× —
  OPTIMIZE -> 22.8 s, chain -> 48.5 s. I-013 TOTAL: OPTIMIZE
  321.3 s -> 22.8 s (14.1×), chain ~350 s -> 48.5 s (7.2×);
  suite 735/0 (VLONG), 20/20 probes. O3 (pure-numpy 1.2×)
  considered, not chosen; O4 closed (m=93 is load-bearing —
  m=20/10 do not converge in 500 iters and are slower).
- Next on the backlog (Roberto's call): I-003 the named move
  constants, I-009/I-010 (notes/ideas.md); I-012 is DONE
  (D-157, the I-017 T1).
- FEATURE ANALYSIS (I-017): T1 DONE (D-157), T2 DONE (D-159:
  the PRNG port — the strict-typing ruling, the C cross-check),
  T3 DONE (D-161: the C-oracle golden suite — the committed
  13003-line golden, test_prng.py 20/0), T4 DONE (D-162: the
  single-game random play — the ODP-9 table, the no-PRNG pick,
  the ec arrest, the 12/0 micro-suite) — the ODP-9
  equivalence document (D-163) passed the first peer review
  (DeepSeek V4 Pro) and is revised to v2 (D-164: the oracle
  Theorem 1, the corpus-level claims reclassified to the T6
  gate, the gate extended with the same-width/small-k/phase
  tests); the SECOND, INDEPENDENT peer review (Kimi K3, D-165)
  is DONE — verdict PASS WITH REQUIRED AMENDMENTS (the design
  and the v2 scope discipline confirmed; three gate-design
  amendments required before the T5 build: (A1) the per-stratum
  marginal comparison + the pinned sampling unit, (A2) the
  focused tests 4-5 as the primary joint gate, (A3) the
  absolute-bias bound against the 1e7 noise floor with
  family-wise error control and a stated power) — v3 is DONE
  (D-166: all three amendments folded into the T6 gate — the
  1e6 scale, the absolute delta* = 2e-3 bound, the focused
  TV/KL primary tests, the sampling-unit pin; v3.1 D-167,
  then v4 FINAL with the THIRD review — GLM 5.3, D-168: the
  v3.1 D0 formula was wrong (36x understated), the table-
  aware cap + the phase term demoted to GATED + the
  corrected certification schedule — the document is
  FROZEN) — T4 FIX (D-169: the non-full double pass now
  stops the game — Roberto's OK) + T5 DONE (D-170): the
  concurrent wave engine (Roberto's option A refined — the
  LOCKSTEP: step = one real move per live lane, the pass
  folded into the step, the double-pass lanes coast on the
  PA swap, the boundary harvest + respawn; the harvest is
  bit-exact vs the T4 reference — LAW-1/2; the 1e6
  benchmark 5.3 s, 188k games/s, target <= 120 s), per the
  plan in notes/analytical_properties_of_features.md §8 —
  the board.py make_move legality finding (the occupied
  square with a flipping ray is applied; the wave routes
  around it via the PA swap) is RULED (D-171: documented
  as the caller's responsibility, the kernel untouched —
  Roberto's ruling). T6 GATE BUILT (D-172): hlp_gate.py
  (the v4 tests 1-6 + the 20 D0 G0-vs-G0 pairs @ 1e5, the
  parametric q95 criterion, suite 14/0/0) — the 1e6
  design gate VERDICT FAIL (D-173: the E1-corpus finding
  — the LMC marginal 47x the G0-G0 noise, the phase scan
  p ~= 0, the phase-locked corpus, seed-independent at
  1e5 (0.174/0.206), the deviation concentrated early
  (ec 52-57) — the path-coupling signature) — G0
  APPROVED as the corpus generator (D-174, Roberto's
  design call after the D-173 verdict): the engine in
  hlp_wave (14/0/2; as fast as G1 in the wave tier,
  identical reproducibility) — next: the 1e7 corpus
  build (rlm_03, ec 20, the arrested-positions sink) +
  the light build check (G0 is the reference by
  construction — the doc's 1e7 build gate loses its
  object), then the I-017 statistics; ODP-9 stays the
  analytical record. PERFORMANCE (D-175, measured; the
  reference: notes/performance_baseline.md): G0 ec=0
  (the full game) = 189,571 games/s (1e7 in 52.8 s; 1e9
  ~= 9 min); G0 ec=20 steady = 277,470 games/s (1e7 in
  36.0 s) — ~11M moves/s. The doc addendum section 11
  FINALIZED per the GLM Round-2 audit (the FAIL is the
  design's, D-174 endorsed without reservation — "it
  died of evidence"; the corrections A-G folded in: the
  sparsity-saturated units, the class-collision cloning
  mechanism, the fallback disposition, the errata).
  The 1e7 build: ACCEPTED (in memory, NO file — D-176
  the build/ guideline now in rules.md): 35.3 s =
  282,911 games/s, integrity + determinism + D0-scale
  spot check OK. T7 LANDED (D-177): the marginal frequency
  accumulator (the per-(feature, instance) column code ->
  count, the dense-bincount / unique-merge split, POOLED over
  the single-ec corpus — the FEATURE_ANALYSIS phase-1 data
  plane) + the ec pin (ec_of = 64 - popcount(mover|opponent)
  = the DB's empty_count — the "mele con mele" window).
  T8 LANDED (D-178): the joint accumulator (the per-requested-
  pair instance×instance (code_i, code_j) -> count, the unique-
  merge, the packed-u64 key, the same-feature diagonal the
  SU = 1 lock) + the 2M early-value probe RAN (the P2 audit
  core: the coverage ~0.22-0.58, the LMC 21/65, the 42-78%
  never-observed at 2M). NEXT: T9 (the PRNG integration test)
  — the SU analysis OPTIONAL, default FALSE; the profiling
  session (the OPTIMIZE pattern, the
  step-by-step walkthrough + the code reviewed together
  — Roberto's commitment) AFTER the SU level is
  complete. I-018 (the outlier report in VALIDATE) is
  parked, Roberto's call.




## Source files
One row per source file, alphabetical (the package path sorts future
packages first). State = a status word + the open/parked items (if any)
+ the D-pointer range; the campaign history lives in the decision log.
Suite = the current verified suite (live DB, D-130 tiers,
2026-09-08) of the file's test module.

| File | State | Suite (live DB) | Doc |
| --- | --- | --- | --- |
| src/reversi/base_model.py | complete: thin facade base over StateMachine (pure delegation); closed (D-074/D-075) | 17/0/0 (via test_logistic_model) | docs/src/reversi/base_model.md |
| src/reversi/board.py | complete: the Reversi game kernel (200 random full games verified on the public API); all issues closed — R1–R5 (D-017 era) + M1–M7 (D-111); flips/make_move vectorized (D-140); I-005: no game-loop module | 221/0/14 | docs/src/reversi/board.md |
| src/reversi/tools/binio.py | complete: binary IO layer — T1–T4 batch (D-051); empty-suffix fix (D-095) | 48/0/0 (45 + 3 usage) | docs/src/reversi/tools/binio.md |
| src/reversi/tools/cache_manager.py | complete: generic load-or-compute cache pipeline (.SHA3-256 sidecar, 8192-chunk verify); closed (D-071/D-072) | 22/0/0 | docs/src/reversi/tools/cache_manager.md |
| src/reversi/feature.py | complete: Feature / FeatureSet (blocked __new__, 3 factories, composition, sorted order); closed (D-038..D-042); the OPEN R1 (unused BeforeValidator import) fixed at D-110 | 20/0/1 | docs/src/reversi/feature.md |
| src/reversi/tools/prng.py | complete: the MT-19937 64-bit PRNG port (the I-017 T2, D-159) — line-by-line from Roberto's C (the strict-typing ruling: np.uint64 the data path); the bit-exact cross-check vs the C build; the smoke micro-suite (the T3 golden suite pending); D-160: the rename from the feature_prng core name (the generic library in tools/) | 10/0/0 | docs/src/reversi/tools/prng.md |
| src/reversi/lm/wrk_analytics.py | complete: the ANALYTICS 14th level — training metrics + console / file reports (the 3-metric header + dense metrics, D-105/M2); closed (D-103) | 4/0/0 | docs/src/reversi/lm/wrk_analytics.md |
| src/reversi/lm/wrk_client_check.py | complete: the CLIENT_CHECK 16th level (PLOT follows as the 17th — D-149) — the saved-model file acceptance test (D-148: the file re-read + the client's array EF + the Y-space residual comparison vs the in-memory VALIDATE forward pass, tolerance = cfg.client_check_tol) | 6/0/0 | docs/src/reversi/lm/wrk_client_check.md |
| src/reversi/lm/hlp_plot.py | complete: the PLOT figure builders (D-149; D-150: the fixed axes — game-value axes always [-64,+64], the density centered [-72,+72], the step-8 ticks — + the two-line bold/italic title + the _sym_limit helper) — the seven Y-space diagnostics (the three R classics + the four extensions), the PlotData + collect_plot_data (the training w_dense pass + the validation forward pass), the R-semantic jitter, the EGV bins, the guarded KDE; matplotlib/scipy lazy-imported (the schema imports PLOT_NAMES on every run) | 11/0/0 | docs/src/reversi/lm/hlp_plot.md |
| src/reversi/lm/wrk_plot.py | complete: the PLOT 17th and LAST level (step 16, after CLIENT_CHECK; D-149) — the whitelist pilot (enable + the optional plot names), the directory resolution (absolute as-is / relative under base_dir), the per-name save in every configured format; D-150: the top-20 extreme-outlier report (the position's bitboards, the stable argsort); no cache (the 8th non-cache deviation, the rlmwf_16 slot), stateless down, D-060 failure | 10/0/0 | docs/src/reversi/lm/wrk_plot.md |
| src/reversi/lm/wrk_config.py | complete: the CONFIG worker — a pure load+validate step (JSON5 → config → base_dir validation) + the config fingerprint (D-142: the ad-hoc cache flow removed, the record is a SAVE artifact); closed (D-077/D-078/D-142; I-011 realized) | 13/0/0 | docs/src/reversi/lm/wrk_config.md |
| src/reversi/lm/wrk_design_matrix.py | complete: the DESIGN_MTR 7th-level worker; closed (D-090) | 3/0/0 | docs/src/reversi/lm/wrk_design_matrix.md |
| src/reversi/lm/wrk_features.py | complete: the FEATURES worker — the 3rd active level (step 2, before POSITIONS — D-157); the first pure-compute level (no cache file ever); closed (D-081/D-082) | 3/0/0 (DB-free, D-157) | docs/src/reversi/lm/wrk_features.md |
| src/reversi/lm/wrk_generate.py | complete: the GENERATE 11th level (dense weights materialization; the R1 for-next-level trap fix); closed (D-097/D-098) | 3/0/0 | docs/src/reversi/lm/wrk_generate.md |
| src/reversi/lm/wrk_gradient.py | complete: the GRADIENT 9th level (the second non-cache; the float32 contract, D-094 R1; D-145: the high_performance_fg flag wiring); closed (D-093/D-094/D-145) | 4/0/0 | docs/src/reversi/lm/wrk_gradient.md |
| src/reversi/lm/wrk_indexes.py | complete: the INDEXES worker (uniform 7-kwargs cache wiring); closed (D-083/D-084) | 2/0/0 | docs/src/reversi/lm/wrk_indexes.md |
| src/reversi/lm/wrk_optimize.py | complete: the OPTIMIZE 10th level — the only level whose "cache" is a plain checkpoint dict via binio; closed (D-096) | 3/0/0 | docs/src/reversi/lm/wrk_optimize.md |
| src/reversi/lm/wrk_positions.py | complete: the POSITIONS worker — the first cache_manager consumer over the regab data set (D-079/D-080); the D-143 extract_and_prepare shared compute path (the duplicate policy) + the cache-hit duplicate line; D-157: step 3, slot rlmwf_03 (the reordering) | 12/0/0 | docs/src/reversi/lm/wrk_positions.md |
| src/reversi/lm/wrk_save.py | complete: the SAVE 15th level (step 14; CLIENT_CHECK runs after it, D-148); D-144: the SINGLE artifact — the v2 model file embeds the config provenance (the D-142 sidecar record retired) | 9/0/1 (via test_lm_worker_full_chain) | docs/src/reversi/lm/wrk_save.md |
| src/reversi/lm/wrk_validate.py | complete: the VALIDATE 13th level (the third non-cache worker); closed (D-101/D-102) | 5/0/0 | docs/src/reversi/lm/wrk_validate.md |
| src/reversi/lm/wrk_vld_positions.py | complete: the VLD_POSITIONS 12th level (the POSITIONS twin over the validation set, D-099/D-100); the D-143 shared extract_and_prepare reuse + the LOG-ONLY independence trace | 11/0/0 | docs/src/reversi/lm/wrk_vld_positions.md |
| src/reversi/lm/wrk_wmaps.py | complete: the WMAPS 6th-level worker; closed (D-086/D-087/D-088) | 3/0/0 | docs/src/reversi/lm/wrk_wmaps.md |
| src/reversi/lm/wrk_zed.py | complete: the ZED 8th level (the first non-cache level); closed (D-091/D-092) | 3/0/0 | docs/src/reversi/lm/wrk_zed.md |
| src/reversi/lm/logistic_model.py | complete: the LM facade — LMContext blackboard (40 fields, 8 *_checksum, 3 injected callables) + the 16-level worker list, activated line by line (D-076..D-104; D-148: CLIENT_CHECK the 16th level); the stale "Remove comments" line dropped (D-113); D-157: the worker list reordering (FEATURES before POSITIONS) | 17/0/0 | docs/src/reversi/lm/logistic_model.md |
| src/reversi/mobility.py | complete: mobility / MobilitySet + popcount64 SWAR kernel; closed (D-035/D-036); disposition per D-036 (PERF tests print-only, no perf gate) | 26/0/1 | docs/src/reversi/mobility.md |
| src/reversi/lm/model_weights.py | complete: the model_weights @dataclass (D-104); D-144: the v2 format (the config provenance leads the body) + the backward-compat v1 reader + the 12-field dataclass | 9/0/1 (via test_lm_worker_full_chain) | docs/src/reversi/lm/model_weights.md |
| src/reversi/tools/opt_lbfgs.py | complete: the LBFGS solver — T1–T7 batch incl. the RuntimeException hard-bug fix (D-053); D-146: the two-loop O2b (the pre-allocated f64 out= product buffer, bit-identical, 1.39×; the numba two-loop measured 1.00-1.02× and not adopted) | 14/0/0 | docs/src/reversi/tools/opt_lbfgs.md |
| src/reversi/pattern.py | complete: principal mask = numerically lowest orbit (D-020); minor sweep 19/19 (D-023/024/025); Burnside attributes (D-032); PatternSet.__repr__ (D-112); the PatternSet Raises docstring fixed — @validate_call raises ValidationError, not TypeError (D-121) | 65/0/3 | docs/src/reversi/pattern.md |
| src/reversi/regab.py | complete: the PostgreSQL regab access layer — T1–T7 batch (D-052); the LZ4 default in the 2 rds file functions (D-139); the D-143 pure helpers regab_dedup_mogv + regab_count_position_overlap | 48/0/0 | docs/src/reversi/regab.md |
| src/reversi/lm/hlp_analytics.py | complete: the ANALYTICS data module (the 3-metric header + Population baseline + dense metrics, D-105/M2; the D-142 Config SHA3-256 line in the common header block — 18 lines, both reports); closed (D-103) | 4/0/0 | docs/src/reversi/lm/hlp_analytics.md |
| src/reversi/lm/client.py | complete: the inference client — the scalar EF + the vectorized make_evaluation_function_array (D-141: strict array, bit-exact per position, @validate_call on both factories); D-148: the in-pipeline consumer (the CLIENT_CHECK level) | 6/0/1 (test_client) + the EF pins via test_lm_worker_full_chain | docs/src/reversi/lm/client.md |
| src/reversi/lm/hlp_config_schemas.py | complete: the pydantic config domain (the LMConfig JSON5 entry point; D-079/D-080); the D-143 regab_allow_duplicate field (default True); the D-145 high_performance_fg flag (default False); the D-148 client_check_tol field (default 1e-8, gt=0); the D-149 PlotConfig section (the PLOT pilot: enable, the format png-default + pair, dpi, the dir_name, the plot-name whitelist with the fail-fast + dedupe validators) | 23/0/0 | docs/src/reversi/lm/hlp_config_schemas.md |
| src/reversi/lm/hlp_design_matrix.py | complete: the DESIGN_MTR data module (7th level); closed (D-090); the LZ4 default (D-139) | 14/0/0 | docs/src/reversi/lm/hlp_design_matrix.md |
| src/reversi/lm/hlp_generate.py | complete: the GENERATE data module (11th level); closed (D-097/D-098); the LZ4 default (D-139) | 16/0/0 | docs/src/reversi/lm/hlp_generate.md |
| src/reversi/lm/hlp_gradient.py | complete: the GRADIENT data module (9th level; the float32 contract; D-145: the dual fg — classic verbatim + the K3 numba kernel behind the high_performance flag); closed (D-093/D-094/D-145) | 14/0/0 | docs/src/reversi/lm/hlp_gradient.md |
| src/reversi/lm/hlp_indexes.py | complete: the INDEXES data module; closed (D-083/D-084); the LZ4 default (D-139) | 14/0/0 | docs/src/reversi/lm/hlp_indexes.md |
| src/reversi/lm/hlp_optimize.py | complete: the OPTIMIZE data module (10th level); closed (D-096); the LZ4 default (D-139) | 20/0/0 | docs/src/reversi/lm/hlp_optimize.md |
| src/reversi/lm/hlp_random_play.py | complete: the single-game random play generator (the I-017 T4, D-162; the D-169 non-full double-pass fix) + the marginal frequency accumulator (the I-017 T7, D-177: the per-(feature, instance) column code -> count, the dense-bincount / unique-merge split, POOLED over the single-ec corpus) + the joint frequency accumulator (the I-017 T8, D-178: the per-requested-pair instance×instance (code_i, code_j) -> count, the unique-merge, the packed-u64 key, the same-feature diagonal the SU = 1 lock) — the FEATURE_ANALYSIS phase-1 data plane (the worker lands in T16); the ODP-9 permutation lookup table (2016 MT19937 draws, lru_cached read-only) + the no-PRNG pick + the ec arrest (PINNED D-177: 64 - popcount(mover|opponent) = the DB's empty_count, the "mele con mele" window) + the pass + the game over + the full trajectory | 21/0/0 (via test_hlp_random_play) | docs/src/reversi/lm/hlp_random_play.md |
| src/reversi/lm/hlp_wave.py | complete: the concurrent WAVE generator (the I-017 T5, D-170 + the D-174 G0 engine — the G1 ODP-9 engine (W lanes in LOCKSTEP, the pass folded into the step, the double-pass discard + boundary harvest/respawn, the bit-exact T4 cross-validation; 1e6 in 5.3 s) + the G0 uniform engine (the single global golden-pinned MT19937, one draw per (lane, step), the bit-exact batch-draw port) — the G0 is the I-017 CORPUS GENERATOR (D-174, Roberto's design call after the D-173 gate verdict) | 14/0/2 (via test_hlp_wave; LONG: the 1e6 G1 + G0 benchmarks) | docs/src/reversi/lm/hlp_wave.md |
| src/reversi/lm/hlp_gate.py | complete: the T6 DESIGN GATE (the I-017 T6, D-172; the v4 doc section 7 pre-registered certification — G1 table pick vs G0 global golden-pinned MT19937 (the bit-exact numba batch-draw port — now the hlp_wave import, the D-174 corpus generator owns it), the 20 D0 G0-vs-G0 pairs @ 1e5 (the parametric q95, the 1/sqrt(N) rescale), the v4 tests 1-6, the structured-array feature codes (the no-overflow exactness); the 1e6 design gate VERDICT FAIL — D-173, the E1-corpus finding) | 14/0/0 (via test_hlp_gate; the full-pipeline smoke under GATE_SMOKE=1) | docs/src/reversi/lm/hlp_gate.md |
| src/reversi/lm/hlp_validate.py | complete: the VALIDATE data module (13th level — the first dedicated data module of a non-cache level); closed (D-101/D-102) | 5/0/0 (via test_lm_worker_validate) | docs/src/reversi/lm/hlp_validate.md |
| src/reversi/lm/hlp_wmaps.py | complete: the WMAPS data object (6th level); closed (D-086/D-087/D-088); the LZ4 default (D-139) | 15/0/0 | docs/src/reversi/lm/hlp_wmaps.md |
| src/reversi/lm/hlp_zed.py | complete: the ZED data module (8th level); closed (D-091/D-092) | 10/0/0 | docs/src/reversi/lm/hlp_zed.md |
| src/reversi/tools/state_machine.py | complete: the generic pipeline orchestrator (Workers up/down + Context + logging / history / CSV); closed (D-057..D-070, D-074, D-078); standing contracts: sentinel worker 0 (D-059), failure semantics (D-060), unique names (D-061), *_for_current_level naming (D-069) | 49/0/0 | docs/src/reversi/tools/state_machine.md |

## Test files
One row per test file, alphabetical.

| File | State | Suite (live DB) | Doc |
| --- | --- | --- | --- |
| src/reversi/test/paths.py | the single home for workspace-root-anchored test paths (D-085) — helper module (0 tests) | — | docs/src/reversi/test/paths.md |
| src/reversi/test/test_binio.py | complete: the T4 batch (D-051); the 3 empty-suffix tests (D-095) | 45/0/0 | docs/src/reversi/test/test_binio.md |
| src/reversi/test/test_board.py | complete: the fix campaign closed (D-026..D-033); the header cleaned up — the "environmeant" typo (D-050) + the grammar sentence (D-121); +20 D-140 tests (array path + 2 PERF) | 221/0/14 | docs/src/reversi/test/test_board.md |
| src/reversi/test/test_cache_manager.py | complete: 22 tests; the D-085 idiom applied (D-072) | 22/0/0 | docs/src/reversi/test/test_cache_manager.md |
| src/reversi/test/test_client.py | complete: the client EF suite (D-141) — the synthetic rlm_04-mirror weights (no DB), the 1000-position bit-exact parity, the u64 coercion, the 2-D guard, the scalar/list rejections, the N=0 edge + the PERF 1M test (PERF=1, measured 5.6M b/s) | 6/0/1 | docs/src/reversi/test/test_client.md |
| src/reversi/test/test_feature.py | complete: 9 verified facts (D-043); the header typo fixed with D-050 | 20/0/1 | docs/src/reversi/test/test_feature.md |
| src/reversi/test/test_prng.py | complete: the MT19937 suite — the smoke micro-suite (the I-017 T2, D-159: the determinism, the dtype pins, the no-consume contracts) + the C-oracle golden suite (T3, D-161: the committed 13003-line golden + the first-100k equi-distribution); D-160: the rename with the module | 20/0/0 | docs/src/reversi/test/test_prng.md |
| src/reversi/test/test_wrk_analytics.py | complete: the ANALYTICS worker suite (D-103 T5, D-105; the D-142 masked-hash helper + the 2 file-report goldens re-pinned) | 4/0/0 | docs/src/reversi/test/test_wrk_analytics.md |
| src/reversi/test/test_wrk_client_check.py | complete: the CLIENT_CHECK worker suite (D-148) — the synthetic rlm_04-mirror ctx (no DB, the real v2 SAVE write), the bit-identity golden ("max difference 0.000e+00"), the RuntimeError + FileNotFoundError paths, the cfg-tolerance pin, the factory name, the no-op down | 6/0/0 | docs/src/reversi/test/test_wrk_client_check.md |
| src/reversi/test/test_hlp_plot.py | complete: the PLOT pure-helper suite (D-149; D-150: the _sym_limit tests) — the seven-name vocabulary lock-step (names ⇄ builders ⇄ titles), the symmetric-axis limit (round-up to the step, the degenerate guard), the R-semantic jitter bounds + the zero-range identity, the EGV even-grid bins + the known-values vector, the KDE zero-variance guard + the curve shape/peak | 11/0/0 | docs/src/reversi/test/test_hlp_plot.md |
| src/reversi/test/test_wrk_plot.py | complete: the PLOT worker suite (D-149; D-150: the outlier-report test + the re-pinned parity golden; D-158: the env-drift golden re-pin) — the synthetic rlm_04-mirror ctx (no DB, the per-instance index contract), the pilot no-ops (enable=false / the empty whitelist), the seven-PNG happy path + the per-up-move byte determinism, the pdf/png pair, the absolute dir, the partial whitelist, the top-20 outlier report (header + 20 lines, non-increasing |residual|), the parity rendering golden, the factory, the no-op down | 10/0/0 | docs/src/reversi/test/test_wrk_plot.md |
| src/reversi/test/test_wrk_config.py | complete: 13 tests (D-078; D-142: the 4-test CacheLogic class removed, the fingerprint + no-cache pins added) | 13/0/0 | docs/src/reversi/test/test_wrk_config.md |
| src/reversi/test/test_wrk_design_matrix.py | complete: the DESIGN_MTR worker suite (D-090) | 3/0/0 | docs/src/reversi/test/test_wrk_design_matrix.md |
| src/reversi/test/test_wrk_features.py | complete: Roberto's file; the D-065/D-085 idiom applied (D-082); D-157: DB-free (the gate + the POSITIONS move removed) | 3/0/0 (DB-free) | docs/src/reversi/test/test_wrk_features.md |
| src/reversi/test/test_lm_worker_full_chain.py | the END-TO-END suite: the full 17-level chain (3 A2030 + 2 read guards + 3 D-144 v2 micro; D-148: the 14/SAVE → 15/CLIENT_CHECK re-pin + the A2030 client-check log pin; D-149: the 15/CLIENT_CHECK → 16/PLOT re-pin + the seven-PNG + the "Plot ... saved:" / "PLOT done: 7 plot(s)" log pins in BOTH chains + the size bands re-centered 22940-23040 / 516500-516700; D-150: the A2030 outlier pins — the "Top 20 extreme validation residuals (outlier report):" header + the 20-count) + the full saved-model round-trip; the A2050 chain VLONG-gated (~1 min since D-145, D-130); the D-104/D-105 pins + the D-141 array-EF batch pin + the D-144 single-source config pin (A2030, the D-142 record test converted) + the v2 read-back provenance pins (A2030 + A2050) + the Config SHA3-256 report pins; D-145: the HP-trajectory re-pin (A2030 71 iters, A2050 356 iters, the w_dense sha3 + EF + report-hash pins, the size bands) | 9/0/1 | docs/src/reversi/test/test_lm_worker_full_chain.md |
| src/reversi/test/test_wrk_generate.py | complete: the GENERATE worker suite (D-097/D-098) | 3/0/0 | docs/src/reversi/test/test_wrk_generate.md |
| src/reversi/test/test_wrk_gradient.py | complete: the GRADIENT worker suite (the float32 contract pin, D-094; D-145: the 2 no-DB flag-wiring tests) | 4/0/0 | docs/src/reversi/test/test_wrk_gradient.md |
| src/reversi/test/test_wrk_indexes.py | complete: the end-to-end cache round-trip pin (D-084); D-157: the setUp step re-pin (FEATURES = step 2) | 2/0/0 | docs/src/reversi/test/test_wrk_indexes.md |
| src/reversi/test/test_wrk_optimize.py | complete: the OPTIMIZE worker suite (D-096) | 3/0/0 | docs/src/reversi/test/test_wrk_optimize.md |
| src/reversi/test/test_wrk_positions.py | complete: Roberto's file; the gate + the D-085 idiom applied (D-080); the D-143 TestLMWorkerPositionsDuplicates (the duplicate policy + the post-policy cache); D-157: rlmwf_03 + step 3 | 12/0/0 | docs/src/reversi/test/test_wrk_positions.md |
| src/reversi/test/test_wrk_validate.py | complete: the VALIDATE worker suite (D-101/D-102) | 5/0/0 | docs/src/reversi/test/test_wrk_validate.md |
| src/reversi/test/test_wrk_vld_positions.py | complete: the VLD_POSITIONS worker suite (D-099/D-100); the D-143 TestVldIndependenceCheck (0% / 100% overlap, traced not raised) | 11/0/0 | docs/src/reversi/test/test_wrk_vld_positions.md |
| src/reversi/test/test_wrk_wmaps.py | complete: the WMAPS worker suite (D-087) | 3/0/0 | docs/src/reversi/test/test_wrk_wmaps.md |
| src/reversi/test/test_wrk_zed.py | complete: the ZED worker suite (D-091/D-092) | 3/0/0 | docs/src/reversi/test/test_wrk_zed.md |
| src/reversi/test/test_logistic_model.py | complete: all 15 methods active (the last muted test restored, 887880e); the D-075/D-076/D-078 corner pins; D-157: the dummy FEATURES worker (the string move to POSITIONS crosses step 2) | 17/0/0 | docs/src/reversi/test/test_logistic_model.md |
| src/reversi/test/test_mobility.py | analyzed (D-037): 13 verified facts | 26/0/1 | docs/src/reversi/test/test_mobility.md |
| src/reversi/test/test_opt_lbfgs.py | complete: the T7 batch + 9 new tests (D-053); D-146: the O2b bit-identity test (the original two-loop algorithm embedded verbatim as the reference) | 14/0/0 | docs/src/reversi/test/test_opt_lbfgs.md |
| src/reversi/test/test_paths.py | complete: the 3 pin tests for the workspace-root paths (D-085) | 3/0/0 | docs/src/reversi/test/test_paths.md |
| src/reversi/test/test_pattern.py | complete: the fix campaign closed (D-026..D-033; T17 the sqa8/sqh1 fixture swap; 21/21 goldens re-derived); T18 retired + M1 fixed in pattern.py (D-121) | 65/0/3 | docs/src/reversi/test/test_pattern.md |
| src/reversi/test/test_regab.py | complete: the T5/T6/T7 batch (D-052) incl. the 4 SQL-injection tests; the db_long_gate (35 DB tests, D-130); the D-143 no-DB micro tier (11 tests: dedup + overlap) | 48/0/0 | docs/src/reversi/test/test_regab.md |
| src/reversi/test/test_hlp_config_schemas.py | complete: the pydantic config domain suite (D-079/D-080; D-145: the flag test; D-148: the 3 client_check_tol tests — default / override+dump / gt=0; D-149: the 6 PlotConfig tests — the defaults (the png-default ruling + the empty whitelist), the format pair + normalization, the bad-format rejections, the fail-fast unknown name, the dedupe, the dir absolute/relative) | 23/0/0 | docs/src/reversi/test/test_hlp_config_schemas.md |
| src/reversi/test/test_hlp_design_matrix.py | complete: the dedicated 14-test data suite (D-090, +2 with D-139) | 14/0/0 | docs/src/reversi/test/test_hlp_design_matrix.md |
| src/reversi/test/test_hlp_generate.py | complete: the GENERATE data suite (D-097/D-098, +2 with D-139) | 16/0/0 | docs/src/reversi/test/test_hlp_generate.md |
| src/reversi/test/test_hlp_gradient.py | complete: the GRADIENT data suite (D-094 M1; D-145: the TestHighPerformanceFg class — equivalence, f32 contract, determinism, markers) | 14/0/0 | docs/src/reversi/test/test_hlp_gradient.md |
| src/reversi/test/test_hlp_indexes.py | complete: 14 tests (D-084; the compressed mock pins with D-139) | 14/0/0 | docs/src/reversi/test/test_hlp_indexes.md |
| src/reversi/test/test_hlp_optimize.py | complete: the OPTIMIZE data suite (D-096, +1 with D-139) | 20/0/0 | docs/src/reversi/test/test_hlp_optimize.md |
| src/reversi/test/test_hlp_random_play.py | complete: the T4 NO-DB micro-suite (D-162) — the table properties, the pick kernel, the hand-counted games (the identity trace, the pass branch, the full 60-ply game, the non-full double pass — the D-169 fix), the seeded pinned trajectories + the independent replay; + the T7 micro-suite (D-177): the ec pin (the hand-counted stone counts, the empty-count identity) + the marginal accumulator (the LMC hand-counted vs the independent position_legal_moves oracle, the R2 inst0 cross-check via compute_indexes, the chunk-merge invariance); + the T8 micro-suite (D-178): the joint accumulator (the (LMC, R2) cross-feature + the (R2, R2) same-feature, each joint vs the independent per-position oracle, the same-feature diagonal ZERO off-diagonal, the chunk-merge invariance) | 21/0/0 | docs/src/reversi/test/test_hlp_random_play.md |
| src/reversi/test/test_hlp_wave.py | complete: the T5 + D-174 NO-DB micro-suite — K1 the pick kernel vs the T4 pick, LAW-1/2 the bit-exact harvest + the phase invariance, the W=1 pass-carrying trajectory (pinned slot 712), LAW-3 the pass fold, LAW-4 the double-pass discard + respawn, the run integrity, the G0 engine (the batch kernel bit-exact vs the golden oracle, the W=1 trajectory ≡ the scalar reference, the run integrity + the determinism), the LONG 1e6 G1 + G0 benchmarks | 14/0/2 (LONG: the benchmarks) | docs/src/reversi/lm/hlp_wave.md |
| src/reversi/test/test_hlp_gate.py | complete: the T6 NO-DB micro-suite (D-172) — the MT19937 batch-draw kernel vs the golden-pinned reference (bit-exact, the twist boundary, the mid-stream start), the W=1 G0 wave ≡ the scalar G0 reference (the stream discipline), the statistics utilities on the hand-computed values, the structured keys (the no-overflow), the full gate smoke (GATE_SMOKE=1) | 14/0/0 (the smoke under GATE_SMOKE=1) | docs/src/reversi/lm/hlp_gate.md |
| src/reversi/test/test_hlp_wmaps.py | complete: the WMAPS data suite (D-087, +2 with D-139) | 15/0/0 | docs/src/reversi/test/test_hlp_wmaps.md |
| src/reversi/test/test_hlp_zed.py | complete: the dedicated 10-test data suite (D-091/D-092) | 10/0/0 | docs/src/reversi/test/test_hlp_zed.md |
| src/reversi/test/test_state_machine.py | complete: 13 original expectations independently re-derived; the T/R/M pins per the D-057..D-070 campaign | 49/0/0 | docs/src/reversi/test/test_state_machine.md |
| src/reversi/test/test_usage_binio.py | complete: the 3 usage tests (D-051) | 3/0/0 | docs/src/reversi/test/test_usage_binio.md |

Test data (src/reversi/test/data/): rlm_00.json (the JSON5 config, D-076),
rlm_01.json (the training DB dump), rlm_02.json (the DB dump), rlm_03.json +
rlm_04.json (the validation sets) — the per-file mirror docs cover them.

## Index
The docs/ mirrors (one per source/test file, D-007) are NOT listed
here: their paths are the Doc column of the two tables above.

- notes/naming.md — canonical board naming convention (row/column,
  D-013; D8 symmetries, D-014)
- notes/rules.md — active legislation: the register of the rules in force (one line per rule, origin D-number; lifecycle RECORD/PROMOTE/RETIRE)
- notes/decisions.md — open historical decision log (append-only, D-NNN; D-117…; the rules in force live in notes/rules.md; closed volumes: decisions_NNN.md)
- notes/decisions_000.md — closed decision volume 000 (D-001…D-116, 2026-08-25 → 2026-09-06)
- notes/analyses/ — archived one-off investigations + the D-106
  classification (verify_t2, verify_burnside, the 6 o1* one-offs,
  classification.md) + the extracted verbatim reviews
  (board_session1_review.md at step 4, pattern_session4_review.md
  at step 5, logistic_model_session21_review.md +
  state_machine_session19_review.md at steps 6-7, the CONFIG
  batch #1 trio at step 8: lm_worker_config_session21_review.md,
  rlm_config_schemas_session22_review.md,
  test_lm_worker_config_session21_review.md, the POSITIONS pair
  at step 9: lm_worker_positions_session22_review.md +
  test_lm_worker_positions_session22_review.md, the FEATURES
  quartet at step 10: feature_session11_review.md +
  test_feature_session11_review.md (session 11) +
  lm_worker_features_session22_review.md +
  test_lm_worker_features_session22_review.md (session 22))
- notes/ideas.md — future backlog (I-NNN)
- notes/log_rules.md — session-journal format rules (rigid; global session numbering; volume rotation: 25 sessions / 2000 lines per volume, only at session boundaries)
- notes/docs_rules.md — mirror-doc format rules (rigid; the
  current-state contract: the 4-line header with the `> State:` line
  as the only permitted time, 7 sections, the forbidden-history
  list, the same-commit lifecycle, the test-doc variant, the
  migration state)
- notes/probe_rules.md — verification-apparatus rules (rigid; the
  a/b/c classification + the independent-derivation criterion, the
  test/probe line, the pipeline-state centralization in the hub,
  the campaign sweep rule, the archive to notes/analyses/, the
  baseline)
- notes/log_000.md — session journal, volume 000 (sessions 1–24, closed 2026-09-01)
- notes/log_001.md — session journal, volume 001 (sessions 25–30, closed 2026-09-08)
- notes/log_002.md — session journal, volume 002 (sessions 31–..., open)
