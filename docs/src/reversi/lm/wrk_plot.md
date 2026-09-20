# reversi/lm/wrk_plot.py
The PLOT worker — the 18th and LAST active level of the LM pipeline (step 18, after CLIENT_CHECK). The run also logs the
TOP-20 EXTREME-OUTLIER report (the 20 validation positions with the largest |residual|, the position's bitboards
included). A non-cache worker — no `cache_manager` wiring, no rlmwf_18* file (a derived-artifact step, regenerated on
every up-move, an idempotent overwrite). It writes the run's matplotlib diagnostic figures (the hlp_plot builders) to
the configured plots directory. All figures are in Y space (the [-64, +64] game-value scale). The pilot is the config's
plot section: the WHITELIST of plot names decides what is generated (a listed name is written, an unlisted one is
skipped, an empty list makes the level a no-op) and the `plot.enable` master switch dominates (false = do nothing, even
with names listed). On an error the worker raises (the failure semantics: the machine logs and re-raises, the step stays
at PLOT). No context attribute is published; `_down` is a no-op (log only).

## API

| name | contract |
|---|---|
| `wrk_plot()` | the factory — `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` returning `Worker("PLOT", _up, _down)` |
| `_up(ctx) -> None` | the pilot check (enable, then the whitelist) → `collect_plot_data` (hlp_plot) → the directory resolution (absolute as-is / relative under `base_dir`) → one figure per whitelisted name, saved in every configured format |
| `_down(ctx) -> None` | the no-op: log only (stateless, as SAVE and CLIENT_CHECK) |

## Architecture

- Imports: `Path`, pydantic, `Worker, Relevance`, the hlp_plot surface ( `PLOT_BUILDERS`, `collect_plot_data`,
  `save_figure`, `close_figure`), `LMContext` under TYPE_CHECKING. NO `reversi.tools.cache_manager` import (by design)
  and NO top-level matplotlib import (it is lazy in hlp_plot — see hlp_plot.md).
- `_up`: the pilot: `plot.enable` false → "PLOT skipped: plot.enable is false." (log only, return); empty `plot.plots` →
  "PLOT skipped: no plot names requested." (log only, return) → "Generating {n} plot(s)..." → `collect_plot_data(ctx)` →
  the directory:
  `Path(plot_cfg.dir_name)`, used as-is when ABSOLUTE (it may live outside base_dir), else `base_dir / dir_name`;
  `mkdir(parents=True, exist_ok=True)` → the per-name loop: `PLOT_BUILDERS[name](data, ctx.cfg.name)` → `save_figure` in
  every format of `plot_cfg.format` (the "pdf,png" pair writes both) → `close_figure` → "Plot '{name}' saved: {paths}" →
  the completion line: "PLOT done: {n} plot(s) written to {dir}."
- `_down`: INFO "Clearing plot attributes..." — nothing cleared (the figures are built and closed locally on every
  up-move).
- `wrk_plot()`: the factory, `@validate_call`-decorated (the uniform worker-factory idiom).

## Verified invariants

Pinned by the 9-test `test_wrk_plot` suite (no DB, the synthetic rlm_04-mirror context) + the 18-check
`probes/verify_plot.py` (no DB) + the full-chain suite (DB-gated).

- The full whitelist in png: the seven figures in `base_dir/plots` (the relative dir_name default), the PNG magic + a >5
  KB size, the per-plot "saved:" lines and the "PLOT done" line; the SECOND up-move regenerates byte-identical files
  (the seeded jitter + the deterministic Agg rendering) (`test_up_all_seven_png`).
- The rendering golden: the parity figure of the synthetic context (SEED 42, N_TRN 1200 / N_VLD 1000, png 150 dpi)
  hashes to the pinned sha3_256 — version-sensitive like the f32 goldens; the env-drift re-pin (visually identical
  rendering) (`test_parity_png_golden`).
- The pilot: `enable=false` with a full whitelist does NOTHING (no directory, no files, the single skip line —
  `test_up_disabled_is_a_noop`); the empty whitelist the same (`test_up_empty_whitelist_is_a_noop`); a partial whitelist
  writes only the listed names (`test_up_partial_whitelist`).
- The formats: the "pdf,png" pair writes both magic per name, exactly 2×2 files (`test_up_format_pair_writes_both`); the
  schema-side format/name validation lives in test_hlp_config_schemas (the PlotConfig section).
- The directory: an ABSOLUTE dir_name is used as-is (outside base_dir), the relative default does not leak there
  (`test_up_absolute_dir_name`).
## Open issues

None.

## Conventions

- The pilot: the plot names in the config are OPTIONAL. The default section (empty whitelist) makes a no-plot config a
  clean no-op level; the rlm_03 / rlm_04 test fixtures list all seven names so the chains exercise the generation
  end-to-end.
- A deviation from the uniform 7-kwargs `cache_manager` wiring — the rlmwf_18 slot stays unused, like
  01/02/06/09/10/11/14/15/16/17.
- The worker is stateless by design: it publishes no context attribute (the figures are local; the only durable outputs
  are the files + the event log lines).
- Y space throughout: the x-axes are on the [-64, +64] scale, the plots comparable across models with different
  logit_clipping.

## Integration

- Pipeline ordering: PLOT is the 18th step; its inputs come from POSITIONS (`ctx.game_values`), ANALYTICS
  (`ctx.train_dense_rn` — the dense training residuals), VALIDATE (`ctx.vld_y_pred`, `ctx.vld_rn`), VLD_POSITIONS
  (`ctx.vld_game_values`) and CONFIG (`ctx.cfg.plot`, `ctx.cfg.name`, `ctx.cfg.base_dir`) — the SM half-open interval
  semantics guarantee every up-move to step 18 passes through all of them.
- Consumes hlp_plot: `collect_plot_data` (the ASSEMBLY of the published series — no forward pass, I-018 — the same
  formulas as hlp_analytics' dense metrics and the CLIENT_CHECK reference), the `PLOT_BUILDERS` registry, `save_figure`
  / `close_figure`.
- Consumes the config: `PlotConfig` (hlp_config_schemas) — the fail-fast name/format validation happens at the CONFIG
  level, before the pipeline reaches PLOT.
- Downstream: nothing — the terminal level. `move_to_last()` reaches it; a failure leaves `current_step` at 18 (the
  failure semantics).
