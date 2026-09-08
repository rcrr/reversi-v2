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
- Packaging: `pyproject.toml` (setuptools, src layout) with twolm
  installed editable in .venv (`pip install -e .`, D-011) —
  `import twolm` works without PYTHONPATH, resolving to src/.
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
  `.venv/bin/python -m unittest twolm.test.<module>`. The
  DB-gated suites (test_regab + the worker suites) need a live
  PostgreSQL + .env + LONG=1, or
  `SKIP_REGAB_DB=1` to skip the 70 DB tests (2 mocked run). The
  runner is unittest by design (D-124): pytest is not a
  dependency (and not in the venv).
- Suite status (verified 2026-09-07, live DB, D-130 tiers):
  673 tests / 0 failures. Default tier: 586 run in ~5 s / 87
  skipped (70 DB-gated + 17 PERF print-only). LONG=1: 655 run
  in ~45 s / 18 skipped (17 PERF + 1 VLONG-gated A2050). Gated
  run (SKIP_REGAB_DB=1): 87 skipped = 17 PERF + 70 DB (35 regab
  + 35 worker-level). Per-file suites: the Suite column of the
  Source files / Test files tables below.
- Probes: 21 tracked under probes/ (hub:
  verify_logistic_model.py owns the pipeline-wide state;
  measure_suite.py is the D-132 timing-measurement tool, no
  checks; rules: notes/probe_rules.md); 20/20 verify probes
  green in both gated and live modes (last campaign sweep,
  D-104/D-105).

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
- THE REORGANIZATION CAMPAIGN (I-001, D-133, open since
  2026-09-08): twolm → reversi with the core/tools/lm split
  per Roberto's approved mapping — 2 commits per module
  (file + references, then the method renames), bottom-up
  (tools → core → lm in machine order); the Source / Test
  tables update row by row as each module moves.
- Sources live in the `twolm` package under src/ (D-008); unit
  tests in src/twolm/test/. Environment: .venv with the pinned
  deps (D-010/D-051/D-052), twolm installed editable (D-011).
  Git repo on master (D-003). Collaboration memory: AGENTS.md
  (constitution) + notes/rules.md (active rules) + this file
  (state) + notes/ (the log: decisions.md the open decision log
  + journal volumes, format rules in log_rules.md).

## Next steps

- Feed notes/ideas.md with Roberto's future-evolution ideas.
- wrk_config R1 (the ad-hoc cache flow): the D-078
  ruling — the revisit trigger (the pipeline completion) is
  now met (15/15); re-evaluate the ad-hoc flow against the
  completed pipeline and the "storicizzazione" idea (I-011).
- The reorganization campaign (I-001, D-133): the twolm →
  reversi reorganization per Roberto's approved mapping —
  phase 1, the 36 modules bottom-up (tools → core → lm in
  machine order); RLMContext → LMContext to be reviewed in
  the final inventory.


## Source files
One row per source file, alphabetical (the package path sorts future
packages first). State = a status word + the open/parked items (if any)
+ the D-pointer range; the campaign history lives in the decision log.
Suite = the current verified suite (live DB, D-130 tiers,
2026-09-07) of the file's test module.

| File | State | Suite (live DB) | Doc |
| --- | --- | --- | --- |
| src/reversi/base_model.py | complete: thin facade base over StateMachine (pure delegation); closed (D-074/D-075) | 17/0/0 (via test_logistic_model) | docs/src/reversi/base_model.md |
| src/reversi/board.py | complete: the Reversi game kernel (200 random full games verified on the public API); all issues closed — R1–R5 (D-017 era) + M1–M7 (D-111); I-005: no game-loop module | 201/0/12 | docs/src/reversi/board.md |
| src/reversi/tools/binio.py | complete: binary IO layer — T1–T4 batch (D-051); empty-suffix fix (D-095) | 48/0/0 (45 + 3 usage) | docs/src/reversi/tools/binio.md |
| src/reversi/tools/cache_manager.py | complete: generic load-or-compute cache pipeline (.SHA3-256 sidecar, 8192-chunk verify); closed (D-071/D-072) | 22/0/0 | docs/src/reversi/tools/cache_manager.md |
| src/reversi/feature.py | complete: Feature / FeatureSet (blocked __new__, 3 factories, composition, sorted order); closed (D-038..D-042); the OPEN R1 (unused BeforeValidator import) fixed at D-110 | 20/0/1 | docs/src/reversi/feature.md |
| src/twolm/lm_worker_analytics.py | complete: the ANALYTICS 14th level — training metrics + console / file reports (the 3-metric header + dense metrics, D-105/M2); closed (D-103) | 4/0/0 | docs/src/twolm/lm_worker_analytics.md |
| src/reversi/lm/wrk_config.py | complete: the CONFIG worker (JSON5 → config → base_dir validation + cache persistence); closed (D-077/D-078). DEFERRED: R1 the ad-hoc cache flow (the D-078 ruling, revisit with the pipeline completion; I-011) | 15/0/0 | docs/src/reversi/lm/wrk_config.md |
| src/reversi/lm/wrk_design_matrix.py | complete: the DESIGN_MTR 7th-level worker; closed (D-090) | 3/0/0 | docs/src/reversi/lm/wrk_design_matrix.md |
| src/reversi/lm/wrk_features.py | complete: the FEATURES worker — the first pure-compute level (no cache file ever); closed (D-081/D-082) | 3/0/0 | docs/src/reversi/lm/wrk_features.md |
| src/reversi/lm/wrk_generate.py | complete: the GENERATE 11th level (dense weights materialization; the R1 for-next-level trap fix); closed (D-097/D-098) | 3/0/0 | docs/src/reversi/lm/wrk_generate.md |
| src/reversi/lm/wrk_gradient.py | complete: the GRADIENT 9th level (the second non-cache; the float32 contract, D-094 R1); closed (D-093/D-094) | 2/0/0 | docs/src/reversi/lm/wrk_gradient.md |
| src/reversi/lm/wrk_indexes.py | complete: the INDEXES worker (uniform 7-kwargs cache wiring); closed (D-083/D-084) | 2/0/0 | docs/src/reversi/lm/wrk_indexes.md |
| src/reversi/lm/wrk_optimize.py | complete: the OPTIMIZE 10th level — the only level whose "cache" is a plain checkpoint dict via binio; closed (D-096) | 3/0/0 | docs/src/reversi/lm/wrk_optimize.md |
| src/reversi/lm/wrk_positions.py | complete: the POSITIONS worker — the first cache_manager consumer over the regab data set; closed (D-079/D-080) | 9/0/0 | docs/src/reversi/lm/wrk_positions.md |
| src/twolm/lm_worker_save.py | complete: the SAVE 15th and LAST level — the pipeline is 15/15 (D-104) | 5/0/1 (via test_lm_worker_full_chain) | docs/src/twolm/lm_worker_save.md |
| src/twolm/lm_worker_validate.py | complete: the VALIDATE 13th level (the third non-cache worker); closed (D-101/D-102) | 5/0/0 | docs/src/twolm/lm_worker_validate.md |
| src/reversi/lm/wrk_vld_positions.py | complete: the VLD_POSITIONS 12th level (the POSITIONS twin over the validation set); closed (D-099/D-100) | 9/0/0 | docs/src/reversi/lm/wrk_vld_positions.md |
| src/reversi/lm/wrk_wmaps.py | complete: the WMAPS 6th-level worker; closed (D-086/D-087/D-088) | 3/0/0 | docs/src/reversi/lm/wrk_wmaps.md |
| src/reversi/lm/wrk_zed.py | complete: the ZED 8th level (the first non-cache level); closed (D-091/D-092) | 3/0/0 | docs/src/reversi/lm/wrk_zed.md |
| src/twolm/logistic_model.py | complete: the RLM facade — RLMContext blackboard (40 fields, 8 *_checksum, 3 injected callables) + the 15-level worker list, activated line by line (D-076..D-104); the stale "Remove comments" line dropped (D-113) | 17/0/0 | docs/src/twolm/logistic_model.md |
| src/reversi/mobility.py | complete: mobility / MobilitySet + popcount64 SWAR kernel; closed (D-035/D-036); disposition per D-036 (PERF tests print-only, no perf gate) | 26/0/1 | docs/src/reversi/mobility.md |
| src/twolm/model_weights.py | complete: the model_weights @dataclass (D-104) | 5/0/1 (via test_lm_worker_full_chain) | docs/src/twolm/model_weights.md |
| src/reversi/tools/opt_lbfgs.py | complete: the LBFGS solver — T1–T7 batch incl. the RuntimeException hard-bug fix (D-053) | 13/0/0 | docs/src/reversi/tools/opt_lbfgs.md |
| src/reversi/pattern.py | complete: principal mask = numerically lowest orbit (D-020); minor sweep 19/19 (D-023/024/025); Burnside attributes (D-032); PatternSet.__repr__ (D-112); the PatternSet Raises docstring fixed — @validate_call raises ValidationError, not TypeError (D-121) | 65/0/3 | docs/src/reversi/pattern.md |
| src/reversi/regab.py | complete: the PostgreSQL regab access layer — T1–T7 batch (D-052) | 37/0/0 | docs/src/reversi/regab.md |
| src/twolm/rlm_analytics.py | complete: the ANALYTICS data module (the 3-metric header + Population baseline + dense metrics, D-105/M2); closed (D-103) | 4/0/0 | docs/src/twolm/rlm_analytics.md |
| src/twolm/rlm_client.py | complete: the inference client (D-104) | 5/0/1 (via test_lm_worker_full_chain) | docs/src/twolm/rlm_client.md |
| src/reversi/lm/hlp_config_schemas.py | complete: the pydantic config domain (the ReversiLogisticModelConfig JSON5 entry point); closed (D-079/D-080) | 13/0/0 | docs/src/reversi/lm/hlp_config_schemas.md |
| src/reversi/lm/hlp_design_matrix.py | complete: the DESIGN_MTR data module (7th level); closed (D-090) | 12/0/0 | docs/src/reversi/lm/hlp_design_matrix.md |
| src/reversi/lm/hlp_generate.py | complete: the GENERATE data module (11th level); closed (D-097/D-098) | 14/0/0 | docs/src/reversi/lm/hlp_generate.md |
| src/reversi/lm/hlp_gradient.py | complete: the GRADIENT data module (9th level; the float32 contract); closed (D-093/D-094) | 8/0/0 | docs/src/reversi/lm/hlp_gradient.md |
| src/reversi/lm/hlp_indexes.py | complete: the INDEXES data module; closed (D-083/D-084) | 14/0/0 | docs/src/reversi/lm/hlp_indexes.md |
| src/reversi/lm/hlp_optimize.py | complete: the OPTIMIZE data module (10th level); closed (D-096) | 19/0/0 | docs/src/reversi/lm/hlp_optimize.md |
| src/reversi/lm/hlp_validate.py | complete: the VALIDATE data module (13th level — the first dedicated data module of a non-cache level); closed (D-101/D-102) | 5/0/0 (via test_lm_worker_validate) | docs/src/reversi/lm/hlp_validate.md |
| src/reversi/lm/hlp_wmaps.py | complete: the WMAPS data object (6th level); closed (D-086/D-087/D-088) | 13/0/0 | docs/src/reversi/lm/hlp_wmaps.md |
| src/reversi/lm/hlp_zed.py | complete: the ZED data module (8th level); closed (D-091/D-092) | 10/0/0 | docs/src/reversi/lm/hlp_zed.md |
| src/reversi/tools/state_machine.py | complete: the generic pipeline orchestrator (Workers up/down + Context + logging / history / CSV); closed (D-057..D-070, D-074, D-078); standing contracts: sentinel worker 0 (D-059), failure semantics (D-060), unique names (D-061), *_for_current_level naming (D-069) | 49/0/0 | docs/src/reversi/tools/state_machine.md |

## Test files
One row per test file, alphabetical.

| File | State | Suite (live DB) | Doc |
| --- | --- | --- | --- |
| src/reversi/test/paths.py | the single home for workspace-root-anchored test paths (D-085) — helper module (0 tests) | — | docs/src/reversi/test/paths.md |
| src/reversi/test/test_binio.py | complete: the T4 batch (D-051); the 3 empty-suffix tests (D-095) | 45/0/0 | docs/src/reversi/test/test_binio.md |
| src/reversi/test/test_board.py | complete: the fix campaign closed (D-026..D-033); the header cleaned up — the "environmeant" typo (D-050) + the grammar sentence (D-121) | 201/0/12 | docs/src/reversi/test/test_board.md |
| src/reversi/test/test_cache_manager.py | complete: 22 tests; the D-085 idiom applied (D-072) | 22/0/0 | docs/src/reversi/test/test_cache_manager.md |
| src/reversi/test/test_feature.py | complete: 9 verified facts (D-043); the header typo fixed with D-050 | 20/0/1 | docs/src/reversi/test/test_feature.md |
| src/twolm/test/test_lm_worker_analytics.py | complete: the ANALYTICS worker suite (D-103 T5, D-105) | 4/0/0 | docs/src/twolm/test/test_lm_worker_analytics.md |
| src/reversi/test/test_wrk_config.py | complete: 15 tests (D-078) | 15/0/0 | docs/src/reversi/test/test_wrk_config.md |
| src/reversi/test/test_wrk_design_matrix.py | complete: the DESIGN_MTR worker suite (D-090) | 3/0/0 | docs/src/reversi/test/test_wrk_design_matrix.md |
| src/reversi/test/test_wrk_features.py | complete: Roberto's file; the D-065/D-085 idiom applied (D-082) | 3/0/0 | docs/src/reversi/test/test_wrk_features.md |
| src/twolm/test/test_lm_worker_full_chain.py | the END-TO-END suite: the full 15-level chain (2 A2030 + 2 read guards) + the full saved-model round-trip; the A2050 chain VLONG-gated (~10 min, D-130); the D-104/D-105 pins | 5/0/1 | docs/src/twolm/test/test_lm_worker_full_chain.md |
| src/reversi/test/test_wrk_generate.py | complete: the GENERATE worker suite (D-097/D-098) | 3/0/0 | docs/src/reversi/test/test_wrk_generate.md |
| src/reversi/test/test_wrk_gradient.py | complete: the GRADIENT worker suite (the float32 contract pin, D-094) | 2/0/0 | docs/src/reversi/test/test_wrk_gradient.md |
| src/reversi/test/test_wrk_indexes.py | complete: the end-to-end cache round-trip pin (D-084) | 2/0/0 | docs/src/reversi/test/test_wrk_indexes.md |
| src/reversi/test/test_wrk_optimize.py | complete: the OPTIMIZE worker suite (D-096) | 3/0/0 | docs/src/reversi/test/test_wrk_optimize.md |
| src/reversi/test/test_wrk_positions.py | complete: Roberto's file; the gate + the D-085 idiom applied (D-080) | 9/0/0 | docs/src/reversi/test/test_wrk_positions.md |
| src/twolm/test/test_lm_worker_validate.py | complete: the VALIDATE worker suite (D-101/D-102) | 5/0/0 | docs/src/twolm/test/test_lm_worker_validate.md |
| src/reversi/test/test_wrk_vld_positions.py | complete: the VLD_POSITIONS worker suite (D-099/D-100) | 9/0/0 | docs/src/reversi/test/test_wrk_vld_positions.md |
| src/reversi/test/test_wrk_wmaps.py | complete: the WMAPS worker suite (D-087) | 3/0/0 | docs/src/reversi/test/test_wrk_wmaps.md |
| src/reversi/test/test_wrk_zed.py | complete: the ZED worker suite (D-091/D-092) | 3/0/0 | docs/src/reversi/test/test_wrk_zed.md |
| src/twolm/test/test_logistic_model.py | complete: all 15 methods active (the last muted test restored, 887880e); the D-075/D-076/D-078 corner pins | 17/0/0 | docs/src/twolm/test/test_logistic_model.md |
| src/reversi/test/test_mobility.py | analyzed (D-037): 13 verified facts | 26/0/1 | docs/src/reversi/test/test_mobility.md |
| src/reversi/test/test_opt_lbfgs.py | complete: the T7 batch + 9 new tests (D-053) | 13/0/0 | docs/src/reversi/test/test_opt_lbfgs.md |
| src/reversi/test/test_paths.py | complete: the 3 pin tests for the workspace-root paths (D-085) | 3/0/0 | docs/src/reversi/test/test_paths.md |
| src/reversi/test/test_pattern.py | complete: the fix campaign closed (D-026..D-033; T17 the sqa8/sqh1 fixture swap; 21/21 goldens re-derived); T18 retired + M1 fixed in pattern.py (D-121) | 65/0/3 | docs/src/reversi/test/test_pattern.md |
| src/reversi/test/test_regab.py | complete: the T5/T6/T7 batch (D-052) incl. the 4 SQL-injection tests; the db_long_gate (35 DB tests, D-130) | 37/0/0 | docs/src/reversi/test/test_regab.md |
| src/reversi/test/test_hlp_config_schemas.py | complete: the pydantic config domain suite (D-079/D-080) | 13/0/0 | docs/src/reversi/test/test_hlp_config_schemas.md |
| src/reversi/test/test_hlp_design_matrix.py | complete: the dedicated 12-test data suite (D-090) | 12/0/0 | docs/src/reversi/test/test_hlp_design_matrix.md |
| src/reversi/test/test_hlp_generate.py | complete: the GENERATE data suite (D-097/D-098) | 14/0/0 | docs/src/reversi/test/test_hlp_generate.md |
| src/reversi/test/test_hlp_gradient.py | complete: the GRADIENT data suite (D-094 M1) | 8/0/0 | docs/src/reversi/test/test_hlp_gradient.md |
| src/reversi/test/test_hlp_indexes.py | complete: 14 tests (D-084) | 14/0/0 | docs/src/reversi/test/test_hlp_indexes.md |
| src/reversi/test/test_hlp_optimize.py | complete: the OPTIMIZE data suite (D-096) | 19/0/0 | docs/src/reversi/test/test_hlp_optimize.md |
| src/reversi/test/test_hlp_wmaps.py | complete: the WMAPS data suite (D-087) | 13/0/0 | docs/src/reversi/test/test_hlp_wmaps.md |
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
