# twolm/lm_worker_save.py

Analysis date: 2026-09-02 — analysis session 29 (D-104, the SAVE
bring-in, Roberto's commit fe506c6 — the LAST bring-in of the pipeline);
fix campaign D-104 approved by Roberto ("T1: OK, T2: OK, T4: OK, T5: OK,
T6: OK, M1: OK ... Procedi!") and applied in the same session. Brought in
by Roberto together with `model_weights.py` (the persistence layer) and
`rlm_client.py` (the inference API) plus the full-chain test module and
the rlm_03/rlm_04 fixtures.

The SAVE worker of the RLM pipeline: the FIFTEENTH and last pipeline
level (step index 14, after ANALYTICS). The SIXTH non-cache worker
(after FEATURES, ZED, GRADIENT, VALIDATE, ANALYTICS) — no
`cache_manager` wiring, no rlmwf_15* file (no cache level ever used a
"15" slot; the pattern of skipping slots 03/07/08/09/12/13 continues).
The level is a pure SINK on every up-move: it reads context attributes
and writes ONE binary artifact — `base_dir/<cfg.output>` (the model
weights file, lz4-compressed by default, with a `.SHA3-256` sidecar
written by binio). It adds NO context attributes; `_down` is a no-op
(log only) — the artifact is never unlinked (the OPTIMIZE-checkpoint /
ANALYTICS-report artifact semantics: build/ files persist across runs).

## Suite status (session 29, post D-104)

- `test_lm_worker_full_chain`: 3/0/0 live (2 A2030 methods + the 2 read
  guards are the only ungated additions; see the test doc), A2050
  LONG-gated (~10 min, `LONG=1`).
- Full discover: 631 tests, 87 skipped under `SKIP_REGAB_DB=1`, GREEN
  (2.6 s). Pre-campaign the bring-in left 628/85; the campaign added 3
  tests (A2030 second-instance + 2 read guards) and 2 gated skips
  (the SKIP_REGAB_DB gate added to both A2030 methods — pre-campaign
  A2030 ran in "gated" mode silently, because `SKIP_REGAB_DB` is a
  test-side convention only: no production code reads it).

## State per Roberto

Pipeline COMPLETE: 15 active levels, 0 commented imports, 0 commented
worker-list entries (pre-campaign: the last two commented lines, the
L54 import and the L221 worker-list entry, were uncommented by the
bring-in itself). The `A2050` / `A2030` class names in the test module
are Roberto's legacy production naming: `A2xxx` is the
endgame-solver production model family (A2 + ec*10; A2050 = ec 20;
production runs A2050, A2150, A2250, ...).

## Architecture (61 lines, post D-104)

- L28-37 imports: pydantic `validate_call`/`ConfigDict` (T1),
  `TYPE_CHECKING`, `Worker`/`Relevance` from state_machine,
  `model_weights_write_file` from model_weights; `RLMContext` under
  TYPE_CHECKING (the rlm_indexes-L166 class, as in every worker).
  The bring-in's dead `from pathlib import Path` (T2) is removed.
- L42 `__all__ = ['lm_worker_save']`.
- L46-52 `_up(ctx)`: INFO "Saving model weights to disk..." →
  `output_path = ctx.cfg.base_dir / ctx.cfg.output` →
  `model_weights_write_file(ctx, output_path, compressed=True)` →
  INFO "Model weights saved to {output_path}". The SAVE log span is
  exactly these 2 lines (plus the state-machine's "Starting worker
  SAVE, UP step" / "Completed UP step" lines).
- L54-56 `_down(ctx)`: INFO "Clearing save attributes..." + the
  comment "Nothing to clear from context, as we just read from it." —
  no context attribute is touched (SAVE is the only worker whose
  `_down` clears nothing; VALIDATE clears 1, ANALYTICS clears 2, etc.).
- L58-61 `lm_worker_save()` — the D-104 T1 gate:
  `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))`,
  returning `Worker("SAVE", _up, _down)`. All 14 worker factories are
  now uniform (the D-092/D-098/D-100/D-103 T1 convention, completed).

## Verified facts (D-104 probe — 30 checks, 0 mismatches)

- The full 15-level chain runs to step 14 / "SAVE" on rlm_04 (3 s,
  probe C1) and rlm_03 (~10 min, D tier, LONG).
- rlm_04 artifact: `rglm_logistic_model_ec_20_TEST04.dat`, 21603 bytes,
  sha3_256 `bcf8d918979aaddba52ed2c9a80571f4fdc939a985ff4f3705510fa4f8010abb`,
  sidecar valid (C6). rlm_03 artifact: 515042 bytes,
  sha3_256 `3ad1805815c536e4506b0804b5be9e8662de53402c37fc3268c8dbbbb6847ff4`
  (D6).
- The write is DETERMINISTIC: a second full instance in the same base
  dir produces a byte-identical file and 6 "Cache successfully loaded
  and validated" hits (C14). Note the 7 cache files vs 6 hits: CONFIG
  re-stores its snapshot on every run ("Configuration file ... stored to
  cache file", INFO — a 'stored' line, not a 'hit'); the 6 hits are
  POSITIONS, INDEXES, WMAPS, DESIGN_MTR, GENERATE, VLD_POSITIONS
  (POSITIONS and VLD_POSITIONS additionally log the DEBUG
  "is_cache_consistent = True." from their validate_fn).
- `_down` semantics: no attribute cleared, artifact persists (the
  build/tmp dir listing after a chain shows the model file + its
  sidecar alongside the caches, the checkpoint and the analytics
  report).

## Minor notes (D-104 observations, report-only)

- O1: the model file is never unlinked by `_down` (artifact semantics,
  consistent with the ANALYTICS report file, D-103 O5).
- The factory gate (T1) is the last of the 14 — with it, every worker
  factory in the pipeline validates its (zero) arguments uniformly.
- `compressed=True` is the only call form in the repo; the
  `compressed` parameter default is True anyway (the read side mirrors
  it).

## Integration notes

- `ctx.cfg.output` is a REQUIRED field of
  `ReversiLogisticModelConfig` (rlm_config_schemas L196,
  `output: Path = Field(...)`) — pre-stored by Roberto in all four
  fixtures (rlm_01 L31 / rlm_02 L31 / rlm_03 L31 / rlm_04 L31) "if
  needed by the SAVE worker later", exactly as the pipeline's
  train_metrics/analytics_report attributes were pre-stored for it.
- The data it persists is the INFERENCE subset: w_dense +
  iwmap_feature_offset + the full FeatureSet + training-population
  stats + 4/5 opt_info keys + 4/7 vld metrics (model_weights.md).
  `ctx.w` (the compressed trained vector) and the zed transforms are
  deliberately NOT persisted: the client reconstructs everything it
  needs (rlm_client.md) — the zed transforms are a pure function of
  `logit_clipping`.

## Appendix — line reference (post D-104, 61 lines)

- L1-26 license header (canonical, untouched)
- L28 `from __future__ import annotations`
- L30 `from pydantic import validate_call, ConfigDict` (T1)
- L32 `from typing import TYPE_CHECKING`
- L34-35 state_machine + model_weights imports
- L37-38 RLMContext under TYPE_CHECKING
- L42 `__all__`
- L46-52 `_up` (2 INFO logs + the write call)
- L54-56 `_down` (no-op)
- L58 `@validate_call(...)`
- L59-61 `lm_worker_save()` factory
