# ARCHIVED — D-106 investigation one-off (session 27/28, the O1 orbit-invariance
# study and the D-104 O1 w_dense investigation), 2026-09-04. Purpose served:
# the O1 pattern and the D-105 w_dense fix are closed and pinned by the
# tests + the module probes; nothing permanent lives in this script.
# (archived at D-106 step 3, the notes/docs hygiene migration)
import os, sys, tempfile, hashlib, re
os.environ.setdefault('SKIP_REGAB_DB', '0')
sys.path.insert(0, 'src')
from unittest.mock import patch
from io import StringIO
from pathlib import Path
from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.binio import verify_sha3_256_sidecar
from twolm.model_weights import model_weights_read_file
from twolm.rlm_client import make_evaluation_function
import numpy as np

with patch('sys.stdout', new=StringIO()) as out:
    tmp = tempfile.mkdtemp(dir='./build/tmp')
    rlm = LogisticModel('src/twolm/test/data/rlm_04.json', verbosity=Verbosity.HIGH, base_dir_override=tmp)
    rlm.move_to_last()
    ctx = rlm.context
    logs = out.getvalue()

print("== pipeline ==", rlm.current_step, rlm.current_worker_name)
print("== vld ==", {k: (repr(v) if isinstance(v, float) else v) for k, v in ctx.vld_metrics.items()})
print("== train ==", {k: (repr(v) if isinstance(v, float) else v) for k, v in ctx.train_metrics.items()})
print("== pop ==", {k: (repr(v) if isinstance(v, float) else v) for k, v in ctx.training_pop_stats.items()})
print("== opt ==", ctx.opt_info)
op = Path(ctx.cfg.base_dir) / ctx.cfg.output
print("== output ==", op.name, op.exists(), "sidecar:", verify_sha3_256_sidecar(op))
print("== file bytes ==", op.stat().st_size, "hash:", hashlib.sha3_256(op.read_bytes()).hexdigest()[:16])
print("== sidecar file ==", sorted(p.name for p in op.parent.iterdir()))
mw = model_weights_read_file(op, compressed=True)
print("== mw ==", mw.version, mw.name, mw.ec, repr(mw.logit_clipping))
print("   tps:", mw.training_pop_stats)
print("   opt:", mw.opt_info)
print("   vld:", mw.vld_metrics)
print("   fs hash:", mw.feature_set.hash[:16], "orig:", ctx.feature_set.hash[:16])
print("   iwmap_off:", mw.iwmap_feature_offset, mw.iwmap_feature_offset.dtype)
print("   w_dense:", mw.w_dense.shape, mw.w_dense.dtype, "hash:", hashlib.sha3_256(mw.w_dense.tobytes()).hexdigest()[:16])
print("   w_dense first8:", mw.w_dense[:8])
print("   w_dense[-4:]:", mw.w_dense[-4:])
print("   orig w_dense hash:", hashlib.sha3_256(ctx.w_dense.tobytes()).hexdigest()[:16])
# 2nd instance: byte-identical rewrite?
with patch('sys.stdout', new=StringIO()) as out2:
    rlm2 = LogisticModel('src/twolm/test/data/rlm_04.json', verbosity=Verbosity.HIGH, base_dir_override=tmp)
    rlm2.move_to_last()
    logs2 = out2.getvalue()
op2 = Path(rlm2.context.cfg.base_dir) / rlm2.context.cfg.output
h2 = hashlib.sha3_256(op2.read_bytes()).hexdigest()[:16]
print("== 2nd instance file hash:", h2, "identical:", h2 == hashlib.sha3_256(op.read_bytes()).hexdigest()[:16])
print("== cache hits inst2:", logs2.count("Cache successfully loaded and validated"))
print("== Extracted inst2:", logs2.count("Extracted"), " established:", logs2.count("established successfully"))
# SAVE log span
i0 = next(i for i, l in enumerate(logs.splitlines()) if "Saving model weights" in l)
i1 = next(i for i, l in enumerate(logs.splitlines()) if "Model weights saved" in l)
print("== SAVE span lines:", i1 - i0 + 1)
for l in logs.splitlines()[i0-1:i1+1]:
    print("   |", l[-90:])
# ef check on a vld position (not just training)
ef = make_evaluation_function(mw)
p = ctx.positions[123]
print("== ef(pos[123]):", ef(p))
y_int = ctx.z2y(np.array([ctx.z2y.__self__(p) if False else 0.0], dtype=np.float32)) if False else None
idxs = ctx.rlm_indexes.indexes[123]
offs = np.repeat(ctx.iwmap_feature_offset[:-1], [f.n_instances for f in ctx.feature_set.features])
wint = ctx.w_dense[offs + idxs]
print("   internal:", float(ctx.z2y(np.array([np.sum(wint)], dtype=np.float32)) * 0 + ctx.z2y(np.array([ (1/(1+np.exp(-np.sum(wint))) )], dtype=np.float32))[0]))
import twolm.rlm_gradient as rg
z = rg.sigmoid(np.sum(wint))
print("   internal z2y:", float(ctx.z2y(np.array([z], dtype=np.float32))[0]))
print("== analytics report head ==")
print(ctx.analytics_report[:400])
