# reversi/tools/prng.py
The MT-19937 64-bit PRNG — the line-by-line Python port of
Roberto's C library (prng.c, 2017 — the 64-bit variant, NOT the
32-bit reference), the I-017 T2 (D-159). One class, MT19937,
mirrors the C prng_mt19937_t struct: the seed-init (the D-199:
the init_by_seed consolidated into the ctor), get_uint64 (the
twist + the 4-op temper), the three double generators ([0,1],
[0,1), (0,1)), random_choice_from_finite_set, the four Fisher-
Yates shuffles, random_string_az, extract_from_set64,
choose_one_from_set64 and get_uint64_batch (the numba batch
draw). The init_by_array is SKIPPED (the D-198). MT19937 is the
SOLE public interface (the D-195: __all__ is [MT19937]); the
single INTERNAL numba kernel _get_uint64_batch is the module's
single source for the twist + the 4-op temper + the G0 wave
stream, and get_uint64 delegates to it (the D-196). The D-199
rationalized the rest: the state (_mt/_mti) is fully INTERNAL
(the C accessors mt/mti dropped), and MM/UM/LM/MAG are kernel-
LOCAL (only NN stays module-level).
> State: D-199 (the ctor-consolidated init, the props + the
kernel constants rationalized) + D-198 + D-197 + D-196 + D-195
+ D-194 + D-193 + D-160 · 2026-09-15 · suite 14/0/0

## API
- MT19937(seed) — the fused C new + the init_by_seed (the
  D-199: the init is CONSOLIDATED into the ctor, the init_by_
  seed method is gone; the seed is REQUIRED; the D-198 removed
  the init_key / init_by_array — the object is ALWAYS
  initialized, the C legacy deferred-init / bare-state path
  dropped, the D-197). The state (_mt / _mti) is INTERNAL — the
  C accessors mt / mti are dropped (the D-199: we never read
  the state to save it).
- get_uint64() -> np.uint64 — the next value of the sequence.
  Delegates to get_uint64_batch(1) (the D-196): the twist + the
  4-op temper live in the numba kernel _get_uint64_batch, no
  duplicated logic.
- get_uint64_batch(n) -> (n,) u64 array — the n successive values
  of the sequence (the D-195 class interface): the INTERNAL
  numba batch-draw kernel _get_uint64_batch (the single source)
  run on the object state (_mt + _mti, mutated in place).
  Bit-exact vs get_uint64 called n times (they share the same
  kernel, the D-196); the state is always initialized (the
  D-197).
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

## Architecture
- The strict-typing ruling (D-159, Roberto: "NUMPY e stiamo
  strict con i tipi"): every 64-bit value in the DATA PATH is a
  numpy uint64 — the type itself applies the C unsigned-
  wraparound contract (the numpy uint64 arithmetic overflows
  modulo 2^64 exactly like the C, no unbounded Python ints, no
  manual masking). Loop counters are plain ints (control flow,
  not data).
- The constants are verbatim from prng.c L154-158 (the D-199
  scoped them): NN = 312 is module-level (the ctor's
  np.zeros(NN, …) + the init loop use it); MM = 156, UM =
  0xFFFFFFFF80000000, LM = 0x000000007FFFFFFF, MAG =
  0xB5026F5AA96619E9 are defined INSIDE the kernel
  _get_uint64_batch (the twist + temper's implementation
  details, the D-199). The C MAG01 array is dropped — only the
  odd scalar MAG (MAG01[1]) is used (the D-199).
- The numba kernel (the D-194, the single source): the single
  _get_uint64_batch @nb.njit(cache=True) at the end of the file
  — the twist + the 4-op temper (prng.c L380-414 line by line),
  the G0 wave stream. It is INTERNAL (not in __all__, the
  D-195/D-196): only the class's get_uint64_batch calls it, and
  get_uint64 delegates to that (n = 1), so the scalar + batch
  paths share ONE kernel (no duplicated twist/temper, the
  D-196). The mt19937_init kernel is REMOVED (the D-196): the
  ctor (the consolidated init_by_seed, the D-199) owns the init
  (it is bit-identical to the removed numba init, so a class
  instance is a valid kernel state). lm/hlp_wave.py drives the
  wave through the class (it carries no PRNG code, the
  D-194/D-195).
- The init multiplier (the ctor's consolidated init, the
  D-199) is HIS constant 6364136223846793005 — it is NOT the
  32-bit-reference 6364136293807784493 (do not "fix" it; the
  golden is the C build, not the reference).
- The C for-loop quirk is preserved: the ctor's init leaves
  mti == NN, so the FIRST get_uint64 twists the just-
  initialized array immediately.
- The numpy overflow warnings on the BY-DESIGN wraps are silenced
  locally (np.errstate over="ignore") in the ctor's init loop —
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
- The strict-typing pins: every generator returns np.uint64 /
  np.float64 (the tests assert the dtypes). The state (_mt /
  _mti) is INTERNAL (the D-199 dropped the mt / mti accessors)
  — it is no longer observed from outside; the C-oracle golden
  pins its behavior end-to-end instead.
- The T3 golden suite landed (D-161): test_prng.py now pins the
  C-oracle committed sequences (data/prng_golden.txt — 10k seed-
  42 uint64, the doubles / choice / extract sequences) + the
  first-100k equi-distribution (the per-bit balance, the top-bit
  chi-square, the choice-64 uniformity) — ALL MATCH. (The
  array-init sections dropped with the D-198; the mt seed-42
  state section dropped with the D-199, the state being internal
  now.)
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
- The numba kernel (the D-196 single source) vs the golden-
  pinned C: get_uint64 (the D-196 delegation) + get_uint64_
  batch (the D-195 class interface) share it — bit-exact over
  2100 draws (the 2000-draw batch + the twist across the 312-
  word boundary + the 100-draw continuation, seed 7) — pinned
  by test_hlp_wave::TestG0Engine::test_batch_matches_reference
  (the W=1 trajectory + the run-determinism suites ride on
  it) + test_prng::TestPrng::test_get_uint64_batch_matches_
  scalar (500 draws vs get_uint64, the twist boundary) + the
  T3 golden 10k seed-42 sequence (now produced through the
  kernel).

## Open issues
- The numba era (Roberto: "appena l'algoritmo funziona
  bisognera farlo andare con numba"): the draw path is fully
  numba through the class (get_uint64 + get_uint64_batch, the
  D-196/D-195, over the single kernel _get_uint64_batch, the
  D-194). The remaining init (in the ctor — the D-199
  consolidated init_by_seed, the D-198 removed the init_by_
  array) is still Python — the last board-design pass (the
  init over a numba init kernel) is the next step (parked,
  Roberto's plan).

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
- The consumer: lm/hlp_wave.py (the G0 wave engine) drives the
  wave through the class's get_uint64_batch (the D-195; this
  module is the single source, the D-194 move) + the wave test
  suite.
- Consumers: the I-017 pipeline (the single-game random play,
  the concurrent wave engine, the marginal frequency
  accumulator) — the seeded corpus generation for the
  FEATURE_ANALYSIS level; random_game.py (the choose_random_
  move pick, the D-193).
- Not a pipeline level: a TOOLS module used by the future levels
  (the D-160 rename from the feature_prng core name — the module
  is a GENERIC MT library: the name follows what it is, not its
  first consumer; the tools/ subpackage per D-133).
