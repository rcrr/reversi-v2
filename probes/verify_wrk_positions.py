#
# verify_wrk_positions.py
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
# verify_wrk_positions.py
#
# Independent ground-truth probe for wrk_positions.py +
# hlp_config_schemas.py (session 21; re-pinned to
# the fixed behaviour in session 22).
#
# A: structure / source pins (no DB)
# B: live pipeline first run (DB hit + flat cache files)
# C: live pipeline second run (cache hit, no DB)
# D: cache_manager flow behaviours (live): disabled cache, corruption,
#    business inconsistency, wrk_positions_is_cache_consistent unit checks
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
import shutil
import atexit
from contextlib import contextmanager
from io import StringIO
from pathlib import Path

import numpy as np

sys.path.insert(0, "src")

from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel, LMContext
from reversi.regab import regab_load_data_set_from_file
from reversi.lm.wrk_positions import wrk_positions

WS = Path(__file__).resolve().parents[1]
TMP_BASE = WS / "build" / "tmp"
TMP_BASE.mkdir(parents=True, exist_ok=True)
PROBE_TMP = Path(tempfile.mkdtemp(dir=str(TMP_BASE)))
atexit.register(lambda: shutil.rmtree(PROBE_TMP, ignore_errors=True))
CONFIG_JSON = WS / "test" / "reversi" / "data" / "rlm_00.json"

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
import reversi.lm.wrk_positions as lp

check("A1 __all__ exposes factory + 3 helpers",
      lp.__all__ == ['wrk_positions', 'wrk_positions_extract_and_prepare', 'wrk_positions_is_cache_consistent'],
      repr(lp.__all__))
w = wrk_positions()
check("A2 factory name POSITIONS", w.name == "POSITIONS", w.name)
src = Path(lp.__file__).read_text()
check("A4 factory HAS @validate_call (M1)",
      "def wrk_positions() -> Worker:" in src
      and "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))" in src)
check("A5 pathlib.Path import removed (M2)",
      "from pathlib import Path" not in src)
# M3 scope (as in the M3 on lm_worker_config): only the flagged lines
# (L73/L89/L92) were the original flags; the remaining trailing
# whitespace (license header, import block, wrk_positions_is_cache_consistent body)
# was swept by the cascade formatting pass.
check("A6 the flagged trailing-whitespace lines (L73/L89/L92) now clean (M3)",
      "\n    ctx.rds_checksum = rds_checksum\n\n" in src
      and "    }\n\n    return\n\n\ndef _down" in src)

ctx = LMContext(config_file_path=Path("rlm_00.json"))
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
# (B1 deleted at D-106 step 3, class c: step 2 / POSITIONS pinned by
#  test_wrk_positions.py::test_read_db_and_populate_cache)
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
dat = b_dir / "rlmwf_04_POSITIONS.dat"
side = b_dir / "rlmwf_04_POSITIONS.dat.SHA3-256"
# (B4 deleted at D-106 step 3, class c: both flat files pinned by
#  test_wrk_positions.py::test_read_db_and_populate_cache —
#  the 'no rlmwf_ subdir' negative is implied by the flat paths)
side_text = side.read_text()
check("B5 sidecar is binio format '<hex>  <basename>'",
      re.fullmatch(r"[0-9a-f]{64}  rlmwf_04_POSITIONS\.dat\n?", side_text) is not None,
      repr(side_text[:80]))
rds_b = regab_load_data_set_from_file(dat)
check("B6 rds_checksum = the rds data checksum (duck-typed)",
      rds_b.compute_sha3_256_hash() == c1.rds_checksum)
# (B7 deleted at D-106 step 3, class c: the 'Extracted … positions
#  from the database.' log pin lives in test_wrk_positions.py
#  test_read_db_and_populate_cache; the 200 count stays pinned by B3a)

# ------------------------------------------------------------------ C
print("--- C. live pipeline second run (cache hit, no DB) ---")
m2, c_logs = run_model(CONFIG_JSON, b_dir, ("CONFIG", "POSITIONS"))
c2 = m2.context
# (C1/C2 deleted at D-106 step 3, class c: step 2 + the cache-hit /
#  no-DB log pins live in test_wrk_positions.py::
#  test_read_cache_on_new_instance)
check("C3 data identical across runs",
      np.array_equal(c1.positions, c2.positions)
      and c1.rds_checksum == c2.rds_checksum)
check("C4 stats identical across runs",
      c1.training_pop_stats["count"] == c2.training_pop_stats["count"]
      and abs(c1.training_pop_stats["mean"] - c2.training_pop_stats["mean"]) < 1e-12)

# ------------------------------------------------------------------ D
print("--- D. cache_manager flow behaviours (live) ---")

# (D1a/D1b deleted at D-106 step 3, class c: the same orchestration
#  facts — forced-computation message + cache still warmed — are
#  pinned in test_cache_manager.py::test_step0_not_allowed_forces_
#  computation (mocked, same cache_manager function); the live
#  use_cache wiring is source-pinned by F4 below)

# D2: corruption -> checksum step fails -> delete + recompute
d2_dir = fresh("d2_warm")
run_model(CONFIG_JSON, d2_dir, ("POSITIONS",))
(d2_dir / "rlmwf_04_POSITIONS.dat").write_bytes(b"CORRUPTED BY PROBE")
m4, d2_logs = run_model(CONFIG_JSON, d2_dir, ("POSITIONS",))
check("D2 corrupted .dat -> checksum WARN + delete + recompute",
      "Checksum validation failed" in d2_logs
      and "Deleting cache and recomputing" in d2_logs
      and "Extracted 200 positions from the database." in d2_logs
      and (d2_dir / "rlmwf_04_POSITIONS.dat").exists())

# D3: business inconsistency (ec 20 -> 10) -> validate_fn False -> recompute
def _ec10(d):
    d["empty_count"] = 10
ec10_path = PROBE_TMP / "rlm_00_ec10.json"
ec10_path.write_text(json5.dumps(cfg_dict_mutate(_ec10)))
d3_dir = fresh("d3_warm")
run_model(CONFIG_JSON, d3_dir, ("POSITIONS",))  # warms with ec 20
m5, d3_logs = run_model(ec10_path, d3_dir, ("POSITIONS",))
rds_d3 = regab_load_data_set_from_file(d3_dir / "rlmwf_04_POSITIONS.dat")
check("D3 inconsistent ec -> 'Application data validation failed' + recompute",
      "Application data validation failed" in d3_logs
      and "Deleting cache and recomputing" in d3_logs
      and "Extracted 200 positions from the database." in d3_logs)
check("D3b cache rewritten with the NEW params (ec=10)", rds_d3.ec == 10,
      f"ec={rds_d3.ec}")

# (D4a-g moved to tests at D-106 step 3, class a §4 conversion:
#  test_wrk_positions.py::TestIsCacheConsistent — the probe
#  warmed a real cache file through the live pipeline; the test
#  builds the same rds metadata in memory (no DB, no cache file))

# ------------------------------------------------------------------ E
print("--- E. rlm_config_schemas validation behaviour ---")
# (E1/E2/E2b/E3/E4/E5/E6/E6b/E8/E8b/E9/E10/E11/E12 moved to tests at
#  D-106 step 3, class a §4 conversion: test_rlm_config_schemas.py —
#  the first test file for the rlm_config_schemas module;
#  deterministic pydantic unit behaviour, no DB, no live pipeline.
#  E7 stays here: a source-text inspection, which stays a probe per
#  probe_rules.md §4.)
import reversi.lm.hlp_config_schemas as rs
rsrc = Path(rs.__file__).read_text()
check("E7 model_validator import now used by the c2>c1 validator (R1/M2)",
      "model_validator" in rsrc.split("from pydantic import")[1].split(")")[0]
      and "@model_validator" in rsrc)

# ------------------------------------------------------------------ F
print("--- F. source-level cross-reference pins ---")
lpsrc = src
seg = lpsrc.split("def _load_from_db")[1].split("def wrk_positions")[0]
check("F1 _load_from_db passes port + password (5-arg RegabDBConnection call)",
      "RegabDBConnection(conn_params.dbname, conn_params.user,\n"
      "                           conn_params.host, str(conn_params.port),\n"
      "                           conn_params.password)" in seg)
check("F2 load_fn passes checksum=False — no redundant sidecar verify (M4)",
      "load_fn     = lambda path: regab_load_data_set_from_file(path, checksum=False)" in lpsrc)
import reversi.regab as rg
rgsrc = Path(rg.__file__).read_text()
store_fn_src = rgsrc.split("def regab_store_data_set_to_file")[1].split("\ndef ")[0]
check("F3 regab_store docstring corrected — no sidecar promise (cross-ref)",
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
