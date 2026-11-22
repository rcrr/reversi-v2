# reversi/endgame_solver.py
The exact endgame solver, scalar and array (the unified API, the board.py idiom: one function, both
forms). `minimax_solve` searches the whole game tree of an endgame with a depth-first minimax,
`alphabeta_solve` the same tree with the zero-window alpha-beta pruning; each takes a GamePosition
scalar (the direct compiled search, the `SolverResult`) or a `GamePositionArray` (the batch on a pool
of worker threads, one per CPU, dynamic dispatch — the `SolverResultArray` of the per-lane results);
all return the game value, the terminal game position of the best line, and the search counters.

## API

The `__all__` names.

| name | contract |
|---|---|
| `OUT_OF_RANGE_DEFEAT_SCORE` | the out-of-range sentinel of the best-value accumulation (−66, the C constant): just outside the game-value range, so the first child value always wins the strict comparison and the no-move-yet state needs no test |
| `GameValue` | the game-value type: `np.int8` (a value from -64 to +64) — defined here, the solver is the producer of game values; `regab.py` imports it from this module |
| `GameValueArray` | the pydantic-validated `NDArray[np.int8]` game-value array type (the int8-dtype `BeforeValidator`) — defined here with `GameValue` |
| `NodeRecord` | the frozen dataclass `(call_id, level, player, parent_move, best_move, value)` — one visited node of the search, as emitted to the `log` callback (see The trace); the move fields are never `None` (the sentinel codes `MOVE_UN` / `MOVE_NA` / `MOVE_PA` express the absences) |
| `SolverResult` | the frozen dataclass `(game_value, final_game_position, nodes, leafs)`: the value is an `np.int8` (the vectorized future's type, kept here for conformance), the final position is a GamePosition scalar (`GamePositionField`) |
| `SolverResultArray` | the frozen dataclass `(game_values, final_game_positions, nodes, leafs)` of parallel arrays, one entry per lane: the `GameValueArray` values, the `GamePositionArray` finals, the int64 node / leaf counts (the natural vectorized result shape — no array of result objects) |
| `minimax_solve(gp, log=None, check_ec=False) -> SolverResult \| SolverResultArray` | the depth-first minimax over the game tree, scalar or array (the unified API): a GamePosition scalar gives the `SolverResult` of the direct compiled search, a `GamePositionArray` the `SolverResultArray` of the worker pool (one thread per CPU, dynamic dispatch — see Architecture); `log` is an optional callable invoked once per visited node, with the `NodeRecord` of the node, when the search of the node completes (scalar form only); `check_ec` (array form only, default False) runs the `uniform_empty_count` precondition check up front |
| `alphabeta_solve(gp, log=None, check_ec=False) -> SolverResult \| SolverResultArray` | the alpha-beta twin of `minimax_solve` (the same natural move order and strict tie-break, the zero-window propagation, the cutoff; the root window is the C ground-node initialization [−66, 66] — see Architecture), scalar or array (the same unified contract); the node / leaf counts are smaller than the minimax ones (the pruned subtrees are never visited) |
| `uniform_empty_count(gps) -> int` | the batch precondition check: all lanes share the same empty count (the message names the distinct counts and the lanes); raises `ValueError` when not uniform, returns the common count otherwise |

## Architecture

- **The search** is a plain recursive DFS (the scalar phase — the vectorized / numba phase is a later step). Every
  visited position is a node: `nodes` counts the root and the leaves, `leafs` counts the terminal positions
  evaluated.
- **The move order is static** (A1, A2, ..., H8): the legal-move bitset is scanned with the `bitboard_bsf`
  bit-scan (the ascending square order). In a tie of equal values the first move in that order is kept (the
  comparison is strict).
- **The values are relative**: the value of a child is negated at every ply, so the returned `game_value` is seen
  from the point of view of the player to move at the root (positive = that player wins the endgame).
- **The pass**: a player with no legal move hands the turn to the opponent — a further node (the same board, the
  other player), with the value coming back negated. A position where NEITHER player has a legal move is a leaf
  (one node, no pass): the terminal check precedes the pass.
- **The leaf value** is `game_position_final_value` (board.py, the WOF scoring: the empty squares are assigned to
  the winner, a draw is 0 — with or without empty squares).
- **The game tree is GamePosition-only**: the search composes the three GamePosition-level tools of board.py
  (`game_position_legal_moves`, `game_position_make_move`, `game_position_final_value`) — no `Position`, no
  mover / opponent handling, no standalone player in the solver code.
- **The compiled search is the only search**: `minimax_solve` runs the numba-compiled `_search` in both modes:
  the position travels as the three field scalars (numba cannot build the structured GamePosition scalar), the
  four public per-lane kernels of board.py (`legal_moves_of`, `flips_of_move`, `final_value_of`,
  `bitboard_bsf`) are inlined by the compiler. The throughput is flat at ~19 M nodes/s (machine
  dependent) across the ffo-01-simplified 0–5 series (the 18M-node case 0 in ~0.95 s). The trace is a
  typed-list sink inside the
  compiled search (one 6-int tuple per node, appended at the node exit, `None` in the untraced mode — the
  untraced specialization compiles the guards away); the records are replayed to the `log` callback when the
  search completes (the trace costs ~78 ms on the 20k-node case 4, the untraced path is untouched at ~1 ms).
- **The alpha-beta search** (`_ab_search`, the compiled twin of `_search`) adds the zero-window propagation
  (the child window is the negated CURRENT parent window) and the cutoff (a child value that reaches the node
  beta ends the move loop; the node exits with its alpha — a bound at a cutoff node, exact otherwise). The node
  best value starts at the window alpha: a fail-low node exits with its window alpha and `MOVE_NA`. The root
  window is the C ground-node initialization (the out-of-range sentinels [−66, 66]): the game-value range lies
  strictly inside it, the root value is exact, and the returned best line is the same line the minimax returns.
  The per-node data (the entry-order counter, the parent move, the alpha / beta window) is threaded through the
  4-element shared `state` array with the same save/restore stack discipline as `_search`, keeping the
  6-parameter signature (the 7th scalar parameter is the numba 0.68 cache-loader segfault trigger, D-662). On the
  ffo-01-simplified series the pruning is 9.9x–25x in node count (case 4: 2,029 vs 20,040; case 0: 1.7M vs 18M)
  at the same per-node throughput (~19 M nodes/s, machine dependent).
- **The array form is a worker pool, not a vectorized frontier** (the design decision of D-667, unified
  scalar / array API of D-669): the array input of both public solvers runs the batch lanes in parallel on a
  pool of worker threads (one per available CPU) with DYNAMIC dispatch (each worker pulls the next unsolved
  lane from the work queue — optimal for the 100x solve-cost variance between endgames), each worker running
  the compiled search of its engine (`_search` / `_ab_search`) DIRECTLY (the per-lane pydantic validation
  skipped — the batch boundary is the only checked one; the scalar input keeps the byte-identical direct
  path, the dispatch is one `isinstance` at the boundary). The njit search releases the GIL while running, so
  the wall time is the batch work over the worker count (~8x on this 8-core machine, measured). The lanes are
  expected to share the same empty count (the batch precondition, checked up front only when `check_ec=True`);
  the per-lane result is EXACTLY the scalar solve result of that lane (zero new search code — the
  D-664/665/666 node-level goldens carry over per lane for free). Scale: the 100 / 1000-lane regab batches
  (the ec=8 positions) solve in ~0.2–0.3 s wall (the 1000-lane batch: 2.3M nodes in 0.22 s, ~10.4 M
  lane-nodes/s — the pool keeps the scalar per-node rate, the lanes just run in parallel). The
  frontier-vectorized core (the lanes as search frontiers, the gather/scatter design) is parked in ideas.md
  as the candidate Rust feature: its numba payoff is limited (the irregular mask/gather control flow is not
  auto-vectorizable), and at 1M–10M batches it would need batching (1k–10k lanes) parallelized worker-pool
  style anyway.

## The trace

The `log` callback receives one `NodeRecord` per visited node, emitted when the search of the
node completes (the C game-tree log works the same way: the call id is assigned at the node
entry, the row is written at its exit). The six fields of the first trace version, each one
matching a column of the C log:

| field | C column | why it is there | where it comes from |
|---|---|---|---|
| `call_id` | `CALL_ID` | aligns the v2 records with the C log one to one | the node number, 1-based, assigned at entry |
| `level` | `CALL_LEVEL` | the shape of the tree | the search depth (1 = the root) |
| `player` | `PLAYER` | the anchor of the sign-flip semantics | the absolute player to move at the node |
| `parent_move` | `PARENT_MOVE` | reconstructs the path from the root | the move by which the parent reached the node (`MOVE_UN` at the root, `MOVE_PA` at the child of a pass) |
| `best_move` | `T_BEST_MOVE` | the decision of the node | the move chosen by the strict comparison (`MOVE_PA` at a pass node, `MOVE_NA` at a leaf) |
| `value` | `T_ALPHA` | the result of the search at the node | the final value of the node, seen from the player to move there (at the root, the game value) |

The C-internal columns (the Zobrist `HASH`, the absolute `BLACKS` / `WHITES` bitboards) are not
part of the record: they depend on the C hash constants and are not reproducible in v2. The
fields grow incrementally — each new field joins with its documented reason (the first
candidates: `is_leaf`, `empty_count`, the legal-move set).

The `T_BEST_MOVE` caveat (alpha-beta): in the C reference log the best move of a non-improving
node (a fail-low node that exits with its window alpha) is not defined by the search — the C node
struct never initializes `best_move` there, so the log carries the stale value of the previous
occupant of the stack slot. The v2 trace records `MOVE_NA` at such nodes, the only value
consistent with the search; a node-by-node comparison against the C log therefore skips
`best_move` where the v2 record is `MOVE_NA` (the minimax log is not affected: a minimax node
always improves or is a leaf).

## Verified invariants

- The search contract on hand-built endgames (the full-board terminals from both perspectives, the draw, the
  draw-with-empties-is-zero WOF case, the single-empties forced move, the equal-value tie keeping the first static
  move, the pass at the root) — `test_endgame_solver::TestMinimaxSolveMicro`.
- The exact solution of the `ffo-01-simplified` 0–8 series of the `gpdb-sample-games.txt` corpus (the generic
  case test: the value, the node / leaf counts, the final position, the solution line played to the final
  position; cases 0–3 are solve-only, the 18M-node case 0 is LONG-gated) —
  `test_endgame_solver::TestMinimaxSolveFixture`.
- The node-by-node trace: the `NodeRecord`s of each solve reproduce the C game-tree log of the case
  (`es_log_ffo-01-simplified-{4..8}.csv`) record by record, on the six comparable columns —
  `test_endgame_solver::TestMinimaxSolveFixture` (the trace tests).
- The exact solution of the `ffo-01-simplified` 0–8 series with the alpha-beta search (the same case
  test as the minimax, against the C alpha-beta reference counts; the solution line is the minimax
  one) — `test_endgame_solver::TestAlphaBetaSolveFixture`.
- The alpha-beta node-by-node trace against the C alpha-beta game-tree log
  (`ab_log_ffo-01-simplified-{4,6,7,8}.csv`) record by record, with the `T_BEST_MOVE` caveat of the
  trace section — `test_endgame_solver::TestAlphaBetaSolveFixture` (the trace tests).
- The alpha-beta / minimax agreement on the value and the final position of the 1–8 series (both
  searches are exact) — `test_endgame_solver::TestAlphaBetaSolveFixture::test_ab_minimax_parity`.
- The array solver on the worker-pool engine: the ten ec=8 lanes of the regab_prng_gp batch 7
  against the INDEPENDENT DB game-value goldens, the per-lane parity with the scalar solve (value,
  final, node / leaf counts), the mixed corner batch (the forced pass, the finished game, the
  wipe-out, a plain lane), the empty batch, and the `uniform_empty_count` / `check_ec` gate —
  `test_endgame_solver::TestAlphaBetaSolveArray`; the 100 / 1000-lane regab batches (the batches 8
  and 9, the ec=8 positions in seq order) against the INDEPENDENT DB game-value goldens, plus the
  PERF throughput printout of the 1000-lane batch —
  `test_endgame_solver::TestAlphaBetaSolveArrayScale`.
- The result container (the fields, the frozen behaviour) — `test_endgame_solver::TestSolverResult`.
- The int8-dtype contract of the `GameValueArray` validator —
  `test_endgame_solver::TestGameValueArrayValidator` (together with the tests above, they cover the
  module at 100% of the statements and branches).

## Open issues

- `_search` is `cache=True` again: numba 0.68 SEGFAULTS a fresh process that loads the cache of the
  7-parameter form (the one with the `parent_move` scalar) — bisected in scratch (the identical body
  with 6 parameters caches and reloads fine; adding the 7th scalar parameter crashes the loader). The
  workaround: `parent_move` lives in the 2-element shared `state` array (state[0] the entry-order
  counter, state[1] the current parent_move, saved/restored around each recursive call) instead of
  being a scalar parameter. To be revisited at the next numba upgrade (the scalar form may cache
  fine there).
- Next: the multi-ply evaluation alpha-beta (`alphabeta_eval`): the search descends to the
  ec-assigned horizon (earlier at the terminal, where the value is the exact WOF one) and the
  horizon leaf value is the REAL of the chosen evaluation function — the search-based evaluation
  (the value plus the root best move), a greenfield v2 design (no C reference). The move-ordered
  variants of the C reference (the `ev` estimated-value and `rglm` random-legal-move orders) and
  the frontier-vectorized core are parked (the latter in ideas.md, the candidate Rust feature for
  the 1M–10M-batch endgame).

## Conventions

- The module owns the SEARCH; the move execution, the legal-move generation, and the WOF leaf value belong to
  `board.py` (reused, not duplicated).
- `game_value` is an `np.int8` already in the scalar API (the value range is [-64..64] ⊂ int8).

## Integration

- Consumes: `board.py` (the three GamePosition-level tools `game_position_legal_moves` /
  `game_position_make_move` / `game_position_final_value` of the traced search, the four public per-lane kernels
  `legal_moves_of` / `flips_of_move` / `final_value_of` / `bitboard_bsf` of the compiled `_search`,
  `make_game_position` for the final-position repack, the `Move` / `Player` types,
  `MOVE_PA` / `MOVE_NA` / `MOVE_UN`).
- Consumed by: the test suite; the ENDGAME-SOLVER
  campaign (the `gpdb-ffo.txt` corpus is the cross-validation surface); `regab.py` (the `GameValue` /
  `GameValueArray` types — the database stores the values the solver produces).
