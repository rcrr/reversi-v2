# reversi/lm/wrk_save.py
The SAVE worker of the LM pipeline — the 16th active level (step 16): the level after ANALYTICS, before
CLIENT_CHECK. The
non-cache worker — no `cache_manager` wiring, no rlmwf_16* file (the flat-file numbering skips every non-cache slot —
  only 03/04/05/07/08/12/13 materialize). A pure SINK on every up-move: reads context attributes, writes ONE artifact —
`base_dir/<cfg.output>` (the model weights file, lz4-compressed by default, with the `.SHA3-256` sidecar written by
binio). That single artifact is SELF-DESCRIBING: the v2 file embeds the configuration provenance (the normalized dump +
the fingerprint, the leading body section — model_weights.md), so the model file is the single source of the run's
configuration. No `<output>.config.json` sidecar record is written. It adds NO context attributes; `_down` is a no-op
(log only) — the artifact is never unlinked (the OPTIMIZE-checkpoint / ANALYTICS-report artifact semantics: build/ files
persist across runs).

## API

| name | contract |
|---|---|
| `wrk_save()` | factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("SAVE", _up, _down)` |

## Architecture

- Imports: pydantic `validate_call`/`ConfigDict`, `TYPE_CHECKING`, `Worker`/`Relevance` from state_machine,
  `model_weights_write_file` (the writer embeds the config provenance itself, so no binio `write_sha3_256_sidecar`
  import is needed), `LMContext` under TYPE_CHECKING (the hlp_indexes- class, as in every worker).
- `__all__ = ['wrk_save']`.
- `_up`: INFO "Saving model weights to disk..." → `output_path = ctx.cfg.base_dir / ctx.cfg.output` → the comment block
  (the single-source semantics) → `model_weights_write_file(ctx, output_path, compressed=True)` → INFO "Model weights
  saved to {output_path}" → DEBUG "Model weights file: {size} bytes, checksum: {sha3-256}." (the
  integrity echo — the final artifact's size + checksum, the compressed bytes hash). The SAVE log
  span is these 3 lines (plus the state-machine's "Starting worker SAVE, UP step"
  / "Completed UP step" lines).
- `_down`: INFO "Clearing save attributes..." + the comment "Nothing to clear from context, as we just read from it." —
  SAVE's `_down` clears nothing (like ANOVA, CLIENT_CHECK and PLOT); VALIDATE and ANALYTICS each clear 4 fields.
- `wrk_save()`: the factory.

## Verified invariants

Pinned by `probes/verify_save.py` (18 checks: A1-A15 static + A6b the config-leads-the-body / v1|v2 guard / corruption
sentinel, the C5 a-portion, the D0 LONG placeholder) + the 9-test `test_lm_worker_full_chain` suite (2 ungated + 3
ungated v2 micro + 4 DB-gated, A2050 additionally VLONG-gated).

- Source shape (probe A1-A3, A10-A15): the `@validate_call` factory + pydantic import (A1), no pathlib (A2), 0
  non-comment trailing-ws lines (A3), the test's 2 SKIP_REGAB_DB gates + the gated-suite idiom (A10-A11), no dead
  imports (A13), the fixtures' `output` fields + cuts (A15: rlm_03 cut=1, rlm_04 cut=10).
- The live rlm_04 chain (the A2030 suite + probe C5): the full 19-worker chain runs to step 19 (move_to_last(),
  "FINAL_LOG_PRINT");
  the v2 artifact `rglm_logistic_model_ec_20_TEST04.dat` is in the 23183-23283 B size band, sidecar valid (the embedded
  dump carries the run's base_dir, so the bytes are run-specific; the size is a band too: LZ4's match structure shifts
  by a few bytes with the 8 random base_dir chars — measured on A2050: 516459 / 516455 for the identical content;
  determinism is pinned by the same-base-dir byte identity + the read-back provenance); probe C5 (the a-portion): the
  LIVE pre-f32 opt `f` 0.005608053877949715 + `g_norm` 6.098220910644159e-05 — the test pins f/g_norm only on the
  read-back `mw.opt_info` (f32).
- The write is DETERMINISTIC within a base dir (test_second_instance_deterministic): a second full instance in the same
  base dir produces a byte-identical file and exactly 6 "Cache successfully loaded and validated" hits (the 6
  rlmwf_ cache files all hit — POSITIONS, INDEXES, WMAPS, DESIGN_MTR, GENERATE, VLD_POSITIONS — + the OPTIMIZE
  checkpoint with its own read-back; the CONFIG level writes no cache file), no "Extracted", no "established
  successfully".
- The single source of the configuration (test_config_provenance_single_source): the record `<output>.config.json` and
  its sidecar do NOT exist; the model file's sidecar still verifies (it covers the v2 content, config section included);
  `ctx.config_checksum` == sha3_256 of the normalized dump (the fingerprint semantics, on the embedded provenance). The
  embedded fields themselves are pinned in test_full_worker_chain (A2030 + A2050): `mw.config_dump` ==
  `ctx.cfg.model_dump_json(indent=4)`, `mw.config_checksum` == `ctx.config_checksum`.
- `_down` semantics: no attribute cleared, the artifact persists (the base-dir listing after a chain shows the model
  file + its sidecar alongside the caches, the checkpoint and the analytics report).

## Open issues

None.

## Conventions

- The no-cache design is a deviation from the uniform 7-kwargs `cache_manager` wiring — intentional (no rlmwf_16 file —
  SAVE writes the config-named model artifact — and the non-cache slots 01/02/06/09/10/11/14/15/17/18/19 have none
  either).
- `compressed=True` is the only call form in the repo; the `compressed` parameter default is True anyway (the read side
  mirrors it).
- The A2030/A2050 test class names are the legacy production naming: A2xxx is the endgame-solver production model family
  (A2 + ec*10; A2050 = ec 20; production runs A2050, A2150, A2250, ...) — rlm_03's pattern set is literally named
  "A2050", rlm_04's is named "EDGE" (the class keeps the legacy name — left as-is, O3).

## Integration

- Consumers: the next level is CLIENT_CHECK (the saved-model file acceptance test — it re-reads THIS level's artifact
  and rebuilds the client's EF on it); the saved file is also consumed out-of-pipeline by `reversi/lm/client.py`
  (`make_evaluation_function` / `make_evaluation_function_array`) + `reversi/lm/model_weights.py`
  (`model_weights_read_file`).
- The configuration provenance: INSIDE the model file (the v2 leading body section — model_weights.md). The same
  fingerprint hex appears on the "Config SHA3-256" line of both analytics reports (hlp_analytics.md); the model file
  stands alone as the shipped artifact.
- The data it persists is the INFERENCE subset: w_dense + iwmap_feature_offset + the full FeatureSet +
  training-population stats + 4/5 opt_info keys + 4/7 vld metrics + the configuration provenance (model_weights.md).
  `ctx.w` (the compressed trained vector) and the zed transforms are deliberately NOT persisted: the client reconstructs
  everything it needs (client.md) — the zed transforms are a pure function of `logit_clipping`.
- `ctx.cfg.output` is a REQUIRED field of `LMConfig` (hlp_config_schemas, `output: Path = Field(...)`) — stored in all
  seven fixtures; the "if needed by the SAVE worker later" comment is in `wrk_analytics.py`.
