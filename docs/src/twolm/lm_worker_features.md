# twolm/lm_worker_features.py

Analysis date: 2026-08-31 — analysis session 22 (D-081). Probe
(scratch/verify_lm_worker_features.py, 42 checks): 0 mismatches.

The FEATURES worker of the RLM pipeline — the 4th active level
(CREATED sentinel → CONFIG → POSITIONS → FEATURES), enabled
line-by-line by Roberto in f051dd3 (the factory import L43 + the
worker-list entry L209 uncommented in logistic_model.py) together
with the related test copied from the original repo. Unlike
POSITIONS, this worker is a PURE-COMPUTE level: it builds a
FeatureSet from the CONFIG-loaded cfg (no DB, no cache_manager, no
cache file — the flat rlmwf_03_FEATURES* files never materialize,
probe B10) and exposes it on the context as `ctx.feature_set` for
the workers that follow.

## Suite status (session 22, D-081)

- `test_lm_worker_features`: 1/0/0 (Roberto's file; the test is
  DB-DEPENDENT — the setUp moves through POSITIONS, which hits the
  DB on a fresh base dir — and T2 flags the missing SKIP_REGAB_DB
  gate; run with the live DB)
- Full discover: 499 tests, 54 skipped under `SKIP_REGAB_DB=1`
  (17 PERF + 35 regab + 2 positions; the new test RUNS ungated —
  it needs the live DB), GREEN; ungated (live DB): 499 run,
  17 skipped (PERF only), GREEN.

## State per Roberto

Pipeline-in-progress, 4 active levels (CREATED → CONFIG →
POSITIONS → FEATURES). OPEN: R1 (the amask debug log) + M1-M3;
test T1-T4 + M1-M2 (awaiting Roberto's call). The next line-by-line
step is `lm_worker_indexes()` + the last muted test
(`_test_move_to_step_by_string` in test_logistic_model.py — a test
file change, Roberto's call).

## Architecture (123 lines)

- `lm_worker_features() -> Worker` (L120-122): factory returning
  `Worker("FEATURES", _up, _down)`. M1: no `@validate_call` (the
  house convention, applied to the lm_worker_positions factory in
  D-080 M1).
- `_up` (L46-48): INFO "Loading board features as defined by the
  model..." → `ctx.feature_set = _load_features(ctx)`.
- `_down` (L50-52): INFO "Clearing features..." →
  `ctx.feature_set = None`.
- `_load_features(ctx) -> FeatureSet` (L54-79): (1)
  `intercept = _load_intercept(ctx)`; (2) `mset = _load_mobility
  (ctx)`; (3) `pset = _load_patterns(ctx)`; (4)
  `FeatureSet(ctx.cfg.feature_set.name, intercept, mset, pset)` —
  the name comes from the schema's `FeatureSetConfig.name`
  (default `'NoNameFeatureSet'` — the fixture has no name key,
  probe B3b); (5) the zero-feature guard:
  `len(feature_set.features) == 0` → ERROR log + ValueError
  ("The feature count is zero. It is not possible to generate a
  model without features.") — the comment at L63 quotes the
  empty-string SHA-256 hash, which the message does not use (M3);
  (6) the INFO summary (name, hash, has Intercept / has
  MobilitySet / has PatternSet + the children's name/hash) and the
  DEBUG per-feature table
  (`{i:03d} [category] name n_instances n_configurations`).
- `_load_intercept(ctx) -> Feature | None` (L81-89): truthy
  `cfg.feature_set.intercept` (schema: `Optional[bool] = False`) →
  `Feature.new_intercept()` (name "INTERCEPT", 1/1), else None.
- `_load_patterns(ctx) -> PatternSet | None` (L91-103): truthy
  `cfg.feature_set.pattern_set` → `Pattern(elt.name, elt.mask)`
  per element (the schema's field_validator already converted the
  16-hex no-0x strings to Bitboard, rlm_config_schemas D-080 M1)
  → `PatternSet(cfg_pset.name, patterns)` + a DEBUG per-pattern
  table; else None.
- `_load_mobility(ctx) -> MobilitySet | None` (L105-117): same
  pattern → `Mobility(elt.name, elt.mask, elt.amask)` per element
  → `MobilitySet(cfg_mset.name, mobility_features)` + a DEBUG
  per-mobility table — R1: the table's amask slot prints
  `m.mask`; else None.

## Verified facts (D-081 probe — 42 checks, 0 mismatches)

- V1 (B1a/B1b, B2): after `move_to_step("FEATURES")` — step 3,
  worker "FEATURES"; the 4-worker list is
  `[CREATED, CONFIG, POSITIONS, FEATURES]`.
- V2 (A4/A5, B10): pure compute — no cache_manager import; the
  base dir after the move holds ONLY the flat
  `rlmwf_01_CONFIG.dat` + `.SHA3-256` and `rlmwf_02_POSITIONS.dat`
  + `.SHA3-256` (no `rlmwf_03_FEATURES*` file); `RLMContext` has
  no `features_checksum` field (the logistic_model probe V10 —
  the feature_set is an in-memory derivation).
- V3 (B1b/B3a/B12): `feature_set` is None before the level, set
  after, cleared by `_down` (down to CONFIG: step 1, None).
- V4 (B3b): the FeatureSet name is `'NoNameFeatureSet'`
  (`FeatureSetConfig.name` default; the fixture has no name key).
- V5 (B4a-c): the intercept (INTERCEPT, 1/1); MobilitySet
  'BasicMobilitySet' with exactly the 3 fixture members (LMC
  mask=all-1s/amask=0, ALMC mask=0/amask=all-1s, DLMC both
  all-1s — the CORRECT values: the R1 bug is log-only); PatternSet
  'BasicPatternSet' with exactly ELLE (0x107) + EDGE (0xFF).
- V6 (B5): feature order — intercept, mobilities in the
  MobilitySet sorted (mask, amask) order [ALMC, LMC, DLMC],
  patterns in the PatternSet sorted mask order [EDGE, ELLE].
- V7 (B6/B7): n_features = 6, n_instances = 16 (1 + 1+1+1 +
  8+4); per-feature counts LMC 65/1, ALMC 65/1, DLMC 129/1, ELLE
  81/8, EDGE 6561/4.
- V8 (B9a-d): hash = `sha3_256(b'INTERCEPT' + mset.hash +
  pset.hash)` — recomputed independently; the independently built
  FeatureSet (public API only, fixture constants) has the same
  feature list and hash.
- V9 (B8a-c): the R1 behaviour pin — at verbosity HIGH the 3
  mobility DEBUG lines print `m.mask` twice: the LMC line shows
  `amask = FFFFFFFFFFFFFFFF` (true amask: 0), the ALMC line shows
  `amask = 0000000000000000` (true amask: FFFFFFFFFFFFFFFF);
  DLMC (both all-1s) is unaffected.
- V10 (B11a/b): the zero-feature guard — a cfg with intercept
  False and no pset/mset → ValueError "The feature count is
  zero..." + an ERROR log.
- V11 (B13a-c): cross-run — a second instance on the same
  base_dir: POSITIONS served from cache ("Cache successfully
  loaded and validated", no "Extracted"), FEATURES recomputed (no
  cache), feature set IDENTICAL (name + hash).
- V12 (A1-A3): structure — 123 lines, `__all__ =
  ['lm_worker_features']`, `Worker("FEATURES", _up, _down)`.
- V13 (A4): the `RLMContext` import sits under TYPE_CHECKING
  (the circular-import guard: logistic_model imports this
  module).

## Issues (OPEN)

- **R1 — the amask debug log prints the mask (log-only, no data
  impact).** L112:
  `f"... mask = {m.mask:016X}, amask = {m.mask:016X}"` — the amask
  slot re-prints `m.mask`. For the fixture: LMC (true amask 0)
  logs FFFFFFFFFFFFFFFF, ALMC (true amask FFFFFFFFFFFFFFFF) logs
  0000000000000000; DLMC (both all-1s) is unaffected. The
  FeatureSet / MobilitySet are built from the correct `m.amask`
  values (V5) — the defect is confined to the DEBUG table, which
  is only visible at verbosity HIGH (the test's Verbosity.LOW
  never reaches it). Fix: print `m.amask` in the amask slot.
  Pinned by A7 + B8a-c.

## Minor notes (OPEN)

- M1 (A6): the factory lacks
  `@validate_call(config=ConfigDict(arbitrary_types_allowed=True))`
  — the house convention (D-080 M1 applied it to
  lm_worker_positions; the factory takes no args, so the impact is
  convention-only).
- M2 (A9): 2 non-header trailing-whitespace lines (L49 after the
  `_up` body, L78 after the feature loop). Scope as in D-078 M3:
  the license-header `# ` lines stay.
- M3 (A8): the orphan comment at L63 —
  `#: Empty String SHA-256 Hash: "e3b0c442..."` — the hash is
  quoted but never used in the error message (a leftover of an
  earlier draft).

## Integration notes

- Pipeline ordering (as for CONFIG / POSITIONS): `ctx.cfg` must be
  set before `_load_features` runs — the SM half-open interval
  semantics guarantee CONFIG runs first on every up-move.
- The worker never touches the injected cache closures — the first
  pipeline level that needs no cache (the cache-consuming levels
  are the ones that persist derived data; FEATURES is pure
  derivation from the config, and `RLMContext` carries no
  `features_checksum` field accordingly).
- The FeatureSet name: the schema default `'NoNameFeatureSet'`
  means the worker's INFO log shows the default unless the config
  carries a `name` key — a config-authoring detail, not a defect
  (V4).
- The `if cfg_x:` truthiness gates: `intercept` is a plain bool
  (genuine truthiness), while `pattern_set` / `mobility_set` are
  pydantic models — always truthy when defined, None when the
  config omits them, so the gates correctly select "present or
  not".

## Appendix — line reference

123 lines, as of D-081.

- L28-38: imports (state_machine L32, feature L33, mobility L34,
  pattern L35, TYPE_CHECKING RLMContext L37-38)
- L42: `__all__`
- L46-48: `_up` (M2 whitespace L49)
- L50-52: `_down`
- L54-79: `_load_features` (zero-feature guard L62-66 [M3 comment
  L63], summary logs L67-77 [M2 whitespace L78])
- L81-89: `_load_intercept`
- L91-103: `_load_patterns`
- L105-117: `_load_mobility` (R1 L112)
- L120-122: `lm_worker_features()` (M1)
