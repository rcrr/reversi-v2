# reversi/tools/prng.py
The MT-19937 64-bit pseudo-random number generator: seeded once with an integer it yields a reproducible stream of
64-bit values (a 312-word state, twisted by a linear recurrence and then tempered; the period is 2^19937 - 1). The
module exposes ONE public class, `MT19937`, plus the two numba pick kernels
(`__all__ = ['MT19937', 'pick_one_from_set64', 'pick_one_from_set64_batch']`); the stream state is fully INTERNAL — it
is never exposed, and a generator is neither saved nor re-seeded.

## API
- MT19937(seed) — construct + seed. The seed is REQUIRED.
- get_uint64() -> np.uint64 — the next value of the sequence.
- get_uint64_batch(n) -> (n,) u64 array — the next n values.
- get_double_in_c0_c1() / _c0_o1() / _o0_o1() -> np.float64 — random floats in [0,1], [0,1), (0,1).
- random_choice_from_finite_set(k) -> np.uint64 — a uniform integer in [0, k-1]; k == 1 returns 0 WITHOUT consuming a
  value; k == 0 raises.
- shuffle_uint8 / shuffle / shuffle_double / shuffle_int (array, n) — in-place Fisher-Yates shuffles (n == 0 or 1
  consumes nothing).
- random_string_az(n) -> str — n random lowercase letters.
- extract_from_set64(set_arr) -> np.uint8 — pick + REMOVE a random bit from the bitmask in set_arr[0] (in place);
  returns the 0-based position.
- choose_one_from_set64(set64) -> (np.uint64, np.uint8) — pick a random bit WITHOUT removing it (the set is read, never
  mutated); returns (1 << p, p). One get_uint64 draw, the pick delegated to the numba kernel pick_one_from_set64 (the
  single source of the technique). The empty set returns the (0, 64) sentinel WITHOUT consuming a draw.
- pick_one_from_set64(s, d) -> (np.uint64, np.uint8) — the numba kernel (D-221): the uniform pick of one bit from the
  NON-ZERO set s given the PRE-DRAWN value d (k = popcount, r = (d >> 11) · 2⁻⁵³ — the c0_o1 scalarization — c =
  floor(r·k), the c-th set bit). The single source shared by choose_one_from_set64 / extract_from_set64 (they draw and
  delegate) and by the numba batch callers.
- pick_one_from_set64_batch(sets, draws, slots) -> (N,) u64 array — the vectorized form (D-221): element i with a
  non-empty set picks from sets[i] using draws[slots[i]] (slots[i] = the number of non-empty sets before i, the caller's
  prefix count); an empty set yields 0 and consumes no draw. Bit-identical to calling choose_one_from_set64 on the
  elements in order with the same stream.

## Architecture
- The seed: the 312-word array is filled by a linear recurrence over the previous word (the multiplier
  6364136223846793005), and the working index is left at NN, so the first get_uint64 twists the just-initialized array
  before its first draw.
- The draw: the numba kernel _get_uint64_batch (the single source) does the TWIST (when the index reaches the end of the
  312-word array, a linear recurrence regenerates the whole array) and the 4-op TEMPER (the returned word is mixed with
  4 bitwise ops). get_uint64 delegates to get_uint64_batch (n = 1), so the scalar and batch paths share one
  implementation; get_uint64_batch is bit-identical to get_uint64 called n times.
- The constants: NN = 312 is module-level (the working-area size); the twist + temper constants MM / UM / LM / MAG are
  local to the kernel (its implementation details).
- The pick-from-set technique (D-221) lives ONCE: the numba kernel pick_one_from_set64 is the single source —
  choose_one_from_set64 and extract_from_set64 draw one value and delegate to it; the batch form
  (pick_one_from_set64_batch) is the same math over an (N,) set array fed by one get_uint64_batch pre-draw.

## Verified invariants
- get_uint64_batch is bit-identical to get_uint64 called n times (they share the one kernel) —
  test_prng::TestPrng::test_get_uint64_batch_matches_scalar.
- random_choice_from_finite_set(1) consumes NOTHING (the next draw equals a fresh instance's first draw); the n <= 1
  shuffles consume nothing too — test_prng::TestPrng::test_random_choice_contracts / test_shuffle_contracts.
- extract_from_set64 clears the picked bit from the ORIGINAL set (the skipped-lowest bits survive); the empty set raises
  — test_prng::TestPrng::test_extract_from_set64.
- choose_one_from_set64 NEVER mutates the set (no removal) and consumes exactly one draw per non-empty pick —
  test_prng::TestChooseOneFromSet64::test_the_set_is_never_mutated /
  test_empty_set_is_the_sentinel_and_consumes_nothing.
- The pick kernels and the class methods agree draw-for-draw (the identity pin: the same stream, the same (bitboard,
  index)) — test_prng::TestPickOneFromSet64::test_scalar_kernel_matches_the_method; the batch kernel is bit-identical to
  the sequential method loop (the stream-alignment probe, the all-empty no-draw case) —
  test_prng::TestPickOneFromSet64::test_batch_kernel_matches_the_method / test_batch_all_empty_sets.

## Open issues

None.

## Conventions

- Typing: every 64-bit value in the data path is a numpy uint64 — the type itself applies the unsigned-wraparound
  contract (the arithmetic overflows modulo 2^64: no unbounded Python ints, no manual masking); the loop counters are
  plain ints (control flow, not data).
- The pick-from-set technique lives ONCE, in the numba kernel: a caller draws and delegates, it never re-implements the
  rank walk (D-221).

## Integration
- Dependencies: numpy + math + numba (the kernel).
- lm/hlp_wave.py (the wave engine) drives the wave through the class's get_uint64_batch; this module is the single
  source of the draw stream.
- random_game.py uses choose_one_from_set64 for the scalar random move pick and pick_one_from_set64_batch for the array
  one (the D-219 stream contract); the seeded random-game corpus generation (feature analysis) rides on the class.
- A TOOLS module (tools/ subpackage): a generic MT library, not a pipeline level.
