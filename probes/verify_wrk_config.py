#!/usr/bin/env python3
"""
Verification probe for the lm_worker_config analysis (session 21, D-077).

Independently re-derives the module's invariants against the real test
config (src/reversi/test/data/rlm_00.json) with a scratch base dir under
build/tmp (D-065). Prints ok/FAIL per check and a mismatch count.
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

from reversi.lm.logistic_model import LogisticModel, RLMContext
from reversi.lm.hlp_config_schemas import ReversiLogisticModelConfig
from reversi.tools.state_machine import Verbosity
import reversi.lm.wrk_config as lwc
import reversi.tools.binio as binio

TMP_BASE = ROOT / "build" / "tmp" / "vlog_lmwc_d077"
CONFIG_JSON = ROOT / "src" / "reversi" / "test" / "data" / "rlm_00.json"

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
                            "_validate_base_dir", "_store_to_file")
                if not callable(getattr(lwc, n, None))]
    check("A4 six module-level privates exist", not privates, repr(privates))

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
    check("B3 ctx.cfg is a ReversiLogisticModelConfig",
          isinstance(ctx.cfg, ReversiLogisticModelConfig))
    raw = json5.loads(CONFIG_JSON.read_text())
    check("B4 cfg.name round-trips from the json",
          ctx.cfg.name == raw["name"], ctx.cfg.name)
    # (B5 deleted at D-106 step 3, class c: the override is pinned by
    #  TestLMWorkerConfigCacheLogic — the cache files are asserted in
    #  the base_dir_override tmp dir)
    check("B6 ctx.use_cache set from the config (True)",
          ctx.use_cache is True, repr(ctx.use_cache))

    dat = base1 / "rlmwf_01_CONFIG.dat"
    side = base1 / "rlmwf_01_CONFIG.dat.SHA3-256"
    check("B7 flat cache file base_dir/rlmwf_01_CONFIG.dat exists", dat.is_file())
    check("B8 sidecar .SHA3-256 exists", side.is_file())
    check("B9 no 'rlmwf_' subdirectory (naming fix)", not (base1 / "rlmwf_").exists())
    check("B10 .dat content == model_dump_json(indent=4)",
          dat.read_text() == dump_cfg(ctx.cfg))
    expect_hex = hashlib.sha3_256(dump_cfg(ctx.cfg).encode()).hexdigest()
    check("B11 sidecar == raw hex sha3_256 of the dump",
          side.read_text() == expect_hex)
    check("B12 sidecar is NOT binio format (no '  <basename>' second token)",
          len(side.read_text().split()) == 1)
    check("B13 binio can READ the worker's bare-hex sidecar",
          binio.verify_sha3_256_sidecar(dat) is True)

    # ------------------------------------------------------------------ C
    print("--- C. re-runs and mutations ---")
    mtime1 = dat.stat().st_mtime
    content1 = dat.read_text()
    model.move_to_step("CREATED")
    model.move_to_step("CONFIG")
    check("C1 identical second run: mtime unchanged",
          dat.stat().st_mtime == mtime1)
    check("C2 identical second run: content unchanged",
          dat.read_text() == content1)
    check("C3 down reset: cfg None, use_cache None",
          (lambda m: (m.move_to_step("CREATED"),
                       (m.context.cfg is None, m.context.use_cache is None))[1])
          (model) == (True, True))

    # config change -> rewrite
    base1b = fresh(TMP_BASE, "run2")
    modified = json5.loads(CONFIG_JSON.read_text())
    modified["description"] = "MODIFIED FOR PROBING"
    mod_path = TMP_BASE / "rlm_00_modified.json"
    mod_path.write_text(json5.dumps(modified, indent=4))
    model2 = LogisticModel(str(mod_path), verbosity=Verbosity.LOW,
                           base_dir_override=base1b)
    model2.move_to_step("CONFIG")
    check("C4 changed config: new checksum written",
          (base1b / "rlmwf_01_CONFIG.dat.SHA3-256").read_text() != expect_hex)

    # corruption -> sentinel RuntimeError
    (base1b / "rlmwf_01_CONFIG.dat").write_text("CORRUPTED DATA")
    model3 = LogisticModel(str(mod_path), verbosity=Verbosity.LOW,
                           base_dir_override=base1b)
    try:
        model3.move_to_step("CONFIG")
        check("C5 corrupted .dat -> RuntimeError 'not matching'", False,
              "no exception")
    except RuntimeError as e:
        check("C5 corrupted .dat -> RuntimeError 'not matching'",
              "not matching" in str(e).lower(), str(e))

    # missing sidecar -> RuntimeError
    base1c = fresh(TMP_BASE, "run3")
    m4 = LogisticModel(str(CONFIG_JSON), verbosity=Verbosity.LOW,
                       base_dir_override=base1c)
    m4.move_to_step("CONFIG")
    (base1c / "rlmwf_01_CONFIG.dat.SHA3-256").unlink()
    m5 = LogisticModel(str(CONFIG_JSON), verbosity=Verbosity.LOW,
                       base_dir_override=base1c)
    try:
        m5.move_to_step("CONFIG")
        check("C6 missing sidecar -> RuntimeError 'is missing'", False,
              "no exception")
    except RuntimeError as e:
        check("C6 missing sidecar -> RuntimeError 'is missing'",
              "is missing" in str(e), str(e))

    # binio-format sidecar vs the worker's bare-hex verify (asymmetry)
    base1d = fresh(TMP_BASE, "run4")
    m6 = LogisticModel(str(CONFIG_JSON), verbosity=Verbosity.LOW,
                       base_dir_override=base1d)
    m6.move_to_step("CONFIG")
    d6 = base1d / "rlmwf_01_CONFIG.dat"
    hexv = hashlib.sha3_256(d6.read_bytes()).hexdigest()
    (base1d / "rlmwf_01_CONFIG.dat.SHA3-256").write_text(f"{hexv}  01_CONFIG.dat\n")
    m7 = LogisticModel(str(CONFIG_JSON), verbosity=Verbosity.LOW,
                       base_dir_override=base1d)
    try:
        m7.move_to_step("CONFIG")
        check("C7 binio-format sidecar -> worker verify FAILS (asymmetry)",
              False, "no exception")
    except RuntimeError as e:
        check("C7 binio-format sidecar -> worker verify FAILS (asymmetry)",
              "not matching" in str(e).lower(), str(e))

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
    # (un-injected) RLMContext instead keeps the no-op lambda (returns None)
    bare = RLMContext(config_file_path=CONFIG_JSON)
    check("E4a bare-context no-op lambda returns None",
          bare.get_cache_file_path_for_current_level() is None)
    # (E4b moved to a test at D-106 step 3, class a §4 conversion:
    #  test_logistic_model.py::TestLogisticModel::
    #  test_injected_cache_closure_requires_cfg)

    # use_cache is never consulted in _store_to_file (source fact)
    src = inspect.getsource(lwc._store_to_file)
    check("E5 'use_cache' absent from _store_to_file source",
          "use_cache" not in src)

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
