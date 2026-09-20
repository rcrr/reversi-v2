#
# hlp_gradient.py
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

from __future__ import annotations

from typing import TYPE_CHECKING, Tuple, Callable
import numpy as np
import numpy.typing as npt

from numba import njit, prange
from scipy.special import expit

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext

__all__ = ['hlp_gradient_compute', 'sigmoid']


def sigmoid(x: np.ndarray) -> np.ndarray:
    """
    Computes the sigmoid (logistic) function on the given array of float values.
    It was computed as:
      return 1. / (1. + np.exp(-x))
    The expit function from scipy provides more numerical stability for extreme values of x.
    """
    return expit(x)


#: The fixed block count (T) of the high-performance kernel: each
#: prange block owns a contiguous row range and accumulates into its
#: own private f64 gradient buffer, so the pass is race-free (numba
#: has no CPU atomics) and run-deterministic (the block split and the
#: final accumulation order are independent of the thread count).
_HP_BLOCKS = 8


@njit(parallel=True, cache=True)
def _hp_fg_kernel(X, w, z, g_blocks, norm_blocks):
    """
    The high-performance single-pass loss/gradient kernel.

    One streaming pass over the design matrix rows: for every row it
    gathers the linear predictor from w (L2-resident), computes the
    sigmoid, the residual, the per-row gradient weight and the
    squared-residual partial norm, and scatters the per-row weight
    into the block's private f64 gradient buffer. No M*P temporary is
    ever materialized: X is read once (row-contiguous) and all the
    working state (w, the per-block buffers) stays in L2.

    X : (M, P) uint32 — the design matrix (weight indices).
    w : (N,) float32  — the current weights.
    z : (M,) float32  — the target values.
    g_blocks : (T, N) float64 — one private gradient buffer per block.
    norm_blocks : (T,) float64 — one squared-residual partial sum per block.
    """
    M_ = X.shape[0]
    P_ = X.shape[1]
    T_ = g_blocks.shape[0]
    nb = (M_ + T_ - 1) // T_
    for b in prange(T_):
        i0 = b * nb
        i1 = i0 + nb
        if i1 > M_:
            i1 = M_
        g = g_blocks[b]
        norm_rn = 0.0
        for i in range(i0, i1):
            acc = np.float32(0.0)
            for j in range(P_):
                acc += w[X[i, j]]
            zhv = np.float32(1.0) / (np.float32(1.0) + np.exp(-acc))
            rn = zhv - z[i]
            vv = zhv * (np.float32(1.0) - zhv) * rn
            norm_rn += rn * rn
            for j in range(P_):
                g[X[i, j]] += vv
        norm_blocks[b] = norm_rn


#: Here validation is not possible, it brings in a convoluted issue with circular imports.
def hlp_gradient_compute(ctx: "LMContext",
                         high_performance: bool = False
                         ) -> Callable[[npt.NDArray[np.float32]], Tuple[np.float32, npt.NDArray[np.float32]]]:
    """
    Builds the function returning loss and gradient.
    Captures X, z, and alpha in a closure for fast repeated evaluations during optimization.
    The loss and gradient are normalized by the number of positions (M) to ensure
    dataset-size independent convergence criteria.

    high_performance: False (the default) returns the classic
    vectorized-numpy closure (proven, readable). True returns the
    high-performance closure: a single numba kernel (see
    _hp_fg_kernel) that computes loss and gradient in one streaming
    pass over the design matrix with no M*P temporaries. The two
    variants are mathematically identical; they differ only in the
    f32 rounding order (a few ulps on f and g), so a run with one
    variant follows a slightly different — but equivalent — L-BFGS
    trajectory than a run with the other. The returned closure
    carries a ``high_performance`` bool attribute identifying the
    variant. The float32 return contract is the same for both:
    (np.float32 f, (N,) float32 g).
    """
    N = len(ctx.w)
    X = ctx.design_matrix
    M, P = X.shape  # M is the number of positions
    z = ctx.z
    alpha = ctx.cfg.stat_model.ridge_regularization / M

    if not high_performance:
        X_flat = X.ravel()

        # Pre-allocate buffers for performance inside the closure
        bincount_weights_buffer = np.empty(M * P, dtype=np.float32)
        bincount_weights_view = bincount_weights_buffer.reshape(M, P)

        def fg(w: npt.NDArray[np.float32]) -> Tuple[np.float32, npt.NDArray[np.float32]]:
            linear_predictor = np.sum(w[X], axis=1)
            zh = sigmoid(linear_predictor)
            dzh = zh * (1. - zh)
            rn = zh - z

            # Normalized loss (Mean Squared Error + Ridge regularization)
            norm_rn = np.dot(rn, rn)
            norm_w = np.dot(w, w)
            f = 0.5 * ((norm_rn / M) + alpha * norm_w)

            # Normalized gradient
            dzh_rn = dzh * rn
            bincount_weights_view[:] = dzh_rn[:, None]
            g0 = np.bincount(X_flat, weights=bincount_weights_buffer, minlength=N) / M
            g1 = alpha * w
            g = g0 + g1

            return np.float32(f), g.astype(np.float32, copy=False)

        fg.high_performance = False
        return fg

    # The high-performance path: one kernel call per
    # evaluation; the private per-block f64 buffers are pre-allocated
    # once and cleared per call, and the final accumulation (the sum
    # over the T blocks, in fixed block order) is done in numpy.
    g_blocks = np.zeros((_HP_BLOCKS, N), dtype=np.float64)
    norm_blocks = np.zeros(_HP_BLOCKS, dtype=np.float64)

    def fg_hp(w: npt.NDArray[np.float32]) -> Tuple[np.float32, npt.NDArray[np.float32]]:
        g_blocks.fill(0.0)
        norm_blocks.fill(0.0)
        _hp_fg_kernel(X, w, z, g_blocks, norm_blocks)
        f = np.float32(0.5 * ((np.sum(norm_blocks) / M) + alpha * np.dot(w, w)))
        g = (g_blocks.sum(axis=0) / M + alpha * w).astype(np.float32)
        return f, g

    fg_hp.high_performance = True
    return fg_hp
