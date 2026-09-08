#!/usr/bin/env python3
"""
verify_save.py — D-104 SAVE bring-in probe (post-campaign goldens).

Tiers:
  A: static hygiene (worker, model_weights, client, test file, fixtures)
  B: model_weights read guards (no DB)
  C: live rlm_04 full 15-level chain (DB)
  D: live rlm_03 full 15-level chain (DB; run only with LONG=1)

Run: .venv/bin/python scratch/verify_save.py [LONG]
"""
import os
import re
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'src'
sys.path.insert(0, str(SRC))
LONG = 'LONG' in sys.argv

FAILURES = []


def check(name, ok, detail=''):
    tag = 'PASS' if ok else 'FAIL'
    print(f"[{tag}] {name}" + (f"  {detail}" if detail and not ok else ''))
    if not ok:
        FAILURES.append(name)


def ws_lines(path):
    # Lines 1-26 are the canonical license header (identical in every repo
    # file); they are never touched by ws sweeps.
    body = Path(path).read_text().splitlines()[26:]
    out = []
    for i, line in enumerate(body, 27):
        if re.match(r'^[ \t]+$', line) or re.search(r'[ \t]$', line):
            out.append(i)
    return out


def tier_a():
    w = SRC / 'twolm' / 'wrk_save.py'
    wt = w.read_text()
    check('A1 worker: @validate_call factory (T1)',
          '@validate_call(config=ConfigDict(arbitrary_types_allowed=True))' in wt
          and 'from pydantic import validate_call, ConfigDict' in wt)
    check('A2 worker: no pathlib import (T2)', 'from pathlib import Path' not in wt)
    check('A3 worker: no ws lines (T4)', not ws_lines(w), str(ws_lines(w)))

    m = SRC / 'twolm' / 'model_weights.py'
    mt = m.read_text()
    check('A4 model_weights: no ws lines (T4)', not ws_lines(m), str(ws_lines(m)))
    check('A5 model_weights: header str/ver + __all__ 3',
          'MODEL_WEIGHTS_FILE_HEADER_STR = "RGLM_BINARY_WEIGHTS"' in mt
          and 'MODEL_WEIGHTS_FILE_HEADER_VER = 1' in mt
          and "'ModelWeights',\n           'model_weights_read_file',\n           'model_weights_write_file'" in mt)
    # dataclass field count
    ds = mt.split('class ModelWeights:', 1)[1].split('#: --- End', 1)[0]
    check('A6 model_weights: ModelWeights 10 fields',
          len([l for l in ds.splitlines() if re.match(r'^\s{4}\w+: ', l)]) == 10,
          str(len([l for l in ds.splitlines() if re.match(r'^\s{4}\w+: ', l)])))

    c = SRC / 'reversi' / 'lm' / 'client.py'
    ct = c.read_text()
    check('A7 client: no dead import (T2)', 'model_weights_read_file' not in ct)
    check('A8 client: __all__ (M1)', "__all__ = ['make_evaluation_function']" in ct)
    check('A9 client: no ws lines (T4)', not ws_lines(c), str(ws_lines(c)))

    t = SRC / 'twolm' / 'test' / 'test_lm_worker_full_chain.py'
    tt = t.read_text()
    check('A10 test: SKIP_REGAB_DB gate x2 (T5a)', tt.count("os.getenv('SKIP_REGAB_DB', '0') == '1'") == 2)
    check('A11 test: D-085 idiom (T5b)',
          'from reversi.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE' in tt
          and 'mkdtemp(dir=str(CUSTOM_TMP_BASE))' in tt
          and 'WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_04.json"' in tt
          and 'WORKSPACE_ROOT / "src" / "reversi" / "test" / "data" / "rlm_03.json"' in tt)
    check('A12 test: no stray #: ### (T5c)', '#: ###' not in tt)
    check('A13 test: no dead imports (T2)',
          'numpy.testing as nptest' not in tt and 'nptest.' not in tt)
    check('A14 test: no ws lines (T4)', not ws_lines(t), str(ws_lines(t)))

    f3 = (SRC / 'twolm' / 'test' / 'data' / 'rlm_03.json').read_text()
    f4 = (SRC / 'twolm' / 'test' / 'data' / 'rlm_04.json').read_text()
    check('A15 fixtures: output field + cuts (rlm_03 cut=1, rlm_04 cut=10)',
          '"output": "rglm_logistic_model_ec_20_TEST03.dat"' in f3
          and '"output": "rglm_logistic_model_ec_20_TEST04.dat"' in f4
          and '"frequency_cut_off": 1,' in f3 and '"frequency_cut_off": 10,' in f4)


def tier_b():
    # (B1/B2 read guards (wrong description / wrong version, the exact
    #  ValueError messages) deleted at D-106 step 3, class c:
    #  test_lm_worker_full_chain.py::TestModelWeightsReadGuards pins
    #  both with assertRaisesRegex on the same message strings)
    return None


def _chain(fixture, name_prefix):
    from unittest.mock import patch
    from io import StringIO
    from reversi.tools.state_machine import Verbosity
    from reversi.lm.logistic_model import LogisticModel
    with patch('sys.stdout', new=StringIO()) as out:
        tmp = tempfile.mkdtemp(dir=str(SRC.parent / 'build' / 'tmp'))
        rlm = LogisticModel(str(SRC / 'twolm' / 'test' / 'data' / fixture),
                            verbosity=Verbosity.HIGH, base_dir_override=tmp)
        rlm.move_to_last()
    return rlm, out.getvalue()


def tier_c():
    rlm, logs = _chain('rlm_04.json', 'C')
    ctx = rlm.context
    # (C1 step 14 SAVE, C2/C3/C3b/C4 the metric goldens, C6 file size +
    #  sha3 + sidecar, C7-C9 read-back, C10/C11 evaluation-function
    #  goldens, C12 console pins, C13 file-report masked hash, C14
    #  second-instance determinism deleted at D-106 step 3, class c:
    #  test_lm_worker_full_chain.py::TestFullChainA2030::
    #  test_full_worker_chain pins the same 7+7+4+4 metric values,
    #  the 21603-byte file + bcf8d918... hash + sidecar verify, the
    #  read-back values, the 6 ef training positions + vld[42], the
    #  5 report substrings + 2 log lines, the d44557a8... masked
    #  report hash, and test_second_instance_deterministic pins the
    #  byte-identical file + 6 cache hits.)
    opt = ctx.opt_info
    # (C5 split at D-106 step 3: the converged/reason/iters portion is
    #  c — the test pins those three — the f/g_norm floats on the LIVE
    #  ctx (pre-f32-roundtrip) stay as the a portion: the test pins
    #  f/g_norm only on the read-back mw.opt_info (f32).)
    check('C5 opt 5-key (a portion: the live f/g_norm floats)',
          float(opt['f']) == 0.00560641149058938
          and float(opt['g_norm']) == 4.3686068238457665e-05, str(opt))


def tier_d():
    if not LONG:
        check('D0 rlm_03 tier (run with LONG=1)', True, 'skipped (no LONG)')
        return
    # (D1-D10 deleted at D-106 step 3, class c: the LONG rlm_03 tier
    #  pins the same goldens as tier C — test_lm_worker_full_chain.py::
    #  TestFullChainA2050::test_full_worker_chain pins step 14, the
    #  vld/train/dense/pop metric sets, the opt info, the 515042-byte
    #  file + 3ad18058... hash + sidecar, the read-back subset, the
    #  5 console report substrings (title + the 4 table rows incl.
    #  Delta -0.00 — the classification's 'a' label for D8 is stale:
    #  the test pins them all at L350-354), the 57f9766b... masked
    #  file-report hash, and the 6 ef training positions. The whole
    #  rlm_03 chain run is retired with the checks.)
    pass


def main():
    tier_a()
    tier_b()
    tier_c()
    tier_d()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILURES: {FAILURES}")
        sys.exit(1)
    print('ALL CHECKS PASSED')


if __name__ == '__main__':
    main()
