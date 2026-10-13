#
# hlp_zed.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi-v2
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

import hashlib
import numpy as np
import numpy.typing as npt

from typing import TYPE_CHECKING, Tuple, Callable
from pydantic import validate_call, ConfigDict

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext


__all__ = ['LMZed',
           'hlp_zed_compute',
           'hlp_zed_fun_factory']


class LMZed:
    """Holds the Z vector and the transformation functions y2z and z2y."""

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self,
                 y2z: Callable[[npt.NDArray[np.int8]], npt.NDArray[np.float32]],
                 z2y: Callable[[npt.NDArray[np.float32]], npt.NDArray[np.float32]],
                 z: npt.NDArray[np.float32]):
        """
        Initialize the Zed data object from the two transformation closures and the z vector (all
        stored by reference).

        Args:
            y2z: the int8 -> float32 closure (the game values to the affine Z space).
            z2y: the float32 -> float32 inverse closure.
            z: the (N,) float32 Z vector (the affine image of the game values).
        """
        self.y2z = y2z
        self.z2y = z2y
        self.z = z

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def compute_sha3_256_hash(self) -> str:
        """
        Compute the sha3_256 hash of the z data vector.

        The two closures are NOT hashed (pure functions of the logit_clipping config, not stored on
        the object).

        Returns:
            str: the sha3_256 hex digest of the z tobytes.
        """
        hasher = hashlib.sha3_256()
        hasher.update(self.z.tobytes())
        sha3_256_hash = hasher.hexdigest()
        return sha3_256_hash


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_zed_fun_factory(logit_clipping: float) -> Tuple[Callable[[npt.NDArray[np.int8]], npt.NDArray[np.float32]],
                                                            Callable[[npt.NDArray[np.float32]], npt.NDArray[np.float32]]]:
    """
    Returns two functions that perform an affine transformation. One on int8 arrays, it maps the
    range [-64, 64] to [logit_clipping, 1 - logit_clipping]. The second does the inverted transformation.

    Args:
        logit_clipping: the float clipping bound c (the z range is [c, 1 - c]).

    Returns:
        y2z: the first closure (int8 -> float32).
        z2y: the second closure (float32 -> float32).
    """
    a = np.float32(0.5)
    b = np.float32((1. - 2. * logit_clipping) / 128.)
    def y_to_z(y: npt.NDArray[np.int8]) -> npt.NDArray[np.float32]:
        y = np.float32(y)
        z = a + y * b
        return z

    a1 = np.float32(-64. / (1. - 2. * logit_clipping))
    b1 = np.float32(128. / (1. - 2. * logit_clipping))
    def z_to_y(z: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
        y = a1 + z * b1
        return y

    return y_to_z, z_to_y


#: Here validation is not possible, it brings in a convoluted issue with circular imports.
def hlp_zed_compute(ctx: "LMContext") -> LMZed:
    """
    Compute the Z vector and the transformation functions from the logit_clipping.

    Args:
        ctx: the LMContext (the game values + the logit_clipping config).

    Returns:
        LMZed: the object (the two closures + the computed z vector).
    """
    alpha = ctx.cfg.stat_model.logit_clipping
    y2z, z2y = hlp_zed_fun_factory(alpha)
    y = ctx.game_values
    z = y2z(y)
    return LMZed(y2z=y2z, z2y=z2y, z=z)
