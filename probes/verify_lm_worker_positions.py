#
# verify_lm_worker_positions.py
#
# Independent ground-truth probe for lm_worker_positions.py +
# rlm_config_schemas.py (session 21, D-079 analysis; re-pinned to
# the fixed behaviour in session 22, D-080).
#
# A: structure / source pins (no DB)
# B: live pipeline first run (DB hit + flat cache files)
# C: live pipeline second run (cache hit, no DB)
# D: cache_manager flow behaviours (live): disabled cache, corruption,
#    business inconsistency, is_cache_consistent unit checks
# E: rlm_config_schemas validation behaviour (no DB)
# F: source-level cross-reference pins
#
# Test DB: tst_regab@localhost (fixture rlm_00.json), bid 8 has rows
# for ec 10 and ec 20 (200 rows) and CMS-only (100 rows).

from __future__ import annotations

import json5
import re
import sys
import tempfile
import os
import shutil
import atexit
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")

from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel, RLMContext
from twolm.rlm_config_schemas import (
    ReversiLogisticModelConfig,
    PatternConfig,
    PatternSetConfig,
    OptimizationConfig,
    ValidationDataSetConfig,
    StatModelConfig,
)
from twolm.regab import regab_load_data_set_from_file
from twolm.lm_worker_positions import (
    lm_worker_positions,
    is_cache_consistent,
)

WS = Path(__file__).resolve().parents[1]
TMP_BASE = WS / "build" / "tmp"
TMP_BASE.mkdir(parents=True, exist_ok=True)
PROBE_TMP = Path(tempfile.mkdtemp(dir=str(TMP_BASE)))
atexit.register(lambda: shutil.rmtree(PROBE_TMP, ignore_errors=True))
CONFIG_JSON = WS / "src" / "twolm" / "test" / "data" / "rlm_00.json"

RESULTS = []

def check(label: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((label, ok))
    print(f"[{'ok  ' if ok else 'FAIL'}] {label}" + (f" — {detail}" if detail and not ok else ""))

@contextmanager
def quiet_stdout():
    real = sys.stdout
    buf = StringIO()
    sys.stdout = buf
    try:
        yield buf
    finally:
        sys.stdout = real

def run_quiet(fn) -> str:
    with quiet_stdout() as buf:
        fn()
    return buf.getvalue()

def run_model(cfg_path: Path, base_dir: Path, steps=("POSITIONS",)):
    """Build a model inside a quiet context, move through the steps,
    and return (model, captured logs)."""
    holder = {}
    def _go():
        m = model_for(cfg_path, base_dir)
        holder["m"] = m
        for s in steps:
            m.move_to_step(s)
    logs = run_quiet(_go)
    return holder["m"], logs

def fresh(name: str) -> Path:
    d = PROBE_TMP / name
    d.mkdir(parents=True, exist_ok=False)
    return d

def model_for(cfg_path: Path, base_dir: Path):
    return LogisticModel(str(cfg_path), verbosity=Verbosity.HIGH,
                         base_dir_override=str(base_dir))

def cfg_dict_mutate(mutate=None) -> dict:
    d = json5.loads(CONFIG_JSON.read_text())
    if mutate:
        mutate(d)
    return d

# ------------------------------------------------------------------ A
print("--- A. structure / source pins (no DB) ---")
import twolm.lm_worker_positions as lp

check("A1 __all__ exposes factory + 2 helpers",
      lp.__all__ == ['lm_worker_positions', 'load_from_db', 'is_cache_consistent'],
      repr(lp.__all__))
w = lm_worker_positions()
check("A2 factory name POSITIONS", w.name == "POSITIONS", w.name)
src = Path(lp.__file__).read_text()
check("A4 factory HAS @validate_call (D-080 M1)",
      "def lm_worker_positions() -> Worker:" in src
      and "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))" in src)
check("A5 pathlib.Path import removed (D-080 M2)",
      "from pathlib import Path" not in src)
# M3 scope (as in D-078 M3 on lm_worker_config): only the D-079-
# flagged lines (L73/L89/L92) are cleaned; the remaining trailing
# whitespace (license header, import block, is_cache_consistent
# body) stays as in the original file.
check("A6 D-079-flagged trailing-whitespace lines (L73/L89/L92) now clean (D-080 M3)",
      "\n    ctx.rds_checksum = rds_checksum\n\n" in src
      and "    }\n\n    return\n\n\ndef _down" in src)

ctx = RLMContext(config_file_path=Path("rlm_00.json"))
ctx.positions = object()
ctx.game_values = object()
ctx.rds_checksum = "x"
ctx.training_pop_stats = {"a": 1}
lp._down(ctx)
check("A3 _down resets the 4 context attributes",
      ctx.positions is None and ctx.game_values is None
      and ctx.rds_checksum is None and ctx.training_pop_stats is None)

# ------------------------------------------------------------------ B
print("--- B. live pipeline first run (DB hit) ---")
b_dir = fresh("b_first_run")
m1, b_logs = run_model(CONFIG_JSON, b_dir, ("POSITIONS",))
c1 = m1.context
check("B1 step 2 / POSITIONS", m1.current_step == 2 and m1.current_worker_name == "POSITIONS")
check("B2 positions/game_values/rds_checksum set",
      c1.positions is not None and c1.game_values is not None
      and isinstance(c1.rds_checksum, str) and len(c1.rds_checksum) == 64,
      repr(c1.rds_checksum))
pstats = c1.training_pop_stats
check("B3a stats keys",
      pstats is not None and set(pstats) == {"count", "mean", "std_dev", "variance"},
      repr(pstats))
gv = c1.game_values
check("B3b stats values match independent numpy recompute",
      pstats["count"] == len(gv)
      and abs(pstats["mean"] - float(np.mean(gv))) < 1e-9
      and abs(pstats["std_dev"] - float(np.std(gv))) < 1e-9
      and abs(pstats["variance"] - float(np.var(gv))) < 1e-9
      and pstats["count"] == 200)
dat = b_dir / "rlmwf_02_POSITIONS.dat"
side = b_dir / "rlmwf_02_POSITIONS.dat.SHA3-256"
check("B4 flat cache files exist, no rlmwf_ subdir",
      dat.exists() and side.exists() and not (b_dir / "rlmwf_").is_dir())
side_text = side.read_text()
check("B5 sidecar is binio format '<hex>  <basename>'",
      re.fullmatch(r"[0-9a-f]{64}  rlmwf_02_POSITIONS\.dat\n?", side_text) is not None,
      repr(side_text[:80]))
rds_b = regab_load_data_set_from_file(dat)
check("B6 rds_checksum = the rds data checksum (duck-typed)",
      rds_b.compute_sha3_256_hash() == c1.rds_checksum)
check("B7 DB was hit (log pin)",
      "Extracted 200 positions from the database." in b_logs)

# ------------------------------------------------------------------ C
print("--- C. live pipeline second run (cache hit, no DB) ---")
m2, c_logs = run_model(CONFIG_JSON, b_dir, ("CONFIG", "POSITIONS"))
c2 = m2.context
check("C1 step 2 / POSITIONS", m2.current_step == 2 and m2.current_worker_name == "POSITIONS")
check("C2 cache hit, no DB",
      "Cache successfully loaded and validated" in c_logs
      and "Extracted" not in c_logs
      and "established successfully" not in c_logs)
check("C3 data identical across runs",
      np.array_equal(c1.positions, c2.positions)
      and c1.rds_checksum == c2.rds_checksum)
check("C4 stats identical across runs",
      c1.training_pop_stats["count"] == c2.training_pop_stats["count"]
      and abs(c1.training_pop_stats["mean"] - c2.training_pop_stats["mean"]) < 1e-12)

# ------------------------------------------------------------------ D
print("--- D. cache_manager flow behaviours (live) ---")

# D1: use_cache=False -> forced computation, cache STILL warmed (D-071 R1)
def _no_cache(d):
    d["use_cache"] = False
nc_path = PROBE_TMP / "rlm_00_nocache.json"
nc_path.write_text(json5.dumps(cfg_dict_mutate(_no_cache)))
d1_dir = fresh("d1_nocache")
m3, d1_logs = run_model(nc_path, d1_dir, ("POSITIONS",))
check("D1a use_cache=False -> 'Cache not allowed' forced computation",
      "Cache not allowed by configuration. Forcing computation." in d1_logs)
check("D1b cache-disabled run still warms the cache file",
      (d1_dir / "rlmwf_02_POSITIONS.dat").exists()
      and (d1_dir / "rlmwf_02_POSITIONS.dat.SHA3-256").exists())

# D2: corruption -> checksum step fails -> delete + recompute
d2_dir = fresh("d2_warm")
run_model(CONFIG_JSON, d2_dir, ("POSITIONS",))
(d2_dir / "rlmwf_02_POSITIONS.dat").write_bytes(b"CORRUPTED BY PROBE")
m4, d2_logs = run_model(CONFIG_JSON, d2_dir, ("POSITIONS",))
check("D2 corrupted .dat -> checksum WARN + delete + recompute",
      "Checksum validation failed" in d2_logs
      and "Deleting cache and recomputing" in d2_logs
      and "Extracted 200 positions from the database." in d2_logs
      and (d2_dir / "rlmwf_02_POSITIONS.dat").exists())

# D3: business inconsistency (ec 20 -> 10) -> validate_fn False -> recompute
def _ec10(d):
    d["regab_data_set"]["ec"] = 10
ec10_path = PROBE_TMP / "rlm_00_ec10.json"
ec10_path.write_text(json5.dumps(cfg_dict_mutate(_ec10)))
d3_dir = fresh("d3_warm")
run_model(CONFIG_JSON, d3_dir, ("POSITIONS",))  # warms with ec 20
m5, d3_logs = run_model(ec10_path, d3_dir, ("POSITIONS",))
rds_d3 = regab_load_data_set_from_file(d3_dir / "rlmwf_02_POSITIONS.dat")
check("D3 inconsistent ec -> 'Application data validation failed' + recompute",
      "Application data validation failed" in d3_logs
      and "Deleting cache and recomputing" in d3_logs
      and "Extracted 200 positions from the database." in d3_logs)
check("D3b cache rewritten with the NEW params (ec=10)", rds_d3.ec == 10,
      f"ec={rds_d3.ec}")

# D4: is_cache_consistent unit checks (no DB — pure metadata compare)
rds_warm = regab_load_data_set_from_file(b_dir / "rlmwf_02_POSITIONS.dat")

def mk_ctx(mutate=None):
    v = ReversiLogisticModelConfig(**cfg_dict_mutate(mutate))
    cx = RLMContext(config_file_path=Path("rlm_00.json"))
    cx.cfg = v
    return cx

check("D4a same cfg -> consistent",
      is_cache_consistent(mk_ctx(), rds_warm) is True)
def _ec19(d): d["regab_data_set"]["ec"] = 19
def _bid9(d): d["regab_data_set"]["bid"] = [9]
def _st_cms(d): d["regab_data_set"]["status"] = ["CMS"]
def _dbname(d): d["regab_data_set"]["regab_db_connection"]["dbname"] = "other_db"
check("D4b different ec -> inconsistent",
      is_cache_consistent(mk_ctx(_ec19), rds_warm) is False)
check("D4c different bid -> inconsistent",
      is_cache_consistent(mk_ctx(_bid9), rds_warm) is False)
check("D4d different status -> inconsistent",
      is_cache_consistent(mk_ctx(_st_cms), rds_warm) is False)
check("D4e different dbname -> inconsistent",
      is_cache_consistent(mk_ctx(_dbname), rds_warm) is False)
check("D4f keyword override wins (bid=[9])",
      is_cache_consistent(mk_ctx(), rds_warm, bid=[9]) is False
      and is_cache_consistent(mk_ctx(), rds_warm, bid=[8], status=["CMS", "CMR"]) is True)
check("D4g str port (regab) vs int port (schema) compares equal",
      rds_warm.rc.port == "5432" and is_cache_consistent(mk_ctx(), rds_warm) is True)

# ------------------------------------------------------------------ E
print("--- E. rlm_config_schemas validation behaviour ---")
base = cfg_dict_mutate()
cfg0 = ReversiLogisticModelConfig(**base)
dumped = json5.loads(cfg0.model_dump_json())
check("E1 round-trip via model_dump_json",
      json5.loads(json5.dumps(dumped))["name"] == base["name"]
      and dumped["cache_files_prefix"] == "rlmwf_")
pc = PatternConfig(name="p", mask="0000000000000107")
check("E2 16-hex (no 0x) -> Bitboard + uppercase 16-hex serializer",
      pc.mask == 0x107
      and json5.loads(PatternConfig(name="p", mask="0000000000000107").model_dump_json())["mask"]
      == "0000000000000107")
try:
    PatternConfig(name="p", mask="0x0000000000000107")
    check("E2b '0x'-prefixed mask REJECTED (docstring example mismatches the parser) (M-item)",
          False, "no exception")
except Exception as e:
    check("E2b '0x'-prefixed mask REJECTED (docstring example mismatches the parser) (M-item)",
          type(e).__name__ == "ValidationError", type(e).__name__)
def _badmask(d):
    d["feature_set"]["pattern_set"]["patterns"][0]["mask"] = "ZZZZ"
try:
    ReversiLogisticModelConfig(**cfg_dict_mutate(_badmask))
    check("E3 invalid hex mask -> ValidationError", False, "no exception")
except Exception as e:
    check("E3 invalid hex mask -> ValidationError",
          type(e).__name__ == "ValidationError", type(e).__name__)
for bad_ec, label in [(99, "E4a"), (-1, "E4b")]:
    def _bdec(d, e=bad_ec): d["regab_data_set"]["ec"] = e
    try:
        ReversiLogisticModelConfig(**cfg_dict_mutate(_bdec))
        check(f"{label} ec={bad_ec} -> ValidationError", False, "no exception")
    except Exception as e:
        check(f"{label} ec={bad_ec} -> ValidationError",
              type(e).__name__ == "ValidationError", type(e).__name__)
for bad, label in [("cms", "E5a"), ("CMSX", "E5b")]:
    def _badst(d, s=bad): d["regab_data_set"]["status"] = [s]
    try:
        ReversiLogisticModelConfig(**cfg_dict_mutate(_badst))
        check(f"{label} status '{bad}' -> ValidationError", False, "no exception")
    except Exception as e:
        check(f"{label} status '{bad}' -> ValidationError",
              type(e).__name__ == "ValidationError", type(e).__name__)
try:
    OptimizationConfig(checkpoint_file="c.json", c1=0.9, c2=0.1)
    check("E6 c1=0.9 + c2=0.1 REJECTED — cross-field c2>c1 validator (D-080 R1)",
          False, "no exception")
except Exception as e:
    check("E6 c1=0.9 + c2=0.1 REJECTED — cross-field c2>c1 validator (D-080 R1)",
          type(e).__name__ == "ValidationError", type(e).__name__)
o = OptimizationConfig(checkpoint_file="c.json", c1=0.1, c2=0.9)
check("E6b c1=0.1 + c2=0.9 accepted (D-080 R1)", o.c1 == 0.1 and o.c2 == 0.9)
import twolm.rlm_config_schemas as rs
rsrc = Path(rs.__file__).read_text()
check("E7 model_validator import now used by the c2>c1 validator (D-080 R1/M2)",
      "model_validator" in rsrc.split("from pydantic import")[1].split(")")[0]
      and "@model_validator" in rsrc)
try:
    ValidationDataSetConfig(bid=[1], status=["xyz"])
    check("E8 validation_data_set.status is STRICT StatusString (D-080 M3)",
          False, "no exception")
except Exception as e:
    check("E8 validation_data_set.status is STRICT StatusString (D-080 M3)",
          type(e).__name__ == "ValidationError", type(e).__name__)
check("E8b valid 3-letter status accepted (D-080 M3)",
      ValidationDataSetConfig(bid=[1], status=["CMS", "CMR"]).status == ["CMS", "CMR"])
check("E9 StatModelConfig HAS the RLMBaseConfig 'properties' field (D-080 M3)",
      "properties" in StatModelConfig.model_fields
      and "properties" in ValidationDataSetConfig.model_fields)
ps1 = PatternSetConfig(name="a")
ps2 = PatternSetConfig(name="b")
ps1.patterns.append(pc)
check("E10 mutable default [] is NOT shared across instances",
      len(ps1.patterns) == 1 and len(ps2.patterns) == 0)
def _nooutput(d): del d["output"]
try:
    ReversiLogisticModelConfig(**cfg_dict_mutate(_nooutput))
    check("E11 missing output -> ValidationError", False, "no exception")
except Exception as e:
    check("E11 missing output -> ValidationError",
          type(e).__name__ == "ValidationError", type(e).__name__)
def _noidx(d): del d["cache_files_prefix"]
check("E12 cache_files_prefix default 'rlmwf_'",
      ReversiLogisticModelConfig(**cfg_dict_mutate(_noidx)).cache_files_prefix == "rlmwf_")

# ------------------------------------------------------------------ F
print("--- F. source-level cross-reference pins ---")
lpsrc = src
seg = lpsrc.split("def load_from_db")[1].split("def lm_worker_positions")[0]
check("F1 load_from_db passes port + password (5-arg RegabDBConnection call) (D-080 R1)",
      "RegabDBConnection(conn_params.dbname, conn_params.user,\n"
      "                           conn_params.host, str(conn_params.port),\n"
      "                           conn_params.password)" in seg)
check("F2 load_fn passes checksum=False — no redundant sidecar verify (D-080 M4)",
      "load_fn     = lambda path: regab_load_data_set_from_file(path, checksum=False)" in lpsrc)
import twolm.regab as rg
rgsrc = Path(rg.__file__).read_text()
store_fn_src = rgsrc.split("def regab_store_data_set_to_file")[1].split("\ndef ")[0]
check("F3 regab_store docstring corrected — no sidecar promise (D-080 cross-ref)",
      "calculates the SHA3-256 checksum" not in store_fn_src
      and "cache_manager" in store_fn_src)
check("F4 use_cache IS consumed here (is_allowed=ctx.use_cache) — the CONFIG worker's switch",
      "is_allowed  = ctx.use_cache" in lpsrc)

# ------------------------------------------------------------------
fails = [l for l, ok in RESULTS if not ok]
print(f"\n{len(fails)} mismatches out of {len(RESULTS)} checks.")
if fails:
    print("FAILED:", *fails, sep="\n  ")
sys.exit(1 if fails else 0)
