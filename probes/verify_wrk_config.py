#!/usr/bin/env python3
"""
Verification probe for the CONFIG level (the ad-hoc cache
flow is removed — the CONFIG level is a pure load+validate step; the
config record is EMBEDDED in the v2 model file at SAVE).

Independently re-derives the module's invariants against the real test
config (test/reversi/data/rlm_00.json) with a scratch base dir under
build/tmp. Prints ok/FAIL per check and a mismatch count.
"""
import hashlib
import inspect
import json
import json5
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reversi.lm.logistic_model import LogisticModel, LMContext
from reversi.lm.hlp_config_schemas import LMConfig
from reversi.tools.state_machine import Verbosity
import reversi.lm.wrk_config as lwc

TMP_BASE = ROOT / "build" / "tmp" / "vlog_lmwc_d077"
CONFIG_JSON = ROOT / "test" / "reversi" / "data" / "rlm_00.json"

mismatches = []


def check(label, cond, detail=""):
    tag = "ok  " if cond else "FAIL"
    if not cond:
        mismatches.append(label)
    extra = f"  -> {detail}" if (detail and not cond) else ""
    print(f"[{tag}] {label}{extra}")


def fresh(base, name):
    d = TMP_BASE / name
    d.mkdir(parents=True)
    return d


def dump_cfg(cfg):
    return cfg.model_dump_json(indent=4)


try:
    # ------------------------------------------------------------------ A
    print("--- A. structure ---")
    check("A1 __all__ == ['wrk_config']",
          lwc.__all__ == ["wrk_config"], repr(lwc.__all__))
    w = lwc.wrk_config()
    check("A2 factory name is 'CONFIG'", w.name == "CONFIG", w.name)
    check("A3 factory up/down are the module callables",
          w._up_callable is lwc._up and w._down_callable is lwc._down)
    privates = [n for n in ("_up", "_down", "_load", "_validate",
                            "_validate_base_dir")
                if not callable(getattr(lwc, n, None))]
    check("A4 five module-level privates exist (_store_to_file "
          "gone — the ad-hoc cache flow removed)",
          not privates, repr(privates))

    # ------------------------------------------------------------------ B
    print("--- B. behaviour on the real config ---")
    base1 = fresh(TMP_BASE, "run1")
    model = LogisticModel(str(CONFIG_JSON), verbosity=Verbosity.LOW,
                          base_dir_override=base1)
    # (B1/B2 deleted at D-106 step 3, class c: pinned by
    #  test_wrk_config.py — setUp (step 0 / CREATED) and
    #  test_move_up (step 1 / CONFIG))
    model.move_to_step("CONFIG")
    ctx = model.context
    check("B3 ctx.cfg is a LMConfig",
          isinstance(ctx.cfg, LMConfig))
    raw = json5.loads(CONFIG_JSON.read_text())
    check("B4 cfg.name round-trips from the json",
          ctx.cfg.name == raw["name"], ctx.cfg.name)
    check("B6 ctx.use_cache set from the config (True)",
          ctx.use_cache is True, repr(ctx.use_cache))
    # The fingerprint is the sha3_256 of the normalized dump
    # (the effective configuration, the base_dir override included).
    check("B6b ctx.config_checksum = sha3_256 of the normalized dump "
          ")",
          ctx.config_checksum
          == hashlib.sha3_256(dump_cfg(ctx.cfg).encode()).hexdigest(),
          repr(ctx.config_checksum))
    check("B7 no rlmwf_* file in the base dir (the CONFIG level "
          "writes nothing — the config record is a SAVE artifact)",
          [p.name for p in base1.iterdir()
           if p.name.startswith("rlmwf_")] == [])

    # ------------------------------------------------------------------ C
    print("--- C. re-runs and resets ---")
    check("C3 down reset: cfg None, use_cache None, config_checksum None "
          ")",
          (lambda m: (m.move_to_step("CREATED"),
                      (m.context.cfg is None,
                       m.context.use_cache is None,
                       m.context.config_checksum is None))[1])
          (model) == (True, True, True))
    # The idempotent second up is a pure load (no cache state to
    # preserve) — the fingerprint is stable across the cycle.
    model.move_to_step("CONFIG")
    check("C1 second up: the fingerprint is stable (pure load, no cache)",
          model.context.config_checksum
          == hashlib.sha3_256(
              dump_cfg(model.context.cfg).encode()).hexdigest())

    # ------------------------------------------------------------------ D
    print("--- D. base_dir validation and errors ---")
    # (D1 moved to a test at D-106 step 3, class a §4 conversion:
    #  test_wrk_config.py::TestLMWorkerConfigBaseDir::
    #  test_base_dir_missing_raises_file_not_found_error)
    # (D2 deleted at D-106 step 3, class c: pinned by test_lm_worker_
    #  config.py::test_base_dir_is_a_file_raises_error)
    # (D3 deleted at D-106 step 3, class c (env-dependent, non-root):
    #  pinned by test_wrk_config.py::test_base_dir_is_not_
    #  writable_raises_error)

    # ------------------------------------------------------------------ E
    print("--- E. gate / integration ---")
    # (E1 deleted at D-106 step 3, class c: pinned by test_lm_worker_
    #  config.py::TestLMWorkerConfigValidation — test_invalid_ec_
    #  out_of_range + the status / hex-mask siblings)

    # gate behaviour unchanged
    # (E2/E3 moved to tests at D-106 step 3, class a §4 conversion —
    #  the D-107 re-pinned guard contract now lives in
    #  test_state_machine.py::test_move_to_step_by_invalid_string /
    #  test_move_to_step_out_of_bounds_high, which pin the FULL
    #  messages ("Worker '<name>' not found in the pipeline." /
    #  "Target step <n> is out of bounds."), not just the type.)

    # the INJECTED closure needs ctx.cfg (ordering load-bearing); a bare
    # (un-injected) LMContext instead keeps the no-op lambda (returns None)
    bare = LMContext(config_file_path=CONFIG_JSON)
    check("E4a bare-context no-op lambda returns None",
          bare.get_cache_file_path_for_current_level() is None)
    # (E4b moved to a test at D-106 step 3, class a §4 conversion:
    #  test_logistic_model.py::TestLogisticModel::
    #  test_injected_cache_closure_requires_cfg)

    # The module never writes files (the ad-hoc store is gone —
    # the config record is written by the SAVE level)
    src_all = inspect.getsource(lwc)
    check("E5 no file-write idiom in the module source",
          "write_text" not in src_all and ".write(" not in src_all)

    # rlm_00.json is JSON5 (comments), not plain JSON
    try:
        json.loads(CONFIG_JSON.read_text())
        plain_ok = True
    except json.JSONDecodeError:
        plain_ok = False
    check("E6 rlm_00.json is NOT plain JSON (json5 load-bearing)", not plain_ok)

    # down logs the clearing line
    m13 = LogisticModel(str(CONFIG_JSON), verbosity=Verbosity.LOW,
                        base_dir_override=fresh(TMP_BASE, "run7"))
    m13.move_to_step("CONFIG")
    m13.move_to_step("CREATED")
    msgs = [e.message for e in m13.sm.logs]
    check("E7 down logs 'Clearing configuration...'",
          any("Clearing configuration" in m for m in msgs))

finally:
    shutil.rmtree(TMP_BASE, ignore_errors=True)

print(f"\n{len(mismatches)} mismatches.")
sys.exit(1 if mismatches else 0)
