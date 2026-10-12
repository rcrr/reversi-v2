#
# test_index.py
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

# How to run the index unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.test_index
#

import unittest

import numpy as np

from reversi.index import Index, IndexArray, validate_index_array


class TestIndex(unittest.TestCase):
    """The Index alias is np.uint32 (the base-3 pattern index space)."""

    def test_index_is_uint32(self):
        self.assertIs(Index, np.uint32)


class TestIndexArray(unittest.TestCase):
    """The IndexArray validator: the ndarray dtype is enforced, non-arrays pass through."""

    def test_rejects_non_uint32_ndarray(self):
        with self.assertRaises(ValueError) as context:
            validate_index_array(np.array([1, 2, 3], dtype=np.uint64))
        self.assertIn("uint32", str(context.exception))

    def test_passes_uint32_ndarray(self):
        a = np.array([1, 2, 3], dtype=np.uint32)
        self.assertIs(validate_index_array(a), a)

    def test_passes_non_array(self):
        v = np.uint32(7)
        self.assertIs(validate_index_array(v), v)

    def test_index_array_is_annotated(self):
        # The pydantic Annotated wrapper carries the BeforeValidator metadata.
        self.assertIn("BeforeValidator", str(IndexArray))


if __name__ == "__main__":
    unittest.main()
