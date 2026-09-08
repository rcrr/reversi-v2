#!/usr/bin/env python3
"""
verify_wmaps.py — scratch probe for the WMAPS bring-in (session 23).

Re-derives and verifies, independently of the test files:
  A. hlp_wmaps.py structure (post D-087: lines, imports, note, contract, ws)
  B. wrk_wmaps.py structure (post D-087: worker shape vs the house)
  C. test_hlp_wmaps.py structure (post D-087: header, idiom, new coverage)
  D. test_wrk_wmaps.py structure (post D-087: gate, idiom, ws)
  E. GOLDEN re-derivation (live DB): the rlm_01.json pipeline WMAPS output
     vs the literals pinned in test_wrk_wmaps.TestLMWorkerWmapsExactValues
  F. Cross-fixture / context facts (rlm_01 stat_model, LMContext fields)

Re-pinned in D-087 to the post-campaign state (all T items pinned FIXED,
R1 pinned as the documented no-guard contract). 64 checks.

Run from the workspace root:  .venv/bin/python scratch/verify_wmaps.py
"""
import re
import sys
from pathlib import Path

import numpy as np

WS = Path(__file__).resolve().parents[1]
SRC = WS / "src" / "reversi"

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
# A. hlp_wmaps.py structure (post D-087)
# ----------------------------------------------------------------------
rlm = lines("src/reversi/lm/hlp_wmaps.py")
check("A1 hlp_wmaps.py is 316 lines (post D-087: 311 - accumulate + note + contract + 0 ws net)", len(rlm) == 316, f"{len(rlm)}")
check("A2 the dead accumulate import is gone (D-087 T4)",
      "from itertools import accumulate" not in read("src/reversi/lm/hlp_wmaps.py")
      and "accumulate" not in read("src/reversi/lm/hlp_wmaps.py"))
check("A3 __all__ lists the 5 public names",
      "'ReversiLogisticModelWMaps'," in read("src/reversi/lm/hlp_wmaps.py")
      and "'hlp_wmaps_is_cache_consistent']" in read("src/reversi/lm/hlp_wmaps.py"))
check("A4 compute_sha3_256_hash is @validate_call-decorated",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\n    def compute_sha3_256_hash" in read("src/reversi/lm/hlp_wmaps.py"))
check("A5 hlp_wmaps_compute has NO @validate_call but the no-validation note (L181, the rlm_indexes style — D-087 T5)",
      "\n@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef hlp_wmaps_compute" not in read("src/reversi/lm/hlp_wmaps.py")
      and rlm[180] == "#: Here validation is not possible, it brings in a convoluted issue with circular imports.",
      repr(rlm[180]))
check("A6 hlp_wmaps_is_cache_consistent has NO @validate_call (same constraint, as in rlm_indexes)",
      "\n@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef hlp_wmaps_is_cache_consistent" not in read("src/reversi/lm/hlp_wmaps.py"))
check("A7 the R1 contract is documented in the compute docstring (D-087 R1 — dense by contract, no guard)",
      "The input pindexes matrix is dense by contract: every cell holds a" in read("src/reversi/lm/hlp_wmaps.py")
      and "are unsigned and never -1 — D-086 R1" in read("src/reversi/lm/hlp_wmaps.py"))
check("A8 store docstring makes no sidecar promise (D-072 shape)",
      '"""Saves the WMaps instance to a binary file."""' in read("src/reversi/lm/hlp_wmaps.py"))
ws_rl = [i + 1 for i, l in enumerate(rlm) if l != l.rstrip() and not l.strip().startswith("#")]
check("A9 0 non-comment trailing-whitespace lines (D-087 T9: 23 stripped)", len(ws_rl) == 0, f"{ws_rl}")
check("A10 the above_mask code line is clean (L280, no trailing space)",
      rlm[279] == "        above_mask = ~mask", repr(rlm[279]))
check("A11 the fallback_details_table code line is clean (L293, no trailing spaces)",
      rlm[292] == "    fallback_details_table = np.array(fallback_data, dtype=np.int64)", repr(rlm[292]))
check("A12 the -1 input sentinel is unguarded at L257 — correct by the R1 dense contract (no guard added)",
      rlm[256] == "        f_iwmap[stats[:, 0].astype(np.int64)] = stats[:, 2]", repr(rlm[256]))

# ----------------------------------------------------------------------
# B. wrk_wmaps.py structure (post D-087)
# ----------------------------------------------------------------------
w = lines("src/reversi/lm/wrk_wmaps.py")
check("B1 wrk_wmaps.py is 91 lines (post D-087: 87 + pydantic + decorator + checksum clear)", len(w) == 91, f"{len(w)}")
check("B2 the pydantic import is present (L32 — D-087 T6)", w[31] == "from pydantic import validate_call, ConfigDict", repr(w[31]))
check("B3 the factory wrk_wmaps is @validate_call-decorated (L88 — D-087 T6)",
      w[87] == "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))" and w[88] == "def wrk_wmaps() -> Worker:",
      repr(w[87:89]))
check("B4 load_fn is the house lambda with checksum=False (L56 — D-087 T7)",
      w[55] == "        load_fn     = lambda path: hlp_wmaps_load_from_file(path, checksum=False),", repr(w[55]))
check("B5 the 7-arg cache wiring matches the house key set",
      all(k in read("src/reversi/lm/wrk_wmaps.py") for k in
          ("cache_path  = ctx.get_cache_file_full_path_for_current_level(),",
           "is_allowed  = ctx.use_cache,", "store_fn    = hlp_wmaps_store_to_file,",
           "validate_fn = lambda cached_wmaps: hlp_wmaps_is_cache_consistent(ctx, cached_wmaps),",
           "compute_fn  = lambda: hlp_wmaps_compute(ctx),", "logger_fn   = ctx.log_event")))
check("B6 _down clears ctx.wmaps_obj_checksum (L85 — D-087 T8, the house shape)",
      w[84] == "    ctx.wmaps_obj_checksum = None", repr(w[84]))
check("B7 _up sets the 6 ctx arrays + wmaps_obj_checksum (the 7 attributes)",
      all(f"ctx.{a} = wmaps_obj.{a}" in read("src/reversi/lm/wrk_wmaps.py")
          for a in ("feature_w_ranges", "iwmap_feature_offset", "iwmap", "wmap", "wmap_fallback", "w"))
      and "ctx.wmaps_obj_checksum = wmaps_obj_checksum" in read("src/reversi/lm/wrk_wmaps.py"))
ws_w = [i + 1 for i, l in enumerate(w) if l != l.rstrip() and not l.strip().startswith("#")]
check("B8 0 whitespace-only lines (D-087 T9: 4 stripped)", ws_w == [], f"{ws_w}")
check("B9 the triple blank line before _up is intact (L47-49, pre-existing)", w[46] == "" and w[47] == "" and w[48] == "")

# ----------------------------------------------------------------------
# C. test_hlp_wmaps.py structure (post D-087)
# ----------------------------------------------------------------------
t1 = lines("src/reversi/test/test_hlp_wmaps.py")
check("C1 test_hlp_wmaps.py is 325 lines (post D-087: 259 + 7 new tests - import/comment/ws net)", len(t1) == 325, f"{len(t1)}")
check("C2 4 classes / 13 tests (the 2 compute + 3 consistency + 6 IO + 2 init since D-087 T10)",
      sum(1 for l in t1 if l.startswith("class ")) == 4 and
      sum(1 for l in t1 if l.strip().startswith("def test_")) == 13)
check("C3 the header is corrected (L38: '-1- Run the tests.' — the file is DB-free, D-087 T2)",
      t1[37] == "# -1- Run the tests.", repr(t1[37]))
check("C4 no SKIP_REGAB_DB mention anywhere in the file (no gate needed — no DB)",
      read("src/reversi/test/test_hlp_wmaps.py").count("SKIP_REGAB_DB") == 0)
check("C5 no DB import in the file", "from reversi.regab" not in read("src/reversi/test/test_hlp_wmaps.py")
      and "import regab" not in read("src/reversi/test/test_hlp_wmaps.py"))
check("C6 D-085 idiom applied: setUpClass (L207) + TemporaryDirectory under CUSTOM_TMP_BASE (L213)",
      t1[206] == "    def setUpClass(cls):"
      and t1[212] == "        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))",
      repr(t1[212]))
check("C7 defensive tearDown (getattr _tmp guard, no shutil)",
      "        if getattr(self, '_tmp', None) is not None:" in read("src/reversi/test/test_hlp_wmaps.py")
      and "shutil" not in read("src/reversi/test/test_hlp_wmaps.py"))
check("C8 the D-085 paths import is present (L60)",
      t1[59] == "from reversi.test.paths import CUSTOM_TMP_BASE", repr(t1[59]))
check("C9 the dead StringIO AND patch imports are gone (D-087 T4)",
      "StringIO" not in read("src/reversi/test/test_hlp_wmaps.py")
      and "unittest.mock" not in read("src/reversi/test/test_hlp_wmaps.py")
      and "patch" not in read("src/reversi/test/test_hlp_wmaps.py"))
check("C10 the leftover generation comment is gone (D-087 T3)",
      "sostituisci" not in read("src/reversi/test/test_hlp_wmaps.py"))
ws_t1 = [i + 1 for i, l in enumerate(t1) if l != l.rstrip() and not l.strip().startswith("#")]
check("C11 0 whitespace-only lines (D-087 T9: 21 stripped)", len(ws_t1) == 0, f"{ws_t1}")
check("C12 the store/load cycle still pins checksum=False on both sides",
      "hlp_wmaps_store_to_file(self.wmaps_original, self.filepath)" in read("src/reversi/test/test_hlp_wmaps.py")
      and "hlp_wmaps_load_from_file(self.filepath, checksum=False)" in read("src/reversi/test/test_hlp_wmaps.py"))
check("C13 the golden-hash test is present with the pinned literal (D-087 T10)",
      "def test_compute_sha3_256_hash_golden" in read("src/reversi/test/test_hlp_wmaps.py")
      and "12c3344ec23c798d7b35eb6eae01034b29ee5c539bfb2018ca2eabc73c861dfa" in read("src/reversi/test/test_hlp_wmaps.py"))
check("C14 the 4 new load-path tests are present (D-087 T10: sidecar valid/mismatch, description, version)",
      all(f"def {n}" in read("src/reversi/test/test_hlp_wmaps.py")
          for n in ("test_load_with_valid_sidecar", "test_load_with_mismatched_sidecar",
                    "test_load_rejects_wrong_description", "test_load_rejects_version_mismatch")))
check("C15 the TestRLMWmapsInit class is present with the precise ValidationError (D-087 T10)",
      "class TestRLMWmapsInit" in read("src/reversi/test/test_hlp_wmaps.py")
      and "from pydantic import ValidationError" in read("src/reversi/test/test_hlp_wmaps.py")
      and "assertRaises(ValidationError)" in read("src/reversi/test/test_hlp_wmaps.py"))

# ----------------------------------------------------------------------
# D. test_wrk_wmaps.py structure (post D-087)
# ----------------------------------------------------------------------
t2 = lines("src/reversi/test/test_wrk_wmaps.py")
check("D1 test_wrk_wmaps.py is 315 lines (post D-087: 301 + 2 gates - ws net)", len(t2) == 315, f"{len(t2)}")
check("D2 2 classes / 3 tests",
      sum(1 for l in t2 if l.startswith("class ")) == 2 and
      sum(1 for l in t2 if l.strip().startswith("def test_")) == 3)
check("D3 the SKIP_REGAB_DB gate exists in BOTH setUps (D-087 T1; D-130: the db_long_gate idiom)",
      t2[73] == "        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates (D-130)"
      and t2[175] == "        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates (D-130)",
      repr(t2[73:75]))
check("D4 import os is present (L46 — for the gate)", t2[45] == "import os", repr(t2[45]))
check("D5 both setUps use the D-085 TemporaryDirectory idiom (L82, L183)",
      t2[81] == "        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))"
      and t2[182] == "        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))",
      repr(t2[81]))
check("D6 both setUps anchor json_config to WORKSPACE_ROOT (L84 rlm_00, L185 rlm_01)",
      t2[83] == "        self.json_config = str(WORKSPACE_ROOT / \"src\" / \"reversi\" / \"test\" / \"data\" / \"rlm_00.json\")"
      and t2[184] == "        self.json_config = str(WORKSPACE_ROOT / \"src\" / \"reversi\" / \"test\" / \"data\" / \"rlm_01.json\")",
      repr(t2[83]))
check("D7 the D-085 paths import is present (L58)",
      t2[57] == "from reversi.test.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT", repr(t2[57]))
check("D8 all 3 LogisticModel constructions use Verbosity.HIGH (house: HIGH in pipeline tests)",
      read("src/reversi/test/test_wrk_wmaps.py").count("verbosity=Verbosity.HIGH") == 3)
check("D9 the D-078 cache names are pinned (rlmwf_05_WMAPS.dat + .SHA3-256)",
      "'rlmwf_05_WMAPS.dat'" in read("src/reversi/test/test_wrk_wmaps.py")
      and "'rlmwf_05_WMAPS.dat.SHA3-256'" in read("src/reversi/test/test_wrk_wmaps.py"))
check("D10 step pins: INDEXES=4, WMAPS=5 (the 6-level pipeline)",
      "self.assertEqual(self.rlm.current_step, 4)" in read("src/reversi/test/test_wrk_wmaps.py")
      and "self.assertEqual(self.rlm.current_step, 5)" in read("src/reversi/test/test_wrk_wmaps.py"))
ws_t2 = [i + 1 for i, l in enumerate(t2) if l != l.rstrip() and not l.strip().startswith("#")]
check("D11 0 whitespace-only lines (D-087 T9: 20 stripped)", len(ws_t2) == 0, f"{ws_t2}")
check("D12 defensive tearDown in both classes (getattr guards, no shutil)",
      read("src/reversi/test/test_wrk_wmaps.py").count("        if getattr(self, '_tmp', None) is not None:") == 2
      and "shutil" not in read("src/reversi/test/test_wrk_wmaps.py"))

# ----------------------------------------------------------------------
# E. GOLDEN re-derivation (live DB) — rlm_01.json
#    The literals are extracted from the test source (single source of
#    truth); the pipeline output is compared against them.
# ----------------------------------------------------------------------
import json5
import tempfile

# (E0 + the test-source extraction machinery deleted at D-106
#  step 3, class c: the five expected_* literals are pinned verbatim
#  by test_wrk_wmaps.py::test_compute_wmaps_exact_values, so
#  extracting them and comparing was tautological.)

from reversi.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE

CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
    from reversi.lm.logistic_model import LogisticModel
    from reversi.tools.state_machine import Verbosity
    rlm_lm = LogisticModel(str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_01.json"),
                           verbosity=Verbosity.LOW, base_dir_override=tmp)
    rlm_lm.move_to_step("WMAPS")
    ctx = rlm_lm.context

    # (E1-E6 deleted at D-106 step 3, class c: feature_w_ranges,
    #  iwmap_feature_offset, iwmap, wmap, wmap_fallback, w are all
    #  pinned verbatim (full literal, shape + dtype) by
    #  test_wrk_wmaps.py::test_compute_wmaps_exact_values —
    #  the probe's comparisons against its own extracted literals
    #  were tautological.)
    # (E7/E8 deleted at D-106 step 3, class c: both operate on the
    #  pinned literals, which the test pins verbatim — the fallback
    #  freq sums and the no-(-1)-sentinel property are implied.)
    # E9 — the w index ranges per feature are contiguous
    ok = True
    for fid in range(len(ctx.feature_w_ranges)):
        fb, wmin, wmax = ctx.feature_w_ranges[fid]
        ok = ok and ((ctx.wmap[ctx.wmap[:, 0] == fid].shape[0]) == wmax - wmin + 1)
    check("E9 per-feature wmap row count == w_max - w_min + 1 (contiguous ranges)", ok)

# ----------------------------------------------------------------------
# F. Cross-fixture / context facts
# ----------------------------------------------------------------------
fix = json5.loads((WS / "src" / "reversi" / "test" / "data" / "rlm_01.json").read_text())
sm = fix["stat_model"]
check("F1 rlm_01 stat_model == {cut_off 2, logit 0.03, ridge 0.0}",
      sm == {"frequency_cut_off": 2, "logit_clipping": 0.03, "ridge_regularization": 0.0}, repr(sm))
fix0 = json5.loads((WS / "src" / "reversi" / "test" / "data" / "rlm_00.json").read_text())
check("F2 rlm_00 stat_model == {cut_off 1, logit 0.05, ridge 0.0}",
      fix0["stat_model"] == {"frequency_cut_off": 1, "logit_clipping": 0.05, "ridge_regularization": 0.0})
check("F3 rlm_01 use_cache is True, cache prefix 'rlmwf_' (D-078)",
      fix["use_cache"] is True and fix["cache_files_prefix"] == "rlmwf_")
lm_src = read("src/reversi/lm/logistic_model.py")
# (F4/F6 pipeline-state pins moved to the hub verify_logistic_model.py
# V3c/V3d at D-106)
check("F5 LMContext declares the 7 Wmaps fields (pre-existing, untouched by the commit)",
      all(f"    {a}: " in lm_src for a in
          ("wmaps_obj_checksum", "feature_w_ranges", "iwmap_feature_offset", "iwmap",
           "wmap", "wmap_fallback", "w")))

# ----------------------------------------------------------------------
print()
if failures:
    print(f"{len(failures)} mismatch(es):")
    for f in failures:
        print(" -", f)
    sys.exit(1)
print("All checks passed.")
