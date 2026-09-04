# ARCHIVED — D-106 investigation one-off (session 27/28, the O1 orbit-invariance
# study and the D-104 O1 w_dense investigation), 2026-09-04. Purpose served:
# the O1 pattern and the D-105 w_dense fix are closed and pinned by the
# tests + the module probes; nothing permanent lives in this script.
# (archived at D-106 step 3, the notes/docs hygiene migration)
import contextlib, io, tempfile
from pathlib import Path
import numpy as np
from twolm.logistic_model import LogisticModel
from twolm.state_machine import Verbosity
from twolm.test.paths import WORKSPACE_ROOT, CUSTOM_TMP_BASE

CUSTOM_TMP_BASE.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(dir=str(CUSTOM_TMP_BASE)) as tmp:
    tmp = Path(tmp)
    cfg = str(WORKSPACE_ROOT / "src" / "twolm" / "test" / "data" / "rlm_02.json")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        m = LogisticModel(cfg, verbosity=Verbosity.HIGH, base_dir_override=tmp)
        m.move_to_step("VALIDATE")
    ctx = m.context
    vld_indexes = ctx.feature_set.compute_indexes(ctx.vld_positions)
    off = ctx.iwmap_feature_offset
    inst = [f.n_instances for f in ctx.feature_set.features]
    cum = np.concatenate([[0], np.cumsum(inst)])
    tot_inst = 0; tot_unseen = 0
    rows_any = np.zeros(len(ctx.vld_positions), dtype=bool)
    for fid, f in enumerate(ctx.feature_set.features):
        cols = vld_indexes[:, cum[fid]:cum[fid + 1]]
        un = ctx.iwmap[cols + off[fid]] == -1
        tot_inst += un.size; tot_unseen += int(un.sum())
        rows_any |= un.any(axis=1)
        n_configs = f.n_configurations
        seen = int((ctx.iwmap[off[fid]:off[fid + 1]] >= 0).sum())
        print(f"{f.name} (fid {fid}): n_instances={inst[fid]} n_configs={n_configs} "
              f"seen_configs={seen} | vld instances={un.size} "
              f"unseen_orbit_instances={int(un.sum())} "
              f"vld_positions_with_unseen={int(un.any(axis=1).sum())}")
    print(f"TOTAL: instances={tot_inst} unseen={tot_unseen} "
          f"({100.0 * tot_unseen / tot_inst:.1f}%)")
    print(f"positions (of {len(ctx.vld_positions)}) with >=1 unseen-orbit instance: {int(rows_any.sum())}")
    print(f"w length: {len(ctx.w)}, w_dense length: {len(ctx.w_dense)}")
