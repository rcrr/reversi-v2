# twolm/rlm_generate.py
The GENERATE domain module of the RLM pipeline — the 11th active
level (CREATED sentinel → CONFIG → POSITIONS → FEATURES →
INDEXES → WMAPS → DESIGN_MTR → ZED → GRADIENT → OPTIMIZE →
GENERATE) and the 5th cache_manager consumer. It expands the
OPTIMIZE compressed weights into the DENSE weight vector used
for inference: `w_dense` ((K,) float32 over ALL theoretical
configurations of the feature set) + `w_checksum` (the OPTIMIZE
compressed-w checksum — the consistency anchor). The flat file
is `rlmwf_10_GENERATE.dat` + `.SHA3-256` (machine closure
`{prefix}{level:02}_{worker_name}.dat`).
> State: D-098 · 9d2ae80 · 2026-09-02 · suite 14/0/0

## API

| name | contract |
|---|---|
| `ReversiLogisticModelDenseWeights` | the data object — `__init__(w_checksum: str, w_dense: NDArray)` both `@validate_call` (the NDArray gate rejects lists) |
| `.compute_sha3_256_hash()` | `@validate_call` — `sha3_256(w_dense.tobytes())` ONLY (the duck-typed data-checksum hook, same shape as the 4 siblings) |
| `rlm_generate_store_to_file(dw, filename)` | `@validate_call` — header "RGLM Dense Weights binary data file" v1 + checksum string + array; NO sidecar (cache_manager writes it, D-072) |
| `rlm_generate_load_from_file(filename, checksum=True)` | `@validate_call` — sidecar verify → 2 header gates (description + the D-098 T1 version gate) → the object |
| `rlm_generate_is_cache_consistent(ctx, dw)` | the single-field gate `dw.w_checksum == ctx.w_checksum` (NO `@validate_call` — the L99 note) |
| `compute_w_dense(ctx)` | `@validate_call`-free (the L104 note) — the compressed → dense expansion over the 3 feature categories |

## Architecture

- `ReversiLogisticModelDenseWeights` (L53-65): plain class, 2
  fields.
- `rlm_generate_store_to_file` (L68-75) /
  `rlm_generate_load_from_file` (L78-96): the standard binio
  round-trip; the load gates in order: the R3-class sidecar
  verify (L80-82, "Checksum mismatch."), the description gate
  (L89-90), the D-098 T1 version gate (L84, L91-92, "File
  version mismatch: found 2, expected 1") — all BEFORE any
  payload parse.
- `rlm_generate_is_cache_consistent` (L99-101, the L98
  no-validation note — `RLMContext` is a TYPE_CHECKING import):
  the single-field gate on `w_checksum` — when the OPTIMIZE
  weights change, the dense expansion must be recomputed.
- `compute_w_dense` (L104-225): per feature, the slice
  `[iwmap_feature_offset[fid] : offset[fid+1]]` of
  `w_dense = zeros(K)` (K = `offset[-1]`), with the 3 category
  branches:
  - Intercept (L137-139): broadcast the single weight
    (`w[w_min : w_max+1][0]`) over the whole slice.
  - Mobility (L141-164): `np.interp` over `arange(n_configurations)`
    with the seen configs (wmap `config_id >= 0` rows) —
    internal missing values interpolated, external clamped (the
    L156-158 note: the ascending precondition is structural,
    hlp_wmaps allocates via `np.unique`); zero seen configs →
    zeros + exactly one `Relevance.WARN` (L163-164).
  - Pattern (L166-220): every config maps to its Principal
    Index (`ref.convert_to_principal_index`, the uint32 cast at
    L202 is mandatory for the pydantic reference model); a
    computed principal (w-index ≥ 0 AND ≠ fallback, L215)
    propagates its trained weight to all symmetric configs
    (L218); everything else — unseen AND fallback configs —
    inherits the frequency-weighted mean of the seen configs
    (L177-178, L212). The fallback weight is logged for
    transparency only, never used (L184-197, Roberto's D-098 R2
    ruling).
  - Unknown category → `RuntimeError("The feature category is
    unknown: {category}")` (L222-223, the D-098 M3 wording).

## Verified invariants

Pinned by the 15-check `probes/verify_generate.py` + the
17-test pair (14 no-DB + 3 DB-gated — see the test docs).

- Module source shape (probe A1-A5): the 5-name `__all__`, the 2
  no-validation notes, the version gate, no trailing ws.
- The data-object behavior (probe D3 + D11): the duck-typed hash
  == independent `sha3_256(w_dense.tobytes())`; the
  hand-re-derived mock golden (INT 0.5; PAT weighted mean
  −0.2; MOB interp/clamp [1, 1, 2, 3, 3]).
- The live rlm_02 re-derivation (probe E2/E4/E5/E7): K = 6588
  (= 1 + 6561 + 27), orbit invariance + seen-config exactness
  on both patterns, the full independent re-derivation ==
  `ctx.w_dense`, the hash golden
  `ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15
  b4`.
- The R2 inference semantics (the L188-197 ruling comment):
  unseen + fallback configs take the weighted mean, NOT the
  trained fallback weight — pinned by the mock golden (unseen →
  −0.2) and by the live E4 exactness check.
- The uint32 pattern-config cast (L202): `np.arange(...,
  dtype=np.uint32)` is mandatory —
  `convert_to_principal_index` takes a pydantic-validated uint32
  array (the live re-derivation exercises it).
- The blackboard fields `w_dense: Any = None` +
  `dense_w_checksum: str | None = None` were pre-declared in
  RLMContext at first import (probe F1 — the D-094 fg pattern).

## Open issues

None.

## Conventions

- The sidecar is written by cache_manager (D-072), not by the
  store function — same as the 4 sibling data modules.
- The consistency gate is a single field (the OPTIMIZE
  `w_checksum`): a dense recomputation is only needed when the
  optimized compressed weights change.
- The np.interp ascending precondition is structural (hlp_wmaps
  `np.unique` slot allocation), not an assumption — the L156-158
  note.

## Integration

- The worker (lm_worker_generate.py) calls all 5 names through
  the uniform 7-kwargs `cache_manager_load_or_compute` (config
  via `ctx.get_cache_file_full_path_for_current_level()`,
  `is_allowed = ctx.use_cache`, store/load/validate/compute
  closures, `logger_fn = ctx.log_event`).
- Consumes the OPTIMIZE `ctx.w` + `ctx.w_checksum` + the WMAPS /
  FEATURES blackboard (features, iwmap, iwmap_feature_offset,
  wmap, feature_w_ranges); produces `ctx.w_dense` +
  `ctx.dense_w_checksum` — the inputs of the future
  VALIDATE/ANALYTICS levels.
