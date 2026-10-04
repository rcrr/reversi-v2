#!/usr/bin/env python3
"""
verify_generate.py — scratch probe for the GENERATE bring-in (session 27).

Re-derives and verifies, independently of the test files:
  A. hlp_generate.py structure (post-campaign: note, version gate, ws)
  B. wrk_generate.py structure (post-campaign: factory gate, the
     the _for_current_level naming, ws)
  C. test_hlp_generate.py structure (post-campaign: English comment, ws)
  D. data-object behavior (no DB): init validation, hash, store/load
     round-trip, the sidecar / description / version gates, the
     is_cache_consistent branches, the test-mock fixture goldens
     (independently re-derived by hand), the error branches
  E. GOLDEN re-derivation (live DB, gated on SKIP_REGAB_DB): the
     rlm_02.json pipeline to GENERATE — K, the per-feature weighted
     means, orbit invariance, the seen-config exactness, the full
     independent re-derivation, the hash golden, the file naming,
     the second-instance cache hit, the _down clearing, the version gate
  F. context facts (LMContext pre-declared fields)

Pinned to the POST-campaign state: the A/B/C structural checks and the
E1/E11 + D6 behavior pins FAIL until the fix campaign is applied
(R1 the _for_next_level name, T2 the missing version gate, the T/M
hygiene items).

Run from the workspace root:  .venv/bin/python scratch/verify_generate.py
"""
import hashlib
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
# A. hlp_generate.py structure (post-campaign)
# ----------------------------------------------------------------------
rlm_src = read("src/reversi/lm/hlp_generate.py")
check("A1 __all__ lists the 5 public names",
      "'LMDenseWeights'," in rlm_src
      and "'hlp_generate_store_to_file'," in rlm_src
      and "'hlp_generate_load_from_file'," in rlm_src
      and "'compute_w_dense'," in rlm_src
      and "'hlp_generate_is_cache_consistent']" in rlm_src)
above_compute = rlm_src.split("def compute_w_dense")[0]
check("A2 the house no-validation note sits directly above compute_w_dense",
      "Here validation is not possible" in "\n".join(above_compute.rsplit("\n", 8)[1:]),
      "last 8 lines above the def: " + repr(above_compute.rsplit("\n", 8)[-6:]))
check("A3 hlp_generate_is_cache_consistent carries the no-validation note too",
      "Here validation is not possible" in "\n".join(rlm_src.split("def hlp_generate_is_cache_consistent")[0].rsplit("\n", 8)[1:]))
check("A4 load gates the file version (the 4 sibling data modules all do — T2)",
      "expected_version" in rlm_src
      and "File version mismatch" in rlm_src)
check("A5 no non-comment trailing whitespace",
      not ws_lines("src/reversi/lm/hlp_generate.py"),
      f"lines {ws_lines('src/reversi/lm/hlp_generate.py')}")

# ----------------------------------------------------------------------
# B. wrk_generate.py structure (post-campaign)
# ----------------------------------------------------------------------
wk_src = read("src/reversi/lm/wrk_generate.py")
check("B1 the worker uses the house name _for_current_level (the "
      "pre-campaign _for_next_level call is the R1 AttributeError)",
      "get_cache_file_full_path_for_current_level" in wk_src
      and "for_next_level" not in wk_src)
check("B2 the factory is @validate_call-decorated + pydantic imported "
      "(all 10 sibling worker factories — D-092 T2 / D-096 T10 pattern)",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef wrk_generate" in wk_src
      and "from pydantic import validate_call, ConfigDict" in wk_src)
check("B3 no non-comment trailing whitespace",
      not ws_lines("src/reversi/lm/wrk_generate.py"),
      f"lines {ws_lines('src/reversi/lm/wrk_generate.py')}")

# ----------------------------------------------------------------------
# C. test_hlp_generate.py structure (post-campaign)
# ----------------------------------------------------------------------
test_src = read("test/reversi/lm/test_hlp_generate.py")
check("C1 the Italian comment is gone (AGENTS.md rule 4 — house fix D-084 T3 class)",
      "AGGIUNTO" not in test_src)
check("C2 no non-comment trailing whitespace",
      not ws_lines("test/reversi/lm/test_hlp_generate.py"),
      f"lines {ws_lines('test/reversi/lm/test_hlp_generate.py')}")

# ----------------------------------------------------------------------
# D. data-object behavior (no DB)
# ----------------------------------------------------------------------
from reversi.lm.hlp_generate import (LMDenseWeights,
                                compute_w_dense)

from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE

CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
    tmp = Path(tmp)

    # (D1 list w_dense rejected / D2 non-str w_checksum rejected
    #  deleted at D-106 step 3, class c: test_hlp_generate.py::
    #  TestHlpGenerateInit::test_init_fails_with_list_w_dense /
    #  test_init_fails_with_non_str_w_checksum)

    # D3 hash
    arr = np.array([0.5, -0.2, 3.0], dtype=np.float32)
    dw = LMDenseWeights("abc", arr)
    h = hashlib.sha3_256(arr.tobytes()).hexdigest()
    check("D3 compute_sha3_256_hash == independent sha3_256(w_dense.tobytes())",
          dw.compute_sha3_256_hash() == h, dw.compute_sha3_256_hash())

    # (D4 store/load round-trip + sidecar, D5 corrupted sidecar ->
    #  'Checksum mismatch.', D6 wrong description -> 'Wrong file
    #  format', D7 version-2 gate, D8 checksum=False load, D9/D10
    #  is_cache_consistent True/False deleted at D-106 step 3, class
    #  c: test_hlp_generate.py::TestHlpGenerateIO pins all of it —
    #  test_store_and_load_cycle (round-trip + the
    #  checksum=False load at L241 + the valid sidecar),
    #  test_load_with_mismatched_sidecar,
    #  test_load_rejects_wrong_description,
    #  test_load_rejects_version_mismatch, and
    #  TestHlpGenerateCacheConsistency::test_consistent_checksum /
    #  test_inconsistent_checksum. The file-building scaffolding
    #  (BinaryWriter blocks, the Ctx/Ctx2 fakes) was used only by
    #  them.)

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

    # (D12 unknown category -> RuntimeError + D13 mobility no-seen
    #  branch (zeros + WARN) deleted at D-106 step 3, class c:
    #  test_hlp_generate.py::TestHlpGenerateCompute::
    #  test_unknown_category_raises /
    #  test_mobility_without_seen_configs_warns_and_zeroes. The
    #  ctx_bad / ctx_m scaffolding was used only by them.)


# ----------------------------------------------------------------------
# E. GOLDEN re-derivation (live DB) — the rlm_02.json pipeline
# ----------------------------------------------------------------------
if os.getenv("SKIP_REGAB_DB", "0") == "1":
    skip("E-tier (live DB golden re-derivation)", "SKIP_REGAB_DB=1")
else:
    with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
        tmp = Path(tmp)
        from reversi.lm.logistic_model import LogisticModel
        from reversi.tools.state_machine import Verbosity
        m = LogisticModel(str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_02.json"),
                          verbosity=Verbosity.LOW, base_dir_override=tmp)
        # (E1 'the pipeline reaches GENERATE' deleted at D-106 step 3,
        #  class c: test_wrk_generate.py::TestLMWorkerGenerate::
        #  test_compute_and_populate_cache pins step 10 / GENERATE)
        try:
            m.move_to_step("GENERATE")
            crashed = False
        except AttributeError:
            crashed = True
        ctx = m.context
        w, iwmap, off, wmap, fwr = ctx.w, ctx.iwmap, ctx.iwmap_feature_offset, ctx.wmap, ctx.feature_w_ranges

        if not crashed:
            K = int(off[-1])
            check("E2 K = 6588 = 6561 (EDGE) + 27 (DIAG3)", K == 6588, f"{K}")
            # (E3 w_dense shape/dtype (6588,) float32 deleted at D-106
            #  step 3, class c: test_wrk_generate.py L128-129)
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
            # (E8 flat cache files + sidecar verify deleted at D-106
            #  step 3, class c: test_wrk_generate.py pins both
            #  files. E9 second-instance cache hit + w_dense identity
            #  -> c: test_read_cache_on_new_instance
            #  (nptest.assert_array_equal). E10 version-2 gate on the
            #  real file -> c: test_load_rejects_version_mismatch.
            #  E11 _down scope -> c:
            #  test_down_clears_generate_attributes. The second
            #  instance run and the v2 header rewrite were used only
            #  by them.)


# ----------------------------------------------------------------------
# F. context facts
# ----------------------------------------------------------------------
lm_src = read("src/reversi/lm/logistic_model.py")
check("F1 LMContext declares w_dense + dense_w_checksum (pre-declared, the D-094 fg pattern)",
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
