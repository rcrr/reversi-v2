# test/reversi/test_endgame_solver.py

The endgame_solver unit suite — 4 classes / 26 tests (25 + the LONG-gated case 0), no DB; the runtime is
dominated by the five traced fixture solves (the trace is the Python search — the numba fast path is the
untraced one). Companion of docs/src/reversi/endgame_solver.md.

## Coverage

| class | tests | what it pins |
|---|---|---|
| `TestSolverResult` | 2 | the result container: the fields (the `np.int8` game value, the final position, the counters) and the frozen behaviour |
| `TestGameValueArrayValidator` | 3 | the int8-dtype contract of the `GameValueArray` validator (moved here with the type in the regab→endgame_solver transfer): the int8 array passes through (identity), the non-int8 array raises, the non-array input passes through |
| `TestMinimaxSolveMicro` | 7 | the search contract on hand-built endgames: the full-board terminal from both perspectives (+16 / −16), the full-board draw (0), the draw-with-48-empties-is-zero (the WOF ruling), the single-empties forced move (+4, 2 nodes / 1 leaf), the equal-value tie keeping the first static move (−14, the A1 line's final), the pass at the root (+10, 3 nodes / 1 leaf) — every case pins the value, the final position, and the node / leaf counts |
| `TestMinimaxSolveFixture` | 14 | the generic fixture test over the `ffo-01-simplified` 0–8 series of the `gpdb-sample-games.txt` corpus (loaded with the gpdb module): one `CASES` entry per case (the value, the node / leaf counts, the final position string, the solution line) — the solve method pins the value, the node / leaf counts, the final position, and the solution line played to the final position (on the numba fast path); the trace method (cases 4–8 only) reproduces the C game-tree log of the case (the `es_log_ffo-01-simplified-{4..8}.csv` fixtures) record by record, on the six comparable columns (call id, level, player, parent move, best move, value). The 18M-node case 0 is LONG-gated |

## Goldens pinned

- The `ffo-01-simplified` 0–8 solutions: the values (18 / −18 / 18 / −18 / 18 / −18 / 18 / −18 / 18), the
  node / leaf counts (18055194/5316151, 1111408/322891, 261482/78435, 105203/32174, 20040/6201, 2256/644,
  519/153, 142/44, 46/15), the final 65-char strings, the solution lines.
- The `ffo-01-simplified` 4–8 traces: the records, one to one with the C log rows (sorted by the call id on
  both sides).
- The micro endgames: the seven (value, final, nodes, leafs) quadruples above.

## Conventions

- The fixture positions are loaded with the gpdb module (`load_game_position_database` + `find`) — the module was
  written for this.
- The micro endgames are 65-char string literals: the boards are built so that the intended shape (the legal-move
  sets, the passes, the ties) is what the asserts pin.

## Integration

- Module under test: `endgame_solver.md`.
- The 65-char string↔GamePosition conversion and the three GamePosition-level game-tree tools are pinned in
  `test_board.md` (the `TestGamePosition` area F) — this suite exercises the SEARCH on top of them.
