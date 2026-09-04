# ARCHIVED — D-106 investigation one-off (session 27/28, the O1 orbit-invariance
# study and the D-104 O1 w_dense investigation), 2026-09-04. Purpose served:
# the O1 pattern and the D-105 w_dense fix are closed and pinned by the
# tests + the module probes; nothing permanent lives in this script.
# (archived at D-106 step 3, the notes/docs hygiene migration)
import os, sys, tempfile, hashlib, re, time
sys.path.insert(0, 'src')
from unittest.mock import patch
from io import StringIO
from pathlib import Path
import numpy as np
from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.binio import verify_sha3_256_sidecar
from twolm.model_weights import model_weights_read_file
from twolm.rlm_client import make_evaluation_function
from twolm.rlm_gradient import sigmoid

def masked_hash(text):
    t = re.sub(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "DATE", text)
    return hashlib.sha3_256(t.encode()).hexdigest()

t0 = time.time()
with patch('sys.stdout', new=StringIO()) as out:
    tmp = tempfile.mkdtemp(dir='./build/tmp')
    rlm = LogisticModel('src/twolm/test/data/rlm_03.json', verbosity=Verbosity.HIGH, base_dir_override=tmp)
    rlm.move_to_last()
    ctx = rlm.context
    logs = out.getvalue()
dt = time.time() - t0
print("run time: %.1f s" % dt)
print("== vld ==", {k: (repr(v) if isinstance(v, float) else v) for k, v in ctx.vld_metrics.items()})
print("== train ==", {k: (repr(v) if isinstance(v, float) else v) for k, v in ctx.train_metrics.items()})
print("== pop ==", ctx.training_pop_stats)
print("== opt ==", ctx.opt_info)
op = Path(ctx.cfg.base_dir) / ctx.cfg.output
print("== file ==", op.name, op.stat().st_size, "sidecar:", verify_sha3_256_sidecar(op), "hash:", hashlib.sha3_256(op.read_bytes()).hexdigest()[:16])
mw = model_weights_read_file(op, compressed=True)
print("== mw ==", mw.version, mw.ec, repr(mw.logit_clipping))
print("   tps:", mw.training_pop_stats)
print("   opt:", mw.opt_info)
print("   vld:", mw.vld_metrics)
print("   fs hash:", mw.feature_set.hash[:16], "orig:", ctx.feature_set.hash[:16])
print("   iwmap_off:", mw.iwmap_feature_offset.tolist(), mw.iwmap_feature_offset.dtype, "len:", len(mw.iwmap_feature_offset))
print("   w_dense:", mw.w_dense.shape, mw.w_dense.dtype, "hash:", hashlib.sha3_256(mw.w_dense.tobytes()).hexdigest()[:16])
print("   w_dense first4:", mw.w_dense[:4])
print("   orig w_dense hash:", hashlib.sha3_256(ctx.w_dense.tobytes()).hexdigest()[:16])
n = len(ctx.positions)
idxs = ctx.rlm_indexes.indexes
offs = np.repeat(ctx.iwmap_feature_offset[:-1], [f.n_instances for f in ctx.feature_set.features])
ok = 0
for i in (0, 5, 123, 555, 9999, n - 1):
    yef = make_evaluation_function(mw)(ctx.positions[i])
    z = sigmoid(np.sum(ctx.w_dense[offs + idxs[i]]))
    yin = float(ctx.z2y(np.array([z], dtype=np.float32))[0])
    ok += (yef == yin)
    print(f"  pos[{i}]: ef={yef!r} bit-equal={yef == yin}")
print("ef bit-equal:", ok, "of 6")
rep = ctx.cfg.base_dir / ctx.cfg.analytics.report_file_name
print("== file report hash (date-masked):", masked_hash(rep.read_text()))
for l in logs.splitlines():
    if 'Generalization Gap' in l or 'Loss (MSE/2)' in l or 'ANALYTICS REPORT' in l:
        print("   |", l.split(']')[-1].strip())
with patch('sys.stdout', new=StringIO()) as out2:
    rlm2 = LogisticModel('src/twolm/test/data/rlm_03.json', verbosity=Verbosity.HIGH, base_dir_override=tmp)
    rlm2.move_to_last()
op2 = Path(rlm2.context.cfg.base_dir) / rlm2.context.cfg.output
print("== 2nd instance identical:", hashlib.sha3_256(op2.read_bytes()).hexdigest()[:16] == hashlib.sha3_256(op.read_bytes()).hexdigest()[:16], "hits:", out2.getvalue().count("Cache successfully loaded and validated"))
