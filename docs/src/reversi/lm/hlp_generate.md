# reversi/lm/hlp_generate.py
The GENERATE domain module of the LM pipeline — the 11th active level (CREATED sentinel → CONFIG → FEATURES → POSITIONS
→ INDEXES → WMAPS → DESIGN_MTR → ZED → GRADIENT → OPTIMIZE → GENERATE) and the 5th cache_manager consumer. It expands
the OPTIMIZE compressed weights into the DENSE weight vector used for inference: `w_dense` ((K,) float32 over ALL
theoretical configurations of the feature set) + `w_checksum` (the OPTIMIZE compressed-w checksum — the consistency
anchor). The flat file is `rlmwf_12_GENERATE.dat` + `.SHA3-256` (machine closure
`{prefix}{level:02}_{worker_name}.dat`).

## API

| name | contract |
|---|---|
| `LMDenseWeights` | the data object — `__init__(w_checksum: str, w_dense: NDArray)` both `@validate_call` (the NDArray gate rejects lists) |
| `.compute_sha3_256_hash()` | `@validate_call` — `sha3_256(w_dense.tobytes())` ONLY (the duck-typed data-checksum hook, same shape as the 4 siblings) |
| `hlp_generate_store_to_file(dw, filename, compressed=True)` | `@validate_call` — header "RGLM Dense Weights binary data file" v1 + checksum string + array; LZ4 whole-file frame by default; the sidecar is written by the binio writer |
| `hlp_generate_load_from_file(filename, checksum=True, compressed=True)` | `@validate_call` — sidecar verify → 2 header gates (description + the version gate) → the object |
| `hlp_generate_is_cache_consistent(ctx, dw)` | the single-field gate `dw.w_checksum == ctx.w_checksum` (NO `@validate_call` — the note) |
| `compute_w_dense(ctx)` | `@validate_call`-free (the note) — the compressed → dense expansion over the 3 feature categories |

## Architecture

- `LMDenseWeights`: plain class, 2 fields.
- `hlp_generate_store_to_file` / `hlp_generate_load_from_file`: the standard binio round-trip — the writer/reader run
  with `compressed=True` by default, the LZ4 whole-file frame, and the sidecar is written by the binio writer
  (cache_manager re-writes it idempotently in the pipeline flow); the load gates in order: the R3-class sidecar verify
  ("Checksum mismatch."), the description gate, the version gate ("File version mismatch: found 2, expected 1") — all
  BEFORE any payload parse.
- `hlp_generate_is_cache_consistent` (the no-validation note — `LMContext` is a TYPE_CHECKING import): the single-field
  gate on `w_checksum` — when the OPTIMIZE weights change, the dense expansion must be recomputed.
- `compute_w_dense`: per feature, the slice `[iwmap_feature_offset[fid] : offset[fid+1]]` of `w_dense = zeros(K)` (K =
  `offset[-1]`), with the 3 category branches:
  - Intercept: broadcast the single weight (`w[w_min : w_max+1][0]`) over the whole slice.
  - Mobility: `np.interp` over `arange(n_configurations)` with the seen configs (wmap `config_id >= 0` rows) — internal
    missing values interpolated, external clamped (the note: the ascending precondition is structural, hlp_wmaps
    allocates via `np.unique`); zero seen configs → zeros + exactly one `Relevance.WARN`.
  - Pattern: every config maps to its Principal Index (`ref.convert_to_principal_index`, the uint32 cast is mandatory
    for the pydantic reference model); a computed principal (w-index ≥ 0 AND ≠ fallback) propagates its trained weight
    to all symmetric configs; everything else — unseen AND fallback configs — inherits the frequency-weighted mean of
    the seen configs. The fallback weight is logged for transparency only, never used (the ruling comment).
  - Unknown category → `RuntimeError("The feature category is unknown: {category}")`.

## Verified invariants

Pinned by the 15-check `probes/verify_generate.py` + the 19-test pair (16 no-DB + 3 DB-gated — see the test docs).

- Module source shape (probe A1-A5): the 5-name `__all__`, the 2 no-validation notes, the version gate, no trailing ws.
- The data-object behavior (probe D3 + D11): the duck-typed hash == independent `sha3_256(w_dense.tobytes())`; the
  hand-re-derived mock golden (INT 0.5; PAT weighted mean −0.2; MOB interp/clamp [1, 1, 2, 3, 3]).
- The live rlm_02 re-derivation (probe E2/E4/E5/E7): K = 6588 (= 1 + 6561 + 27), orbit invariance + seen-config
  exactness on both patterns, the full independent re-derivation == `ctx.w_dense`, the hash golden
  `ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15 b4`.
- The R2 inference semantics (the ruling comment): unseen + fallback configs take the weighted mean, NOT the trained
  fallback weight — pinned by the mock golden (unseen → −0.2) and by the live E4 exactness check.
- The uint32 pattern-config cast: `np.arange(..., dtype=np.uint32)` is mandatory — `convert_to_principal_index` takes a
  pydantic-validated uint32 array (the live re-derivation exercises it).
- The blackboard fields `w_dense: Any = None` + `dense_w_checksum: str | None = None` were pre-declared in LMContext at
  first import (probe F1 — the fg pattern).

## Open issues

None.

## Conventions

- The sidecar story: the binio writer writes the `.SHA3-256` over the compressed bytes (the checksum service is on by
  default); in the pipeline flow cache_manager re-writes the same sidecar (idempotent) — as in the 4 sibling data
  modules.
- The consistency gate is a single field (the OPTIMIZE `w_checksum`): a dense recomputation is only needed when the
  optimized compressed weights change.
- The np.interp ascending precondition is structural (hlp_wmaps `np.unique` slot allocation), not an assumption — the
  code comment states it.

## Integration

- The worker (wrk_generate.py) calls all 5 names through the uniform 7-kwargs `cache_manager_load_or_compute` (config
  via `ctx.get_cache_file_full_path_for_current_level()`, `is_allowed = ctx.use_cache`, store/load/validate/compute
  closures, `logger_fn = ctx.log_event`).
- Consumes the OPTIMIZE `ctx.w` + `ctx.w_checksum` + the WMAPS / FEATURES blackboard (features, iwmap,
  iwmap_feature_offset, wmap, feature_w_ranges); produces `ctx.w_dense` + `ctx.dense_w_checksum` — the inputs of the
  future VALIDATE/ANALYTICS levels.
