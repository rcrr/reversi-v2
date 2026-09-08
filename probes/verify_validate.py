#!/usr/bin/env python3
"""
verify_validate.py — scratch probe for the VALIDATE bring-in
(session 28, Roberto's commit 536eadc — the 13th pipeline level,
the first bring-in with a dedicated data module rlm_validate).

Re-derives and verifies, independently of the test files (there
are none — the bring-in has no test file, T5):
  A. lm_worker_validate.py + rlm_validate.py structure (pinned to
     the post-campaign expectations: R1 the unimported `Any`
     annotation, T1 the factory gate, T2 the dead imports, T3 the
     wrong header name, T4 the ws lines, T5 the missing test file)
  B. context facts (the RLMContext pre-declared vld_metrics /
     analytics_report fields)
  C. GOLDEN re-derivation (live DB, gated on SKIP_REGAB_DB): the
     rlm_02.json pipeline to VALIDATE (step 12) — the 6-metric
     goldens, the log lines, the no-cache-file fact, the
     second-instance determinism, the _down scope
  D. unit facts (no DB): the full metric math on a hand-computed
     2-position case (SimpleNamespace), the float() types, the
     worker's ratio-line ZeroDivisionError demo on a perfect
     Y-space fit (M1)

Run from the workspace root:  .venv/bin/python scratch/verify_validate.py
"""
import contextlib
import io
import math
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import numpy as np

WS = Path(__file__).resolve().parents[1]
SRC = WS / "src" / "twolm"

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
# A. lm_worker_validate.py + rlm_validate.py structure
# ----------------------------------------------------------------------
wk_src = read("src/twolm/lm_worker_validate.py")
dv_src = read("src/twolm/rlm_validate.py")
check("A1 Worker named VALIDATE + __all__ + validate_model the single public data name",
      'Worker("VALIDATE", _up, _down)' in wk_src
      and "__all__ = ['lm_worker_validate']" in wk_src
      and "__all__ = ['validate_model']" in dv_src)
check("A2 the factory is @validate_call-decorated + pydantic imported "
      "(all 11 sibling worker factories — the D-100 T1 pattern)",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef lm_worker_validate" in wk_src
      and "from pydantic import validate_call, ConfigDict" in wk_src)
check("A3 no dead import in the worker (`numpy as np` is never used)",
      "import numpy as np" not in wk_src)
check("A4 no dead import in rlm_validate (RegabDBConnection + "
      "regab_extract_data_set_from_db are never used — the data comes from "
      "ctx.vld_positions / ctx.vld_game_values, set by VLD_POSITIONS)",
      "RegabDBConnection" not in dv_src
      and "regab_extract_data_set_from_db" not in dv_src)
_typing_line = dv_src.split("from typing import")[1].split("\n")[0]
check("A5 the `Any` in the `Dict[str, Any]` return annotation is imported "
      "(R1: pre-campaign it is not — a PEP 563-masked latent NameError, nothing "
      "calls get_type_hints on validate_model today; the D-074 R2 class)",
      "Any" in _typing_line or "-> Dict[str, Any]:" not in dv_src,
      f"typing line: {repr(_typing_line)}")
check("A6 the rlm_validate header carries its OWN name (the bring-in says "
      "rlm_config_schemas.py — copy-paste)",
      lines("src/twolm/rlm_validate.py")[1] == "# rlm_validate.py")
_wk_ws = ws_lines("src/twolm/lm_worker_validate.py")
_dv_ws = ws_lines("src/twolm/rlm_validate.py")
check("A7a the worker has no code ws lines (pre-campaign: L48/L49/L51 — the 2 "
      "ws-only + the trailing on the validate_model call)",
      _wk_ws == [], f"lines {_wk_ws}")
check("A7b rlm_validate has no code ws lines (pre-campaign: 27 lines — the "
      "docstring trailing ws + the docstring ws-only lines + L108/L118)",
      _dv_ws == [], f"lines {_dv_ws}")
check("A8 a test file exists for the worker (pre-campaign: absent — T5)",
      (WS / "src" / "twolm" / "test" / "test_lm_worker_validate.py").exists())
check("A9 the _down scope clears exactly the ONE field _up sets (vld_metrics)",
      "ctx.vld_metrics = None" in wk_src
      and wk_src.count("ctx.vld_metrics = None") == 1
      and "ctx.vld_metrics = metrics" in wk_src)
check("A10 rlm_validate REUSES sigmoid from rlm_gradient (defined + exported there)",
      "from reversi.lm.hlp_gradient import sigmoid" in dv_src
      and "def sigmoid(x: np.ndarray) -> np.ndarray:" in read("src/reversi/lm/hlp_gradient.py")
      and "'sigmoid'" in read("src/reversi/lm/hlp_gradient.py").split("__all__ = ")[1].split("]")[0])
check("A11 the worker uses NO cache_manager (VALIDATE is pure compute — like "
      "FEATURES / ZED / GRADIENT; the rlmwf_12 slot stays unused)",
      "cache_manager" not in wk_src and "cache_manager" not in dv_src)
check("A12 the returned dict has exactly the 7 keys (post D-102 M3: vld_mse_y "
      "added — mse_y was computed but omitted pre-campaign; the worker consumes all 7)",
      set(dv_src.split("return {")[1].split("}")[0].split("'")[1::2])
      == {"vld_loss", "vld_mse_z", "vld_mae_z", "vld_mae_y", "vld_mse_y",
          "vld_rmse_y", "vld_samples"})
check("A13 the unused vld_indexes.shape[1] is underscore-unpacked (M2, D-102; "
      "the D-096 M1 pattern)",
      "vld_M, _ = vld_indexes.shape" in dv_src
      and "vld_P" not in dv_src)

# ----------------------------------------------------------------------
# B. context facts (the B1-B3 pipeline-state pins moved to the hub
# verify_logistic_model.py V3c/V3d at D-106)
# ----------------------------------------------------------------------
lm_src = read("src/twolm/logistic_model.py")
check("B4 RLMContext pre-declared vld_metrics (the future analytics_report)",
      "    vld_metrics: Any = None" in lm_src
      and "    analytics_report: Any = None" in lm_src)

# ----------------------------------------------------------------------
# C. GOLDEN re-derivation (live DB) — the rlm_02.json pipeline to VALIDATE
# ----------------------------------------------------------------------
if os.getenv("SKIP_REGAB_DB", "0") == "1":
    skip("C-tier (live DB golden re-derivation)", "SKIP_REGAB_DB=1")
else:
    from twolm.logistic_model import LogisticModel
    from reversi.tools.state_machine import Verbosity
    from reversi.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE

    CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
        tmp = Path(tmp)
        cfg_path = str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_02.json")

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            m = LogisticModel(cfg_path, verbosity=Verbosity.HIGH, base_dir_override=tmp)
            m.move_to_step("VALIDATE")
        out = buf.getvalue()
        ctx = m.context

        # (C1 deleted at D-106 step 3, class c: step 12 / VALIDATE is
        #  pinned by all three test_lm_worker_validate.py tests)
        met = ctx.vld_metrics
        # (C2 deleted at D-106 step 3, class c: the 7-key dict + all
        #  7 exact goldens are pinned by test_validate_model_goldens)
        # (C3 deleted at D-106 step 3, class c: all 5 log lines are
        #  pinned by test_validate_model_goldens)
        # C4 the internal consistency (independent re-derivation from the ctx arrays)
        vld_z = ctx.y2z(ctx.vld_game_values)
        check("C4 internal consistency: mse_z == 2*vld_loss, mae_y <= rmse_y "
              "(Jensen), rmse_y^2 ~ mse_y, vld_samples == len(vld_positions) == "
              "len(vld_game_values), vld_z in [0, 1]",
              met["vld_mse_z"] == 2 * met["vld_loss"]
              and met["vld_mae_y"] <= met["vld_rmse_y"]
              # rel_tol 1e-6: mse_y / rmse_y are float32-derived — the square
              # round-trip carries float32-level error (~3e-8 here).
              and math.isclose(met["vld_mse_y"], met["vld_rmse_y"] ** 2, rel_tol=1e-6)
              and met["vld_samples"] == len(ctx.vld_positions) == len(ctx.vld_game_values)
              and vld_z.min() >= 0.0 and vld_z.max() <= 1.0,
              f"mse_z={met['vld_mse_z']} 2*loss={2 * met['vld_loss']} "
              f"z=({vld_z.min()}, {vld_z.max()})")
        # C5 the no-cache fact: VALIDATE writes nothing (the rlmwf_12 slot unused)
        c12 = [p.name for p in tmp.iterdir() if p.name.startswith("rlmwf_12")]
        check("C5 no rlmwf_12_* cache file in the base dir (VALIDATE is pure compute)",
              c12 == [], f"files: {c12}")
        # (C6 deleted at D-106 step 3, class c: identical metrics +
        #  no DB re-extraction + the 6 cache_manager hits are pinned
        #  by test_second_instance_deterministic — the classification
        #  had marked this a, assuming the test file held only 2
        #  golden-run tests; it has 3, and this is one of them)
        # (C7 deleted at D-106 step 3, class c (a? resolved): the
        #  _down scope is pinned by test_down_clears_vld_metrics)


# ----------------------------------------------------------------------
# D. unit facts (no DB) — the full metric math on a hand-computed case
# ----------------------------------------------------------------------
from twolm.rlm_validate import validate_model


def fake_ctx(game_values, indexes, offsets, w_dense):
    # The y2z/z2y lambdas mirror the zed factory (hlp_zed L80-83/L87-89):
    # the float32 CAST BEFORE the affine (the real y2z does NOT overflow on
    # int8 64 — a raw (y + 64) on int8 would wrap to -128).
    return SimpleNamespace(
        vld_positions=np.zeros(len(game_values), dtype=np.uint64),
        vld_game_values=np.asarray(game_values, dtype=np.int8),
        feature_set=SimpleNamespace(
            compute_indexes=lambda p: np.asarray(indexes, dtype=np.int64),
            features=[SimpleNamespace(n_instances=len(offsets) - 1)]),
        iwmap_feature_offset=np.asarray(offsets, dtype=np.int64),
        w_dense=np.asarray(w_dense, dtype=np.float64),
        y2z=lambda y: (np.float32(y) + 64) / 128,
        z2y=lambda z: 128 * z - 64,
        log_event=lambda rel, msg: None)


# 1 feature / 2 instances, 2 positions.
# vld_indexes [[0,1],[1,0]] + col_offsets [0,0] -> dense_indices [[0,1],[1,0]]
# w_dense [0.5,-0.5] -> linear_predictor [0,0] -> z_pred [0.5,0.5]
# y2z(y)=(y+64)/128: game [0,64] -> vld_z [0.5,1.0]
# rn_z [0,-0.5]: norm 0.25, loss 0.0625, mse_z 0.125, mae_z 0.25
# z2y(z)=128z-64: y_pred [0,0], rn_y [0,-64]: mae_y 32, mse_y 2048, rmse_y sqrt(2048)
_d = validate_model(fake_ctx([0, 64], [[0, 1], [1, 0]], [0, 2], [0.5, -0.5]))
# (D1 moved to a test at D-106 step 3, class a §4 conversion:
#  test_lm_worker_validate.py::TestValidateModelUnit::
#  test_full_metric_math_on_hand_computed_case — the same
#  hand-computed 2-position fixture. The call stays here because
#  D2 pins the result TYPES.)
check("D2 every metric value is a PYTHON float (the float() casts) + vld_samples an int",
      all(type(_d[k]) is float for k in ("vld_loss", "vld_mse_z", "vld_mae_z",
                                         "vld_mae_y", "vld_mse_y", "vld_rmse_y"))
      and type(_d["vld_samples"]) is int)
# (D3 moved to a test at D-106 step 3, class a §4 conversion:
#  test_lm_worker_validate.py::TestValidateModelUnit::
#  test_rmse_mae_line_is_zero_guarded — the M1 (D-102) zero-guard
#  branch on a perfect Y-space fit)


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
