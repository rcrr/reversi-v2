#!/usr/bin/env python3
"""
verify_generate.py — scratch probe for the GENERATE bring-in (session 27).

Re-derives and verifies, independently of the test files:
  A. rlm_generate.py structure (post-campaign: note, version gate, ws)
  B. lm_worker_generate.py structure (post-campaign: factory gate, the
     D-074 _for_current_level naming, ws)
  C. test_rlm_generate.py structure (post-campaign: English comment, ws)
  D. data-object behavior (no DB): init validation, hash, store/load
     round-trip, the sidecar / description / version gates, the
     is_cache_consistent branches, the test-mock fixture goldens
     (independently re-derived by hand), the error branches
  E. GOLDEN re-derivation (live DB, gated on SKIP_REGAB_DB): the
     rlm_02.json pipeline to GENERATE — K, the per-feature weighted
     means, orbit invariance, the seen-config exactness, the full
     independent re-derivation, the hash golden, the file naming,
     the second-instance cache hit, the _down clearing, the version gate
  F. context facts (RLMContext pre-declared fields)

Pinned to the POST-campaign state: the A/B/C structural checks and the
E1/E11 + D6 behavior pins FAIL until the fix campaign is applied
(R1 the _for_next_level name, T2 the missing version gate, the T/M
hygiene items).

Run from the workspace root:  .venv/bin/python scratch/verify_generate.py
"""
import hashlib
import os
import re
import sys
import tempfile
from pathlib import Path

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
# A. rlm_generate.py structure (post-campaign)
# ----------------------------------------------------------------------
rlm_src = read("src/twolm/rlm_generate.py")
check("A1 __all__ lists the 5 public names",
      "'ReversiLogisticModelDenseWeights'," in rlm_src
      and "'rlm_generate_store_to_file'," in rlm_src
      and "'rlm_generate_load_from_file'," in rlm_src
      and "'compute_w_dense'," in rlm_src
      and "'rlm_generate_is_cache_consistent']" in rlm_src)
above_compute = rlm_src.split("def compute_w_dense")[0]
check("A2 the house no-validation note sits directly above compute_w_dense",
      "Here validation is not possible" in "\n".join(above_compute.rsplit("\n", 8)[1:]),
      "last 8 lines above the def: " + repr(above_compute.rsplit("\n", 8)[-6:]))
check("A3 rlm_generate_is_cache_consistent carries the no-validation note too",
      "Here validation is not possible" in "\n".join(rlm_src.split("def rlm_generate_is_cache_consistent")[0].rsplit("\n", 8)[1:]))
check("A4 load gates the file version (the 4 sibling data modules all do — T2)",
      "expected_version" in rlm_src
      and "File version mismatch" in rlm_src)
check("A5 no non-comment trailing whitespace",
      not ws_lines("src/twolm/rlm_generate.py"),
      f"lines {ws_lines('src/twolm/rlm_generate.py')}")

# ----------------------------------------------------------------------
# B. lm_worker_generate.py structure (post-campaign)
# ----------------------------------------------------------------------
wk_src = read("src/twolm/lm_worker_generate.py")
check("B1 the worker uses the D-074 house name _for_current_level (the "
      "pre-campaign _for_next_level call is the R1 AttributeError)",
      "get_cache_file_full_path_for_current_level" in wk_src
      and "for_next_level" not in wk_src)
check("B2 the factory is @validate_call-decorated + pydantic imported "
      "(all 10 sibling worker factories — D-092 T2 / D-096 T10 pattern)",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef lm_worker_generate" in wk_src
      and "from pydantic import validate_call, ConfigDict" in wk_src)
check("B3 no non-comment trailing whitespace",
      not ws_lines("src/twolm/lm_worker_generate.py"),
      f"lines {ws_lines('src/twolm/lm_worker_generate.py')}")

# ----------------------------------------------------------------------
# C. test_rlm_generate.py structure (post-campaign)
# ----------------------------------------------------------------------
test_src = read("src/twolm/test/test_rlm_generate.py")
check("C1 the Italian comment is gone (AGENTS.md rule 4 — house fix D-084 T3 class)",
      "AGGIUNTO" not in test_src)
check("C2 no non-comment trailing whitespace",
      not ws_lines("src/twolm/test/test_rlm_generate.py"),
      f"lines {ws_lines('src/twolm/test/test_rlm_generate.py')}")

# ----------------------------------------------------------------------
# D. data-object behavior (no DB)
# ----------------------------------------------------------------------
from pydantic import ValidationError
from twolm import binio
from twolm.rlm_generate import (ReversiLogisticModelDenseWeights,
                                rlm_generate_store_to_file,
                                rlm_generate_load_from_file,
                                rlm_generate_is_cache_consistent,
                                compute_w_dense)

from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE

CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
    tmp = Path(tmp)

    # D1 init validation
    try:
        ReversiLogisticModelDenseWeights("x", [1.0, 2.0])
        check("D1 list w_dense rejected (NDArray gate)", False, "no error")
    except ValidationError:
        check("D1 list w_dense rejected (NDArray gate)", True)
    try:
        ReversiLogisticModelDenseWeights(123, np.zeros(2, np.float32))
        check("D2 non-str w_checksum rejected", False, "no error")
    except ValidationError:
        check("D2 non-str w_checksum rejected", True)

    # D2 hash
    arr = np.array([0.5, -0.2, 3.0], dtype=np.float32)
    dw = ReversiLogisticModelDenseWeights("abc", arr)
    h = hashlib.sha3_256(arr.tobytes()).hexdigest()
    check("D3 compute_sha3_256_hash == independent sha3_256(w_dense.tobytes())",
          dw.compute_sha3_256_hash() == h, dw.compute_sha3_256_hash())

    # D3 round-trip
    p = tmp / "dense.dat"
    rlm_generate_store_to_file(dw, p)
    dw2 = rlm_generate_load_from_file(p, checksum=True)
    check("D4 store/load round-trip (w_checksum + w_dense + sidecar)",
          dw2.w_checksum == "abc" and np.array_equal(dw2.w_dense, arr)
          and (p.parent / "dense.dat.SHA3-256").exists())

    # D4 corrupted sidecar (the hash field)
    sc = tmp / "dense.dat.SHA3-256"
    orig = sc.read_text()
    line = orig.splitlines()[0]
    hexf, name = line.split(None, 1)
    bad = ("0" if hexf[0] != "0" else "1") + hexf[1:] + "  " + name
    sc.write_text(bad + "\n" + orig[len(line) + 1:])
    try:
        rlm_generate_load_from_file(p, checksum=True)
        check("D5 corrupted hash sidecar -> RuntimeError 'Checksum mismatch.'", False, "no error")
    except RuntimeError as e:
        check("D5 corrupted hash sidecar -> RuntimeError 'Checksum mismatch.'",
              str(e) == "Checksum mismatch.", str(e))
    finally:
        sc.write_text(orig)

    # D5 wrong description
    bad_p = tmp / "wrong.dat"
    with binio.BinaryWriter(bad_p) as w:
        w.write_header("Some other file", 1)
        w.write_string("abc")
        w.write_array(arr)
    try:
        rlm_generate_load_from_file(bad_p, checksum=False)
        check("D6 wrong description -> RuntimeError 'Wrong file format: ...'", False, "no error")
    except RuntimeError as e:
        check("D6 wrong description -> RuntimeError 'Wrong file format: ...'",
              str(e) == "Wrong file format: Some other file", str(e))

    # D6 version gate (post T2)
    v2 = tmp / "v2.dat"
    with binio.BinaryWriter(v2) as w:
        w.write_header("RGLM Dense Weights binary data file", 2)
        w.write_string("abc")
        w.write_array(arr)
    try:
        rlm_generate_load_from_file(v2, checksum=False)
        check("D7 version-2 file -> RuntimeError 'File version mismatch: found 2, expected 1'",
              False, "loaded silently (no version gate)")
    except RuntimeError as e:
        check("D7 version-2 file -> RuntimeError 'File version mismatch: found 2, expected 1'",
              str(e) == "File version mismatch: found 2, expected 1", str(e))

    # D7 checksum=False skips the sidecar
    p2 = tmp / "nosidecar.dat"
    with binio.BinaryWriter(p2) as w:
        w.write_header("RGLM Dense Weights binary data file", 1)
        w.write_string("abc")
        w.write_array(arr)
    dw3 = rlm_generate_load_from_file(p2, checksum=False)
    check("D8 checksum=False loads without a sidecar", dw3.w_dense.shape == (3,))

    # D8 is_cache_consistent
    class Ctx:
        w_checksum = "abc"
    check("D9 is_cache_consistent True on match", rlm_generate_is_cache_consistent(Ctx(), dw) is True)
    class Ctx2:
        w_checksum = "def"
    check("D10 is_cache_consistent False on mismatch", rlm_generate_is_cache_consistent(Ctx2(), dw) is False)

    # D11 the test-mock fixture golden (independently re-derived by hand:
    #      INT 0.5; PAT weighted_mean = (-0.2*10)/10 = -0.2, only config 1
    #      is computed -> [-0.2, -0.2, -0.2]; MOB interp over known
    #      configs {1: 1.0, 3: 3.0} clamped -> [1.0, 1.0, 2.0, 3.0, 3.0])
    from types import SimpleNamespace
    ctx = SimpleNamespace()
    ctx.feature_set = SimpleNamespace(
        hash="abc",
        features=[
            SimpleNamespace(name="INT", category=0, n_instances=1, n_configurations=1),
            SimpleNamespace(name="PAT", category=2, n_instances=1, n_configurations=3,
                            ref=SimpleNamespace(convert_to_principal_index=lambda x: x)),
            SimpleNamespace(name="MOB", category=1, n_instances=1, n_configurations=5),
        ])
    ctx.iwmap_feature_offset = np.array([0, 1, 4, 9], dtype=np.uint32)
    ctx.iwmap = np.array([0, -1, 1, 0, -1, 2, -1, 3, -1], dtype=np.int64)
    ctx.feature_w_ranges = np.array([[-1, 0, 0], [0, 0, 1], [-1, 2, 3]], dtype=np.int64)
    ctx.wmap = np.array([[1, -1, 3], [1, 1, 10], [2, 1, 5], [2, 3, 5]], dtype=np.int64)
    ctx.w = np.array([0.5, -0.2, 1.0, 3.0], dtype=np.float32)
    ctx.w_checksum = "abc654"
    ctx.log_event = lambda rel, msg: None
    wd = compute_w_dense(ctx).w_dense
    expected = np.array([0.5, -0.2, -0.2, -0.2, 1.0, 1.0, 2.0, 3.0, 3.0], dtype=np.float32)
    check("D11 the test-mock fixture golden (hand re-derivation)",
          wd.dtype == np.float32 and len(wd) == 9 and np.array_equal(wd, expected),
          repr(wd.tolist()))

    # D12 unknown category -> RuntimeError
    ctx_bad = SimpleNamespace()
    ctx_bad.feature_set = SimpleNamespace(
        hash="x",
        features=[SimpleNamespace(name="X", category=9, n_instances=1, n_configurations=1)])
    ctx_bad.iwmap_feature_offset = np.array([0, 1], dtype=np.uint32)
    ctx_bad.iwmap = np.array([0], dtype=np.int64)
    ctx_bad.feature_w_ranges = np.array([[-1, 0, 0]], dtype=np.int64)
    ctx_bad.wmap = np.zeros((0, 3), dtype=np.int64)
    ctx_bad.w = np.array([0.1], dtype=np.float32)
    ctx_bad.w_checksum = "z"
    ctx_bad.log_event = lambda rel, msg: None
    try:
        compute_w_dense(ctx_bad)
        check("D12 unknown category (9) -> RuntimeError", False, "no error")
    except RuntimeError as e:
        check("D12 unknown category (9) -> RuntimeError",
              "unknown" in str(e).lower() and "9" in str(e), str(e))

    # D13 mobility with no seen configs -> zeros + WARN (no crash)
    ctx_m = SimpleNamespace()
    ctx_m.feature_set = SimpleNamespace(
        hash="x",
        features=[SimpleNamespace(name="MOB", category=1, n_instances=1, n_configurations=4)])
    ctx_m.iwmap_feature_offset = np.array([0, 4], dtype=np.uint32)
    ctx_m.iwmap = np.array([-1, -1, -1, -1], dtype=np.int64)
    ctx_m.feature_w_ranges = np.array([[-1, 0, 0]], dtype=np.int64)
    ctx_m.wmap = np.zeros((0, 3), dtype=np.int64)
    ctx_m.w = np.array([0.0], dtype=np.float32)
    ctx_m.w_checksum = "z"
    warns = []
    ctx_m.log_event = lambda rel, msg: warns.append(msg)
    wm = compute_w_dense(ctx_m).w_dense
    check("D13 mobility no-seen branch -> zeros + WARN log",
          np.array_equal(wm, np.zeros(4, np.float32)) and len(warns) == 1 and "no seen" in warns[0])


# ----------------------------------------------------------------------
# E. GOLDEN re-derivation (live DB) — the rlm_02.json pipeline
# ----------------------------------------------------------------------
if os.getenv("SKIP_REGAB_DB", "0") == "1":
    skip("E-tier (live DB golden re-derivation)", "SKIP_REGAB_DB=1")
else:
    with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
        tmp = Path(tmp)
        from twolm.logistic_model import LogisticModel
        from twolm.state_machine import Verbosity
        m = LogisticModel(str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_02.json"),
                          verbosity=Verbosity.LOW, base_dir_override=tmp)
        try:
            m.move_to_step("GENERATE")
            crashed = False
        except AttributeError as e:
            crashed = True
            check("E1 the pipeline reaches GENERATE (pre-fix R1: AttributeError "
                  "'get_cache_file_full_path_for_next_level')", False, str(e))
        ctx = m.context
        w, iwmap, off, wmap, fwr = ctx.w, ctx.iwmap, ctx.iwmap_feature_offset, ctx.wmap, ctx.feature_w_ranges

        if not crashed:
            K = int(off[-1])
            check("E2 K = 6588 = 6561 (EDGE) + 27 (DIAG3)", K == 6588, f"{K}")
            check("E3 w_dense (6588,) float32", ctx.w_dense.shape == (6588,) and ctx.w_dense.dtype == np.float32)
            # independent per-feature re-derivation (a different code path)
            ref = np.full(K, np.nan, dtype=np.float64)
            wm_ok = True
            for fid, f in enumerate(ctx.feature_set.features):
                s, e = int(off[fid]), int(off[fid + 1])
                f_iw = iwmap[s:e]
                rows = wmap[wmap[:, 0] == fid]
                t = rows[rows[:, 1] >= 0]
                tconf = t[:, 1].astype(np.int64)
                tfreq = t[:, 2]
                tweights = w[f_iw[tconf]]
                wm = float(np.dot(tweights, tfreq)) / float(np.sum(tfreq))
                dense = np.full(e - s, wm, dtype=np.float64)
                principal = f.ref.convert_to_principal_index(np.arange(e - s, dtype=np.uint32))
                comp = f_iw[principal] >= 0
                dense[comp] = w[f_iw[principal[comp]]]
                ref[s:e] = dense
                inv = np.array_equal(dense, dense[principal])
                exact = np.allclose(dense[tconf], tweights)
                wm_ok = wm_ok and inv and exact
            check("E4 orbit invariance + seen-config exactness (both patterns)", wm_ok)
            check("E5 the full independent re-derivation == ctx.w_dense",
                  np.allclose(ref, ctx.w_dense.astype(np.float64), rtol=0, atol=0)
                  or np.array_equal(ref.astype(np.float32), ctx.w_dense))
            h = hashlib.sha3_256(ctx.w_dense.tobytes()).hexdigest()
            check("E7 hash golden ec9d6545...b15b4 == ctx.dense_w_checksum",
                  h == "ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15b4"
                  and h == ctx.dense_w_checksum, h)
            check("E8 the flat cache files rlmwf_10_GENERATE.dat + .SHA3-256 exist + verify",
                  (tmp / "rlmwf_10_GENERATE.dat").exists()
                  and binio.verify_sha3_256_sidecar(tmp / "rlmwf_10_GENERATE.dat"))
            # second instance: cache hit
            m2 = LogisticModel(str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_02.json"),
                               verbosity=Verbosity.LOW, base_dir_override=tmp)
            m2.move_to_step("GENERATE")
            check("E9 second instance: the GENERATE cache hit (w_dense identical)",
                  np.array_equal(m2.context.w_dense, ctx.w_dense))
            # the version gate on the real file (post T2): rewrite header v2
            with binio.BinaryReader(tmp / "rlmwf_10_GENERATE.dat") as r:
                desc, version = r.read_header()
            v2f = tmp / "v2.dat"
            with binio.BinaryWriter(v2f) as wwr:
                wwr.write_header(desc, 2)
                wwr.write_string(ctx.w_checksum)
                wwr.write_array(ctx.w_dense)
            try:
                rlm_generate_load_from_file(v2f, checksum=False)
                check("E10 version-2 file -> RuntimeError 'File version mismatch' (post T2)", False,
                      "loaded silently")
            except RuntimeError as e:
                check("E10 version-2 file -> RuntimeError 'File version mismatch' (post T2)",
                      "version mismatch" in str(e).lower(), str(e))
            # _down clearing
            from twolm.lm_worker_generate import lm_worker_generate
            lm_worker_generate().down(ctx)
            check("E11 _down clears w_dense + dense_w_checksum",
                  ctx.w_dense is None and ctx.dense_w_checksum is None)


# ----------------------------------------------------------------------
# F. context facts
# ----------------------------------------------------------------------
lm_src = read("src/twolm/logistic_model.py")
check("F1 RLMContext declares w_dense + dense_w_checksum (pre-declared, the D-094 fg pattern)",
      "    dense_w_checksum: str | None = None" in lm_src
      and "    w_dense: Any = None" in lm_src)
# (F2/F3 pipeline-state pins moved to the hub verify_logistic_model.py
# V3c/V3d at D-106)


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
