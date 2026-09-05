<!-- ARCHIVED — D-106 step 23 (the docs/ rewrite, 2026-09-04): the CACHE_MANAGER family (this doc + the test doc) moved out of docs/src/twolm/ into the snapshot schema per docs_rules.md §1/§4. This is a frozen historical record: it is never updated. Stale-in-current-context notes: (1) the "33-check probe + 2 boundary probes" figure — the current probes/verify_cache_manager.py (the 4091e72 move) has 6 surviving check() calls: V2 ×3 (the sidecar-naming loop), V9c (the step-3b WARN), V10b (the success identity), V16 (the logger arg shape). The D-106 step-3 deletions (all class c → test_cache_manager): V1 (the file checksum moved to binio at D-072), V3a-d → TestVerifyChecksum, V4 → TestDeleteCacheFiles, V5a-d/V6 → the step-0/step-1 tests, V7a-c → the step-2 tests, V8a-c → the step-3a test, V9a-b → the validation-failed test, V10a/c → the step-4 test, V11-V13 → the duck-typed checksum tests; V17 was the class-a §4 conversion → TestValidateCallCoercion (the test file is now 627 lines / 22 tests — the class map appendix below is the PRE-step-3 603-line state). (2) the "468 tests / 52 skipped" full-discover figure predates the D-106 steps (current: 664/87 gated). (3) the R1-R4 + M1-M3 campaign narrative is frozen history. -->

# cache_manager.py — analysis

Date: 2026-08-30. Module added by Roberto (2 files: cache_manager.py +
test_cache_manager.py, commit a0cd31f). **Analysis session 20; fix
campaign batch 1 applied (D-071): R1 resolved as intentional
(documented + pinned), R2 fixed (validate in the try), R4 fixed
(@validate_call), M1-M3 fixed, T1/T2/T3/T4/T5/T7 pinned + 8 new
tests — suite 13 → 21. Batch 2 applied (D-072): R3 RESOLVED (binio
sidecar API adopted: `import hashlib` and the two re-implemented
helpers deleted, thin `_verify_checksum` wrapper over
`verify_sha3_256_sidecar`, sidecar now in binio's sha3_256sum
format, legacy bare-hex sidecars still verify), T6 fixed (artifact
base anchored to the workspace root), T3 pin restated, R3 +
legacy-compat + malformed/undecodable pins added, 2
direct-compute helper tests dropped — suite 21 → 21. All OPEN items
closed; T8 report-only. Module CLOSED.**

Suite: **21 tests, GREEN 21/0/0** (no PERF gates). Suite is fast
(~0.15s).

Full workspace: **468 tests, GREEN, 52 skipped under the gate**
(17 PERF + 35 regab DB-gated; without `SKIP_REGAB_DB=1` the DB tests
run against live PostgreSQL and only 17 skip).

## Architecture

`cache_manager` is a small, domain-agnostic caching utility: one
public function orchestrates a 4-step validation pipeline for
"load cached result or recompute" around injected business-logic
callbacks. It is the first domain module to import
`twolm.state_machine` (`Relevance` for the injected logger) and
`twolm.binio` (the checksum sidecar API, D-072 — no import cycle:
binio imports no twolm module; no new pyproject dependency). The
public function carries the house `@validate_call` gate (D-071/R4):
`cache_path` is coerced `str` → `Path`, non-coercible values raise
`ValidationError`.

### Components

| Component | Role |
|---|---|
| `cache_manager_load_or_compute(...)` | The only public API. 4-step pipeline (below). Returns `(cache_hit: bool, data: T, data_checksum: str \| None)`. |
| `_verify_checksum(path)` | Step 2: thin wrapper over binio's `verify_sha3_256_sidecar` (D-072); maps `FileNotFoundError` / `BinaryFormatError` / `UnicodeDecodeError` → `False` (a bad sidecar invalidates, never crashes). |
| `_delete_cache_files(path)` | Unlinks data + sidecar, both `missing_ok=True` (idempotent). |
| binio sidecar API (imported, D-072) | `compute_sha3_256`, `write_sha3_256_sidecar`, `verify_sha3_256_sidecar`, `BinaryFormatError` — own file hashing + sidecar I/O; replace the deleted `_compute_checksum` / `_save_checksum`. |
| `_compute_sha3_256_hash(data)` | Duck typing: if the data object has a callable `compute_sha3_256_hash` attribute, call it and return the result, else `None`. |
| `_compute_and_store(...)` | The shared "compute" tail: INFO log, `compute_fn()`, data checksum, `store_fn(data, path)`, binio `write_sha3_256_sidecar`, INFO logs; returns `(False, data, data_checksum)`. |
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
  disk. binio's `sha3_256sum` format `<hex>  <basename>\n` (V15,
  restated in D-072); pre-D-072 legacy bare-hexdigest sidecars still
  verify (binio's first-token parser).
- **Data checksum** (3rd return element): content hash of the business
  data object, obtained duck-typing `data.compute_sha3_256_hash()`.
  `None` when the object has no such callable. Intended for the
  caller to record (e.g. in the DB) which content was loaded/computed.
  Different value AND different concept from the file checksum (per
  the docstring, L136 — typos in original, M2).

### Integration notes

- `logger_fn` takes `(Relevance, str)` — the natural binding is the
  `log_event` method that `StateMachine.__init__` injects into the
  shared `Context` (V17 context-injection, M9 left as-is per D-070).
- The `.dat` cache files this module validates match the naming
  produced by the state_machine `Context` cache helpers
  (`{prefix}{level:02}_{name}.dat`, D-069 M5/M8): this module is the
  load-or-compute engine for exactly those files.
- Sidecar naming AND content format are now exactly binio's
  (D-072/R3): `write_sha3_256_sidecar` writes, the
  `verify_sha3_256_sidecar`-backed wrapper verifies. Cross-process
  sidecars written by binio tooling (or a plain `sha3_256sum`-style
  writer) now verify (V15c flipped); legacy bare-hex sidecars keep
  verifying (zero cache invalidation).

## Verified facts (V1-V17)

Independently re-derived (scratch/verify_cache_manager.py, 33 checks
+ 2 boundary probes), zero mismatches.

| # | Fact | Method |
|---|---|---|
| V1 | File hashing is binio's `compute_sha3_256` (1 MiB chunks, SHA3-256): 64-char lowercase hex, deterministic. The old re-implemented `_compute_checksum` (8 KiB chunks) was proven identical by the D-071 probe and is deleted in D-072 | Direct compare + charset check (D-071 probe) |
| V2 | Sidecar name = `<full-original-name>.SHA3-256` (`with_suffix` re-applies the original suffix: `data.dat` → `data.dat.SHA3-256`, `a.b.dat` → `a.b.dat.SHA3-256`, extension-less `data` → `data.SHA3-256`) — same naming scheme as binio | Path probes |
| V3 | `_verify_checksum` (wrapper, D-072): False when sidecar missing (FileNotFoundError → False); True after binio `write_sha3_256_sidecar`; False after data tamper (digest mismatch); False on a malformed sidecar (BinaryFormatError → False) and on an undecodable one (UnicodeDecodeError → False) | 4-case probe + 2 wrapper probes |
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
| V15 | Sidecar content = binio's `sha3_256sum` line `<hex>  <name>\n` (D-072, restated); a binio-written sidecar now VERIFIES (V15c flipped — pre-D-072 it failed); a legacy bare-hexdigest sidecar still verifies (first-token parser) | Format probe + 2 D-072 pins |
| V16 | `validate_fn` raising is now CAUGHT by the step-3 try/except (D-071/R2) → delete + recompute, ERROR log carries the exception text (was: propagated to the caller with the stale cache left in place) | Boundary probe + test |
| V17 | `@validate_call` gate (D-071/R4): `str` `cache_path` is coerced to `Path` (works); `int`/`None` → pydantic `ValidationError` (was: bare `AttributeError`) | Edge probe |

## Issues (R1-R4)

R1, R2, R4 resolved/fixed in the D-071 campaign (2026-08-30,
Roberto's approvals); R3 RESOLVED in the D-072 campaign (batch 2,
2026-08-30, Roberto's approval of the binio-import proposal). All
issues closed.

### R1 — Step 0 still writes the cache — RESOLVED as intentional (D-071)
`is_allowed=False` → the code calls `_compute_and_store`, i.e. it
computes AND stores the result (+ sidecar) even though caching is
"not allowed by configuration" (V5, V5b). Roberto's ruling: "e'
comportamento atteso. Quando la cache e' disabilitata viene forzato
il ricalcolo, ma il risultato e' sempre trascritto nel cache_file" —
a cache-disabled run forces the recompute but the result is ALWAYS
transcribed to the cache file. No behaviour change; documented in the
`is_allowed` docstring line (L141-144) and pinned by
`test_step0_not_allowed_forces_computation` (T4: file rewritten +
valid sidecar).

### R2 — `validate_fn` exceptions now handled like load failures — FIXED (D-071)
Roberto: "risolviamo la asimmetria, mettiamo anche validate nel try,
se validate si interrompe con eccezione, cancellare tutto e
ricompute". `validate_fn(cached_data)` moved INSIDE the step-3
try/except (L178-185): a raising validator now deletes the cache
files and forces recomputation, exactly like a load failure. The
ERROR message was re-worded to "Failed to load or validate cache
file '<path>': <e>. Recomputing." (covers all three callables in the
try; pinned by test_step3a + test_validate_exception_forces_
recomputation + test_load_path_checksum_method_raises_recomputes).
The `validate_fn` returning False (no exception) path is unchanged.

### R3 — Sidecar content format is not binio-compatible — RESOLVED (D-072)
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
rejected by cache_manager → wasted recomputation. Roberto's ruling:
"ho capito che NON va bene" — with his proposal: import binio into
cache_manager and use the native binio API instead of
re-implementing the three helpers. Applied in D-072 (superseding
option (b)): `import hashlib` deleted, `_compute_checksum` and
`_save_checksum` deleted (binio's `compute_sha3_256` /
`write_sha3_256_sidecar` own the job); `_verify_checksum` is now a
5-line wrapper over `verify_sha3_256_sidecar` mapping
(FileNotFoundError, BinaryFormatError, UnicodeDecodeError) → False
(a corrupt sidecar invalidates, never crashes);
`_compute_and_store` writes the sidecar via
`write_sha3_256_sidecar`. Bonus of binio's first-token parser:
legacy bare-hex sidecars keep verifying (zero cache invalidation)
AND binio-format sidecars now pass (V15c flips). Pinned:
`test_binio_sidecar_verifies` (R3), `test_legacy_bare_hex_sidecar_
still_verifies` (compat), `test_verify_checksum_fails_if_sidecar_
malformed` (exception mapping), `test_sidecar_content_is_binio_
format` (T3 restated). Trade-off recorded: cache_manager now
imports twolm.binio (same package; no import cycle — binio imports
no twolm module; no new pyproject dependency).

### R4 — `@validate_call` added (D-071)
House convention (NOTES.md "Conventions in the code"; state_machine
D-069 M11). Roberto: "aggiungi". `@validate_call(config=
ConfigDict(arbitrary_types_allowed=True))` on
`cache_manager_load_or_compute` (L124); pydantic is now a module
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

## Appendix: line-number reference (2026-08-30, post D-072; file
194 lines)

- `__all__`: L50
- `T` TypeVar: L55 · `ComputeFunc/LoadFunc/StoreFunc/ValidateFunc/
  LoggerFunc`: L58-62
- `SHA3_256_CHECKSUM_SUFFIX`: L65
- binio import (D-072): L41-45 · state_machine import: L46
- `_verify_checksum`: L68 (binio call: L78, exception mapping:
  L79-80)
- `_delete_cache_files`: L83 (both unlinks `missing_ok=True`:
  L86-87)
- `_compute_sha3_256_hash`: L90 (getattr: L93, callable gate:
  L96, call: L97, None: L99)
- `_compute_and_store`: L103 (INFO: L109, compute: L110, data
  checksum: L112, store: L115, binio sidecar: L117, return: L120)
- `cache_manager_load_or_compute`: L124 (D-071 decorator: L123;
  docstring: L132-156, incl. the R1 is_allowed note L141-144;
  Step 0: L158-161; Step 1: L163-166; Step 2: L168-172, M3 message
  L170; Step 3: L174-185 — try L178-185 (load L179, data checksum
  L180, validate L181, R2 comment L175-177), False branch L187-190;
  success: L192-194)
