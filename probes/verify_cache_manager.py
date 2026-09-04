# verify_cache_manager.py — independent ground-truth probes for the
# cache_manager.py analysis (session 20). Not part of the suite.
# Run: .venv/bin/python scratch/verify_cache_manager.py
from __future__ import annotations

import tempfile
from pathlib import Path

from twolm.cache_manager import (
    cache_manager_load_or_compute,
    _verify_checksum,
    _delete_cache_files,
    _compute_sha3_256_hash,
    SHA3_256_CHECKSUM_SUFFIX,
)
# D-072: _compute_checksum / _save_checksum were removed from
# cache_manager (the checksum service moved to twolm.binio); the sidecar
# is now written in sha3_256sum format by write_sha3_256_sidecar.
from twolm.binio import write_sha3_256_sidecar
from twolm.state_machine import Relevance

TMP = Path(tempfile.mkdtemp(dir="build/tmp"))
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


class DummyWithHash:
    """Data object WITH the duck-typed method."""
    def __init__(self, payload, digest="ab" * 32):
        self.payload = payload
        self._digest = digest
        self.hash_calls = 0

    def compute_sha3_256_hash(self):
        self.hash_calls += 1
        return self._digest


class DummyBadHash(DummyWithHash):
    def compute_sha3_256_hash(self):
        raise RuntimeError("hash boom")


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


# (V1 deleted at D-106: _compute_checksum was removed in D-072 — the
# file-checksum fact now lives in twolm.binio, pinned by test_binio /
# test_cache_manager; re-pin = c.)

# --- V2 sidecar naming ---------------------------------------------------
# with_suffix(suffix + ".SHA3-256") RE-APPLIES the original suffix:
# the sidecar is <full-original-name>.SHA3-256 (same scheme as binio).
for name, expect in [("data.dat", "data.dat.SHA3-256"),
                     ("a.b.dat", "a.b.dat.SHA3-256"),
                     ("data", "data.SHA3-256")]:
    p = TMP / name
    check(f"V2 sidecar of {name!r} == {expect!r}", sidecar(p).name == expect, sidecar(p).name)

# --- V3 verify behaviour ---------------------------------------------------
p3 = TMP / "v3.dat"
p3.write_text("x")
check("V3a verify False when sidecar missing", _verify_checksum(p3) is False)
write_sha3_256_sidecar(p3, suffix=SHA3_256_CHECKSUM_SUFFIX)
check("V3b verify True after save", _verify_checksum(p3) is True)
p3.write_text("x CHANGED")
check("V3c verify False after data tamper", _verify_checksum(p3) is False)
sidecar(p3).write_text("0" * 64)
p3.write_text("x")
check("V3d verify False with wrong sidecar", _verify_checksum(p3) is False)

# (V15 deleted at D-106: the sidecar-format fact FLIPPED in D-072 —
# binio sha3_256sum is now canonical and bare hex is the legacy
# compatibility path, so all three claims are obsolete; the current
# format is pinned by test_binio / test_cache_manager; re-pin = c.)

# --- V4 delete ----------------------------------------------------------------
p4 = TMP / "v4.dat"
p4.write_text("d")
write_sha3_256_sidecar(p4, suffix=SHA3_256_CHECKSUM_SUFFIX)
_delete_cache_files(p4)
_delete_cache_files(p4)  # must not raise
check("V4 delete removes both + idempotent", not p4.exists() and not sidecar(p4).exists())

# --- V5 step 0: is_allowed=False still stores --------------------------------
p5 = TMP / "v5.dat"
p5.write_text("old")
r5, ev5 = run_pipeline(p5, is_allowed=False)
check("V5a step0 returns (False, computed, None)", r5[0] is False and r5[2] is None)
check("V5b step0 cache file STILL WRITTEN", p5.exists() and sidecar(p5).exists())
check("V5c step0 message", ev5[0] == (Relevance.INFO, "Cache not allowed by configuration. Forcing computation."), str(ev5[0]))
check("V5d step0 no load/validate events", not any("loaded" in m for _, m in ev5))

# --- V6 step 1: missing file ---------------------------------------------------
p6 = TMP / "v6.dat"
r6, _ = run_pipeline(p6, is_allowed=True)
check("V6 step1 missing -> compute+store, (False, data, None)", r6[0] is False and p6.exists() and sidecar(p6).exists())

# --- V7 step 2: mismatch -> delete + recompute ------------------------------
p7 = TMP / "v7.dat"
p7.write_text("corrupt")
sidecar(p7).write_text("0" * 64)
r7, ev7 = run_pipeline(p7, is_allowed=True)
new_content = p7.read_text()
check("V7a step2 returns (False, data, None)", r7[0] is False and r7[2] is None)
check("V7b step2 old files deleted + re-stored (content is the recomputed payload)", new_content == "c" and _verify_checksum(p7) is True)
# (V7c the step-2 WARN message: deleted at D-106 — category c per the
# classification, and its pinned text was stale anyway: the current
# message is "Checksum validation failed for … (sidecar missing or
# mismatched) …", pinned exactly by test_cache_manager's
# test_step2_checksum_mismatch_forces_recomputation via
# assert_any_call(Relevance.WARN, …).)

# --- V8 step 3a: load raises ----------------------------------------------------
p8 = TMP / "v8.dat"
p8.write_text("data")
write_sha3_256_sidecar(p8, suffix=SHA3_256_CHECKSUM_SUFFIX)
r8, ev8 = run_pipeline(p8, is_allowed=True, load_exc=IOError("disk dead"))
check("V8a step3a returns (False, computed, None)", r8[0] is False and r8[2] is None)
check("V8b step3a old files deleted + re-stored (content is the recomputed payload)", p8.exists() and p8.read_text() == "c" and _verify_checksum(p8) is True)
check("V8c step3a ERROR message carries exception text", any(rel is Relevance.ERROR and "disk dead" in m for rel, m in ev8), str([m for _, m in ev8]))

# --- V9 step 3b: validation fails ------------------------------------------------
p9 = TMP / "v9.dat"
p9.write_text("data")
write_sha3_256_sidecar(p9, suffix=SHA3_256_CHECKSUM_SUFFIX)
r9, ev9 = run_pipeline(p9, is_allowed=True, load_ret=Dummy("cached"), validate_ret=False)
check("V9a step3b returns (False, computed, None)", r9[0] is False and r9[2] is None)
check("V9b step3b re-stored (content is the recomputed payload)", p9.read_text() == "c" and _verify_checksum(p9) is True)
check("V9c step3b WARN message", any(rel is Relevance.WARN and "validation failed" in m for rel, m in ev9))

# --- V10 success path ---------------------------------------------------------------
p10 = TMP / "v10.dat"
p10.write_text("data")
write_sha3_256_sidecar(p10, suffix=SHA3_256_CHECKSUM_SUFFIX)
sentinel = Dummy("from-cache")
r10, ev10 = run_pipeline(p10, is_allowed=True, load_ret=sentinel)
check("V10a success returns (True, loaded, None-for-plain-data)", r10[0] is True and r10[2] is None)
check("V10b success identity: same object as load returned", r10[1] is sentinel)
check("V10c success INFO message", any(rel is Relevance.INFO and "Cache successfully loaded" in m for rel, m in ev10))

# --- V11 duck-typed data checksum -----------------------------------------------------
obj = DummyWithHash("x", digest="cd" * 32)
p11 = TMP / "v11.dat"
r11, _ = run_pipeline(p11, is_allowed=False, data_factory=lambda: obj)
check("V11a compute path returns the data's own checksum", r11 == (False, obj, "cd" * 32))

p11b = TMP / "v11b.dat"
p11b.write_text("x")
write_sha3_256_sidecar(p11b, suffix=SHA3_256_CHECKSUM_SUFFIX)
obj_b = DummyWithHash("x", digest="ef" * 32)
r11b, _ = run_pipeline(p11b, is_allowed=True, load_ret=obj_b)
check("V11b load path returns the data's own checksum", r11b[0] is True and r11b[2] == "ef" * 32)

# --- V12 non-callable attribute -------------------------------------------------------
d12 = DummyWithHash("x")
d12.compute_sha3_256_hash = 5  # replace with a non-callable
check("V12 non-callable attr -> checksum None, no exception", _compute_sha3_256_hash(d12) is None)
check("V12b dict (no attr) -> None", _compute_sha3_256_hash({"a": 1}) is None)

# --- V13 hash method raises on load path ----------------------------------------------
p13 = TMP / "v13.dat"
p13.write_text("x")
write_sha3_256_sidecar(p13, suffix=SHA3_256_CHECKSUM_SUFFIX)
bad = DummyBadHash("x")
r13, ev13 = run_pipeline(p13, is_allowed=True, load_ret=bad)
check("V13 load-path hash raise is caught -> recompute", r13[0] is False and r13[1] is not bad and isinstance(r13[1], Dummy))
check("V13b ERROR log mentions the raise", any(rel is Relevance.ERROR and "hash boom" in m for rel, m in ev13))

# --- V16 logger receives (Relevance, str) -----------------------------------------------
p16 = TMP / "v16.dat"
_, ev16 = run_pipeline(p16, is_allowed=False)
check("V16 logger args are (Relevance, str)", all(isinstance(r, Relevance) and isinstance(m, str) for r, m in ev16))

# --- V17 str cache_path: @validate_call coerces to Path (D-106 re-pin) --
# The original premise — "no @validate_call here, the raw str reaches
# .exists() as an AttributeError" — is stale: the function carries
# @validate_call now (the D-076-era gate idiom) and pydantic lax mode
# coerces str -> Path. The flow then dies in the framework's sidecar
# write (write_sha3_256_sidecar -> open(path, "rb"), FileNotFoundError:
# the probe's no-op store_fn never created the file). Pinned here: the
# COERCION — the inner callback must observe a Path. (Verified live
# 2026-09-04: store_fn sees a pathlib.PosixPath.) §4 test-conversion
# candidate (the coercion is unique — no test covers it).
v17_seen = []
try:
    cache_manager_load_or_compute(cache_path="not-a-path", is_allowed=False,
                                  load_fn=lambda p: None,
                                  store_fn=lambda d, p: v17_seen.append(p),
                                  validate_fn=lambda d: True, compute_fn=lambda: None,
                                  logger_fn=lambda r, m: None)
    check("V17 str cache_path coerced to Path (@validate_call)", False,
          "no exception")
except FileNotFoundError:
    check("V17 str cache_path coerced to Path (@validate_call)",
          bool(v17_seen) and isinstance(v17_seen[0], Path),
          type(v17_seen[0]).__name__ if v17_seen else "store_fn not called")
except Exception as e:
    check("V17 str cache_path coerced to Path (@validate_call)",
          False, f"{type(e).__name__}: {e}")

print()
if FAILS:
    print(f"{len(FAILS)} FAILURES: {FAILS}")
    raise SystemExit(1)
print("ALL PROBES PASSED")
