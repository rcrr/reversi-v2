# reversi/tools/prng.py
The MT-19937 64-bit PRNG — the line-by-line Python port of
Roberto's C library (prng.c, 2017 — the 64-bit variant, NOT the
32-bit reference), the I-017 T2 (D-159). One class, MT19937,
mirrors the C prng_mt19937_t struct and its 15 functions: the two
inits (by seed / by array), get_uint64 (the twist + the 4-op
temper), the three double generators ([0,1], [0,1), (0,1)),
random_choice_from_finite_set, the four Fisher-Yates shuffles,
random_string_az, extract_from_set64 and choose_one_from_set64.
The module is the SINGLE SOURCE of the numba MT19937-64 kernels
(mt19937_init / mt19937_batch_draw) — the G0 wave stream.
> State: D-194 (the numba kernels — the single source) + D-193
+ D-160 · 2026-09-15 · suite 20/0/0

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
- choose_one_from_set64(set64) -> (np.uint64, np.uint8) — the
  uniform pick from the u64 set, NO removal (the D-193, unlike
  extract_from_set64: the set is read, never mutated): k =
  popcount, ONE get_double_in_c0_o1 draw, the c = floor(r·k)
  lowest set bits skipped, the next lowest set bit picked —
  returns (1 << p, p). The empty set returns the (0, 64)
  sentinel (64 = PA in the Move domain) WITHOUT consuming a draw.
- mt19937_init(mt, seed) -> mti — the numba init (the C
  prng_mt19937_init_by_seed, line by line; the verbatim quirk:
  the loop leaves mti == NN, the first draw twists). mt is the
  caller's (NN,) u64 array, filled in place.
- mt19937_batch_draw(mt, mti, n) -> (draws, mti) — the numba
  batch draw: n successive u64 draws (the twist + the 4-op
  temper, prng.c L380-414 line by line), bit-exact vs the
  golden-pinned MT19937 class above (the T3 C oracle). The
  state (mt, mti) is the caller's, mutated in place.

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
  MAG01 = {0, 0xB5026F5AA96619E9}; MAG = MAG01[1] (the scalar
  the numba kernel switches on).
- The numba kernels (the D-194, the single source): the
  mt19937_init + mt19937_batch_draw @nb.njit(cache=True)
  section at the end of the file — the G0 wave stream;
  lm/hlp_wave.py imports them (it carries no PRNG code
  anymore).
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
- The T3 golden suite landed (D-161): test_prng.py now pins the
  C-oracle committed sequences (data/prng_golden.txt — 10k
  seed-42 + 1k array-init uint64, the two mt init states, the
  doubles / choice / extract sequences) + the first-100k
  equi-distribution (the per-bit balance, the top-bit chi-
  square, the choice-64 uniformity) — ALL MATCH.
- The k == 1 no-consume contract: random_choice_from_finite_set(1)
  leaves the sequence position untouched (the next draw equals a
  fresh instance's first draw).
- The shuffle no-op for n <= 1 consumes nothing (same contract).
- extract_from_set64: the C clears the picked bit from the
  ORIGINAL set (the skipped-lowest bits survive); the empty set
  raises (the C assert *set).
- choose_one_from_set64 (D-193): the NO-removal contract (the
  set is read, never mutated) + the uniform pick + the
  one-draw-per-pick stream consumption — pinned by the
  test_random_game golden (the exact 1000-draw frequencies at
  seed 93: any stream-consumption drift moves them).
- The numba batch kernel vs the golden-pinned class (the D-194
  single source): bit-exact over 2100 draws (the 2000-draw
  batch + the twist across the 312-word boundary + the 100-
  draw continuation, seed 7) — pinned by test_hlp_wave::
  TestG0Engine::test_batch_matches_reference (the W=1
  trajectory + the run-determinism suites ride on it).

## Open issues
- The numba era (Roberto: "appena l'algoritmo funziona
  bisognera farlo andare con numba"): the batch-draw path is
  numba (the kernel section, the D-194); the CLASS hot path
  (get_uint64 + the inits) is still Python — the board-design
  transformation (the single numba kernel + the dual public
  face, the class as a thin state wrapper) is the next pass
  (parked, Roberto's plan).

## Conventions
- The GNU header (the house template) + the provenance docstring
  (the C source, the D-number, the typing ruling).
- The method names mirror the C function names (the prng_ /
  _mt19937_ prefix stripped) — a 1:1 C-to-Python map.
- The C @brief/@details doc comments are carried into the Python
  docstrings (the "line by line" fidelity extends to the
  documentation).

## Integration
- Dependencies: numpy + math + numba (the kernel section, the
  D-194).
- The kernel consumer: lm/hlp_wave.py (the G0 wave engine —
  this module is the single source, the D-194 move) + the
  wave test suite.
- Consumers: the I-017 pipeline (the single-game random play,
  the concurrent wave engine, the marginal frequency
  accumulator) — the seeded corpus generation for the
  FEATURE_ANALYSIS level; random_game.py (the choose_random_
  move pick, the D-193).
- Not a pipeline level: a TOOLS module used by the future levels
  (the D-160 rename from the feature_prng core name — the module
  is a GENERIC MT library: the name follows what it is, not its
  first consumer; the tools/ subpackage per D-133).
