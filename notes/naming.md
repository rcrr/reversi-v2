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
