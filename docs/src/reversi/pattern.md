# reversi/pattern.py
Pattern recognition for Reversi PDB: the D8 orbit of a pattern mask
(instances, stabilizer, the induced permutations on its squares), a
PEXT-style packing of the 64-bit board into S contiguous bits, the
base-3 encoding of every legal configuration (3^S states, uint32),
and the principal configuration index under the induced symmetries.
PatternSet computes all principal indexes for N positions in one
fused Numba pipeline; PatternType is the closed table of shapes. No
search, no PDB storage, no disk I/O except the CSV writer.
> State: D-112 · 66c3588 · 2026-09-06 · suite 65/0/3

## API

| family | name | contract |
|---|---|---|
| Types | `Index` | type alias `np.uint32` — a base-3 configuration index (safe because S ≤ 18) |
| Types | `IndexArray` | annotated ndarray; the BeforeValidator requires uint32 for ndarrays, scalars pass through |
| Pattern | `Pattern(name: str, mask: Bitboard)` | strict constructor (no coercion); ValueError: empty mask, > 18 squares, non-principal mask (the error lists all 8 transformed masks) |
| Pattern | construction attributes | `n_squares`, `n_configurations = 3^S`, `tmasks` (8, canonical slot order), `squares`/`snames` (ascending board order), `unique_masks`, `mask_to_index` (first-seen slot), `mask_indexes`, `unique_mask_indexes`, `n_instances = \|Orb\|`, `n_stabilizers = 8/\|Orb\|`, `trans_fs`/`anti_trans_fs` (length n_instances, first-seen slots), `squares_t`/`snames_t`/`squares_ts`/`snames_ts` (per-instance; `_ts` sorted), `fingerprint`, `type`, `powers_3`/`bit_shifts`, `p_masks`/`u_masks`/`p_shifts` (the lazy run-based pack plan), `principal_index_dict` / `principal_index_count` (lazy), `n_invariant_configs`/`n_unique_configs` (Burnside, D-032), `symmetry_fs`/`anti_symmetry_fs`, `unique_symmetric_instance_indexes` |
| Pattern | `compute_indexes_on_position(pos) -> NDArray[Index]` | the anti-transform → pack → base-3 pipeline; scalar → (n_instances,), (N,) → (N, n_instances) |
| Pattern | `compute_principal_index_dict() -> None` | populates the lazy dict {config → min over its stabilizer orbit} + the unique principal indexes and their count |
| Pattern | `convert_to_principal_index(index) -> IndexArray` | the dict lookup (computes the dict on first use) |
| Pattern | `_pack_bb(bb)` / `_unpack_bb(packed)` | PEXT-style compress / PDEP-style expand; dual scalar/array |
| Pattern | `print(output)` / `mdp_record() -> str` / `mdp_csv_file(patterns, filename)` | the 2-D diagram; the CSV record line; the classmethod CSV writer |
| PatternType | the 12 members (`NONE`, `TYPE_0`…`TYPE_9`, `TYPE_3D`, `TYPE_7D`) + `from_fingerprint(fp) -> Optional[PatternType]` | the closed table of (type, sample_mask, sample_name, level, n_instances, n_stabilizers); a pattern whose fingerprint is not in the table raises ValueError at construction; unknown fp → None |
| Data | `sample_pattern_data` | 29 (name, python-int mask) tuples (the masks are python ints — callers wrap with `Bitboard(...)`); used to generate the mdp.csv for the LaTeX document |
| PatternSet | `PatternSet(name: str, patterns: List[Pattern])` | strict; ValueError: empty list, duplicate names, duplicate masks; stored sorted by mask; `hash` = sha3_256 of the concatenated mask bytes (little-endian) |
| PatternSet | `names` / `masks` | `@property`: List[str] / uint64 ndarray over the sorted patterns |
| PatternSet | `__repr__` | one-line summary: name, the set hash, the patterns in mask-sorted order via `Pattern.__repr__` (D-112 M1) |
| PatternSet | `print_summary(output)` / `print(output)` | text rendering |
| PatternSet | `compute_principal_indexes(positions) -> IndexArray` | the fused Numba pipeline; (N,) PositionArray → (N, Σ n_instances); precondition: the positions are collision-free (the caller checks, e.g. `board.position_check_collisions`) |

## Architecture

```
board.py: D8 transforms / anti tables, bitboards, Position
    |
PatternType (Enum, 12 members)
    fingerprint -> {type, sample_mask, sample_name, level, n_instances, n_stabilizers}
    |
Pattern (one principal mask)
    orbit: tmasks(8) -> unique_masks (first-seen order);
        n_stabilizers = 8 / n_instances
    symmetries: unique_symmetric_instance_indexes + symmetry_fs /
        anti_symmetry_fs; fingerprint (I/S/T) -> PatternType
    Burnside: n_invariant_configs / n_unique_configs (D-032)
    pack plan: p_masks / u_masks / p_shifts (runs of set bits)
    config indexing: powers_3, bit_shifts; principal_index_dict
    |
numba kernels (njit parallel=True, cache=True): pack, unpack,
    computes_indexes, compute_principal_indexes (fused)
    |
PatternSet (name + mask-sorted patterns + sha3_256 hash)
    compute_principal_indexes: (N,) PositionArray -> (N, total_cols) IndexArray
```

- **Principal mask rule (D-020)** — a mask is principal iff it is the
  numerically lowest mask among its 8 D8 transforms: a mask is a
  64-bit integer, so the orbit minimum is a unique representative.
  The constructor rejects the rest and names the offending slot.
- **D8 slot order (D-014) is load-bearing** — `tmasks[i]` = T_i(mask)
  in the canonical order; the anti-table slots hold inverses; the
  instance order is the first-seen order over slots
  (`dict.fromkeys`), so instance 0 is always the ro000 image (= the
  principal mask itself). Reordering the slots breaks everything
  silently.
- **PEXT-style packing** — the S pattern squares compress to S
  contiguous bits; packed bit k ↔ the k-th square of `squares`
  (ascending board order). The plan's "planes" are runs of
  consecutive set bits in the mask (not 8-bit planes); single-run
  patterns take a fast path.
- **Base-3 configuration indexing** — digit k ∈ {0 empty, 1 mover, 2
  opponent}; index = Σ digit_k·3^k (uint32). The principal index =
  the min over the configuration's orbit under the permutations the
  stabilizer induces on the pattern squares — a configuration-level
  canonicalization, distinct from the instance-level one of the mask.
- **Burnside counts (D-032)** — `n_invariant_configs` =
  (1/8)·Σ_g |X^g| over the 8 transformations; `n_unique_configs` =
  (n_invariant_configs + (n_stabilizers−1)·3^F)/8, F = the number of
  squares fixed by every symmetry function.
- **Pydantic + Numba layering** — every public method is
  `@validate_call` (the constructors `strict`); hot paths are
  `njit(parallel=True, cache=True)` (no `fastmath` — meaningless for
  integer ops); the construction-time (cold) path calls the
  pydantic-wrapped scalar functions directly.
- **Closed type table** — a pattern whose computed fingerprint is not
  in the PatternType table raises ValueError at construction; the 12
  types are the closed set of supported shapes.
- **The fused PatternSet kernel** — (1) `bitboard_anti_transformations`
  on both player bitboards (N, 8); (2) transpose to (8, N) for
  C-contiguous per-slot gathers; (3) per-pattern block: gather the
  `unique_mask_indexes` rows, `_numba_pack_bb_kernel` →
  `_numba_computes_indexes_kernel`; (4) per instance, the block min
  over the `argsort(mask_indexes)` coset slots (=
  `compute_principal_index_dict`'s quantity) into the output
  columns. Output (N, total_cols), `total_cols = Σ n_instances(p)`.
- **Output column layout (implicit)** — concatenation in the set's
  mask-sorted order; pattern i contributes `n_instances(i)` columns
  in first-seen order. No method exposes the offsets — a caller
  reassociating columns recomputes them from the patterns.
- **Platform: little-endian only** (D-022) — the D8 bit tricks, the
  pack/unpack, and the set hash (native-order `mask.tobytes()`) are
  verified on little-endian only; no portability work is planned.

## Verified invariants

- The principal-mask rule (non-principal rejected; the error lists the
  full orbit and names the offending slot) —
  `test_pattern::TestPattern` (the non-principal and the
  non-minimum-orbit tests).
- The constructor guards (both args strict: no int mask, no numpy
  string name; empty mask; > 18 squares) and the `__repr__`/`__str__`
  goldens — `test_pattern::TestPattern`.
- The orbit attributes and the D8 round-trips: the exact 8-slot
  `tmasks`, ascending `squares`/`snames`, the per-instance
  `snames_t`, `n_instances`/`n_stabilizers`/`n_configurations`, and
  the `trans_fs`/`anti_trans_fs` round-trip (applying the anti-table
  functions to the transformed masks recovers the original) —
  `test_pattern::TestPattern.test_init_attributes`.
- The run-based pack plan and the pack/unpack round-trip against 18
  reference bitboards (empty, full, r1-r8, c1-c8), scalar and
  vectorized, covering the single-run fast path (EDGE) and the
  multi-run plan (ELLE, R2-R4, CORNER, DIAG8, FOURC) —
  `test_pattern::TestPatternPack`.
- The symmetry structure of 29 patterns: the exact `symmetry_fs` list
  for each, from the trivial orbit (ELLE, DOTA1: 8 instances / 1
  stabilizer) to the full-stabilizer patterns (CORE, FOURC: 1
  instance / 8) — `test_pattern::TestPatternSymmetries`
  (the invariance test).
- The Burnside counts (D-032): golden `n_invariant_configs` /
  `n_unique_configs` for all 29 sample patterns (ground truth: full
  3^S enumeration + `principal_index_count`; e.g. EDGE 81 / 3321 =
  (6561+81)/2) and the general invariants (1 ≤ n_invariant ≤
  n_unique ≤ 3^S, with equality to 3^S when the symmetry is trivial)
  — `test_pattern::TestPatternSymmetries` (the Burnside golden and
  invariant tests).
- The 6561-entry EDGE principal dictionary, pinned with the full
  non-circular specification (`dict[c] = min(c, flip(c))`, where flip
  reverses the base-3 digits), its length, the unique count 3321, and
  hand-derived spot values —
  `test_pattern::TestPatternComputePrincipalIndexDict` (the edge
  test); CORE pins its full 81-entry dictionary, the small patterns
  are spot-checked against hand-derived values.
- The fused PatternSet pipeline, pinned with exact golden outputs:
  the 3-pattern set (single record and multiple positions), the
  13-pattern set (49 hand-derived principal indexes, the column
  attribution, the mask-sorted pattern order), and a
  4-distinct-position test that guards row-mixing in the kernel (the
  EDGE per-column stabilizer-coset min) —
  `test_pattern::TestPatternSetComputePrincipalIndexes`.
- The PatternType table: the `from_fingerprint` round-trip for all 12
  members, unknown fingerprint → None, and the data fields
  (sample mask/name, level, orbit/stabilizer counts) —
  `test_pattern::TestPatternType`.
- The PatternSet guards (empty list, duplicate names, duplicate
  masks, strict element types), the mask-sorted storage, the
  `names`/`masks` properties, the sha3_256 hash, and the `__repr__`
  golden (D-112 M1) — `test_pattern::TestPatternSet`.
- The MDP output: the `mdp_record` golden lines (ELLE, EDGE, SNAKE,
  CORE, DIAG8), the `mdp_csv_file` type errors, the written content
  and the empty-list case — `test_pattern::TestPatternMdpRecord`,
  `test_pattern::TestPatternMdpCsvFile`.
- The renderings: the 2-D `print` diagram and the set
  `print`/`print_summary` — `test_pattern::TestPatternPrint`,
  `test_pattern::TestPatternSet`.
- The D8 group structure on the transformation functions (the Cayley
  table: identity, associativity, multiple inputs, the sample
  patterns) — `test_pattern::TestTransformationsCayleyTable`.

## Open issues

None.

## Conventions

- The D8 slot order (D-014, notes/naming.md) is load-bearing — never
  reorder or rename the slots or the tables.
- A mask is a 64-bit integer — the principal is the orbit minimum
  (D-020); keep the check strict and the error informative.
- The uint32 base-3 index is safe only while S ≤ 18
  (`MAX_NUMBER_OF_SQUARES_FOR_PATTERN`) — the bound is conservative
  (S = 19 still fits: (3^20−3)/2 < 2^32).
- `n_squares` is `np.uint8` — cast to `int` before exponentiating
  (the numpy scalar wraps: 3**8 → 161); the production code already
  casts where needed (e.g. `compute_principal_index_dict`).
- Little-endian only (D-022): the set hash uses native-order
  `tobytes()`; no endianness portability work.
- The sample-data masks are python ints — callers wrap with
  `Bitboard(...)`.
- New public methods: `@validate_call` (strict for the constructors);
  hot loops `njit(parallel=True, cache=True)` — no `fastmath`.

## Integration

- Consumes `board.py` (the D8 transforms + anti tables, the
  bitboard utils, `Position`).
- Consumed by: `feature.py`, `wrk_features.py` (the FEATURES
  pipeline level), `mobility.py`, `model_weights.py`,
  `hlp_indexes.py`.
- Not a pipeline level itself: a domain module used BY the workers.
