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
    PlotConfig,
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

    def test_optimization_high_performance_fg(self):
        """I-013: high_performance_fg defaults to False (the classic
        fg) and accepts True (the numba high-performance fg)."""
        o = OptimizationConfig(checkpoint_file="c.json")
        self.assertFalse(o.high_performance_fg)
        o2 = OptimizationConfig(checkpoint_file="c.json",
                                high_performance_fg=True)
        self.assertTrue(o2.high_performance_fg)

    # -- D-148: the client_check_tol field ---------------------------------

    def test_client_check_tol_default(self):
        """D-148: client_check_tol defaults to 1e-8 (Roberto's
        ruling) — the fixture does not set it."""
        cfg = LMConfig(**self._cfg_dict())
        self.assertEqual(cfg.client_check_tol, 1e-8)

    def test_client_check_tol_override(self):
        """An explicit value survives the validation (and the dump
        round-trip: the field travels with the normalized dump)."""
        d = self._cfg_dict()
        d["client_check_tol"] = 1e-9
        cfg = LMConfig(**d)
        self.assertEqual(cfg.client_check_tol, 1e-9)
        dumped = json5.loads(cfg.model_dump_json())
        self.assertEqual(dumped["client_check_tol"], 1e-9)

    def test_client_check_tol_nonpositive_rejected(self):
        """The gt=0 constraint: a zero or negative tolerance is a
        ValidationError (a check that never fails is not a check)."""
        for bad in (0.0, -1e-8):
            with self.assertRaises(ValidationError):
                LMConfig(**self._cfg_dict(
                    lambda d, b=bad: d.update(client_check_tol=b)))

    # -- D-149: the PlotConfig section -------------------------------------

    def test_plot_defaults(self):
        """D-149: the plot section defaults — enable True, format
        'png' (the png-default ruling), dpi 150, the relative
        'plots' dir, and an EMPTY whitelist (the PLOT level is a
        no-op until names are listed)."""
        cfg = LMConfig(**self._cfg_dict())
        self.assertTrue(cfg.plot.enable)
        self.assertEqual(cfg.plot.format, "png")
        self.assertEqual(cfg.plot.dpi, 150)
        self.assertEqual(cfg.plot.dir_name, Path("plots"))
        self.assertEqual(cfg.plot.plots, [])

    def test_plot_format_pair_and_normalization(self):
        """The format field: a lone token and the comma-separated
        pair are both accepted; whitespace is normalized away
        ('png, pdf' -> 'png,pdf'), the order is preserved."""
        self.assertEqual(PlotConfig(format="pdf").format, "pdf")
        self.assertEqual(PlotConfig(format="pdf,png").format, "pdf,png")
        self.assertEqual(PlotConfig(format="png, pdf").format,
                         "png,pdf")

    def test_plot_format_bad_rejected(self):
        """Unknown tokens, empty tokens (the trailing comma) and
        duplicates are all a ValidationError."""
        for bad in ("jpg", "pdf,", "", "png,png"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValidationError):
                    PlotConfig(format=bad)

    def test_plot_unknown_name_rejected(self):
        """An unknown plot name is rejected at the CONFIG level
        (the fail-fast typo guard, the PLOT_NAMES vocabulary)."""
        with self.assertRaises(ValidationError):
            PlotConfig(plots=["residual_density", "nope"])

    def test_plot_dedup_preserving_order(self):
        """A repeated name is deduplicated, order preserved (a
        duplicate would regenerate the same file twice)."""
        p = PlotConfig(plots=["parity", "resid_qq", "parity"])
        self.assertEqual(p.plots, ["parity", "resid_qq"])

    def test_plot_dir_absolute_and_relative(self):
        """The dir_name is a Path: an absolute one stays absolute
        (the worker will use it as-is, outside base_dir), a
        relative one stays relative (the worker resolves it under
        base_dir)."""
        self.assertTrue(PlotConfig(dir_name="/tmp/elsewhere").dir_name
                        .is_absolute())
        self.assertFalse(PlotConfig(dir_name="my-plots").dir_name
                         .is_absolute())

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

    # -- T15: the I-017 FEATURE_ANALYSIS / EFFECT_SIZE config -------------------

    def test_i017_defaults(self):
        """The I-017 D-175 opt-in: the feature_analysis / the
        effect_size enable default FALSE, the target_level
        default 'last', the corpus defaults (seed 42, 1e7, ec
        20), the su_pairs empty. D-186: the rlm_00 now carries
        the section (the opt-in) — strip it to check the pure
        defaults (the absent-section no-op)."""
        def _strip_i017(d):
            d.pop("feature_analysis", None)
            d.pop("effect_size", None)
            d.pop("target_level", None)
        cfg = LMConfig(**self._cfg_dict(_strip_i017))
        self.assertFalse(cfg.feature_analysis.enable)
        self.assertFalse(cfg.effect_size.enable)
        self.assertEqual(cfg.target_level, "last")
        self.assertEqual(cfg.feature_analysis.corpus.seed, 42)
        self.assertEqual(cfg.feature_analysis.corpus.total_positions,
                         10_000_000)
        self.assertEqual(cfg.feature_analysis.corpus.ec, 20)
        self.assertEqual(cfg.feature_analysis.su_pairs, [])
        self.assertFalse(cfg.feature_analysis.export_csv)
        self.assertFalse(cfg.effect_size.export_csv)
        self.assertEqual(cfg.effect_size.top_k_adherence, 20)

    def test_i017_su_pairs_canonical_dedupe(self):
        """The P6 canonical order + the dedupe: the repeated pair
        (any order) collapses to one sorted tuple."""
        def _pairs(d):
            d["feature_analysis"] = {"su_pairs": [["EDGE", "LMC"],
                                                  ["LMC", "EDGE"]]}
        cfg = LMConfig(**self._cfg_dict(_pairs))
        self.assertEqual(cfg.feature_analysis.su_pairs,
                         [("EDGE", "LMC")])

    def test_i017_su_pairs_fail_fast(self):
        """The fail-fast against the feature set: a name not in
        the feature set (the mobility + the pattern names) is
        rejected at the CONFIG level."""
        def _badpair(d):
            d["feature_analysis"] = {"su_pairs": [["LMC", "UNKNOWN"]]}
        with self.assertRaises(ValidationError):
            LMConfig(**self._cfg_dict(_badpair))

    def test_i017_target_level_field(self):
        """The target_level field: a level name (the 'FEATURE_'
        'ANALYSIS' stop) or 'last' (the default)."""
        def _tlevel(d):
            d["target_level"] = "FEATURE_ANALYSIS"
        cfg = LMConfig(**self._cfg_dict(_tlevel))
        self.assertEqual(cfg.target_level, "FEATURE_ANALYSIS")


if __name__ == '__main__':
    unittest.main()
