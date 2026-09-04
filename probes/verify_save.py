#!/usr/bin/env python3
"""
verify_save.py — D-104 SAVE bring-in probe (post-campaign goldens).

Tiers:
  A: static hygiene (worker, model_weights, rlm_client, test file, fixtures)
  B: model_weights read guards (no DB)
  C: live rlm_04 full 15-level chain (DB)
  D: live rlm_03 full 15-level chain (DB; run only with LONG=1)

Run: .venv/bin/python scratch/verify_save.py [LONG]
"""
import os
import re
import sys
import time
import tempfile
import hashlib
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
    w = SRC / 'twolm' / 'lm_worker_save.py'
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

    c = SRC / 'twolm' / 'rlm_client.py'
    ct = c.read_text()
    check('A7 rlm_client: no dead import (T2)', 'model_weights_read_file' not in ct)
    check('A8 rlm_client: __all__ (M1)', "__all__ = ['make_evaluation_function']" in ct)
    check('A9 rlm_client: no ws lines (T4)', not ws_lines(c), str(ws_lines(c)))

    t = SRC / 'twolm' / 'test' / 'test_lm_worker_full_chain.py'
    tt = t.read_text()
    check('A10 test: SKIP_REGAB_DB gate x2 (T5a)', tt.count("os.getenv('SKIP_REGAB_DB', '0') == '1'") == 2)
    check('A11 test: D-085 idiom (T5b)',
          'from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE' in tt
          and 'mkdtemp(dir=str(CUSTOM_TMP_BASE))' in tt
          and 'WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_04.json"' in tt
          and 'WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_03.json"' in tt)
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
    from twolm.binio import BinaryWriter
    from twolm.model_weights import model_weights_read_file, MODEL_WEIGHTS_FILE_HEADER_STR
    tmp = Path(tempfile.mkdtemp(dir=str(SRC.parent / 'build' / 'tmp')))
    p = tmp / 'd.dat'
    with BinaryWriter(p, compressed=False) as w:
        w.write_header('WRONG_DESC', version=1)
        w.write_string('x')
    try:
        model_weights_read_file(p, compressed=False)
        check('B1 read guard: wrong description', False, 'no raise')
    except ValueError as e:
        check('B1 read guard: wrong description',
              str(e) == "File header mismatch, expected 'RGLM_BINARY_WEIGHTS', found 'WRONG_DESC'.", str(e))
    p2 = tmp / 'v.dat'
    with BinaryWriter(p2, compressed=False) as w:
        w.write_header(MODEL_WEIGHTS_FILE_HEADER_STR, version=99)
        w.write_string('x')
    try:
        model_weights_read_file(p2, compressed=False)
        check('B2 read guard: wrong version', False, 'no raise')
    except ValueError as e:
        check('B2 read guard: wrong version',
              str(e) == "File header version, expected '1', found '99'.", str(e))


def _chain(fixture, name_prefix):
    from unittest.mock import patch
    from io import StringIO
    from twolm.state_machine import Verbosity
    from twolm.logistic_model import LogisticModel
    with patch('sys.stdout', new=StringIO()) as out:
        tmp = tempfile.mkdtemp(dir=str(SRC.parent / 'build' / 'tmp'))
        rlm = LogisticModel(str(SRC / 'twolm' / 'test' / 'data' / fixture),
                            verbosity=Verbosity.HIGH, base_dir_override=tmp)
        rlm.move_to_last()
    return rlm, out.getvalue()


def tier_c():
    import numpy as np
    rlm, logs = _chain('rlm_04.json', 'C')
    ctx = rlm.context
    check('C1 15 levels: step 14 SAVE',
          rlm.current_step == 14 and rlm.current_worker_name == 'SAVE',
          f"{rlm.current_step} {rlm.current_worker_name}")
    vld = ctx.vld_metrics
    check('C2 vld 7 exact',
          vld == {'vld_loss': 0.00575742032378912, 'vld_mse_z': 0.01151484064757824,
                  'vld_mae_z': 0.0845922976732254, 'vld_mae_y': 11.048789978027344,
                  'vld_mse_y': 196.43809509277344, 'vld_rmse_y': 14.015637397766113,
                  'vld_samples': 20000}, str(vld))
    trn = ctx.train_metrics
    check('C3 train 7 exact',
          trn == {'train_mae_y': 10.899353761577668, 'train_rmse_y': 13.822995683195872,
                  'train_loss': 0.00560641149058938, 'train_samples': 199932,
                  'pop_mae_y': 21.73034518830014, 'pop_rmse_y': 26.406980394267364,
                  'pop_loss': 0.020438173785805702}, str(trn))
    td = ctx.train_dense_metrics
    check('C3b train_dense 4 exact (D-105/M2 — the w_dense pass; rlm_04 cut 10, '
          '1923 training positions touch IC configs)',
          td == {'train_dense_mae_y': 10.905119078281873,
                 'train_dense_rmse_y': 13.831248070093375,
                 'train_dense_loss': 0.0056069279089570045,
                 'train_dense_samples': 199932}, str(td))
    pop = ctx.training_pop_stats
    check('C4 pop 4 exact',
          pop == {'count': 199932, 'mean': -1.3912930396334753,
                  'std_dev': 26.40698039426738, 'variance': 697.3286135432216}, str(pop))
    opt = ctx.opt_info
    check('C5 opt 5-key',
          opt['converged'] is True and opt['reason'] == 'CONVERGED_MIN_GRAD'
          and opt['iters'] == 67 and float(opt['f']) == 0.00560641149058938
          and float(opt['g_norm']) == 4.3686068238457665e-05, str(opt))

    op = ctx.cfg.base_dir / ctx.cfg.output
    check('C6 file 21603 B + sha3 + sidecar',
          op.stat().st_size == 21603
          and hashlib.sha3_256(op.read_bytes()).hexdigest()
          == 'bcf8d918979aaddba52ed2c9a80571f4fdc939a985ff4f3705510fa4f8010abb'
          and __import__('twolm.binio', fromlist=['verify_sha3_256_sidecar']).verify_sha3_256_sidecar(op))

    from twolm.model_weights import model_weights_read_file
    mw = model_weights_read_file(op, compressed=True)
    check('C7 read-back metadata',
          mw.version == 1 and mw.name == ctx.cfg.name and mw.ec == 20
          and float(mw.logit_clipping) == float(np.float32(0.01)),
          f"{mw.version} {mw.name} {mw.ec} {mw.logit_clipping}")
    check('C8 read-back tps/opt/vld f32',
          mw.training_pop_stats['count'] == np.uint64(199932)
          and float(mw.training_pop_stats['mean']) == -1.3912930488586426
          and float(mw.training_pop_stats['std_dev']) == 26.406980514526367
          and float(mw.training_pop_stats['variance']) == 697.32861328125
          and mw.opt_info['reason'] == 'CONVERGED_MIN_GRAD'
          and mw.opt_info['iters'] == np.uint32(67)
          and float(mw.opt_info['f']) == 0.00560641149058938
          and float(mw.opt_info['g_norm']) == 4.3686068238457665e-05
          and mw.vld_metrics['vld_samples'] == np.uint32(20000)
          and float(mw.vld_metrics['vld_rmse_y']) == 14.015637397766113
          and float(mw.vld_metrics['vld_mae_y']) == 11.048789978027344
          and float(mw.vld_metrics['vld_loss']) == 0.00575742032378912)
    check('C9 read-back fs hash + iwmap + w_dense',
          mw.feature_set.hash == 'ec4f15374a00b729629d62ee0eb4354cbf163950672b7a9db9f81375e40559ef'
          and np.array_equal(mw.iwmap_feature_offset, np.array([0, 1, 66, 6627], dtype=np.uint32))
          and mw.w_dense.shape == (6627,) and mw.w_dense.dtype == np.float32
          and hashlib.sha3_256(mw.w_dense.tobytes()).hexdigest()
          == '7ecdeba66d9f34b9396e199dd4a5933196131db497ff88fce726bcd75f1f4f37'
          and np.array_equal(mw.w_dense, ctx.w_dense),
          f"{mw.feature_set.hash[:16]} {mw.iwmap_feature_offset.tolist()} {mw.w_dense.shape}")

    from twolm.rlm_client import make_evaluation_function
    ef = make_evaluation_function(mw)
    expected_ef = {0: -37.12018585205078, 1: -28.228458404541016, 7: 45.391082763671875,
                   123: 40.502410888671875, 999: 16.26209259033203,
                   len(ctx.positions) - 1: 23.326324462890625}
    check('C10 ef 6 training positions bit-exact',
          all(ef(ctx.positions[i]) == y for i, y in expected_ef.items()))
    check('C11 ef vld[42] (substitution path) bit-exact',
          ef(ctx.vld_positions[42]) == 11.932792663574219,
          repr(ef(ctx.vld_positions[42])))

    check('C12 console pins',
          'MODEL ANALYTICS REPORT: RGLM (Logistic) - Short-Long Test 04 (rlm_04.json)' in ctx.analytics_report
          and 'Loss (MSE/2)    | 5.6064e-03     | 5.6069e-03     | 5.7574e-03' in ctx.analytics_report
          and 'Population (baseline)  : RMSE 26.41  MAE 21.73  Loss 2.0438e-02' in ctx.analytics_report
          and 'Generalization Gap (RMSE)   : 0.18' in ctx.analytics_report
          and 'Substitution Delta (RMSE)   : 0.01' in ctx.analytics_report
          and 'Validation completed. Loss (MSE/2): 5.75742032e-03' in logs
          and 'Saving model weights to disk...' in logs)

    rep = (ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name).read_text()
    masked = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", 'DATE', rep)
    check('C13 file report masked hash + detail sections',
          hashlib.sha3_256(masked.encode()).hexdigest()
          == 'd44557a8efd007f4634c2949a0cf9eca60d7b38f790c2bbd1e058245a4045a2e'
          and 'PATTERN FEATURE: EDGE (fid=2)' in rep
          and 'MOBILITY FEATURE: LMC (fid=1)' in rep
          and 'Creation Date               :' in rep)

    from unittest.mock import patch as _p
    from io import StringIO as _S
    from twolm.logistic_model import LogisticModel as LM
    from twolm.state_machine import Verbosity
    with _p('sys.stdout', new=_S()) as out2:
        rlm2 = LM(str(SRC / 'twolm' / 'test' / 'data' / 'rlm_04.json'),
                  verbosity=Verbosity.HIGH, base_dir_override=ctx.cfg.base_dir)
        rlm2.move_to_last()
    logs2 = out2.getvalue()
    op2 = ctx.cfg.base_dir / ctx.cfg.output
    check('C14 2nd instance byte-identical + 6 cache hits',
          hashlib.sha3_256(op2.read_bytes()).hexdigest()
          == 'bcf8d918979aaddba52ed2c9a80571f4fdc939a985ff4f3705510fa4f8010abb'
          and logs2.count('Cache successfully loaded and validated') == 6
          and 'Extracted' not in logs2
          and 'established successfully' not in logs2,
          f"hits={logs2.count('Cache successfully loaded and validated')}")


def tier_d():
    if not LONG:
        check('D0 rlm_03 tier (run with LONG=1)', True, 'skipped (no LONG)')
        return
    import numpy as np
    t0 = time.time()
    rlm, logs = _chain('rlm_03.json', 'D')
    ctx = rlm.context
    print(f"   (rlm_03 chain: {time.time() - t0:.0f} s)")
    check('D1 15 levels: step 14 SAVE',
          rlm.current_step == 14 and rlm.current_worker_name == 'SAVE')
    vld = ctx.vld_metrics
    check('D2 vld 7 exact',
          vld == {'vld_loss': 0.001578879076987505, 'vld_mse_z': 0.00315775815397501,
                  'vld_mae_z': 0.04321568086743355, 'vld_mae_y': 5.644496440887451,
                  'vld_mse_y': 53.86997604370117, 'vld_rmse_y': 7.339616775512695,
                  'vld_samples': 199932}, str(vld))
    trn = ctx.train_metrics
    check('D3 train 7 exact',
          trn == {'train_mae_y': 5.396253447071691, 'train_rmse_y': 7.015377800787937,
                  'train_loss': 0.001444403431378305, 'train_samples': 1999179,
                  'pop_mae_y': 21.758215006979484, 'pop_rmse_y': 26.417003454424307,
                  'pop_loss': 0.020453333854675293}, str(trn))
    td = ctx.train_dense_metrics
    check('D3b train_dense 4 exact (D-105/M2 — rlm_03 cut 1: dense == compressed '
          'up to f32 rounding of w_dense, Substitution Delta "-0.00")',
          td == {'train_dense_mae_y': 5.396253444189108,
                 'train_dense_rmse_y': 7.015377798958687,
                 'train_dense_loss': 0.0014424461405724287,
                 'train_dense_samples': 1999179}, str(td))
    pop = ctx.training_pop_stats
    check('D4 pop 4 exact',
          pop == {'count': 1999179, 'mean': -1.3259453005458741,
                  'std_dev': 26.417003454424318, 'variance': 697.8580715110664}, str(pop))
    opt = ctx.opt_info
    check('D5 opt 5-key',
          opt['converged'] is True and opt['reason'] == 'CONVERGED_MIN_GRAD'
          and opt['iters'] == 397 and float(opt['f']) == 0.001444403431378305
          and float(opt['g_norm']) == 7.43771579436725e-06, str(opt))
    op = ctx.cfg.base_dir / ctx.cfg.output
    from twolm.binio import verify_sha3_256_sidecar
    from twolm.model_weights import model_weights_read_file
    check('D6 file 515042 B + sha3 + sidecar',
          op.stat().st_size == 515042
          and hashlib.sha3_256(op.read_bytes()).hexdigest()
          == '3ad1805815c536e4506b0804b5be9e8662de53402c37fc3268c8dbbbb6847ff4'
          and verify_sha3_256_sidecar(op))
    mw = model_weights_read_file(op, compressed=True)
    check('D7 read-back f32 subsets + fs + arrays',
          mw.feature_set.hash == '2c8bb32b40eff2c1e22b992e56b8d60fb51c17afb81d48f9414aef46c349e43d'
          and np.array_equal(mw.iwmap_feature_offset, np.array(
              [0, 1, 66, 59115, 118164, 124725, 144408, 150969, 151050,
               157611, 157854, 158583, 160770, 167331], dtype=np.uint32))
          and mw.w_dense.shape == (167331,) and mw.w_dense.dtype == np.float32
          and hashlib.sha3_256(mw.w_dense.tobytes()).hexdigest()
          == 'a012689f70ef8a492ce0fbf374a49e79e62f758a83fce94540a459bd28b527fc'
          and float(mw.training_pop_stats['mean']) == -1.325945258140564
          and float(mw.opt_info['f']) == 0.001444403431378305
          and float(mw.vld_metrics['vld_loss']) == 0.001578879076987505)
    check('D8 console pins + file report hash',
          'MODEL ANALYTICS REPORT: RGLM (Logistic) - Long Test 03 (rlm_03.json)' in ctx.analytics_report
          and 'Loss (MSE/2)    | 1.4444e-03     | 1.4424e-03     | 1.5789e-03' in ctx.analytics_report
          and 'Population (baseline)  : RMSE 26.42  MAE 21.76  Loss 2.0453e-02' in ctx.analytics_report
          and 'Generalization Gap (RMSE)   : 0.32' in ctx.analytics_report
          and 'Substitution Delta (RMSE)   : -0.00' in ctx.analytics_report,
          'console')
    rep = (ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name).read_text()
    masked = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", 'DATE', rep)
    check('D9 file report masked hash + XEDGE detail',
          hashlib.sha3_256(masked.encode()).hexdigest()
          == '57f9766b7e5115903319f3387b192e490c71674eebc2e2c199040579b5fad83a'
          and 'PATTERN FEATURE: XEDGE' in rep
          and 'Creation Date               :' in rep)
    from twolm.rlm_client import make_evaluation_function
    ef = make_evaluation_function(mw)
    expected_ef = {0: 7.2613525390625, 5: -32.98143768310547, 123: 40.5123291015625,
                   555: 24.14972686767578, 9999: -19.389434814453125,
                   len(ctx.positions) - 1: 57.8465576171875}
    check('D10 ef 6 training positions bit-exact',
          all(ef(ctx.positions[i]) == y for i, y in expected_ef.items()))


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
