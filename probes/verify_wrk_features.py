#!/usr/bin/env python3
#
# verify_wrk_features.py
#
# Probe pinning the verified behaviour of the FEATURES worker
# (src/reversi/lm/wrk_features.py) and of its test file
# (src/reversi/test/test_wrk_features.py), session 22
# (D-081 analysis). Re-pinned in session 22 (D-082) to the fixed
# behaviour: R1 (the amask log prints m.amask), M1-M3 (factory
# @validate_call, the 2 whitespace lines, the orphan comment
# removed), test T1-T4 + M2 (D-065 idiom, the SKIP_REGAB_DB gate,
# the dead import now load-bearing, header grammar, whitespace
# clean) + the new golden content test (its hash literal pinned).
# Test M1 (the POSITIONS-dependency comment) stays as-is per
# Roberto's call — recorded at I-012 (evaluate moving FEATURES
# before POSITIONS).
#
# Independent derivation: the expected FeatureSet is built from the
# fixture values (rlm_00.json) through the public Feature /
# FeatureSet / Mobility / MobilitySet / Pattern / PatternSet API
# (not the worker code path) and compared with the worker output.
#
# Requires the live regab test DB (the POSITIONS level runs as part
# of the pipeline; the fixture points at tst_regab on localhost).
#
# House convention: writes only under build/tmp, self-cleans via
# atexit; exit code 1 on any mismatch.
#

import atexit
import contextlib
import hashlib
import io
import json5
import os
import re
import shutil
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

TMP = ROOT / "build" / "tmp" / "verify_wrk_features"
TMP.mkdir(parents=True, exist_ok=True)
atexit.register(lambda: shutil.rmtree(TMP, ignore_errors=True))

ALL1 = 0xFFFFFFFFFFFFFFFF
CFG = "src/reversi/test/data/rlm_00.json"

fails = 0

def check(label, cond, detail=""):
    # stderr: stdout is redirected to StringIO around the pipeline moves
    # (the B8/B13 log-content pins read the captured stream).
    global fails
    if not cond:
        fails += 1
    print(f"[{'ok  ' if cond else 'FAIL'}] {label}" + (f" -- {detail}" if detail and not cond else ""), file=sys.stderr)


#
# A — source structure of wrk_features.py (content pins).
#

src = (ROOT / "src" / "reversi" / "lm" / "wrk_features.py").read_text()

check("A1 125 lines (post D-082: +pydantic import +decorator, -orphan comment)",
      len(src.splitlines()) == 125)
check("A2 __all__ = ['wrk_features']", "__all__ = ['wrk_features']" in src)
check("A3 factory returns Worker('FEATURES', _up, _down)",
      'def wrk_features() -> Worker:' in src and 'return Worker("FEATURES", _up, _down)' in src)
check("A4 RLMContext import under TYPE_CHECKING (circular-import guard)",
      'if TYPE_CHECKING:\n    from reversi.lm.logistic_model import RLMContext' in src)
check("A5 worker does not import cache_manager (pure compute, no cache files)",
      "cache_manager" not in src)
check("A6 M1 FIXED (D-082): @validate_call on the factory + the pydantic import",
      "@validate_call" in src and "from pydantic import validate_call, ConfigDict" in src
      and '@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef wrk_features() -> Worker:' in src)
check("A7 R1 FIXED (D-082): amask debug log prints m.amask",
      'amask = {m.amask:016X}' in src and 'amask = {m.mask:016X}' not in src)
check("A8 M3 FIXED (D-082): the orphan 'Empty String SHA-256 Hash' comment removed",
      "Empty String SHA-256 Hash" not in src and "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" not in src)
check("A9 M2 FIXED (D-082): no non-comment trailing-whitespace lines",
      not any(line != line.rstrip() for line in src.splitlines() if not line.lstrip().startswith("#")))

#
# B — runtime behaviour (the worker end-to-end, verbosity HIGH).
#

import numpy as np

from reversi.tools.state_machine import Relevance, Verbosity
from reversi.lm.logistic_model import LogisticModel
from reversi.feature import Feature, FeatureSet
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet
from reversi.lm.hlp_config_schemas import ReversiLogisticModelConfig
import reversi.lm.wrk_features as lwf


def u(h):
    return np.uint64(int(h, 16))


(TMP / "base1").mkdir(parents=True, exist_ok=True)

# --- first instance: CREATED -> CONFIG -> POSITIONS -> FEATURES ---

out1 = io.StringIO()
with contextlib.redirect_stdout(out1):
    m1 = LogisticModel(CFG, verbosity=Verbosity.HIGH, base_dir_override=str(TMP / "base1"))
    # (B1a the worker-list pin moved to the hub verify_logistic_model.py
    # V3c/V3d at D-106)
    check("B1b RLMContext feature_set field exists, None before the level",
          m1.context.feature_set is None)
    m1.move_to_step("FEATURES")
s1 = out1.getvalue()

check("B2 step 3 / 'FEATURES' after the move",
      m1.current_step == 3 and m1.current_worker_name == "FEATURES")

fs = m1.context.feature_set
check("B3a feature_set populated", fs is not None)
check("B3b name = 'NoNameFeatureSet' (schema default — the fixture has no name key)",
      fs.name == "NoNameFeatureSet")
check("B4a intercept feature", fs.intercept is not None
      and fs.intercept.name == "INTERCEPT"
      and int(fs.intercept.n_configurations) == 1
      and int(fs.intercept.n_instances) == 1)
check("B4b MobilitySet 'BasicMobilitySet' with the 3 fixture members",
      fs.mset.name == "BasicMobilitySet"
      and {(str(m.name), int(m.mask), int(m.amask)) for m in fs.mset.mobilities}
      == {("LMC", ALL1, 0), ("ALMC", 0, ALL1), ("DLMC", ALL1, ALL1)})
check("B4c PatternSet 'BasicPatternSet' with the 2 fixture members",
      fs.pset.name == "BasicPatternSet"
      and {(str(p.name), int(p.mask)) for p in fs.pset.patterns} == {("ELLE", 0x107), ("EDGE", 0xFF)})
check("B5 feature order: intercept, mobilities sorted (mask, amask), patterns sorted mask",
      [f.name for f in fs.features] == ["INTERCEPT", "ALMC", "LMC", "DLMC", "EDGE", "ELLE"])
check("B6 n_features 6, n_instances 16 (1 + 1+1+1 + 8+4)",
      len(fs.features) == 6 and fs.n_instances == 16)
check("B7 per-feature counts (LMC 65/1, ALMC 65/1, DLMC 129/1, ELLE 81/8, EDGE 6561/4)",
      {f.name: (int(f.n_configurations), int(f.n_instances)) for f in fs.features}
      == {"INTERCEPT": (1, 1), "LMC": (65, 1), "ALMC": (65, 1), "DLMC": (129, 1),
          "EDGE": (6561, 4), "ELLE": (81, 8)})

# R1 behaviour pin: the DEBUG lines print m.mask twice (D-081 R1).
# cfg order: [LMC, ALMC, DLMC]; LMC amask is 0, ALMC mask is 0.
m_lines = [l for l in s1.splitlines() if "Mobility: name =" in l]
check("B8a 3 mobility debug lines", len(m_lines) == 3)
lmc = next(l for l in m_lines if "name = LMC" in l)
almc = next(l for l in m_lines if "name = ALMC" in l)
check("B8b R1 FIXED (D-082): LMC line now prints the true amask = 0000000000000000",
      "mask = FFFFFFFFFFFFFFFF, amask = 0000000000000000" in lmc)
check("B8c R1 FIXED (D-082): ALMC line now prints the true amask = FFFFFFFFFFFFFFFF",
      "mask = 0000000000000000, amask = FFFFFFFFFFFFFFFF" in almc)

# Independent derivation through the public API.
my_mset = MobilitySet("BasicMobilitySet", [
    Mobility("LMC", u("FFFFFFFFFFFFFFFF"), u("0000000000000000")),
    Mobility("ALMC", u("0000000000000000"), u("FFFFFFFFFFFFFFFF")),
    Mobility("DLMC", u("FFFFFFFFFFFFFFFF"), u("FFFFFFFFFFFFFFFF")),
])
my_pset = PatternSet("BasicPatternSet", [
    Pattern("ELLE", u("0000000000000107")),
    Pattern("EDGE", u("00000000000000FF")),
])
check("B9a mset hash matches the independent build", my_mset.hash == fs.mset.hash)
check("B9b pset hash matches the independent build", my_pset.hash == fs.pset.hash)
expected_hash = hashlib.sha3_256(b"INTERCEPT"
                                 + my_mset.hash.encode("utf-8")
                                 + my_pset.hash.encode("utf-8")).hexdigest()
check("B9c hash = sha3_256(b'INTERCEPT' + mset.hash + pset.hash)", fs.hash == expected_hash)
my_fs = FeatureSet("NoNameFeatureSet", Feature.new_intercept(), my_mset, my_pset)
check("B9d independent FeatureSet: identical feature list + hash",
      [(f.name, int(f.n_configurations), int(f.n_instances)) for f in my_fs.features]
      == [(f.name, int(f.n_configurations), int(f.n_instances)) for f in fs.features]
      and my_fs.hash == fs.hash)

# On-disk effect: only the CONFIG + POSITIONS flat cache files, no FEATURES cache.
files = sorted(p.name for p in (TMP / "base1").iterdir())
check("B10 flat cache files: CONFIG + POSITIONS only (no rlmwf_03_FEATURES*)",
      files == ["rlmwf_01_CONFIG.dat", "rlmwf_01_CONFIG.dat.SHA3-256",
                "rlmwf_02_POSITIONS.dat", "rlmwf_02_POSITIONS.dat.SHA3-256"])

# (B11a/B11b moved to a test at D-106 step 3, class a §4 conversion:
#  test_wrk_features.py::TestLMWorkerFeaturesGuards::
#  test_zero_features_raises_value_error — the zero-feature fail-fast
#  guard, ValueError message + ERROR log event)

# Down direction: FEATURES (3) -> CONFIG (1) clears the feature_set.
m1.move_to_step("CONFIG")
check("B12 down to CONFIG: step 1, feature_set cleared",
      m1.current_step == 1 and m1.context.feature_set is None)

# Second instance on the same base dir: POSITIONS served from cache,
# FEATURES recomputed (no cache) but identical.
out2 = io.StringIO()
with contextlib.redirect_stdout(out2):
    m2 = LogisticModel(CFG, verbosity=Verbosity.HIGH, base_dir_override=str(TMP / "base1"))
    m2.move_to_step("FEATURES")
s2 = out2.getvalue()
check("B13a second run: POSITIONS cache hit", "Cache successfully loaded" in s2)
check("B13b second run: no DB extraction", "Extracted" not in s2)
check("B13c second run: identical feature set (name + hash)",
      m2.context.feature_set.name == fs.name and m2.context.feature_set.hash == fs.hash)

#
# C — source structure of test_wrk_features.py (content pins).
#

tsrc = (ROOT / "src" / "reversi" / "test" / "test_wrk_features.py").read_text()

check("C1 206 lines (post D-106 step 3: the zero-feature guard test class added; pre: 164, post D-085)",
      len(tsrc.splitlines()) == 206)
check("C2 2 classes / 3 test methods (the D-106 step-3 guard class added; the D-082 golden content test kept)",
      "class TestLMWorkerFeatures" in tsrc
      and "class TestLMWorkerFeaturesGuards" in tsrc
      and len(re.findall(r"    def test_", tsrc)) == 3)
check("C3 T1 FIXED (D-082, re-anchored D-085): the D-065 idiom via the shared reversi.test.paths module (import, setUpClass mkdir, TemporaryDirectory, defensive tearDown)",
      "from reversi.test.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT" in tsrc
      and "CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)" in tsrc
      and 'tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))' in tsrc
      and "mkdtemp" not in tsrc)
check("C4 T2 FIXED (D-082): the SKIP_REGAB_DB gate at the top of setUp",
      "SKIP_REGAB_DB" in tsrc
      and "self.skipTest('SKIP_REGAB_DB=1: database tests skipped')" in tsrc)
check("C5 T3 FIXED (D-082): the Path import is now load-bearing (tmp_dir; D-085: CUSTOM_TMP_BASE moved to reversi.test.paths)",
      "from pathlib import Path" in tsrc and len(re.findall(r"\bPath\b", tsrc)) > 1)
check("C6 T4 FIXED (D-082): header grammar 'How to run the wrk_features unit tests.' + DB/gate run note",
      "How to run the wrk_features unit tests." in tsrc
      and "SKIP_REGAB_DB=1 skips the DB-gated tests" in tsrc)
check("C7 M1 (D-082, as-is per Roberto — I-012: evaluate moving FEATURES before POSITIONS): the setUp comment stays",
      "as FEATURES depends on the configuration loaded there" in tsrc)
check("C8 M2 FIXED (D-082): no trailing-whitespace lines",
      not any(line != line.rstrip() for line in tsrc.splitlines() if not line.lstrip().startswith("#")))
check("C9 golden test: the 3 hash literals pinned (fs / mset / pset)",
      "453e918aeabfa3f7ff43f110ab72719b3f1d1906158933436234b7bab075a159" in tsrc
      and "2e5535935d46d82a941ef87d43d22562735db9b6bf41db51d6eb6a8f21208a94" in tsrc
      and "04d52f12d3438393dd3cd9d47df73c1135ffdf9ed8e9f4d4571f5d1adcbb8c18" in tsrc)
check("C10 golden test: the feature-order + counts pin (6 features, 16 instances)",
      "[(f.name, f.n_configurations, f.n_instances)" in tsrc
      and "('INTERCEPT', 1, 1), ('ALMC', 65, 1), ('LMC', 65, 1)" in tsrc
      and "('DLMC', 129, 1), ('EDGE', 6561, 4), ('ELLE', 81, 8)]" in tsrc
      and "self.assertEqual(fs.n_instances, 16)" in tsrc)

print(f"\n{fails} mismatch(es)")
sys.exit(1 if fails else 0)
