# cache_manager.py — analysis

Date: 2026-08-30. Module added by Roberto (2 files: cache_manager.py +
test_cache_manager.py, commit a0cd31f). **Analysis session 20; fix
campaign batch 1 applied (D-071): R1 resolved as intentional
(documented + pinned), R2 fixed (validate in the try), R4 fixed
(@validate_call), M1-M3 fixed, T1/T2/T3/T4/T5/T7 pinned + 8 new
tests — suite 13 → 21. Still OPEN: R3 (awaiting Roberto's ruling),
T6 (awaiting Roberto's OK), T8 (report-only).**

Suite: **21 tests, GREEN 21/0/0** (no PERF gates). Suite is fast
(~0.034s).

Full workspace: **468 tests, GREEN, 52 skipped under the gate**
(17 PERF + 35 regab DB-gated; without `SKIP_REGAB_DB=1` the DB tests
run against live PostgreSQL and only 17 skip).

## Architecture

`cache_manager` is a small, domain-agnostic caching utility: one
public function orchestrates a 4-step validation pipeline for
"load cached result or recompute" around injected business-logic
callbacks. It is the first domain module to import
`twolm.state_machine` (`Relevance` for the injected logger). The
public function carries the house `@validate_call` gate (D-071/R4):
`cache_path` is coerced `str` → `Path`, non-coercible values raise
`ValidationError`.

### Components

| Component | Role |
|---|---|
| `cache_manager_load_or_compute(...)` | The only public API. 4-step pipeline (below). Returns `(cache_hit: bool, data: T, data_checksum: str \| None)`. |
| `_compute_checksum(path)` | SHA3-256 of a file (8 KiB read chunks) → 64-char lowercase hex. |
| `_verify_checksum(path)` | Step 2: sidecar exists AND content (stripped) equals the recomputed file checksum. |
| `_save_checksum(path)` | Writes the sidecar with the bare hexdigest (no newline, no filename). |
| `_delete_cache_files(path)` | Unlinks data + sidecar, both `missing_ok=True` (idempotent). |
| `_compute_sha3_256_hash(data)` | Duck typing: if the data object has a callable `compute_sha3_256_hash` attribute, call it and return the result, else `None`. |
| `_compute_and_store(...)` | The shared "compute" tail: INFO log, `compute_fn()`, data checksum, `store_fn(data, path)`, sidecar, INFO logs; returns `(False, data, data_checksum)`. |
| `SHA3_256_CHECKSUM_SUFFIX` | `".SHA3-256"` — sidecar suffix constant. |
| `ComputeFunc / LoadFunc / StoreFunc / ValidateFunc / LoggerFunc` | Type aliases for the injected callbacks. |

### Pipeline (steps 0-3, per the docstring)

1. **Step 0 — allowed?** `is_allowed` false → compute tail. The
   compute tail **also stores** (V5b) — INTENTIONAL by Roberto's
   ruling (D-071/R1): a cache-disabled run forces the recompute but
   the result is always transcribed to the cache file (warms the
   cache); pinned in the docstring + by the test (T4).
2. **Step 1 — present?** data file missing → compute tail.
3. **Step 2 — consistent?** sidecar missing or mismatching → WARN
   "Checksum validation failed ... (sidecar missing or mismatched)",
   delete both files, compute tail.
4. **Step 3 — valid?** `load_fn(path)` + the duck-typed data checksum
   + `validate_fn(data)` are wrapped in ONE try/except (post
   D-071/R2: a raising validator is treated exactly like a load
   failure) → ERROR "Failed to load or validate cache file ...",
   delete both, compute tail. Then a `validate_fn` returning False
   (no exception) → WARN "Application data validation failed ...",
   delete both, compute tail.
5. **Success** → INFO, return `(True, loaded_data, loaded_data_checksum)`.

All failure paths converge on `_compute_and_store`: after any
invalidation the caller always gets fresh, stored, checksummed data —
the pipeline never returns partially validated state.

### The two checksums (do not confuse)

- **File checksum** (the sidecar): integrity of the cached bytes on
  disk. Bare hexdigest format (V15).
- **Data checksum** (3rd return element): content hash of the business
  data object, obtained duck-typing `data.compute_sha3_256_hash()`.
  `None` when the object has no such callable. Intended for the
  caller to record (e.g. in the DB) which content was loaded/computed.
  Different value AND different concept from the file checksum (per
  the docstring, L142 — typos in original, M2).

### Integration notes

- `logger_fn` takes `(Relevance, str)` — the natural binding is the
  `log_event` method that `StateMachine.__init__` injects into the
  shared `Context` (V17 context-injection, M9 left as-is per D-070).
- The `.dat` cache files this module validates match the naming
  produced by the state_machine `Context` cache helpers
  (`{prefix}{level:02}_{name}.dat`, D-069 M5/M8): this module is the
  load-or-compute engine for exactly those files.
- Sidecar naming (`<full-name>.SHA3-256`) is the same scheme binio
  uses for its sidecars (V2), but the **content format differs**
  (V15c, R3).

## Verified facts (V1-V17)

Independently re-derived (scratch/verify_cache_manager.py, 33 checks
+ 2 boundary probes), zero mismatches.

| # | Fact | Method |
|---|---|---|
| V1 | `_compute_checksum` = independent `hashlib.sha3_256` of the file bytes; 64-char lowercase hex; deterministic | Direct compare + charset check |
| V2 | Sidecar name = `<full-original-name>.SHA3-256` (`with_suffix` re-applies the original suffix: `data.dat` → `data.dat.SHA3-256`, `a.b.dat` → `a.b.dat.SHA3-256`, extension-less `data` → `data.SHA3-256`) — same naming scheme as binio | Path probes |
| V3 | `_verify_checksum`: False when sidecar missing; True after `_save_checksum`; False after data tamper; False after sidecar tamper | 4-case probe |
| V4 | `_delete_cache_files` removes both files; idempotent (second call no-raise) | Probe |
| V5 | Step 0 (`is_allowed=False`): compute tail runs — **data + sidecar are written anyway** (V5b, INTENTIONAL per D-071/R1); returns `(False, data, None)`; INFO "Cache not allowed by configuration. Forcing computation." | Pipeline probe with pre-existing cache |
| V6 | Step 1 (file missing): compute tail; data + sidecar created; `(False, data, None)` | Pipeline probe |
| V7 | Step 2 (mismatch OR missing sidecar): both files deleted, WARN "Checksum validation failed for '<path>' (sidecar missing or mismatched). Deleting cache and recomputing." (post D-071/M3), recompute + re-store; new files verify True | Pipeline probe |
| V8 | Step 3 (`load_fn` raises, OR data checksum raises, OR `validate_fn` raises — D-071/R2): both deleted, ERROR "Failed to load or validate cache file '<path>': <exception text>. Recomputing." (post D-071), recompute + re-store | Pipeline probe (IOError / RuntimeError / ValueError) |
| V9 | Step 3b (`validate_fn` False): both deleted, WARN "Application data validation failed for '<path>'. Deleting cache and recomputing.", recompute + re-store | Pipeline probe |
| V10 | Success: `(True, data, data_checksum)`; the returned object is the SAME object `load_fn` returned (identity); compute/store not called; INFO "Cache successfully loaded and validated from '<path>'." | Pipeline probe |
| V11 | Duck-typed data checksum: an object with a `compute_sha3_256_hash()` method → its returned value is the 3rd element, on BOTH the compute path and the load path | Pipeline probe with marker digest |
| V12 | `_compute_sha3_256_hash`: non-callable attribute (e.g. int) → `None`, no exception; attribute absent (e.g. dict) → `None` | Direct probe |
| V13 | `compute_sha3_256_hash` raising on the LOAD path is caught by the same try/except as load failure → delete + recompute, ERROR log carries the exception text | Pipeline probe |
| V14 | `logger_fn` is always called with `(Relevance, str)` | Pipeline probe |
| V15 | Sidecar content = bare 64-hex hexdigest, NO trailing newline; a binio `sha3_256sum`-format sidecar (`<hex>  <name>\n`) FAILS `_verify_checksum` (content includes the basename) | Format probe |
| V16 | `validate_fn` raising is now CAUGHT by the step-3 try/except (D-071/R2) → delete + recompute, ERROR log carries the exception text (was: propagated to the caller with the stale cache left in place) | Boundary probe + test |
| V17 | `@validate_call` gate (D-071/R4): `str` `cache_path` is coerced to `Path` (works); `int`/`None` → pydantic `ValidationError` (was: bare `AttributeError`) | Edge probe |

## Issues (R1-R4)

R1, R2, R4 resolved/fixed in the D-071 campaign (2026-08-30,
Roberto's approvals); R3 OPEN, awaiting his ruling.

### R1 — Step 0 still writes the cache — RESOLVED as intentional (D-071)
`is_allowed=False` → the code calls `_compute_and_store`, i.e. it
computes AND stores the result (+ sidecar) even though caching is
"not allowed by configuration" (V5, V5b). Roberto's ruling: "e'
comportamento atteso. Quando la cache e' disabilitata viene forzato
il ricalcolo, ma il risultato e' sempre trascritto nel cache_file" —
a cache-disabled run forces the recompute but the result is ALWAYS
transcribed to the cache file. No behaviour change; documented in the
`is_allowed` docstring line (L150-153) and pinned by
`test_step0_not_allowed_forces_computation` (T4: file rewritten +
valid sidecar).

### R2 — `validate_fn` exceptions now handled like load failures — FIXED (D-071)
Roberto: "risolviamo la asimmetria, mettiamo anche validate nel try,
se validate si interrompe con eccezione, cancellare tutto e
ricompute". `validate_fn(cached_data)` moved INSIDE the step-3
try/except (L187-194): a raising validator now deletes the cache
files and forces recomputation, exactly like a load failure. The
ERROR message was re-worded to "Failed to load or validate cache
file '<path>': <e>. Recomputing." (covers all three callables in the
try; pinned by test_step3a + test_validate_exception_forces_
recomputation + test_load_path_checksum_method_raises_recomputes).
The `validate_fn` returning False (no exception) path is unchanged.

### R3 — Sidecar content format is not binio-compatible — OPEN, awaiting Roberto's ruling
`_save_checksum` writes the bare hexdigest (64 chars, no newline, no
filename); binio's `write_sha3_256_sidecar` writes
`"<hex>  <basename>\n"` (the standard `sha3_256sum` format,
verifiable with `sha3_256sum -c`). The two formats share the SAME
sidecar file name (`<full-name>.SHA3-256`) but differ in CONTENT, and
`_verify_checksum` compares the whole stripped sidecar text against
the bare digest:

- a sidecar produced by binio (hex + two spaces + basename) reads
  back as `"abc123...  cache.dat"` ≠ `"abc123..."` → `_verify_
  checksum` returns False → the cache is treated as CORRUPT and the
  heavy computation is silently redone (V15c);
- conversely, a cache_manager sidecar (bare hex) would be rejected
  by binio's `verify_sha3_256_sidecar` (malformed, no basename).

Inside cache_manager's own flow this never bites — the compute tail
calls `_save_checksum` AFTER `store_fn`, so the sidecar is always
overwritten in the bare format; the first load after a compute
succeeds. The risk is cross-process: any cache file whose sidecar
was written OUTSIDE the pipeline by the binio tooling
(`write_sha3_256_sidecar`, or a plain `sha3_256sum`-style writer) is
rejected by cache_manager → wasted recomputation. Options:
(a) leave as-is + document that cache_manager sidecars are its own
format (and the pipeline always owns its sidecars); (b) make
`_verify_checksum` tolerant — accept the first whitespace-separated
token as the digest (both formats verify; a bare hexdigest is still
accepted since it has no whitespace). Awaiting Roberto's ruling.

### R4 — `@validate_call` added (D-071)
House convention (NOTES.md "Conventions in the code"; state_machine
D-069 M11). Roberto: "aggiungi". `@validate_call(config=
ConfigDict(arbitrary_types_allowed=True))` on
`cache_manager_load_or_compute` (L132); pydantic is now a module
import (already a workspace dependency, pyproject unchanged).
Behaviour change (approved with the fix): a `str` `cache_path` is
coerced to `Path` and works; non-coercible values (`int`, `None`, ...)
raise a pydantic `ValidationError` instead of a bare `AttributeError`
(V17).

## Minor notes (M1-M3) — all fixed (D-071)

- **M1** — Dead import: `Any` removed from the typing import.
- **M2** — Docstring typos fixed: "difefrent value and difefrent
  concept from the cacke file checksum" → "different value and
  different concept from the cache file checksum"; comment "Look up
  for the ..." → "Look for the ...".
- **M3** — The step-2 WARN message is now accurate for both step-2
  cases: "Checksum validation failed for '<path>' (sidecar missing
  or mismatched). Deleting cache and recomputing." (was "Checksum
  mismatch ..." — wrong when the sidecar is merely missing); pinned
  by test_step2 + test_step2_missing_sidecar_forces_recomputation.

## Appendix: line-number reference (2026-08-30, post D-071; file
203 lines)

- `__all__`: L46
- `T` TypeVar: L51 · `ComputeFunc/LoadFunc/StoreFunc/ValidateFunc/
  LoggerFunc`: L54-58
- `SHA3_256_CHECKSUM_SUFFIX`: L61
- `_compute_checksum`: L64 (8 KiB chunk loop: L68-70)
- `_verify_checksum`: L73 (sidecar: L75, exists check: L76, read +
  strip: L79, compare: L82)
- `_save_checksum`: L85 (bare hexdigest write: L89)
- `_delete_cache_files`: L92 (both unlinks `missing_ok=True`: L95-96)
- `_compute_sha3_256_hash`: L99 (getattr: L102, callable gate:
  L105, call: L106, None: L108)
- `_compute_and_store`: L112 (INFO: L118, compute: L119, data
  checksum: L121, store: L124, sidecar: L126, return: L129)
- `cache_manager_load_or_compute`: L133 (D-071 decorator: L132;
  docstring: L141-165, incl. the R1 is_allowed note L150-153;
  Step 0: L167-170; Step 1: L172-175; Step 2: L177-181, M3 message
  L179; Step 3: L183-199 — try L187-194 (load L188, data checksum
  L189, validate L190, R2 comment L184-186), False branch L196-199;
  success: L201-203)
