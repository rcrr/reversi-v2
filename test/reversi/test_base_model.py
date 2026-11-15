#
# test_base_model.py
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

# How to run the base model unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time PERF=0 python3 -m unittest test.reversi.test_base_model
#

import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

from reversi.base_model import BaseModel
from reversi.tools.state_machine import Context, StateMachine, Verbosity, Worker


class TestBaseModelFacade(unittest.TestCase):
    """The BaseModel facade: the delegation contract to the StateMachine (3 mock workers, no DB)."""

    def setUp(self):
        self.patcher = patch('sys.stdout', new=StringIO())
        self.patcher.start()
        self.up = [MagicMock() for _ in range(3)]
        self.down = [MagicMock() for _ in range(3)]
        self.context = Context()
        self.workers = [Worker(n, self.up[i], self.down[i])
                        for i, n in enumerate(("A", "B", "C"))]
        self.model = BaseModel(self.workers, self.context)

    def tearDown(self):
        self.patcher.stop()

    def test_construction_builds_the_machine(self):
        self.assertIsInstance(self.model.sm, StateMachine)
        self.assertIs(self.model.context, self.context)
        self.assertEqual(self.model.current_step, 0)

    def test_step_delegation(self):
        self.model.move_to_step(2)
        self.assertEqual(self.model.current_step, 2)
        self.assertEqual(self.model.current_worker_name, "C")

    def test_move_to_last(self):
        self.model.move_to_last()
        self.assertEqual(self.model.current_step, 2)

    def test_verbosity_property(self):
        self.model.verbosity = Verbosity.LOW
        self.assertEqual(self.model.verbosity, Verbosity.LOW)

    def test_run_drives_to_the_named_target(self):
        self.model.run("B")
        self.assertEqual(self.model.current_step, 1)
        self.up[1].assert_called_once_with(self.context)
        self.up[2].assert_not_called()

    def test_run_last_string_goes_to_the_end(self):
        self.model.run("last")
        self.assertEqual(self.model.current_step, 2)
        self.up[1].assert_called_once()
        self.up[2].assert_called_once()

    def test_run_default_uses_the_configured_target(self):
        self.model.run()
        self.assertEqual(self.model.current_step, 2)

    def test_run_is_a_resume(self):
        self.model.run("B")
        self.model.run("C")
        self.assertEqual(self.model.current_step, 2)
        self.assertEqual(self.up[1].call_count, 1)  # B is not re-run
        self.up[2].assert_called_once_with(self.context)

    def test_configured_target_defaults_to_none(self):
        self.assertIsNone(self.model._configured_target_level())


if __name__ == "__main__":
    unittest.main()
