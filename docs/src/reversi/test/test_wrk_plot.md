# reversi/test/test_wrk_plot.py
The no-DB suite of the PLOT worker (the 17th level, D-149): it
exercises the worker DIRECTLY on a synthetic rlm_04-mirror context
(the same feature layout and the same production iwmap pin as
test_wrk_client_check.py) — the training design indexes are built
with the REAL `compute_indexes` column contract (one column per
feature INSTANCE, the configuration index within the feature), and
`wrk_plot().up(ctx)` runs the full level: pilot → `collect_plot_
data` → directory → the figures → the save. No DB, no pipeline:
the `Worker.up` @validate_call gate (context: Context) requires a
REAL `LMContext`; the `cfg` attribute is the SimpleNamespace
stand-in (the D-144 v2 micro-test idiom) and `log_event` a
capturing lambda.
> State: D-149 · 2026-09-10 · suite 9/0/0

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestWrkPlot` (ungated — no DB, no pipeline; setUp: `mkdtemp` under `CUSTOM_TMP_BASE`, the seeded synthetic ctx — SEED 42, N_TRN 1200 / N_VLD 1000, int8 game values in steps of 2, logit clipping 0.01, the rlm_04 feature layout + iwmap [0,1,66,6627], the per-instance training index matrix) | 9 | `test_factory_returns_named_worker`: the `@validate_call` factory returns `Worker("PLOT", …)` (the uniform worker-factory idiom). `test_up_disabled_is_a_noop`: the D-149 master switch — `enable=false` with a FULL whitelist does NOTHING (no directory, no files, the captured log is exactly `["PLOT skipped: plot.enable is false."]`). `test_up_empty_whitelist_is_a_noop`: names are OPTIONAL — an empty whitelist is a clean no-op (`"PLOT skipped: no plot names requested."`). `test_up_all_seven_png`: the full whitelist in png — the seven figures in `base_dir/plots` (the relative dir_name default), the PNG magic + a >5 KB size, the per-plot "Plot '{name}' saved:" lines + the "PLOT done: 7 plot(s) written to {dir}." line; the SECOND up-move regenerates BYTE-IDENTICAL files (the seeded jitter + the deterministic Agg rendering — the per-name sha3 comparison). `test_up_format_pair_writes_both`: the 'pdf,png' pair (the D-149 format ruling) — both magics per name, exactly 2×2 files. `test_up_absolute_dir_name`: the D-149 directory ruling — an ABSOLUTE dir_name is used as-is (outside base_dir), the relative default does not leak there. `test_up_partial_whitelist`: only the LISTED names are generated (a listed name is written, an unlisted one is skipped) — one file, "PLOT done: 1 plot(s)". `test_parity_png_golden`: THE D-149 RENDERING GOLDEN — the parity figure of the synthetic context (SEED 42, N_TRN 1200 / N_VLD 1000, png 150 dpi) hashes to the pinned sha3_256 (version-sensitive, like the f32 goldens, D-127). `test_down_is_a_noop_log`: the stateless `_down` (as SAVE / CLIENT_CHECK) logs only. |

## Goldens pinned

- The parity PNG sha3_256: `ff459b8e9e232481e49e97ebf4f4668fec3f
  cc0eccaadf1612173afaf50299d0` — the rendering golden of the
  synthetic context (it moves when matplotlib or numpy changes, as
  the f32 goldens do).
- The per-up-move determinism: every one of the seven PNGs hashes
  equal across two up-moves (the seeded jitter, the KDE subsample
  seed, the Agg backend).
- The skip-line literals: "PLOT skipped: plot.enable is false." /
  "PLOT skipped: no plot names requested." — the D-149 pilot
  wording (the no-op paths).
- The completion-line shape: "PLOT done: {n} plot(s) written to
  {dir}." (the count + the resolved directory).
- The `iwmap` pin [0, 1, 66, 6627] (the production rlm_04 layout)
  + the per-instance index contract (one column per feature
  instance, the value the configuration index within the feature)
  — the synthetic context mirrors the real INDEXES level.

## Conventions

- The D-065/D-085 idiom: files ONLY under `build/tmp`
  (`CUSTOM_TMP_BASE`), removed in `tearDown` (the `mkdtemp`
  + `shutil.rmtree` pattern).
- `Worker.up` is `@validate_call`-gated with `context: Context`
  (state_machine L87-90): a SimpleNamespace context is rejected by
  the gate — hence the real `LMContext`; only the `cfg` attribute
  (with its `plot` SimpleNamespace) may be a stand-in.
- The synthetic data is SEEDed (42) so the golden is stable; the
  sizes (N_TRN 1200 / N_VLD 1000) keep the module under ~5 s in
  the default tier.

## Integration

- The DB-gated complement: `test_lm_worker_full_chain` (the A2030
  chain pins the seven PNGs + the "saved:"/"done" log lines at the
  20k/199932 scale; the A2050 VLONG chain at the 200k scale) +
  `probes/verify_logistic_model.py` V3c (the 17-level pipeline
  shape, the PLOT last).
- The hlp-level complement: `test_hlp_plot` (the pure helpers: the
  vocabulary, the jitter, the EGV bins, the KDE guard).
- The schema complement: `test_hlp_config_schemas` (the PlotConfig
  section — the defaults, the format normalization, the fail-fast
  name guard, the dedupe).
- The probe complement: `probes/verify_plot.py` (the 16-check
  no-DB probe: the vocabulary, the lazy import, the seven-builder
  rendering, the pair formats, the determinism, the pilot
  semantics).
- The level under test: `reversi/lm/wrk_plot.py` (wrk_plot.md);
  the builders: `reversi/lm/hlp_plot.py` (hlp_plot.md); the
  schema: `reversi/lm/hlp_config_schemas.py` (the PlotConfig
  section).
