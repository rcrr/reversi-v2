# pattern.py analysis

_Analyzed: 2026-08-27 (session 1, review only). Source: `src/twolm/pattern.py`
(package `twolm`), GPL-3. Status: analyzed in depth; **all real issues
resolved** — R1 (D-020, code fix + regression test), R2-R7 (D-021,
docstring/hygiene fixes, code behavior untouched), R8 (D-022, closed by
decision: little-endian-only platform note, no code change). Test suite:
`src/twolm/test/test_pattern.py` — GREEN: 50 tests, 0 failures, 3 skipped
(PERF=1 gate). The test file's content is out of scope (dedicated session
planned)._

## What it is
Pattern recognition for Reversi PDB. A **Pattern** is a fixed set of squares
(`mask`, a principal bitboard); the module derives its D8 orbit
(**instances**), its internal symmetries (**stabilizer** and the permutations
it induces on the pattern squares), a PEXT-style packing of the 64-bit board
into S contiguous bits, a base-3 encoding of every legal configuration on
those S squares (3^S states, uint32), and the canonical **principal**
configuration index obtained by quotienting configurations under the pattern's
induced symmetries. **PatternSet** groups patterns and computes all principal
indexes for N positions in one fused Numba pipeline. **PatternType** is a
closed table of 11 pattern types classified by a transformation fingerprint.

Depends on `board.py` (D8 transforms + anti tables, bitboards, positions).
No search, no PDB storage, no disk I/O except the optional CSV writer
(`Pattern.mdp_csv_file`).

## Platform assumption: little-endian only
**The entire engine is tested on little-endian processors only.** Every
function that performs bit or byte manipulation — and in this engine there
are many (D8 bitboard transforms, PEXT-style packing, base-3 encoding,
set-hash serialization via native-order `mask.tobytes()`) — is **untested
on non-little-endian platforms**; behavior there is not guaranteed. User
decision (D-022, 2026-08-27): the legacy engine is written and validated
for little-endian; no endianness portability work is planned. R8
(endianness-dependent set hash) was therefore closed by documenting this
assumption instead of changing the code.

## Architecture
Layers (bottom → top):

```
board.py: D8 transforms / anti tables, bitboards, Position
    |
PatternType (Enum, 12 members; L82)
    fingerprint -> {type, sample_mask, sample_name, level, n_instances, n_stabilizers}
    |
Pattern (one principal mask; L144)
    orbit: tmasks(8) -> unique_masks (instances); n_stabilizers = 8/n_instances
    induced symmetries: unique_symmetric_instance_indexes + symmetry_fs / anti_symmetry_fs
    fingerprint (I/S/T markers) -> PatternType
    Burnside counts: n_invariant_configs / n_unique_configs (D-032)
    pack plan: p_masks / u_masks / p_shifts (runs of consecutive set bits)
    config indexing: powers_3, bit_shifts; principal_index_dict (lazy)
    |
numba kernels (njit cache=True): _numba_pack_bb (L785), _numba_unpack_bb (L818),
    _numba_computes_indexes_kernel (L849), _numba_compute_principal_indexes_kernel (L1115, fused)
    |
PatternSet (L944: name + patterns + sha3_256 hash, mask-sorted)
    compute_principal_indexes: (N,) PositionArray -> (N, total_cols) IndexArray
```

Cross-cutting design decisions:
1. **Principal mask rule (D-020)** — a mask is principal iff it is the
   numerically lowest mask among its 8 D8 transforms: a mask is a 64-bit
   integer (a bijection with 0..2^64−1), so the orbit minimum is a unique
   representative. `Pattern.__init__` raises `ValueError` otherwise
   (L314-339, listing all 8 transformed masks).
2. **D8 slot order (D-014) is load-bearing.** `tmasks[i]` = T_i(mask) in the
   canonical slot order; anti-table slots hold inverses (slot s = T_s^{-1});
   instance order is the *first-seen* order over slots (`dict.fromkeys`), so
   instance 0 is always the ro000 image (= the principal mask itself).
   Reordering the slots would break everything silently.
3. **PEXT-style packing** — the S pattern squares are compressed to S
   contiguous bits; packed bit k ↔ the k-th square of `squares` (ascending
   board order). The plan's "planes" are *runs* of consecutive set bits in
   the mask (not 8-bit planes); single-run patterns take a fast path.
4. **Base-3 configuration indexing** — digit k ∈ {0 empty, 1 mover, 2
   opponent}; index = Σ digit_k·3^k (uint32). The **principal** index = min
   over the orbit of a configuration under the permutations induced by the
   stabilizer on the pattern squares — a *configuration-level*
   canonicalization, distinct from the instance-level canonicalization of
   the mask.
5. **Pydantic + Numba layering** — every public method is `@validate_call`
   (exception: `Pattern.__init__` hand-checks with `isinstance`,
   L287-290); hot paths are Numba (`cache=True, parallel=True,
   fastmath=True`); the construction-time (cold) path calls the
   pydantic-wrapped scalar functions directly.
6. **Closed type table** — a pattern whose computed fingerprint is not in
   the PatternType table raises `ValueError` at construction (L471-476);
   the 12 types are the closed set of supported pattern shapes.

## Pattern class (L144)

Plain Python class (not a pydantic model). One instance = one principal mask.

### Construction — `__init__(name: str, mask: Bitboard)` (L274-495)
- Hand validation: `isinstance(name, str)`, `isinstance(mask, Bitboard)`
  (L287-290) — the only public entry in the module without
  `@validate_call`. A Python `int` mask is **rejected** (a scalar
  `np.uint64` instance is required); numpy string scalars are rejected for
  `name`.
- `n_squares = bitboard_count(mask)` (L294), hard limit
  `MAX_NUMBER_OF_SQUARE_FOR_PATTERN = 18` (L78; enforced L295-296). Rationale
  per the L77 comment: the base-3 packing index must fit uint32 —
  conservative, since `(3^20−3)/2 < 2^32` means S=19 still fits.
- `tmasks` (L298) = `bitboard_transformations([mask])[0]` — the 8 transforms
  in canonical D8 slot order.
- Principal check (L314-339): nested `@validate_call` closure **with no
  arguments** (the decorator validates nothing) scans t1..t7 for a
  *numerically lower* mask; the first offender is reported (D-020).
- `squares`/`snames` (L299-300) = `bitboard_to_square_list(mask)[::-1]` →
  **ascending** square index (A1 first). The class docstring says "sorted in
  descending priority" (L160) — wrong (R3).
- `unique_masks` / `mask_to_index` / `mask_indexes` (L301-306):
  `mask_to_index` is built with a **reversed** enumerate (L302) so it maps
  each distinct transformed mask to its **first-seen** slot index (a forward
  comprehension would give the last); `unique_mask_indexes` =
  `dict.fromkeys(mask_indexes)` = first-seen order.
- Orbit numbers (L307-310): `n_instances = len(unique_masks)`,
  `n_stabilizers = 8 // n_instances`; `trans_fs` / `anti_trans_fs`
  (L311-312) = one pydantic-wrapped function per distinct instance (length
  = n_instances, **not** 8), taken from the first-seen slots.
- `_compute_transformed_cells()` (L497) fills `squares_t` / `snames_t` /
  `squares_ts` / `snames_ts` (docstring L201-211): per-instance square data;
  the `_ts` variants are sorted per instance — used for the *set* equality
  test in the fingerprint.
- Fingerprint + type (L443-476): for i = 1..7, instance i is compared with
  the *earliest* j < i having the matching property: **I**{j} = same
  *ordered* square sequence; **S**{j} = same square *set* (permutation);
  **T**{i} = new instance set. `PatternType.from_fingerprint` (lazy
  class-level `_lookup` cache, L136-140); unknown fingerprint → `ValueError`
  (L471-476) listing all 11 known fingerprints.
- `powers_3` / `bit_shifts` (L478-480) — the L478 comment names a
  non-existent method `compute_indexes_on_board` (R7; the real one is
  `compute_indexes_on_position`, L653).
- `principal_index_dict` / `principal_indexes` / `principal_index_count`
  (L487-490) stay **None until first use** (lazy; computed by
  `compute_principal_index_dict`, L697).
- `_check_invariances()` (L536, invoked from `__init__`): verifies that each
  symmetry function preserves the mask, that trans/anti are consistent
  inverses, and the mask-index bookkeeping. Its docstring (L538) also
  claims "pack/unpack logic" checks — **none exist** (minor issue).

### Symmetries (induced permutations)
For each distinct non-identity permutation the stabilizer induces on the
pattern's squares, one D8 slot is recorded:
`unique_symmetric_instance_indexes` (built with a pos_map/dedup over the
stabilizer elements) plus the matching `symmetry_fs` / `anti_symmetry_fs`
(the anti-inverse of each symmetry function). Semantically this is the
stabilizer *modulo its kernel* — the set of induced permutations (the
pattern's "automorphism group" in quotient form).

The class docstring claims `len(unique_symmetric_instance_indexes) =
n_stabilizers - 1` (L184) — **false**: DOTA1 (1 square) has
n_stabilizers = 2 (ro000 and fa1h8 both fix A1) but both induce the
identity permutation on its single square, so the list is empty (verified;
R2 below). The correct statement: the count is the number of distinct
non-identity permutations induced by the stabilizer; it equals
`n_stabilizers − 1` only when the pattern's squares separate all
stabilizer elements.

**Burnside counts (D-032).** The constructor (`_compute_symmetry_burnside_counts`)
computes two `int` attributes from this induced group
G′ = {id} ∪ {distinct non-identity induced permutations}
(|G′| = 1 + len(symmetry_fs)):
- `n_invariant_configs = 3^B`, B = number of G′-orbits on the S squares
  (a configuration is G′-invariant iff it is constant on each orbit);
- `n_unique_configs = (1/|G′|) · Σ_{g∈G′} 3^{c(g)}` (Burnside on the 3^S
  configurations; c(g) = number of cycles of g) — equals
  `principal_index_count` after `compute_principal_index_dict()`, but
  obtained in O(S) instead of O(3^S).
Both were verified against independent ground truth on all 29 sample
patterns before implementation (n_invariant: full enumeration of the 3^S
configurations; n_unique: the production principal dict): EDGE 81/3321,
CORE 3/21, DOTA1 3/3, 2X6COR 531441/531441. Golden:
`test_burnside_counts_golden` + invariants `test_burnside_counts_invariants`
(1 ≤ n_invariant_configs ≤ n_unique_configs ≤ n_configurations; equality
with 3^S when symmetry_fs is empty).

### Fingerprint → PatternType
- Markers: t_i vs the earliest j < i with the matching property; I beats S.
  Example DOTA1 → (I0, T1, T2, T3, I1, I2, I3, **I0**): t7 = fa1h8 fixes A1
  pointwise, so its 1-square *sequence* equals t0's → "I0", not "S0".
- The 12-member table (L82-130): TYPE_0..TYPE_9 + TYPE_3D (DOTA1) +
  TYPE_7D (DIAG8). Data fields: `type` (string "0".."9"/"3D"/"7D"),
  `sample_mask`, `sample_name`, `level` (metadata 1..8, carried to
  CSV/LaTeX export), `n_instances`, `n_stabilizers`. The table's
  n_instances/n_stabilizers agree with the computed values of the sample
  patterns (DOTA1/EDGE/CORE verified directly; the rest implied by the
  suite's fingerprint matches) — but nothing cross-checks them in code.
- The 29 `sample_pattern_data` patterns collapse to 12 types (all of
  them — verified live 2026-08-28): e.g. EDGE
  (row 1) and R2 (row 2) have *identical* fingerprints → type 2. A type
  classifies the orbit shape, not the position.

### Packing (PEXT-style)
`_precompute_pack_unpack_plans` (L342, nested): walks the mask; each *run*
of consecutive set bits becomes one plane: `p_masks` (board-domain block
mask), `p_shifts` (start_source − dest_pos, ≥ 0), `u_masks` (expansion).
EDGE (row 1, one 8-run) → p_masks [0xFF], p_shifts [0] (verified). CORE
(central 4 = bits 27,28,35,36: two 2-runs) → 2 planes, which exercises the
multi-plane OR branch of the kernel (covered by the PatternSet check below).
`_pack_bb(pos)` (L610) / `_unpack_bb(index)` (L631), dual scalar/array,
implement the plan via `_numba_pack_bb_kernel` / `_numba_unpack_bb_kernel`:
per plane `extracted = (bb & p_mask) >> p_shift`, OR-folded into the
destination (single-plane fast path skips the fold loop).

### Configuration indexing and principal indexes
- `compute_indexes_on_position(pos)` (L653), dual scalar/array:
  1. `bitboard_anti_transformations([pos])` → (N,8) board-domain positions;
     slot s = T_s^{-1}(pos) — pre-transforming, so packing instance s reads
     the configuration straight in canonical slot frame.
  2. Slice `[:, unique_mask_indexes]`, pack (m, o) per instance, base-3
     index per instance (NO principal min here — raw per-instance
     configuration indexes).
  Scalar input → 1-D (n_instances,) uint32.
- `compute_principal_index_dict()` (L697): enumerates **all** 3^S packed
  configurations (digits → (m,o) via `_compute_mover_opponent_by_index_value`,
  L711), applies `[ro000] + symmetry_fs` (L704) and repacks
  (`_compute_indexes_on_ss_packed_tensor`, L721: np.stack + matmul with
  powers_3 + `(idxs[0] + 2*idxs[1]).astype(uint32)`);
  `principal_index_dict = min over axis 1` (L765) — each configuration maps
  to the minimum index in its symmetry orbit; `principal_indexes =
  np.unique(...)`, `principal_index_count` (L766-767). Memory: ~N·3^S
  uint32 — S=18 ≈ 387 M rows → realistic only for small patterns.
- `convert_to_principal_index(index: IndexArray)` (L772): array-only
  fancy-index into the lazily computed dict.
- **No mover/opponent collision check** anywhere in this module: a square
  with both bits set yields digit 3 and silently produces garbage indexes.
  Callers must pass legal positions (board.py provides
  `position_check_collisions`).

### Verified (this session, 2026-08-27)
1. **EDGE** (0xFF): fingerprint [I0,T1,T2,T3,S0,S1,S2,S3] = the TYPE_2
   table, and matches hand derivation from the D-014 transform definitions
   (fvert = left-right mirror, fh1a8, …). n_instances = 4, n_stabilizers =
   2, stabilizer {ro000, fvert}; mask_indexes [0,1,2,3,0,1,2,3];
   unique_mask_indexes [0,1,2,3]; unique_symmetric_instance_indexes [4]
   (fvert — the only non-identity induced permutation, 4 transpositions);
   pack plan [0xFF]/[0]; type 2.
2. **R2** (row 2, 0xFF00): fingerprint identical to EDGE → same type 2.
3. **DOTA1** (A1, 0x1): fingerprint [I0,T1,T2,T3,I1,I2,I3,I0] = TYPE_3D
   table; n_instances = 4, n_stabilizers = 2, unique_symmetric_instance_
   indexes = [] — the counterexample to the L184 claim.
4. **CORE** (0x1818000000 = d4,e4,d5,e5): 1 instance, 8 stabilizers,
   fingerprint (I0, S0×7) = TYPE_9 — ro090 cycles the central 4
   (d4→e4→e5→d5→d4), so all 8 images are the same *set*, only t0 keeps the
   *order*.
5. **Non-principal rejection**: `Pattern("BAD", 0xFF00000000000000)` (row 8)
   → ValueError listing all 8 transformed masks (principal is #2 = row 1).
6. **Principal canonicalization, EDGE**: `principal_index_dict` identical to
   a brute-force min over `{id} ∪ symmetry_fs` on all 6561 configurations;
   `principal_index_count` = 3321 = (6561 + 81)/2 — exactly Burnside's
   lemma for the induced C2 (81 configurations fixed by the fvert
   transposition): the symmetry reduction is mathematically exact, and the
   fused-kernel per-group min (PatternSet section) computes the same
   quantity.
7. `n_instances × n_stabilizers = 8` holds for every pattern observed
   (EDGE 4×2, DOTA1 4×2, CORE 1×8, corners+a2 8×1).
8. **Scalar path**: EDGE `compute_indexes_on_position` on one position →
   shape (4,) uint32; `convert_to_principal_index` on it → 4 principal
   values consistent with the dict.

### Issues (Pattern) → consolidated list below
R1 (principal non-uniqueness), R2 (false L184 invariant), R3 (L160
"descending priority"), R7 (stale L478 comment), plus minors (L296
"n_square" message; "patetrn" typos L188/L211; "A dictionary" wording for
the ndarray L233; `@validate_call` inconsistency; the reversed-enumerate
`mask_to_index` idiom; `_check_invariances` docstring over-claim;
`fastmath` on integer kernels; `Bitboard`/`np.uint64` return surface).

## PatternSet class (L944)

A named collection of Patterns with a fused vectorized pipeline.

### Construction — `__init__(name: str, patterns: List[Pattern])` (L963)
- `@validate_call` (arbitrary_types_allowed): **both arguments required**
  (no defaults — one positional arg binds to `name` and fails validation;
  `patterns=[…]` without `name` → "Missing required argument").
- Duplicate *names* → ValueError (L977-979) — note: NOT listed in the
  `Raises:` block of the docstring (L971-974).
- Duplicate *masks* → ValueError (L981-984) — catches identical mask values
  only, not distinct orbit-equivalent masks (see R1: two "principal" masks
  of the same orbit could both enter a set).
- Patterns are sorted by mask value (L987) — this order defines the
  pipeline's column layout (below).
- `hash` (L990-991) = `sha3_256` over the `tobytes()` of the sorted masks:
  the docstring (L953) says "SHA256" (R4), and `tobytes()` is native-endian
  so the value is endianness-dependent (R8).

### API
- `names` / `masks`: properties (attribute-style, derived from `patterns`),
  next to the `name`/`patterns`/`hash` attributes. (Converted from methods
  in minor #15, D-024.)
- `print_summary()` / `print()` (L1014/L1025): `@validate_call`, IO default
  stdout.
- `compute_principal_indexes(positions: PositionArray)` (L1034): **array
  only** (no scalar path); the main pipeline:
  1. `bitboard_anti_transformations` on the raw mover and opponent arrays
     (L1046-1047) → two (N,8) bitboard grids, slot s = T_s^{-1} — computed
     **once for the whole set**, shared by all patterns.
  2. Layout extraction (L1049-1092): `S_max`/`P_max` via `max()` — an
     **empty set crashes** ("max() arg is an empty sequence"); per-pattern
     plan arrays: `n_squares_arr`, `bit_shifts_matrix (L,S_max)`,
     `idx_sort_matrix (L,8) = argsort(mask_indexes)`, `n_groups_arr`,
     `group_size_arr = 8 // n_groups`, `col_offsets`, and the 3-D
     `pack_masks_3d` / `pack_shifts_3d` stacked from each pattern's
     `pack_plan`. `n_groups = len(np.unique(mask_indexes))` = n_instances,
     and `n_groups` divides 8 (orbit–stabilizer), so `group_size` is exact.
  3. Fused `_numba_compute_principal_indexes_kernel` (L1115, `njit
     parallel=True, cache=True, fastmath=True`), per position n (prange)
     and pattern i:
     - for each of the 8 slots s: inline multi-plane pack of
       `m_atrxs[n,s]`/`o_atrxs[n,s]` (OR-fold, L1167-1171), then the base-3
       sum per bit (L1177-1185), `local_symmetry_indexes[s] = 2·idx_o +
       idx_m` (uint32 throughout; uint32 is safe because S ≤ 18).
     - for each group g: min over the `group_size` slots selected by
       `idx_sort_matrix[i, g·group_size … + group_size]` (L1190-1201) and
       write `out[n, col_offset + g]`. `argsort(mask_indexes)` makes the
       slots of each instance contiguous, so that block is exactly the
       stabilizer coset of the instance — the block min is the
       **principal index** of that instance, i.e. the same quantity
       `Pattern.compute_principal_index_dict` computes per pattern.
  4. Returns (N, total_cols) uint32 with `total_cols = Σ_p n_instances(p)`.

### Output column layout (implicit)
Concatenation in the set's mask-sorted order: pattern i contributes
`n_instances(i)` columns in canonical instance order (first-seen D8 slot,
instance 0 = ro000 image). No method exposes the column offsets — a caller
reassociating columns must recompute them from the patterns. (Design note.)

### Verified (this session, 2026-08-27)
1. Constructor contract: both args required; the "name missing" /
   "patterns missing" pydantic errors behave as the code implies.
2. Set (DOTA1, EDGE, CORE) sorts by mask to [DOTA1, EDGE, CORE]
   (0x1 < 0xFF < 0x1818000000); hash `d824a523…` (stable within a
   given endianness).
3. **Pipeline equivalence**: on 200 random collision-free positions,
   `compute_principal_indexes` output (200, 9) is **exactly equal** to the
   per-pattern reference (concatenated
   `compute_indexes_on_position` → `convert_to_principal_index` in
   mask-sorted set order). This exercises both the single-plane fast path
   (DOTA1, EDGE) and the multi-plane OR branch (CORE: two 2-runs) inside
   the fused kernel.
4. Per-pattern column counts = n_instances (4/4/1); `group_size =
   8/n_instances` divides evenly in every observed pattern.

### Issues (PatternSet) → consolidated list below
R4 (docstring "SHA256" vs sha3_256), R8 (endianness-dependent hash), plus
minors (duplicate-name Raises missing from docstring; empty-set `max()`
crash; array-only API vs Pattern's dual API; implicit column layout;
methods vs properties).

## Standalone functions and module-level objects

### Module header and exports (L1-78)
- L1-27 GPL-3 header (L7 typo: "Aauthor").
- L36 `import time` — **unused** (grep-verified; R5).
- L59-61 `__all__ = ['Index', 'IndexArray', 'Pattern', 'sample_pattern_data',
  'PatternSet']` — `PatternType` missing (R6).
- L66 `Index: TypeAlias = np.uint32`; L68 `validate_index_array`
  (BeforeValidator: ndarrays must be uint32, non-arrays pass through to
  pydantic); L76 `IndexArray = Annotated[np.ndarray, …]`.
- L78 `MAX_NUMBER_OF_SQUARE_FOR_PATTERN = 18` (singular "SQUARE" in the
  name); the L77 comment ties the bound to the uint32 base-3 index —
  conservative (S=19 still fits: (3^20−3)/2 < 2^32).

### Pattern-level Numba kernels
- `_numba_pack_bb_kernel` (L785): `(bb_array, pack_masks (P,), pack_shifts
  (P,))` → packed array of the same shape. ravel → per element:
  single-plane fast path `(bb & mask) >> shift`, else OR-fold over planes;
  reshape. (Note: `pack_masks.shape[0]` here vs `unpack_masks.size` in the
  sibling — cosmetic inconsistency.)
- `_numba_unpack_bb_kernel` (L818): the inverse ("PDEP simulation"):
  per plane `acc |= (packed & unpack_masks[p]) << pack_shifts[p]`.
- `_numba_computes_indexes_kernel` (L849): `(packed_m, packed_o,
  bit_shifts (S,), powers_3 (S,))` → base-3 index per element:
  `Σ (bit_m·3^b + bit_o·2·3^b)`. 1-D branch (scalar-position path: M =
  n_instances elements) + 2-D (N, M) prange branch. Accumulation mixes
  uint32 (`Index(0)` seed, `powers_3`) with uint64 bit terms
  (`Bitboard(1)` mask); numba unifies upward and the uint32 `out` store
  truncates — safe **only** because S ≤ 18 keeps values < 3^18 < 2^32.

### `sample_pattern_data` (L910-940)
29 `(name, python-int mask)` tuples (ELLE, SNAKE, EDGE, R2-R4, XEDGE,
DIAG3-8, CORNER, 2X5COR, 2X6COR, RCT2X4, CASTLE, BARBEL, MACE, FOURC,
CORE, CORED, COREA, WHIRL, TAU, DOTA1, DOTB1, TWOND). The masks are
**Python ints** — callers wrap with `Bitboard(...)` (L907). The block
comment (L895-908) carries stale environment instructions (`$(REVERSI_HOME)`,
`py/` layout, old venv) for a project that now uses `.venv` + editable
`src` layout (D-006/D-008) — minor issue. All 29 masks verified principal;
they span exactly the 11 PatternType fingerprints (verified).

### `Pattern.mdp_csv_file` / `mdp_record` (L243 / L563)
- `mdp_record()` → one comma-joined line: `name, mask(16X), n_squares,
  n_configurations, n_instances, n_stabilizers, type, sample_name, level,
  …` (L265 header: `n_squares,n_configurations,n_instances,n_stabilizers,`…).
- `mdp_csv_file(patterns, filename)` — classmethod, **hand-validated**
  arguments (not `@validate_call`), writes the records; for the LaTeX
  document's pattern table.

### PatternType (L82-140)
- 12 members: TYPE_0..TYPE_9 + TYPE_3D (DOTA1) + TYPE_7D (DIAG8); each
  `(fingerprint tuple, data dict)`. Fingerprint slots 1..7 encode
  I/S/T vs earlier slots (see Pattern section). Representative samples:
  TYPE_0 ELLE (8 inst, 1 stab), TYPE_2 EDGE (4, 2), TYPE_6 COREA (2, 4),
  TYPE_9 CORE (1, 8).
- `from_fingerprint` (L137): lazy class-level `_lookup` dict (built once);
  returns None for unknown fingerprints (Pattern then raises, L471-476).

## Real issues (candidates for fix, priority order)
_Original session (review-only, D-019): no code was changed, fixes
deferred. All items now resolved on 2026-08-27, each approved explicitly
by the user one at a time (fix campaign): R1 (D-020); R2-R7 (D-021);
R8 (D-022) — R8 closed as a documentation decision (little-endian-only
platform assumption), not a code change._

- **R1. [RESOLVED 2026-08-27, D-020] Principal-mask rule — unique
  representative.** Before the fix: `_check_mask_is_principal` (L314-339)
  rejected a mask only if some transform had a *strictly* lower BSR. When
  the orbit's minimal BSR is shared by several distinct orbit members —
  exactly: masks containing all 4 corners (all 8 transforms then have
  BSR 63) — each of them was independently accepted as "principal".
  Verified counterexample: 4 corners + a2 = 0x8100000000000181 and
  4 corners + h2 = 0x8100000000008081 — same orbit, distinct masks, both
  constructed fine, all 8 transforms of each at BSR 63. Fix applied
  (option (a), chosen by the user): the principal is the numerically
  lowest mask of the orbit — masks are 64-bit integers, a bijection with
  0..2^64−1, so the orbit minimum is a well-defined unique representative.
  The check now scans t1..t7 for a numerically lower mask (docstring
  updated to match). For the counterexample orbit the unique principal is
  now 4 corners + b1 = 0x8100000000000083; the other 7 members are
  rejected. Regression test: `test_init_rejects_non_minimum_orbit_masks`
  (test_pattern.py). The 29 sample patterns are unaffected (all re-verified
  constructible); suite GREEN (50 tests, 3 PERF skips).
- **R2. [RESOLVED 2026-08-27, D-021] False docstring invariant
  (L184).** "It holds that:
  len (unique_symmetric_instance_indexes) = n_stabilizers - 1" is false:
  DOTA1 (1 square) has n_stabilizers = 2 (ro000, fa1h8 — both fix A1) but
  both induce the identity permutation on it, so the list is empty.
  Correct statement (now in the docstring): the count is the number of
  stabilizer *elements* that induce a non-identity permutation on the
  pattern squares; it equals n_stabilizers − 1 only when no non-identity
  stabilizer element acts trivially on the squares. Fix applied
  2026-08-27 (D-021): docstring updated, code untouched.
- **R3. [RESOLVED 2026-08-27, D-021] `squares` docstring wrong
  (L160).** "sorted in descending priority"
  — the actual order is **ascending** board order (A1 first; verified:
  EDGE.squares = [0..7]). The entire downstream (pack plan, base-3 digits,
  fingerprint) relies on ascending order. Fix applied 2026-08-27 (D-021):
  docstring now reads "sorted in ascending board order (A1 first)".
- **R4. [RESOLVED 2026-08-27, D-021] PatternSet docstring says "SHA256"
  (L953); the code computes
  `hashlib.sha3_256` (L991).** Doc follows code. Fix applied 2026-08-27
  (D-021): docstring now reads "A SHA3-256 hash of the sorted mask
  values"; code untouched.
- **R5. [RESOLVED 2026-08-27, D-021] Unused `import time` (L36).**
  Fix applied 2026-08-27 (D-021): import removed.
- **R6. [RESOLVED 2026-08-27, D-021] `PatternType` missing from
  `__all__` (L59-61).** It is public
  surface (Pattern.type_info, `from_fingerprint`, CSV export) and
  `from twolm.pattern import *` (suggested by the L906 comment) does not
  import it. Fix applied 2026-08-27 (D-021): `PatternType` added to
  `__all__`; star-import verified to export it.
- **R7. [RESOLVED 2026-08-27, D-021] Stale comment (L478).** "Used by the
  compute_indexes_on_board
  method." — no such method exists; the real consumers are
  `compute_indexes_on_position` (L653) and the PatternSet pipeline. Fix
  applied 2026-08-27 (D-021): comment now reads "Used by
  compute_indexes_on_position and the PatternSet pipeline." (trailing
  whitespace removed).
- **R8. [CLOSED 2026-08-27, D-022 — documented, no code change] Set hash
  is endianness-dependent (L990).**
  `pattern.mask.tobytes()` is native byte order, so the identifier differs
  between little- and big-endian platforms. The proposed fix (fixed
  big-endian serialization) was **rejected** by the user: the legacy
  engine is written and tested for little-endian processors only — bit and
  byte manipulation is pervasive (including the move-generation and
  legal-moves pipelines) and its behavior on non-little-endian platforms
  is not guaranteed. Resolution: document the platform assumption
  instead — see "Platform assumption: little-endian only".

## Minor issues / inconsistencies
- L7 header typo "Aauthor" → "Author". **[RESOLVED 2026-08-27 — minor #1;
  fixed in pattern.py, board.py, test_board.py, test_pattern.py; commit
  b070918.]**
- L296 error message "n_square = {…}" → "n_squares". **[RESOLVED 2026-08-27
  — minor #2.]**
- "patetrn" typos: L188, L211 → "pattern". **[RESOLVED 2026-08-27 — minor
  #3 (L191, L214 in the current file).]**
- L233 "A dictionary mapping each configuration index to its principal
  index" — `principal_index_dict` is a dense ndarray (legacy name);
  reword. **[RESOLVED 2026-08-27 — minor #4: "A dense array mapping
  ..."; legacy name kept.]**
- `sample_pattern_data` block comment (L895-908): stale environment
  instructions (REVERSI_HOME, py/ layout, old venv) vs current .venv +
  editable src (D-006/D-008). **[RESOLVED 2026-08-27 — minor #5: comment
  now points to `<workspace root>` + `.venv`, no PYTHONPATH.]**
- `Pattern.__init__` (L287-290) hand-checks with `isinstance` while every
  other public method uses `@validate_call`; numpy string scalars are
  rejected for `name`. **[RESOLVED 2026-08-27 — minor #6, D-023: `__init__`
  now `@validate_call(strict=True, arbitrary_types_allowed=True)`, manual
  checks removed; constructor rejects everything that is not a `str` name /
  `np.uint64` (Bitboard) mask; TypeError → ValidationError; the two
  pinning tests updated to `ValidationError`.]**
- Nested `_check_mask_is_principal` (L314) carries `@validate_call` with
  zero arguments (validates nothing); sibling nested helpers are
  undecorated. **[RESOLVED 2026-08-27 — minor #7: removed the two no-op
  decorators (both `_check_mask_is_principal` and
  `_precompute_pack_unpack_plans` were decorated, zero arguments);
  `_get_position_mapping` keeps its (meaningful) decorator; no behavior
  change.]**
- `mask_to_index` reversed-enumerate idiom (L302): correct (first-seen
  index) but obscure — a forward comprehension would silently give the
  *last* occurrence. Add a comment.
- `_check_invariances` docstring (L538) claims "pack/unpack logic" checks;
  none exist.
- PatternSet `__init__` `Raises:` block (L971-974) omits
  ValueError(duplicate names) (L979).
- PatternType static fields (n_instances/n_stabilizers/sample_mask/level)
  are never cross-checked against the computed values of the representative
  (consistent for all 11 — spot-verified). **[RESOLVED 2026-08-27 — minor
  #11: cross-check added right after the fingerprint lookup; raises
  AssertionError if the table ever disagrees with the computed
  n_instances/n_stabilizers; suite confirms all 11 entries consistent.]**
- `MAX_NUMBER_OF_SQUARE_FOR_PATTERN`: singular "SQUARE" in the name; value
  18 conservative (S=19 fits uint32). **[RESOLVED 2026-08-27 — minor #12:
  renamed to `MAX_NUMBER_OF_SQUARES_FOR_PATTERN` (plural, consistent with
  n_squares); the "uint32 space" comment was factually wrong (3^20 < 2^32,
  even S=20 fits) and reworded as a conservative project choice.]**
- `fastmath=True` on integer-only kernels (L817, L848, L1114) — harmless,
  noisy. **[RESOLVED 2026-08-27 — minor #13: removed from all four
  kernels (the sweep found four, not three: pack, unpack, computes_indexes,
  compute_principal_indexes); no floating-point ops anywhere in them;
  PERF=1 suite fully GREEN after cache rebuild. A/B check (Roberto's
  request, 4 interleaved PERF=1 runs, fastmath ON/OFF): no measurable
  difference — pack/unpack ranges fully overlap, principal_indexes ranges
  overlap (one ON-side 1.23 s outlier from machine load), compute_indexes
  ~5-6% faster OFF-side but confounded by pair position; fastmath flags
  only affect floating-point IR, these kernels are pure integer.]**
- Scalar return surface: `_pack_bb` returns `Bitboard(…)`, `_unpack_bb`
  returns `np.uint64(…)` — same alias, cosmetic. **[RESOLVED 2026-08-27 —
  minor #14: `_unpack_bb` scalar path now `Bitboard(result.item())`,
  symmetric with `_pack_bb` (Bitboard is a plain alias of np.uint64, so
  identical values, consistent style).]**
- `names()`/`masks()` are methods next to attribute-style
  `name`/`patterns`/`hash`. **[RESOLVED 2026-08-27 — minor #15 (D-024):
  both converted to @property (attribute-style, derived from patterns);
  the two test call sites updated; KNOWN PENDING: legacy callers in the
  original 2008 repo (if any) use the old .names()/.masks() syntax —
  update at migration, tracked as I-006 in notes/ideas.md.]**
- `Pattern` has no `__repr__`/`__str__` (only print methods).
  **[RESOLVED 2026-08-27 — minor #16: `__repr__` added (Python falls back
  to it for `__str__` too), one line with name + mask, consistent with the
  first line of print(); no behavior change. PatternSet still has no
  __repr__ — out of scope of this item, noted as a possible follow-up.]**
- Empty `PatternSet(name, [])` is accepted, then
  `compute_principal_indexes` crashes in `max()` (L1050) with an
  unhelpful error. **[RESOLVED 2026-08-27 — minor #17: fail-fast
  `ValueError('Patterns list cannot be empty')` as the first check in
  PatternSet.__init__; docstring Raises updated; empty sets are
  meaningless for the indexing pipeline.]**
- A pattern with `n_squares = 0` (empty mask) is not explicitly rejected:
  n_configurations = 1, empty pack plan — degenerate, probably unintended.
  **[RESOLVED 2026-08-27 — minor #18: explicit fail-fast ValueError in
  Pattern.__init__ ("a pattern must select at least one square").
  Pre-fix the empty mask was rejected only accidentally — its degenerate
  fingerprint [I0 x8] is absent from the type table, which produced the
  confusing "fingerprint has not been found" error; same ValueError
  outcome, now explicit, earlier, and explanatory.]**
- No mover/opponent collision check in any indexing API (precondition;
  board.py provides `position_check_collisions`). **[RESOLVED 2026-08-27
  — minor #19 (D-025): leave-as-is by decision. The "caller validates"
  contract is already encoded by the tests (which check collisions before
  calling) and by the upstream engine; duplicating the check on the hot
  path was rejected. Precondition now documented in both docstrings
  (compute_indexes_on_position, compute_principal_indexes). No code
  change.]**

## Conventions to respect in any new work on this file
- **D8 slot order (D-014) is load-bearing**: `tmasks[i]` = T_i in
  canonical order; anti-table slots are inverses (slot s = T_s^{-1});
  instance order = first-seen slot order. Never reorder or rename slots.
- Instance 0 is always the ro000 image (= the principal mask itself);
  `trans_fs`/`anti_trans_fs` lists are indexed by **instance** (length =
  n_instances), not by slot.
- Packed domain: S contiguous bits, bit k ↔ the k-th square of `squares`
  (ascending board order); base-3 digits 0/1/2; uint32; S ≤ 18.
- Principal index = min over the induced-stabilizer orbit (config-level
  canonicalization); the per-pattern dict (L697) and the fused PatternSet
  kernel (L1115) compute the same quantity (verified equivalent).
- PatternSet column layout: Σ n_instances, in mask-sorted set order,
  canonical instance order; offsets are **not** exposed by the API.
- Dual scalar/array API at Pattern level (`compute_indexes_on_position`,
  `_pack_bb`, `_unpack_bb`); **array-only** at PatternSet level
  (`compute_principal_indexes`, `convert_to_principal_index`).
- The 11-type PatternType table is a **closed set**: an unknown computed
  fingerprint raises ValueError by design.
- Numba kernels are `cache=True`: first call compiles into `__pycache__`
  (cold-start latency is expected).
- `sample_pattern_data` masks are Python ints — wrap with `Bitboard(...)`
  before constructing Patterns.

## Verdict
The core mathematics is sound: orbit/stabilizer bookkeeping, the I/S/T
fingerprint, the run-based pack plan, and the base-3 + principal reduction
all verified against brute force (EDGE dict vs hand enumeration, Burnside
3321 = (6561+81)/2) and against the fused Numba pipeline (200 random
positions, exact match, both single- and multi-plane branches). All real
issues are resolved: R1 (D-020) — code fix + regression test; R2-R7
(D-021) — docstring/hygiene fixes, code behavior untouched; R8 (D-022) —
closed by decision as a little-endian-only platform assumption (documented,
no code change). Minor sweep COMPLETE (2026-08-27): all 19 items resolved
(D-023 item #6 strict constructor; D-024 item #15 property conversion +
I-006 legacy-migration follow-up; D-025 item #19 leave-as-is with
documented precondition; items #1-#5, #7-#12, #14, #16-#18
doc/hygiene/API-consistency/fail-fast fixes). Nothing blocks the current
29 sample patterns or the GREEN suite (50 tests, 3 PERF skips).
