#
# test_fixtures.py
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

"""
Unit tests for the rebuildable LM test fixtures helper (test/reversi/fixtures.py): the path
helpers, the fixture config set content (all five members, rlm_04 as the reference), the
consumer gate (require_lm_fixture) and the create idempotency — all STATIC (no pipeline run,
no DB, no artifact required): the build itself is a manual, seconds-long operation proven by
the first consumer.
"""

import json5
import unittest
from pathlib import Path
from unittest import mock

from test.reversi import fixtures

#: The fixture set: the multi-ply EF family, the full ec20...ec0 ladder (the depth-ladder
#: member set A = ec20 over B = ec20...ec16 -> depths 0...4 plus the deep-search members
#: ec15...ec0, for the in-search terminal / pass-branch tests).
ECS = (20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
FIXTURES = {ec: f'rlm_fixture_simple_ec{ec}' for ec in ECS}
FIXTURE = FIXTURES[20]  # the gate / idempotency tests run on the ec20 member


class TestFixturePaths(unittest.TestCase):
    """The path helpers derive the house layout."""

    def test_config_path(self):
        self.assertEqual(
            fixtures.lm_fixture_config_path(FIXTURE),
            Path('test/reversi/data/rlm_fixture_simple_ec20.json'))

    def test_fixture_dir(self):
        self.assertEqual(
            fixtures.lm_fixture_dir(FIXTURE),
            Path('build/tmp/fixtures/rlm_fixture_simple_ec20'))

    def test_model_path(self):
        self.assertEqual(
            fixtures.lm_fixture_model_path(FIXTURE),
            Path('build/tmp/fixtures/rlm_fixture_simple_ec20/rlm_fixture_simple_ec20.dat'))


class TestFixtureConfigs(unittest.TestCase):
    """The committed fixture configs carry the fixture contract (all five members)."""

    @classmethod
    def setUpClass(cls):
        # The house .json data files are json5 (the /* ... */ comment header + the trailing
        # commas) — parsed with the pipeline's own loader.
        cls.cfgs = {
            name: json5.loads(fixtures.lm_fixture_config_path(name).read_text())
            for name in FIXTURES.values()
        }
        cls.rlm04 = json5.loads(Path('test/reversi/data/rlm_04.json').read_text())

    def test_identity(self):
        for ec, name in FIXTURES.items():
            with self.subTest(ec=ec):
                self.assertEqual(self.cfgs[name]['name'],
                                 f'RGLM (Logistic) - LM fixture simple ec{ec} ({name}.json)')
                self.assertEqual(self.cfgs[name]['empty_count'], ec)

    def test_output_location(self):
        for ec, name in FIXTURES.items():
            with self.subTest(ec=ec):
                self.assertEqual(self.cfgs[name]['base_dir'], f'build/tmp/fixtures/{name}')
                self.assertEqual(self.cfgs[name]['output'], f'{name}.dat')

    def test_fixture_flags(self):
        for name in self.cfgs:
            with self.subTest(fixture=name):
                self.assertIs(self.cfgs[name]['regab_allow_duplicate'], False)
                self.assertFalse(self.cfgs[name]['plot']['enable'])

    def test_rlm_04_inheritance(self):
        # The training-relevant sections are the rlm_04 ones, untouched (rlm_04 is the
        # direct reference — no hardcoded values).
        for name in self.cfgs:
            with self.subTest(fixture=name):
                for section in ('stat_model', 'optimization', 'feature_set',
                                 'regab_data_set', 'validation_data_set'):
                    self.assertEqual(self.cfgs[name][section], self.rlm04[section])


class TestRequireLmFixture(unittest.TestCase):
    """The consumer gate: the path when present, the actionable error when missing."""

    def test_not_existing_fixture_raises(self):
        # A name with no config and no artifact (it is never built): the gate raises the
        # actionable RuntimeError, naming the exact build command. Direct, no mock — the
        # missing state is the real one.
        with self.assertRaises(RuntimeError) as ctx:
            fixtures.require_lm_fixture('not_existing_fixture')
        msg = str(ctx.exception)
        self.assertIn('python -m test.reversi.fixtures create not_existing_fixture', msg)
        self.assertIn('build/tmp/fixtures/not_existing_fixture/not_existing_fixture.dat', msg)

    def test_present_returns_path(self):
        with mock.patch.object(fixtures, 'FIXTURE_ROOT', Path('/nonexistent/root')):
            with mock.patch.object(Path, 'is_file', return_value=True):
                self.assertEqual(
                    fixtures.require_lm_fixture(FIXTURE),
                    fixtures.lm_fixture_model_path(FIXTURE))

    def test_missing_names_the_build_command(self):
        with mock.patch.object(fixtures, 'FIXTURE_ROOT', Path('/nonexistent/root')):
            with self.assertRaises(RuntimeError) as ctx:
                fixtures.require_lm_fixture(FIXTURE)
        self.assertIn(f'python -m test.reversi.fixtures create {FIXTURE}', str(ctx.exception))

    def test_missing_model_path_is_reported(self):
        with mock.patch.object(fixtures, 'FIXTURE_ROOT', Path('/nonexistent/root')):
            with self.assertRaises(RuntimeError) as ctx:
                fixtures.require_lm_fixture(FIXTURE)
        # The (patched-root) model path in the message: the name-derived tail is root-agnostic.
        self.assertIn('rlm_fixture_simple_ec20/rlm_fixture_simple_ec20.dat', str(ctx.exception))


class TestCreateLmFixture(unittest.TestCase):
    """The create idempotency + the config-missing error (no pipeline run)."""

    def test_missing_config_raises(self):
        with self.assertRaises(ValueError):
            fixtures.create_lm_fixture('no_such_fixture')

    def test_existing_artifact_short_circuits(self):
        # A fake (present) artifact under a patched root: create must NOT run the pipeline.
        with mock.patch.object(fixtures, 'FIXTURE_ROOT', Path('/nonexistent/root')):
            with mock.patch.object(Path, 'is_file', return_value=True):
                with mock.patch.object(fixtures, 'LogisticModel',
                                        side_effect=AssertionError('pipeline must not run')):
                    self.assertEqual(
                        fixtures.create_lm_fixture(FIXTURE),
                        fixtures.lm_fixture_model_path(FIXTURE))


if __name__ == '__main__':
    unittest.main()
