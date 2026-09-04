# ARCHIVED — D-106 investigation one-off (session 27/28, the O1 orbit-invariance
# study and the D-104 O1 w_dense investigation), 2026-09-04. Purpose served:
# the O1 pattern and the D-105 w_dense fix are closed and pinned by the
# tests + the module probes; nothing permanent lives in this script.
# (archived at D-106 step 3, the notes/docs hygiene migration)
import sys, tempfile
sys.path.insert(0, 'src')
from unittest.mock import patch
from io import StringIO
import numpy as np
from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
import twolm.rlm_gradient as rg

def compare(fixture, label):
    with patch('sys.stdout', new=StringIO()) as out:
        tmp = tempfile.mkdtemp(dir='./build/tmp')
        rlm = LogisticModel(f'src/twolm/test/data/{fixture}', verbosity=Verbosity.HIGH, base_dir_override=tmp)
        rlm.move_to_last()
        ctx = rlm.context
    n = ctx.design_matrix.shape[0]
    lin_comp = np.sum(ctx.w[ctx.design_matrix].astype(np.float64), axis=1)
    idxs = ctx.rlm_indexes.indexes
    ni = [f.n_instances for f in ctx.feature_set.features]
    offs_row = np.repeat(ctx.iwmap_feature_offset[:-1], ni)
    w_idx = np.broadcast_to(offs_row.astype(np.int64), idxs.shape) + idxs.astype(np.int64)
    wd = ctx.w_dense[w_idx]
    lin_dense = np.sum(wd.astype(np.float64), axis=1)
    y_comp = ctx.z2y(rg.sigmoid(lin_comp))
    y_dense = ctx.z2y(rg.sigmoid(lin_dense))
    dlin = lin_comp != lin_dense
    dy = y_comp != y_dense
    print(f"== {label} ({fixture}): n_train={n} cut={ctx.cfg.stat_model.frequency_cut_off}")
    print(f"   lin bit-differ: {int(dlin.sum())}/{n}   y bit-differ: {int(dy.sum())}/{n}")
    if dlin.sum():
        p = int(np.argmax(dlin))
        cols = np.where(wd[p] != ctx.w[ctx.design_matrix[p]])[0]
        # cumulative instance -> feature mapping
        cum = np.concatenate([[0], np.cumsum(ni)])
        fids = [f for k, f in enumerate(ctx.feature_set.features) if cum[k] <= cols[0] < cum[k+1]]
        for j in cols[:4]:
            wci = int(ctx.design_matrix[p, j])
            fid, conf, freq = [int(x) for x in ctx.wmap[wci]]
            print(f"   pos[{p}] inst[{j}] fid={fid} conf={conf} freq={freq} w_comp={float(ctx.w[wci])!r} w_dense={float(wd[p, j])!r}")
        # wmap_fallback entries for that feature
        fb = ctx.wmap_fallback
        print(f"   wmap_fallback rows: {len(fb)}; sample: {fb[:3].tolist() if len(fb) else '-'}")
        print(f"   sample y: comp={float(y_comp[p])!r} dense={float(y_dense[p])!r}")
        rel = np.abs(y_dense - y_comp)
        print(f"   max |dy| = {float(rel.max())!r}  mean |dy| over differing = {float(rel[dy].mean())!r}")
    return ctx

compare('rlm_04.json', 'RLM04')
compare('rlm_01.json', 'RLM01')
