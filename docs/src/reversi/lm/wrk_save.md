# reversi/lm/wrk_save.py
The SAVE worker — the 15th and LAST active level of the RLM pipeline
(step 14, after ANALYTICS; the pipeline is 15/15 COMPLETE since the
D-104 bring-in fe506c6, which brought this worker in together with
model_weights.py, rlm_client.py, the full-chain test module, and the
rlm_03/rlm_04 fixtures). The 6th non-cache worker — no
`cache_manager` wiring, no rlmwf_15* file (no cache level ever used a
"15" slot; the flat-file numbering skips 03/07/08/09/12/13/15). A pure
SINK on every up-move: it reads context attributes and writes ONE
binary artifact — `base_dir/<cfg.output>` (the model weights file,
lz4-compressed by default, with the `.SHA3-256` sidecar written by
binio). It adds NO context attributes; `_down` is a no-op (log only) —
the artifact is never unlinked (the OPTIMIZE-checkpoint /
ANALYTICS-report artifact semantics: build/ files persist across runs).
> State: D-104 · 7fb070b · 2026-09-03 · suite 5/0/0 (via
  test_lm_worker_full_chain — 2 ungated read-guard tests; 3 DB-gated,
  A2050 additionally LONG-gated)

## API

| name | contract |
|---|---|
| `wrk_save()` | factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` (D-104 T1 — with it all 14 worker factories are uniform) returning `Worker("SAVE", _up, _down)` |

## Architecture

61 lines (post D-104).

- Imports (L28-38): pydantic `validate_call`/`ConfigDict` (L30, T1),
  `TYPE_CHECKING` (L32), `Worker`/`Relevance` from state_machine (L34),
  `model_weights_write_file` (L35), `RLMContext` under TYPE_CHECKING
  (L37-38, the hlp_indexes-L166 class, as in every worker). The
  bring-in's dead `from pathlib import Path` is removed (T2).
- `__all__ = ['wrk_save']` (L42).
- `_up` (L46-52): INFO "Saving model weights to disk..." (L47) →
  `output_path = ctx.cfg.base_dir / ctx.cfg.output` (L49) →
  `model_weights_write_file(ctx, output_path, compressed=True)` (L51)
  → INFO "Model weights saved to {output_path}" (L52). The SAVE log
  span is exactly these 2 lines (plus the state-machine's "Starting
  worker SAVE, UP step" / "Completed UP step" lines).
- `_down` (L54-56): INFO "Clearing save attributes..." + the comment
  "Nothing to clear from context, as we just read from it." — SAVE is
  the only worker whose `_down` clears nothing (VALIDATE clears 1,
  ANALYTICS clears 2, ...).
- `wrk_save()` (L58-61): the factory, `@validate_call` since the
  D-104 T1 gate.

## Verified invariants

Pinned by `probes/verify_save.py` (17 checks: A1-A15 static, the C5
a-portion, the D0 LONG placeholder) + the 5-test
`test_lm_worker_full_chain` suite (2 ungated + 3 DB-gated, A2050
additionally LONG-gated).

- Source shape (probe A1-A3, A10-A15): the `@validate_call` factory +
  pydantic import (A1), no pathlib (A2), 0 non-comment trailing-ws
  lines (A3, T4), the test's 2 SKIP_REGAB_DB gates + the D-085 idiom
  (A10-A11), no dead imports (A13), the fixtures' `output` fields +
  cuts (A15: rlm_03 cut=1, rlm_04 cut=10).
- The live rlm_04 chain (the A2030 suite + probe C5): the full
  15-level chain runs to step 14 / "SAVE"; the artifact
  `rglm_logistic_model_ec_20_TEST04.dat` is 21603 bytes, sha3_256
  `bcf8d918979aaddba52ed2c9a80571f4fdc939a985ff4f3705510fa4f8010abb`,
  sidecar valid; probe C5 (the a-portion): the LIVE pre-f32 opt
  `f` 0.00560641149058938 + `g_norm` 4.3686068238457665e-05 — the
  test pins f/g_norm only on the read-back `mw.opt_info` (f32).
- The write is DETERMINISTIC (test_second_instance_deterministic): a
  second full instance in the same base dir produces a byte-identical
  file and exactly 6 "Cache successfully loaded and validated" hits
  (7 cache files: CONFIG re-stores its snapshot on every run — a
  'stored' line, not a 'hit'; the 6 hits are POSITIONS, INDEXES,
  WMAPS, DESIGN_MTR, GENERATE, VLD_POSITIONS), no "Extracted", no
  "established successfully".
- `_down` semantics: no attribute cleared, the artifact persists (the
  base-dir listing after a chain shows the model file + its sidecar
  alongside the caches, the checkpoint and the analytics report).

## Open issues

None.

## Conventions

- The no-cache design is the 6th deviation from the uniform 7-kwargs
  `cache_manager` wiring — intentional and accepted by Roberto (the
  rlmwf_15 slot stays unused like 03/07/08/12).
- `compressed=True` is the only call form in the repo; the
  `compressed` parameter default is True anyway (the read side mirrors
  it).
- The A2030/A2050 test class names are Roberto's legacy production
  naming: A2xxx is the endgame-solver production model family (A2 +
  ec*10; A2050 = ec 20; production runs A2050, A2150, A2250, ...) —
  rlm_03's pattern set is literally named "A2050", rlm_04's is named
  "EDGE" (the class keeps the legacy name — left as-is, accepted,
  O3).

## Integration

- Consumers: the terminal level of the StateMachine — nothing runs
  after SAVE; the saved file is consumed by `twolm/rlm_client.py`
  (`make_evaluation_function`) + `reversi/lm/model_weights.py`
  (`model_weights_read_file`).
- The data it persists is the INFERENCE subset: w_dense +
  iwmap_feature_offset + the full FeatureSet + training-population
  stats + 4/5 opt_info keys + 4/7 vld metrics (model_weights.md).
  `ctx.w` (the compressed trained vector) and the zed transforms are
  deliberately NOT persisted: the client reconstructs everything it
  needs (rlm_client.md) — the zed transforms are a pure function of
  `logit_clipping`.
- `ctx.cfg.output` is a REQUIRED field of
  `ReversiLogisticModelConfig` (rlm_config_schemas L196,
  `output: Path = Field(...)`) — pre-stored by Roberto in all four
  fixtures (each L31) "if needed by the SAVE worker later".
