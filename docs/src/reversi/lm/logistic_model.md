# reversi/lm/logistic_model.py
The first concrete domain facade: it wires the generic StateMachine to the LM (Reversi Logistic Model) pipeline — a
4-step construction (validate the domain paths, build the shared LMContext blackboard, assemble the 19-level worker
list, hand the parts to BaseModel → StateMachine) — plus the LMContext @dataclass: config state, every data artifact
produced by the 19 levels, the 9 checksum fields, and the 3 infrastructure callables the machine injects at
construction. It is also the pipeline's script entry (the `build_model` entry, the `__main__` block).

## API

| family | name | contract |
|---|---|---|
| Context | `LMContext(Context)` | `@dataclass`, 46 fields (43 data/config + the 3 injected callables); the only no-default field is `config_file_path`; the 3 injected callables carry lambda no-op defaults (the pre-injection fallback) |
| Context | config group | `config_file_path: Path`, `base_dir_override: Path \| None`, `use_cache: bool \| None`, `cfg: Any`, `config_checksum: str \| None` (the config fingerprint — the sha3_256 of the normalized dump, computed at CONFIG, consumed by the SAVE record + the analytics report) |
| Context | data artifacts (38) | by stage: positions `rds_checksum`/`positions`/`game_values`/`training_pop_stats`; features `feature_set`/`su_analysis_tables` (the corpus frequency tables, the cross-level blackboard for the ANOVA level); indexes `hlp_indexes_checksum`/`hlp_indexes`; wmaps `wmaps_obj_checksum`/`feature_w_ranges`/`iwmap_feature_offset`/`iwmap`/`wmap`/`wmap_fallback`/`w`; design `design_matrix_checksum`/`design_matrix`; zed `zed_checksum`/`y2z`/`z2y`/`z`; gradient `fg`; optimize `w_checksum`/`opt_info`; dense `dense_w_checksum`/`w_dense`; vld `vld_rds_checksum`/`vld_positions`/`vld_game_values`/`vld_pop_stats`; validation `vld_metrics`/`vld_y_pred`/`vld_rn`/`vld_outliers` (the published series + the 20 records); analytics `train_metrics`/`train_dense_metrics`/`train_dense_rn`/`analytics_report` — the 9 `*_checksum` fields pair with cache_manager's duck-typed compute flow |
| Context | injected callables | `log_event`, `get_cache_file_path_for_current_level`, `get_cache_file_full_path_for_current_level` (lambda no-op defaults = pre-injection fallback, replaced at init by the machine's closures) |
| Facade | `LogisticModel(config_file_path, verbosity=STANDARD, base_dir_override=None)` | `@validate_call` (arbitrary_types_allowed) 4-step construction; wrong-typed args raise pydantic ValidationError at the facade boundary |
| Facade | pass-throughs | `move_to_step(int \| str)`, `move_to_last()`, `show_event_log()`, `show_history_of_moves()`, `export_history_of_moves_as_csv(path)` — pure delegation to the StateMachine |
| Facade | `run(target_level=None)` | the target-driven driver (inherited from `base_model.md`): the first real level (CONFIG) runs first, then the target resolves as the explicit argument, else `_configured_target_level()`, else the last step; `"last"` / a blank value → `move_to_last()` |
| Facade | `_configured_target_level() -> int \| str \| None` | the LM override: `cfg.target_level` of the loaded config (`None` when no config is loaded or the field is absent — the base default, i.e. the whole pipeline) |
| Facade | views | `current_step`, `current_worker_name` (read-only mirrors), `verbosity` (get/set through the SM) |
| CLI | `build_model(json_config: Path, verbosity: Verbosity) -> None` | `@validate_call` (arbitrary_types_allowed); build the `LogisticModel` and run it to the last level (`move_to_last()`) — the `__main__` script entry, not in `__all__` |
| Private | `_check_config_file_path(str \| Path) -> Path` | TypeError (bad type), FileNotFoundError (missing), IsADirectoryError (a directory) |
| Private | `_check_base_dir_override(str \| Path) -> Path` | TypeError, FileNotFoundError, NotADirectoryError (a file) |
| Private | `_created_up` / `_created_down(ctx)` | the level-0 CREATED sentinels: log ERROR + raise RuntimeError |

## Architecture

```
LogisticModel.__init__ (@validate_call, arbitrary_types_allowed)
    1. _check_config_file_path / _check_base_dir_override (plain helpers)
    2. LMContext(config_file_path, base_dir_override)  — the blackboard
    3. workers = [ Worker("CREATED", _created_up, _created_down),
                   wrk_config(), wrk_positions(), ..., wrk_save() ]
    4. super().__init__(workers, context, verbosity)
           |
BaseModel -> StateMachine: stores workers/context, INJECTS log_event +
    format_event_log + the two cache closures into the context
    (replacing the lambda defaults),
    step 0 / "CREATED"
```

- **4-step construction** — (1) validate the domain paths with the plain helpers, (2) build the shared `LMContext`, (3)
  assemble the worker list (sentinel + the 19 factory calls), (4) `super().__init__` hands workers + context + verbosity
  to `BaseModel` → `StateMachine`, which injects `log_event` + `format_event_log` + the two cache-path
  closures into the context (replacing the lambda defaults under the same names — the same mechanism as `log_event`).
- **LMContext is the shared blackboard** — a `@dataclass` extending the plain (non-dataclass) `Context` base; workers
  publish to the pre-declared fields (an ad-hoc attribute works but breaks the pattern); `cfg` must be populated by the
  CONFIG worker before any cache call (the injected closures read `ctx.cfg.cache_files_prefix` / `ctx.cfg.base_dir` and
  raise AttributeError otherwise).
- **Pipeline shape: 19 levels, all active** —

  ```
  CREATED (0, sentinel) -> CONFIG -> FEATURES -> SU_ANALYSIS
  -> POSITIONS -> INDEXES -> ANOVA -> WMAPS -> DESIGN_MTR
  -> ZED -> GRADIENT -> OPTIMIZE -> GENERATE -> VLD_POSITIONS
  -> VALIDATE -> ANALYTICS -> SAVE -> CLIENT_CHECK -> PLOT
  -> FINAL_LOG_PRINT
  ```
(SU_ANALYSIS step 3, the rlmwf_03 slot; ANOVA step 6, NO cache; PLOT step 18; FINAL_LOG_PRINT step 19, NO cache, the
optional `log_file_name` gate)

No commented factory imports or worker-list entries remain. The factories follow `wrk_x()` → `Worker` (19 modules,
`wrk_config` … `wrk_final_log_print`); the tests patch them by name in THIS module's namespace
(`reversi.lm.logistic_model.wrk_config`, …). All 19 factories carry the uniform `@validate_call` gate.
- **use_cache is per-run** — `wrk_config` sets `ctx.use_cache` from the config (`hlp_config_schemas`
  `use_cache: bool = True`); the CONFIG down path resets it to None (the cache_switch pattern).
- **A2xxx naming (legacy production)** — the "A2050" / "A2030" labels of the full-chain tests are the build-config
  family names (the A2050 = the 11-pattern production set, the A2030 = the small EDGE+LMC one); they are NOT derived
  from the ec (both fixtures run ec 20). Intentional, not a typo — do not "fix" them.
- **Script entry (runnable as a command)** — from the workspace root:
  `python -m reversi.lm.logistic_model <config.json> [--verbosity {high,moderate,standard,low,very_low,none}]`
  (default `standard`). The `__main__` block parses the `--verbosity` choice (lowercase `Verbosity` names) and
  calls `build_model` — build the facade, run it to the last level.

## Verified invariants

Pinned by `probes/verify_logistic_model.py` (21 checks) + `test_logistic_model.py` (29 tests).

- The LMContext dataclass shape: plain `Context` base, `config_file_path` the only no-default field, `use_cache` default
  None, the legacy `_for_next_level` names gone, the `*_for_current_level` fields with lambda defaults, the `log_event`
  lambda default — probe V1a-V1g.
- `typing.get_type_hints(LMContext)` succeeds (the `str | None` annotations, no latent Union NameError) — probe V8.
- The config-path helper: str/Path → Path, TypeError, FileNotFoundError, IsADirectoryError — probe V6a-V6b +
  `test_logistic_model::test_config_path_helper_edge_branches`.
- The base-dir helper: str/Path → Path, TypeError, NotADirectoryError — probe V7a-V7b +
  `test_logistic_model::test_base_dir_helper_edge_branches`.
- The complete pipeline: 18 active levels (the 18th, PLOT, is the matplotlib diagnostics — wrk_plot.md; the 17th,
  CLIENT_CHECK, the saved-model file acceptance test — wrk_client_check.md), 0 commented worker imports/entries — probe
  V3c-V3d.
- The injection: the live context's `*_for_current_level` attributes ARE the machine's closures (`_get_cache_file_path`
  / `_get_cache_file_full_path`), `log_event` a bound method, no legacy name in the live context — probe V4a/V4d +
  `test_logistic_model::test_injected_cache_helpers_are_the_machine_closures`.
- The machine boundaries on the `{}` dummy config: `move_to_step(1)` / `move_to_step("POSITIONS")` / `move_to_last()` /
  `run("POSITIONS")` all hit the CONFIG worker first and raise its pydantic ValidationError (the gate split — no
  conversion to the gate's TypeError), a failed move leaves `current_step` at the failed step — probe V9 (4 labels) +
  the `test_move_to_step_*` tests.
- The target-driven stop: `run()` runs CONFIG first, honors the explicit argument over `cfg.target_level`, resolves
  `"last"` / a blank / an absent config to the last step, RESUMES without re-running the levels already done, moves back
  (with their down()) for a lower target, and lets the machine's ValueError / TypeError through — the mocked
  `test_run_*` tests + the real-config `TestRunFacadeOnARealConfig` (FEATURES / SU_ANALYSIS, no DB).
- The 9 checksum fields, and NO `features_checksum` (FEATURES is a pure in-memory derivation) — probe V10.
- The per-level cache path: `<prefix><level:02>_<worker>.dat`, the full variant prepending `cfg.base_dir` —
  `test_logistic_model::test_injected_cache_helper_computes_the_worker_path`.
- The pre-injection fallback: a bare (un-injected) `LMContext` keeps the no-op lambda defaults (helpers return None,
  `log_event` does nothing) — `test_logistic_model::test_pre_injection_fallback_is_no_op_lambda`; a bare call of an
  injected closure before the CONFIG worker raises AttributeError —
  `test_logistic_model::test_injected_cache_closure_requires_cfg`.
- The CREATED sentinels: a direct call logs ERROR then raises RuntimeError —
  `test_logistic_model::test_created_sentinel_workers_raise`.
- The constructor guards: a non-str/Path `config_file_path` → ValidationError (before any factory runs), a missing
  config → FileNotFoundError, a missing base_dir → FileNotFoundError — `test_logistic_model` (the validation-error,
  invalid-config-path and base-dir-override tests).
- The facade is a pure pass-through: every method delegates per method, the read-only views mirror the SM, verbosity
  round-trips — `test_logistic_model` (the facade-delegation, views/verbosity and CSV-export tests).

## Open issues

None.

## Conventions

- The `*_for_current_level` names are the injected-cache-helper contract — a context field renamed back to
  `_for_next_level` silently returns None to the workers (the R1 trap); keep the names in lockstep with the StateMachine
  injection.
- Blackboard fields are pre-declared on LMContext before a worker consumes or publishes them.
- A2xxx = legacy production model family (A2 + ec·10) — do not "fix" these names.
- Worker factories: uniform `@validate_call` gate, patched by name in this module's namespace in the tests.
- Test artifacts live under `build/tmp`, never the system temp dir.

## Integration

- Consumes `state_machine.py` (StateMachine, Worker, Context, Verbosity, Relevance) + `base_model.py` (BaseModel) + the
  18 `wrk_*` factory modules.
- Consumed by: the 18 workers and their `hlp_*` data modules (LMContext as the shared blackboard / type reference),
  `model_weights.py`.
- Not a pipeline level itself: the facade that RUNS the pipeline.
