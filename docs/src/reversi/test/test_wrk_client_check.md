# reversi/test/test_wrk_client_check.py
The no-DB suite of the CLIENT_CHECK worker (the 16th level,
D-148): it exercises the worker DIRECTLY on a synthetic
rlm_04-mirror context (the same layout and the same production
iwmap pin as test_client.py) — the model file is written with the
REAL `model_weights_write_file` (the v2 LZ4 artifact + sidecar),
then `wrk_client_check().up(ctx)` runs the full level: file
re-read → client's array EF → residual comparison. No DB, no
pipeline: the `Worker.up` @validate_call gate (context: Context)
requires a REAL `LMContext`; the `cfg` attribute is the
SimpleNamespace stand-in (the D-144 v2 micro-test idiom) and
`log_event` a capturing lambda.
> State: D-148 · 4244a93 · 2026-09-10 · suite 6/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestWrkClientCheck` (ungated — no DB, no pipeline; setUp: `mkdtemp` under `CUSTOM_TMP_BASE`, the seeded synthetic ctx — SEED 42, 2000 collision-free positions, int8 game values in steps of 2, logit clipping 0.01, the rlm_04 feature layout + iwmap [0,1,66,6627]) | 6 | `test_factory_returns_named_worker`: the `@validate_call` factory returns `Worker("CLIENT_CHECK", …)` (the uniform worker-factory idiom). `test_up_passes_on_unmodified_file`: THE D-148 BIT-IDENTITY GOLDEN — after the real SAVE write, the level passes and the captured log contains "Client check passed: 2000 validation residuals, max difference 0.000e+00 (tolerance 1.0e-08)." (the f64-view residuals from the file round-trip + the array EF equal the in-memory VALIDATE forward pass's exactly). `test_up_missing_file_raises`: no SAVE artifact → the read's `FileNotFoundError` propagates (the D-060 failure semantics). `test_up_diverged_weights_raise`: the in-memory `w_dense` diverges from the file after the save (the corruption / drift case, max difference ~0.2) → `RuntimeError` with the full diagnosis message ("…by 1.959e-01 (first at position 1355), above the tolerance 1.0e-08. The model file, the client, or the validation forward pass has diverged.") + exactly one ERROR log line. `test_tolerance_is_read_from_config`: Roberto's ruling — the tolerance is the `cfg.client_check_tol` field (the JSON config value, not a module constant): the same divergence is ADMITTED by a wide tolerance (1.0) and REJECTED by a tight one (1e-4). `test_down_is_a_noop_log`: the stateless `_down` (as SAVE) logs only. |

## Goldens pinned

- The pass-line literal: "Client check passed: 2000 validation
  residuals, max difference 0.000e+00 (tolerance 1.0e-08)." — the
  `0.000e+00` is the bit-identity claim (a 1-ulp drift breaks the
  assertIn); the DB-gated A2030 chain pins the same line at full
  scale (20000 residuals, test_lm_worker_full_chain), the A2050
  VLONG chain exercises the 199932-residual form.
- The divergence magnitude (~1.959e-01 at the seeded 1e-3 weight
  perturbation) is pinned by regex (magnitude-agnostic:
  `[\d.]+e-\d+`), so the test survives a re-seed of the synthetic
  weights.
- The `iwmap` pin [0, 1, 66, 6627] (the production rlm_04 layout,
  as in test_client.py) — the synthetic context IS the rlm_04
  shape.

## Conventions

- The D-065/D-085 idiom: files ONLY under `build/tmp`
  (`CUSTOM_TMP_BASE`), removed in `tearDown` (the `mkdtemp`
  + `shutil.rmtree` pattern).
- The real `model_weights_write_file` (not a hand-crafted body, as
  in the `TestModelWeightsV2` micro tier): the point of the suite
  is the LEVEL on the SHIPPED artifact format.
- `Worker.up` is `@validate_call`-gated with `context: Context`
  (state_machine L87-90): a SimpleNamespace context is rejected by
  the gate — hence the real `LMContext` (the wrk_validate M1
  idiom); only the `cfg` attribute may be a stand-in (the dataclass
  declares it `Any`).

## Integration

- The DB-gated complement: `test_lm_worker_full_chain` (the
  A2030/A2050 chains run the level end-to-end; the A2030 log pin)
  + `probes/verify_logistic_model.py` V3c (the 16-level pipeline
  shape, the CLIENT_CHECK last).
- The level under test: `reversi/lm/wrk_client_check.py`
  (wrk_client_check.md); the client factories: `reversi/lm/
  client.py` (client.md); the v2 file format: `reversi/lm/
  model_weights.py` (model_weights.md).
