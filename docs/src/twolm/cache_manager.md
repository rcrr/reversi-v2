# cache_manager.py — analysis

Date: 2026-08-30. Module added by Roberto (2 files: cache_manager.py +
test_cache_manager.py, commit a0cd31f). **Analysis session 20 — no
source changes yet; R1-R4 + T1-T8 + M1-M3 documented, fix campaign
pending Roberto's approvals.**

Suite: **13 tests, GREEN 13/0/0** (no PERF gates). Suite is fast
(~0.025s).

Full workspace: **460 tests, GREEN, 52 skipped under the gate**
(17 PERF + 35 regab DB-gated; without `SKIP_REGAB_DB=1` the DB tests
run against live PostgreSQL and only 17 skip).

## Architecture

`cache_manager` is a small, domain-agnostic caching utility: one
public function orchestrates a 4-step validation pipeline for
"load cached result or recompute" around injected business-logic
callbacks. It is the first domain module to import
`twolm.state_machine` (`Relevance` for the injected logger).

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

1. **Step 0 — allowed?** `is_allowed` false → compute tail. Note: the
   compute tail **also stores** (V5b) — flagged as R1.
2. **Step 1 — present?** data file missing → compute tail.
3. **Step 2 — consistent?** sidecar missing or mismatching → WARN,
   delete both files, compute tail.
4. **Step 3 — valid?** `load_fn(path)` + the duck-typed data checksum
   are wrapped in ONE try/except: any exception (load failure OR data
   checksum failure) → ERROR, delete both, compute tail. Then
   `validate_fn(data)` (NOT in the try — R2) false → WARN, delete
   both, compute tail.
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
| V5 | Step 0 (`is_allowed=False`): compute tail runs — **data + sidecar are written anyway** (V5b); returns `(False, data, None)`; INFO "Cache not allowed by configuration. Forcing computation." | Pipeline probe with pre-existing cache |
| V6 | Step 1 (file missing): compute tail; data + sidecar created; `(False, data, None)` | Pipeline probe |
| V7 | Step 2 (mismatch OR missing sidecar): both files deleted, WARN "Checksum mismatch for '<path>'. Deleting cache and recomputing.", recompute + re-store; new files verify True | Pipeline probe |
| V8 | Step 3a (`load_fn` raises): both deleted, ERROR "Failed to load cache file '<path>': <exception text>. Recomputing.", recompute + re-store | Pipeline probe (IOError) |
| V9 | Step 3b (`validate_fn` False): both deleted, WARN "Application data validation failed for '<path>'. Deleting cache and recomputing.", recompute + re-store | Pipeline probe |
| V10 | Success: `(True, data, data_checksum)`; the returned object is the SAME object `load_fn` returned (identity); compute/store not called; INFO "Cache successfully loaded and validated from '<path>'." | Pipeline probe |
| V11 | Duck-typed data checksum: an object with a `compute_sha3_256_hash()` method → its returned value is the 3rd element, on BOTH the compute path and the load path | Pipeline probe with marker digest |
| V12 | `_compute_sha3_256_hash`: non-callable attribute (e.g. int) → `None`, no exception; attribute absent (e.g. dict) → `None` | Direct probe |
| V13 | `compute_sha3_256_hash` raising on the LOAD path is caught by the same try/except as load failure → delete + recompute, ERROR log carries the exception text | Pipeline probe |
| V14 | `logger_fn` is always called with `(Relevance, str)` | Pipeline probe |
| V15 | Sidecar content = bare 64-hex hexdigest, NO trailing newline; a binio `sha3_256sum`-format sidecar (`<hex>  <name>\n`) FAILS `_verify_checksum` (content includes the basename) | Format probe |
| V16 | `validate_fn` raising propagates to the caller (NOT caught — it is outside the step-3 try); cache files left in place | Boundary probe |
| V17 | No `@validate_call`: `cache_path` as `str` → `AttributeError` (from `with_suffix` on the step-0 path); no pydantic coercion | Edge probe |

## Issues (R1-R4) — OPEN, Roberto's calls

### R1 — Step 0 still writes the cache (P0 question)
`is_allowed=False` → the code calls `_compute_and_store`, i.e. it
computes AND stores the result (+ sidecar) even though caching is
"not allowed by configuration" (V5, V5b). The log message says
"Forcing computation" — but the store is not optional. Two readings:
(a) intentional — "not allowed to LOAD" (e.g. first run / config
toggle), warm the cache opportunistically; (b) unintended — a
cache-disabled run should not create cache files (disk side effect +
the next run with caching enabled would trust it). Needs Roberto's
ruling; whichever way, the current behaviour must then be pinned
(test T4) or changed (source).

### R2 — `validate_fn` exceptions propagate, load failures do not
Only `load_fn` + the data-checksum call are in the try/except
(L178-184). A `validate_fn` that raises (a bug in the business
validator) propagates to the caller with the stale cache files left
in place (V16). Defensible as "a broken validator should crash loudly
instead of silently recomputing into an infinite loop", but it is an
asymmetry worth documenting (or, if undesired, catching + invalidating
like the load path). Roberto's call: document + pin, or catch.

### R3 — Sidecar content format is not binio-compatible
`_save_checksum` writes the bare hexdigest; binio's
`write_sha3_256_sidecar` writes `"<hex>  <basename>\n"` (the
`sha3_256sum -c` format). A cache file whose sidecar was produced by
binio (or by the manual `write_sha3_256_sidecar` helper) is rejected
by `_verify_checksum` (V15c) → silent recompute. Inside the
pipeline's own flow this never bites (the compute tail overwrites the
sidecar with the bare format after `store_fn`), but cross-module
interop does. Options: (a) leave as-is + document (cache_manager
sidecars are its own format); (b) make `_verify_checksum` tolerant —
parse the first whitespace-separated token. Roberto's call.

### R4 — No `@validate_call` on the public function (house convention)
House convention (NOTES.md "Conventions in the code"; state_machine
D-069 M11) puts `@validate_call` on public functions. Here the lone
public function is bare, so `str`/`None` `cache_path` surface as
`AttributeError` (V17) instead of a `ValidationError`. Note: adding
the decorator would make pydantic coerce `str` → `Path` (str paths
would start WORKING), which is a behaviour change, not just hygiene.
Low priority; Roberto's call.

## Minor notes (M1-M3)

- **M1** — Dead import: `Any` (L38) is never used in the module.
- **M2** — Docstring typos (L142): "difefrent value and difefrent
  concept from the cacke file checksum" → "different ... the cache
  file checksum". Also L98 comment: "Look up for the ..." → "Look for
  the ..." (grammar).
- **M3** — The step-2 WARN message reads "Checksum mismatch" also
  when the sidecar is simply MISSING (the step-2 branch covers both
  cases, V7). Informational-only precision.
