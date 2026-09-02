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
gate's TypeError). D-079/D-080: lm_worker_positions enabled
(601de87) + analyzed/fixed; rlm_config_schemas analyzed/fixed.
D-081 (f051dd3, Roberto): `lm_worker_features()` uncommented —
the pipeline now runs 4 active levels (CREATED sentinel → CONFIG
→ POSITIONS → FEATURES); the 35-check probe re-pinned to the
post-D-074/D-076/D-081 state (the session-21 original pinned the
pre-D-074 state and was never re-pinned): 0 mismatches. D-083/D-085/
D-087/D-088/D-091/D-092: WMAPS + DESIGN_MTR + ZED brought in by
Roberto (a323e0f, 582841e, 439c966) and analyzed/fixed per level —
the pipeline now runs 9 active levels. D-093 (a0adc6e, Roberto):
GRADIENT brought in — 9th active level; the 35-check probe
re-pinned to the 9-worker state (V3c had pinned the stale 5-worker
list since a323e0f): 0 mismatches. D-094: GRADIENT fix campaign
(R1 float32 cast, T1-T9, M1 dedicated suite) — no change to this
module. D-096 (1ebdd8b, Roberto): OPTIMIZE brought in (the two
modules + the two tests, the import + worker-list entry) — 10th
active level; the 35-check probe re-pinned to the 10-worker state
(V3c had pinned the 9-worker list since a0adc6e): 0 mismatches — no
change to this module. D-097 (e31c061, Roberto): GENERATE brought
in (rlm_generate + lm_worker_generate + test_rlm_generate, the
import L50 + worker-list entry L216) — 11th active level; the probe
re-pinned to the 11-worker state (V3c had pinned the 10-worker
list since 1ebdd8b): 0 mismatches. D-098: the GENERATE fix
campaign (R1 + T1-T9 + M1-M5) — no change to this module beyond
the bring-in lines. D-099 (ede2efe, Roberto): VLD_POSITIONS
brought in (lm_worker_vld_positions, the import L51 + worker-list
entry L217) — 12th active level; the probe re-pinned to the
12-worker state (V3c had pinned the 11-worker list since
e31c061): 0 mismatches — no change to this module. D-100: the
VLD_POSITIONS fix campaign (R1 + T1-T5 + M1-M3, test file
added) — no change to this module beyond the bring-in lines.
D-101 (536eadc, Roberto): VALIDATE brought in (lm_worker_validate
+ rlm_validate — the first bring-in with a dedicated data module
besides the worker; the import L52 + worker-list entry L218) — 13th
active level. D-102: the VALIDATE fix campaign (R1 + T1-T5 +
M1-M3, test file added) — no change to this module beyond the
bring-in lines. D-103 (96dacb5, Roberto): ANALYTICS brought in
(lm_worker_analytics + rlm_analytics — the 2nd bring-in with a
dedicated data module, function-only; the import L53 + worker-list
entry L220) — 14th active level; the 35-check probe re-pinned to
the 14-worker state (V3c had pinned the 13-worker list since
536eadc): 0 mismatches. D-103 campaign: the ANALYTICS fix campaign
(T1-T6 + M1-M3, test file added, rlm_01.json detailed_report +=
LMC) — this module: RLMContext pre-declares train_metrics (M1,
L155), 39 fields.**
Sibling modules
lm_worker_config / lm_worker_positions / rlm_config_schemas are
deliberately NOT analyzed this session (Roberto: "Lo faremo in
seguito").

State per Roberto (intentional, NOT defects):
- the pipeline is deliberately PARTIAL: of the 15 workers 14 are
  active (CREATED sentinel + CONFIG + POSITIONS + FEATURES +
  INDEXES + WMAPS + DESIGN_MTR + ZED + GRADIENT + OPTIMIZE +
  GENERATE + VLD_POSITIONS + VALIDATE + ANALYTICS — the worker
  list L206-220); the last remaining factory import is commented
  (L54, "Remove comments when modules are added"): save;
- the 2 tests in test_logistic_model that were once muted
  (`test_move_to_step_delegates_to_state_machine`,
  `test_move_to_step_by_string`) are both restored "una riga alla
  volta, seguendo lo sviluppo della pipeline": D-076 (the CONFIG
  level) + session 28 (the POSITIONS level, existing since
  601de87/D-079, per Roberto's approval) — all 15 methods active,
  0 muted.

Suite: 15/0/0 GREEN (test_logistic_model, all 15 active,
post D-075/D-076 + the session-28 restore).

## Architecture

`LogisticModel` is the first concrete **domain facade**: it extends
`BaseModel` (base_model.md) and wires the generic StateMachine to the
RLM (Reversi Logistic Model) pipeline. Construction is a 4-step
recipe (L184-225): (1) validate the domain paths with the plain
helpers, (2) build the shared `RLMContext` dataclass, (3) assemble
the worker list (sentinel + commented factory calls), (4)
`super().__init__` hands workers + context + verbosity to
`BaseModel` → `StateMachine`, which also **injects**
`log_event` + the two cache-path closures into the context (V17).

`RLMContext` (a `@dataclass` extending the plain `Context` base) is
the shared blackboard: 39 fields holding config state + every data
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
| `RLMContext(Context)` | `@dataclass`, 39 fields: 3 path/flags (`config_file_path` — the only no-default field, `base_dir_override`, `use_cache`), `cfg`, 32 data artifacts (8 of them `*_checksum`), 3 injected callables with lambda no-op defaults (`log_event`, the 2 cache helpers, D-069 `*_for_current_level` names — R1). |
| `_created_up` / `_created_down` | Level-0 sentinel workers: log ERROR + raise RuntimeError ("should never happen") — the D-059 sentinel made explicit, as planned in the state_machine resolution. |
| `LogisticModel(BaseModel)` | The facade; 4-step construction (L183-224), `@validate_call`-gated `__init__` (R3). |

### Pipeline shape (15 levels, per the commented worker list)

CREATED (0, sentinel) → CONFIG → POSITIONS → FEATURES → INDEXES →
WMAPS → DESIGN_MTR → ZED → GRADIENT → OPTIMIZE → GENERATE →
VLD_POSITIONS → VALIDATE → ANALYTICS → SAVE. 14 levels are active
today (through ANALYTICS, D-103); the next line-by-line step
is `lm_worker_save` (the last commented entry). The worker
factories follow the pattern `lm_worker_x()` → `Worker` (the tests
patch `twolm.logistic_model.lm_worker_config` etc., i.e. the
factory names in THIS module's namespace).

## Verified facts (V1-V10)

Independently re-derived (scratch/verify_logistic_model.py,
35-check probe), zero mismatches. Re-pinned in D-081 (session 22)
to the post-D-074/D-076/D-081 state: V1e/V1f now pin the
D-074/R1 rename (the legacy `_for_next_level` names gone, the
`*_for_current_level` lambda fields present), V8 pins
`get_type_hints` SUCCEEDING (D-074/R2), V6 pins the
`IsADirectoryError` for a directory as config (D-074/M3) + the
facade `@validate_call` ValidationError (D-074/R3), V3c pins the
14-worker list (re-pinned D-103 — it had been stale since
536eadc),
V9 pins the worker boundaries (D-076 gate split + D-060 failure
semantics), V10 pins the absence of a `features_checksum` field
(the FEATURES level is a pure in-memory derivation).

| # | Fact | Method |
|---|---|---|
| V1 | `RLMContext` is a dataclass on a PLAIN (non-dataclass) `Context` base; `config_file_path` is the only no-default field; `use_cache` defaults to None; the 2 injected cache-helper fields carry the D-069 `*_for_current_level` names with lambda no-op defaults (the pre-injection fallback, D-074/R1) | dataclasses.fields inspection |
| V2 | After `LogisticModel(...)`: the `*_for_current_level` context attributes ARE the injected closures (the dataclass lambda defaults replaced at init — the same mechanism as `log_event`); no dual-name state remains (D-074/R1) | Live probe (re-run post D-074) |
| V3 | `model.context is model.sm.context`; verbosity get/set delegates; at init step 0 / "CREATED" | Probe |
| V4 | Sentinel callables log ERROR then raise RuntimeError on DIRECT call; a bare (non-injected) context runs them safely (no-op log, still raises) | Probe |
| V5 | `_check_config_file_path`: str/Path → Path; int → TypeError ("Argument config_file_path is not an instance of str or Path"); a directory → IsADirectoryError ("File path is not a file: ...") post M3/D-074 | Probe |
| V6 | `_check_base_dir_override`: str/Path → Path; int → TypeError; a file → NotADirectoryError ("File path is not a directory: ...") | Probe |
| V7 | 4-worker machine boundaries (re-pinned D-081 — the 1-worker pre-D-076 preconditions are obsolete): on the `{}` dummy config, `move_to_step(1)`, `move_to_step("POSITIONS")` and `move_to_last()` all hit the CONFIG worker first and raise its pydantic ValidationError (the D-076 gate split — no conversion to the gate's TypeError); a failed move leaves `current_step` at the failed step 1 (D-060) | Probe (fresh model per boundary) |
| V8 | (pre-D-074 state) `typing.get_type_hints(RLMContext)` → **NameError: name 'Union' is not defined** — the missing import was latent, masked by `from __future__ import annotations` (PEP 563); post D-074/R2 the annotations are `str | None` and `get_type_hints` resolves | Probe (pre) + re-check (post) |
| V9 | The 8 `*_checksum` fields: rds, rlm_indexes, wmaps_obj, design_matrix, zed, w, dense_w, vld_rds (all `str | None` post D-074/R2) | dataclasses.fields inspection |
| V10 | The two cache-consuming worker call sites use the D-069 names (D-074/R1): lm_worker_config.py `ctx.get_cache_file_path_for_current_level()`, lm_worker_positions.py `ctx.get_cache_file_full_path_for_current_level()` — they resolve to the real injected closures now that both entries are enabled (lm_worker_features is the 3rd enabled worker but never touches the closures — no cache, D-081) | grep (cross-reference) + probe V3c |

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

## Appendix: line-number reference (2026-09-02, file 225 lines,
post D-103)

- `from __future__ import annotations`: L28
- imports: L30-32 (dataclasses — `field` removed M5/D-075 ·
  pathlib · typing) · L34 (pydantic, D-074/R3) · L36 (state_
  machine) · L37 (base_model) · L39-54 (worker factories: L41-53
  active post 96dacb5/D-103, L54 commented — save)
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
  `vld_metrics` L152, `train_metrics` L155 (D-103 M1),
  `analytics_report` L156, injected callables
  L158-163 (comment L158-160, `log_event` L161, D-069
  `*_for_current_level` names L162-163 — R1 resolved)
- `_created_up` / `_created_down`: L168-174 (level-0 comment L166)
- `LogisticModel`: L177 (class docstring L178-181) —
  `__init__` L184-225: `@validate_call` L183 (R3), signature
  L184-187, docstring L188-192 (M4), path validation L194-197,
  context build L200-203, workers list L206-222 (sentinel L207,
  active factory calls L208-220 post 96dacb5/D-103, commented
  factory call L221 — save), `super().__init__` L225
