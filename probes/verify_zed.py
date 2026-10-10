#!/usr/bin/env python3
#
# verify_zed.py — scratch probe (gitignored) for the ZED level, re-pinned
# to the POST-CAMPAIGN state (D-092: T1-T8 applied).
#
# Tiers:
#   A  hlp_zed.py structural pins (post T6/T7/T8)
#   B  wrk_zed.py structural pins (post T2/T8)
#   C  test_wrk_zed.py structural pins (post T1/T4/T5/T8)
#   D  live golden (rlm_01.json pipeline through ZED, independent recompute)
#   F  cross-module facts (logistic_model.py, repo state)
#   G  dedicated test_hlp_zed.py (post T3)
#
import contextlib
import hashlib
import io
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # the root test/ tree (the test.reversi helpers)
SRC = ROOT / 'src' / 'reversi'

RESULTS = []

def check(name, cond, detail=''):
    RESULTS.append((name, bool(cond), detail))
    return cond

def lines_of(relpath):
    if relpath.startswith('test/'):
        # the zone-abbreviated test path: test/test_X.py = the lm zone
        path = ROOT / 'test' / 'reversi' / 'lm' / relpath[len('test/'):]
    else:
        path = SRC / 'lm' / relpath
    return path.read_text().splitlines()

# ---------------------------------------------------------------- A tier
rlm = lines_of('hlp_zed.py')
check('A1  hlp_zed.py is 129 lines (post T6 note + T7 decorator)', len(rlm) == 129, f'{len(rlm)}')
check('A2  __all__ = class + compute + factory (L41-43)',
      rlm[40] == "__all__ = ['LMZed',"
      and rlm[41] == "           'hlp_zed_compute',"
      and rlm[42] == "           'zed_fun_factory']")
check('A3  class LMZed at L46', rlm[45].startswith('class LMZed'))
check('A4  __init__ @validate_call (L49-50) w/ arbitrary_types_allowed',
      rlm[48] == '    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))'
      and rlm[49] == '    def __init__(self,')
check('A5  compute_sha3_256_hash decorated (L67), hashes z.tobytes() only (L79)',
      rlm[66] == '    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))'
      and rlm[67] == '    def compute_sha3_256_hash(self) -> str:'
      and rlm[78] == '        hasher.update(self.z.tobytes())')
check('A6  T7 DONE: zed_fun_factory decorated (L84) + def (L85)',
      rlm[83] == '@validate_call(config=ConfigDict(arbitrary_types_allowed=True))'
      and rlm[84] == 'def zed_fun_factory(logit_clipping: float) -> Tuple[Callable[[npt.NDArray[np.int8]], npt.NDArray[np.float32]],')
check('A7  factory math pins: a=0.5 (L98), b=(1-2c)/128 (L99), a1 (L105), b1 (L106)',
      rlm[97] == '    a = np.float32(0.5)'
      and rlm[98] == '    b = np.float32((1. - 2. * logit_clipping) / 128.)'
      and rlm[104] == '    a1 = np.float32(-64. / (1. - 2. * logit_clipping))'
      and rlm[105] == '    b1 = np.float32(128. / (1. - 2. * logit_clipping))')
check('A8  T6 DONE: the no-validation note at L114 above hlp_zed_compute (L115)',
      rlm[113] == '#: Here validation is not possible, it brings in a convoluted issue with circular imports.'
      and rlm[114] == 'def hlp_zed_compute(ctx: "LMContext") -> LMZed:'
      and sum(1 for l in rlm if 'Here validation is not possible' in l) == 1)
check('A9  compute body: alpha (L125), y = ctx.game_values (L127), z = y2z(y) (L128)',
      rlm[124] == '    alpha = ctx.cfg.stat_model.logit_clipping'
      and rlm[126] == '    y = ctx.game_values'
      and rlm[127] == '    z = y2z(y)')
check('A10 no cache API in hlp_zed (no store / load / is_cache_consistent)',
      not any(k in l for l in rlm for k in ('def hlp_zed_store', 'def hlp_zed_load', 'def hlp_zed_is_cache')))
check('A11 TYPE_CHECKING guard for LMContext (L37-38)',
      rlm[36] == 'if TYPE_CHECKING:' and rlm[37] == '    from reversi.lm.logistic_model import LMContext')
check('A12 T8 DONE: 0 trailing-ws lines',
      {i + 1 for i, l in enumerate(rlm) if l != l.rstrip()} == set())
# (A13/A14/A15 factory(0.02) golden + round-trip + endpoints deleted
#  at D-106 step 3, class c: test_hlp_zed.py::TestZedFunFactory pins
#  the same — test_factory_alpha_0.02_golden (the same literal),
#  test_round_trip, and the endpoints for TWO clippings (0.02 AND
#  0.03, a superset of the probe's))

# ---------------------------------------------------------------- B tier
wk = lines_of('wrk_zed.py')
check('B1  wrk_zed.py is 75 lines (post T2 +1 import +1 decorator + the 2 docstrings in the cascade pass)', len(wk) == 75, f'{len(wk)}')
check('B2  __all__ = ["wrk_zed"] (L42)', wk[41] == "__all__ = ['wrk_zed']")
check('B3  T2 DONE: pydantic import (L32) + factory decorated (L72) + def (L73)',
      wk[31] == 'from pydantic import validate_call, ConfigDict'
      and wk[71] == '@validate_call(config=ConfigDict(arbitrary_types_allowed=True))'
      and wk[72] == 'def wrk_zed() -> Worker:')
check('B4  no cache_manager import (by design: no disk caching, L50 comment)',
      'cache_manager' not in '\n'.join(wk)
      and 'ZED computation is very fast (vectorized math), so we compute it on the fly without disk caching.' in wk[49])
check('B5  _up sets ctx.y2z / z2y / z / zed_checksum (L54-57)',
      wk[53] == '    ctx.y2z = zed_obj.y2z' and wk[54] == '    ctx.z2y = zed_obj.z2y'
      and wk[55] == '    ctx.z = zed_obj.z' and wk[56] == '    ctx.zed_checksum = zed_checksum')
check('B6  _down clears ALL FOUR attributes to None (L66-69)',
      wk[65] == '    ctx.y2z = None' and wk[66] == '    ctx.z2y = None'
      and wk[67] == '    ctx.z = None' and wk[68] == '    ctx.zed_checksum = None')
check('B7  Worker name is "ZED" (L75)', wk[74] == '    return Worker("ZED", _up, _down)')
check('B8  T8 DONE: trailing-ws lines = header only (6,11,16,21)',
      {i + 1 for i, l in enumerate(wk) if l != l.rstrip()} == {6, 11, 16, 21})

# ---------------------------------------------------------------- C tier
tc = lines_of('test/test_wrk_zed.py')
check('C1  test_wrk_zed.py is 160 lines (post T1/T4/T5 + the cascade pass: 1 bare-# + import os + comment rejoins)', len(tc) == 160, f'{len(tc)}')
check('C2  2 classes: TestZedFunFactory (L61, 1 test) + TestLMWorkerZed (L77, 2 tests)',
      tc[60] == 'class TestZedFunFactory(unittest.TestCase):'
      and tc[76] == 'class TestLMWorkerZed(unittest.TestCase):'
      and sum(1 for l in tc if l.startswith('    def test_')) == 3)
check('C3  the db_long_gate idiom in setUp (L83) + paths import (L56) + NO os import (dead, dropped in the cascade pass)',
      'import os' not in tc
      and tc[82] == "        db_long_gate(self)  # the SKIP_REGAB_DB + LONG gates"
      and tc[55] == 'from test.reversi.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE'
      and 'from test.reversi.tags import db_long_gate' in '\n'.join(tc))
check('C4  header CLAIMS the gate (L37-38, D-130 tier wording) — the claim is NOW true (ties to C3)',
      'a live regab DB + LONG=1 is required;' in tc[36]
      and 'SKIP_REGAB_DB=1 skips the DB-gated tests' in tc[36]
      and 'VLONG=1 implies LONG, see test.reversi.tags' in tc[37])
check('C5  T4 DONE: TemporaryDirectory FIRST (L90) under CUSTOM_TMP_BASE + tmp_dir = Path (L91) + WORKSPACE_ROOT json (L92)',
      tc[89] == '        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))'
      and tc[90] == '        self.tmp_dir = Path(self._tmp.name)'
      and tc[91] == '        self.json_config = str(WORKSPACE_ROOT / "test" / "reversi" / "data" / "rlm_01.json")')
check('C6  T4 DONE: no dead imports — no shutil, Path is load-bearing (Path(self._tmp.name))',
      'import shutil' not in '\n'.join(tc) and tc[50] == 'from pathlib import Path'
      and '\n'.join(tc).count('Path(') == 1)
check('C7  step pins (re-pinned: DESIGN_MTR = 8, ZED = 9)',
      tc[98] == "        self.rlm.move_to_step('DESIGN_MTR')" and tc[99] == '        self.assertEqual(self.rlm.current_step, 8)'
      and tc[121] == "        self.rlm.move_to_step('ZED')" and tc[122] == '        self.assertEqual(self.rlm.current_step, 9)')
check('C8  goldens: logit_clipping 0.03 (L112), y (10,) int8 (L116), z (10,) float32 (L132-141)',
      tc[111] == '        expected_logit_clipping = 0.03'
      and tc[115] == '        expected_y = np.array([10, 36, -22, 18, -16, 14, -22, 20, 0, 2], dtype=np.int8)'
      and tc[131] == '        expected_z = np.array([0.5734375,'
      and tc[140] == '                               0.5146875], dtype=np.float32)')
check('C9  T5 DONE: test_down_clears_zed_attributes — move(8), step 8, DESIGN_MTR name, 4 assertIsNone',
      tc[144] == '    def test_down_clears_zed_attributes(self):'
      and tc[149] == '        self.rlm.move_to_step(8)'
      and tc[150] == '        self.assertEqual(self.rlm.current_step, 8)'
      and tc[151] == "        self.assertEqual(self.rlm.current_worker_name, 'DESIGN_MTR')"
      and tc[152:156] == ['        self.assertIsNone(self.rlm.context.y2z)',
                          '        self.assertIsNone(self.rlm.context.z2y)',
                          '        self.assertIsNone(self.rlm.context.z)',
                          '        self.assertIsNone(self.rlm.context.zed_checksum)'])
check('C10 T8 DONE: trailing-ws lines = header only (6,11,16,21)',
      {i + 1 for i, l in enumerate(tc) if l != l.rstrip()} == {6, 11, 16, 21})

# ---------------------------------------------------------------- D tier (live)
sys.path.insert(0, str(ROOT / 'src'))
from reversi.lm.logistic_model import LogisticModel  # noqa: E402
from reversi.tools.state_machine import Verbosity  # noqa: E402

CLIP = 0.03

tmp = tempfile.TemporaryDirectory(dir=str(ROOT / 'build' / 'tmp'))
try:
    base = Path(tmp.name)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rlm01 = LogisticModel(str(ROOT / 'test' / 'reversi' / 'data' / 'rlm_01.json'),
                              verbosity=Verbosity.HIGH, base_dir_override=base)
        # (D1 c? resolves to a (KEEP): the test pins only the y2z +
        #  z pre-state; z2y / zed_checksum pre-state are probe-unique)
        check('D1  pre-state before the first ZED up: y2z/z2y/z/zed_checksum all None',
              rlm01.context.y2z is None and rlm01.context.z2y is None
              and rlm01.context.z is None and rlm01.context.zed_checksum is None)
        rlm01.move_to_step('ZED')
    # (D2 step 7 / name ZED deleted at D-106 step 3, class c:
    #  test_wrk_zed.py::test_compute_zed pins it)
    y = rlm01.context.game_values
    # (D3 game_values == golden y deleted at D-106 step 3, class c:
    #  the test pins expected_y verbatim. The y binding stays: D5
    #  and D10 use it.)
    z = rlm01.context.z
    # (D4 ctx.z == golden z deleted at D-106 step 3, class c: the
    #  test pins expected_z verbatim (the same 10 floats). The z
    #  binding stays: D5-D7 use it.)
    c = rlm01.context.cfg.stat_model.logit_clipping
    b64 = np.float32((1. - 2. * c) / 128.)
    z_ref = np.float32(0.5) + y.astype(np.float32) * b64
    check('D5  independent float32 recompute 0.5 + y*(1-2c)/128 == ctx.z (exact)',
          np.array_equal(z, z_ref))
    z_ref64 = 0.5 + y.astype(np.float64) * ((1. - 2. * CLIP) / 128.)
    check('D6  float64 reference agrees (allclose 1e-6/1e-7)',
          np.allclose(z, z_ref64, rtol=1e-6, atol=1e-7))
    check('D7  ctx.zed_checksum == sha3_256(z.tobytes()) (hash covers z only)',
          rlm01.context.zed_checksum == hashlib.sha3_256(z.tobytes()).hexdigest(),
          rlm01.context.zed_checksum)
    y2z, z2y = rlm01.context.y2z, rlm01.context.z2y
    # (D8 a? resolves to a (KEEP): the test pins y2z not-None but
    #  never the z2y pre-down wiring)
    check('D8  ctx.y2z / ctx.z2y are callables (closures from the factory)',
          callable(y2z) and callable(z2y))
    check('D9  live endpoints: y2z(-64) ~= 0.03, y2z(0) == 0.5, y2z(64) ~= 0.97',
          abs(float(y2z(np.int8(-64))) - 0.03) < 1e-6
          and float(y2z(np.int8(0))) == 0.5
          and abs(float(y2z(np.int8(64))) - 0.97) < 1e-6)
    check('D10 live round-trip: z2y(y2z(y)) == float32(y) (allclose 1e-6/1e-7)',
          np.allclose(z2y(y2z(y)), y.astype(np.float32), rtol=1e-6, atol=1e-7))
    files = sorted(p.name for p in base.iterdir())
    expected_files = sorted(
        ['rlmwf_04_POSITIONS.dat', 'rlmwf_04_POSITIONS.dat.SHA3-256',
         'rlmwf_05_INDEXES.dat', 'rlmwf_05_INDEXES.dat.SHA3-256',
         'rlmwf_07_WMAPS.dat', 'rlmwf_07_WMAPS.dat.SHA3-256',
         'rlmwf_08_DESIGN_MTR.dat', 'rlmwf_08_DESIGN_MTR.dat.SHA3-256'])
    check('D11 NO rlmwf_07_ZED* file: no disk caching for ZED (by design)',
          files == expected_files, str(files))
    with contextlib.redirect_stdout(io.StringIO()):
        rlm01.move_to_step(6)
    # (D12 _down live (step 6, 4 attrs None) deleted at D-106 step
    #  3, class c: test_down_clears_zed_attributes pins exactly this
    #  scope — the 4 assertIsNone at L153-156)
finally:
    tmp.cleanup()

# ---------------------------------------------------------------- F tier (cross)
lm_lines = lines_of('logistic_model.py')
check('F1  LMContext zed fields pre-declared (the block shifts with every '
      'insertion above it)',
      lm_lines[147] == '    zed_checksum: str | None = None'
      and lm_lines[148] == '    y2z: Any = None'
      and lm_lines[149] == '    z2y: Any = None'
      and lm_lines[150] == '    z: Any = None')
# (F2/F3 pipeline-state pins moved to the hub verify_logistic_model.py
# V3c/V3d at D-106)
check('F4  T3 DONE: dedicated test_hlp_zed.py exists, 10 tests, no DB wiring',
      (ROOT / 'test' / 'reversi' / 'lm' / 'test_hlp_zed.py').exists()
      and sum(1 for l in lines_of('test/test_hlp_zed.py') if l.startswith('    def test_')) == 10
      and 'from reversi.lm.logistic_model' not in '\n'.join(lines_of('test/test_hlp_zed.py')))
check('F5  D-007 mirror docs written for all 4 zed files (post-campaign state)',
      (ROOT / 'docs' / 'src' / 'reversi' / 'lm' / 'hlp_zed.md').exists()
      and (ROOT / 'docs' / 'src' / 'reversi' / 'lm' / 'wrk_zed.md').exists()
      and (ROOT / 'docs' / 'test' / 'reversi' / 'lm' / 'test_wrk_zed.md').exists()
      and (ROOT / 'docs' / 'test' / 'reversi' / 'lm' / 'test_hlp_zed.md').exists())

# ---------------------------------------------------------------- G tier (dedicated suite)
gd = lines_of('test/test_hlp_zed.py')
check('G1  test_hlp_zed.py is 156 lines', len(gd) == 156, f'{len(gd)}')
check('G2  no DB / no gate / no tmp wiring: no logistic_model import, no SKIP_REGAB_DB, no paths import, no import os',
      all(k not in '\n'.join(gd) for k in ('from reversi.lm.logistic_model', 'SKIP_REGAB_DB',
                                           'test.reversi.paths', 'import os')))
check('G3  3 classes (L58/89/118): TestZedFunFactory + TestHlpZedCompute + TestLMZed',
      gd[57] == 'class TestZedFunFactory(unittest.TestCase):'
      and gd[88] == 'class TestHlpZedCompute(unittest.TestCase):'
      and gd[117] == 'class TestLMZed(unittest.TestCase):')
check('G4  factory goldens: alpha 0.02 literal [0.02, 0.5, 0.545, 0.98] + round-trip + 2-clipplings endpoints',
      'expected = np.array([0.02, 0.5, 0.545, 0.98], dtype=np.float32)' in '\n'.join(gd)
      and 'def test_round_trip' in '\n'.join(gd)
      and 'def test_endpoints_for_two_clipplings' in '\n'.join(gd)
      and '(0.02, 0.02, 0.98), (0.03, 0.03, 0.97)' in '\n'.join(gd))
check('G5  mock compute: SimpleNamespace ctx + (4,) exact golden [0.5734375, 0.764375, 0.3384375, 0.646875]',
      'SimpleNamespace' in '\n'.join(gd)
      and 'expected = np.array([0.5734375, 0.764375, 0.3384375, 0.646875],' in '\n'.join(gd)
      and 'nptest.assert_array_equal(expected, zed.z)' in '\n'.join(gd))
check('G6  init: 2 ValidationError pins (not_an_array / not_callable) + stores-by-reference',
      'LMZed(y2z=y2z, z2y=z2y, z="not_an_array")' in '\n'.join(gd)
      and 'LMZed(y2z="not_callable", z2y=z2y,' in '\n'.join(gd)
      and 'def test_init_stores_by_reference' in '\n'.join(gd)
      and '\n'.join(gd).count('assertRaises(ValidationError)') == 2)
check('G7  hash golden: the rlm_01 (10,) literal pinned to 3d49fd5d...f365d9b2',
      "'3d49fd5d56ced2f7bb70e5c24c8100b3318a7e66e7c990de53ed2f16f365d9b2'" in '\n'.join(gd))
check('G8  header: no-DB claim ("no live regab DB required — the compute test")',
      'no live regab DB required' in '\n'.join(gd))
check('G9  T8 clean: 0 trailing-ws lines',
      {i + 1 for i, l in enumerate(gd) if l != l.rstrip()} == set())
check('G10 the 3 domain names imported (LMZed / hlp_zed_compute / zed_fun_factory)',
      'from reversi.lm.hlp_zed import (LMZed,' in '\n'.join(gd)
      and 'hlp_zed_compute,' in '\n'.join(gd)
      and 'zed_fun_factory)' in '\n'.join(gd))

# ---------------------------------------------------------------- report
n_fail = 0
for name, ok, detail in RESULTS:
    mark = 'ok  ' if ok else 'FAIL'
    if not ok:
        n_fail += 1
    print(f'[{mark}] {name}' + (f'  -- {detail}' if detail and not ok else ''))
print(f'\n{len(RESULTS)} checks, {n_fail} mismatches')
sys.exit(1 if n_fail else 0)
