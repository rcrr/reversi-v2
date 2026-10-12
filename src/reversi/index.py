#
# index.py
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

from typing import TypeAlias, Annotated

import numpy as np
import numpy.typing as npt

from pydantic import BeforeValidator


__all__ = ['Index', 'IndexArray']

#: Represents a reversi pattern index.
Index: TypeAlias = np.uint32


def validate_index_array(v: any) -> any:
    """Ensure a numpy array strictly uses the uint32 dtype (scalars pass through)."""
    if isinstance(v, np.ndarray) and v.dtype != np.uint32:
        raise ValueError(f"Array dtype must be uint32, got {v.dtype}")
    return v


#: A Pydantic-compatible type hint for Index (np.uint32) arrays.
IndexArray = Annotated[npt.NDArray[np.uint32], BeforeValidator(validate_index_array)]
