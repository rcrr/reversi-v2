#!/usr/bin/env python3
#
# verify_zed.py — scratch probe (gitignored) for the ZED level, re-pinned
# to the POST-CAMPAIGN state (D-092: T1-T8 applied).
#
# Tiers:
#   A  rlm_zed.py structural pins (post T6/T7/T8)
#   B  lm_worker_zed.py structural pins (post T2/T8)
#   C  test_lm_worker_zed.py structural pins (post T1/T4/T5/T8)
#   D  live golden (rlm_01.json pipeline through ZED, independent recompute)
#   F  cross-module facts (logistic_model.py, repo state)
#   G  dedicated test_rlm_zed.py (post T3)
#
import contextlib
import hashlib
import io
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'src' / 'twolm'

RESULTS = []

def check(name, cond, detail=''):
    RESULTS.append((name, bool(cond), detail))
    return cond

def lines_of(relpath):
    return (SRC / relpath).read_text().splitlines()

# ---------------------------------------------------------------- A tier
rlm = lines_of('rlm_zed.py')
check('A1  rlm_zed.py is 103 lines (post T6 note + T7 decorator)', len(rlm) == 103, f'{len(rlm)}')
check('A2  __all__ = class + compute + factory (L42-44)',
      rlm[41] == "__all__ = ['ReversiLogisticModelZed',"
      and rlm[42] == "           'rlm_zed_compute',"
      and rlm[43] == "           'zed_fun_factory']")
check('A3  class ReversiLogisticModelZed at L48', rlm[47].startswith('class ReversiLogisticModelZed'))
check('A4  __init__ @validate_call (L53-54) w/ arbitrary_types_allowed',
      rlm[52] == '    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))'
      and rlm[53] == '    def __init__(self,')
check('A5  compute_sha3_256_hash decorated (L62-63), hashes z.tobytes() only (L65)',
      rlm[61] == '    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))'
      and rlm[62] == '    def compute_sha3_256_hash(self) -> str:'
      and rlm[64] == '        hasher.update(self.z.tobytes())')
check('A6  T7 DONE: zed_fun_factory decorated (L70) + def (L71)',
      rlm[69] == '@validate_call(config=ConfigDict(arbitrary_types_allowed=True))'
      and rlm[70] == 'def zed_fun_factory(logit_clipping: float) -> Tuple[Callable[[npt.NDArray[np.int8]], npt.NDArray[np.float32]],')
check('A7  factory math pins: a=0.5 (L78), b=(1-2c)/128 (L79), a1 (L85), b1 (L86)',
      rlm[77] == '    a = np.float32(0.5)'
      and rlm[78] == '    b = np.float32((1. - 2. * logit_clipping) / 128.)'
      and rlm[84] == '    a1 = np.float32(-64. / (1. - 2. * logit_clipping))'
      and rlm[85] == '    b1 = np.float32(128. / (1. - 2. * logit_clipping))')
check('A8  T6 DONE: the no-validation note at L94 above rlm_zed_compute (L95)',
      rlm[93] == '#: Here validation is not possible, it brings in a convoluted issue with circular imports.'
      and rlm[94] == 'def rlm_zed_compute(ctx: "RLMContext") -> ReversiLogisticModelZed:'
      and sum(1 for l in rlm if 'Here validation is not possible' in l) == 1)
check('A9  compute body: alpha (L99), y = ctx.game_values (L101), z = y2z(y) (L102)',
      rlm[98] == '    alpha = ctx.cfg.stat_model.logit_clipping'
      and rlm[100] == '    y = ctx.game_values'
      and rlm[101] == '    z = y2z(y)')
check('A10 no cache API in rlm_zed (no store / load / is_cache_consistent)',
      not any(k in l for l in rlm for k in ('def rlm_zed_store', 'def rlm_zed_load', 'def rlm_zed_is_cache')))
check('A11 TYPE_CHECKING guard for RLMContext (L37-38)',
      rlm[36] == 'if TYPE_CHECKING:' and rlm[37] == '    from twolm.logistic_model import RLMContext')
check('A12 T8 DONE: trailing-ws lines = header only (6,11,16,21)',
      {i + 1 for i, l in enumerate(rlm) if l != l.rstrip()} == {6, 11, 16, 21})
# (A13/A14/A15 factory(0.02) golden + round-trip + endpoints deleted
#  at D-106 step 3, class c: test_rlm_zed.py::TestZedFunFactory pins
#  the same — test_factory_alpha_0.02_golden (the same literal),
#  test_round_trip, and the endpoints for TWO clippings (0.02 AND
#  0.03, a superset of the probe's))

# ---------------------------------------------------------------- B tier
wk = lines_of('lm_worker_zed.py')
check('B1  lm_worker_zed.py is 73 lines (post T2 +1 import +1 decorator)', len(wk) == 73, f'{len(wk)}')
check('B2  __all__ = ["lm_worker_zed"] (L42)', wk[41] == "__all__ = ['lm_worker_zed']")
check('B3  T2 DONE: pydantic import (L32) + factory decorated (L70) + def (L71)',
      wk[31] == 'from pydantic import validate_call, ConfigDict'
      and wk[69] == '@validate_call(config=ConfigDict(arbitrary_types_allowed=True))'
      and wk[70] == 'def lm_worker_zed() -> Worker:')
check('B4  no cache_manager import (by design: no disk caching, L49 comment)',
      'cache_manager' not in '\n'.join(wk)
      and 'ZED computation is very fast (vectorized math), so we compute it on the fly without disk caching.' in wk[48])
check('B5  _up sets ctx.y2z / z2y / z / zed_checksum (L53-56)',
      wk[52] == '    ctx.y2z = zed_obj.y2z' and wk[53] == '    ctx.z2y = zed_obj.z2y'
      and wk[54] == '    ctx.z = zed_obj.z' and wk[55] == '    ctx.zed_checksum = zed_checksum')
check('B6  _down clears ALL FOUR attributes to None (L64-67)',
      wk[63] == '    ctx.y2z = None' and wk[64] == '    ctx.z2y = None'
      and wk[65] == '    ctx.z = None' and wk[66] == '    ctx.zed_checksum = None')
check('B7  Worker name is "ZED" (L73)', wk[72] == '    return Worker("ZED", _up, _down)')
check('B8  T8 DONE: trailing-ws lines = header only (6,11,16,21)',
      {i + 1 for i, l in enumerate(wk) if l != l.rstrip()} == {6, 11, 16, 21})

# ---------------------------------------------------------------- C tier
tc = lines_of('test/test_lm_worker_zed.py')
check('C1  test_lm_worker_zed.py is 164 lines (post T1/T4/T5)', len(tc) == 164, f'{len(tc)}')
check('C2  2 classes: TestZedFunFactory (L62, 1 test) + TestLMWorkerZed (L78, 2 tests)',
      tc[61] == 'class TestZedFunFactory(unittest.TestCase):'
      and tc[77] == 'class TestLMWorkerZed(unittest.TestCase):'
      and sum(1 for l in tc if l.startswith('    def test_')) == 3)
check('C3  T1 DONE: import os (L45) + gate in setUp (L85) + paths import (L58)',
      tc[44] == 'import os'
      and tc[84] == "        if os.getenv('SKIP_REGAB_DB', '0') == '1':"
      and tc[57] == 'from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE'
      and 'self.skipTest(' in '\n'.join(tc))
check('C4  header CLAIMS the gate (L38-39) — the claim is NOW true (ties to C3)',
      'SKIP_REGAB_DB=1' in tc[37] and 'skips the DB-gated tests' in tc[38])
check('C5  T4 DONE: TemporaryDirectory FIRST (L94) under CUSTOM_TMP_BASE + tmp_dir = Path (L95) + WORKSPACE_ROOT json (L96)',
      tc[93] == '        self._tmp = tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE))'
      and tc[94] == '        self.tmp_dir = Path(self._tmp.name)'
      and tc[95] == '        self.json_config = str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_01.json")')
check('C6  T4 DONE: no dead imports — no shutil, Path is load-bearing (Path(self._tmp.name))',
      'import shutil' not in '\n'.join(tc) and tc[52] == 'from pathlib import Path'
      and '\n'.join(tc).count('Path(') == 1)
check('C7  step pins: DESIGN_MTR = 6 (L103-104), ZED = 7 (L126-127)',
      tc[102] == "        self.rlm.move_to_step('DESIGN_MTR')" and tc[103] == '        self.assertEqual(self.rlm.current_step, 6)'
      and tc[125] == "        self.rlm.move_to_step('ZED')" and tc[126] == '        self.assertEqual(self.rlm.current_step, 7)')
check('C8  goldens: logit_clipping 0.03 (L116), y (10,) int8 (L120), z (10,) float32 (L136-145)',
      tc[115] == '        expected_logit_clipping = 0.03'
      and tc[119] == '        expected_y = np.array([10, 36, -22, 18, -16, 14, -22, 20, 0, 2], dtype=np.int8)'
      and tc[135] == '        expected_z = np.array([0.5734375,'
      and tc[144] == '                               0.5146875], dtype=np.float32)')
check('C9  T5 DONE: test_down_clears_zed_attributes (L149) — move(6) (L154), step 6 (L155), DESIGN_MTR name (L156), 4 assertIsNone (L157-160)',
      tc[148] == '    def test_down_clears_zed_attributes(self):'
      and tc[153] == '        self.rlm.move_to_step(6)'
      and tc[154] == '        self.assertEqual(self.rlm.current_step, 6)'
      and tc[155] == "        self.assertEqual(self.rlm.current_worker_name, 'DESIGN_MTR')"
      and tc[156:160] == ['        self.assertIsNone(self.rlm.context.y2z)',
                          '        self.assertIsNone(self.rlm.context.z2y)',
                          '        self.assertIsNone(self.rlm.context.z)',
                          '        self.assertIsNone(self.rlm.context.zed_checksum)'])
check('C10 T8 DONE: trailing-ws lines = header only (6,11,16,21)',
      {i + 1 for i, l in enumerate(tc) if l != l.rstrip()} == {6, 11, 16, 21})

# ---------------------------------------------------------------- D tier (live)
sys.path.insert(0, str(ROOT / 'src'))
from twolm.logistic_model import LogisticModel  # noqa: E402
from reversi.tools.state_machine import Verbosity  # noqa: E402

CLIP = 0.03

tmp = tempfile.TemporaryDirectory(dir=str(ROOT / 'build' / 'tmp'))
try:
    base = Path(tmp.name)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rlm01 = LogisticModel(str(ROOT / 'src' / 'twolm' / 'test' / 'data' / 'rlm_01.json'),
                              verbosity=Verbosity.HIGH, base_dir_override=base)
        # (D1 c? resolves to a (KEEP): the test pins only the y2z +
        #  z pre-state; z2y / zed_checksum pre-state are probe-unique)
        check('D1  pre-state before the first ZED up: y2z/z2y/z/zed_checksum all None',
              rlm01.context.y2z is None and rlm01.context.z2y is None
              and rlm01.context.z is None and rlm01.context.zed_checksum is None)
        rlm01.move_to_step('ZED')
    # (D2 step 7 / name ZED deleted at D-106 step 3, class c:
    #  test_lm_worker_zed.py::test_compute_zed pins it)
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
        ['rlmwf_01_CONFIG.dat', 'rlmwf_01_CONFIG.dat.SHA3-256',
         'rlmwf_02_POSITIONS.dat', 'rlmwf_02_POSITIONS.dat.SHA3-256',
         'rlmwf_04_INDEXES.dat', 'rlmwf_04_INDEXES.dat.SHA3-256',
         'rlmwf_05_WMAPS.dat', 'rlmwf_05_WMAPS.dat.SHA3-256',
         'rlmwf_06_DESIGN_MTR.dat', 'rlmwf_06_DESIGN_MTR.dat.SHA3-256'])
    check('D11 NO rlmwf_07_ZED* file: no disk caching for ZED (by design)',
          files == expected_files, str(files))
    with contextlib.redirect_stdout(io.StringIO()):
        rlm01.move_to_step(6)
    # (D12 _down live (step 6, 4 attrs None) deleted at D-106 step
    #  3, class c: test_down_clears_zed_attributes pins exactly this
    #  scope — the 4 assertIsNone at L157-160)
finally:
    tmp.cleanup()

# ---------------------------------------------------------------- F tier (cross)
lm_lines = lines_of('logistic_model.py')
check('F1  RLMContext zed fields pre-declared (L129-132), untouched by the commit',
      lm_lines[128] == '    zed_checksum: str | None = None'
      and lm_lines[129] == '    y2z: Any = None'
      and lm_lines[130] == '    z2y: Any = None'
      and lm_lines[131] == '    z: Any = None')
# (F2/F3 pipeline-state pins moved to the hub verify_logistic_model.py
# V3c/V3d at D-106)
check('F4  T3 DONE: dedicated test_rlm_zed.py exists, 10 tests, no DB wiring',
      (SRC / 'test' / 'test_rlm_zed.py').exists()
      and sum(1 for l in lines_of('test/test_rlm_zed.py') if l.startswith('    def test_')) == 10
      and 'from twolm.logistic_model' not in '\n'.join(lines_of('test/test_rlm_zed.py')))
check('F5  D-007 mirror docs written for all 4 zed files (post-campaign state)',
      (ROOT / 'docs' / 'src' / 'twolm' / 'rlm_zed.md').exists()
      and (ROOT / 'docs' / 'src' / 'twolm' / 'lm_worker_zed.md').exists()
      and (ROOT / 'docs' / 'src' / 'twolm' / 'test' / 'test_lm_worker_zed.md').exists()
      and (ROOT / 'docs' / 'src' / 'twolm' / 'test' / 'test_rlm_zed.md').exists())

# ---------------------------------------------------------------- G tier (dedicated suite)
gd = lines_of('test/test_rlm_zed.py')
check('G1  test_rlm_zed.py is 157 lines', len(gd) == 157, f'{len(gd)}')
check('G2  no DB / no gate / no tmp wiring: no logistic_model import, no SKIP_REGAB_DB, no paths import, no import os',
      all(k not in '\n'.join(gd) for k in ('from twolm.logistic_model', 'SKIP_REGAB_DB',
                                           'twolm.test.paths', 'import os')))
check('G3  3 classes (L59/90/119): TestZedFunFactory + TestRLMZedCompute + TestReversiLogisticModelZed',
      gd[58] == 'class TestZedFunFactory(unittest.TestCase):'
      and gd[89] == 'class TestRLMZedCompute(unittest.TestCase):'
      and gd[118] == 'class TestReversiLogisticModelZed(unittest.TestCase):')
check('G4  factory goldens: alpha 0.02 literal [0.02, 0.5, 0.545, 0.98] + round-trip + 2-clippling endpoints',
      'expected = np.array([0.02, 0.5, 0.545, 0.98], dtype=np.float32)' in '\n'.join(gd)
      and 'def test_round_trip' in '\n'.join(gd)
      and 'def test_endpoints_for_two_clipplings' in '\n'.join(gd)
      and '(0.02, 0.02, 0.98), (0.03, 0.03, 0.97)' in '\n'.join(gd))
check('G5  mock compute: SimpleNamespace ctx + (4,) exact golden [0.5734375, 0.764375, 0.3384375, 0.646875]',
      'SimpleNamespace' in '\n'.join(gd)
      and 'expected = np.array([0.5734375, 0.764375, 0.3384375, 0.646875],' in '\n'.join(gd)
      and 'nptest.assert_array_equal(expected, zed.z)' in '\n'.join(gd))
check('G6  init: 2 ValidationError pins (not_an_array / not_callable) + stores-by-reference',
      'ReversiLogisticModelZed(y2z=y2z, z2y=z2y, z="not_an_array")' in '\n'.join(gd)
      and 'ReversiLogisticModelZed(y2z="not_callable", z2y=z2y,' in '\n'.join(gd)
      and 'def test_init_stores_by_reference' in '\n'.join(gd)
      and '\n'.join(gd).count('assertRaises(ValidationError)') == 2)
check('G7  hash golden: the rlm_01 (10,) literal pinned to 3d49fd5d...f365d9b2',
      "'3d49fd5d56ced2f7bb70e5c24c8100b3318a7e66e7c990de53ed2f16f365d9b2'" in '\n'.join(gd))
check('G8  header: no-DB claim ("no live regab DB required — the compute test")',
      'no live regab DB required' in '\n'.join(gd))
check('G9  T8 clean: trailing-ws lines = header only (6,11,16,21)',
      {i + 1 for i, l in enumerate(gd) if l != l.rstrip()} == {6, 11, 16, 21})
check('G10 the 3 domain names imported (ReversiLogisticModelZed / rlm_zed_compute / zed_fun_factory)',
      'from twolm.rlm_zed import (ReversiLogisticModelZed,' in '\n'.join(gd)
      and 'rlm_zed_compute,' in '\n'.join(gd)
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
