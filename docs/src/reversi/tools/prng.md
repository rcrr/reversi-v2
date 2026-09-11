# reversi/tools/prng.py
The MT-19937 64-bit PRNG — the line-by-line Python port of
Roberto's C library (prng.c, 2017 — the 64-bit variant, NOT the
32-bit reference), the I-017 T2 (D-159). One class, MT19937,
mirrors the C prng_mt19937_t struct and its 15 functions: the two
inits (by seed / by array), get_uint64 (the twist + the 4-op
temper), the three double generators ([0,1], [0,1), (0,1)),
random_choice_from_finite_set, the four Fisher-Yates shuffles,
random_string_az and extract_from_set64.
> State: D-160 · pending · 2026-09-11 · suite 10/0/0

## API
- MT19937(seed=… | init_key=…) — the fused C new + one init call
  (fail-fast: exactly one of the two must be given).
- init_by_seed(seed) / init_by_array(init_key) — the C inits, line
  by line; init_by_array fails fast on an EMPTY key (the C read
  would be an out-of-bounds UB).
- get_uint64() -> np.uint64 — the next value of the sequence (the
  twist triggers automatically; a BARE state — never init'ed,
  only possible via the internals — falls back to the C default
  seed 5489).
- get_double_in_c0_c1() / _c0_o1() / _o0_o1() -> np.float64 — [0,1],
  [0,1), (0,1).
- random_choice_from_finite_set(k) -> np.uint64 — uniform in
  [0, k-1]; k == 1 returns 0 WITHOUT consuming a value (the C
  contract); k == 0 raises (the C assert).
- shuffle_uint8 / shuffle / shuffle_double / shuffle_int
  (array, n) — the Fisher-Yates in-place shuffles (the C
  uint8 / generic-pointer / double / int faces; n == 0 or 1
  consumes nothing).
- random_string_az(n) -> str — n random chars in [a..z].
- extract_from_set64(set_arr) -> np.uint8 — picks + removes a
  random bit from the uint64 bitmask in set_arr[0] (IN PLACE, the
  C pointer semantics) and returns the 0-based position.

## Architecture
- The strict-typing ruling (D-159, Roberto: "NUMPY e stiamo
  strict con i tipi"): every 64-bit value in the DATA PATH is a
  numpy uint64 — the type itself applies the C unsigned-
  wraparound contract (the numpy uint64 arithmetic overflows
  modulo 2^64 exactly like the C, no unbounded Python ints, no
  manual masking). Loop counters are plain ints (control flow,
  not data).
- The constants are verbatim from prng.c L154-158: NN = 312,
  MM = 156, UM = 0xFFFFFFFF80000000, LM = 0x000000007FFFFFFF,
  MAG01 = {0, 0xB5026F5AA96619E9}.
- The init_by_seed multiplier is HIS constant
  6364136223846793005 — it is NOT the 32-bit-reference
  6364136293807784493 (do not "fix" it; the golden is the C
  build, not the reference).
- The C for-loop quirk is preserved: init_by_seed leaves
  mti == nn, so the FIRST get_uint64 twists the just-initialized
  array immediately.
- The numpy overflow warnings on the BY-DESIGN wraps are silenced
  locally (np.errstate over="ignore") in the two init loops —
  the wrap is the contract, not an error.
- The three bitw_* C helpers used by extract_from_set64
  (bit_works.c) are inlined: the popcount, (s - 1) & s (clear the
  lowest set bit), and (s & -s).bit_length() - 1 (the de Bruijn
  bsf) — no separate bit_works module (the port is the prng
  only).
- Skipped from the C: the 4 prng_stdlib_* wrappers (thin over
  srand/rand) and prng_uint64_from_clock_random_seed (the
  clock-based seed: non-deterministic, unused — the pipeline
  seed comes from the config and is part of the cache
  signature).

## Verified invariants
- BIT-EXACT vs the C: the T2 cross-check (scratch/, the C build
  of prng.c + bit_works.c + time_utils.c + the disposable
  harness) — 64 get_uint64 values (seed 42), 64 (the init-by-
  array key {1,2,3,4}), 8 get_double_in_c0_o1, 16
  random_choice_from_finite_set(5): ALL MATCH, in
  warnings-as-errors mode. The full golden suite lands in T3
  (the C build + ut_prng.c the oracles).
- The strict-typing pins: the state mt is a uint64 ndarray
  (shape (312,)); every generator returns np.uint64 /
  np.float64 (the tests assert the dtypes).
- The k == 1 no-consume contract: random_choice_from_finite_set(1)
  leaves the sequence position untouched (the next draw equals a
  fresh instance's first draw).
- The shuffle no-op for n <= 1 consumes nothing (same contract).
- extract_from_set64: the C clears the picked bit from the
  ORIGINAL set (the skipped-lowest bits survive); the empty set
  raises (the C assert *set).

## Open issues
- The T3 golden suite (the committed bit-sequence golden vs the
  C build + the published vectors + the 100k equi-distribution
  property) — the next task (I-017 T3).
- The numba era (Roberto: "appena l'algoritmo funziona bisognera
  farlo andare con numba"): the uint64 state is the right
  substrate for the T5 wave engine; no action at T2 (the PRNG
  draws are the RARE path — the 2016 table-build draws per seed;
  the hot path is the table lookup).

## Conventions
- The GNU header (the house template) + the provenance docstring
  (the C source, the D-number, the typing ruling).
- The method names mirror the C function names (the prng_ /
  _mt19937_ prefix stripped) — a 1:1 C-to-Python map.
- The C @brief/@details doc comments are carried into the Python
  docstrings (the "line by line" fidelity extends to the
  documentation).

## Integration
- No dependencies outside numpy + math (the core module is
  standalone).
- Future consumers: the I-017 tasks T4-T7 (the single-game
  random play, the concurrent wave engine, the permutation
  lookup table, the marginal frequency accumulator) — the
  seeded corpus generation for the FEATURE_ANALYSIS level (T12).
- Not a pipeline level: a TOOLS module used by the future levels
  (the D-160 rename from the feature_prng core name — the module
  is a GENERIC MT library: the name follows what it is, not its
  first consumer; the tools/ subpackage per D-133).
