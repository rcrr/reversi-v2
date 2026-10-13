#
# verify_cache_manager.py
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

# verify_cache_manager.py — independent ground-truth probes for the
# cache_manager.py analysis (session 20). Not part of the suite.
# Run: .venv/bin/python probes/verify_cache_manager.py
from __future__ import annotations

import atexit
import shutil
import tempfile
from pathlib import Path

from reversi.tools.cache_manager import (
    cache_manager_load_or_compute,
    SHA3_256_CHECKSUM_SUFFIX,
)
# _compute_checksum / _save_checksum were removed from
# cache_manager (the checksum service moved to reversi.tools.binio); the sidecar
# is now written in sha3_256sum format by write_sha3_256_sidecar.
from reversi.tools.binio import write_sha3_256_sidecar
from reversi.tools.state_machine import Relevance

TMP = Path(tempfile.mkdtemp(dir="build/tmp"))
# the probe artifacts are removed afterwards (probe_rules §2), also when a
# check fails mid-run: the atexit hook is the house idiom
atexit.register(lambda: shutil.rmtree(TMP, ignore_errors=True))
FAILS = []


def check(name, cond, detail=""):
    status = "ok  " if cond else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not cond:
        FAILS.append(name)


class Dummy:
    """Data object WITHOUT a compute_sha3_256_hash method."""
    def __init__(self, payload):
        self.payload = payload

    def __eq__(self, other):
        return isinstance(other, Dummy) and self.payload == other.payload


# (DummyWithHash / DummyBadHash removed at D-106 step 3 with the
#  V11/V12/V13 checks that exercised them — their duck-typed
#  checksum facts are pinned by the test_cache_manager.py tests
#  named in those deletions.)


def fresh_logger():
    events = []
    def log(rel, msg):
        events.append((rel, msg))
    return log, events


def run_pipeline(path, is_allowed=True, load_ret=None, load_exc=None,
                 validate_ret=True, data_factory=lambda: Dummy("c")):
    def load_fn(p):
        if load_exc is not None:
            raise load_exc
        return load_ret if load_ret is not None else Dummy("cached")

    def store_fn(d, p):
        p.write_text(str(d.payload))

    def compute_fn():
        return data_factory()

    log, events = fresh_logger()
    result = cache_manager_load_or_compute(
        cache_path=path, is_allowed=is_allowed, load_fn=load_fn,
        store_fn=store_fn, validate_fn=lambda d: validate_ret,
        compute_fn=compute_fn, logger_fn=log)
    return result, events


def sidecar(p: Path) -> Path:
    return p.with_suffix(p.suffix + SHA3_256_CHECKSUM_SUFFIX)


# (V1 deleted at D-106: _compute_checksum left cache_manager — the
# file-checksum fact now lives in reversi.tools.binio, pinned by test_binio /
# test_cache_manager; re-pin = c.)

# --- V2 sidecar naming ---------------------------------------------------
# with_suffix(suffix + ".SHA3-256") RE-APPLIES the original suffix:
# the sidecar is <full-original-name>.SHA3-256 (same scheme as binio).
for name, expect in [("data.dat", "data.dat.SHA3-256"),
                     ("a.b.dat", "a.b.dat.SHA3-256"),
                     ("data", "data.SHA3-256")]:
    p = TMP / name
    check(f"V2 sidecar of {name!r} == {expect!r}", sidecar(p).name == expect, sidecar(p).name)

# (V3a-d deleted at D-106 step 3, class c: the verify behaviour is
#  pinned by test_cache_manager.py::TestVerifyChecksum —
#  test_verify_checksum_missing / test_verify_checksum_ok /
#  test_verify_checksum_mismatch / test_verify_checksum_invalid_format)

# (V15 deleted at D-106: the sidecar-format fact FLIPPED when binio took over —
# binio sha3_256sum is now canonical and bare hex is the legacy
# compatibility path, so all three claims are obsolete; the current
# format is pinned by test_binio / test_cache_manager; re-pin = c.)

# (V4 deleted at D-106 step 3, class c: delete-both + idempotent is
#  pinned by test_cache_manager.py::TestDeleteCacheFiles)

# (V5a-d deleted at D-106 step 3, class c: step 0 is pinned by
#  test_cache_manager.py::TestCacheManagerFlow::test_step0_not_allowed_
#  forces_computation — the INFO message via assert_any_call, the
#  files still written, the (False, computed, None) tuple)

# (V6 deleted at D-106 step 3, class c: step 1 (missing file ->
#  compute + store) is pinned by test_cache_manager.py::
#  test_step1_missing_computes_and_stores)

# (V7a/V7b deleted at D-106 step 3, class c: step 2 (mismatch ->
#  delete + recompute + re-store) is pinned by
#  test_cache_manager.py::test_step2_checksum_mismatch_forces_
#  recomputation + the POSITIONS-worker live test)
# (V7c the step-2 WARN message: deleted at D-106 — category c per the
# classification, and its pinned text was stale anyway: the current
# message is "Checksum validation failed for … (sidecar missing or
# mismatched) …", pinned exactly by test_cache_manager's
# test_step2_checksum_mismatch_forces_recomputation via
# assert_any_call(Relevance.WARN, …).)

# (V8a-c deleted at D-106 step 3, class c: step 3a (load raises ->
#  delete + recompute + re-store, ERROR with the exception text) is
#  pinned by test_cache_manager.py::test_step3_load_error_forces_
#  recomputation)
# (V9a/V9b deleted at D-106 step 3, class c: step 3b (validation
#  fails -> recompute + re-store) is pinned by
#  test_validation_failed_forces_recomputation)
p9 = TMP / "v9.dat"
p9.write_text("data")
write_sha3_256_sidecar(p9, suffix=SHA3_256_CHECKSUM_SUFFIX)
r9, ev9 = run_pipeline(p9, is_allowed=True, load_ret=Dummy("cached"), validate_ret=False)
check("V9c step3b WARN message", any(rel is Relevance.WARN and "validation failed" in m for rel, m in ev9))

# (V10a/V10c deleted at D-106 step 3, class c: the success tuple +
#  the INFO message are pinned by test_cache_manager.py::test_step4_
#  valid_cache_returns_load)
p10 = TMP / "v10.dat"
p10.write_text("data")
write_sha3_256_sidecar(p10, suffix=SHA3_256_CHECKSUM_SUFFIX)
sentinel = Dummy("from-cache")
r10, ev10 = run_pipeline(p10, is_allowed=True, load_ret=sentinel)
check("V10b success identity: same object as load returned", r10[1] is sentinel)

# (V11a/V11b deleted at D-106 step 3, class c: the duck-typed data
#  checksum on both paths is pinned by
#  test_compute_path_uses_data_own_checksum +
#  test_load_path_uses_data_own_checksum)
# (V12/V12b deleted at D-106 step 3, class c: the non-callable-attr
#  and no-attr None returns are pinned by
#  test_compute_sha3_256_hash_non_callable_method +
#  test_compute_sha3_256_hash_no_method)
# (V13/V13b deleted at D-106 step 3, class c: the load-path hash
#  raise -> recompute + the ERROR log are pinned by
#  test_load_path_hash_error_forces_recomputation)

# --- V16 logger receives (Relevance, str) -----------------------------------------------
p16 = TMP / "v16.dat"
_, ev16 = run_pipeline(p16, is_allowed=False)
check("V16 logger args are (Relevance, str)", all(isinstance(r, Relevance) and isinstance(m, str) for r, m in ev16))

# (V17 moved to a test at D-106 step 3, class a §4 conversion:
#  test_cache_manager.py::TestValidateCallCoercion::
#  test_str_cache_path_is_coerced_to_path — the @validate_call
#  str->Path coercion (D-106/D-107 re-pin: the inner store_fn must
#  observe a Path; the flow then dies in the framework's sidecar
#  write with FileNotFoundError)

print()
if FAILS:
    print(f"{len(FAILS)} FAILURES: {FAILS}")
    raise SystemExit(1)
print("ALL PROBES PASSED")
