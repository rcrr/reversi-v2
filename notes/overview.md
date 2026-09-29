# overview.md — entry point

## Format rules (rigid — follow when editing this file)

The rigid format rules for this file live in notes/rules.md — the "Roles of the notes files" section, the
notes/overview.md bullet. Consult it before editing.

## Project

This workspace is dedicated to the research and development of evaluation functions for Reversi positions. The methods
employed focus on machine learning techniques that leverage solved positions generated from random gameplay paths.

## Conventions in the code (respect them in any new work)

- Board vocabulary is canonical: **row** (1–8, top→bottom) and **column** (A–H, left→right) — never file/rank (chess).
  A1 = top-left (N-W) = bit 0; H8 = bottom-right (S-E) = bit 63. row_1 = [A1..H1]; column_a = [A1..A8]. Full text:
  notes/naming.md (D-013).
- Dual scalar/array API: public functions accept scalar OR 1-D array, return the input kind. Same validation pattern
  everywhere (is_scalar → atleast_1d → ndim check → dispatch → reshape back).
- `@validate_call` (pydantic, arbitrary_types_allowed) on all public functions.
- Numba `njit(cache=True)` + `prange` for hot loops; numba overloads for the four D8 primitives (fa1h8, fh1a8, fhori,
  fvert).
- Position = numpy structured dtype `[('mover', u64), ('opponent', u64)]`.
- Move codes: 0..63 = squares, 64 = PA (pass), 65 = NA, 66 = UN.
- D8 slot order is fixed and load-bearing (D-014): anti-transform slot s = T_s^{-1}; in pattern.py instance 0 = the
  ro000 image, and trans_fs/anti_trans_fs are indexed by instance (length = n_instances), not by slot.
- Pattern config indexes are base-3 uint32 over ≤ 18 squares (S ≤ 18); packed bit k ↔ the k-th square of
  `Pattern.squares` (ascending board order); principal index = min over the induced-stabilizer orbit.
- Test artifacts (D-065): unit tests write files ONLY under `workspace_root/build/tmp` and remove them afterwards (a
  `finally`/cleanup unlink, so a failing test leaves no garbage); no test writes anywhere else (notably: not the CWD).
  `build/` is gitignored.


## Environment

- Venv: `.venv/` (gitignored, D-010), Python 3.12.3.
- Packaging: `pyproject.toml` (setuptools, src layout) with the `reversi` package installed editable in .venv —
  `import reversi` works without PYTHONPATH, resolving to src/.
- Dependencies (pyproject.toml, minimal set): numpy ≥ 2.0 (bitboards / structured dtypes), pydantic ≥ 2
  (@validate_call), numba ≥ 0.60 (njit / prange / overload; pulls llvmlite), lz4 (binio), psycopg2 / pandas /
  python-dotenv (regab).
- Test command: `./run_utests.sh` (the canonical runner; tiers: default fast ~5 s, LONG=1, VLONG=1 ~10 min incl. the
  A2050 chain and implies LONG; PERF=1 adds the print-only perf tests). The standard pre-commit run is
  `LONG=1 ./run_utests.sh`; VLONG=1 only when useful. A single module:
  `.venv/bin/python -m unittest test.reversi[.zone].<module>` (the zones: lm, tools). The DB-gated suites (test_regab +
  the worker suites) need a live PostgreSQL + .env + LONG=1, or `SKIP_REGAB_DB=1` to skip the DB tests. The runner is
  unittest by design (pytest is not a dependency).
- Probes: tracked under probes/ (hub: verify_logistic_model.py owns the pipeline-wide state; rules:
  notes/probe_rules.md).

## Current state

Current state only — the session-by-session history lives in the journal volumes (notes/log_NNN.md) and the decision log
(notes/decisions.md); the file-by-file state lives in the Source files / Test files tables below. MAX 10 bullets, no
bullet-per-campaign (D-334).

- The 19-level pipeline is live and green (968 tests, LONG; the 1e6 wave benchmark — VVLONG — replays bit-exact, 28065
  dead lanes): the ML chain CONFIG → … → SAVE → CLIENT_CHECK → PLOT → FINAL_LOG_PRINT (the optional full run log on
  file, the `log_file_name` gate), plus the OPTIONAL SU_ANALYSIS (step 3) + ANOVA (step 6) — default FALSE, opt-in.
- The descriptive docstring style is the house rule (rules.md, D-318); the retroactive conversion stays user-directed,
  one module at a time.
- The LM facade is the pipeline's script entry:
  `python -m reversi.lm.logistic_model <config.json> [--verbosity {high,moderate,standard,low,very_low,none}]` (default
  `standard`), from the workspace root; the stop is target-driven — `run(target_level=…)` runs CONFIG first, then stops
  at the argument / `cfg.target_level` / the last step.
- The ec (empty_count) is consolidated in ONE required root field (int, 0..60, between name and description): the single
  source for the SU corpus generation, the DB extraction (training + validation), and the saved model.


## Next steps

- Select the tests by DURATION with the 5 tags (VVLONG, VLONG, LONG, PERF, DB); re-verify the tag-assignment technique;
  analyze every LONG / VLONG / VVLONG test for a possible shorter equivalent.
- Verify all the TEST sources: the code + docstring format, the documentation criteria (D-267); remove the documentation
  that describes the history.
- Rework MOBILITY: drop the difference concept — a mobility is a MASK + a binary flag (mover vs opponent).
- Add the project README (English, like everything else).
- Verify the format of the WORKER sources — all the sub-works (the history out of the docstrings, the 120-char reflow,
  the D-318 docstring conversion).
- Verify the format of the board, pattern, feature, mobility sources + the tools (the same sub-works).

## Source files
One row per source file, alphabetical by full path. State = a status word + the open/parked items (if any); the campaign
history lives in the decision log.

| File | State | Doc |
| --- | --- | --- |
| src/reversi/base_model.py | complete | [docs/src/reversi/base_model.md](docs/src/reversi/base_model.md) |
| src/reversi/board.py | complete | [docs/src/reversi/board.md](docs/src/reversi/board.md) |
| src/reversi/feature.py | complete | [docs/src/reversi/feature.md](docs/src/reversi/feature.md) |
| src/reversi/lm/client.py | complete | [docs/src/reversi/lm/client.md](docs/src/reversi/lm/client.md) |
| src/reversi/lm/hlp_analytics.py | complete | [docs/src/reversi/lm/hlp_analytics.md](docs/src/reversi/lm/hlp_analytics.md) |
| src/reversi/lm/hlp_anova.py | complete | [docs/src/reversi/lm/hlp_anova.md](docs/src/reversi/lm/hlp_anova.md) |
| src/reversi/lm/hlp_config_schemas.py | complete | [docs/src/reversi/lm/hlp_config_schemas.md](docs/src/reversi/lm/hlp_config_schemas.md) |
| src/reversi/lm/hlp_design_matrix.py | complete | [docs/src/reversi/lm/hlp_design_matrix.md](docs/src/reversi/lm/hlp_design_matrix.md) |
| src/reversi/lm/hlp_final_log_print.py | complete | [docs/src/reversi/lm/hlp_final_log_print.md](docs/src/reversi/lm/hlp_final_log_print.md) |
| src/reversi/lm/hlp_generate.py | complete | [docs/src/reversi/lm/hlp_generate.md](docs/src/reversi/lm/hlp_generate.md) |
| src/reversi/lm/hlp_gradient.py | complete | [docs/src/reversi/lm/hlp_gradient.md](docs/src/reversi/lm/hlp_gradient.md) |
| src/reversi/lm/hlp_indexes.py | complete | [docs/src/reversi/lm/hlp_indexes.md](docs/src/reversi/lm/hlp_indexes.md) |
| src/reversi/lm/hlp_optimize.py | complete | [docs/src/reversi/lm/hlp_optimize.md](docs/src/reversi/lm/hlp_optimize.md) |
| src/reversi/lm/hlp_plot.py | complete | [docs/src/reversi/lm/hlp_plot.md](docs/src/reversi/lm/hlp_plot.md) |
| src/reversi/lm/hlp_su_analysis.py | complete | [docs/src/reversi/lm/hlp_su_analysis.md](docs/src/reversi/lm/hlp_su_analysis.md) |
| src/reversi/lm/hlp_validate.py | complete | [docs/src/reversi/lm/hlp_validate.md](docs/src/reversi/lm/hlp_validate.md) |
| src/reversi/lm/hlp_wmaps.py | complete | [docs/src/reversi/lm/hlp_wmaps.md](docs/src/reversi/lm/hlp_wmaps.md) |
| src/reversi/lm/hlp_zed.py | complete | [docs/src/reversi/lm/hlp_zed.md](docs/src/reversi/lm/hlp_zed.md) |
| src/reversi/lm/logistic_model.py | complete | [docs/src/reversi/lm/logistic_model.md](docs/src/reversi/lm/logistic_model.md) |
| src/reversi/lm/model_weights.py | complete | [docs/src/reversi/lm/model_weights.md](docs/src/reversi/lm/model_weights.md) |
| src/reversi/lm/wrk_analytics.py | complete | [docs/src/reversi/lm/wrk_analytics.md](docs/src/reversi/lm/wrk_analytics.md) |
| src/reversi/lm/wrk_anova.py | complete | [docs/src/reversi/lm/wrk_anova.md](docs/src/reversi/lm/wrk_anova.md) |
| src/reversi/lm/wrk_client_check.py | complete | [docs/src/reversi/lm/wrk_client_check.md](docs/src/reversi/lm/wrk_client_check.md) |
| src/reversi/lm/wrk_config.py | complete | [docs/src/reversi/lm/wrk_config.md](docs/src/reversi/lm/wrk_config.md) |
| src/reversi/lm/wrk_design_matrix.py | complete | [docs/src/reversi/lm/wrk_design_matrix.md](docs/src/reversi/lm/wrk_design_matrix.md) |
| src/reversi/lm/wrk_features.py | complete | [docs/src/reversi/lm/wrk_features.md](docs/src/reversi/lm/wrk_features.md) |
| src/reversi/lm/wrk_final_log_print.py | complete | [docs/src/reversi/lm/wrk_final_log_print.md](docs/src/reversi/lm/wrk_final_log_print.md) |
| src/reversi/lm/wrk_generate.py | complete | [docs/src/reversi/lm/wrk_generate.md](docs/src/reversi/lm/wrk_generate.md) |
| src/reversi/lm/wrk_gradient.py | complete | [docs/src/reversi/lm/wrk_gradient.md](docs/src/reversi/lm/wrk_gradient.md) |
| src/reversi/lm/wrk_indexes.py | complete | [docs/src/reversi/lm/wrk_indexes.md](docs/src/reversi/lm/wrk_indexes.md) |
| src/reversi/lm/wrk_optimize.py | complete | [docs/src/reversi/lm/wrk_optimize.md](docs/src/reversi/lm/wrk_optimize.md) |
| src/reversi/lm/wrk_plot.py | complete | [docs/src/reversi/lm/wrk_plot.md](docs/src/reversi/lm/wrk_plot.md) |
| src/reversi/lm/wrk_positions.py | complete | [docs/src/reversi/lm/wrk_positions.md](docs/src/reversi/lm/wrk_positions.md) |
| src/reversi/lm/wrk_save.py | complete | [docs/src/reversi/lm/wrk_save.md](docs/src/reversi/lm/wrk_save.md) |
| src/reversi/lm/wrk_su_analysis.py | complete | [docs/src/reversi/lm/wrk_su_analysis.md](docs/src/reversi/lm/wrk_su_analysis.md) |
| src/reversi/lm/wrk_validate.py | complete | [docs/src/reversi/lm/wrk_validate.md](docs/src/reversi/lm/wrk_validate.md) |
| src/reversi/lm/wrk_vld_positions.py | complete | [docs/src/reversi/lm/wrk_vld_positions.md](docs/src/reversi/lm/wrk_vld_positions.md) |
| src/reversi/lm/wrk_wmaps.py | complete | [docs/src/reversi/lm/wrk_wmaps.md](docs/src/reversi/lm/wrk_wmaps.md) |
| src/reversi/lm/wrk_zed.py | complete | [docs/src/reversi/lm/wrk_zed.md](docs/src/reversi/lm/wrk_zed.md) |
| src/reversi/mobility.py | complete | [docs/src/reversi/mobility.md](docs/src/reversi/mobility.md) |
| src/reversi/pattern.py | complete | [docs/src/reversi/pattern.md](docs/src/reversi/pattern.md) |
| src/reversi/random_game.py | complete | [docs/src/reversi/random_game.md](docs/src/reversi/random_game.md) |
| src/reversi/regab.py | complete | [docs/src/reversi/regab.md](docs/src/reversi/regab.md) |
| src/reversi/tools/binio.py | complete | [docs/src/reversi/tools/binio.md](docs/src/reversi/tools/binio.md) |
| src/reversi/tools/cache_manager.py | complete | [docs/src/reversi/tools/cache_manager.md](docs/src/reversi/tools/cache_manager.md) |
| src/reversi/tools/opt_lbfgs.py | complete | [docs/src/reversi/tools/opt_lbfgs.md](docs/src/reversi/tools/opt_lbfgs.md) |
| src/reversi/tools/prng.py | complete | [docs/src/reversi/tools/prng.md](docs/src/reversi/tools/prng.md) |
| src/reversi/tools/state_machine.py | complete | [docs/src/reversi/tools/state_machine.md](docs/src/reversi/tools/state_machine.md) |

## Test files
One row per test file, alphabetical by full path. Suite (standard run) = the module's count under the standard
pre-commit run (LONG=1, the live DB) as `<total>/<failures>/<skipped>`; a (+N VLONG) marks the tier-gated tests that
skip in it.

| File | State | Suite (standard run) | Doc |
| --- | --- | --- | --- |
| test/reversi/lm/test_client.py | complete | 7/0/1 | [docs/test/reversi/lm/test_client.md](docs/test/reversi/lm/test_client.md) |
| test/reversi/lm/test_hlp_anova.py | complete | 16/0/0 | [docs/test/reversi/lm/test_hlp_anova.md](docs/test/reversi/lm/test_hlp_anova.md) |
| test/reversi/lm/test_hlp_config_schemas.py | complete | 30/0/0 | [docs/test/reversi/lm/test_hlp_config_schemas.md](docs/test/reversi/lm/test_hlp_config_schemas.md) |
| test/reversi/lm/test_hlp_design_matrix.py | complete | 14/0/0 | [docs/test/reversi/lm/test_hlp_design_matrix.md](docs/test/reversi/lm/test_hlp_design_matrix.md) |
| test/reversi/lm/test_hlp_generate.py | complete | 16/0/0 | [docs/test/reversi/lm/test_hlp_generate.md](docs/test/reversi/lm/test_hlp_generate.md) |
| test/reversi/lm/test_hlp_gradient.py | complete | 15/0/0 | [docs/test/reversi/lm/test_hlp_gradient.md](docs/test/reversi/lm/test_hlp_gradient.md) |
| test/reversi/lm/test_hlp_indexes.py | complete | 14/0/0 | [docs/test/reversi/lm/test_hlp_indexes.md](docs/test/reversi/lm/test_hlp_indexes.md) |
| test/reversi/lm/test_hlp_optimize.py | complete | 20/0/0 | [docs/test/reversi/lm/test_hlp_optimize.md](docs/test/reversi/lm/test_hlp_optimize.md) |
| test/reversi/lm/test_hlp_plot.py | complete | 11/0/0 | [docs/test/reversi/lm/test_hlp_plot.md](docs/test/reversi/lm/test_hlp_plot.md) |
| test/reversi/lm/test_hlp_su_analysis.py | complete | 38/0/0 | [docs/test/reversi/lm/test_hlp_su_analysis.md](docs/test/reversi/lm/test_hlp_su_analysis.md) |
| test/reversi/lm/test_hlp_wmaps.py | complete | 15/0/0 | [docs/test/reversi/lm/test_hlp_wmaps.md](docs/test/reversi/lm/test_hlp_wmaps.md) |
| test/reversi/lm/test_hlp_zed.py | complete | 10/0/0 | [docs/test/reversi/lm/test_hlp_zed.md](docs/test/reversi/lm/test_hlp_zed.md) |
| test/reversi/lm/test_lm_worker_full_chain.py | complete | 9/0/1 (+1 VLONG) | [docs/test/reversi/lm/test_lm_worker_full_chain.md](docs/test/reversi/lm/test_lm_worker_full_chain.md) |
| test/reversi/lm/test_logistic_model.py | complete | 29/0/0 | [docs/test/reversi/lm/test_logistic_model.md](docs/test/reversi/lm/test_logistic_model.md) |
| test/reversi/lm/test_wrk_analytics.py | complete | 14/0/0 | [docs/test/reversi/lm/test_wrk_analytics.md](docs/test/reversi/lm/test_wrk_analytics.md) |
| test/reversi/lm/test_wrk_anova.py | complete | 7/0/0 | [docs/test/reversi/lm/test_wrk_anova.md](docs/test/reversi/lm/test_wrk_anova.md) |
| test/reversi/lm/test_wrk_client_check.py | complete | 6/0/0 | [docs/test/reversi/lm/test_wrk_client_check.md](docs/test/reversi/lm/test_wrk_client_check.md) |
| test/reversi/lm/test_wrk_config.py | complete | 13/0/0 | [docs/test/reversi/lm/test_wrk_config.md](docs/test/reversi/lm/test_wrk_config.md) |
| test/reversi/lm/test_wrk_design_matrix.py | complete | 3/0/0 | [docs/test/reversi/lm/test_wrk_design_matrix.md](docs/test/reversi/lm/test_wrk_design_matrix.md) |
| test/reversi/lm/test_wrk_features.py | complete | 3/0/0 | [docs/test/reversi/lm/test_wrk_features.md](docs/test/reversi/lm/test_wrk_features.md) |
| test/reversi/lm/test_wrk_final_log_print.py | complete | 6/0/0 | [docs/test/reversi/lm/test_wrk_final_log_print.md](docs/test/reversi/lm/test_wrk_final_log_print.md) |
| test/reversi/lm/test_wrk_generate.py | complete | 3/0/0 | [docs/test/reversi/lm/test_wrk_generate.md](docs/test/reversi/lm/test_wrk_generate.md) |
| test/reversi/lm/test_wrk_gradient.py | complete | 4/0/0 | [docs/test/reversi/lm/test_wrk_gradient.md](docs/test/reversi/lm/test_wrk_gradient.md) |
| test/reversi/lm/test_wrk_indexes.py | complete | 2/0/0 | [docs/test/reversi/lm/test_wrk_indexes.md](docs/test/reversi/lm/test_wrk_indexes.md) |
| test/reversi/lm/test_wrk_optimize.py | complete | 3/0/0 | [docs/test/reversi/lm/test_wrk_optimize.md](docs/test/reversi/lm/test_wrk_optimize.md) |
| test/reversi/lm/test_wrk_plot.py | complete | 9/0/0 | [docs/test/reversi/lm/test_wrk_plot.md](docs/test/reversi/lm/test_wrk_plot.md) |
| test/reversi/lm/test_wrk_positions.py | complete | 12/0/0 | [docs/test/reversi/lm/test_wrk_positions.md](docs/test/reversi/lm/test_wrk_positions.md) |
| test/reversi/lm/test_wrk_su_analysis.py | complete | 10/0/1 (+1 VLONG) | [docs/test/reversi/lm/test_wrk_su_analysis.md](docs/test/reversi/lm/test_wrk_su_analysis.md) |
| test/reversi/lm/test_wrk_validate.py | complete | 9/0/0 | [docs/test/reversi/lm/test_wrk_validate.md](docs/test/reversi/lm/test_wrk_validate.md) |
| test/reversi/lm/test_wrk_vld_positions.py | complete | 11/0/0 | [docs/test/reversi/lm/test_wrk_vld_positions.md](docs/test/reversi/lm/test_wrk_vld_positions.md) |
| test/reversi/lm/test_wrk_wmaps.py | complete | 3/0/0 | [docs/test/reversi/lm/test_wrk_wmaps.md](docs/test/reversi/lm/test_wrk_wmaps.md) |
| test/reversi/lm/test_wrk_zed.py | complete | 3/0/0 | [docs/test/reversi/lm/test_wrk_zed.md](docs/test/reversi/lm/test_wrk_zed.md) |
| test/reversi/paths.py | complete (helper module, 0 tests) | — | [docs/test/reversi/paths.md](docs/test/reversi/paths.md) |
| test/reversi/tags.py | complete (helper module, 0 tests) | — | [docs/test/reversi/tags.md](docs/test/reversi/tags.md) |
| test/reversi/test_board.py | complete | 247/0/15 | [docs/test/reversi/test_board.md](docs/test/reversi/test_board.md) |
| test/reversi/test_feature.py | complete | 25/0/1 | [docs/test/reversi/test_feature.md](docs/test/reversi/test_feature.md) |
| test/reversi/test_mobility.py | complete | 26/0/1 | [docs/test/reversi/test_mobility.md](docs/test/reversi/test_mobility.md) |
| test/reversi/test_paths.py | complete | 3/0/0 | [docs/test/reversi/test_paths.md](docs/test/reversi/test_paths.md) |
| test/reversi/test_pattern.py | complete | 65/0/3 | [docs/test/reversi/test_pattern.md](docs/test/reversi/test_pattern.md) |
| test/reversi/test_random_game.py | complete | 33/0/1 | [docs/test/reversi/test_random_game.md](docs/test/reversi/test_random_game.md) |
| test/reversi/test_regab.py | complete | 48/0/0 | [docs/test/reversi/test_regab.md](docs/test/reversi/test_regab.md) |
| test/reversi/tools/test_binio.py | complete | 45/0/0 | [docs/test/reversi/tools/test_binio.md](docs/test/reversi/tools/test_binio.md) |
| test/reversi/tools/test_cache_manager.py | complete | 22/0/0 | [docs/test/reversi/tools/test_cache_manager.md](docs/test/reversi/tools/test_cache_manager.md) |
| test/reversi/tools/test_opt_lbfgs.py | complete | 14/0/0 | [docs/test/reversi/tools/test_opt_lbfgs.md](docs/test/reversi/tools/test_opt_lbfgs.md) |
| test/reversi/tools/test_prng.py | complete | 22/0/0 | [docs/test/reversi/tools/test_prng.md](docs/test/reversi/tools/test_prng.md) |
| test/reversi/tools/test_state_machine.py | complete | 50/0/0 | [docs/test/reversi/tools/test_state_machine.md](docs/test/reversi/tools/test_state_machine.md) |
| test/reversi/tools/test_usage_binio.py | complete | 3/0/0 | [docs/test/reversi/tools/test_usage_binio.md](docs/test/reversi/tools/test_usage_binio.md) |

Test data (test/reversi/data/):

- `ffo_12_log_sample.csv` — the FFO-12 legacy C solve-log sample (the `position_hash` parity fixture, the deterministic
  1002-row stride — 1003 lines incl. the header)
- `prng_golden.txt` — the committed PRNG golden (the 18436 lines, the 20 sections)
- `rlm_00.json` — the JSON5 unit-test config (the base rlm_00 fixture of the NO-DB mock-ctx suites)
- `rlm_01.json` — the unit-test config (the Design Matrix data structure)
- `rlm_02.json` — the unit-test config (the gradient worker)
- `rlm_03.json` — the LONG-tier full-worker-chain config (the A2050 feature set)
- `rlm_04.json` — the shorter full-worker-chain config (EDGE + MOBILITY)
- `rlm_05.json` — the SU-analysis experiment config (the 2M corpus, ec 20, stops at SU_ANALYSIS)
- `rlm_06.json` — the SU-analysis experiment config (the 100M tier, ec 20)

## Index
The docs/ mirrors (one per source/test file, D-007) are NOT listed here: their paths are the Doc column of the two
tables above.

- notes/naming.md — canonical board naming convention (row/column, D-013; D8 symmetries, D-014)
- notes/rules.md — active legislation ("legislative body"): the register of the rules in force, R-NNN-numbered (a bold
  title + a 1–3 line description, origin D-number; added/amended/retired only on explicit user approval)
- notes/decisions.md — open historical decision log (append-only, D-NNN; the rules in force live in notes/rules.md;
  closed volumes: decisions_NNN.md)
- notes/decisions_000.md — closed decision volume 000 (D-001…D-116, 2026-08-25 → 2026-09-06)
- notes/decisions_001.md — closed decision volume 001 (D-117…D-158, 2026-09-06 → 2026-09-11)
- notes/decisions_002.md — closed decision volume 002 (D-159…D-206, 2026-09-11 → 2026-09-15, the D-333 rotation)
- notes/decisions_003.md — closed decision volume 003 (D-207…D-257, 2026-09-15 → 2026-09-19, the D-333 rotation)
- notes/decisions_004.md — closed decision volume 004 (D-258…D-300, 2026-09-19 → 2026-09-23, the D-333 rotation)
- notes/decisions_005.md — closed decision volume 005 (D-301…D-332, 2026-09-23 → 2026-09-29, the D-333 rotation)
- notes/analyses/ — archived one-off investigations + the classification + the extracted verbatim reviews + the
  historical project docs (the historical/ subdir: the I-017 project plan — analytical_properties_of_features.md, the
  wave-tier performance baseline — performance_baseline.md, the ODP-9 material)
- notes/ideas.md — the OPEN backlog (I-NNN, D-235)
- notes/ideas-closed.md — the CLOSED ideas (done | dropped): the compacted I-NNN record (D-235)
- notes/log_rules.md — session-journal format rules (rigid; global session numbering; volume rotation: 25 sessions /
  2000 lines per volume, only at session boundaries)
- notes/docs_rules.md — mirror-doc format rules (rigid; the current-state contract)
- notes/tools.md — the workspace-tool rules (the four requirements + the inventory, D-248/D-249)
- notes/probe_rules.md — verification-apparatus rules (rigid; the a/b/c classification + the independent-derivation
  criterion, the test/probe line, the pipeline-state centralization in the hub, the campaign sweep rule, the archive to
  notes/analyses/, the baseline)
- notes/log_000.md — session journal, volume 000 (sessions 1–24, closed 2026-09-01)
- notes/log_001.md — session journal, volume 001 (sessions 25–30, closed 2026-09-08)
- notes/log_002.md — session journal, volume 002 (sessions 31–37, closed 2026-09-18)
- notes/log_003.md — session journal, volume 003 (sessions 38–89, closed 2026-09-29)
- notes/log_004.md — session journal, volume 004 (sessions 90–..., open)
