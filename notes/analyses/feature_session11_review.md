<!-- ARCHIVED — D-106 step 10 (the docs/ rewrite, 2026-09-04): the
     complete session-11 analysis (2026-08-28) of feature.py moved
     out of docs/src/twolm/feature.md per docs_rules.md §1/§4.
     This is a frozen historical record: it is never updated.
     Stale-in-current-context notes: (1) the "Suite baseline:
     13/0/1 (1 skip = PERF gate)" figure is PRE the test T
     campaign (D-043..D-050, 2026-08-28/29) — test_feature.py has
     been unchanged since a5db33b (D-050, 2026-08-29) and the
     current suite is 19/0/1 (19 run + 1 PERF skip); (2) the
     L144 line "The IndexArray return annotation applies the same
     BeforeValidator dtype check as in pattern.py/mobility.py"
     misattributes the check — it rides on the IMPORTED
     IndexArray alias (pattern.py L74: Annotated + BeforeValidator
     (validate_index_array)); feature.py's own BeforeValidator
     import (L49) is never referenced (dead since b51bea6; the
     D-038 R4 batch removed only the dead typing imports) —
     surfaced as the new OPEN R1 of the migrated mirror; (3) the
     V1-V7 / R1-R4 / M1-M4 campaign narratives are frozen
     history (all disposed: D-038, D-039..D-042). -->

# feature.py analysis

_Analyzed 2026-08-28 (session 11). Source: 275 lines, added 2026-08-28
(commit b51bea6). Suite baseline: `twolm.test.test_feature` 13/0/1
GREEN (1 skip = PERF gate). Environment: numpy 2.5.2, numba 0.67.0,
Python 3.12.3._

## What it is

`feature.py` is the **first integration module of the pipeline**: it
wraps the three feature sources already in the package — the constant
intercept, `Mobility` (mobility.py) and `Pattern` (pattern.py) — into
two classes:

- `Feature`: one evaluation feature, typed as `INTERCEPT`, `MOBILITY`
  or `PATTERN` (nested `Category` IntEnum), carrying the `name`,
  `n_configurations`, `n_instances` and the source object in `ref`
  (kept out of `__repr__`). Direct construction is blocked
  (`Feature()` raises `RuntimeError`); instances come only from the
  factory methods `new_intercept()`, `new_from_mobility(m)`,
  `new_from_pattern(p)`.
- `FeatureSet`: a named collection composed of an optional intercept
  feature, a `MobilitySet` and a `PatternSet`. It builds the flat
  `features` list, the summed `n_instances`, a derived `hash`,
  `print_summary`, and `compute_indexes(positions)` — the 2-D
  `(N, I)` uint32 index matrix that stacks, per position, the feature
  index blocks side by side (this is the table-lookup matrix a
  feature-table / PDB evaluation would consume).

The module exports `Feature`, `FeatureSet` (`__all__`, L53-54).

## Architecture

```
feature.py
├── Feature                       (L59)  @dataclass(init=False)
│   ├── Category(IntEnum)         (L73)  INTERCEPT=0, MOBILITY=1, PATTERN=2
│   ├── __new__   @validate_call (L82)   always raises RuntimeError (blocked)
│   ├── _create_empty (classmethod, L93) object.__new__ bypass, internal
│   ├── new_intercept    (classmethod, L101) const feature: 1/1, ref=None
│   ├── new_from_pattern (classmethod, L118) copies name/n_configurations/n_instances
│   └── new_from_mobility(classmethod, L138) same, from Mobility
└── FeatureSet                    (L156)
    ├── __init__    @validate_call (L176)  intercept category check;
    │                                       features list; n_instances sum; hash
    ├── print_summary @validate_call (L220)  name/hash + per-set + per-feature lines
    └── compute_indexes @validate_call (L248) (N, I) uint32 = hstack of blocks
```

Dependencies: `twolm.board` (PositionArray), `twolm.pattern`
(Pattern, PatternSet, Index, IndexArray), `twolm.mobility`
(Mobility, MobilitySet) — i.e. all three modules; feature.py is their
composition point and owns no board logic of its own.

### Construction — `Feature` (L59-154)

- `@dataclass(init=False)` with a `__new__` that unconditionally
  raises `RuntimeError` (L82-89): `Feature(...)` is impossible; the
  docstring/message say "use the Factory Method instead". The
  decorated `__new__` takes `*args, **kwargs` (Any) so pydantic passes
  validation through and the RuntimeError propagates — verified live
  (V7). `_create_empty` calls `object.__new__(cls)` to bypass it; the
  factories then assign every field, including `ref`.
- The three factories are strict `@validate_call`
  (arbitrary_types_allowed): `new_from_pattern("string")` →
  `pydantic.ValidationError` (V7); they copy `name`,
  `n_configurations`, `n_instances` from the source and keep the
  source in `ref` (repr=False, L71).
- Dataclass defaults: `__eq__` over ALL fields (including `ref`),
  auto `__repr__` without `ref`. The suite relies on the field-wise
  `__eq__` (`assertEqual(feature_set.intercept, self.intercept)`).
  Not frozen: fields are mutable — consistent with the factory design
  (created once, then read).
- With `from __future__ import annotations` (L28) all annotations are
  strings; `@validate_call` resolves them from module globals, so the
  `Mobility`/`Pattern`/`MobilitySet`/`PatternSet` imports (L42-45)
  are load-bearing for validation even though they appear "only" in
  annotations — do not drop them as unused.

### Construction — `FeatureSet.__init__` (L176-217)

1. `intercept` (a `Feature`) with a category other than
   `INTERCEPT` → `ValueError("Argument intercept is a feature having
   the wrong category ...")` (L185-187);
2. `features` is built in fixed order (L194-203): the intercept
   (if any), then one `Feature.new_from_mobility(m)` per mobility of
   `mset` (the set's **sorted (mask, amask)** order), then one
   `Feature.new_from_pattern(p)` per pattern of `pset` (the set's
   **sorted mask** order). Verified live (V4): for the 13-pattern +
   3-mobility fixtures the order is
   `[INTERCEPT, ALMC, LMC, DLMC, 2X5COR, XEDGE, R2, CORNER, R3,
   DIAG4, R4, DIAG5, CORE, RCT2X4, DIAG6, DIAG7, DIAG8]` — i.e. the
   child sets' sorted order, NOT the caller's insertion order;
3. `n_instances = Σ f.n_instances` over `features` (L205); for the
   standard fixtures: 1 (intercept) + 3 (mobilities, each 1) + 49
   (patterns: 2X5COR 8, XEDGE/R2/CORNER/R3/DIAG4/R4/DIAG5/DIAG6/DIAG7
   4 each, CORE 1, RCT2X4 2, DIAG8 2) = 53 (V2);
4. `hash = sha3_256` over `b''.join(chunks)` (L207-215) where
   `chunks` = `[b'INTERCEPT']` (if intercept) `+ [mset.hash as UTF-8]`
   (if mset) `+ [pset.hash as UTF-8]` (if pset). Note the hash is
   over the child sets' **hash strings** (transitively over their
   sorted mask contents), not over raw masks; the `name` is NOT part
   of the hash — consistent with the child sets. Re-implemented from
   scratch, all three literals reproduce (V1):
   mset `2e553593…208a94`, pset `ff97ce55…040ea`,
   feature `f5663932…b74167`.

The class docstring originally called it a "SHA256 hash" — it is
sha3_256 (R1, corrected D-038). The `__init__` docstring originally
said "with the given name and list of features" — there is no
features parameter (R3, corrected D-038).

### compute_indexes (L248-275) — column layout

`@validate_call`, `positions: PositionArray → IndexArray`.

```
I = Σ f.n_instances over features
N = len(positions)
N == 0 or I == 0  →  np.empty((N, I), dtype=Index)   (early edge return)
else  →  np.hstack of the active blocks, in order:
    intercept → zeros (N, 1)
    mset      → mset.compute_indexes(positions)          (N, #mobilities)
    pset      → pset.compute_principal_indexes(positions) (N, Σ n_instances)
```

- The intercept column is the constant 0 (a bias column;
  n_configurations = 1).
- **Column layout (verified, not documented — R2):** column 0 =
  intercept; then the mobility columns in the MobilitySet's sorted
  (mask, amask) order (one column each); then the pattern blocks in
  the PatternSet's sorted mask order, each pattern p expanded into
  `n_instances(p)` columns in the pattern's unique-mask first-seen
  slot order (the D8 instance order, instance 0 = the ro000 image,
  D-014 convention; each column is the orbit-group minimum of
  `2·idx_o + idx_m` over the anti-transformed frames —
  `PatternSet.compute_principal_indexes`, pattern.py L1149-1230).
  Live-verified for the EDGE + DIAG4 fixture (V5): the 3×10 matrix
  equals the pure-Python re-derivation column by column.
- Preconditions: the D-025 collision-free contract flows in through
  `pset.compute_principal_indexes` (caller's responsibility when a
  pset is present); the mobility block has no such precondition.
- The `IndexArray` return annotation applies the same
  BeforeValidator dtype check as in pattern.py/mobility.py —
  consistent convention.

### print_summary (L220-245)

Header line `FeatureSet: name = ..., length = ..., hash = ...`, then
intercept present/None, per-set name+hash lines, and one line per
feature `{i:02d} {category} {name:10s} {n_instances} {n_configurations:10,d}`.
`f.category` is an IntEnum: on Python 3.12 the f-string renders the
int value (`0`, `1`, `2`) — pinned by the suite goldens. `output:
Union[IO, io.StringIO] = sys.stdout`.

## Verified (this session, 2026-08-28)

Independent ground truth: pure-Python legal moves (8-ray), pure-Python
base-3 orbit-min reduction over the 8 anti-transformed frames,
from-scratch sha3_256 hashes. `twolm.board` (proven kernel,
193/0/12) used only for the D8 transforms/anti-transforms
(D-014 slot order) and `legal_moves`. `twolm.feature` is NOT imported
by the verification math (only for the live structural checks).
Script: `scratch/verify_feature.py` (untracked, per convention).

| # | fact | result |
|---|------|--------|
| V1 | all three hashes re-implemented from scratch: MobilitySet (3, sorted (mask,amask), 16 LE bytes), PatternSet (13, sorted mask, 8 LE bytes), FeatureSet (b'INTERCEPT' + hex strings) | all == pinned literals (2e553593…, ff97ce55…, f5663932…) |
| V2 | 13 pattern orbit sizes (pure-Python D8 orbits), mask-sorted order: [8,4,4,4,4,4,4,4,1,2,4,4,2] | == test golden list; Σ features n_instances = 53 |
| V3 | 3×10 compute_indexes golden re-derived in pure Python: intercept 0, LMC (pure legal moves == board.legal_moves), EDGE 4 principal columns, DIAG4 4 principal columns | all 3 rows == golden |
| V4 | live `features` order + categories: intercept, sorted mobilities (ALMC, LMC, DLMC), sorted patterns (2X5COR, XEDGE, R2, CORNER, R3, DIAG4, R4, DIAG5, CORE, RCT2X4, DIAG6, DIAG7, DIAG8) | as stated |
| V5 | live `compute_indexes` 3×10 matrix vs pure-Python matrix | identical; dtype uint32 |
| V6 | edge shapes: N=0 → (0, 10); I=0 → (3, 0); both → (0, 0); dtype uint32 in all | all match |
| V7 | factories' field values; `Feature()` → RuntimeError; wrong intercept category → ValueError ("wrong category"); 4 invalid argument types (None, list, str, int64 ndarray) → ValidationError | all match |
| V8 | full suite baseline | 13/0/1 GREEN |

## Real issues (candidates for fix, priority order)

_2026-08-28: all four approved by Roberto in one go and applied the
same day (D-038, single batch commit; doc/hygiene only, no behavior
change; suite 13/0/1 GREEN, verifier all green)._

- **R1 — FeatureSet class docstring, hash description (doc-only).
  DONE (D-038).**
  L164 says "A SHA256 hash of the intercept, mset, and pset
  attributes" — it is `hashlib.sha3_256` (L215), and the input is
  precisely: `b'INTERCEPT'` (if intercept present) followed by the
  child sets' hash **hex strings** (UTF-8) in the order mset, pset;
  the set `name` is excluded. Rewrite the line to state this
  construction (V1 ground truth).
- **R2 — compute_indexes column-layout contract (doc-only). DONE
  (D-038).** The
  "column layout" block above is verified but nowhere documented:
  column 0 = intercept; mobility columns in sorted (mask, amask)
  order; pattern blocks in sorted mask order, each pattern expanded
  into n_instances columns in the pattern's unique-mask first-seen
  (D8 instance) order. Add a "Column contract" paragraph to the
  `compute_indexes` docstring (and a pointer in the class docstring)
  — same treatment as mobility R2.
- **R3 — FeatureSet.__init__ docstring stale (doc-only). DONE
  (D-038).** L181-183:
  "with the given name and list of features" — the signature has
  (name, intercept, mset, pset); no features parameter. Rewrite with
  the actual parameters and a `Raises:` clause (ValueError, wrong
  intercept category).
- **R4 — dead imports (hygiene, code). DONE (D-038).** L30: `TypeAlias`, `List`,
  `Tuple`, `Annotated` are unused in code (`List`/`Tuple` appear only
  in docstring prose). Remove them from the `typing` import. (The
  `Mobility`/`Pattern` imports are load-bearing for
  `@validate_call` annotation resolution — keep.)

## Minor issues / inconsistencies

_Noted 2026-08-28; disposed one at a time per Roberto. M1 DONE
(D-039), M2 DONE (D-040), M3 left as-is (D-041, follow-up I-007),
M4 DONE (D-042). All four disposed._

- **M1 — dead empty-set guard in `compute_indexes`. DONE
  (D-039).** The pset branch of the active-blocks loop was
  `if self.pset and len(self.pset.patterns) > 0`, while the mset
  branch was a plain `if self.mset:`. An empty `PatternSet` is
  impossible (PatternSet fail-fast, D-033-era #17), so the
  `len(...) > 0` test was dead; an empty `MobilitySet` is legal
  (deliberate, mobility M3) and its `(N, 0)` block is handled
  correctly by `hstack`. Dead clause removed for symmetry;
  behaviour identical.
- **M2 — placeholder-less f-strings in `print_summary`. DONE
  (D-040).** L228/L230: `prt(f"  Intercept is present.")` /
  `"  Intercept is None."` — the
  `f` prefix was unused (the mset/pset lines below do have
  placeholders). Cosmetic; the `f` prefixes removed, output
  identical.
- **M3 — no column labelling helper on FeatureSet (observation
  only). Left as-is (D-041, option a per Roberto; follow-up
  I-007).** Unlike `MobilitySet.names`/`masks` (D-024 style),
  `FeatureSet` offers no way to map a matrix column back to its
  feature name (callers must reconstruct it from
  `intercept`/`mset`/`pset`). It is an engine-side need, not a
  module requirement; the helper design (each pattern occupies
  n_instances D8-instance columns) is deferred until the pipeline
  module that labels columns arrives.
- **M4 — Feature.__new__ docstring grammar. DONE (D-042).**
  L84-85: "Blocks the client to create new instances of feature
  via the Feature() call." — minor phrasing; rewritten to "Blocks
  direct instantiation of Feature: calling Feature() always raises
  RuntimeError. Use the factory methods instead (e.g.
  Feature.new_from_pattern())."

## Conventions to respect in any new work on this file

- Board/D8 layout per D-013/D-014 (verified): bit =
  8×(row−1)+(col−1); A1 = bit 0 … H8 = bit 63; slot order
  [ro000, ro090, ro180, ro270, fvert, fh1a8, fhori, fa1h8] (regular)
  with slots 1/3 inverted for anti-transformations.
- Child-set ordering is load-bearing: `features` (and therefore
  `compute_indexes` columns) follow the child sets' sorted storage,
  never caller insertion order.
- The `Feature` dataclass `__eq__` includes `ref`; equality of two
  features built from equal (but distinct) Pattern/Mobility objects
  holds because those are dataclasses with field-wise eq — do not
  weaken without a decision.
- `from __future__ import annotations`: annotations resolve through
  module globals at `@validate_call` decoration time; keep the
  `Mobility`/`Pattern`/set imports in scope.
- Python 3.12 IntEnum str semantics: f-strings render `Category`
  members as bare ints — print goldens depend on this.
- Doc mirror (D-007): this file documents src/twolm/feature.py.

## Verdict

A **correct** composition module: no board logic of its own, all
behaviour delegated to the three proven modules, and every derived
quantity (hash, n_instances, the 2-D index matrix, the column
layout) re-derives exactly against independent ground truth
(V1–V7, zero mismatches — including the full 3×10 golden matrix and
all three pinned hashes). It is the pipeline's first integration
point: after this, `FeatureSet.compute_indexes` is the natural
producer of evaluation-table input. Module-side gaps are documentary
(R1–R3) plus dead imports (R4); no real logic defect found.

Test file preliminary observations (for the dedicated
`docs/src/twolm/test/test_feature.md` analysis, next step): a dead
`if False:` block in `TestFeatureSetComputeIndexes.test_compute_indexes`
that references `position_print` (never imported — would NameError if
made live); header grammar ("How to use the unit tests feature
module.") and the same "environmeant" typo as test_board (reported
there, Roberto's call); dead imports (`npt`, `nptest`, `Callable`,
`TypeAlias`, `List`, bare `pydantic`); `import time` with trailing
spaces (same cosmetic as test_mobility, left as-is there); no
`__repr__` golden for the dataclass `Feature`; partial-None
constructions untested (intercept-only, mset-only, pset-only — only
all-None is covered); `test_print_summary` uses `assertIn` on 8 lines
only (no full golden).
