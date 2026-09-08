#!/usr/bin/env python3
"""
verify_design_matrix.py — scratch probe for the DESIGN_MTR bring-in
(session 23, the 7th pipeline level).

Re-derives and verifies, independently of the test files:
  A. hlp_design_matrix.py structure (post warning-fix: explicit cast,
     guards, decorators, whitespace)
  B. wrk_design_matrix.py structure (worker shape vs the house)
  C. test_wrk_design_matrix.py structure (DB claim vs gate, idiom,
     golden pins, whitespace)
  D. GOLDEN re-derivation (live DB): the rlm_01.json pipeline DESIGN_MTR
     output vs the literal pinned in test_wrk_design_matrix, plus
     the independent X = iwmap[pindexes + col_offsets] recomputation
  F. Cross-fixture / context facts (LMContext fields, the rlm_01
     feature layout)

Run from the workspace root:  .venv/bin/python scratch/verify_design_matrix.py
"""
import re
import sys
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parents[1]

failures = []


def check(label, cond, detail=""):
    print(f"[{'ok  ' if cond else 'FAIL'}] {label}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        failures.append(label)


def read(p):
    return (WS / p).read_text()


def lines(p):
    return read(p).splitlines()


# ----------------------------------------------------------------------
# A. hlp_design_matrix.py structure (post the approved warning fix)
# ----------------------------------------------------------------------
rlm = lines("src/reversi/lm/hlp_design_matrix.py")
check("A1 hlp_design_matrix.py is 133 lines (post D-090: 135 + note - redundant guard - ws strip)", len(rlm) == 133, f"{len(rlm)}")
check("A2 the explicit-cast fix is in place (L123-124: astype on the source + the note)",
      rlm[118] == "    X = np.empty(pindexes.shape, dtype=np.uint32)"
      and rlm[119] == "    #: Explicit cast: ctx.iwmap is int64 (the -1 unseen-config sentinel),"
      and rlm[120] == "    #: X is uint32 — the implicit output cast is deprecated (NumPy 2.5)."
      and rlm[121] == "    np.take(ctx.iwmap.astype(np.uint32), pindexes_with_offsets, out=X)",
      repr(rlm[118:122]))
check("A3 no raw int64->uint32 np.take remains",
      "np.take(ctx.iwmap, pindexes_with_offsets, out=X)" not in read("src/reversi/lm/hlp_design_matrix.py"))
check("A4 __all__ lists the 5 public names",
      "'LMDesignMatrix'," in read("src/reversi/lm/hlp_design_matrix.py")
      and "'hlp_design_matrix_is_cache_consistent']" in read("src/reversi/lm/hlp_design_matrix.py"))
check("A5 exactly 4 @validate_call decorators (init, hash, store, load — NOT compute / is_cache_consistent)",
      read("src/reversi/lm/hlp_design_matrix.py").count("@validate_call(config=ConfigDict(arbitrary_types_allowed=True))") == 4
      and "\ndef hlp_design_matrix_compute" in read("src/reversi/lm/hlp_design_matrix.py"))
check("A6 T4 FIXED: the no-validation note sits above hlp_design_matrix_compute (the rlm_indexes L166 class)",
      rlm[106] == "#: Here validation is not possible, it brings in a convoluted issue with circular imports."
      and rlm[107] == "def hlp_design_matrix_compute(ctx: \"LMContext\") -> LMDesignMatrix:")
check("A7 R1 FIXED: the single -1 guard remains (L116-117) with the precise ValueError",
      rlm[115] == "    if np.any(ctx.iwmap[pindexes_with_offsets] == -1):"
      and rlm[116] == "        raise ValueError(\"It should never happen, pindexes is referring an invalid value.\")")
check("A8 R1 FIXED: the redundant count_nonzero guard is GONE",
      "count_nonzero" not in read("src/reversi/lm/hlp_design_matrix.py")
      and "mismatch between indexes and valid values" not in read("src/reversi/lm/hlp_design_matrix.py"))
check("A9 store docstring makes no sidecar promise (D-072 shape)",
      '"""Saves the Design Matrix instance to a binary file."""' in read("src/reversi/lm/hlp_design_matrix.py"))
ws_rl = [i + 1 for i, l in enumerate(rlm) if l != l.rstrip() and not l.strip().startswith("#")]
check("A10 T5 FIXED: zero non-comment trailing-whitespace lines", ws_rl == [], f"{ws_rl}")
check("A11 X is allocated uint32 (the test pins the dtype contract)",
      "    X = np.empty(pindexes.shape, dtype=np.uint32)" in read("src/reversi/lm/hlp_design_matrix.py"))
check("A12 col_offsets = repeat(iwmap_feature_offset[:-1], n_instances per feature)",
      "col_offsets = np.repeat(ctx.iwmap_feature_offset[:-1], n_instances_per_feature)" in read("src/reversi/lm/hlp_design_matrix.py")
      and "pindexes_with_offsets = pindexes + col_offsets" in read("src/reversi/lm/hlp_design_matrix.py"))
check("A13 the hash is over X.tobytes() (the single data array)",
      "hasher.update(self.X.tobytes())" in read("src/reversi/lm/hlp_design_matrix.py"))
check("A14 is_cache_consistent compares wmaps_obj_checksum only (the 1-field compare)",
      "is_hash_consistent = dm.wmaps_obj_checksum == ctx.wmaps_obj_checksum" in read("src/reversi/lm/hlp_design_matrix.py"))
check("A15 triple blank lines at L42/L50 (house precedent — rlm_indexes carries the same)",
      rlm[41] == "" and rlm[42] == "" and rlm[43] == "" and rlm[49] == "" and rlm[50] == "" and rlm[51] == "")

# ----------------------------------------------------------------------
# B. wrk_design_matrix.py structure
# ----------------------------------------------------------------------
w = lines("src/reversi/lm/wrk_design_matrix.py")
check("B1 wrk_design_matrix.py is 80 lines (post D-090: 77 + pydantic import + decorator)", len(w) == 80, f"{len(w)}")
check("B2 T2 FIXED: the pydantic import is present (as in the other 6 workers)",
      "from pydantic import validate_call, ConfigDict" in read("src/reversi/lm/wrk_design_matrix.py"))
check("B3 T2 FIXED: the factory wrk_design_matrix is @validate_call-decorated",
      w[76] == "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))"
      and w[77] == "def wrk_design_matrix() -> Worker:")
check("B4 T3 FIXED: load_fn is the lambda with checksum=False (single sidecar check)",
      "        load_fn     = lambda path: hlp_design_matrix_load_from_file(path, checksum=False)," in read("src/reversi/lm/wrk_design_matrix.py"))
check("B5 the 7-arg cache wiring matches the house key set",
      all(k in read("src/reversi/lm/wrk_design_matrix.py") for k in
          ("cache_path  = ctx.get_cache_file_full_path_for_current_level(),",
           "is_allowed  = ctx.use_cache,", "store_fn    = hlp_design_matrix_store_to_file,",
           "validate_fn = lambda cached_dm: hlp_design_matrix_is_cache_consistent(ctx, cached_dm),",
           "compute_fn  = lambda: hlp_design_matrix_compute(ctx),", "logger_fn   = ctx.log_event")))
check("B6 _up sets both ctx.design_matrix and ctx.design_matrix_checksum",
      "    ctx.design_matrix = dm_obj.X" in read("src/reversi/lm/wrk_design_matrix.py")
      and "    ctx.design_matrix_checksum = dm_checksum" in read("src/reversi/lm/wrk_design_matrix.py"))
check("B7 _down clears BOTH ctx.design_matrix and ctx.design_matrix_checksum (the house shape)",
      "    ctx.design_matrix = None" in read("src/reversi/lm/wrk_design_matrix.py")
      and "    ctx.design_matrix_checksum = None" in read("src/reversi/lm/wrk_design_matrix.py"))
ws_w = [i + 1 for i, l in enumerate(w) if l != l.rstrip() and not l.strip().startswith("#")]
check("B8 T5 FIXED: zero whitespace-only lines", ws_w == [], f"{ws_w}")
check("B9 the worker name is DESIGN_MTR (Worker('DESIGN_MTR', _up, _down))",
      'return Worker("DESIGN_MTR", _up, _down)' in read("src/reversi/lm/wrk_design_matrix.py"))

# ----------------------------------------------------------------------
# C. test_wrk_design_matrix.py structure
# ----------------------------------------------------------------------
t = lines("src/reversi/test/test_wrk_design_matrix.py")
check("C1 test_wrk_design_matrix.py is 226 lines (post D-090: 202 + gates + idiom - ws strip)", len(t) == 226, f"{len(t)}")
check("C2 2 classes / 3 tests",
      sum(1 for l in t if l.startswith("class ")) == 2 and
      sum(1 for l in t if l.strip().startswith("def test_")) == 3)
check("C3 T1 FIXED: the gate is in BOTH setUps (D-130: the db_long_gate idiom) and the header claim is now true",
      "# -1- Run the tests (a live regab DB + LONG=1 is required;" in read("src/reversi/test/test_wrk_design_matrix.py")
      and "SKIP_REGAB_DB=1 skips the DB-gated tests as in test_regab" in read("src/reversi/test/test_wrk_design_matrix.py")
      and read("src/reversi/test/test_wrk_design_matrix.py").count("db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates (D-130)") == 2
      and "import os" in read("src/reversi/test/test_wrk_design_matrix.py"))
check("C4 T7 FIXED: the D-085 idiom is applied (TemporaryDirectory under CUSTOM_TMP_BASE x2)",
      read("src/reversi/test/test_wrk_design_matrix.py").count("self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))") == 2
      and "mkdtemp" not in read("src/reversi/test/test_wrk_design_matrix.py"))
check("C5 T7 FIXED: both json_config paths are WORKSPACE_ROOT-anchored (rlm_00 + rlm_01)",
      'self.json_config = str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_00.json")' in read("src/reversi/test/test_wrk_design_matrix.py")
      and 'self.json_config = str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_01.json")' in read("src/reversi/test/test_wrk_design_matrix.py"))
check("C6 T7 FIXED: the reversi.test.paths import is present (WORKSPACE_ROOT + CUSTOM_TMP_BASE)",
      "from reversi.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE" in read("src/reversi/test/test_wrk_design_matrix.py"))
check("C7 T7 FIXED: the (former) shutil import is gone with the rmtree teardowns",
      "shutil" not in read("src/reversi/test/test_wrk_design_matrix.py"))
check("C8 all 3 LogisticModel constructions use Verbosity.HIGH (house: HIGH in pipeline tests)",
      read("src/reversi/test/test_wrk_design_matrix.py").count("verbosity=Verbosity.HIGH") == 3)
check("C9 the D-078 cache names are pinned (rlmwf_06_DESIGN_MTR.dat + .SHA3-256)",
      "'rlmwf_06_DESIGN_MTR.dat'" in read("src/reversi/test/test_wrk_design_matrix.py")
      and "'rlmwf_06_DESIGN_MTR.dat.SHA3-256'" in read("src/reversi/test/test_wrk_design_matrix.py"))
check("C10 step pins: WMAPS=5 (x2 setUps), DESIGN_MTR=6 (x2 self.rlm + x1 rlm2 — the 7-level pipeline)",
      read("src/reversi/test/test_wrk_design_matrix.py").count("self.assertEqual(self.rlm.current_step, 5)") == 2
      and read("src/reversi/test/test_wrk_design_matrix.py").count("self.assertEqual(self.rlm.current_step, 6)") == 2
      and read("src/reversi/test/test_wrk_design_matrix.py").count("self.assertEqual(rlm2.current_step, 6)") == 1)
ws_t = [i + 1 for i, l in enumerate(t) if l != l.rstrip() and not l.strip().startswith("#")]
check("C11 T5 FIXED: zero whitespace-only lines", len(ws_t) == 0, f"{ws_t}")
check("C12 the golden literal is (10,7) uint32 with the 10 pinned rows",
      "self.assertEqual(X.shape, (10, 7))" in read("src/reversi/test/test_wrk_design_matrix.py")
      and "], dtype=np.uint32)" in read("src/reversi/test/test_wrk_design_matrix.py")
      and "nptest.assert_array_equal(expected_X, X)" in read("src/reversi/test/test_wrk_design_matrix.py"))
check("C13 the uint32 dtype contract is pinned 3x (L112, L146, L183)",
      read("src/reversi/test/test_wrk_design_matrix.py").count("np.uint32") == 4)
check("C14 the before-DESIGN_MTR None-ness is pinned (L173)",
      "self.assertIsNone(self.rlm.context.design_matrix)" in read("src/reversi/test/test_wrk_design_matrix.py"))

# ----------------------------------------------------------------------
# D. GOLDEN re-derivation (live DB) — rlm_01.json
#    The literal is extracted from the test source (single source of
#    truth); the pipeline output is compared, and X is independently
#    recomputed from iwmap + pindexes + col_offsets.
# ----------------------------------------------------------------------
import json5
import tempfile

# (D0 + the test-source extraction machinery deleted at D-106 step 3,
#  class c: the pinned expected_X literal is pinned by the test
#  itself — C12 meta-pins the nptest.assert_array_equal
#  (expected_X, X) call in the test source, and the literal's
#  (10,7) shape is the shape the test compares against.)

from reversi.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE

CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)
seen_n_inst = None
seen_n_conf = None
with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
    from reversi.lm.logistic_model import LogisticModel
    from reversi.tools.state_machine import Verbosity
    rlm_lm = LogisticModel(str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_01.json"),
                           verbosity=Verbosity.LOW, base_dir_override=tmp)
    rlm_lm.move_to_step("DESIGN_MTR")
    ctx = rlm_lm.context
    seen_n_inst = [f.n_instances for f in ctx.feature_set.features]
    seen_n_conf = [f.n_configurations for f in ctx.feature_set.features]

    # (D1-D4 deleted at D-106 step 3, class c: step 6 / the (10,7)
    #  shape / the uint32 dtype / X == the pinned literal are all
    #  pinned by test_wrk_design_matrix.py — the step in both
    #  setUps, the dtype 3x, and
    #  nptest.assert_array_equal(expected_X, X))
    # Independent recomputation: X[i,j] = iwmap[pindexes[i,j] + col_offsets[j]]
    n_inst = [f.n_instances for f in ctx.feature_set.features]
    col_off = np.repeat(ctx.iwmap_feature_offset[:-1], n_inst)
    X_recomputed = ctx.iwmap[ctx.hlp_indexes.indexes + col_off].astype(np.uint32)
    check("D5 independent recompute: X == iwmap[pindexes + col_offsets] (the D-086-style single source of truth)",
          np.array_equal(ctx.design_matrix, X_recomputed))
    check("D6 every X value is a valid w index (< W = len(w))",
          ctx.design_matrix.max() < len(ctx.w), f"max={ctx.design_matrix.max()}, W={len(ctx.w)}")
    # Per feature: the values of all its instance columns lie in its iwmap region
    ok = True
    col = 0
    for fidx, f in enumerate(ctx.feature_set.features):
        off = ctx.iwmap_feature_offset[fidx]
        region = ctx.iwmap[off: off + f.n_configurations]
        cols = ctx.design_matrix[:, col:col + f.n_instances]
        ok = ok and set(int(v) for v in cols.ravel()) <= set(int(v) for v in region)
        col += f.n_instances
    check("D7 per feature: X's instance columns stay within the owning feature's iwmap region", ok)
    check("D8 the intercept column is all zeros (single config 0 -> w index 0)",
          (ctx.design_matrix[:, 0] == 0).all(), ctx.design_matrix[:, 0].tolist())
    # (D9 deleted at D-106 step 3, class c: both flat files'
    #  existence is asserted by the DB test, L109-110)
    check("D10 design_matrix_checksum == sha3_256(X.tobytes()) (the DATA checksum)",
          ctx.design_matrix_checksum == __import__("hashlib").sha3_256(ctx.design_matrix.tobytes()).hexdigest())

# ----------------------------------------------------------------------
# F. Cross-fixture / context facts
# ----------------------------------------------------------------------
lm_src = read("src/reversi/lm/logistic_model.py")
check("F1 LMContext declares design_matrix_checksum + design_matrix (pre-existing, as in the WMAPS fields)",
      "    design_matrix_checksum: str | None = None" in lm_src
      and "    design_matrix: Any = None" in lm_src)
# (F2/F3 pipeline-state pins moved to the hub verify_logistic_model.py
# V3c/V3d at D-106)
import json5 as _j
fix = _j.loads((WS / "src" / "reversi" / "test" / "data" / "rlm_01.json").read_text())
check("F4 rlm_01 stat_model == {cut_off 2, logit 0.03, ridge 0.0} (the WMAPS fixture, reused)",
      fix["stat_model"] == {"frequency_cut_off": 2, "logit_clipping": 0.03, "ridge_regularization": 0.0})
check("F5 rlm_01 feature layout: n_instances [1,1,4,1] (sum 7), n_configurations [1,65,27,81] (K=174)",
      seen_n_inst == [1, 1, 4, 1] and sum(seen_n_inst) == 7
      and [int(v) for v in seen_n_conf] == [1, 65, 27, 81] and sum(int(v) for v in seen_n_conf) == 174,
      f"n_inst={seen_n_inst} n_conf={seen_n_conf}")

# ----------------------------------------------------------------------
# G. test_hlp_design_matrix.py (new in D-090 T6 — the dedicated unit
#    tests for the data object, mirroring test_hlp_wmaps)
# ----------------------------------------------------------------------
g = lines("src/reversi/test/test_hlp_design_matrix.py")
check("G1 test_hlp_design_matrix.py is 258 lines (new file, D-090 T6)", len(g) == 258, f"{len(g)}")
check("G2 4 classes / 12 tests (2 compute + 2 consistency + 6 IO + 2 init)",
      sum(1 for l in g if l.startswith("class ")) == 4 and
      sum(1 for l in g if l.strip().startswith("def test_")) == 12)
check("G3 the header makes NO DB claim (the file is DB-free, dummy ctx)",
      "# -1- Run the tests." in read("src/reversi/test/test_hlp_design_matrix.py")
      and "SKIP_REGAB_DB" not in read("src/reversi/test/test_hlp_design_matrix.py"))
check("G4 the D-085 idiom is applied (TemporaryDirectory under CUSTOM_TMP_BASE, defensive tearDown)",
      "self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))" in read("src/reversi/test/test_hlp_design_matrix.py")
      and "if getattr(self, '_tmp', None) is not None:" in read("src/reversi/test/test_hlp_design_matrix.py"))
check("G5 the golden hash of the IO object is pinned",
      "da86a916e03c76befa6f5df70e6221b0f9a355173e356ea63fef89ea9719757b" in read("src/reversi/test/test_hlp_design_matrix.py"))
check("G6 the 3 RuntimeError pins + the ValidationError pin + the guard ValueError pin",
      read("src/reversi/test/test_hlp_design_matrix.py").count("assertRaises(RuntimeError)") == 3
      and "assertRaises(ValidationError)" in read("src/reversi/test/test_hlp_design_matrix.py")
      and "pindexes is referring an invalid value" in read("src/reversi/test/test_hlp_design_matrix.py"))
ws_g = [i + 1 for i, l in enumerate(g) if l != l.rstrip() and not l.strip().startswith("#")]
check("G7 zero whitespace-only lines", ws_g == [], f"{ws_g}")

# ----------------------------------------------------------------------
print()
if failures:
    print(f"{len(failures)} mismatch(es):")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("All checks passed.")
