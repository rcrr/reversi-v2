# reversi/endgame_solver.py
The scalar exact endgame solver. `minimax_solve` searches the whole game tree of an endgame with a depth-first
minimax and returns the game value, the terminal game position of the best line, and the search counters.

## API

The 2 `__all__` names.

| name | contract |
|---|---|
| `SolverResult` | the frozen dataclass `(game_value, final_game_position, nodes, leafs)`: the value is an `np.int8` (the vectorized future's type, kept here for conformance), the final position is a GamePosition scalar |
| `NodeRecord` | the frozen dataclass of one traced node: `call_id`, `level`, `player`, `parent_move`, `best_move`, `value` (see The trace) |
| `minimax_solve(gp, log=None) -> SolverResult` | the depth-first minimax over the game tree of the GamePosition scalar `gp` (see Architecture for the search contract); the optional `log` callback receives one NodeRecord per visited node, at the node's exit |

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

`minimax_solve` accepts an optional `log` callback: one `NodeRecord` per visited node, emitted at the node's exit.
The record is the projection of the legacy C game-tree log columns that the Python solver owns (the C-internal
columns — the Zobrist hash, the absolute colours — are not part of the record):

| field | C log column | why / where |
|---|---|---|
| `call_id` | `CALL_ID` | the node's id in the search: 1 at the root, assigned in visit order |
| `level` | `CALL_LEVEL` | the depth in the tree: 1 at the root |
| `player` | `PLAYER` | the absolute player to move at the node |
| `parent_move` | `PARENT_MOVE` | the move that led to the node: `None` at the root, the pass for a pass node |
| `best_move` | `T_BEST_MOVE` | the node's best move: `None` at a leaf, the pass at a pass node |
| `value` | `T_ALPHA` | the node's value from the point of view of the player to move there |

The first version keeps only the fields needed to cross-validate the solution line and the search shape; further
fields (the leaf / empties / legal-move details) are added incrementally, each with its own why/where row.

## Verified invariants

- The search contract on hand-built endgames (the full-board terminals from both perspectives, the draw, the
  draw-with-empties-is-zero WOF case, the single-empties forced move, the equal-value tie keeping the first static
  move, the pass at the root) — `test_endgame_solver::TestMinimaxSolveMicro`.
- The exact solution of the `ffo-01-simplified-8` fixture position (the value 18, the final position, the 46 nodes
  / 15 leaves, the A1-B1-H1-G2 solution line) — `test_endgame_solver::TestMinimaxSolveFixture`.
- The result container (the fields, the frozen behaviour) — `test_endgame_solver::TestSolverResult`.
- The node-by-node trace of the `ffo-01-simplified-8` solution: the 46 records match the C game-tree log one to
  one — `test_endgame_solver::TestMinimaxSolveFixture::test_ffo_01_simplified_8_trace`.

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
- Consumed by: the test suites and the probes that need documented position batches; the ENDGAME-SOLVER
  campaign (the `gpdb-ffo.txt` corpus is the cross-validation surface).
