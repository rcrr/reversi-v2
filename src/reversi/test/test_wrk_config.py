#
# test_wrk_config.py
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
# How to use the unit tests wrk_config module.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests.
#
# time python3 -m unittest reversi.test.test_wrk_config
#

import unittest
import os
import json5
import hashlib
import tempfile

from unittest.mock import patch
from io import StringIO
from pathlib import Path
from pydantic import ValidationError

from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel
from reversi.test.paths import CUSTOM_TMP_BASE, WORKSPACE_ROOT


class TestLMWorkerConfig(unittest.TestCase):
    """Tests for the CONFIG worker basic up/down movements and properties."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        # Patch stdout to keep test output clean
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        # TemporaryDirectory created FIRST so a mid-setup failure
        # still leaves a cleanable temp dir.
        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        self.json_config = str(WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_00.json")
        self.rlm = LogisticModel(self.json_config,
                                 verbosity=Verbosity.LOW,
                                 base_dir_override=self.tmp_dir)
        self.assertEqual(self.rlm.current_step, 0)
        self.assertEqual(self.rlm.current_worker_name, 'CREATED')

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def test_move_up(self):
        self.rlm.move_to_step('CONFIG')
        self.assertEqual(self.rlm.current_step, 1)
        self.assertEqual(self.rlm.current_worker_name, 'CONFIG')

    def test_move_down(self):
        rlm = self.rlm
        rlm.move_to_step('CONFIG')
        self.assertEqual(rlm.current_step, 1)
        self.assertEqual(rlm.current_worker_name, 'CONFIG')
        rlm.move_to_step('CREATED')
        self.assertEqual(rlm.current_step, 0)
        self.assertEqual(rlm.current_worker_name, 'CREATED')
        # T3 (D-078): the _down reset is pinned — both context
        # artifacts are cleared (D-142: the fingerprint too).
        self.assertIsNone(rlm.context.cfg)
        self.assertIsNone(rlm.context.use_cache)
        self.assertIsNone(rlm.context.config_checksum)

    def test_move_up_with_cache(self):
        rlm = self.rlm
        rlm.move_to_step('CONFIG')
        self.assertEqual(rlm.current_step, 1)
        self.assertEqual(rlm.current_worker_name, 'CONFIG')
        rlm.move_to_step('CREATED')
        self.assertEqual(rlm.current_step, 0)
        self.assertEqual(rlm.current_worker_name, 'CREATED')
        rlm.move_to_step('CONFIG')
        self.assertEqual(rlm.current_step, 1)
        self.assertEqual(rlm.current_worker_name, 'CONFIG')

    def test_properties(self):
        rlm = self.rlm
        rlm.move_to_step('CONFIG')
        self.assertEqual(rlm.current_step, 1)
        self.assertEqual(rlm.current_worker_name, 'CONFIG')

        number = rlm.context.cfg.properties.get('number')
        expected_number = 7
        self.assertEqual(number, expected_number)

        string = rlm.context.cfg.properties.get('string')
        expected_string = 'A string'
        self.assertEqual(string, expected_string)

        is_on = rlm.context.cfg.properties.get('is_on')
        expected_is_on = False
        self.assertEqual(is_on, expected_is_on)

        value = rlm.context.cfg.properties.get('missing_key')
        expected_value = None
        self.assertEqual(value, expected_value)

    def test_config_fingerprint(self):
        """D-142: the config fingerprint is the sha3_256 of the
        normalized dump (the effective configuration, the base_dir
        override included) — the single source of truth for the SAVE
        config record and the analytics report."""
        self.rlm.move_to_step('CONFIG')
        ctx = self.rlm.context
        expected = hashlib.sha3_256(
            ctx.cfg.model_dump_json(indent=4).encode()).hexdigest()
        self.assertEqual(ctx.config_checksum, expected)

    def test_no_cache_file_written(self):
        """D-142: the CONFIG level writes NOTHING to the base dir —
        the ad-hoc cache flow is gone (the config record is a SAVE
        artifact, next to the model file)."""
        self.rlm.move_to_step('CONFIG')
        rlmwf = [p.name for p in self.tmp_dir.iterdir()
                 if p.name.startswith('rlmwf_')]
        self.assertEqual(rlmwf, [], f"unexpected rlmwf_ files: {rlmwf}")


class TestLMWorkerConfigValidation(unittest.TestCase):
    """Tests that Pydantic correctly rejects invalid JSON configurations."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)
        # Schema-complete payload: valid EXCEPT the one field each test
        # breaks, so the assertions pin the constraint under test.
        self.valid_json_content = {
            "name": "Test Model",
            "description": "Test",
            "base_dir": "will/be/overwritten",
            "output": "rglm_logistic_model_TEST.dat",
            "use_cache": True,
            "regab_data_set": {
                "regab_db_connection": {"dbname": "t", "user": "t", "host": "l"},
                "bid": [1], "status": ["CMS"], "ec": 10
            },
            "stat_model": {"frequency_cut_off": 1},
            "optimization": {"checkpoint_file": "opt_checkpoint.json"},
            "validation_data_set": {"bid": [1], "status": ["CMS"]},
            "feature_set": {
                "name": "FSet",
                "intercept": False,
                "mobility_set": {"name": "MSet", "mobility_features": [
                    {"name": "M", "mask": "FFFFFFFFFFFFFFFF", "amask": "0000000000000000"}
                ]},
                "pattern_set": {"name": "PSet", "patterns": [
                    {"name": "P", "mask": "00000000000000FF"}
                ]}
            }
        }

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            self._tmp.cleanup()

    def _write_json(self, payload: dict) -> Path:
        """Helper to write a JSON payload to a temp file and return its path."""
        file_path = Path(self.tmp_dir) / "test_config.json"
        with open(file_path, "w") as f:
            json5.dump(payload, f)
        return file_path

    def test_invalid_json_syntax(self):
        """Test that malformed JSON raises an exception."""
        file_path = Path(self.tmp_dir) / "bad_syntax.json"
        file_path.write_text("{ this is not valid json }")
        
        rlm = LogisticModel(file_path, verbosity=Verbosity.LOW, base_dir_override=self.tmp_dir)
        # T2 (D-078): pin the actual exception — json5 0.15.0 raises
        # a plain ValueError on a syntax error (no JSON5Exception in
        # this version), before pydantic ever sees the payload.
        with self.assertRaises(ValueError):
            rlm.move_to_step('CONFIG')

    def test_invalid_ec_out_of_range(self):
        """Test that ec > 60 is rejected by Pydantic."""
        payload = self.valid_json_content.copy()
        payload['regab_data_set']['ec'] = 99 # Invalid!
        
        rlm = LogisticModel(self._write_json(payload), verbosity=Verbosity.LOW, base_dir_override=self.tmp_dir)
        with self.assertRaises(ValidationError):
            rlm.move_to_step('CONFIG')

    def test_invalid_status_format(self):
        """Test that status not matching 3 uppercase letters is rejected."""
        payload = self.valid_json_content.copy()
        payload['regab_data_set']['status'] = ["INVALID"]
        
        rlm = LogisticModel(self._write_json(payload), verbosity=Verbosity.LOW, base_dir_override=self.tmp_dir)
        with self.assertRaises(ValidationError):
            rlm.move_to_step('CONFIG')

    def test_invalid_hex_mask_format(self):
        """Test that a non-hex string in a pattern mask is rejected."""
        payload = self.valid_json_content.copy()
        payload['feature_set']['pattern_set']['patterns'][0]['mask'] = "ZZZZZZZZZZZZZZZZ"
        
        rlm = LogisticModel(self._write_json(payload), verbosity=Verbosity.LOW, base_dir_override=self.tmp_dir)
        with self.assertRaises(ValidationError):
            rlm.move_to_step('CONFIG')


class TestLMWorkerConfigBaseDir(unittest.TestCase):
    """Tests the validation of the base_dir_override parameter."""

    @classmethod
    def setUpClass(cls):
        CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.patcher_stdout = patch('sys.stdout', new=StringIO())
        self.mock_stdout = self.patcher_stdout.start()

        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))
        self.tmp_dir = Path(self._tmp.name)

    def tearDown(self):
        if getattr(self, 'patcher_stdout', None) is not None:
            self.patcher_stdout.stop()
        if getattr(self, '_tmp', None) is not None:
            # Restore write permissions before deleting (the
            # not-writable test leaves the dir at 0o444).
            try:
                os.chmod(self.tmp_dir, 0o755)
            except OSError:
                pass
            self._tmp.cleanup()

    def test_base_dir_is_a_file_raises_error(self):
        """Test that passing a file path instead of a directory raises NotADirectoryError."""
        fake_file = Path(self.tmp_dir) / "I_am_a_file.txt"
        fake_file.touch()
        
        valid_json = Path('src/reversi/test/data/rlm_00.json')

        # The check happens in __init__, not in the worker!
        with self.assertRaises(NotADirectoryError) as context:
            rlm = LogisticModel(valid_json, verbosity=Verbosity.LOW, base_dir_override=fake_file)
            
        self.assertIn("not a directory", str(context.exception).lower())

    def test_base_dir_is_not_writable_raises_error(self):
        """Test that an un-writable directory raises PermissionError."""
        os.chmod(self.tmp_dir, 0o444)

        valid_json = Path('src/reversi/test/data/rlm_00.json')
        rlm = LogisticModel(valid_json, verbosity=Verbosity.LOW, base_dir_override=self.tmp_dir)

        # R3 (D-078): the precise OS exception type, not RuntimeError.
        with self.assertRaises(PermissionError) as context:
            rlm.move_to_step('CONFIG')
        self.assertIn("not writable", str(context.exception))

    def test_base_dir_missing_raises_file_not_found_error(self):
        """Test that a base_dir that doesn't exist (from the json, no
        override) raises FileNotFoundError from the CONFIG worker.

        D-106 step 3 (probe_rules.md §4): the third base_dir guard
        branch, converted from the verify_wrk_config.py D1 probe.
        The file (NotADirectoryError) and not-writable (PermissionError)
        branches are pinned above."""
        payload = json5.loads(
            (WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_00.json").read_text())
        payload["base_dir"] = str(Path(self.tmp_dir) / "no_such_dir_xyz")
        json_path = Path(self.tmp_dir) / "rlm_00_nodir.json"
        with open(json_path, "w") as f:
            json5.dump(payload, f)

        rlm = LogisticModel(json_path, verbosity=Verbosity.LOW)
        with self.assertRaises(FileNotFoundError) as context:
            rlm.move_to_step('CONFIG')
        self.assertIn("doesn't exist", str(context.exception))


if __name__ == '__main__':
    unittest.main()
