#
# verify_optimize.py — independent verification probe for the OPTIMIZE
# bring-in (rlm_optimize.py, lm_worker_optimize.py,
# test_rlm_optimize.py, test_lm_worker_optimize.py), re-pinned to the
# post-D-096-campaign state.
#
# Tiers:
#   A  rlm_optimize.py structure (post-campaign)
#   B  lm_worker_optimize.py structure (post-campaign)
#   C  test_rlm_optimize.py structure (post-campaign, M10 expansion)
#   D  test_lm_worker_optimize.py structure (post-campaign)
#   E  cross-file (logistic_model, RLMContext, schemas, opt_lbfgs,
#      rlm_02.json)
#   F  checkpoint IO (no DB)
#   G  helper functions (no DB)
#   H  live pipeline through OPTIMIZE (DB required)
#
# Run:  .venv/bin/python scratch/verify_optimize.py
#
import contextlib
import hashlib
import io
import re
import sys
import tempfile
import traceback
from io import StringIO
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "twolm"

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))


def read(name):
    return (SRC / name).read_text()


def ws_lines(text):
    return {i + 1 for i, ln in enumerate(text.splitlines())
            if ln != ln.rstrip() and not ln.strip().startswith("#")}


# ---------------------------------------------------------------- A tier
print("== tier A: rlm_optimize.py structure (post D-096)")
a = read("rlm_optimize.py")
al = a.splitlines()
check("A1 line count 267", len(al) == 267, f"{len(al)}")
check("A2 T13 header fixed (was 'rglm.py')",
      al[1] == "# rlm_optimize.py" and "rglm.py" not in a)
check("A3 __future__ annotations", "from __future__ import annotations" in a)
check("A4 T9: Tuple dead import removed",
      "from typing import List, Dict, Any, TYPE_CHECKING" in a
      and a.count("Tuple") == 0, f"Tuple occurrences: {a.count('Tuple')}")
check("A5 __all__ 6 names",
      re.search(r"__all__ = \['optimization_info_dict',.*?'weights_compute_sha3_256_hash'\]",
                a, re.S) is not None)
check("A6 checkpoint-dict design comment",
      al[55] == "#: Unlike the other layers, where the cache—when present—is organized using a class and a data object,"
      and al[56] == "#: the OPTIMIZE layer cache (called a checkpoint) consists of a dictionary.")
check("A7 save @validate_call + header",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\n"
      "def save_optimization_checkpoint(filepath: Path," in a
      and 'bw.write_header("RGLM Optimization Checkpoint", 1)' in a)
check("A8 len(sl) written + zip(sl, yl, rho) written",
      "bw.write_i32(len(sl))" in a and "for s, y, r in zip(sl, yl, rho):" in a)
check("A9 M9: 'Atomically' removed (no atomic write in the code)",
      "Atomically" not in a
      and "Serialize the L-BFGS history vectors chronologically:" in a)
check("A10 M6: history lists must have equal length (fail fast)",
      "if not (len(sl) == len(yl) == len(rho)):" in a
      and "(the L-BFGS history is stored as (s, y, rho) triples)" in a)
check("A11 load @validate_call + 2 RuntimeError gates",
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\n"
      "def load_optimization_checkpoint(filepath: Path) -> Dict[str, Any]:" in a
      and 'The file is not a proper optimization checkpoint. Found: {description}' in a
      and "Checkpoint version mismatch: found {version}, expected 1" in a)
check("A12 R3: load verifies the SHA3-256 sidecar",
      "if not binio.verify_sha3_256_sidecar(filepath):" in a
      and "Checkpoint checksum mismatch: {filepath} does not match its SHA3-256 sidecar" in a)
check("A13 exactly 4 @validate_call decorators", a.count("@validate_call") == 4,
      f"{a.count('@validate_call')}")
check("A14 T11: two no-validation notes (L173 + L230)",
      a.count("#: Here validation is not possible, it brings in a convoluted issue with circular imports.") == 2
      and al[172].startswith("#: Here validation is not possible")
      and al[229].startswith("#: Here validation is not possible"))
check("A15 R1: ridge gate in is_optimization_cache_consistent (3rd gate)",
      "The ridge regularization parameter has changed." in a
      and "math.isclose(ctx.cfg.stat_model.ridge_regularization," in a
      and "rel_tol=1e-5, abs_tol=1e-8)" in a)
check("A16 R1b+M3: status_converged slimmed (no rr gate, no dead mg isclose)",
      "mg_is_consistent" not in a and "rr_is_consistent" not in a
      and "judgement criterion, not part of the objective" in a)
check("A17 weights hash NDArray[np.float32]",
      "def weights_compute_sha3_256_hash(w: npt.NDArray[np.float32]) -> str:" in a
      and "hasher.update(w.tobytes())" in a)
check("A18 no code ws lines (house sweep)", ws_lines(a) == set(),
      str(sorted(ws_lines(a))))
check("A19 'Read header properly!' colloquial comment kept",
      "# Read header properly!" in a)
check("A20 'checpoint' typo fixed in the docstring", "checpoint" not in a)

# ---------------------------------------------------------------- B tier
print("== tier B: lm_worker_optimize.py structure (post D-096)")
b = read("lm_worker_optimize.py")
bl = b.splitlines()
check("B1 line count 190", len(bl) == 190, f"{len(bl)}")
check("B2 T8: 'Aauthor' typo fixed",
      bl[6] == "# Author Roberto Corradini mailto:rob_corradini@yahoo.it"
      and "Aauthor" not in b)
check("B3 T9: Path dead import removed",
      "from pathlib import Path" not in b and "Path(" not in b)
check("B4 T10: factory @validate_call + pydantic import",
      "from pydantic import validate_call, ConfigDict" in b and
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\n"
      "def lm_worker_optimize() -> Worker:" in b)
check("B5 triple blanks kept (house worker style, L45-47)",
      all(bl[i] == "" for i in (44, 45, 46)))
check("B6 checkpoint path via cfg (config-driven name, not rlmwf_ prefix)",
      "checkpoint_path = ctx.cfg.base_dir / opt_cfg.checkpoint_file" in b
      and "if checkpoint_path.exists() and ctx.use_cache:" in b)
check("B7 M1: min_grad unpack discards the unused count",
      "min_grad_value, _ = opt_cfg.min_grad" in b
      and b.count("min_grad_count") == 0)
check("B8 'or' disjunction kept (completed branch)",
      "elif is_optimization_status_converged(ctx, cp) or cp['iters'] >= ctx.cfg.optimization.max_iters:" in b)
check("B9 M4: 'cecksum' typo fixed x2",
      "cecksum" not in b and b.count("Weight vector checksum") == 2)
check("B10 M2: unreachable else removed (comment kept)",
      "Checkpoint exists but state is unrecognized. Restarting from scratch." not in b
      and "unreachable: iters is an int" in b)
check("B11 save_fn 7-param + INCOMPLETE intermediate checkpoints",
      "def save_fn(w, sl, yl, rho, k, f, g_norm):" in b
      and "converged=False," in b and 'reason="INCOMPLETE",' in b)
check("B12 M5: intermediate save uses completed-count semantics",
      "iters=k + 1," in b)
check("B13 lbfgs call (16 kwargs incl. warm-start)",
      "w_opt, info = lbfgs(" in b and "initial_iter=initial_iter" in b
      and "fg=ctx.fg," in b)
check("B14 R4: _down clears fg + w_checksum + opt_info (w kept)",
      "ctx.fg = None" in b and "ctx.w_checksum = None" in b
      and "ctx.opt_info = None" in b)
check("B15 R2: corrupted checkpoint -> delete + scratch",
      "except (RuntimeError, binio.BinaryFormatError, OSError) as exc:" in b
      and "Deleting it and starting from scratch." in b
      and "checkpoint_path.unlink(missing_ok=True)" in b
      and 'checkpoint_path.name + ".SHA3-256"' in b
      and "from reversi.tools import binio" in b)
check("B16 no code ws lines (house sweep)", ws_lines(b) == set(),
      str(sorted(ws_lines(b))))
check("B17 final save uses info['w']/['sl']/['yl']/['rho']",
      "w=info['w']," in b and "sl=info['sl']," in b
      and "yl=info['yl']," in b and "rho=info['rho']" in b)

# ---------------------------------------------------------------- C tier
print("== tier C: test_rlm_optimize.py structure (post D-096)")
c = read("test/test_rlm_optimize.py")
cl = c.splitlines()
c_code = "\n".join(ln for ln in cl if not ln.strip().startswith("#"))
check("C1 line count 340", len(cl) == 340, f"{len(cl)}")
check("C2 T14: header fixed (no live regab DB required)",
      "no live regab DB required" in c and "SKIP_REGAB_DB" not in c
      and "logistic_model" not in c_code and "regab" not in c_code.lower())
check("C3 no SKIP_REGAB_DB gate in code (not needed — no DB)",
      "os.getenv" not in c_code and "skipTest" not in c_code)
check("C4 D-085 idiom applied",
      "tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))" in c
      and "from twolm.test.paths import CUSTOM_TMP_BASE" in c
      and "mkdtemp" not in c and "shutil" not in c)
check("C5 defensive tearDown",
      "if getattr(self, '_tmp', None) is not None:\n            self._tmp.cleanup()" in c)
check("C6 4 classes / 19 tests (M10 expansion)",
      c.count("class Test") == 4 and len(re.findall(r"    def test_\w+", c)) == 19)
check("C7 T15: test names fixed (they test the checksum gates)",
      "def test_inconsistent_design_matrix_checksum(" in c
      and "def test_inconsistent_zed_checksum(" in c
      and "test_inconsistent_iters" not in c
      and "test_inconsistent_m(" not in c)
check("C8 R1 test: ridge gate branch",
      "def test_inconsistent_ridge(" in c
      and "'ridge_regularization': 0.02" in c)
check("C9 R3 test: corrupted content rejected at load",
      "def test_checksum_mismatch_raises(" in c
      and "Checkpoint checksum mismatch" in c)
check("C10 M10 tests: error paths, dtypes, empty history, golden hashes, helpers",
      "def test_wrong_description_raises(" in c
      and "def test_wrong_version_raises(" in c
      and "def test_empty_history_roundtrip(" in c
      and "def test_history_length_mismatch_raises(" in c
      and "def test_file_golden_hash(" in c
      and "6e01ff8614e8732484b7af59b01615989357ce1af2419864621965af221bd280" in c
      and "def test_sidecar_produced_and_matches(" in c
      and "class TestRLMOptimizeHelpers" in c
      and "class TestRLMOptimizeStatusConverged" in c
      and "78a7baac51aedf442b3de09a583af1a0704c8aece3b156aaf630780b2d7dc060" in c
      and "def test_f32_roundtrip_passes(" in c
      and "def test_judged_against_new_tolerance(" in c)
check("C11 status tests: the ridge branch moved out (judged on min_grad only)",
      "def test_converged_below_tolerance(" in c
      and "def test_not_converged_above_tolerance(" in c)
check("C12 no code ws lines (house sweep)", ws_lines(c) == set(),
      str(sorted(ws_lines(c))))

# ---------------------------------------------------------------- D tier
print("== tier D: test_lm_worker_optimize.py structure (post D-096)")
d = read("test/test_lm_worker_optimize.py")
dl = d.splitlines()
check("D1 line count 174", len(dl) == 174, f"{len(dl)}")
check("D2 T1: SKIP_REGAB_DB gate in setUp (header claim now true)",
      "# T1 (D-096):" in d
      and "if os.getenv('SKIP_REGAB_DB', '0') == '1':" in d
      and "self.skipTest('SKIP_REGAB_DB=1: database tests skipped')" in d)
check("D3 T2: D-085 idiom applied",
      "tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))" in d
      and "Path(self._tmp.name)" in d
      and 'WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_02.json"' in d
      and "mkdtemp" not in d and "shutil" not in d)
check("D4 T4: dead imports removed (skipUnless gone; os/Path now used)",
      "skipUnless" not in d
      and "import os" in d and "os.getenv" in d
      and "from pathlib import Path" in d and "Path(" in d)
check("D5 T3: dead if-False block removed", "if False:" not in d)
check("D6 T5: stray ':# ###' comment removed", "#: ###" not in d)
check("D7 1 class / 3 tests, step pins GRADIENT=8 / OPTIMIZE=9",
      d.count("class Test") == 1 and len(re.findall(r"    def test_\w+", d)) == 3
      and re.findall(r"    def test_\w+", d) ==
      ["    def test_optimization_runs",
       "    def test_max_iters_treated_as_completed",
       "    def test_down_clears_optimize"]
      and "assertEqual(self.rlm.current_step, 8)" in d
      and "assertEqual(self.rlm.current_step, 9)" in d)
check("D8 T6: vacuous assertNotIn replaced with the real lbfgs marker",
      'self.assertNotIn("L-BFGS - [", logs)' in d
      and 'self.assertNotIn("Starting L-BFGS optimization"' not in d)
check("D9 T7: _down test pins R4 (fg + w_checksum + opt_info cleared, w kept)",
      "self.rlm.move_to_step(8)" in d
      and "self.assertIsNone(ctx.fg)" in d
      and "self.assertIsNone(ctx.w_checksum)" in d
      and "self.assertIsNone(ctx.opt_info)" in d
      and "nptest.assert_array_equal(ctx.w, w_before)" in d)
check("D10 cfg mutation on the pydantic config (not frozen: works)",
      "ctx.cfg.optimization.max_iters = 10" in d
      and "rlm2.context.cfg.optimization.max_iters = 10" in d)
check("D11 no code ws lines (house sweep)", ws_lines(d) == set(),
      str(sorted(ws_lines(d))))

# ---------------------------------------------------------------- E tier
print("== tier E: cross-file")
lm = read("logistic_model.py")
# (E1/E2 pipeline-state pins moved to the hub verify_logistic_model.py
# V3c/V3d at D-106)
check("E3 RLMContext pre-declared fields (w, fg, w_checksum, opt_info, dense_w_checksum)",
      "    w: Any = None" in lm and "    fg: Any = None" in lm
      and "    w_checksum: str | None = None" in lm
      and "    opt_info: Any = None" in lm
      and "    dense_w_checksum: str | None = None" in lm)
sc = read("rlm_config_schemas.py")
check("E4 OptimizationConfig: min_grad Tuple[float, int] + checkpoint_file Path",
      "min_grad: Tuple[float, int] = Field(default=(1e-5, 3)" in sc
      and "checkpoint_file: Path = Field(..., description=" in sc)
obl = read("opt_lbfgs.py")
check("E5 lbfgs signature has all 16 kwargs the worker passes",
      all(k in obl for k in ["x0", "c1", "c2", "min_grad", "min_p_fun_decrease",
                             "max_iters", "m", "log_every_n", "logger",
                             "save_every_n", "save_fn", "initial_sl",
                             "initial_yl", "initial_rho", "initial_iter"]))
check("E6 lbfgs info dict: the 9 keys the worker consumes",
      "'w': x," in obl and "'sl': sl," in obl and "'yl': yl," in obl
      and "'rho': rho" in obl and "'g_norm': np.linalg.norm(fgv.grad)," in obl)
check("E7 x0.copy() (ctx.w never mutated in place; float32 preserved)",
      "x = x0.copy()" in obl)
j = (SRC / "test" / "data" / "rlm_02.json").read_text()
check("E8 rlm_02 optimization block",
      '"max_iters": 50' in j and '"m": 19' in j and '"c1": 0.0001' in j
      and '"c2": 0.9' in j and '"min_grad": [1e-3, 3]' in j
      and '"min_p_fun_decrease": [1e-5, 3]' in j
      and '"log_every_n": 1' in j and '"save_every_n": 0' in j
      and '"checkpoint_file": "checkpoint_optimize.dat"' in j)

# ---------------------------------------------------------------- F tier
# (F1-F10 checkpoint IO (real files) deleted at D-106 step 3, class
#  c: test_rlm_optimize.py::TestRLMOptimizeIO pins ALL of it with
#  real files — test_store_and_load_cycle (the round-trip + dtypes +
#  rho float, the f32 metadata), test_empty_history_roundtrip,
#  test_wrong_description_raises, test_wrong_version_raises,
#  test_file_golden_hash (the same 6e01ff86... literal),
#  test_sidecar_produced_and_matches (existence + verify),
#  test_checksum_mismatch_raises (R3: corrupted content rejected),
#  test_history_length_mismatch_raises (M6: asymmetric history).
#  The save_optimization_checkpoint / load_optimization_checkpoint /
#  binio imports they used are removed with them.)
# (weights_compute_sha3_256_hash is still imported for the G3 oracle
#  check, which stays — in the G-tier import below.)

# ---------------------------------------------------------------- G tier
print("== tier G: helper functions (no DB)")
from twolm.rlm_optimize import weights_compute_sha3_256_hash


def g_main():
    # (G1/G2 info_dict branches, G4 cache_consistent 4 branches,
    #  G5 status_converged 4 branches deleted at D-106 step 3, class
    #  c: test_rlm_optimize.py pins all of it —
    #  test_info_dict_filters_to_context_keys,
    #  test_info_dict_missing_key_raises, the 4
    #  TestRLMOptimizeCacheConsistency tests, the 4
    #  TestRLMOptimizeStatusConverged tests. The rec_log / make_ctx
    #  scaffolding was used only by G4/G5.)
    try:
        w = np.array([0.1, 0.2, 0.3], dtype=np.float32)
        h = weights_compute_sha3_256_hash(w)
        assert h == "78a7baac51aedf442b3de09a583af1a0704c8aece3b156aaf630780b2d7dc060", h
        assert h == hashlib.sha3_256(w.tobytes()).hexdigest()
        check("G3 weights hash golden + independent", True)
    except Exception as exc:
        check("G3 weights hash golden + independent", False, repr(exc))


g_main()

# ---------------------------------------------------------------- H tier
print("== tier H: live pipeline through OPTIMIZE (DB required)")
from reversi.tools.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.rlm_optimize import (load_optimization_checkpoint,
                                save_optimization_checkpoint)


def h_main():
    with tempfile.TemporaryDirectory(dir=ROOT / "build" / "tmp") as tmp:
        # HIGH (not LOW): at LOW=3 the machine only displays WARN+, so the
        # worker INFO logs (and the lbfgs logger INFO lines) would never be
        # captured — same verbosity choice as the worker test itself.
        json_config = str(ROOT / "src" / "twolm" / "test" / "data" / "rlm_02.json")
        rlm = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                            base_dir_override=tmp)
        out = StringIO()
        with contextlib.redirect_stdout(out):
            rlm.move_to_step("OPTIMIZE")
        logs1 = out.getvalue()

        def h1():
            assert rlm.current_step == 9, rlm.current_step
            assert rlm.current_worker_name == "OPTIMIZE"
            ctx = rlm.context
            assert ctx.w.dtype == np.float32 and len(ctx.w) == 2981
            assert ctx.w_checksum == hashlib.sha3_256(ctx.w.tobytes()).hexdigest()
            assert set(ctx.opt_info.keys()) == {"converged", "reason", "iters", "f", "g_norm"}
            assert "Starting OPTIMIZE worker..." in logs1
            assert "Optimization finished." in logs1
            files = sorted(p.name for p in Path(tmp).iterdir())
            for n in ("rlmwf_01_CONFIG.dat", "rlmwf_01_CONFIG.dat.SHA3-256",
                      "rlmwf_02_POSITIONS.dat", "rlmwf_02_POSITIONS.dat.SHA3-256",
                      "rlmwf_04_INDEXES.dat", "rlmwf_04_INDEXES.dat.SHA3-256",
                      "rlmwf_05_WMAPS.dat", "rlmwf_05_WMAPS.dat.SHA3-256",
                      "rlmwf_06_DESIGN_MTR.dat", "rlmwf_06_DESIGN_MTR.dat.SHA3-256",
                      "checkpoint_optimize.dat", "checkpoint_optimize.dat.SHA3-256"):
                assert n in files, files
            assert not [n for n in files if n.startswith(("rlmwf_03", "rlmwf_07", "rlmwf_08"))], files

        def h2():
            ctx = rlm.context
            cp = load_optimization_checkpoint(Path(tmp) / "checkpoint_optimize.dat")
            np.testing.assert_array_equal(cp["w"], ctx.w)
            f_final, g_final = ctx.fg(ctx.w)
            assert abs(float(cp["f"]) - float(f_final)) <= 1e-6 * abs(float(f_final)) + 1e-9, \
                (float(cp["f"]), float(f_final))
            g_norm_final = np.linalg.norm(g_final)
            assert abs(float(cp["g_norm"]) - float(g_norm_final)) <= 1e-6 * float(g_norm_final) + 1e-9
            assert cp["iters"] >= 1 and cp["max_iters"] == 50 and cp["m"] == 19
            assert cp["converged"] == (str(cp["reason"]).startswith("CONVERGED")), cp["reason"]
            assert cp["design_matrix_checksum"] == ctx.design_matrix_checksum
            assert cp["zed_checksum"] == ctx.zed_checksum

        def h3():
            ctx = rlm.context
            f_opt, _ = ctx.fg(ctx.w)
            f_zero, _ = ctx.fg(np.zeros(2981, dtype=np.float32))
            assert float(f_opt) < float(f_zero), (float(f_opt), float(f_zero))
            assert not np.all(ctx.w == 0)

        for name, fn in (("H1 full run: state + 12 base-dir files", h1),
                         ("H2 checkpoint == ctx (independent fg)", h2),
                         ("H3 loss decreased (independent)", h3)):
            try:
                fn()
                check(name, True)
            except Exception as exc:
                check(name, False, f"{exc!r}\n{traceback.format_exc()}")
        # H4: second instance — the completed-checkpoint path
        try:
            rlm2 = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                 base_dir_override=tmp)
            out2 = StringIO()
            with contextlib.redirect_stdout(out2):
                rlm2.move_to_step("OPTIMIZE")
            logs2 = out2.getvalue()
            assert "Checkpoint: optimization already completed." in logs2, logs2[-2000:]
            assert "Iterations" in logs2
            assert "L-BFGS - [" not in logs2, "lbfgs ran in run 2"
            np.testing.assert_array_equal(rlm2.context.w, rlm.context.w)
            check("H4 second instance: completed path, no lbfgs", True)
        except Exception as exc:
            check("H4 second instance: completed path, no lbfgs", False, f"{exc!r}\n{traceback.format_exc()}")
        # H5: crafted INCOMPLETE checkpoint -> resume path
        try:
            cp = load_optimization_checkpoint(Path(tmp) / "checkpoint_optimize.dat")
            save_optimization_checkpoint(
                filepath=Path(tmp) / "checkpoint_optimize.dat",
                design_matrix_checksum=rlm.context.design_matrix_checksum,
                zed_checksum=rlm.context.zed_checksum,
                ridge_regularization=0.01, min_grad_value=1e-3,
                max_iters=50, m=19, converged=False, reason="INCOMPLETE",
                iters=5, f=float(cp["f"]), g_norm=0.5,
                w=cp["w"], sl=cp["sl"], yl=cp["yl"], rho=cp["rho"])
            rlm3 = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                 base_dir_override=tmp)
            out3 = StringIO()
            with contextlib.redirect_stdout(out3):
                rlm3.move_to_step("OPTIMIZE")
            logs3 = out3.getvalue()
            assert "Resuming optimization from iteration 5." in logs3, logs3[-2000:]
            assert "L-BFGS - [" in logs3, "lbfgs did not run in the resume"
            cp3 = load_optimization_checkpoint(Path(tmp) / "checkpoint_optimize.dat")
            assert cp3["iters"] > 5, cp3["iters"]
            check("H5 crafted INCOMPLETE checkpoint: resume path", True)
        except Exception as exc:
            check("H5 crafted INCOMPLETE checkpoint: resume path", False, f"{exc!r}\n{traceback.format_exc()}")
        # H6: changed logit_clipping -> zed checksum change -> start from scratch
        try:
            rlm4 = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                 base_dir_override=tmp)
            rlm4.move_to_step("CONFIG")
            rlm4.context.cfg.stat_model.logit_clipping = 0.02
            out4 = StringIO()
            with contextlib.redirect_stdout(out4):
                rlm4.move_to_step("OPTIMIZE")
            logs4 = out4.getvalue()
            assert "Checkpoint config mismatch. Starting from scratch." in logs4, logs4[-2000:]
            assert "The definition of the Z array has changed." in logs4
            assert "L-BFGS - [" in logs4
            cp4 = load_optimization_checkpoint(Path(tmp) / "checkpoint_optimize.dat")
            assert cp4["zed_checksum"] == rlm4.context.zed_checksum
            assert cp4["zed_checksum"] != rlm.context.zed_checksum
            check("H6 changed clipping: inconsistent -> scratch", True)
        except Exception as exc:
            check("H6 changed clipping: inconsistent -> scratch", False, f"{exc!r}\n{traceback.format_exc()}")
        # H6b: R1 (D-096) — a RIDGE-ONLY change (same zed checksum) must
        # behave exactly like a clipping change: scratch, not silent accept
        try:
            with tempfile.TemporaryDirectory(dir=ROOT / "build" / "tmp") as tmp6b:
                rlm6a = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                      base_dir_override=tmp6b)
                with contextlib.redirect_stdout(StringIO()):
                    rlm6a.move_to_step("OPTIMIZE")
                zed_before = rlm6a.context.zed_checksum
                rlm6b = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                      base_dir_override=tmp6b)
                rlm6b.move_to_step("CONFIG")
                rlm6b.context.cfg.stat_model.ridge_regularization = 0.02
                out6b = StringIO()
                with contextlib.redirect_stdout(out6b):
                    rlm6b.move_to_step("OPTIMIZE")
                logs6b = out6b.getvalue()
                assert "The ridge regularization parameter has changed." in logs6b, logs6b[-2000:]
                assert "Checkpoint config mismatch. Starting from scratch." in logs6b, logs6b[-2000:]
                assert "L-BFGS - [" in logs6b
                assert rlm6b.context.zed_checksum == zed_before, "zed is unchanged (only ridge)"
                cp6b = load_optimization_checkpoint(Path(tmp6b) / "checkpoint_optimize.dat")
                assert np.float32(cp6b["ridge_regularization"]) == np.float32(0.02)
                assert cp6b["zed_checksum"] == zed_before
                check("H6b R1: ridge-only change -> scratch (same as clipping)", True)
        except Exception as exc:
            check("H6b R1: ridge-only change -> scratch (same as clipping)",
                  False, f"{exc!r}\n{traceback.format_exc()}")
        # H7: use_cache=False -> no load, but the checkpoint is still saved
        # (the D-071 R1 pattern: a cache-disabled run still warms the cache)
        try:
            with tempfile.TemporaryDirectory(dir=ROOT / "build" / "tmp") as tmp7:
                rlm5a = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                      base_dir_override=tmp7)
                with contextlib.redirect_stdout(StringIO()):
                    rlm5a.move_to_step("OPTIMIZE")
                assert (Path(tmp7) / "checkpoint_optimize.dat").exists()
                # second instance: the checkpoint now EXISTS, but
                # use_cache=False must gate the load off (cfg is only
                # available after the CONFIG level has run)
                rlm5b = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                      base_dir_override=tmp7)
                with contextlib.redirect_stdout(StringIO()):
                    rlm5b.move_to_step("GRADIENT")
                # the switch is the CONTEXT field the CONFIG worker
                # populated from cfg (the worker gate reads ctx.use_cache)
                rlm5b.context.use_cache = False
                out5 = StringIO()
                with contextlib.redirect_stdout(out5):
                    rlm5b.move_to_step("OPTIMIZE")
                logs5 = out5.getvalue()
                assert "Checkpoint found" not in logs5
                assert "already completed" not in logs5
                assert "Resuming" not in logs5
                assert "L-BFGS - [" in logs5
                assert (Path(tmp7) / "checkpoint_optimize.dat").exists()
                check("H7 use_cache=False: no load, checkpoint still saved (D-071 R1 pattern)", True)
        except Exception as exc:
            check("H7 use_cache=False: no load, checkpoint still saved (D-071 R1 pattern)",
                  False, f"{exc!r}\n{traceback.format_exc()}")
        # H8: R2 (D-096) — a corrupted checkpoint must not kill the worker:
        # delete + scratch + a final checkpoint is written
        try:
            with tempfile.TemporaryDirectory(dir=ROOT / "build" / "tmp") as tmp8:
                rlm8a = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                      base_dir_override=tmp8)
                with contextlib.redirect_stdout(StringIO()):
                    rlm8a.move_to_step("OPTIMIZE")
                cp_path = Path(tmp8) / "checkpoint_optimize.dat"
                data = bytearray(cp_path.read_bytes())
                data[-1] ^= 0x01
                cp_path.write_bytes(bytes(data))  # corrupt, sidecar untouched
                rlm8b = LogisticModel(json_config, verbosity=Verbosity.HIGH,
                                      base_dir_override=tmp8)
                out8 = StringIO()
                with contextlib.redirect_stdout(out8):
                    rlm8b.move_to_step("OPTIMIZE")
                logs8 = out8.getvalue()
                assert "Checkpoint could not be loaded" in logs8, logs8[-2000:]
                assert "Deleting it and starting from scratch." in logs8
                assert "L-BFGS - [" in logs8
                assert cp_path.exists(), "the final checkpoint was re-saved"
                cp8 = load_optimization_checkpoint(cp_path)
                assert cp8["converged"] == (str(cp8["reason"]).startswith("CONVERGED"))
                check("H8 R2: corrupted checkpoint -> delete + scratch + re-save", True)
        except Exception as exc:
            check("H8 R2: corrupted checkpoint -> delete + scratch + re-save",
                  False, f"{exc!r}\n{traceback.format_exc()}")


h_main()

# ---------------------------------------------------------------- report
n_fail = 0
for name, ok, detail in results:
    if not ok:
        n_fail += 1
        print(f"FAIL {name}: {detail}")
print(f"\n{len(results)} checks, {n_fail} mismatches")
sys.exit(1 if n_fail else 0)
