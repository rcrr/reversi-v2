# notes/naming.md — Naming convention (canonical, read once, apply always)

Recorded 2026-08-26 on Roberto's explicit instruction, after rejecting T08
(report §5.8): the analysis had imported chess vocabulary (file/rank) into a
Reversi project that speaks row/column. The code was correct; the analysis
vocabulary was not. This file is the single source of truth for board
vocabulary in this workspace — code, docs, notes, and replies all follow it.

## Board vocabulary — this is Reversi, not chess
- Never use "file" or "rank". The project vocabulary is **column** and
  **row**.
- 8 columns: A–H, left to right.
- 8 rows: 1–8, top to bottom.
- Square name: column letter first, then row number (A1, C4, H8).
- A1 = top-left corner (N-W).
- H8 = bottom-right corner (S-E).

## Bitboard
- The least significant bit (bit 0) is square A1.
- The most significant bit (bit 63) is square H8.
- row_1 = [A1 ... H1]
- column_a = [A1 ... A8]

## D8 — the eight board symmetries (canonical, fixed 2026-08-26)

The eight D8 symmetries are a geometric/algebraic property of the BOARD
itself. The order below is arbitrary but FIXED by Roberto's decision
(D-014) — do not reorder, rename, or "fix" it. Square names follow the
row/column convention above; A1 = top-left (bit 0), H8 = bottom-right
(bit 63).

Corner tracking uses the four corners in fixed order
[A1, H1, A8, H8] = [N-W, N-E, S-W, S-E]:

| slot | name    | transformation                                            | [A1, H1, A8, H8] maps to |
|------|---------|-----------------------------------------------------------|--------------------------|
| 0    | ro000   | identity                                                  | [A1, H1, A8, H8]         |
| 1    | ro090   | 90° rotation, clockwise                                   | [H1, H8, A1, A8]         |
| 2    | ro180   | 180° rotation (clockwise)                                 | [H8, A8, H1, A1]         |
| 3    | ro270   | 270° rotation clockwise (= 90° counter-clockwise)         | [A8, A1, H8, H1]         |
| 4    | fvert   | reflection on the median vertical axis (column a ↔ column h, rows fixed) | [H1, A1, H8, A8] |
| 5    | fh1a8   | reflection on the h1–a8 diagonal                          | [H8, H1, A8, A1]         |
| 6    | fhori   | reflection on the median horizontal axis (row 1 ↔ row 8, columns fixed) | [A8, H8, A1, H1] |
| 7    | fa1h8   | reflection on the a1–h8 diagonal                          | [A1, A8, H1, H8]         |

Anti-transformations, same slot order (the inverse of each
transformation):

| slot      | 0     | 1     | 2     | 3     | 4     | 5     | 6     | 7     |
|-----------|-------|-------|-------|-------|-------|-------|-------|-------|
| transform | ro000 | ro090 | ro180 | ro270 | fvert | fh1a8 | fhori | fa1h8 |
| anti      | ro000 | ro270 | ro180 | ro090 | fvert | fh1a8 | fhori | fa1h8 |

Defining property: for every slot, applying the transformation and then
its anti-transformation (in either order) returns the input board
unchanged — transformation ∘ anti-transformation = identity. The
rotations pair up (ro090⁻¹ = ro270, ro180⁻¹ = ro180); every reflection
is its own inverse.

The slot order above is exactly the output order of
`bitboard_transformations` / `bitboard_anti_transformations` in
src/twolm/board.py and of the orbit test classes in
src/twolm/test/test_board.py. Code, tests, and the docstring diagrams
were re-verified cell-by-cell on 2026-08-26 (T16, D-014): they agree.

Reading rule for every board diagram in this workspace: row 1 on top,
column a on the left. Under any other reading (e.g. row 1 at the
bottom) the same bit pattern appears as the wrong symmetry (clockwise
becomes counter-clockwise, left-right mirrored, etc.) — that
convention slip is what produced the false "diagram is wrong" verdicts
of report §6 item T16.
