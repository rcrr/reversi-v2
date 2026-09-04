# ARCHIVED — D-106 investigation one-off (session 27/28, the O1 orbit-invariance
# study and the D-104 O1 w_dense investigation), 2026-09-04. Purpose served:
# the O1 pattern and the D-105 w_dense fix are closed and pinned by the
# tests + the module probes; nothing permanent lives in this script.
# (archived at D-106 step 3, the notes/docs hygiene migration)
import os, sys, tempfile, hashlib
sys.path.insert(0, 'src')
from unittest.mock import patch
from io import StringIO
from pathlib import Path
import numpy as np
from twolm.state_machine import Verbosity
from twolm.logistic_model import LogisticModel
from twolm.model_weights import model_weights_read_file, MODEL_WEIGHTS_FILE_HEADER_STR
from twolm.rlm_client import make_evaluation_function
from twolm.rlm_gradient import sigmoid

with patch('sys.stdout', new=StringIO()) as out:
    tmp = tempfile.mkdtemp(dir='./build/tmp')
    rlm = LogisticModel('src/twolm/test/data/rlm_04.json', verbosity=Verbosity.HIGH, base_dir_override=tmp)
    rlm.move_to_last()
    ctx = rlm.context
op = Path(ctx.cfg.base_dir) / ctx.cfg.output
mw = model_weights_read_file(op, compressed=True)
ef = make_evaluation_function(mw)
n = len(ctx.positions)
print("n train:", n, "n vld:", len(ctx.vld_positions))
idxs = ctx.rlm_indexes.indexes
offs = np.repeat(ctx.iwmap_feature_offset[:-1], [f.n_instances for f in ctx.feature_set.features])
zok = 0
for i in (0, 1, 7, 123, 999, n - 1):
    yef = ef(ctx.positions[i])
    z = sigmoid(np.sum(ctx.w_dense[offs + idxs[i]]))
    yin = float(ctx.z2y(np.array([z], dtype=np.float32))[0])
    zok += (yef == yin)
    print(f"  pos[{i}]: ef={yef!r} internal={yin!r} bit-equal={yef == yin}")
print("bit-equal count:", zok)
# vld position ef (unseen configs may be present)
yv = ef(ctx.vld_positions[42])
print("ef(vld[42]):", yv)
# error branches
import binio
bad = Path('./build/tmp') / 'badheader.dat'
with open(op, 'rb') as f:
    data = f.read()
# corrupt description: flip bytes in the first 40 bytes
import lz4.block
raw = lz4.block.decompress(data, uncompressed_size=len(data))
