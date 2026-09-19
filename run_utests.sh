#!/usr/bin/env bash
#
# run_utests.sh — the reversi.test suite in canonical order (D-130).
#
# Usage:
#   ./run_utests.sh              fast tier (no DB)
#   PERF=1 ./run_utests.sh       + the print-only performance tests
#   LONG=1 ./run_utests.sh       + the DB-gated pipeline tests
#   VLONG=1 ./run_utests.sh      + the long instruments (the A2050 chain)
#   VVLONG=1 ./run_utests.sh     + the very-long ones (the 1e6 benchmark)
#   SKIP_REGAB_DB=1 ...          no-DB environment: every DB test is
#                                skipped whatever the tier
#
# The tiers are CUMULATIVE (D-256): VVLONG=1 implies VLONG -> LONG.
# The PERF / LONG / VLONG / VVLONG / SKIP_REGAB_DB variables are
# inherited by the test process as-is. The module order is
# the canonical one (D-130): a new test module is inserted here at
# its logical position — never appended at the end.
#
set -euo pipefail
cd "$(dirname "$0")"
source .venv/bin/activate

echo "run_utests: PERF=${PERF:-0} LONG=${LONG:-0} VLONG=${VLONG:-0} SKIP_REGAB_DB=${SKIP_REGAB_DB:-0}"

MODULES=(
    # 0 — tools
    reversi.test.test_binio
    reversi.test.test_usage_binio
    reversi.test.test_opt_lbfgs
    reversi.test.test_prng
    # 1 — board & pattern concepts
    reversi.test.test_board
    reversi.test.test_random_game
    reversi.test.test_pattern
    reversi.test.test_mobility
    reversi.test.test_feature
    # 2 — infrastructure
    reversi.test.test_cache_manager
    reversi.test.test_state_machine
    reversi.test.test_logistic_model
    reversi.test.test_paths
    # 3 — DB access
    reversi.test.test_regab
    # 4 — the pipeline, machine order 1-16 (each data module
    #     immediately before its worker; the 17-level end-to-end
    #     chain — including SAVE + CLIENT_CHECK + PLOT — last)
    # test_hlp_random_play: the T12-level data module (the worker
    # lands in T12; the ODP-9 pick table + the single-game loop
    # land here at T4)
    reversi.test.test_hlp_random_play
    # test_hlp_wave: the T5 numba wave engine (the corpus
    # engine, the I-017 SU-analysis generator)
    reversi.test.test_hlp_wave
    reversi.test.test_hlp_config_schemas
    reversi.test.test_wrk_config
    reversi.test.test_wrk_features
    # test_hlp_feature_analysis: the SHARED analysis kernels
    # (the I-017; the SU/entropy/MI kernels T11, the
    # dispersion/audit T12, the ANOVA T13, the adherence T14)
    reversi.test.test_hlp_feature_analysis
    # test_wrk_su_analysis: the SU_ANALYSIS worker
    # (the I-017 T16; the SU-analysis corpus cache + the phase-2
    # statistics + the reports)
    reversi.test.test_wrk_su_analysis
    reversi.test.test_wrk_positions
    reversi.test.test_hlp_indexes
    reversi.test.test_wrk_indexes
    # test_wrk_effect_size: the EFFECT_SIZE worker (the I-017
    # T17; the eta²/omega² + the adherence, the graceful
    # degradation; the step 6 position, after INDEXES)
    reversi.test.test_wrk_effect_size
    reversi.test.test_hlp_wmaps
    reversi.test.test_wrk_wmaps
    reversi.test.test_hlp_design_matrix
    reversi.test.test_wrk_design_matrix
    reversi.test.test_hlp_zed
    reversi.test.test_wrk_zed
    reversi.test.test_hlp_gradient
    reversi.test.test_wrk_gradient
    reversi.test.test_hlp_optimize
    reversi.test.test_wrk_optimize
    reversi.test.test_hlp_generate
    reversi.test.test_wrk_generate
    reversi.test.test_wrk_vld_positions
    reversi.test.test_wrk_validate
    reversi.test.test_wrk_analytics
    reversi.test.test_client
    reversi.test.test_wrk_client_check
    reversi.test.test_hlp_plot
    reversi.test.test_wrk_plot
    reversi.test.test_lm_worker_full_chain
)

exec python -m unittest "${MODULES[@]}"
