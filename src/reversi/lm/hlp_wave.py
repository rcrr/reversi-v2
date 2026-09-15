#
# hlp_wave.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi
#
# Author Roberto Corradini mailto:rob_corradini@yahoo.it
# Copyright 2026 Roberto Corradini. All rights reserved.
#
# License
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

"""
The concurrent WAVE generator (the I-017 T5, the D-174
corpus generator): a batch of W games ("lanes") advanced in
LOCKSTEP on a SINGLE GLOBAL MT19937 (the project's
golden-pinned PRNG, the "one seed for all" pin, the numba
batch draw of tools/prng.py — the single source, the D-194
move; bit-exact vs the T3 oracle). One draw per (lane, step)
in lane order, W draws
per step: the real-move lanes pick the (draw % k)-th set
bit (the modulo bias < k/2^64, 12 orders below the noise
floor); the pass/dead lanes' draws are CONSUMED (unused).
The stream is GLOBAL across waves (the run is one stream,
the (wave, step, lane) order). This is the I-017 CORPUS
GENERATOR (the 1e7 build).

THE LOCKSTEP INVARIANT (Roberto's option A, refined): one
wave STEP = one REAL MOVE per live lane. A needed pass FOLDS
INTO the step (the pass lane's real move comes from the
swapped side's legal set — the second Kogge-Stone pass of
the step), so a pass adds NO step. Every
real move occupies exactly one square (the flips recolor,
they do not add stones), so after S = 60 - ec_target steps
every live lane is at EXACTLY ec_target — the harvest is
the WHOLE wave at the boundary: no ragged exits, no per-
step harvest mask, no inline respawns. The "brutish" logic
(the gathers, the respawns, the dead-lane bookkeeping)
lives in the rare per-wave boundary code; the hot step is
five full-wave vectorized calls, zero per-lane branching.

THE DOUBLE PASS is the game over (as the fixed T4 loop):
at a step, lm == 0 AND lo == 0 (the mover has no legal
move and, after the pass, the opponent has none either —
the board is unchanged, so the state is terminal, full or
not) kills the lane: it COASTS (its applied move is PA —
the documented kernel swap, a harmless field flip in a
discarded state: the swap is the only input that cannot
corrupt the stale position, since the kernel's legality
test is "flips non-zero" and an occupied square with a
flipping ray would be APPLIED — the board.py latent
finding, flagged to Roberto), its counter freezes, it is
NOT harvested at the boundary,
and it respawns there with the next slot. Dead lanes are
rare (a non-full double pass is < 0.2% of random games) —
their coasting wastes < 0.1% of the compute.

THE HOT STEP (all full-wave, uniform):

    lm = legal_moves(M, O)             (D-111 Kogge-Stone)
    lo = legal_moves(O, M)             (the pass lanes' source)
    pass_mask = (lm == 0)
    dead      = pass_mask & (lo == 0)  (the double pass)
    move      = _pick_g0(draws, where(pass_mask, lo, lm))
    move      = where(dead, PA, move)   (the dead lanes ride
                                         the documented
                                         swap)
    (M, O)    = make_move(where(pass_mask & ~dead,
                                (O, M), (M, O)), move)
    counter   += ~dead                 (the real move walks
                                        the counter; the
                                        pass does not)

THE SINK (v1): the arrested POSITIONS only (mover, opp,
slot) in boundary chunks — "di quello si prendono le
statistiche" (Roberto). The file writer (the corpus format,
the POSITIONS step D-157 alignment) is the T6 concern.
"""

from __future__ import annotations

import numpy as np
import numba as nb

from reversi.board import legal_moves, make_position, position_make_move
from reversi.tools.prng import NN, mt19937_batch_draw, mt19937_init

__all__ = ['INITIAL_MOVER', 'INITIAL_OPP', 'PA', 'MAX_EC',
           'WaveState', 'BufferSink', 'make_wave',
           'step_wave_g0', 'run_wave_g0']

#: The standard start (the official Othello setup —
#: random_game.initial_game_position is the canonical
#: source): the mover (black, the starting player) holds
#: E4+D5, the opponent (white) D4+E5 — A1 = top-left =
#: bit 0.
INITIAL_MOVER: np.uint64 = np.uint64(0x0000000810000000)
INITIAL_OPP: np.uint64 = np.uint64(0x0000001008000000)

#: The pass move code (board.py Move domain: 0..63 squares,
#: 64 = PA). Never APPLIED by the wave (the pass is the
#: source swap) — the constant is for the trace helpers.
PA: int = 64

#: The maximum initial ec (64 squares - 4 start stones).
MAX_EC: int = 60

# The G0 stream (the single global golden-pinned MT19937)
# lives in tools/prng.py — the SINGLE SOURCE (the D-194
# move): the NN constant + the mt19937_init /
# mt19937_batch_draw numba kernels, imported below.


class WaveState:
    """
    The wave arrays (the W lanes) + the run bookkeeping.
    Plain arrays (no dataclass: the numba-friendly plain
    layout, the tests mutate them directly as a seam).

    Attributes:
      W:          the lane count.
      slot_base:  the first slot id of this wave (the slot
                 ids run ONWARD across waves — a lane that
                 dies consumes its slot and is not
                 harvested; the harvested slots are
                 therefore unique but NOT contiguous).
      mover/opp:  the lane bitboards (u64).
      counter:    the per-lane step counter (i64) — the
                 phase pin: counter0 = the slot id.
      slot:       the per-lane slot id (i64, provenance).
      alive:      the live-lane mask (bool).
      next_slot:  the next slot id to hand out.
      steps:      the real-move steps done in the current
                 wave (0..60-ec_target).
      harvested:  the positions delivered so far (the run).
      dead_total: the lanes killed so far (the double
                 passes, incl. coasted steps).
    """

    def __init__(self, W: int, slot_base: int):
        self.W = int(W)
        self.slot_base = int(slot_base)
        self.mover = np.full(W, INITIAL_MOVER, dtype=np.uint64)
        self.opp = np.full(W, INITIAL_OPP, dtype=np.uint64)
        self.slot = np.arange(slot_base, slot_base + W,
                             dtype=np.int64)
        self.counter = self.slot.copy()
        self.alive = np.ones(W, dtype=np.bool_)
        self.next_slot = slot_base + W
        self.steps = 0
        self.harvested = 0
        self.dead_total = 0


def make_wave(W: int, slot_base: int = 0) -> WaveState:
    """A fresh wave of W lanes at the initial position,
    slots slot_base..slot_base+W-1, counter = slot (the
    T5 slot pin)."""
    return WaveState(W, slot_base)


# ---------------------------------------------------------------------
# The G0 pick (D-174 — the corpus generator; the bit-verified
# kernel, the D-173 gate origin). The G0 stream (the MT19937
# init + the batch draw) is tools/prng.py — the single source
# (the D-194 move).
# ---------------------------------------------------------------------


@nb.njit(parallel=True, cache=True)
def _pick_g0(draws, src):
    """The G0 uniform pick: rank = draw % k (the modulo
    bias < k/2^64, 12 orders below the noise floor);
    k == 0 -> (PA, no step). The HW popcount (numba has no
    .bit_count on uint64)."""
    n = src.shape[0]
    move = np.empty(n, dtype=np.uint8)
    step = np.empty(n, dtype=np.bool_)
    for i in nb.prange(n):
        x = src[i]
        c = x - ((x >> 1) & np.uint64(0x5555555555555555))
        c = (c & np.uint64(0x3333333333333333)) + \
            ((c >> 2) & np.uint64(0x3333333333333333))
        c = (c + (c >> 4)) & np.uint64(0x0F0F0F0F0F0F0F0F)
        k = int((c * np.uint64(0x0101010101010101)) >> 56)
        if k == 0:
            move[i] = np.uint8(PA)
            step[i] = False
            continue
        rank = int(draws[i] % np.uint64(k))
        y = x
        for _ in range(rank):
            y &= y - np.uint64(1)
        lb = y & -y
        square = 0
        while lb > np.uint64(1):
            lb >>= 1
            square += 1
        move[i] = np.uint8(square)
        step[i] = True
    return move, step


def step_wave_g0(state: WaveState, mt: np.ndarray,
                 mti: int
                 ) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """
    One lockstep step, the G0 uniform pick (D-174): the
    SAME step logic (the pass folded, the
    double-pass coast, the counter walk) with the pick
    from the GLOBAL MT19937 stream — W draws per step,
    lane order, the pass/dead lanes' draws consumed
    (unused). Returns (move, pass_mask, dead, mti) — the
    updated stream index (the caller threads it through
    the run, the stream is global across waves).
    """
    M, O = state.mover, state.opp
    lm = legal_moves(M, O)
    lo = legal_moves(O, M)
    pass_mask = lm == 0
    dead = pass_mask & (lo == 0)
    src = np.where(pass_mask, lo, lm)
    draws, mti = mt19937_batch_draw(mt, mti, state.W)
    move, _ = _pick_g0(draws, src)
    # The dead lanes ride the PA SWAP (the documented
    # kernel behaviour — the same rationale as the G0 step).
    move = np.where(dead, np.uint8(PA), move)
    swapped = pass_mask & ~dead
    out = position_make_move(
        make_position(np.where(swapped, O, M),
                      np.where(swapped, M, O)), move)
    state.mover[:], state.opp[:] = out['mover'], out['opponent']
    state.counter += (~dead).astype(np.int64)
    if dead.any():
        state.alive &= ~dead
        state.dead_total += int(dead.sum())
    state.steps += 1
    return move, pass_mask, dead, mti


def _harvest_and_respawn(state: WaveState, sink, total: int) -> int:
    """
    The boundary: the live lanes are ALL at exactly
    ec_target (the lockstep invariant) — gather them (in
    slot order), deliver to the sink (truncating to the
    run's remaining quota — deterministic: the first
    `remaining` alive lanes in array order), and reseed
    the WHOLE wave (harvested + dead) with fresh slots.
    """
    remaining = total - state.harvested
    idx = np.nonzero(state.alive)[0]
    n = min(int(idx.size), remaining)
    if n:
        sink.add(state.mover[idx[:n]], state.opp[idx[:n]],
                 state.slot[idx[:n]])
    state.mover[:] = INITIAL_MOVER
    state.opp[:] = INITIAL_OPP
    # The fresh slots: ONWARD, one per lane (a scalar here
    # would collapse the wave to a single slot — the phase
    # pin is the per-lane slot id).
    state.slot[:] = state.next_slot + \
        np.arange(state.W, dtype=np.int64)
    state.counter[:] = state.slot
    state.next_slot += state.W
    state.alive[:] = np.ones(state.W, dtype=np.bool_)
    state.steps = 0
    state.harvested += n
    return n


class BufferSink:
    """
    The in-memory sink (v1): the boundary chunks
    (mover, opp, slot) kept in RAM. The 1e6 benchmark
    holds ~24 MB. The file writer (the corpus format, the
    POSITIONS step D-157 alignment) is the T6 concern.
    """

    def __init__(self):
        self.chunks: list[tuple[np.ndarray, np.ndarray,
                                np.ndarray]] = []
        self.count = 0

    def add(self, mover: np.ndarray, opp: np.ndarray,
            slot: np.ndarray) -> None:
        self.chunks.append((mover.copy(), opp.copy(), slot.copy()))
        self.count += int(mover.size)

    def flatten(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """The (mover, opp, slot) arrays over all chunks
        (the slot order, then the chunk order)."""
        if not self.chunks:
            empty = np.empty(0)
            return (empty.astype(np.uint64),
                    empty.astype(np.uint64),
                    empty.astype(np.int64))
        return (np.concatenate([c[0] for c in self.chunks]),
                np.concatenate([c[1] for c in self.chunks]),
                np.concatenate([c[2] for c in self.chunks]))


def run_wave_g0(total: int, ec_target: int, seed: int,
                wave_size: int, sink: BufferSink,
                slot_base: int = 0) -> dict:
    """
    The G0 corpus generator (D-174): the same lockstep
    waves, the G0 uniform pick on the GLOBAL MT19937
    stream (one seed, the "one for the JSON" pin — the
    stream is global across waves: the (wave, step, lane)
    draw order). Deterministic in (seed, slot_base): the
    same seed + slot_base replay bit-exactly.

    Returns:
      The run provenance: {'harvested', 'waves',
      'next_slot', 'dead', 'mti' (the final stream index —
      the provenance pin)}.
    """
    if not (0 <= int(ec_target) <= MAX_EC):
        raise ValueError(
            f"ec_target {ec_target} is out of the [0, {MAX_EC}] domain")
    steps_per_wave = MAX_EC - int(ec_target)
    state = make_wave(int(wave_size), int(slot_base))
    mt = np.zeros(NN, dtype=np.uint64)
    mti = mt19937_init(mt, int(seed))
    waves = 0
    while state.harvested < total:
        for _ in range(steps_per_wave):
            _, _, _, mti = step_wave_g0(state, mt, mti)
        _harvest_and_respawn(state, sink, int(total))
        waves += 1
    return {'harvested': state.harvested, 'waves': waves,
            'next_slot': state.next_slot, 'dead': state.dead_total,
            'mti': mti}
