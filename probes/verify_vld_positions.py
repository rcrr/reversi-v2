#!/usr/bin/env python3
"""
verify_vld_positions.py — scratch probe for the VLD_POSITIONS bring-in
(session 28, Roberto's commit ede2efe — the 12th pipeline level).

Re-derives and verifies, independently of the test files (there are
none — the bring-in has no test file, T6):
  A. wrk_vld_positions.py structure (pinned to the post-campaign
     expectations: R1 the _for_current_level naming, T2 the factory
     gate, T3 the dead imports, T4 the load_fn checksum=False shape,
     T5 the 3 ws-only lines)
  B. context facts (the LMContext pre-declared vld fields, the
     ValidationDataSetConfig schema)
  C. GOLDEN re-derivation (live DB, gated on SKIP_REGAB_DB): the
     rlm_02.json pipeline to VLD_POSITIONS — the pre-campaign R1
     crash demo + the alias-simulation fallback, the vld stats
     goldens, the rlmwf_11_VLD_POSITIONS.dat flat file + sidecar,
     the second-instance cache hit, the _down scope
  D. unit facts (no DB): the worker factory, the reused
     is_cache_consistent override semantics (SimpleNamespace)

Run from the workspace root:  .venv/bin/python probes/verify_vld_positions.py
"""
import os
import sys
import tempfile
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS))  # the root test/ tree (the test.reversi helpers)
SRC = WS / "src" / "reversi"

failures = []
skipped = []


def check(label, cond, detail=""):
    print(f"[{'ok  ' if cond else 'FAIL'}] {label}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(label)


def skip(label, detail=""):
    print(f"[skip] {label}" + (f" — {detail}" if detail else ""))
    skipped.append(label)


def read(p):
    return (WS / p).read_text()


def lines(p):
    return read(p).splitlines()


def ws_lines(p):
    """Non-comment lines with trailing whitespace (license-header '# ' lines exempt)."""
    return [i + 1 for i, ln in enumerate(lines(p))
            if ln.endswith((" ", "\t")) and not ln.lstrip().startswith("#")]


# ----------------------------------------------------------------------
# A. wrk_vld_positions.py structure
# ----------------------------------------------------------------------
wk_src = read("src/reversi/lm/wrk_vld_positions.py")
check("A1 Worker named VLD_POSITIONS + __all__",
      'Worker("VLD_POSITIONS", _up, _down)' in wk_src
      and "__all__ = ['wrk_vld_positions']" in wk_src)
check("A2 the worker uses the house name _for_current_level (the "
      "_for_next_level call is the R1 AttributeError)",
      "get_cache_file_full_path_for_current_level" in wk_src
      and "for_next_level" not in wk_src)
check("A3 the factory is @validate_call-decorated + pydantic imported "
      "(all 10 sibling worker factories — D-092 T2 / D-096 T10 / D-098 T3 pattern)",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef wrk_vld_positions" in wk_src
      and "from pydantic import validate_call, ConfigDict" in wk_src)
check("A4 load_fn passes checksum=False (no double sidecar verify)",
      "lambda path: regab_load_data_set_from_file(path, checksum=False)" in wk_src)
check("A5 no dead imports (the file delegates extraction to wrk_positions.extract_and_prepare, D-143)",
      "from pathlib import Path" not in wk_src
      and "RegabDataSet" not in wk_src
      and "RegabDBConnection" not in wk_src
      and "regab_extract_data_set_from_db" not in wk_src
      and "regab_load_data_set_from_file" in wk_src
      and "regab_store_data_set_to_file" in wk_src)
_vld_ws = ws_lines("src/reversi/lm/wrk_vld_positions.py")
check("A6 no code ws lines (the import-block line swept in the cascade "
      "formatting pass, as in wrk_positions)",
      _vld_ws == [],
      f"lines {_vld_ws}")
check("A7 reuses extract_and_prepare + is_cache_consistent from wrk_positions "
      "(D-143: the vld compute path is the shared extract-and-prepare; "
      "load_from_db lives inside it)",
      "from reversi.lm.wrk_positions import extract_and_prepare, is_cache_consistent" in wk_src)
check("A8 the vld query params are passed to BOTH the compute and the validate fns",
      "is_cache_consistent(ctx, cached_vld_rds, bid=vld_cfg.bid, status=vld_cfg.status)" in wk_src
      and "extract_and_prepare(ctx, bid=vld_cfg.bid, status=vld_cfg.status)" in wk_src)

# ----------------------------------------------------------------------
# B. context facts (the B1-B3 pipeline-state pins moved to the hub
# verify_logistic_model.py V3c/V3d at D-106)
# ----------------------------------------------------------------------
lm_src = read("src/reversi/lm/logistic_model.py")
check("B4 LMContext pre-declared vld fields (vld_rds_checksum, vld_positions, "
      "vld_game_values, vld_pop_stats) + the future vld_metrics / analytics_report",
      "    vld_rds_checksum: str | None = None" in lm_src
      and "    vld_positions: Any = None" in lm_src
      and "    vld_game_values: Any = None" in lm_src
      and "    vld_pop_stats: Any = None" in lm_src
      and "    vld_metrics: Any = None" in lm_src
      and "    analytics_report: Any = None" in lm_src)
sc_src = read("src/reversi/lm/hlp_config_schemas.py")
check("B5 LMConfig.validation_data_set: ValidationDataSetConfig "
      "(bid: List[NonNegativeInt] + status: List[StatusString], no ec field — "
      "the vld query inherits ec from regab_data_set)",
      "validation_data_set: ValidationDataSetConfig" in sc_src
      and "class ValidationDataSetConfig(LMBaseConfig):" in sc_src
      and "bid: List[NonNegativeInt]" in sc_src
      and "status: List[StatusString]" in sc_src
      and "ec" not in sc_src.split("class ValidationDataSetConfig")[1].split("class ")[0])

# ----------------------------------------------------------------------
# C. GOLDEN re-derivation (live DB) — the rlm_02.json pipeline
# ----------------------------------------------------------------------
if os.getenv("SKIP_REGAB_DB", "0") == "1":
    skip("C-tier (live DB golden re-derivation)", "SKIP_REGAB_DB=1")
else:
    from reversi.lm.logistic_model import LogisticModel
    from reversi.tools.state_machine import Verbosity
    from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE

    CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
        tmp = Path(tmp)
        cfg_path = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_02.json")

        def make_model(aliased: bool, verbosity=Verbosity.LOW):
            m = LogisticModel(cfg_path, verbosity=verbosity, base_dir_override=tmp)
            if aliased:
                # the pre-campaign R1 alias simulation: bind the missing
                # _for_next_level name to the injected _for_current_level
                # closure so the level can run at all.
                m.context.get_cache_file_full_path_for_next_level = \
                    m.context.get_cache_file_full_path_for_current_level
            return m

        crashed = False
        try:
            m = make_model(aliased=False)
            m.move_to_step("VLD_POSITIONS")
        except AttributeError:
            crashed = True
            # (C1 deleted at D-106 step 3, class c: reaching
            #  VLD_POSITIONS / step 11 is pinned by test_lm_worker_
            #  vld_positions.py — test_compute_and_populate_cache,
            #  test_read_cache_on_new_instance, and the down test.
            #  This branch is dead on the current pipeline: the R1
            #  AttributeError no longer happens.)
        if crashed:
            print("     alias simulation: binding _for_next_level -> _for_current_level "
                  "and retrying on a fresh instance (same base dir)...")
            m = make_model(aliased=True)
            m.move_to_step("VLD_POSITIONS")
        ctx = m.context

        # (C2 deleted at D-106 step 3, class c: the structural facts —
        #  dtype.names ("mover", "opponent"), 1-D game values, the
        #  checksum, and the stats-dict keys — are pinned by
        #  test_compute_and_populate_cache; the exact 4-key set stays
        #  pinned here by C3b, which indexes all four keys)

        # C3 the stats goldens (independent re-derivation from the raw arrays)
        n_pos = len(ctx.vld_positions)
        n_gv = len(ctx.vld_game_values)
        s = ctx.vld_pop_stats
        check("C3a count == len(vld_positions) == len(vld_game_values)",
              s["count"] == n_pos == n_gv,
              f"count={s['count']} positions={n_pos} game_values={n_gv}")
        mean = float(np.mean(ctx.vld_game_values))
        std_dev = float(np.std(ctx.vld_game_values))
        variance = float(np.var(ctx.vld_game_values))
        check("C3b vld_pop_stats mean/std/var == the independent float64 re-derivation",
              float(s["mean"]) == mean and float(s["std_dev"]) == std_dev
              and float(s["variance"]) == variance,
              f"stats={ (s['mean'], s['std_dev'], s['variance']) } vs re-derived=({mean}, {std_dev}, {variance})")
        check("C3c the live vld golden (bid [8], CMS+CMR, ec 20): count 200, "
              "mean 3.64, std 23.809880302093077, variance 566.9104",
              s["count"] == 200 and mean == 3.64
              and std_dev == 23.809880302093077 and variance == 566.9104,
              f"count={s['count']} mean={mean} std={std_dev} var={variance}")
        check("C3d the live vld golden: vld_rds_checksum e8087903...f4c48 "
              "(distinct from the training 32da0ed3...) + int8 game values in [-58, 56]",
              ctx.vld_rds_checksum
              == "e8087903437d9d42d64499626f5b4426505d3b9538539e19fb8f45dc9c9f4c48"
              and ctx.vld_game_values.dtype == np.int8
              and ctx.vld_game_values.min() == -58 and ctx.vld_game_values.max() == 56)
        check("C4 the vld rds checksum differs from the training rds checksum "
              "(two distinct data sets, two distinct cache files)",
              ctx.vld_rds_checksum != ctx.rds_checksum)

        # (C5 deleted at D-106 step 3, class c: both flat files + the
        #  sidecar verify are pinned by test_compute_and_populate_cache)

        # (C6 deleted at D-106 step 3, class c: the cache hit + no
        #  re-extraction + data identity (assert_array_equal +
        #  checksum) are pinned by test_read_cache_on_new_instance)
        # (C7 deleted at D-106 step 3, class c: the _down scope is
        #  pinned by test_down_clears_vld_positions_attributes)


# ----------------------------------------------------------------------
# D. unit facts (no DB)
# ----------------------------------------------------------------------
from reversi.lm.wrk_vld_positions import wrk_vld_positions
from reversi.lm.wrk_positions import is_cache_consistent, load_from_db, extract_and_prepare

w = wrk_vld_positions()
check("D1 the factory returns a Worker named VLD_POSITIONS with up/down callables",
      w.name == "VLD_POSITIONS" and callable(w.up) and callable(w.down))


# (D2-D7 moved to tests at D-106 step 3, class a §4 conversion:
#  test_wrk_vld_positions.py::TestIsCacheConsistentOverride —
#  the SimpleNamespace stand-ins for the context and the cached rds
#  come along; the test runs under SKIP_REGAB_DB=1 (no DB). D8 keeps
#  the reuse-identity pin here.)
check("D8 load_from_db + extract_and_prepare + is_cache_consistent are the reused "
      "wrk_positions functions (identity, not re-implementations; D-143: "
      "extract_and_prepare is the shared compute path)",
      load_from_db.__module__ == "reversi.lm.wrk_positions"
      and extract_and_prepare.__module__ == "reversi.lm.wrk_positions"
      and is_cache_consistent.__module__ == "reversi.lm.wrk_positions")


# ----------------------------------------------------------------------
print()
if skipped:
    print(f"{len(skipped)} check(s) skipped (gated).")
if failures:
    print(f"{len(failures)} mismatch(es):")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("All checks passed.")
