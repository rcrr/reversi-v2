"""
Unit tests for the rebuildable LM test fixtures helper (test/reversi/fixtures.py): the path
helpers, the ec20 fixture config content, the consumer gate (require_lm_fixture) and the
create idempotency — all STATIC (no pipeline run, no DB, no artifact required): the build
itself is a manual, seconds-long operation proven by the first consumer.
"""

import json5
import unittest
from pathlib import Path
from unittest import mock

from test.reversi import fixtures

FIXTURE = 'rlm_fixture_simple_ec20'


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


class TestEc20FixtureConfig(unittest.TestCase):
    """The committed ec20 config carries the fixture contract."""

    @classmethod
    def setUpClass(cls):
        # The house .json data files are json5 (the /* ... */ comment header + the trailing
        # commas) — parsed with the pipeline's own loader.
        cls.cfg = json5.loads(fixtures.lm_fixture_config_path(FIXTURE).read_text())

    def test_identity(self):
        self.assertEqual(self.cfg['name'],
                         'RGLM (Logistic) - LM fixture simple ec20 (rlm_fixture_simple_ec20.json)')
        self.assertEqual(self.cfg['empty_count'], 20)

    def test_output_location(self):
        self.assertEqual(self.cfg['base_dir'], 'build/tmp/fixtures/rlm_fixture_simple_ec20')
        self.assertEqual(self.cfg['output'], 'rlm_fixture_simple_ec20.dat')

    def test_fixture_flags(self):
        self.assertIs(self.cfg['regab_allow_duplicate'], False)
        self.assertFalse(self.cfg['plot']['enable'])

    def test_rlm_04_inheritance(self):
        # The training-relevant sections are the rlm_04 ones, untouched.
        self.assertEqual(self.cfg['stat_model'],
                         {'frequency_cut_off': 10, 'logit_clipping': 0.01,
                          'ridge_regularization': 0.01})
        self.assertEqual(self.cfg['regab_data_set']['bid'], [6])
        self.assertEqual(self.cfg['validation_data_set']['bid'], [5])
        fs = self.cfg['feature_set']
        self.assertTrue(fs['intercept'])
        self.assertEqual(fs['pattern_set']['name'], 'EDGE')
        self.assertEqual(fs['mobility_set']['mobility_features'][0]['name'], 'LMC')


class TestRequireLmFixture(unittest.TestCase):
    """The consumer gate: the path when present, the actionable error when missing."""

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
