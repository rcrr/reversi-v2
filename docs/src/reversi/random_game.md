# reversi/random_game.py
The random-game module of the Reversi engine: the random move pick, the random move execution, and the random path —
including the batch array engine that plays a whole corpus of positions in lockstep. It is the corpus generator for the
random-play statistics: the SU_ANALYSIS level's production corpus engine (the play-path batches feed the
hlp_su_analysis accumulators; the hlp_wave wave engine is retired — D-285).

## API

The 3 `__all__` functions. Dual contract throughout: a scalar PositionField in → scalar out, a PositionArray of any
shape in → array out of the same shape (a 1-D batch keeps the classic layout; the 2-D (N, 2) uint64 raw input is
coerced to the 1-D PositionArray by the PositionArray validator). The PRNG is INJECTED — the caller owns the
MT19937 stream ("one seed for all"); the N-D element order (the draw order) is the C-order ravel of the array.

| family | name | contract |
|---|---|---|
| pick | `random_game_choose_move(p, prng) -> Bitboard \| BitboardArray` | a random legal move: `position_legal_moves` + the uniform pick (`choose_one_from_set64` / the batch kernel). No legal move: the empty bitboard 0 — the caller's pass signal |
| move | `random_game_make_move(p, prng) -> (PositionField \| PositionArray, Move \| MoveArray)` | pick + execute via `position_flips`: the resulting position (the next player's view) and the played move (the square, 64 = PA). No legal move: the pass and the swapped position |
| path | `random_game_play_path(p, target_ec, prng) -> (PositionField \| PositionArray, np.uint8 \| uint8 array)` | random legal moves until the empty count reaches `target_ec` (ONE shared target) or the game-over double pass; returns the final position + its empty count (an ordinal np.uint8). Already at or below the target: returned as-is |

The PRNG stream contract (all three): the elements consume their draws from the ONE injected stream in element order,
exactly like a scalar loop — one draw per non-terminal element, no draw for a pass. The array calls are deterministic
given the seed; the single-pick functions are bit-identical to the sequential scalar processing of the same positions,
and the N == 1 path call is bit-identical to the scalar call.

## Architecture

Layered over board.py and tools/prng.py — no state of its own, no PRNG of its own; every function is pure in its inputs.
The game mechanics live in board.py, the draw/pick techniques in tools/prng.py: this module composes them and
re-implements neither.

- The scalar paths: the thin composition of the board/prng public functions (the legal set + `choose_one_from_set64`;
  the flips via `position_flips`).
- The array single-pick paths: one `get_uint64_batch` pre-draw for the needing elements (the prefix slot map) and the
  per-element pick via the prng batch kernel.
- The array path engine: the step loop in TWO fused kernels — `_classify_step` (per lane: the legal set via board's
  per-lane primitive `legal_moves_of`, the classification masks, the pass lanes' opponent set in kernel) and
  `_advance_step` (per lane: the pick via prng's `pick_one_from_set64` on the pre-drawn slot, the flip set via board's
  `flips_of_move`, the in-place state update). Between the passes only the needs count, the prefix slot map and one
  `get_uint64_batch` call. The state is the raw (movers, opponents) uint64 pair — copied once from the input, advanced
  in place, assembled into the Position array once at the end.
- The step bound is derived from the input (a lane needs at most its ec surplus over the target, plus one); a stall
  would raise, never hang.

## Verified invariants

- The pick: every draw is a member of the legal set, and the EXACT 1000-draw frequencies [258, 229, 249, 264] over the
  initial-position legal set {D3, C4, F5, E6} at seed 93 — pinned by test_random_game::TestRandomGameChooseMove::
  test_random_game_choose_move.
- The move execution: from the 20-empty fixture with two legal moves, N = 12 draws yield ONLY the two resulting boards,
  each consistent with the drawn move and one stone ahead; a position with no legal move returns the pass and the
  swapped position — pinned by test_random_game::TestRandomGameMakeMove.
- The path: the final empty count is <= the start and >= the target; the game-over double pass ends the lane with the
  input view returned; the single-pass game continues via the pass — pinned by test_random_game::TestRandomGamePlayPath.
- The array paths are bit-identical to the sequential scalar processing (the single-pick functions and the N == 1 path
  call) and deterministic — pinned by test_random_game::
  TestRandomGameChooseMoveArray::test_array_matches_sequential_scalar,
  TestRandomGameMakeMoveArray::test_array_matches_sequential_scalar,
  TestRandomGamePlayPathArray::test_single_lane_array_matches_scalar / test_determinism.
- The multi-generation distinctness (the hash-based duplicate check over N = 10 paths) — pinned by test_random_game::
  TestRandomGamePlayPath::test_random_game_play_path_multi_generation.
- The 1M-games benchmark (print-only) — test_random_game::
  TestRandomGamePlayPathArray::test_perf_play_path_million_games_to_ec0.

## Open issues

None.

## Conventions

- The PRNG stream is the caller's: the module never draws outside the injected stream, and the array consumption is
  documented per element and per step (the reproducibility discipline).
- The PRNG pick technique lives in tools/prng.py (the per-lane njit primitive `pick_one_from_set64`); this module
  composes it and never re-implements it.
- The game mechanics live in board.py (the per-lane njit primitives `legal_moves_of` / `flips_of_move`); the fused
  kernels call them and never duplicate the geometries.
- The engine arrays are mutated in place: the input batch is copied once, the caller's array is never touched.
- The empty move set is the module constant `_EMPTY_MOVE_SET` — the pass signal of the pick domain; the tests pin the
  expected values as literals (the goldens), not through the constant.
- @validate_call (pydantic, arbitrary_types_allowed) on the public functions; the dual scalar/array signature, arrays
  of any shape (the pick / make-move run on the C-order ravel of the legal-move sets; the play-path engine runs on
  the C-order ravel of the positions — the 1-D lane engine is unchanged — and the outputs are reshaped back to the
  positions shape).

## Integration

- board.py (the geometry + the positions + the per-lane njit primitives `legal_moves_of` / `flips_of_move`).
- tools/prng.py (the MT19937 stream, the pick primitives, the batch pre-draw).
- The SU_ANALYSIS corpus engine (the su-corpus-5 lineage): wrk_su_analysis.py (step 3) feeds its play-path batches —
  the harvested lanes at the model's ec — to the hlp_su_analysis accumulators. The hlp_wave wave engine is
  RETIRED
  (D-285).
