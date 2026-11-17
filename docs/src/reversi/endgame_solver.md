# reversi/endgame_solver.py
The scalar exact endgame solver. `minimax_solve` searches the whole game tree of an endgame with a depth-first
minimax and returns the game value, the terminal game position of the best line, and the search counters.

## API

The 2 `__all__` names.

| name | contract |
|---|---|
| `GameValue` | the game-value type: `np.int8` (a value from -64 to +64) — defined here, the solver is the producer of game values; `regab.py` imports it from this module |
| `GameValueArray` | the pydantic-validated `NDArray[np.int8]` game-value array type (the int8-dtype `BeforeValidator`) — defined here with `GameValue` |
| `NodeRecord` | the frozen dataclass `(call_id, level, player, parent_move, best_move, value)` — one visited node of the search, as emitted to the `log` callback (see The trace); the move fields are never `None` (the sentinel codes `MOVE_UN` / `MOVE_NA` / `MOVE_PA` express the absences) |
| `SolverResult` | the frozen dataclass `(game_value, final_game_position, nodes, leafs)`: the value is an `np.int8` (the vectorized future's type, kept here for conformance), the final position is a GamePosition scalar (`GamePositionField`) |
| `minimax_solve(gp, log=None) -> SolverResult` | the depth-first minimax over the game tree of the GamePosition scalar `gp` (see Architecture for the search contract); `log` is an optional callable invoked once per visited node, with the `NodeRecord` of the node, when the search of the node completes |

## Architecture

- **The search** is a plain recursive DFS (the scalar phase — the vectorized / numba phase is a later step). Every
  visited position is a node: `nodes` counts the root and the leaves, `leafs` counts the terminal positions
  evaluated.
- **The move order is static** (A1, A2, ..., H8): the legal-move bitset is scanned square by square in index
  order. In a tie of equal values the first move in that order is kept (the comparison is strict).
- **The values are relative**: the value of a child is negated at every ply, so the returned `game_value` is seen
  from the point of view of the player to move at the root (positive = that player wins the endgame).
- **The pass**: a player with no legal move hands the turn to the opponent — a further node (the same board, the
  other player), with the value coming back negated. A position where NEITHER player has a legal move is a leaf
  (one node, no pass): the terminal check precedes the pass.
- **The leaf value** is `position_final_value` (board.py, the WOF scoring: the empty squares are assigned to the
  winner, a draw is 0 — with or without empty squares).

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

## Verified invariants

- The search contract on hand-built endgames (the full-board terminals from both perspectives, the draw, the
  draw-with-empties-is-zero WOF case, the single-empties forced move, the equal-value tie keeping the first static
  move, the pass at the root) — `test_endgame_solver::TestMinimaxSolveMicro`.
- The exact solution of the `ffo-01-simplified-8` fixture position (the value 18, the final position, the 46 nodes
  / 15 leaves, the A1-B1-H1-G2 solution line) — `test_endgame_solver::TestMinimaxSolveFixture`.
- The node-by-node trace: the 46 `NodeRecord`s of the `ffo-01-simplified-8` solve reproduce the C
  game-tree log record by record, on the six comparable columns —
  `test_endgame_solver::TestMinimaxSolveFixture` (the trace test).
- The result container (the fields, the frozen behaviour) — `test_endgame_solver::TestSolverResult`.
- The int8-dtype contract of the `GameValueArray` validator —
  `test_endgame_solver::TestGameValueArrayValidator` (together with the tests above, they cover the
  module at 100% of the statements and branches).

## Open issues

- The search is pure Python: fine for the small endgames of the test / POC phase, the vectorized numba phase is
  the next step of the campaign.

## Conventions

- The module owns the SEARCH; the move execution, the legal-move generation, and the WOF leaf value belong to
  `board.py` (reused, not duplicated).
- `game_value` is an `np.int8` already in the scalar API (the value range is [-64..64] ⊂ int8).

## Integration

- Consumes: `board.py` (`position_legal_moves`, `position_make_move`, `position_final_value`,
  `make_position`, `make_game_position`, the `Move` / `Player` types, `MOVE_PA`).
- Consumed by: the test suite; the future `alpha_beta` solver (the shared `SolverResult`); the ENDGAME-SOLVER
  campaign (the `gpdb-ffo.txt` corpus is the cross-validation surface); `regab.py` (the `GameValue` /
  `GameValueArray` types — the database stores the values the solver produces).
