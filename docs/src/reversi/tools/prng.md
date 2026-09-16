# reversi/tools/prng.py
The MT-19937 64-bit pseudo-random number generator.

## What it is
MT-19937 (the 64-bit Mersenne Twister) is a DETERMINISTIC
generator: seeded once with an integer, it yields a reproducible
stream of 64-bit values. The state is a 312-word (64-bit) array; a
draw first TWISTS the array (a linear recurrence mixing the 312
words) and then TEMPERS the output word with a 4-operation bitwise
mix. The period is 2^19937 - 1, so a single seed defines the whole
stream.

The module exposes ONE public class, MT19937 (`__all__ =
['MT19937']`). The state is fully INTERNAL: it is never exposed,
and a generator is neither saved nor re-seeded.

Typing: every 64-bit value in the data path is a numpy uint64 —
the type itself applies the unsigned-wraparound contract
(arithmetic overflows modulo 2^64; no unbounded Python ints, no
manual masking). Loop counters are plain ints (control flow, not
data).

## API
- MT19937(seed) — construct + seed. The seed is REQUIRED.
- get_uint64() -> np.uint64 — the next value of the sequence.
- get_uint64_batch(n) -> (n,) u64 array — the next n values.
- get_double_in_c0_c1() / _c0_o1() / _o0_o1() -> np.float64 —
  random floats in [0,1], [0,1), (0,1).
- random_choice_from_finite_set(k) -> np.uint64 — a uniform integer
  in [0, k-1]; k == 1 returns 0 WITHOUT consuming a value; k == 0
  raises.
- shuffle_uint8 / shuffle / shuffle_double / shuffle_int
  (array, n) — in-place Fisher-Yates shuffles (n == 0 or 1
  consumes nothing).
- random_string_az(n) -> str — n random lowercase letters.
- extract_from_set64(set_arr) -> np.uint8 — pick + REMOVE a random
  bit from the bitmask in set_arr[0] (in place); returns the
  0-based position.
- choose_one_from_set64(set64) -> (np.uint64, np.uint8) — pick a
  random bit WITHOUT removing it (the set is read, never mutated);
  returns (1 << p, p). The empty set returns the (0, 64) sentinel
  WITHOUT consuming a draw.

## How it works
- The seed: the 312-word array is filled by a linear recurrence
  over the previous word (the multiplier 6364136223846793005), and
  the working index is left at NN, so the first get_uint64 twists
  the just-initialized array before its first draw.
- The draw: the numba kernel _get_uint64_batch (the single source)
  does the TWIST (when the index reaches the end of the 312-word
  array, a linear recurrence regenerates the whole array) and the
  4-op TEMPER (the returned word is mixed with 4 bitwise ops).
  get_uint64 delegates to get_uint64_batch (n = 1), so the scalar
  and batch paths share one implementation; get_uint64_batch is
  bit-identical to get_uint64 called n times.
- The constants: NN = 312 is module-level (the working-area size);
  the twist + temper constants MM / UM / LM / MAG are local to the
  kernel (its implementation details).
- The bit helpers used by extract_from_set64 are inlined: the
  popcount, (s - 1) & s (clear the lowest set bit), and
  (s & -s).bit_length() - 1 (the index of the lowest set bit).

## Invariants
- get_uint64_batch is bit-identical to get_uint64 called n times
  (they share the one kernel).
- random_choice_from_finite_set(1) consumes NOTHING (the next draw
  equals a fresh instance's first draw); the n <= 1 shuffles
  consume nothing too.
- extract_from_set64 clears the picked bit from the ORIGINAL set
  (the skipped-lowest bits survive); the empty set raises.
- choose_one_from_set64 NEVER mutates the set (no removal) and
  consumes exactly one draw per non-empty pick.

## Integration
- Dependencies: numpy + math + numba (the kernel).
- lm/hlp_wave.py (the G0 wave engine) drives the wave through the
  class's get_uint64_batch; this module is the single source of the
  draw stream.
- random_game.py uses choose_one_from_set64 for the random move
  pick; the seeded random-game corpus generation (feature
  analysis) rides on the class.
- A TOOLS module (tools/ subpackage): a generic MT library, not a
  pipeline level.
