#
# verify_gradient.py — independent verification probe for the GRADIENT
# bring-in (hlp_gradient.py, wrk_gradient.py,
# test_wrk_gradient.py, rlm_02.json), re-pinned to the
# post-D-094-campaign state.
#
# Tiers:
#   A  hlp_gradient.py structure (post-campaign)
#   B  wrk_gradient.py structure (post-campaign)
#   C  test_wrk_gradient.py structure (post-campaign)
#   D  live pipeline through GRADIENT (DB required) + independent
#      float64 re-derivation of f and g (w = 0 and w != 0)
#   E  cross-file (logistic_model, schemas, pyproject, rlm_02.json)
#   G  dedicated test_hlp_gradient.py (no DB)
#
# Run:  .venv/bin/python scratch/verify_gradient.py
#
import re
import sys
import tempfile
import traceback
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # the root test/ tree (the test.reversi helpers)
SRC = ROOT / "src" / "reversi"

results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))


def read(name):
    if name.startswith("test/"):
        # the zone-abbreviated test path: test/test_X.py = the lm zone
        return (ROOT / "test" / "reversi" / "lm" / name[len("test/"):]).read_text()
    return (SRC / "lm" / name).read_text()


def ws_lines(text):
    return {i + 1 for i, ln in enumerate(text.splitlines())
            if ln != ln.rstrip() and not ln.strip().startswith("#")}


# ---------------------------------------------------------------- A tier
print("== tier A: hlp_gradient.py structure (post D-094)")
a = read("hlp_gradient.py")
al = a.splitlines()
check("A1 line count 180", len(al) == 180, f"{len(al)}")
check("A2 __all__", "__all__ = ['hlp_gradient_compute', 'sigmoid']" in a)
check("A3 scipy import", "from scipy.special import expit" in a)
check("A3b numba import (I-013)", "from numba import njit, prange" in a)
check("A4 TYPE_CHECKING LMContext",
      "if TYPE_CHECKING:" in a and
      "from reversi.lm.logistic_model import LMContext" in a)
check("A5 no validate_call (hlp_gradient_compute — the L166 class)",
      "validate_call" not in a)
check("A6 no pydantic import", "pydantic" not in a)
check("A7 no ws lines", ws_lines(a) == set(), str(sorted(ws_lines(a))))
check("A8 sigmoid docstring (descriptive)",
      "Compute the sigmoid (logistic) function element-wise" in a
      and "The scipy expit form is numerically stable for extreme "
      "values of x" in a)
check("A9 four defs (I-013: the _hp_fg_kernel module def + the 4-space fg_hp; the classic fg is nested 8-space in the branch)",
      re.findall(r"^(?:def |    def ).*$", a, re.M) ==
      ["def sigmoid(x: np.ndarray) -> np.ndarray:",
       "def _hp_fg_kernel(X, w, z, g_blocks, norm_blocks):",
       "def hlp_gradient_compute(ctx: \"LMContext\",",
       "    def fg_hp(w: npt.NDArray[np.float32]) -> Tuple[np.float32, npt.NDArray[np.float32]]:"])
check("A10 docstring claims",
      "normalized by the number of positions (M)" in a and
      "Captures X, z, and alpha in a closure" in a)
check("A11 return expit", "return expit(x)" in a)
check("A12 T3 no-validation note (L95)",
      al[94] == "#: Here validation is not possible, it brings in a convoluted issue with circular imports.")
check("A13 R1 float32 cast",
      "return np.float32(f), g.astype(np.float32, copy=False)" in a)
check("A14 I-013 kernel structure (D-325: hi_perf_blocks replaces _HP_BLOCKS)",
      "@njit(parallel=True, cache=True)" in a and
      "hi_perf_blocks: int = 8" in a and
      "for b in prange(T_):" in a and
      "g_blocks = np.zeros((hi_perf_blocks, N), dtype=np.float64)" in a
      and "norm_blocks = np.zeros(hi_perf_blocks, dtype=np.float64)" in a
      and "_HP_BLOCKS" not in a)
check("A15 I-013 flag + variant marker",
      "high_performance: bool = False" in a and
      "fg.high_performance = False" in a and
      "fg_hp.high_performance = True" in a)

# ---------------------------------------------------------------- B tier
print("== tier B: wrk_gradient.py structure (post D-094)")
b = read("wrk_gradient.py")
bl = b.splitlines()
check("B1 line count 72", len(bl) == 72, f"{len(bl)}")
check("B2 worker name", 'Worker("GRADIENT", _up, _down)' in b)
check("B3 T2 factory @validate_call + pydantic import",
      "from pydantic import validate_call, ConfigDict" in b and
      "@validate_call(config=ConfigDict(arbitrary_types_allowed=True))\n"
      "def wrk_gradient() -> Worker:" in b)
check("B4 non-cache comment",
      "GRADIENT building is a closure generation, very fast. No cache needed." in b)
check("B5 _up sets fg (I-013: the config flag is passed; D-325: + the block count)",
      "high_performance = ctx.cfg.optimization.high_performance_fg" in b
      and "hi_perf_blocks = ctx.cfg.optimization.hi_perf_blocks" in b
      and "ctx.fg = hlp_gradient_compute(" in b
      and "        ctx, high_performance=high_performance, hi_perf_blocks=hi_perf_blocks)" in b
      and 'f"Gradient function generated (high_performance: {high_performance})."' in b)
check("B6 _down clears fg", "ctx.fg = None" in b)
check("B7 no ws lines", ws_lines(b) == set(), str(sorted(ws_lines(b))))
check("B8 M4 triple blanks kept (house worker style, L39-41 + L43-45)",
      all(bl[i] == "" for i in (38, 39, 40, 42, 43, 44)))
check("B9 factory docstring",
      '"""Return the GRADIENT worker instance."""' in b)

# ---------------------------------------------------------------- C tier
print("== tier C: test_wrk_gradient.py structure (post D-094)")
c = read("test/test_wrk_gradient.py")
cl = c.splitlines()
check("C1 line count 184", len(cl) == 184, f"{len(cl)}")
check("C2 header gate claim (D-130 tier wording)",
      "a live regab DB + LONG=1 is required;" in c and
      "SKIP_REGAB_DB=1 skips the DB-gated tests" in c and
      "VLONG=1 implies LONG, see test.reversi.tags" in c)
code_no_header = "\n".join(ln for ln in cl if not ln.strip().startswith("#"))
check("C3 T5 gate in code (D-130: the db_long_gate idiom)",
      "db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates" in code_no_header and
      "# The SKIP_REGAB_DB gate, as in test_regab" in c)
check("C4 T6 D-085 idiom",
      "from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE" in c and
      "tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))" in c and
      "Path(self._tmp.name)" in c and
      "WORKSPACE_ROOT / \"test\" / \"reversi\" / \"data\" / \"rlm_02.json\"" in c
      and "mkdtemp" not in c and "shutil" not in c)
check("C5 2 classes 4 tests (I-013: the no-DB flag-wiring class)",
      c.count("class Test") == 2 and
      re.findall(r"    def test_\w+", c) ==
      ["    def test_generate_gradient", "    def test_down_clears_gradient",
       "    def test_up_flag_true_builds_hp_variant",
       "    def test_up_flag_false_builds_classic_variant"])
check("C11 I-013 wiring test (the worker + the Context mock)",
      "from reversi.lm.wrk_gradient import wrk_gradient" in c and
      "class TestGradientFlagWiring" in c and
      "ctx = Context()" in c and
      "wrk_gradient().up(ctx)" in c and
      "ctx.fg.high_performance" in c)
check("C6 defensive tearDown",
      "if getattr(self, 'patcher_stdout', None) is not None:" in c and
      "if getattr(self, '_tmp', None) is not None:\n            self._tmp.cleanup()" in c)
check("C7 no ws lines", ws_lines(c) == set(), str(sorted(ws_lines(c))))
check("C8 goldens",
      "0.02049378" in c and "3.558e-4" in c and
      "-2.395e-4" in c and "1.101e-3" in c)
check("C9 shape pins", "(199952, 8)" in c and "2981" in c)
check("C10 step pins + T7 _down test (re-pinned: ZED 9 / GRADIENT 10)",
      "move_to_step('ZED')" in c and "assertEqual(self.rlm.current_step, 9)" in c
      and "move_to_step('GRADIENT')" in c and "assertEqual(self.rlm.current_step, 10)" in c
      and "self.rlm.move_to_step(9)" in c
      and "assertEqual(self.rlm.current_worker_name, 'ZED')" in c
      and "assertIsNone(self.rlm.context.fg)" in c)

# ---------------------------------------------------------------- D tier
print("== tier D: live pipeline + independent re-derivation (DB)")
from reversi.tools.state_machine import Verbosity
from reversi.lm.logistic_model import LogisticModel


def live(name, fn):
    try:
        fn()
        check(name, True)
    except Exception as exc:
        check(name, False, f"{exc!r}\n{traceback.format_exc()}")


def d_main():
    with tempfile.TemporaryDirectory(dir=ROOT / "build" / "tmp") as tmp:
        json_config = str(ROOT / "test" / "reversi" / "data" / "rlm_02.json")
        rlm = LogisticModel(json_config, verbosity=Verbosity.LOW,
                            base_dir_override=tmp)

        # (D1 pre-state / D2 move to GRADIENT / D3 fg callable /
        #  D4 X/w/z shapes+dtypes deleted at D-106 step 3, class c:
        #  test_wrk_gradient.py pins all of it — setUp the
        #  step-7 pre-state, test_generate_gradient the fg-None
        #  pre-state + step 8 + callable + the (199952, 8) / 2981
        #  shapes, test_down_clears_gradient the step pins again.
        #  The dtype sub-assertions are the cross-module contracts
        #  of ZED / DESIGN_MTR, pinned by their own module tests.)

        def d5():
            ctx = rlm.context
            alpha = ctx.cfg.stat_model.ridge_regularization / 199952
            assert abs(alpha - 0.01 / 199952) < 1e-18, alpha
            assert ctx.cfg.stat_model.logit_clipping == 0.01

        def d6():
            ctx = rlm.context
            f, g = ctx.fg(ctx.w)
            # f is float32 (the float32 dot of 199952 terms)
            assert f.dtype == np.float32, f.dtype
            # independent float64 re-derivation, w = 0
            X = ctx.design_matrix.astype(np.float64)
            z = ctx.z.astype(np.float64)
            M = X.shape[0]
            zh = 1.0 / (1.0 + np.exp(-0.0))  # sigmoid(0) = 0.5, lp = 0
            rn = zh - z
            f_ref = 0.5 * float(np.dot(rn, rn) / M)
            # rtol 1e-5: the pipeline dot accumulates in float32
            assert abs(float(f) - f_ref) <= 1e-5 * f_ref, (float(f), f_ref)
            # the test golden, at the test's own tolerance
            assert abs(float(f) - 0.02049378) <= 1e-6 * 0.02049378 + 1e-7

        def d7():
            ctx = rlm.context
            f, g = ctx.fg(ctx.w)
            X = ctx.design_matrix
            z = ctx.z.astype(np.float64)
            M = X.shape[0]
            dzh_rn = 0.25 * (0.5 - z)  # dzh = 0.25 at w = 0
            g0 = np.zeros(2981, dtype=np.float64)
            np.add.at(g0, X.ravel(), np.repeat(dzh_rn, 8))
            g0 /= M
            for k, golden in ((0, 3.558e-4), (1, -2.395e-4), (2980, 1.101e-3)):
                assert abs(float(g[k]) - g0[k]) <= 1e-4 * abs(g0[k]) + 1e-7, (k, float(g[k]), g0[k])
                assert abs(float(g[k]) - golden) <= 1e-4 * abs(golden) + 1e-7
            # R1 (D-093) FIXED (D-094): g is now float32 (the
            # np.float32(f) + g.astype(np.float32) cast) — matching
            # the return annotation.
            assert g.dtype == np.float32, g.dtype

        def d8():
            ctx = rlm.context
            rng = np.random.default_rng(42)
            w = (rng.standard_normal(2981) * 0.05).astype(np.float32)
            f, g = ctx.fg(w)
            Xi = ctx.design_matrix  # uint32 for the fancy indexing
            w64 = w.astype(np.float64)
            z = ctx.z.astype(np.float64)
            M = Xi.shape[0]
            lp = np.sum(w64[Xi], axis=1)
            zh = 1.0 / (1.0 + np.exp(-lp))
            rn = zh - z
            f_ref = 0.5 * (float(np.dot(rn, rn)) / M + 0.01 / M * float(np.dot(w64, w64)))
            assert abs(float(f) - f_ref) <= 1e-5 * abs(f_ref) + 1e-7, (float(f), f_ref)
            dzh_rn = zh * (1 - zh) * rn
            g0 = np.zeros(2981, dtype=np.float64)
            np.add.at(g0, Xi.ravel(), np.repeat(dzh_rn, 8))
            g_ref = g0 / M + 0.01 / M * w64
            assert np.max(np.abs(g.astype(np.float64) - g_ref)) <= 1e-5 * np.max(np.abs(g_ref)) + 1e-7, \
                float(np.max(np.abs(g.astype(np.float64) - g_ref)))

        def d9():
            ctx = rlm.context
            a1, g1 = ctx.fg(ctx.w)
            a2, g2 = ctx.fg(ctx.w)
            assert a1 == a2
            assert np.array_equal(g1, g2)

        def d10():
            files = sorted(p.name for p in Path(tmp).iterdir())
            # the no-cache slots of the CURRENT numbering: 09 = ZED,
            # 10 = GRADIENT (they were 07/08 before the I-017 reordering)
            assert not [n for n in files if n.startswith("rlmwf_09")], files
            assert not [n for n in files if n.startswith("rlmwf_10")], files
            for n in ("rlmwf_04_POSITIONS.dat",
                      "rlmwf_05_INDEXES.dat", "rlmwf_07_WMAPS.dat",
                      "rlmwf_08_DESIGN_MTR.dat"):
                assert n in files, files

        # (D11 _down live (fg None) deleted at D-106 step 3, class
        #  c: test_down_clears_gradient pins the same scope — step
        #  7, name ZED, fg None)

        def d12():
            ctx = rlm.context
            fs = ctx.feature_set
            assert fs.intercept is None
            names = sorted(p.name for p in fs.pset.patterns)
            assert names == ["DIAG3", "EDGE"], names
            assert len(fs.mset.mobilities) == 0
            total = sum(p.n_instances for p in fs.pset.patterns)
            assert total == 8, total

        # The pipeline bootstrap the deleted D1/D2 used to carry as
        # side effects: move to GRADIENT runs the whole chain
        # (POSITIONS ... DESIGN_MTR, ZED, GRADIENT) and populates
        # design_matrix / w / z / feature_set / fg that D5-D12 read.
        # (The assertions around the moves — the step-7 pre-state,
        # step 8, name GRADIENT, fg callable — were class c, deleted
        # at D-106 step 3: test_wrk_gradient.py pins them.)
        rlm.move_to_step("GRADIENT")

        for name, fn in (("D5 alpha + clipping", d5),
                         ("D6 f(w=0) re-derived", d6),
                         ("D7 g(w=0) re-derived + float32 (R1)", d7),
                         ("D8 f+g(w!=0) re-derived (ridge)", d8),
                         ("D9 closure stateless (2 calls)", d9),
                         ("D10 no rlmwf_07*/08* files", d10),
                         ("D12 feature set (8 instances)", d12)):
            live(name, fn)


live("D0 live pipeline through GRADIENT", d_main)

# ---------------------------------------------------------------- E tier
print("== tier E: cross-file")
lm = read("logistic_model.py")
check("E1 LMContext fg field", "    fg: Any = None" in lm)
# (E2/E3 pipeline-state pins moved to the hub verify_logistic_model.py
# V3c/V3d at D-106)
py = (ROOT / "pyproject.toml").read_text()
check("E4 T1 scipy in pyproject", '"scipy",' in py)
import scipy
check("E5 scipy in venv 1.18.1", scipy.__version__ == "1.18.1", scipy.__version__)
check("E6 StatModelConfig ridge field",
      "ridge_regularization: float = Field(default=0.00, ge=0.00)" in read("hlp_config_schemas.py"))
j = (ROOT / "test" / "reversi" / "data" / "rlm_02.json").read_text()
check("E7 rlm_02 config",
      '"logit_clipping": 0.01' in j and '"ridge_regularization": 0.01' in j
      and '"frequency_cut_off": 1' in j and '"intercept": false' in j
      and '"empty_count": 20' in j and '"bid": [6, 7]' in j
      and j.count('"name": "') >= 2)
check("E8 rlm_02 trailing comma (JSON5)",
      re.search(r'"ridge_regularization": 0\.01,\s*\n\s*\}', j) is not None)

# ---------------------------------------------------------------- G tier
print("== tier G: dedicated test_hlp_gradient.py (no DB)")
gd = read("test/test_hlp_gradient.py")
gdl = gd.splitlines()
check("G1 line count 284 + no-DB header claim",
      len(gdl) == 284 and
      "no live regab DB required" in gd and
      "as in test_hlp_zed" in gd, f"{len(gdl)}")
check("G2 3 classes 15 tests (I-013: the TestHighPerformanceFg class; D-325: + the block-count test)",
      gd.count("class Test") == 3 and
      len(re.findall(r"    def test_\w+", gd)) == 15)
check("G9 I-013 HP tests (equivalence, f32 contract, determinism, marker; D-325: + the block-count test)",
      "class TestHighPerformanceFg" in gd and
      "test_hp_matches_classic" in gd and
      "test_hp_output_dtypes" in gd and
      "test_hp_deterministic" in gd and
      "test_hp_variant_markers" in gd and
      "test_hp_block_count" in gd and
      "high_performance=True" in gd)
check("G3 no DB wiring",
      "from reversi.lm.logistic_model" not in gd and
      "SKIP_REGAB_DB" not in gd and
      "test.reversi.paths" not in gd and
      "import os" not in gd)
check("G4 SimpleNamespace mock",
      "from types import SimpleNamespace" in gd and
      "SimpleNamespace(" in gd and
      "stat_model=SimpleNamespace(ridge_regularization=ridge)" in gd)
check("G5 zero-weights goldens",
      "4 / 75" in gd and "1 / 30" in gd and "-1 / 30" in gd)
check("G6 R1 dtype pins",
      "self.assertEqual(f.dtype, np.float32)" in gd and
      "self.assertEqual(g.dtype, np.float32)" in gd)
check("G7 ridge scaling pin (0.5 * (b-a)/M * ||w||^2)",
      "0.5 * (0.50 - 0.01) / 3 * float(np.dot(dw, dw))" in gd and
      "(0.50 - 0.01) / 3 * dw" in gd)
check("G8 minlength empty-bucket pin",
      "self.assertEqual(g.shape, (3,))" in gd and
      "0.015 * 0.3" in gd)

# ---------------------------------------------------------------- report
n_fail = 0
for name, ok, detail in results:
    if not ok:
        n_fail += 1
        print(f"FAIL {name}: {detail}")
print(f"\n{len(results)} checks, {n_fail} mismatches")
sys.exit(1 if n_fail else 0)
