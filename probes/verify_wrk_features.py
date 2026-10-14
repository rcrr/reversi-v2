#!/usr/bin/env python3
#
# verify_wrk_features.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi-v2
#
# Author Roberto Corradini mailto:rob_corradini@yahoo.it
# Copyright 2026 Roberto Corradini. All rights reserved.
#
# License
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

#
# verify_wrk_features.py
#
# Probe pinning the verified behaviour of the FEATURES worker
# (src/reversi/lm/wrk_features.py) and of its test file
# (test/reversi/lm/test_wrk_features.py), session 22
# Re-pinned in session 22 (D-082) to the fixed
# behaviour: R1 (the debug log prints the mask + side), M1-M3 (factory
# @validate_call, the 2 whitespace lines, the orphan comment
# removed), test T1-T4 + M2 (the tmp-dir idiom, the SKIP_REGAB_DB gate,
# the dead import now load-bearing, header grammar, whitespace
# clean) + the new golden content test (its hash literal pinned).
# Test M1 resolved (I-012 realized, the I-017 T1): the
# stale POSITIONS-dependency comment is removed and the setUp
# moves to FEATURES directly.
#
# Independent derivation: the expected FeatureSet is built from the
# fixture values (rlm_00.json) through the public Feature /
# FeatureSet / Mobility / MobilitySet / Pattern / PatternSet API
# (not the worker code path) and compared with the worker output.
#
# DB-free (the move to FEATURES no longer crosses
# POSITIONS — CONFIG + FEATURES only).
#
# House convention: writes only under build/tmp, self-cleans via
# atexit; exit code 1 on any mismatch.
#

import atexit
import contextlib
import hashlib
import io
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # the root test/ tree (the test.reversi helpers)
os.chdir(ROOT)

TMP = ROOT / "build" / "tmp" / "verify_wrk_features"
TMP.mkdir(parents=True, exist_ok=True)
atexit.register(lambda: shutil.rmtree(TMP, ignore_errors=True))

ALL1 = 0xFFFFFFFFFFFFFFFF
CFG = "test/reversi/data/rlm_00.json"

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

check("A1 155 lines",
      len(src.splitlines()) == 155)
check("A2 __all__ = ['wrk_features']", "__all__ = ['wrk_features']" in src)
check("A3 factory returns Worker('FEATURES', _up, _down)",
      'def wrk_features() -> Worker:' in src and 'return Worker("FEATURES", _up, _down)' in src)
check("A4 LMContext import under TYPE_CHECKING (circular-import guard)",
      'if TYPE_CHECKING:\n    from reversi.lm.logistic_model import LMContext' in src)
check("A5 worker does not import cache_manager (pure compute, no cache files)",
      "cache_manager" not in src)
check("A6 M1 FIXED (D-082): @validate_call on the factory + the pydantic import",
      "@validate_call" in src and "from pydantic import validate_call, ConfigDict" in src
      and '@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef wrk_features() -> Worker:' in src)
check("A7 R1 FIXED (D-082): the mobility debug log prints the mask + side",
      'side = {m.side}' in src and 'amask' not in src)
check("A8 M3 FIXED (D-082): the orphan 'Empty String SHA-256 Hash' comment removed",
      "Empty String SHA-256 Hash" not in src
      and "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855" not in src)
check("A9 M2 FIXED (D-082): no non-comment trailing-whitespace lines",
      not any(line != line.rstrip() for line in src.splitlines() if not line.lstrip().startswith("#")))

#
# B — runtime behaviour (the worker end-to-end, verbosity HIGH).
#

import numpy as np

from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel
from reversi.feature import Feature, FeatureSet
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet



def u(h):
    return np.uint64(int(h, 16))


(TMP / "base1").mkdir(parents=True, exist_ok=True)

# --- first instance: CREATED -> CONFIG -> FEATURES ---

out1 = io.StringIO()
with contextlib.redirect_stdout(out1):
    m1 = LogisticModel(CFG, verbosity=Verbosity.HIGH, base_dir_override=str(TMP / "base1"))
    # (B1a the worker-list pin moved to the hub verify_logistic_model.py
    # V3c/V3d at D-106)
    check("B1b LMContext feature_set field exists, None before the level",
          m1.context.feature_set is None)
    m1.move_to_step("FEATURES")
s1 = out1.getvalue()

check("B2 step 2 / 'FEATURES' after the move",
      m1.current_step == 2 and m1.current_worker_name == "FEATURES")

fs = m1.context.feature_set
check("B3a feature_set populated", fs is not None)
check("B3b name = 'NoNameFeatureSet' (schema default — the fixture has no name key)",
      fs.name == "NoNameFeatureSet")
check("B4a intercept feature", fs.intercept is not None
      and fs.intercept.name == "INTERCEPT"
      and int(fs.intercept.n_configurations) == 1
      and int(fs.intercept.n_instances) == 1)
check("B4b MobilitySet 'BasicMobilitySet' with the 2 fixture members",
      fs.mset.name == "BasicMobilitySet"
      and {(str(m.name), int(m.mask), m.side) for m in fs.mset.mobilities}
      == {("LMC", ALL1, "mover"), ("ALMC", ALL1, "opponent")})
check("B4c PatternSet 'BasicPatternSet' with the 2 fixture members",
      fs.pset.name == "BasicPatternSet"
      and {(str(p.name), int(p.mask)) for p in fs.pset.patterns} == {("ELLE", 0x107), ("EDGE", 0xFF)})
check("B5 feature order: intercept, mobilities sorted (mask, side), patterns sorted mask",
      [f.name for f in fs.features] == ["INTERCEPT", "LMC", "ALMC", "EDGE", "ELLE"])
check("B6 n_features 5, n_instances 15 (1 + 1+1 + 8+4)",
      len(fs.features) == 5 and fs.n_instances == 15)
check("B7 per-feature counts (LMC 65/1, ALMC 65/1, ELLE 81/8, EDGE 6561/4)",
      {f.name: (int(f.n_configurations), int(f.n_instances)) for f in fs.features}
      == {"INTERCEPT": (1, 1), "LMC": (65, 1), "ALMC": (65, 1),
          "EDGE": (6561, 4), "ELLE": (81, 8)})

# R1 behaviour pin: the DEBUG lines print the mask + side.
# cfg order: [LMC, ALMC]; both full-board masks, the two sides.
m_lines = [l for l in s1.splitlines() if "Mobility: name =" in l]
check("B8a 2 mobility debug lines", len(m_lines) == 2)
lmc = next(l for l in m_lines if "name = LMC" in l)
almc = next(l for l in m_lines if "name = ALMC" in l)
check("B8b R1 FIXED (D-082): LMC line prints the full-board mask + side mover",
      "mask = FFFFFFFFFFFFFFFF, side = mover" in lmc)
check("B8c R1 FIXED (D-082): ALMC line prints the full-board mask + side opponent",
      "mask = FFFFFFFFFFFFFFFF, side = opponent" in almc)

# Independent derivation through the public API.
my_mset = MobilitySet("BasicMobilitySet", [
    Mobility("LMC", u("FFFFFFFFFFFFFFFF"), "mover"),
    Mobility("ALMC", u("FFFFFFFFFFFFFFFF"), "opponent"),
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

# On-disk effect: no cache files at all (POSITIONS is
# downstream of FEATURES, so its cache file is not written either).
# (the CONFIG level writes no cache file anymore.)
files = sorted(p.name for p in (TMP / "base1").iterdir())
check("B10 flat cache files: none (no rlmwf_01_CONFIG* — "
      "no rlmwf_02_FEATURES* — the pure-compute level writes nothing)",
      files == [])

# (B11a/B11b moved to a test at D-106 step 3, class a §4 conversion:
#  test_wrk_features.py::TestLMWorkerFeaturesGuards::
#  test_zero_features_raises_value_error — the zero-feature fail-fast
#  guard, ValueError message + ERROR log event)

# Down direction: FEATURES (2) -> CONFIG (1) clears the feature_set.
m1.move_to_step("CONFIG")
check("B12 down to CONFIG: step 1, feature_set cleared",
      m1.current_step == 1 and m1.context.feature_set is None)

# Second instance on the same base dir: FEATURES recomputed (no
# cache) and identical; no DB access at all (POSITIONS is
# not in the path).
out2 = io.StringIO()
with contextlib.redirect_stdout(out2):
    m2 = LogisticModel(CFG, verbosity=Verbosity.HIGH, base_dir_override=str(TMP / "base1"))
    m2.move_to_step("FEATURES")
s2 = out2.getvalue()
check("B13a second run: no DB access (no connection, no extraction — "
      "POSITIONS is not in the path)",
      "established successfully" not in s2 and "Extracted" not in s2)
check("B13b second run: the FEATURES level ran (the INFO line)",
      "Loading board features as defined by the model..." in s2)
check("B13c second run: identical feature set (name + hash)",
      m2.context.feature_set.name == fs.name and m2.context.feature_set.hash == fs.hash)

#
# C — source structure of test_wrk_features.py (content pins).
#

tsrc = (ROOT / "test" / "reversi" / "lm" / "test_wrk_features.py").read_text()

check("C1 187 lines",
      len(tsrc.splitlines()) == 187)
check("C2 2 classes / 3 test methods (the D-106 step-3 guard class added; the D-082 golden content test kept)",
      "class TestLMWorkerFeatures" in tsrc
      and "class TestLMWorkerFeaturesGuards" in tsrc
      and len(re.findall(r"    def test_", tsrc)) == 3)
check("C3 T1 FIXED (D-082, re-anchored D-085): the idiom via the shared test.reversi.paths module "
      "(import, setUpClass mkdir, TemporaryDirectory, defensive tearDown)",
      "from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT" in tsrc
      and "CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)" in tsrc
      and 'tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))' in tsrc
      and "mkdtemp" not in tsrc)
check("C4 gate REMOVED (the setUp is DB-free — no POSITIONS in the path)",
      "db_long_gate" not in tsrc and "SKIP_REGAB_DB" not in tsrc)
check("C5 T3 FIXED (D-082): the Path import is now load-bearing (tmp_dir; "
      "D-085: CUSTOM_TMP_BASE moved to test.reversi.paths)",
      "from pathlib import Path" in tsrc and len(re.findall(r"\bPath\b", tsrc)) > 1)
check("C6 T4 FIXED (D-082; re-anchored): header grammar 'How to run the wrk_features unit tests.' "
      "+ the DB-free run note",
      "How to run the wrk_features unit tests." in tsrc
      and "Run the tests (DB-free: the setUp moves to" in tsrc)
check("C7 M1 resolved (I-012 realized): the stale POSITIONS-dependency comment is gone",
      "as FEATURES depends on the configuration loaded there" not in tsrc
      and "move_to_step('POSITIONS')" not in tsrc)
check("C8 M2 FIXED (D-082): no trailing-whitespace lines",
      not any(line != line.rstrip() for line in tsrc.splitlines() if not line.lstrip().startswith("#")))
check("C9 golden test: the 3 hash literals pinned (fs / mset / pset)",
      "9de406cfce702bf2ae80fee401138bec2bdaf7b1b38de94dc4c065fadd47da73" in tsrc
      and "d857e3c3e1d2fcadcea4d0125c69e518c74a34dc694598ac9ad57dda1e3037b8" in tsrc
      and "04d52f12d3438393dd3cd9d47df73c1135ffdf9ed8e9f4d4571f5d1adcbb8c18" in tsrc)
check("C10 golden test: the feature-order + counts pin (5 features, 15 instances)",
      "[(f.name, f.n_configurations, f.n_instances)" in tsrc
      and "('INTERCEPT', 1, 1), ('LMC', 65, 1), ('ALMC', 65, 1)" in tsrc
      and "('EDGE', 6561, 4), ('ELLE', 81, 8)]" in tsrc
      and "self.assertEqual(fs.n_instances, 15)" in tsrc)

print(f"\n{fails} mismatch(es)")
sys.exit(1 if fails else 0)
