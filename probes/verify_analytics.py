#!/usr/bin/env python3
"""
verify_analytics.py — scratch probe for the ANALYTICS bring-in
(session 28, Roberto's commit 96dacb5 — the 14th pipeline level,
the 2nd bring-in with a dedicated data module, rlm_analytics,
function-only like hlp_gradient / hlp_validate).

Re-derives and verifies, independently of the test files (there
are none — the bring-in has no test file, T5):
  A. lm_worker_analytics.py + rlm_analytics.py structure (pinned to
     the post-campaign expectations: T1 the factory gate, T2 the
     dead imports, T4 the ws lines, T5 the missing test file,
     R1-class the undeclared train_metrics blackboard field)
  B. context facts (the RLMContext pre-declared fields)
  C. GOLDEN re-derivation (live DB, gated on SKIP_REGAB_DB): the
     rlm_02.json pipeline to ANALYTICS (step 13) — the 7-metric
     training goldens, the 4-key dense-pass goldens (D-105/M2), the
     console report, the file report (date-masked golden hash), the
     no-cache-file fact, the second-instance determinism, the _down
     scope
  D. unit facts (no DB): the full training-metric math on a
     hand-computed 2-position case, the opt_info None branch, the
     dense-pass metric math (D-105/M2), the console-report N/A branch

 D-105 re-pin: the header table is now the 3-metric TRAINING |
 TRAINING-DENSE | VALIDATION layout (+ Population baseline line +
 Substitution Delta line; the Generalization Gap is dense-vs-dense).

Run from the workspace root:  .venv/bin/python scratch/verify_analytics.py
"""
import contextlib
import hashlib
import io
import math
import os
import re
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
# A. lm_worker_analytics.py + rlm_analytics.py structure
# ----------------------------------------------------------------------
wk_src = read("src/twolm/lm_worker_analytics.py")
dv_src = read("src/reversi/lm/hlp_analytics.py")
check("A1 Worker named ANALYTICS + __all__ + the 4 public data names "
      "(function-only module — no data class, no store/load; D-105/M2 "
      "added compute_training_dense_metrics)",
      'Worker("ANALYTICS", _up, _down)' in wk_src
      and "__all__ = ['lm_worker_analytics']" in wk_src
      and "__all__ = ['compute_training_metrics', 'compute_training_dense_metrics',\n"
      "           'format_console_report', 'format_file_report']" in dv_src)
check("A2 the factory is @validate_call-decorated + pydantic imported "
      "(all 12 sibling worker factories — the D-102 T1 pattern; "
      "pre-campaign: missing)",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef lm_worker_analytics" in wk_src
      and "from pydantic import validate_call, ConfigDict" in wk_src)
check("A3 no dead import in the worker (`Path` is never used — the report "
      "path is built from ctx.cfg.base_dir, already a Path)",
      "from pathlib import Path" not in wk_src)
check("A4 no dead imports in rlm_analytics (`sys` is never used; `Optional` "
      "and `List` are in the typing line but never referenced)",
      "import sys" not in dv_src
      and re.search(r"from typing import .*", dv_src).group(0)
      == "from typing import TYPE_CHECKING, Dict")
check("A5 both headers carry their own names",
      lines("src/twolm/lm_worker_analytics.py")[1] == "# lm_worker_analytics.py"
      and lines("src/reversi/lm/hlp_analytics.py")[1] == "# hlp_analytics.py")
_wk_ws = ws_lines("src/twolm/lm_worker_analytics.py")
_dv_ws = ws_lines("src/reversi/lm/hlp_analytics.py")
check("A6a the worker has no code ws lines (pre-campaign: 6 — L47/50/53/57 "
      "ws-only + L63/65 trailing)",
      _wk_ws == [], f"lines {_wk_ws}")
check("A6b rlm_analytics has no code ws lines (pre-campaign: 39 — the "
      "ws-only + trailing lines across the table helpers)",
      _dv_ws == [], f"lines {_dv_ws}")
check("A7 the worker writes the report to base_dir/<cfg.analytics."
      "report_file_name> and stores the console report on the context",
      'ctx.cfg.analytics.report_file_name' in wk_src
      and "ctx.analytics_report = console_report" in wk_src)
check("A8 the _down scope clears exactly the THREE fields _up sets "
      "(train_metrics, train_dense_metrics (D-105/M2) + analytics_report)",
      wk_src.count("= None") == 3
      and "ctx.analytics_report = None" in wk_src
      and "ctx.train_metrics = None" in wk_src
      and "ctx.train_dense_metrics = None" in wk_src)
check("A9 the worker uses NO cache_manager (ANALYTICS is pure compute — like "
      "FEATURES / ZED / GRADIENT / VALIDATE; the rlmwf_12 slot stays unused)",
      "cache_manager" not in wk_src and "cache_manager" not in dv_src)
check("A10 the 4 public data fns take ctx under TYPE_CHECKING and carry NO "
      "@validate_call (the rlm_indexes-L166 class — consistent with "
      "hlp_validate.validate_model; report-only pin; D-105/M2 added "
      "compute_training_dense_metrics)",
      dv_src.count("@validate_call") == 0
      and dv_src.count('def ') == 7
      and "if TYPE_CHECKING:" in dv_src)
check("A11 a test file exists for the worker (pre-campaign: absent — T5)",
      (WS / "src" / "twolm" / "test" / "test_lm_worker_analytics.py").exists())
check("A12 RLMContext pre-declares train_metrics (pre-campaign: it does NOT — "
      "the worker sets an ad-hoc attribute; dataclasses allow it, but every "
      "other blackboard field is declared; Roberto's call)",
      "    train_metrics: Any = None" in read("src/twolm/logistic_model.py"))
check("A13 RLMContext pre-declares train_dense_metrics (D-105/M2 — the "
      "dense-pass dict the ANALYTICS worker publishes, same idiom as "
      "train_metrics)",
      "    train_dense_metrics: Any = None" in read("src/twolm/logistic_model.py"))

# ----------------------------------------------------------------------
# B. context facts (the B1-B3 pipeline-state pins moved to the hub
# verify_logistic_model.py V3c/V3d at D-106)
# ----------------------------------------------------------------------
lm_src = read("src/twolm/logistic_model.py")
check("B4 RLMContext pre-declared vld_metrics (L152) + train_metrics (L155) "
      "+ train_dense_metrics (L156, D-105/M2) + analytics_report (L157)",
      "    vld_metrics: Any = None" in lm_src
      and "    train_metrics: Any = None" in lm_src
      and "    train_dense_metrics: Any = None" in lm_src
      and "    analytics_report: Any = None" in lm_src)
check("B5 the schema has AnalyticsConfig (detailed_report default [], "
      "report_file_name default 'model_analytics_report.txt') — so "
      "ctx.cfg.analytics always exists and L60 of the worker is safe",
      "class AnalyticsConfig(RLMBaseConfig)" in read("src/reversi/lm/hlp_config_schemas.py")
      and 'report_file_name: str = Field(' in read("src/reversi/lm/hlp_config_schemas.py")
      and 'default="model_analytics_report.txt"' in read("src/reversi/lm/hlp_config_schemas.py")
      and "    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)" in read("src/reversi/lm/hlp_config_schemas.py"))

# ----------------------------------------------------------------------
# C. GOLDEN re-derivation (live DB) — the rlm_02.json pipeline to ANALYTICS
# ----------------------------------------------------------------------
if os.getenv("SKIP_REGAB_DB", "0") == "1":
    skip("C-tier (live DB golden re-derivation)", "SKIP_REGAB_DB=1")
else:
    from twolm.logistic_model import LogisticModel
    from reversi.tools.state_machine import Verbosity
    from reversi.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE
    from reversi.lm.hlp_analytics import format_file_report

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

        check("C1 the rlm_02 pipeline reaches VALIDATE (step 12) with no crash",
              m.current_worker_name == "VALIDATE" and m.current_step == 12,
              f"step={m.current_step} name={m.current_worker_name}")
        check("C2 pre-state at step 12: analytics_report None, train_metrics "
              "+ train_dense_metrics (D-105/M2) not yet set",
              ctx.analytics_report is None
              and getattr(ctx, "train_metrics", None) is None
              and getattr(ctx, "train_dense_metrics", None) is None
              and (A12_DECLARED := ("    train_metrics: Any = None" in read("src/twolm/logistic_model.py"))
                   or "train_metrics" not in vars(ctx)),
              f"train_metrics in vars(ctx): {'train_metrics' in vars(ctx)}")
        # C3 the 13th-level move: ANALYTICS
        buf3 = io.StringIO()
        with contextlib.redirect_stdout(buf3):
            m.move_to_step("ANALYTICS")
        out3 = buf3.getvalue()
        check("C3 the rlm_02 pipeline reaches ANALYTICS (step 13) with no crash",
              m.current_worker_name == "ANALYTICS" and m.current_step == 13,
              f"step={m.current_step} name={m.current_worker_name}")
        tm = ctx.train_metrics
        check("C4 the train_metrics goldens (rlm_02 live, bid [6,7] training, "
              "199952 samples — first run, pinned by the live run): 7 keys",
              tm is not None and set(tm) == {"train_mae_y", "train_rmse_y",
                                             "train_loss", "train_samples",
                                             "pop_mae_y", "pop_rmse_y", "pop_loss"},
              f"got {tm}")
        if tm is not None:
            check("C4a the train_metrics values (live): "
                  f"mae_y {tm.get('train_mae_y')!r}, rmse_y {tm.get('train_rmse_y')!r}, "
                  f"loss {tm.get('train_loss')!r}, samples {tm.get('train_samples')!r}, "
                  f"pop_mae_y {tm.get('pop_mae_y')!r}, pop_rmse_y {tm.get('pop_rmse_y')!r}, "
                  f"pop_loss {tm.get('pop_loss')!r}",
                  tm["train_samples"] == 199952
                  and tm["train_loss"] == ctx.opt_info["f"]
                  and tm["train_mae_y"] <= tm["train_rmse_y"]
                  and tm["pop_mae_y"] <= tm["pop_rmse_y"])
        # (C4b deleted at D-106 step 3, class c: the train_dense_
        #  metrics goldens are pinned by test_lm_worker_analytics.py::
        #  test_reach_analytics_level — the 4-key dict + exact values.
        #  The binding stays: C8 + the gap/delta line checks use td)
        td = ctx.train_dense_metrics
        # C5 the report file
        rpt = tmp / "model_analytics_report.txt"
        check("C5 the report file exists at base_dir/model_analytics_report.txt",
              rpt.exists(), f"dir listing: {[p.name for p in tmp.iterdir()]}")
        if rpt.exists():
            content = rpt.read_text()
            check("C5a the file report = header (detailed) + FEATURE SET SUMMARY "
                  "+ MOBILITY (empty — no mobility features) + PATTERN details "
                  "(EDGE rows printed — in detailed_report; DIAG3 rows omitted — "
                  "not in it; ELLE/LMC absent from the fixture)",
                  "MODEL ANALYTICS REPORT: RGLM (Logistic) - Unit Test 02 (rlm_02.json)" in content
                  and "Creation Date" in content
                  and "FEATURE SET SUMMARY:" in content
                  and "MOBILITY FEATURES DETAILS:" in content
                  and "PATTERN FEATURES DETAILS:" in content
                  and "PATTERN FEATURE: EDGE (fid=0)" in content
                  and "PATTERN FEATURE: DIAG3 (fid=1)" in content
                  and "(Table rows omitted: feature not in config 'analytics.detailed_report')" in content
                  and "MOBILITY FEATURE:" not in content
                  and "PATTERN FEATURE: ELLE" not in content
                  and content.count("(Table rows omitted") == 1)
            masked = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE", content)
            FILE_HASH = hashlib.sha3_256(masked.encode()).hexdigest()
            print(f"       file report golden (date-masked sha3_256): {FILE_HASH}")
            recomputed = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE",
                                format_file_report(ctx))
            check("C5b the file report is deterministic (date-masked) — "
                  "recompute via format_file_report and compare",
                  hashlib.sha3_256(recomputed.encode()).hexdigest() == FILE_HASH)
        # (C6 deleted at D-106 step 3, class c: the 17 header lines +
        #  the 4 worker/data INFO lines are pinned by
        #  test_lm_worker_analytics.py::test_analytics_report_lines)
        _ls = out3.splitlines()
        _l0 = (next(i for i, l in enumerate(_ls)
                    if "Generating model analytics report..." in l)
               if any("Generating model analytics report..." in l for l in _ls)
               else None)
        _l1 = (next(i for i, l in enumerate(_ls)
                    if "Analytics report saved to" in l)
               if _l0 is not None else None)
        _span = (len(out3.splitlines()[_l0:_l1 + 1])
                 if _l0 is not None else -1)
        check("C6a the step-13 log span from 'Generating model analytics "
              "report...' to 'Analytics report saved to ...' is exactly 21 "
              "lines (1 'Generating' + 1 'Computing metrics' + 1 'Computing "
              "dense-pass metrics' (D-105/M2) + 17 header lines + 1 'saved "
              "to') — pinned by the live run",
              _span == 21, f"span lines: {_span}")
        # C7 no new cache file (the rlmwf_12 slot stays unused)
        c12 = [p.name for p in tmp.iterdir() if p.name.startswith("rlmwf_12")]
        check("C7 no rlmwf_12_* cache file in the base dir (ANALYTICS is pure compute)",
              c12 == [], f"files: {c12}")
        check("C7b the rlmwf_* file set is unchanged by ANALYTICS "
              "(01/02/04/05/06/10/11 + sidecars — the 7 cache levels)",
              sorted(p.name for p in tmp.iterdir() if p.name.startswith("rlmwf_"))
              == sorted(["rlmwf_01_CONFIG.dat", "rlmwf_02_POSITIONS.dat",
                         "rlmwf_04_INDEXES.dat", "rlmwf_05_WMAPS.dat",
                         "rlmwf_06_DESIGN_MTR.dat", "rlmwf_10_GENERATE.dat",
                         "rlmwf_11_VLD_POSITIONS.dat",
                         "rlmwf_01_CONFIG.dat.SHA3-256", "rlmwf_02_POSITIONS.dat.SHA3-256",
                         "rlmwf_04_INDEXES.dat.SHA3-256", "rlmwf_05_WMAPS.dat.SHA3-256",
                         "rlmwf_06_DESIGN_MTR.dat.SHA3-256", "rlmwf_10_GENERATE.dat.SHA3-256",
                         "rlmwf_11_VLD_POSITIONS.dat.SHA3-256"]))
        # C8 second instance on the same base dir: deterministic recompute
        buf2 = io.StringIO()
        with contextlib.redirect_stdout(buf2):
            m2 = LogisticModel(cfg_path, verbosity=Verbosity.HIGH, base_dir_override=tmp)
            m2.move_to_step("ANALYTICS")
        out2 = buf2.getvalue()
        check("C8 second instance: identical train_metrics + identical "
              "train_dense_metrics (D-105/M2) + identical console report "
              "(ANALYTICS has no cache file — determinism is the pin) "
              "+ no DB re-extraction + the 6 cache_manager levels all hit",
              m2.context.train_metrics == tm
              and m2.context.train_dense_metrics == td
              and m2.context.analytics_report == ctx.analytics_report
              and "Extracted" not in out2
              and out2.count("Cache successfully loaded and validated") == 6,
              f"hits={out2.count('Cache successfully loaded and validated')}")
        # C9 the _down scope
        m2.move_to_step(12)
        check("C9 _down (back to VALIDATE, step 12) clears train_metrics, "
              "train_dense_metrics (D-105/M2) + analytics_report",
              m2.context.train_metrics is None
              and m2.context.train_dense_metrics is None
              and m2.context.analytics_report is None
              and m2.current_step == 12
              and m2.current_worker_name == "VALIDATE")
        # C10 independent re-derivation of the training metrics (compressed path)
        X = ctx.design_matrix
        pred = np.sum(ctx.w[X].astype(np.float64), axis=1)
        from reversi.lm.hlp_gradient import sigmoid
        z_pred = sigmoid(pred)
        y_pred = ctx.z2y(z_pred)
        y_true = ctx.game_values.astype(np.float64)
        rn = y_pred - y_true
        check("C10 independent re-derivation (float64, compressed path): "
              "mae_y / rmse_y / pop_* / pop_loss match train_metrics exactly",
              tm is not None
              and float(np.mean(np.abs(rn))) == tm["train_mae_y"]
              and float(np.sqrt(np.dot(rn, rn) / len(rn))) == tm["train_rmse_y"]
              and float(np.mean(np.abs(y_true - np.mean(y_true)))) == tm["pop_mae_y"]
              and float(np.sqrt(np.dot(y_true - np.mean(y_true), y_true - np.mean(y_true)) / len(y_true))) == tm["pop_rmse_y"])
        vld = ctx.vld_metrics
        _gap_line = next(l for l in ctx.analytics_report.splitlines()
                         if "Generalization Gap" in l)
        _gap_val = _gap_line.rsplit(":", 1)[1].strip()
        check("C11 the header's Generalization Gap line = vld_rmse_y - "
              "train_dense_rmse_y (%.2f) — DENSE vs DENSE (D-105/M2): a pure "
              "generalization measure, no mixed representations; the "
              "compressed-vs-dense substitution effect is the separate "
              "Substitution Delta row below; rlm_02 has no mobility, no "
              "intercept, cut 1",
              _gap_val == f"{vld['vld_rmse_y'] - td['train_dense_rmse_y']:.2f}",
              f"line: {_gap_line!r} expected: {vld['vld_rmse_y'] - td['train_dense_rmse_y']:.2f}")
        _sub_line = next(l for l in ctx.analytics_report.splitlines()
                         if "Substitution Delta" in l)
        _sub_val = _sub_line.rsplit(":", 1)[1].strip()
        check("C11b the Substitution Delta line = train_dense_rmse_y - "
              "train_rmse_y (%.2f) — at rlm_02's frequency_cut_off=1 the "
              "residual is only the f32 rounding of w_dense (no IC configs)",
              _sub_val == f"{td['train_dense_rmse_y'] - tm['train_rmse_y']:.2f}",
              f"line: {_sub_line!r}")


# ----------------------------------------------------------------------
# D. unit facts (no DB) — the full metric math on a hand-computed case
# ----------------------------------------------------------------------
from reversi.lm.hlp_analytics import (compute_training_metrics,
                                 compute_training_dense_metrics,
                                 format_console_report)


def fake_ctx(game_values, design_matrix, w, opt_info):
    # y2z/z2y mirror the zed factory (the float32 cast before the affine).
    return SimpleNamespace(
        design_matrix=np.asarray(design_matrix, dtype=np.uint32),
        w=np.asarray(w, dtype=np.float32),
        w_dense=None,
        game_values=np.asarray(game_values, dtype=np.int8),
        y2z=lambda y: (np.float32(y) + 64) / 128,
        z2y=lambda z: 128 * z - 64,
        opt_info=opt_info,
        log_event=lambda rel, msg: None)


# 2 positions, 1 feature / 2 instances / 2 configs (a symmetric 2x2 design).
# w [1,-1]: predictor = w[0]+w[1] = 0 on both rows -> z_pred 0.5 -> y_pred 0.
# game [10,-10]: rn_y [-10,10]: mae 10, rmse 10. pop baseline: y_mean 0 ->
# pop_mae 10, pop_rmse 10. z_true [0.578125, 0.421875]: z_mean 0.5,
# rn_z_pop +/-0.078125: pop_loss 0.5*2*(0.078125^2)/2 = 0.0030517578125.
_d = compute_training_metrics(fake_ctx([10, -10], [[0, 1], [1, 0]], [1.0, -1.0],
                                       {"f": 0.123}))
check("D1 the full training-metric math on the hand-computed 2-position case: "
      "mae_y 10.0, rmse_y 10.0, train_loss 0.123 (opt_info['f']), samples 2, "
      "pop_mae_y 10.0, pop_rmse_y 10.0, pop_loss 0.0030517578125",
      _d == {"train_mae_y": 10.0, "train_rmse_y": 10.0, "train_loss": 0.123,
             "train_samples": 2, "pop_mae_y": 10.0, "pop_rmse_y": 10.0,
             "pop_loss": 0.0030517578125},
      f"got {_d}")
_d2 = compute_training_metrics(fake_ctx([10, -10], [[0, 1], [1, 0]], [1.0, -1.0],
                                        None))
check("D2 the opt_info None branch: train_loss falls back to 0.0",
      _d2["train_loss"] == 0.0 and _d2["train_mae_y"] == 10.0)
_h = format_console_report(SimpleNamespace(
    cfg=SimpleNamespace(name="HandCase"),
    w=np.zeros(4, dtype=np.float32),
    w_dense=np.zeros(10, dtype=np.float32),
    opt_info={"reason": "done", "iters": 7},
    train_metrics={"train_mae_y": 1.5, "train_rmse_y": 2.5,
                   "train_loss": 3e-3, "train_samples": 100,
                   "pop_mae_y": 4.5, "pop_rmse_y": 5.5, "pop_loss": 6e-3},
    train_dense_metrics=None,
    vld_metrics=None))
check("D3 the console report (no tables, no date): the N/A TRAINING-DENSE "
      "(D-105/M2) + VALIDATION columns (6 N/A cells), the Population "
      "baseline line, the Generalization Gap 0.00 + Substitution Delta "
      "0.00 lines, 17 lines total",
      "MODEL ANALYTICS REPORT: HandCase" in _h
      and "Optimization Status         : done (7 iters)" in _h
      and "Population (baseline)  : RMSE 5.50  MAE 4.50  Loss 6.0000e-03" in _h
      and "Generalization Gap (RMSE)   : 0.00" in _h
      and "Substitution Delta (RMSE)   : 0.00" in _h
      and len(_h.strip().split("\n")) == 17
      and _h.count("N/A") == 6,
      f"lines={len(_h.strip().split(chr(10)))}\n{_h}")


# D4 (D-105/M2) the dense-pass metric math on the same hand-computed
# 2-position case: 1 feature / 2 instances / 2 configs, dense indices
# [[0,1],[1,0]] (raw [[0,1],[1,0]] + offsets [0,0]) over w_dense [1,-1]
# -> predictor 0 on both rows -> z_pred 0.5 -> y_pred 0. Same residuals
# as D1: mae_y 10, rmse_y 10, loss 0.5*mean(rn_z^2) = 0.0030517578125.
def fake_dense_ctx(game_values, indexes, w_dense, offsets, n_instances):
    return SimpleNamespace(
        rlm_indexes=SimpleNamespace(indexes=np.asarray(indexes, dtype=np.int32)),
        iwmap_feature_offset=np.asarray(offsets, dtype=np.uint32),
        feature_set=SimpleNamespace(
            features=[SimpleNamespace(n_instances=n_instances)]),
        w_dense=np.asarray(w_dense, dtype=np.float32),
        game_values=np.asarray(game_values, dtype=np.int8),
        y2z=lambda y: (np.float32(y) + 64) / 128,
        z2y=lambda z: 128 * z - 64,
        log_event=lambda rel, msg: None)


_dd = compute_training_dense_metrics(
    fake_dense_ctx([10, -10], [[0, 1], [1, 0]], [1.0, -1.0], [0, 2], 2))
check("D4 the dense-pass metric math on the hand-computed 2-position case "
      "(D-105/M2): mae_y 10.0, rmse_y 10.0, loss 0.0030517578125, samples 2",
      _dd == {"train_dense_mae_y": 10.0, "train_dense_rmse_y": 10.0,
              "train_dense_loss": 0.0030517578125, "train_dense_samples": 2},
      f"got {_dd}")


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
