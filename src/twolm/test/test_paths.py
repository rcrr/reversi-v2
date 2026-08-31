#
# test_paths.py
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

#
#
# How to run the paths unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest twolm.test.test_paths
#



import unittest

from twolm.test import paths



class TestPaths(unittest.TestCase):
    """Tests for the twolm.test.paths workspace-root constants (D-085)."""

    def test_workspace_root_holds_the_marker(self):
        """WORKSPACE_ROOT is absolute and holds the pyproject.toml marker."""
        self.assertTrue(paths.WORKSPACE_ROOT.is_absolute())
        self.assertTrue((paths.WORKSPACE_ROOT / "pyproject.toml").is_file())

    def test_workspace_root_is_ancestor_of_this_file(self):
        """The root contains the test package this file belongs to."""
        self.assertTrue((paths.WORKSPACE_ROOT / "src" / "twolm" / "test" / "paths.py").is_file())

    def test_custom_tmp_base_is_under_the_root(self):
        """CUSTOM_TMP_BASE is exactly <root>/build/tmp, absolute."""
        self.assertEqual(paths.CUSTOM_TMP_BASE, paths.WORKSPACE_ROOT / "build" / "tmp")
        self.assertTrue(paths.CUSTOM_TMP_BASE.is_absolute())


if __name__ == '__main__':
    unittest.main()
