# logistic_model.py — analysis

Date: 2026-08-30. Module added by Roberto (6bb45fb, 6-file batch with
base_model + lm_worker_config + lm_worker_positions +
rlm_config_schemas + test_logistic_model). **Analysis session 21;
fix campaign batch 1 applied (D-074): R1 RESOLVED (D-069 rename —
RLMContext fields + the 2 ported worker call sites), R2 RESOLVED
(8 annotations → `str | None`, no import), R3 RESOLVED
(@validate_call, with base_model R1), M1-M4 fixed; M5 NEW and OPEN
(dead `field` import); D-075: M5 FIXED — all R/M CLOSED.
D-076: `lm_worker_config()` uncommented in the worker list
(pipeline: CREATED + CONFIG now the 2 active levels), json5
declared in pyproject.toml, SM gate split (domain pydantic
ValidationErrors from the CONFIG worker no longer converted to the
gate's TypeError).** Sibling modules
lm_worker_config / lm_worker_positions / rlm_config_schemas are
deliberately NOT analyzed this session (Roberto: "Lo faremo in
seguito").

State per Roberto (intentional, NOT defects):
- the pipeline is deliberately PARTIAL: of the 15 workers
  `CREATED` + `CONFIG` are active (D-076: `lm_worker_config()`
  uncommented, L207); `lm_worker_positions` is imported (L42) but
  its list entry is commented (L208); the other 12 factory imports
  are commented (L43-54, "Remove comments when modules are added");
- the 1 muted test in test_logistic_model (`_test_move_to_step_by_
  string`) comes back "una riga alla volta, seguendo lo sviluppo
  della pipeline" (D-076: `test_move_to_step_delegates_to_state_
  machine` restored — the CONFIG level it targets now exists).

Suite: 14/0/0 GREEN (test_logistic_model, 14 active + 1 muted,
post D-075/D-076).

## Architecture

`LogisticModel` is the first concrete **domain facade**: it extends
`BaseModel` (base_model.md) and wires the generic StateMachine to the
RLM (Reversi Logistic Model) pipeline. Construction is a 4-step
recipe (L183-224): (1) validate the domain paths with the plain
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
plus the 3 infrastructure callables (D-069 `*_for_current_level`
names post D-074/R1, lambda no-op defaults as the pre-injection
fallback). The 8 checksum fields
(`*_checksum`) pair with `cache_manager`'s duck-typed
`compute_sha3_256_hash` flow: workers store the data checksum the
same way `cache_manager_load_or_compute` returns it.

### Components

| Component | Role |
|---|---|
| `_check_config_file_path(str\|Path) -> Path` | Type-check (bare TypeError), `Path(...)` coercion, existence (FileNotFoundError), is-file (IsADirectoryError — fixed in M3). |
| `_check_base_dir_override(str\|Path) -> Path` | Same pattern; is-dir check raises NotADirectoryError. |
| `RLMContext(Context)` | `@dataclass`, 38 fields: 3 path/flags (`config_file_path` — the only no-default field, `base_dir_override`, `use_cache`), `cfg`, 29 data artifacts (8 of them `*_checksum`), 3 injected callables with lambda no-op defaults (`log_event`, the 2 cache helpers, D-069 `*_for_current_level` names — R1). |
| `_created_up` / `_created_down` | Level-0 sentinel workers: log ERROR + raise RuntimeError ("should never happen") — the D-059 sentinel made explicit, as planned in the state_machine resolution. |
| `LogisticModel(BaseModel)` | The facade; 4-step construction (L183-224), `@validate_call`-gated `__init__` (R3). |

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
| V1 | `RLMContext` is a dataclass on a PLAIN (non-dataclass) `Context` base; `config_file_path` is the only no-default field; `use_cache` defaults to None; the 2 injected cache-helper fields carry the D-069 `*_for_current_level` names with lambda no-op defaults (the pre-injection fallback, D-074/R1) | dataclasses.fields inspection |
| V2 | After `LogisticModel(...)`: the `*_for_current_level` context attributes ARE the injected closures (the dataclass lambda defaults replaced at init — the same mechanism as `log_event`); no dual-name state remains (D-074/R1) | Live probe (re-run post D-074) |
| V3 | `model.context is model.sm.context`; verbosity get/set delegates; at init step 0 / "CREATED" | Probe |
| V4 | Sentinel callables log ERROR then raise RuntimeError on DIRECT call; a bare (non-injected) context runs them safely (no-op log, still raises) | Probe |
| V5 | `_check_config_file_path`: str/Path → Path; int → TypeError ("Argument config_file_path is not an instance of str or Path"); a directory → IsADirectoryError ("File path is not a file: ...") post M3/D-074 | Probe |
| V6 | `_check_base_dir_override`: str/Path → Path; int → TypeError; a file → NotADirectoryError ("File path is not a directory: ...") | Probe |
| V7 | 1-worker machine boundaries (the muted tests' preconditions): `move_to_step(1)` → IndexError "Target step 1 is out of bounds."; `move_to_step("POSITIONS")` → ValueError "Worker 'POSITIONS' not found in the pipeline."; `move_to_last()` at step 0 is a no-op | Probe |
| V8 | (pre-D-074 state) `typing.get_type_hints(RLMContext)` → **NameError: name 'Union' is not defined** — the missing import was latent, masked by `from __future__ import annotations` (PEP 563); post D-074/R2 the annotations are `str | None` and `get_type_hints` resolves | Probe (pre) + re-check (post) |
| V9 | The 8 `*_checksum` fields: rds, rlm_indexes, wmaps_obj, design_matrix, zed, w, dense_w, vld_rds (all `str | None` post D-074/R2) | dataclasses.fields inspection |
| V10 | The two ALREADY-PORTED worker call sites use the D-069 names (D-074/R1): lm_worker_config.py `ctx.get_cache_file_path_for_current_level()`, lm_worker_positions.py `ctx.get_cache_file_full_path_for_current_level()` — they resolve to the real injected closures once the worker entries are enabled | grep (cross-reference, modules not otherwise analyzed) |

## Issues (R1-R3)

### R1 — D-069 name divergence: RLMContext + the ported workers use the OLD cache-helper names — RESOLVED (D-074, session 21)
D-069 (state_machine M5) renamed the injected cache helpers to
`get_cache_file_path_for_current_level` /
`get_cache_file_full_path_for_current_level` and flagged "two call
sites in domain modules lm_worker_config + logistic_model to update
at port". The port did NOT update them: `RLMContext` still declared
the injected callables under the pre-D-069 `_for_next_level` names
(lambda no-op defaults, "# Injected by StateMachine"), and both
ported workers called the old names (V10). Nothing broke yet — the
worker list entries are commented — but the divergence was a
**silent-failure trap**: `StateMachine.__init__` injects the real
closures under the NEW names (state_machine L179/L187, plain
instance attributes), so a worker running against this context would
find the no-op lambda under the old name and get `None` for its
cache path, with no exception. **Applied (D-074), option (a),
Roberto-approved:** the 2 `RLMContext` fields renamed to the D-069
names (the lambda defaults are now the pre-injection fallback under
the SAME names, exactly like `log_event`) AND the 2 ported worker
call sites renamed (lm_worker_config `get_cache_file_path_for_
current_level`, lm_worker_positions `get_cache_file_full_path_for_
current_level`) — 4 lines total, D-069-compliant. Verified: the
injected closures bind under the renamed fields, no `for_next_level`
reference remains in src/; the D-069 follow-up in the state_machine
doc is marked CLOSED.

### R2 — `Union` is used but never imported — RESOLVED (D-074, session 21)
`from typing import List, Any, Callable` (L32) has no `Union`, yet 8
RLMContext fields were annotated `Union[str, None]`. It only worked
because `from __future__ import annotations` (L28) makes PEP 563
store annotations as unevaluated strings; `typing.get_type_hints
(RLMContext)` proved the latent NameError (V8, pre-state). **Applied
(D-074):** matching the file's own modern style (`Path | None`,
`bool | None`), the 8 annotations were rewritten as `str | None` —
no import needed; `get_type_hints` now resolves.

### R3 — No `@validate_call` on `LogisticModel.__init__` — RESOLVED (D-074, session 21, with base_model R1)
Same call as base_model.md R1 (decided once, applied to both facades):
the manual `isinstance` checks raised bare TypeErrors; the house
`@validate_call` gate (D-069 M11 pattern on the SM) would give
pydantic ValidationErrors. **Applied (D-074), Roberto-approved:**
`@validate_call(config=ConfigDict(arbitrary_types_allowed=True))` on
`LogisticModel.__init__` AND on `BaseModel.__init__` (pydantic is
now an import in both modules). Approved behaviour change:
wrong-typed constructor args (e.g. an `int` config_file_path) now
raise a pydantic `ValidationError` at the facade boundary instead of
the manual `TypeError` / the inner SM gate; valid `str` paths are
unchanged — `arbitrary_types_allowed=True` keeps the manual helpers
as the single gate for existence/type semantics (the `Path(...)`
coercion at L68/L78 stays belt-and-braces for the checks that follow
it).

## Minor notes (M1-M4)

- **M1** (FIXED, D-074) — Comment typo: "Full exploded weigth array"
  → "weight" (now L141).
- **M2** (FIXED, D-074) — `vld__pop_stats` (now L149): double
  underscore, unlike every other vld field (`vld_positions`,
  `vld_game_values`, `vld_rds_checksum`, `vld_metrics`). Roberto:
  "e' un typo" → renamed `vld_pop_stats`.
- **M3** (FIXED, D-074) — `_check_config_file_path` raised
  FileNotFoundError for the "path exists but is a directory" case;
  now raises `IsADirectoryError` (L71-72) — the accurate type,
  symmetric with `_check_base_dir_override`'s NotADirectoryError (
  L81-82).
- **M4** (FIXED, D-074) — `LogisticModel.__init__` docstring added
  (L187-191) (house style: public methods documented — the facade
  methods in base_model.py all have one-liners).
- **M5** (FIXED, D-075) — Dead import: `field` from `dataclasses`
  (L30) was imported but never used — `RLMContext` has no
  `field(...)` members. Removed (Roberto: "rimuovi").

## Integration notes

- **cache_manager flow**: when the worker entries are uncommented,
  the workers call `cache_manager_load_or_compute(...)` with
  `is_allowed = ctx.use_cache` (lm_worker_positions L60) and the
  cache paths from the injected helpers — the D-069
  `*_for_current_level` names (D-074/R1) are what feed that flow.
- **cfg precondition**: both injected closures read
  `ctx.cfg.cache_files_prefix` / `ctx.cfg.base_dir` (state_machine
  L172/L184) — `cfg` must be populated by the CONFIG worker before
  any cache call (the closures raise AttributeError otherwise; the
  lambda no-op fallback sits under the same names now but is
  reachable only pre-injection, i.e. on a bare RLMContext).
- **use_cache**: `lm_worker_config` sets `ctx.use_cache = cfg.use_
  cache` from the config (rlm_config_schemas `use_cache: bool =
  True`), and the CONFIG down path resets it to None (L58/L66) —
  the cache switch is per-run, per the R1 ruling pattern of
  cache_manager (D-071).

## Appendix: line-number reference (2026-08-30, file 224 lines,
post D-074)

- `from __future__ import annotations`: L28
- imports: L30-32 (dataclasses — `field` removed M5/D-075 ·
  pathlib · typing) · L34 (pydantic, D-074/R3) · L36 (state_
  machine) · L37 (base_model) · L39-54 (worker factories: L41-42
  active, L43-54 commented)
- `__all__`: L57
- `_check_config_file_path`: L65-73 (type check L66-67, existence
  L69-70, is-file L71-72 — IsADirectoryError, M3)
- `_check_base_dir_override`: L75-83 (is-dir L81-82)
- `RLMContext`: L88 (`@dataclass` L87, docstring L89-92) —
  `config_file_path` L93, `base_dir_override` L94, `use_cache` L95,
  `cfg` L100, positions group L103-106, `feature_set` L109, indexes
  L112-113, wmaps L116-122, design matrix L125-126, zed L129-132,
  `fg` L135, opt L138-139, dense w L142-143 (comment L141 — M1
  fixed), vld group L146-149 (`vld_pop_stats` L149 — M2 fixed),
  `vld_metrics` L152, `analytics_report` L155, injected callables
  L157-162 (comment L157-159, `log_event` L160, D-069
  `*_for_current_level` names L161-162 — R1 resolved)
- `_created_up` / `_created_down`: L167-173 (level-0 comment L165)
- `LogisticModel`: L176 (class docstring L177-180) —
  `__init__` L183-224: `@validate_call` L182 (R3), signature
  L183-186, docstring L187-191 (M4), path validation L193-196,
  context build L199-202, workers list L205-221 (sentinel L206,
  commented factory calls L207-220), `super().__init__` L224
