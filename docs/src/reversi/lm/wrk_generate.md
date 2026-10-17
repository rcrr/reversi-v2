# reversi/lm/wrk_generate.py
The GENERATE worker of the LM pipeline — the 12th active level (step 12), the dense-expansion level: `_up` runs the
uniform 7-kwargs `cache_manager_load_or_compute` flow to materialize the dense weight vector (`ctx.w_dense` +
`ctx.dense_w_checksum`) and `_down` clears both. The 6th cache_manager consumer: the flat file `rlmwf_12_GENERATE.dat`
+ `.SHA3-256` (machine closure `{prefix}{level:02}_{worker_name}.dat`); after OPTIMIZE's config-driven checkpoint name,
GENERATE is the last cache level before VLD_POSITIONS (rlmwf_13).

## API

| name | contract |
|---|---|
| `wrk_generate()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (all worker factories share the pattern) returning `Worker("GENERATE", _up, _down)` |

## Architecture

- `_up`: logs "Generating dense weight vector (w_dense) for inference..." and runs the uniform 7-kwargs
  `cache_manager_load_or_compute`: `cache_path = ctx.get_cache_file_full_path_for_current_level()`,
  `is_allowed = ctx.use_cache`, `load_fn = hlp_generate_load_from_file`, `store_fn = hlp_generate_store_to_file`,
  `validate_fn` = the is_cache_consistent closure, `compute_fn` = the hlp_generate_compute_w_dense closure,
  `logger_fn = ctx.log_event`. Then `ctx.w_dense = dense_obj.w_dense` + the DEBUG shape log, and `ctx.dense_w_checksum` (the
  duck-typed hash the flow returns).
- `_down`: logs "Clearing dense weight vector..." and sets `ctx.w_dense = None` + `ctx.dense_w_checksum = None` — the
  scope pinned by the worker test `test_down_clears_generate_attributes`.
- `wrk_generate()`: the factory, `@validate_call`-decorated.

## Verified invariants

Pinned by the `probes/verify_generate.py` B + E + F tiers + the 3-test suite.

- Worker source shape (probe B1-B3): the `_for_current_level` name (no `_for_next_level` anywhere), the factory
  decorator + pydantic import, no trailing ws.
- The pre-declared blackboard fields (probe F1): `w_dense: Any = None` + `dense_w_checksum: str | None = None` in
  LMContext — no context change needed.
- The live rlm_02 flow (probe E tier + the worker suite): the full pipeline to GENERATE writes `rlmwf_12_GENERATE.dat` +
  `.SHA3-256` (the sidecar verifies); `ctx.w_dense` is (6588,) float32; `ctx.dense_w_checksum` == the hash golden
  `ec9d65453bb112bf277c79f96a86edfa9468bb01f42a2763cd82d69c5b2b15b4`; the second instance on the same base dir gets the
  cache hit ("Cache successfully loaded and validated", no recompute, `w_dense` array-equal); `move_to_step(11)` back to
  OPTIMIZE clears BOTH fields.

## Open issues

None.

## Conventions

- The flat-file numbering takes rlmwf_12 (informational): the next cache level (VLD_POSITIONS) takes rlmwf_13 — unlike
  OPTIMIZE's config-named checkpoint.
- The triple blank lines after the imports are the canonical pattern of all worker files (house style).

## Integration

- The 12th LM level; the last cache-consuming level before VLD_POSITIONS (the rlmwf_12 slot). Consumes the OPTIMIZE
  `ctx.w` + `ctx.w_checksum` + the WMAPS / FEATURES blackboard (via hlp_generate_compute_w_dense); produces `ctx.w_dense` +
  `ctx.dense_w_checksum` — the inputs of the VALIDATE and ANALYTICS levels.
- The worker-test setUp moves through OPTIMIZE (step 11) first, so the full 12-level chain is exercised end-to-end on
  the live DB before GENERATE — that is why all 3 tests are DB-gated.
