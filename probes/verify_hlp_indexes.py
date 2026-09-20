#!/usr/bin/env python3
#
# verify_hlp_indexes.py
#
# Probe pinning the verified behaviour of the INDEXES level:
# the domain module (src/reversi/lm/hlp_indexes.py) and the worker
# (src/reversi/lm/wrk_indexes.py), plus the source structure of
# their two test files (test_hlp_indexes.py,
# test_wrk_indexes.py), session 23 (D-083 analysis).
#
# The B tier is pure (no DB): the store/load round-trip, the
# sidecar flow, the is_cache_consistent logic and the compute
# path are exercised with a real FeatureSet (fixture constants,
# public API) and fabricated 2-position arrays. The C tier
# needs the live regab test DB (the pipeline moves through
# POSITIONS): the flat rlmwf_05_INDEXES.dat naming, the data
# checksum, the sidecar format, the cross-run cache round-trip
# and the _down clearing.
#
# House convention: writes only under build/tmp, self-cleans via
# atexit; exit code 1 on any mismatch.
#
# Re-pinned in session 23 (D-084) to the post-campaign state:
# hlp_indexes R1 (A8 docstring corrected) + M1 (imports gone) +
# M2 (A9 typo fixed) + M3 (A10 4→0 whitespace) + M4 (version
# gate via expected_version) + M6 (__repr__ added — A3 4→5);
# wrk_indexes M1 (D3 @validate_call) + M2 (D6 2→0) +
# M3 (D5 load_fn checksum=False); test_hlp_indexes T1-T5 +
# M1-M2 (F3 import gone, F4 header, F5 English comment, F7
# ValidationError pins + rds_checksum present, F8 both branches,
# F9 19→0, 13→14 tests); test_wrk_indexes T1-T3 + M1
# (E2 D-065 idiom, E3 gate, E4 header, E7 13→0 + defensive
# tearDown).
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
sys.path.insert(0, str(ROOT))  # the root test/ tree (the test.reversi helpers)
os.chdir(ROOT)

TMP = ROOT / "build" / "tmp" / "verify_hlp_indexes"
TMP.mkdir(parents=True, exist_ok=True)
atexit.register(lambda: shutil.rmtree(TMP, ignore_errors=True))

CFG = "test/reversi/data/rlm_00.json"

fails = 0

def check(label, cond, detail=""):
    # stderr: stdout is redirected to StringIO around the pipeline
    # moves (the C6 log-content pins read the captured stream).
    global fails
    if not cond:
        fails += 1
    print(f"[{'ok  ' if cond else 'FAIL'}] {label}" + (f" -- {detail}" if detail and not cond else ""), file=sys.stderr)


#
# A — source structure of hlp_indexes.py (content pins).
#

src = (ROOT / "src" / "reversi" / "lm" / "hlp_indexes.py").read_text()

check("A1 197 lines (post D-139: 190 + the 2x compressed kwarg + docstring lines)",
      len(src.splitlines()) == 197
      and "from enum import IntEnum" not in src
      and "Protocol" not in src
      and "BeforeValidator" not in src
      and "AfterValidator" not in src
      and "Field" not in src)
check("A2 __all__: the 5 public names",
      "__all__ = ['LMIndexes'," in src
      and "'hlp_indexes_store_to_file'" in src
      and "'hlp_indexes_load_from_file'" in src
      and "'hlp_indexes_compute'" in src
      and "'hlp_indexes_is_cache_consistent']" in src)
check("A3 @validate_call on __init__ / compute_sha3_256_hash / __repr__ / store / load — and NOT on compute / is_cache_consistent (5 total; D-084 M6 __repr__)",
      src.count("@validate_call") == 5)
check("A4 compute: the deliberate no-validation comment (circular import)",
      "#: Here validation is not possible, it brings in a convoluted issue with circular imports.\ndef hlp_indexes_compute(" in src)
i_hdr = src.index("w.write_header(description, version)")
i_s1 = src.index("w.write_string(hlp_indexes.rds_checksum)")
i_s2 = src.index("w.write_string(hlp_indexes.feature_set_hash)")
i_arr = src.index("w.write_array(hlp_indexes.indexes)")
check("A5 store: description + version 1, write order header -> rds_checksum -> feature_set_hash -> array",
      'description = "LMIndexes binary data file"' in src
      and "version = 1" in src
      and i_hdr < i_s1 < i_s2 < i_arr)
check("A6 load: checksum=True default + sidecar verify + header checks + the 3 RuntimeError messages",
      "checksum: bool = True" in src
      and "binio.verify_sha3_256_sidecar(filename)" in src
      and "The checksum file signature doesn't match with current file." in src
      and "The file is not a proper" in src
      and "The file version is not consistent" in src)
check("A7 is_cache_consistent: the 2-field metadata compare (feature_set_hash + rds_checksum), no DB params in the module",
      "cached_feature_set_hash == expected_feature_set_hash" in src
      and "cached_rds_checksum == expected_rds_checksum" in src
      and "dbname" not in src and "bid" not in src)
check("A8 D-139: the store docstring — the compression default + the true sidecar story (the stale D-084 R1 note corrected: the binio writer writes it, cache_manager re-writes it idempotently)",
      "LZ4 whole-file compression by default (D-139, as in model_weights)." in src
      and "the SHA3-256 sidecar is written by the binio writer" in src
      and "no SHA3-256 sidecar is written by this function" not in src
      and "write_sha3_256_sidecar" not in src)
check("A9 D-084 M2: the 'togheter' typo fixed (the docstring reads 'together')",
      "together with the hash signature" in src and "togheter" not in src)
check("A10 D-084 M3: 0 non-comment trailing-whitespace lines",
      sum(1 for l in src.splitlines() if l != l.rstrip() and not l.lstrip().startswith("#")) == 0)
check("A11 compute body: rds_checksum + feature_set.hash + feature_set.compute_indexes(ctx.positions)",
      "rds_checksum = ctx.rds_checksum" in src
      and "feature_set_hash = ctx.feature_set.hash" in src
      and "indexes = ctx.feature_set.compute_indexes(ctx.positions)" in src)

#
# B — hlp_indexes runtime, NO DB (independent derivation).
#

import numpy as np

from reversi.tools import binio
from reversi.lm import hlp_indexes
from reversi.feature import Feature, FeatureSet
from reversi.mobility import Mobility, MobilitySet
from reversi.pattern import Pattern, PatternSet


def u(h):
    return np.uint64(int(h, 16))


my_mset = MobilitySet("BasicMobilitySet", [
    Mobility("LMC", u("FFFFFFFFFFFFFFFF"), u("0000000000000000")),
    Mobility("ALMC", u("0000000000000000"), u("FFFFFFFFFFFFFFFF")),
    Mobility("DLMC", u("FFFFFFFFFFFFFFFF"), u("FFFFFFFFFFFFFFFF")),
])
my_pset = PatternSet("BasicPatternSet", [
    Pattern("ELLE", u("0000000000000107")),
    Pattern("EDGE", u("00000000000000FF")),
])
my_fs = FeatureSet("NoNameFeatureSet", Feature.new_intercept(), my_mset, my_pset)

idx = np.arange(32, dtype=np.uint32).reshape(2, 16)
obj = hlp_indexes.LMIndexes("RDSHASH", my_fs.hash, idx)
# (B1 init attribute identity (c? resolves to c) deleted at D-106
#  step 3, class c: test_hlp_indexes.py::TestLMIndexes
#  ::test_init_success pins all three — the two equalities +
#  assertIs(obj.indexes, DUMMY_INDEXES). The obj binding stays:
#  B2/B3 use it.)
check("B2 data checksum: sha3_256 over indexes.tobytes() (independent recompute)",
      obj.compute_sha3_256_hash() == hashlib.sha3_256(idx.tobytes()).hexdigest())

dat = TMP / "idx.bin"
hlp_indexes.hlp_indexes_store_to_file(obj, dat)
check("B3 store writes the .dat", dat.exists())
loaded = hlp_indexes.hlp_indexes_load_from_file(dat, checksum=False)
check("B4 load (checksum=False): the fields round-trip",
      loaded.rds_checksum == "RDSHASH" and loaded.feature_set_hash == my_fs.hash
      and np.array_equal(loaded.indexes, idx) and loaded.indexes.dtype == np.uint32)

binio.write_sha3_256_sidecar(dat)
loaded2 = hlp_indexes.hlp_indexes_load_from_file(dat)  # checksum=True default
check("B5 load (checksum=True, default) with a valid sidecar round-trips",
      np.array_equal(loaded2.indexes, idx))

blob = bytearray(dat.read_bytes())
blob[len(blob) // 2] ^= 0xFF
dat.write_bytes(bytes(blob))
try:
    hlp_indexes.hlp_indexes_load_from_file(dat)
    check("B6 corrupted file + checksum=True -> RuntimeError (sidecar mismatch)", False, "no exception")
except RuntimeError as e:
    check("B6 corrupted file + checksum=True -> RuntimeError (sidecar mismatch)",
          "checksum file signature" in str(e))
except Exception as e:
    check("B6 corrupted file + checksum=True -> RuntimeError (sidecar mismatch)", False,
          f"got {type(e).__name__}: {e}")

# A file with the wrong description / version (checksum=False to reach the header).
from reversi.lm import hlp_indexes as ri
with binio.BinaryWriter(TMP / "wrong_desc.bin", compressed=True) as w:
    w.write_header("Wrong Description", 1)
    w.write_string("a")
    w.write_string("b")
    w.write_array(idx)
try:
    hlp_indexes.hlp_indexes_load_from_file(TMP / "wrong_desc.bin", checksum=False)
    check("B7 wrong description -> RuntimeError", False, "no exception")
except RuntimeError as e:
    check("B7 wrong description -> RuntimeError", "not a proper" in str(e))
with binio.BinaryWriter(TMP / "wrong_ver.bin", compressed=True) as w:
    w.write_header("LMIndexes binary data file", 99)
    w.write_string("a")
    w.write_string("b")
    w.write_array(idx)
try:
    hlp_indexes.hlp_indexes_load_from_file(TMP / "wrong_ver.bin", checksum=False)
    check("B8 wrong version -> RuntimeError", False, "no exception")
except RuntimeError as e:
    check("B8 wrong version -> RuntimeError", "version is not consistent" in str(e))

# (B9/B10/B11 is_cache_consistent True/False branches deleted at
#  D-106 step 3, class c: test_hlp_indexes.py pins all three —
#  test_is_cache_consistent_returns_true / _returns_false /
#  _returns_false_rds_differs. The ok_ctx scaffolding was used only
#  by them.)

# compute: a REAL FeatureSet (fixture constants) + a fabricated 2-position array.
positions2 = np.array([[0x0280820280828002, 0x0041414141414100],
                       [0x1414102410284141, 0x0BEB8B9BD3D3FBBE]], dtype=np.uint64)
fake_ctx = types.SimpleNamespace(rds_checksum="RDSFAKE", feature_set=my_fs, positions=positions2)
res = hlp_indexes.hlp_indexes_compute(fake_ctx)
expected = my_fs.compute_indexes(positions2)
check("B12 compute: (2, 16) uint32 matrix identical to FeatureSet.compute_indexes called directly",
      res.indexes.shape == (2, 16) and res.indexes.dtype == np.uint32
      and np.array_equal(res.indexes, expected))
check("B13 compute: the checksums come from the ctx (rds_checksum + feature_set.hash)",
      res.rds_checksum == "RDSFAKE" and res.feature_set_hash == my_fs.hash)

# (B14 init rejects a non-str hash (c? resolves to c) deleted at
#  D-106 step 3, class c: test_hlp_indexes.py::
#  test_init_fails_with_invalid_hash_type is exactly this case
#  (feature_set_hash=12345 -> ValidationError))

#
# C — pipeline integration (live regab DB required).
#

from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel

(TMP / "base1").mkdir(parents=True, exist_ok=True)

out1 = io.StringIO()
with contextlib.redirect_stdout(out1):
    m1 = LogisticModel(CFG, verbosity=Verbosity.HIGH, base_dir_override=str(TMP / "base1"))
    m1.move_to_step("INDEXES")
s1 = out1.getvalue()

# (C1 step 4 / 'INDEXES' deleted at D-106 step 3, class c:
#  test_wrk_indexes.py pins step 4 / name INDEXES in three
#  places — the compute test, the pre-state, and the cache test)
files = sorted(p.name for p in (TMP / "base1").iterdir())
check("C2 flat cache files: SU_ANALYSIS (the rlm_00 opt-in, D-175) + "
      "POSITIONS + INDEXES — no rlmwf_01_CONFIG* (D-142), no rlmwf_02_FEATURES* "
      "(the pure-compute level writes nothing)",
      files == ["rlmwf_03_SU_ANALYSIS.dat",
                "rlmwf_03_SU_ANALYSIS.dat.SHA3-256",
                "rlmwf_04_POSITIONS.dat", "rlmwf_04_POSITIONS.dat.SHA3-256",
                "rlmwf_05_INDEXES.dat", "rlmwf_05_INDEXES.dat.SHA3-256",
                "su_analysis"],
      f"{files}")
ri = m1.context.hlp_indexes
check("C3 ctx.hlp_indexes set + the data checksum = sha3_256(indexes.tobytes()) (independent recompute)",
      ri is not None
      and m1.context.hlp_indexes_checksum == hashlib.sha3_256(ri.indexes.tobytes()).hexdigest())
sc = (TMP / "base1" / "rlmwf_05_INDEXES.dat.SHA3-256").read_text()
check("C4 the sidecar is the flat sha3_256sum line over the .dat file (the FILE checksum — different from the data checksum)",
      sc == f"{binio.compute_sha3_256(TMP / 'base1' / 'rlmwf_05_INDEXES.dat')}  rlmwf_05_INDEXES.dat\n"
      and sc.split()[0] != m1.context.hlp_indexes_checksum)
n_pos = len(m1.context.positions)
indep = m1.context.feature_set.compute_indexes(m1.context.positions)
check("C5 indexes shape (N, 16) uint32 (N = the training position count, 16 = the fixture n_instances sum) and identical to the independent recompute",
      ri.indexes.shape == (n_pos, 16) and ri.indexes.dtype == np.uint32
      and np.array_equal(ri.indexes, indep))

out2 = io.StringIO()
with contextlib.redirect_stdout(out2):
    m2 = LogisticModel(CFG, verbosity=Verbosity.HIGH, base_dir_override=str(TMP / "base1"))
    m2.move_to_step("INDEXES")
s2 = out2.getvalue()
ri2 = m2.context.hlp_indexes
# (C6a/C6b second-run cache-hit log pins deleted at D-106 step 3,
#  class c: test_read_cache_on_new_instance pins the same two log
#  facts — assertIn 'Cache successfully loaded and validated' +
#  assertNotIn 'Executing heavy computation')
check("C6c second run: identical hlp_indexes (checksum + indexes)",
      m2.context.hlp_indexes_checksum == m1.context.hlp_indexes_checksum
      and np.array_equal(ri2.indexes, ri.indexes))

m1.move_to_step("FEATURES")
check("C7 down to FEATURES: hlp_indexes + hlp_indexes_checksum cleared",
      m1.current_step == 2 and m1.context.hlp_indexes is None
      and m1.context.hlp_indexes_checksum is None)

#
# D — source structure of wrk_indexes.py (content pins).
#

wsrc = (ROOT / "src" / "reversi" / "lm" / "wrk_indexes.py").read_text()

check("D1 80 lines (D-084: +1 pydantic import, +1 @validate_call)",
      len(wsrc.splitlines()) == 80)
check("D2 __all__ = ['wrk_indexes']", "__all__ = ['wrk_indexes']" in wsrc)
check("D3 D-084 M1: the factory returns Worker('INDEXES', _up, _down) WITH @validate_call (house convention, as in the other workers post-campaign)",
      '@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\ndef wrk_indexes() -> Worker:' in wsrc
      and 'return Worker("INDEXES", _up, _down)' in wsrc
      and "from pydantic import validate_call, ConfigDict" in wsrc)
check("D4 LMContext import under TYPE_CHECKING (circular-import guard)",
      'if TYPE_CHECKING:\n    from reversi.lm.logistic_model import LMContext' in wsrc)
check("D5 the D-072 cache wiring: the 7 kwargs (full-path closure, use_cache, the 5 hlp_indexes fns)",
      "cache_path  = ctx.get_cache_file_full_path_for_current_level()," in wsrc
      and "is_allowed  = ctx.use_cache," in wsrc
      and "load_fn     = lambda path: hlp_indexes_load_from_file(path, checksum=False)," in wsrc
      and "store_fn    = hlp_indexes_store_to_file," in wsrc
      and "hlp_indexes_is_cache_consistent(ctx, cached_hlp_indexes)" in wsrc
      and "compute_fn  = lambda: hlp_indexes_compute(ctx)," in wsrc
      and "logger_fn   = ctx.log_event" in wsrc)
check("D6 _down clears BOTH context attributes; 0 non-comment trailing-whitespace lines (D-084 M2)",
      "ctx.hlp_indexes = None" in wsrc and "ctx.hlp_indexes_checksum = None" in wsrc
      and sum(1 for l in wsrc.splitlines() if l != l.rstrip() and not l.lstrip().startswith("#")) == 0)

#
# E — source structure of test_wrk_indexes.py (content pins).
#

tsrc = (ROOT / "test" / "reversi" / "lm" / "test_wrk_indexes.py").read_text()

check("E1 154 lines, 1 class / 2 tests (post D-085; D-130: the tier note adds a header line)",
      len(tsrc.splitlines()) == 154
      and "class TestLMWorkerIndexes" in tsrc
      and len(re.findall(r"    def test_", tsrc)) == 2)
check("E2 D-084 T1 (D-085: re-anchored via test.reversi.paths): the D-065 idiom — import of CUSTOM_TMP_BASE, setUpClass mkdir, TemporaryDirectory FIRST, no mkdtemp / no shutil.rmtree",
      "from test.reversi.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT" in tsrc
      and "setUpClass" in tsrc
      and "tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))" in tsrc
      and "mkdtemp" not in tsrc and "shutil" not in tsrc)
check("E3 D-084 T2: the SKIP_REGAB_DB gate at the top of setUp (the move to INDEXES runs POSITIONS — a DB hit on a fresh base dir, D-157 order)",
      "SKIP_REGAB_DB" in tsrc and "db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates" in tsrc
      and "self.rlm.move_to_step('FEATURES')" in tsrc)
check("E4 D-084 T3: header grammar 'How to run the wrk_indexes unit tests.' + the DB run note",
      "How to run the wrk_indexes unit tests." in tsrc
      and "a live regab DB + LONG=1 is required;" in tsrc)
check("E5 the rlmwf_05_INDEXES.dat + .SHA3-256 pins and the 'Executing heavy computation' pin",
      "rlmwf_05_INDEXES.dat" in tsrc and "rlmwf_05_INDEXES.dat.SHA3-256" in tsrc
      and '"Executing heavy computation"' in tsrc)
check("E6 the (accurate) dependency comment: INDEXES depends on the feature_set loaded in FEATURES",
      "Move to FEATURES first, as INDEXES depends on the feature_set loaded there" in tsrc)
check("E7 0 non-comment trailing-whitespace lines (D-084 M1); the tearDown is defensive (getattr guards)",
      sum(1 for l in tsrc.splitlines() if l != l.rstrip() and not l.lstrip().startswith("#")) == 0
      and tsrc.count("getattr(self, ") == 2)

#
# F — source structure of test_hlp_indexes.py (content pins).
#

fsrc = (ROOT / "test" / "reversi" / "lm" / "test_hlp_indexes.py").read_text()

check("F1 307 lines, 5 classes / 14 tests (post D-139: the compressed=True mock pins)",
      len(fsrc.splitlines()) == 307
      and len(re.findall(r"^class Test", fsrc, flags=re.M)) == 5
      and len(re.findall(r"    def test_", fsrc)) == 14
      and "def test_is_cache_consistent_returns_false_rds_differs" in fsrc)
check("F2 no temp-dir machinery at all (every file I/O is mocked — binio patched): no mkdtemp / TemporaryDirectory / CUSTOM_TMP_BASE",
      "mkdtemp" not in fsrc and "TemporaryDirectory" not in fsrc
      and "CUSTOM_TMP_BASE" not in fsrc and "@patch('reversi.lm.hlp_indexes.binio')" in fsrc)
import ast as _ast
_idx_name_uses = [n for n in _ast.walk(_ast.parse(fsrc))
                  if isinstance(n, _ast.Name) and n.id == "IndexArray"]
check("F3 D-084 T1: the dead 'from reversi.pattern import IndexArray' import removed (only the docstring occurrence remains; zero code-level uses)",
      "from reversi.pattern import IndexArray" not in fsrc
      and len(re.findall(r"\bIndexArray\b", fsrc)) == 1
      and len(_idx_name_uses) == 0)
check("F4 D-084 T2: header grammar 'How to run the hlp_indexes unit tests.'",
      "How to run the hlp_indexes unit tests." in fsrc)
check("F5 D-084 T5: the Italian comment replaced with English (AGENTS.md rule 4)",
      "Non mockiamo il modulo" not in fsrc
      and "The module is not mocked; only a fake \"model\" object is created" in fsrc)
check("F6 the shared dummy: np.zeros((2, 2), dtype=np.uint32)",
      "DUMMY_INDEXES = np.zeros((2, 2), dtype=np.uint32)" in fsrc)
check("F7 D-084 T3+T4: the 2 assertRaises(ValidationError) pins (no broad Exception) + rds_checksum present in test_init_fails_with_invalid_indexes_type (the invalid indexes is what's under test)",
      fsrc.count("self.assertRaises(ValidationError)") == 2
      and fsrc.count("self.assertRaises(Exception)") == 0
      and "from pydantic import ValidationError" in fsrc
      and 'feature_set_hash="valid_hash"' in fsrc
      and "indexes=[[1, 2], [3, 4]]" in fsrc
      and "rds_checksum" in fsrc[fsrc.index("def test_init_fails_with_invalid_indexes_type"):
                fsrc.index("class TestHlpIndexesStoreToFile")])
check("F8 D-084 M2: is_cache_consistent — BOTH single-field branches tested (feature_set_hash-only and rds-only)",
      fsrc.count('"identical_hash"') >= 8
      and fsrc.count("outdated") == 2)
check("F9 0 non-comment trailing-whitespace lines (D-084 M1)",
      sum(1 for l in fsrc.splitlines() if l != l.rstrip() and not l.lstrip().startswith("#")) == 0)

print(f"\n{fails} mismatch(es)")
sys.exit(1 if fails else 0)
