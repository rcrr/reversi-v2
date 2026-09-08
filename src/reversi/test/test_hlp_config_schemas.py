#
# test_hlp_config_schemas.py
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
# How to run the hlp_config_schemas unit tests.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the tests (no database required — the schemas validate
#     in memory only).
#
# time python3 -m unittest reversi.test.test_hlp_config_schemas
#

import unittest
import json5
from pathlib import Path

from pydantic import ValidationError

from reversi.lm.hlp_config_schemas import (
    LMConfig,
    PatternConfig,
    PatternSetConfig,
    OptimizationConfig,
    ValidationDataSetConfig,
    StatModelConfig,
)
from reversi.test.paths import WORKSPACE_ROOT


class TestRlmConfigSchemas(unittest.TestCase):
    """Deterministic pydantic unit behaviour of hlp_config_schemas.

    D-106 step 3 (probe_rules.md §4): this is the first test file
    for the hlp_config_schemas module. The checks were converted
    from the verify_wrk_positions.py E section (the probe
    keeps only its E7 source-text pin — source inspections stay
    probes per §4). The base payload is the rlm_00.json fixture
    (the same one the probe used)."""

    def setUp(self):
        self.base = json5.loads(
            (WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" /
             "rlm_00.json").read_text())

    def _cfg_dict(self, mutate=None) -> dict:
        """A deep-copied fixture payload, optionally mutated."""
        d = json5.loads(json5.dumps(self.base))
        if mutate:
            mutate(d)
        return d

    # -- E1: dump round-trip -------------------------------------------------

    def test_model_dump_json_round_trip(self):
        """The full config round-trips via model_dump_json: the name
        survives and cache_files_prefix keeps its 'rlmwf_' value."""
        cfg = LMConfig(**self._cfg_dict())
        dumped = json5.loads(cfg.model_dump_json())
        self.assertEqual(dumped["name"], self.base["name"])
        self.assertEqual(dumped["cache_files_prefix"], "rlmwf_")

    # -- E2/E2b/E3: pattern mask parsing -------------------------------------

    def test_pattern_mask_16_hex_parsed_and_serialized(self):
        """A 16-hex string (no 0x) parses to the Bitboard int and
        serializes back to the uppercase 16-hex form."""
        pc = PatternConfig(name="p", mask="0000000000000107")
        self.assertEqual(pc.mask, 0x107)
        dumped = json5.loads(
            PatternConfig(name="p", mask="0000000000000107").model_dump_json())
        self.assertEqual(dumped["mask"], "0000000000000107")

    def test_pattern_mask_0x_prefix_rejected(self):
        """A '0x'-prefixed mask is rejected (the docstring example
        mismatches the parser — the M-item of the D-079 analysis)."""
        with self.assertRaises(ValidationError):
            PatternConfig(name="p", mask="0x0000000000000107")

    def test_invalid_hex_mask_rejected(self):
        """A non-hex mask in the full config is rejected by the
        schema (the worker-level pin of the ec/status siblings
        lives in test_wrk_config.py)."""
        def _badmask(d):
            d["feature_set"]["pattern_set"]["patterns"][0]["mask"] = "ZZZZ"
        with self.assertRaises(ValidationError):
            LMConfig(**self._cfg_dict(_badmask))

    # -- E4/E5: regab_data_set constraints ------------------------------------

    def test_ec_out_of_range_rejected(self):
        """ec outside [0, 100] is rejected by the schema (D-076:
        the domain check stays a schema constraint, not a worker
        one)."""
        for bad_ec in (99, -1):
            with self.subTest(ec=bad_ec):
                def _bdec(d, e=bad_ec):
                    d["regab_data_set"]["ec"] = e
                with self.assertRaises(ValidationError):
                    LMConfig(**self._cfg_dict(_bdec))

    def test_invalid_status_rejected(self):
        """status must be exactly 3 uppercase letters: lowercase
        'cms' and the 4-letter 'CMSX' are both rejected."""
        for bad in ("cms", "CMSX"):
            with self.subTest(status=bad):
                def _badst(d, s=bad):
                    d["regab_data_set"]["status"] = [s]
                with self.assertRaises(ValidationError):
                    LMConfig(**self._cfg_dict(_badst))

    # -- E6: optimization cross-field validator --------------------------------

    def test_optimization_c2_lte_c1_rejected(self):
        """The cross-field c2>c1 validator (D-080 R1) rejects
        c1=0.9 + c2=0.1."""
        with self.assertRaises(ValidationError):
            OptimizationConfig(checkpoint_file="c.json", c1=0.9, c2=0.1)

    def test_optimization_c2_gt_c1_accepted(self):
        """c1=0.1 + c2=0.9 passes the cross-field validator."""
        o = OptimizationConfig(checkpoint_file="c.json", c1=0.1, c2=0.9)
        self.assertEqual(o.c1, 0.1)
        self.assertEqual(o.c2, 0.9)

    # -- E8/E9: validation_data_set + stat_model --------------------------------

    def test_validation_dataset_status_strict(self):
        """validation_data_set.status is a STRICT StatusString
        (D-080 M3): 'xyz' is rejected, valid 3-letter codes pass."""
        with self.assertRaises(ValidationError):
            ValidationDataSetConfig(bid=[1], status=["xyz"])
        ok = ValidationDataSetConfig(bid=[1], status=["CMS", "CMR"])
        self.assertEqual(ok.status, ["CMS", "CMR"])

    def test_properties_field_in_model_fields(self):
        """Both LMBaseConfig descendants carry the 'properties'
        field (D-080 M3)."""
        self.assertIn("properties", StatModelConfig.model_fields)
        self.assertIn("properties", ValidationDataSetConfig.model_fields)

    # -- E10: mutable defaults --------------------------------------------------

    def test_pattern_set_mutable_default_not_shared(self):
        """The mutable default [] is NOT shared across instances."""
        pc = PatternConfig(name="p", mask="0000000000000107")
        ps1 = PatternSetConfig(name="a")
        ps2 = PatternSetConfig(name="b")
        ps1.patterns.append(pc)
        self.assertEqual(len(ps1.patterns), 1)
        self.assertEqual(len(ps2.patterns), 0)

    # -- E11/E12: required fields + defaults -------------------------------------

    def test_missing_output_rejected(self):
        """The 'output' field is required."""
        def _nooutput(d):
            del d["output"]
        with self.assertRaises(ValidationError):
            LMConfig(**self._cfg_dict(_nooutput))

    def test_cache_files_prefix_default(self):
        """cache_files_prefix defaults to 'rlmwf_' when absent."""
        def _noidx(d):
            del d["cache_files_prefix"]
        cfg = LMConfig(**self._cfg_dict(_noidx))
        self.assertEqual(cfg.cache_files_prefix, "rlmwf_")


if __name__ == '__main__':
    unittest.main()
