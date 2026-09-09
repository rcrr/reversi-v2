# reversi/lm/wrk_save.py
The SAVE worker — the 15th and LAST active level of the LM pipeline
(step 14, after ANALYTICS). The 6th non-cache worker — no
`cache_manager` wiring, no rlmwf_15* file (no cache level ever used a
"15" slot; the flat-file numbering skips 03/07/08/09/12/13/15). A pure
SINK on every up-move: it reads context attributes and writes TWO
artifacts — `base_dir/<cfg.output>` (the model weights file,
lz4-compressed by default, with the `.SHA3-256` sidecar written by
binio) and, since D-142, the configuration provenance record
`base_dir/<cfg.output>.config.json` (the normalized dump + its
`.SHA3-256` checksum sidecar — the record travels with the shipped
artifact). It adds NO context attributes; `_down` is a no-op (log
only) — the artifacts are never unlinked (the OPTIMIZE-checkpoint /
ANALYTICS-report artifact semantics: build/ files persist across runs).
> State: D-142 · 181cb57 · 2026-09-09 · suite 6/0/0 (via
  test_lm_worker_full_chain — 2 ungated + 4 DB-gated, A2050
  additionally VLONG-gated)

## API

| name | contract |
|---|---|
| `wrk_save()` | factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("SAVE", _up, _down)` |

## Architecture

76 lines (post D-142).

- Imports (L28-39): pydantic `validate_call`/`ConfigDict` (L30),
  `TYPE_CHECKING` (L32), `Worker`/`Relevance` from state_machine
  (L34), `write_sha3_256_sidecar` from binio (L35, D-142),
  `model_weights_write_file` (L36), `LMContext` under TYPE_CHECKING
  (L39, the hlp_indexes-L166 class, as in every worker).
- `__all__ = ['wrk_save']` (L42).
- `_up` (L47-55): INFO "Saving model weights to disk..." (L48) →
  `output_path = ctx.cfg.base_dir / ctx.cfg.output` (L50) →
  `model_weights_write_file(ctx, output_path, compressed=True)` (L52)
  → INFO "Model weights saved to {output_path}" (L53) →
  `_store_config_record(ctx, output_path)` (L55, D-142). The SAVE log
  span is these 3 lines (plus the state-machine's "Starting worker
  SAVE, UP step" / "Completed UP step" lines).
- `_store_config_record` (L57-68, D-142): the provenance record —
  `config_json = ctx.cfg.model_dump_json(indent=4)` (the normalized
  dump: the EFFECTIVE configuration of the run, the base_dir
  override included — the same bytes whose sha3_256 is
  `ctx.config_checksum`, computed at CONFIG), written to
  `output_path.with_suffix(".config.json")` (e.g.
  `rglm_logistic_model_ec_20_TEST04.config.json`) via
  `write_text`, then the binio checksum sidecar
  (`write_sha3_256_sidecar`, the standard `sha3_256sum` format —
  verifiable with `sha3_256sum -c`), then the INFO log.
- `_down` (L70-73): INFO "Clearing save attributes..." + the comment
  "Nothing to clear from context, as we just read from it." — SAVE is
  the only worker whose `_down` clears nothing (VALIDATE clears 1,
  ANALYTICS clears 2, ...).
- `wrk_save()` (L75-76): the factory.

## Verified invariants

Pinned by `probes/verify_save.py` (17 checks: A1-A15 static, the C5
a-portion, the D0 LONG placeholder) + the 6-test
`test_lm_worker_full_chain` suite (2 ungated + 4 DB-gated, A2050
additionally VLONG-gated).

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
  (the 6 rlmwf_ cache files all hit — POSITIONS, INDEXES, WMAPS,
  DESIGN_MTR, GENERATE, VLD_POSITIONS — + the OPTIMIZE checkpoint
  with its own read-back; the CONFIG level writes no cache file
  anymore, D-142), no "Extracted", no "established successfully".
- The config record (D-142, test_config_record_sidecar):
  `<output>.config.json` exists next to the model file, its content
  is byte-identical to `ctx.cfg.model_dump_json(indent=4)` (and
  matches `ctx.config_checksum`), and its `.SHA3-256` sidecar
  verifies (the binio sidecar API).
- `_down` semantics: no attribute cleared, the artifacts persist (the
  base-dir listing after a chain shows the model file + its sidecar
  + the config record pair alongside the caches, the checkpoint and
  the analytics report).

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
  after SAVE; the saved file is consumed by `reversi/lm/client.py`
  (`make_evaluation_function`) + `reversi/lm/model_weights.py`
  (`model_weights_read_file`).
- The config record (D-142): `<output>.config.json` + its
  `.SHA3-256` sidecar — the normalized config dump (the effective
  configuration of the run, the base_dir override included) that
  generated the model; the same fingerprint hex appears on the
  "Config SHA3-256" line of both analytics reports
  (hlp_analytics.md).
- The data it persists is the INFERENCE subset: w_dense +
  iwmap_feature_offset + the full FeatureSet + training-population
  stats + 4/5 opt_info keys + 4/7 vld metrics (model_weights.md).
  `ctx.w` (the compressed trained vector) and the zed transforms are
  deliberately NOT persisted: the client reconstructs everything it
  needs (client.md) — the zed transforms are a pure function of
  `logit_clipping`.
- `ctx.cfg.output` is a REQUIRED field of
  `LMConfig` (hlp_config_schemas L196,
  `output: Path = Field(...)`) — pre-stored by Roberto in all four
  fixtures (each L31) "if needed by the SAVE worker later".
