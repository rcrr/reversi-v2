# logistic_model.py — analysis

Date: 2026-08-30. Module added by Roberto (6bb45fb, 6-file batch with
base_model + lm_worker_config + lm_worker_positions +
rlm_config_schemas + test_logistic_model). **Analysis session 21;
fix campaign pending Roberto's calls.** Sibling modules
lm_worker_config / lm_worker_positions / rlm_config_schemas are
deliberately NOT analyzed this session (Roberto: "Lo faremo in
seguito").

State per Roberto (intentional, NOT defects):
- the pipeline is deliberately PARTIAL: of the 15 workers only
  `CREATED` is active; `lm_worker_config` / `lm_worker_positions` are
  imported (L39-40) but their list entries are commented (L197-198);
  the other 12 factory imports are commented (L41-52, "Remove
  comments when modules are added");
- the 2 muted tests in test_logistic_model come back "una riga alla
  volta, seguendo lo sviluppo della pipeline".

Suite: 5/0/0 GREEN (test_logistic_model, 5 active + 2 muted).

## Architecture

`LogisticModel` is the first concrete **domain facade**: it extends
`BaseModel` (base_model.md) and wires the generic StateMachine to the
RLM (Reversi Logistic Model) pipeline. Construction is a 4-step
recipe (L183-214): (1) validate the domain paths with the plain
helpers, (2) build the shared `RLMContext` dataclass, (3) assemble
the worker list (sentinel + commented factory calls), (4)
`super().__init__` hands workers + context + verbosity to
`BaseModel` → `StateMachine`, which also **injects**
`log_event` + the two cache-path closures into the context (V17).

`RLMContext` (a `@dataclass` extending the plain `Context` base) is
the shared blackboard: 38 fields holding config state + every data
artifact produced by the (future) workers, grouped by pipeline
stage (positions → features → indexes → wmaps → design matrix →
zed → gradient → optimization → dense w → validation → analytics),
plus the 3 infrastructure callables. The 8 checksum fields
(`*_checksum`) pair with `cache_manager`'s duck-typed
`compute_sha3_256_hash` flow: workers store the data checksum the
same way `cache_manager_load_or_compute` returns it.

### Components

| Component | Role |
|---|---|
| `_check_config_file_path(str\|Path) -> Path` | Type-check (bare TypeError), `Path(...)` coercion, existence (FileNotFoundError), is-file (FileNotFoundError — see M3). |
| `_check_base_dir_override(str\|Path) -> Path` | Same pattern; is-dir check raises NotADirectoryError. |
| `RLMContext(Context)` | `@dataclass`, 38 fields: 3 path/flags (`config_file_path` — the only no-default field, `base_dir_override`, `use_cache`), `cfg`, 29 data artifacts (8 of them `*_checksum`), 3 injected callables with lambda no-op defaults (`log_event`, the 2 cache helpers — see R1 for the name issue). |
| `_created_up` / `_created_down` | Level-0 sentinel workers: log ERROR + raise RuntimeError ("should never happen") — the D-059 sentinel made explicit, as planned in the state_machine resolution. |
| `LogisticModel(BaseModel)` | The facade; 4-step construction (L183-214). |

### Pipeline shape (15 levels, per the commented worker list)

CREATED (0, sentinel) → CONFIG → POSITIONS → FEATURES → INDEXES →
WMAPS → DESIGN_MATRIX → ZED → GRADIENT → OPTIMIZE → GENERATE →
VLD_POSITIONS → VALIDATE → ANALYTICS → SAVE. Only CREATED is active
today; the worker factories follow the pattern `lm_worker_x()` →
`Worker` (the tests patch `twolm.logistic_model.lm_worker_config`
etc., i.e. the factory names in THIS module's namespace).

## Verified facts (V1-V10)

Independently re-derived (scratch/verify_logistic_model.py, 30-check
probe), zero mismatches.

| # | Fact | Method |
|---|---|---|
| V1 | `RLMContext` is a dataclass on a PLAIN (non-dataclass) `Context` base; `config_file_path` is the only no-default field; `use_cache` defaults to None; the 2 injected cache-helper fields carry the PRE-D-069 `_for_next_level` names with lambda no-op defaults; the D-069 `*_for_current_level` names are NOT dataclass fields | dataclasses.fields inspection |
| V2 | After `LogisticModel(...)`: the context has BOTH `get_cache_file_path_for_next_level` (the no-op lambda — calling it returns None) AND `get_cache_file_path_for_current_level` (the real injected closure) — the D-069 name divergence is live | Live probe |
| V3 | `model.context is model.sm.context`; verbosity get/set delegates; at init step 0 / "CREATED" | Probe |
| V4 | Sentinel callables log ERROR then raise RuntimeError on DIRECT call; a bare (non-injected) context runs them safely (no-op log, still raises) | Probe |
| V5 | `_check_config_file_path`: str/Path → Path; int → TypeError ("Argument config_file_path is not an instance of str or Path"); a directory → FileNotFoundError ("File path is not a file: ...") | Probe |
| V6 | `_check_base_dir_override`: str/Path → Path; int → TypeError; a file → NotADirectoryError ("File path is not a directory: ...") | Probe |
| V7 | 1-worker machine boundaries (the muted tests' preconditions): `move_to_step(1)` → IndexError "Target step 1 is out of bounds."; `move_to_step("POSITIONS")` → ValueError "Worker 'POSITIONS' not found in the pipeline."; `move_to_last()` at step 0 is a no-op | Probe |
| V8 | `typing.get_type_hints(RLMContext)` → **NameError: name 'Union' is not defined** — the missing import is latent, masked by `from __future__ import annotations` (PEP 563) | Probe |
| V9 | The 8 `*_checksum` fields: rds, rlm_indexes, wmaps_obj, design_matrix, zed, w, dense_w, vld_rds (all `Union[str, None]`) | dataclasses.fields inspection |
| V10 | The two ALREADY-PORTED worker call sites use the pre-D-069 names: lm_worker_config.py L102 `ctx.get_cache_file_path_for_next_level()`, lm_worker_positions.py L59 `ctx.get_cache_file_full_path_for_next_level()` — so once those workers are enabled they would resolve to the no-op lambdas and silently get `None` | grep (cross-reference, modules not otherwise analyzed) |

## Issues (R1-R3)

### R1 — D-069 name divergence: RLMContext + the ported workers use the OLD cache-helper names — OPEN, awaiting Roberto's call
D-069 (state_machine M5) renamed the injected cache helpers to
`get_cache_file_path_for_current_level` /
`get_cache_file_full_path_for_current_level` and flagged "two call
sites in domain modules lm_worker_config + logistic_model to update
at port". The port did NOT update them: `RLMContext` still declares
the injected callables under the pre-D-069 `_for_next_level` names
(L157-158, lambda no-op defaults, "# Injected by StateMachine"), and
both ported workers call the old names (V10). Today nothing breaks —
the worker list entries are commented — but the divergence is a
**silent-failure trap**: `StateMachine.__init__` injects the real
closures under the NEW names (state_machine L179/L187, plain
instance attributes), so a worker running against this context would
find the no-op lambda under the old name and get `None` for its
cache path, with no exception. Fix options: (a) rename the 2
`RLMContext` fields to the D-069 names (the lambda defaults then
serve as the pre-injection fallback, exactly like `log_event`) AND
rename the 2 worker call sites — 4 lines total, D-069-compliant, my
recommendation; (b) keep the old names everywhere and revert the SM
injection to the old names (against D-069); (c) defer until the
worker modules are analyzed.

### R2 — `Union` is used but never imported — OPEN, awaiting Roberto's call
`from typing import List, Any, Callable` (L32) has no `Union`, yet 8
RLMContext fields are annotated `Union[str, None]` (L101, L110,
L114, L123, L127, L136, L140, L144). It only works because
`from __future__ import annotations` (L28) makes PEP 563 store
annotations as unevaluated strings; `typing.get_type_hints(RLMContext)`
proves the latent NameError (V8). Fix: import `Union` (minimal), or —
matching the file's own modern style (`Path | None`, `bool | None`) —
rewrite the 8 annotations as `str | None`.

### R3 — No `@validate_call` on `LogisticModel.__init__` — OPEN, awaiting Roberto's call
Same call as base_model.md R1 (decided once, applied to both facades):
the manual `isinstance` checks raise bare TypeErrors; the house
`@validate_call` gate (D-069 M11 pattern on the SM) would give
pydantic ValidationErrors + the `str` → `Path` coercion for free
(the manual `Path(...)` coercion at L66/L76 then becomes belt-and-
braces for the existence checks).

## Minor notes (M1-M4)

- **M1** — Comment typo: "Full exploded weigth array" (L139) →
  "weight".
- **M2** — `vld__pop_stats` (L147): double underscore, unlike every
  other vld field (`vld_positions`, `vld_game_values`,
  `vld_rds_checksum`, `vld_metrics`). Nothing references it yet
  (the vld workers are not ported), so it is inert for now — but
  decide: typo for `vld_pop_stats`, or the original repo's name
  (kept for fidelity)?
- **M3** — `_check_config_file_path` raises FileNotFoundError for the
  "path exists but is a directory" case (L69-70); `IsADirectoryError`
  would be the accurate type (asymmetry with `_check_base_dir_
  override`'s NotADirectoryError, L80).
- **M4** — `LogisticModel.__init__` has no docstring (house style:
  public methods documented — the facade methods in base_model.py
  all have one-liners).

## Integration notes

- **cache_manager flow**: when the worker entries are uncommented,
  the workers call `cache_manager_load_or_compute(...)` with
  `is_allowed = ctx.use_cache` (lm_worker_positions L60) and the
  cache paths from the injected helpers — the R1 names are what
  feed that flow.
- **cfg precondition**: both injected closures read
  `ctx.cfg.cache_files_prefix` / `ctx.cfg.base_dir` (state_machine
  L172/L184) — `cfg` must be populated by the CONFIG worker before
  any cache call (the closures raise AttributeError otherwise; the
  lambda no-op fallback under the old names would instead silently
  return None — the R1 trap).
- **use_cache**: `lm_worker_config` sets `ctx.use_cache = cfg.use_
  cache` from the config (rlm_config_schemas `use_cache: bool =
  True`), and the CONFIG down path resets it to None (L58/L66) —
  the cache switch is per-run, per the R1 ruling pattern of
  cache_manager (D-071).

## Appendix: line-number reference (2026-08-30, file 214 lines)

- `from __future__ import annotations`: L28
- imports: L30-32 (typing, no Union — R2) · L34 (state_machine) ·
  L35 (base_model) · L37-52 (worker factories: L39-40 active,
  L41-52 commented)
- `__all__`: L55
- `_check_config_file_path`: L63-71 (Type check L64-65, existence
  L67-68, is-file L69-70)
- `_check_base_dir_override`: L73-81 (is-dir L79-80)
- `RLMContext`: L86 (`@dataclass` L85, docstring L87-90) —
  `config_file_path` L91, `base_dir_override` L92, `use_cache` L93,
  `cfg` L98, positions group L101-104, `feature_set` L107, indexes
  L110-111, wmaps L114-120, design matrix L123-124, zed L127-130,
  `fg` L133, opt L136-137, dense w L140-141 (typo L139 — M1), vld
  positions L144-147 (`vld__pop_stats` L147 — M2), `vld_metrics`
  L150, `analytics_report` L153, injected callables L156-158
  (legacy names — R1)
- `_created_up` / `_created_down`: L163-169 (level-0 comment L161)
- `LogisticModel`: L172 (class docstring L173-176) —
  `__init__` L178-214: signature L178-181, path validation L184-186,
  context build L189-192, workers list L195-211 (sentinel L196,
  commented factory calls L197-210), `super().__init__` L214
