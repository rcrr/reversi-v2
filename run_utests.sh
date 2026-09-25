#!/usr/bin/env bash
#
# run_utests.sh — the unit-test suite (test.reversi) in canonical order (D-130).
#
# Usage:
#   ./run_utests.sh              fast tier (no DB)
#   PERF=1 ./run_utests.sh       + the print-only performance tests
#   LONG=1 ./run_utests.sh       + the DB-gated pipeline tests
#   VLONG=1 ./run_utests.sh      + the long instruments (the A2050 chain)
#   VVLONG=1 ./run_utests.sh     + the very-long ones (currently
#                                  uninstrumented — D-285)
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
    test.reversi.tools.test_binio
    test.reversi.tools.test_usage_binio
    test.reversi.tools.test_opt_lbfgs
    test.reversi.tools.test_prng
    # 1 — board & pattern concepts
    test.reversi.test_board
    test.reversi.test_random_game
    test.reversi.test_pattern
    test.reversi.test_mobility
    test.reversi.test_feature
    # 2 — infrastructure
    test.reversi.tools.test_cache_manager
    test.reversi.tools.test_state_machine
    test.reversi.lm.test_logistic_model
    test.reversi.test_paths
    # 3 — DB access
    test.reversi.test_regab
    # 4 — the pipeline, machine order 1-16 (each data module
    #     immediately before its worker; the 17-level end-to-end
    #     chain — including SAVE + CLIENT_CHECK + PLOT — last)
    test.reversi.lm.test_hlp_config_schemas
    test.reversi.lm.test_wrk_config
    test.reversi.lm.test_wrk_features
    # test_hlp_feature_analysis: the ANOVA analysis kernels
    # (the I-017; the D-298 split — the ANOVA T13, the adherence
    # T14 + its private kl / TV / chi-square helpers)
    test.reversi.lm.test_hlp_feature_analysis
    # test_hlp_su_analysis: the SU analysis LOGIC (D-289: the
    # signature, the binio I/O D-288, the compute determinism, the
    # theoretical space D-278/279, the SU groups, the report/CSV) +
    # the frequency accumulators (the D-295 test_hlp_random_play
    # migration: the marginal / the joint + the PRNG integration) +
    # the SU kernel micro-suite (the D-298 hlp_feature_analysis
    # migration: the T11 / T12 entropy-MI-SU / dispersion-audit)
    test.reversi.lm.test_hlp_su_analysis
    # test_wrk_su_analysis: the SU_ANALYSIS worker
    # (the I-017 T16; the SU-analysis corpus cache + the phase-2
    # statistics + the reports)
    test.reversi.lm.test_wrk_su_analysis
    test.reversi.lm.test_wrk_positions
    test.reversi.lm.test_hlp_indexes
    test.reversi.lm.test_wrk_indexes
    # test_wrk_anova: the ANOVA worker (the I-017
    # T17; the eta²/omega² + the adherence, the graceful
    # degradation; the step 6 position, after INDEXES)
    test.reversi.lm.test_wrk_anova
    test.reversi.lm.test_hlp_wmaps
    test.reversi.lm.test_wrk_wmaps
    test.reversi.lm.test_hlp_design_matrix
    test.reversi.lm.test_wrk_design_matrix
    test.reversi.lm.test_hlp_zed
    test.reversi.lm.test_wrk_zed
    test.reversi.lm.test_hlp_gradient
    test.reversi.lm.test_wrk_gradient
    test.reversi.lm.test_hlp_optimize
    test.reversi.lm.test_wrk_optimize
    test.reversi.lm.test_hlp_generate
    test.reversi.lm.test_wrk_generate
    test.reversi.lm.test_wrk_vld_positions
    test.reversi.lm.test_wrk_validate
    test.reversi.lm.test_wrk_analytics
    test.reversi.lm.test_client
    test.reversi.lm.test_wrk_client_check
    test.reversi.lm.test_hlp_plot
    test.reversi.lm.test_wrk_plot
    test.reversi.lm.test_lm_worker_full_chain
)

exec python -m unittest "${MODULES[@]}"
