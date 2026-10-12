#
# hlp_optimize.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi
#
# Author Roberto Corradini mailto:rob_corradini@yahoo.it
# Copyright 2026 Roberto Corradini. All rights reserved.
#
# License
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA
# or visit the site <http://www.gnu.org/licenses/>.
#

from __future__ import annotations

import math
import hashlib
import numpy as np
import numpy.typing as npt

from pathlib import Path
from typing import List, Dict, Any, TYPE_CHECKING
from pydantic import validate_call, ConfigDict

from reversi.tools import binio
from reversi.tools.state_machine import Relevance

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['hlp_optimize_info_dict',
           'hlp_optimize_save_checkpoint',
           'hlp_optimize_load_checkpoint',
           'hlp_optimize_is_cache_consistent',
           'hlp_optimize_is_status_converged',
           'hlp_optimize_weights_compute_hash']



#: Unlike the other layers, where the cache—when present—is organized using a class and a data
#: object, the OPTIMIZE layer cache (called a checkpoint) consists of a dictionary.

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_optimize_save_checkpoint(filepath: Path,
                                 design_matrix_checksum: str,
                                 zed_checksum: str,
                                 ridge_regularization: float,
                                 min_grad_value: float,
                                 max_iters: int,
                                 m: int,
                                 converged: bool,
                                 reason: str,
                                 iters: int,
                                 f: float,
                                 g_norm: float,
                                 w: np.ndarray,
                                 sl: List[np.ndarray],
                                 yl: List[np.ndarray],
                                 rho: List[float],
                                 compressed: bool = True) -> None:
    """
    Save the L-BFGS state and metadata to a binary checkpoint file.

    LZ4 whole-file compression by default (as in model_weights).

    Args:
        filepath (Path): the destination checkpoint path.
        design_matrix_checksum (str): the design-matrix checksum of the run (gate 1 of the
            consistency check).
        zed_checksum (str): the z-array checksum of the run (gate 2 of the consistency check).
        ridge_regularization (float): the ridge coefficient (gate 3, stored as f32).
        min_grad_value (float): the min_grad stopping tolerance value (stored as f32).
        max_iters (int): the configured maximum iteration count.
        m (int): the L-BFGS history length.
        converged (bool): whether the run converged (stored as the i32 1/0).
        reason (str): the convergence reason string.
        iters (int): the number of completed iterations.
        f (float): the final objective value (stored as f32).
        g_norm (float): the final gradient norm (stored as f32).
        w (np.ndarray): the weight vector.
        sl (List[np.ndarray]): the L-BFGS displacement vectors (s).
        yl (List[np.ndarray]): the L-BFGS gradient-change vectors (y).
        rho (List[float]): the L-BFGS scaling factors (one per (s, y) pair).
        compressed (bool): True (the default) — the LZ4 whole-file compression.
    """
    # The file stores a single length prefix plus one (s, y, rho) triple per entry, so the three
    # history lists must have equal length (fail fast instead of a framing error at load).
    if not (len(sl) == len(yl) == len(rho)):
        raise ValueError("sl, yl and rho must have the same length "
                         "(the L-BFGS history is stored as (s, y, rho) triples)")
    with binio.BinaryWriter(filepath, compressed=compressed) as bw:
        bw.write_header("RGLM Optimization Checkpoint", 1)
        bw.write_string(design_matrix_checksum)
        bw.write_string(zed_checksum)
        bw.write_f32(ridge_regularization)
        bw.write_f32(min_grad_value)
        bw.write_i32(max_iters)
        bw.write_i32(m)
        bw.write_i32(1 if converged else 0)
        bw.write_string(reason)
        bw.write_i32(iters)
        bw.write_f32(f)
        bw.write_f32(g_norm)

        bw.write_i32(len(sl))
        bw.write_array(w)

        # Serialize the L-BFGS history vectors chronologically: zip() pairs each displacement vector
        # (s) with its corresponding gradient change (y) and scaling factor (rho) and writes them
        # sequentially into the binary file for a seamless warm start.
        for s, y, r in zip(sl, yl, rho):
            bw.write_array(s)
            bw.write_array(y)
            bw.write_f64(r)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_optimize_load_checkpoint(filepath: Path, compressed: bool = True) -> Dict[str, Any]:
    """
    Load the L-BFGS state from a binary checkpoint file.

    LZ4 whole-file compression by default (as in model_weights). Verifies the header (description
    and version) and the SHA3-256 sidecar before trusting any payload: the sidecar exists precisely
    for this.

    Args:
        filepath (Path): the checkpoint path.
        compressed (bool): True (the default) — the LZ4 whole-file compression.

    Returns:
        Dict[str, Any]: the checkpoint state (the 15 keys the worker consumes).
    """
    with binio.BinaryReader(filepath, compressed=compressed) as br:
        # Read header properly!
        description, version = br.read_header()
        if description != "RGLM Optimization Checkpoint":
            raise RuntimeError(f"The file is not a proper optimization checkpoint. Found: {description}")
        if version != 1:
            raise RuntimeError(f"Checkpoint version mismatch: found {version}, expected 1")

        if not binio.verify_sha3_256_sidecar(filepath):
            raise RuntimeError(
                f"Checkpoint checksum mismatch: {filepath} does not match its SHA3-256 sidecar")

        # Read the checksum from earlier steps
        design_matrix_checksum = br.read_string()
        zed_checksum = br.read_string()
        ridge_regularization = br.read_f32()
        min_grad_value = br.read_f32()

        # 2. Read the metadata
        max_iters = br.read_i32()
        m = br.read_i32()
        converged = bool(br.read_i32())
        reason = br.read_string()
        iters = br.read_i32()
        f = br.read_f32()
        g_norm = br.read_f32()

        # 3. Read the L-BFGS memory state
        len_mem = br.read_i32()
        w = br.read_array()

        sl, yl, rho = [], [], []
        for _ in range(len_mem):
            sl.append(br.read_array())
            yl.append(br.read_array())
            rho.append(br.read_f64())
    return {
        'design_matrix_checksum': design_matrix_checksum,
        'zed_checksum': zed_checksum,
        'ridge_regularization': ridge_regularization,
        'min_grad_value': min_grad_value,
        'max_iters': max_iters,
        'm': m,
        'converged': converged,
        'reason': reason,
        'iters': iters,
        'f': f,
        'g_norm': g_norm,
        'w': w,
        'sl': sl,
        'yl': yl,
        'rho': rho
    }


#: Here validation is not possible, it brings in a convoluted issue with circular imports.
def hlp_optimize_is_cache_consistent(ctx: "LMContext", checkpoint: Dict[str, Any]) -> bool:
    """
    Validate the checkpoint against the current configuration.

    The three gates are:
      - ctx.design_matrix_checksum
        It ensures that the game positions, feature set, frequency clipping are all
        unchanged. The actual JSON config and database extraction are consistent with
        the reloaded data from the checkpoint file cache.
      - ctx.zed_checksum
        It ensures that the game values and logit clipping are consistent as well.
      - ctx.cfg.stat_model.ridge_regularization
        The ridge coefficient is part of the objective function, so a change invalidates the checkpoint
        exactly like a zed checksum change does (a ridge change keeps the same behavior as a logit_clipping
        change — recompute from scratch).

    Args:
        ctx ("LMContext"): the live context (the two checksums + the ridge coefficient).
        checkpoint (Dict[str, Any]): the loaded checkpoint state.

    Returns:
        bool: True when all three gates pass (the checkpoint is reusable).
    """

    if ctx.design_matrix_checksum != checkpoint['design_matrix_checksum']:
        ctx.log_event(Relevance.WARN, "The definition of the Design Matrix has changed.")
        ctx.log_event(Relevance.WARN, f"ctx.design_matrix_checksum:           {ctx.design_matrix_checksum}.")
        ctx.log_event(Relevance.WARN, f"checkpoint['design_matrix_checksum']: {checkpoint['design_matrix_checksum']}.")
        return False

    if ctx.zed_checksum != checkpoint['zed_checksum']:
        ctx.log_event(Relevance.WARN, "The definition of the Z array has changed.")
        ctx.log_event(Relevance.WARN, f"ctx.zed_checksum:           {ctx.zed_checksum}.")
        ctx.log_event(Relevance.WARN, f"checkpoint['zed_checksum']: {checkpoint['zed_checksum']}.")
        return False

    if not math.isclose(ctx.cfg.stat_model.ridge_regularization,
                        checkpoint['ridge_regularization'], rel_tol=1e-5, abs_tol=1e-8):
        ctx.log_event(Relevance.WARN, "The ridge regularization parameter has changed.")
        ctx.log_event(Relevance.WARN,
                      f"ctx.cfg.stat_model.ridge_regularization: {ctx.cfg.stat_model.ridge_regularization:.4e}.")
        ctx.log_event(Relevance.WARN, f"checkpoint['ridge_regularization']: {checkpoint['ridge_regularization']:.4e}.")
        return False

    ctx.log_event(Relevance.INFO,
                  "The definition of the Design Matrix, the Z array and the ridge regularization are unchanged.")
    return True


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_optimize_info_dict(lbfgs_info: dict) -> dict:
    """
    Filter the unused entries given by the lbfgs function.

    Keeps the ones saved into the logistic_model context.

    Args:
        lbfgs_info (dict): the full info dict returned by the lbfgs run.

    Returns:
        dict: the 5 context keys (converged, reason, iters, f, g_norm).
    """
    info = {
        'converged': lbfgs_info['converged'],
        'reason':    lbfgs_info['reason'],
        'iters':     lbfgs_info['iters'],
        'f':         lbfgs_info['f'],
        'g_norm':    lbfgs_info['g_norm']
    }
    return info


#: Here validation is not possible, it brings in a convoluted issue with circular imports.
def hlp_optimize_is_status_converged(ctx: "LMContext", checkpoint: Dict[str, Any]) -> bool:
    """
    Validate the checkpoint convergence status against the current stopping tolerance. The
    configuration consistency (design matrix, z array and ridge gates) is checked by
    hlp_optimize_is_cache_consistent before this function is reached, so here only the stored
    gradient norm is compared with the CURRENT min_grad tolerance: the tolerance is a judgement
    criterion, not part of the objective, so a changed tolerance re-judges the stored state (a
    looser tolerance may accept a not-converged checkpoint, a stricter one forces further iterations).

    Args:
        ctx ("LMContext"): the live context (the current min_grad tolerance).
        checkpoint (Dict[str, Any]): the loaded checkpoint state.

    Returns:
        bool: True when the stored gradient norm is below the current tolerance.
    """
    min_grad = ctx.cfg.optimization.min_grad
    ctx.log_event(Relevance.TRACE, f"Parameter ctx.cfg.optimization.min_grad = ({min_grad[0]:.4e}, {min_grad[1]})")
    min_grad_value, _ = min_grad

    cp_min_grad_value = checkpoint['min_grad_value']
    ctx.log_event(Relevance.TRACE, f"Parameter checkpoint['min_grad_value'] = {cp_min_grad_value:.4e}")

    cp_g_norm = checkpoint['g_norm']
    ctx.log_event(Relevance.TRACE, f"Parameter checkpoint['g_norm'] = {cp_g_norm:.4e}")

    if cp_g_norm < min_grad_value:
        ctx.log_event(Relevance.INFO, "Obtained gradient norm is lower than required, convergence is reached.")
        return True
    else:
        ctx.log_event(Relevance.INFO, "Obtained gradient norm is greater than required, convergence is not reached.")
        return False


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def hlp_optimize_weights_compute_hash(w: npt.NDArray[np.float32]) -> str:
    """
    Compute the SHA3-256 hash of the raw bytes of the weight vector.

    Returns:
        str: the 64-char hex digest.
    """
    hasher = hashlib.sha3_256()
    hasher.update(w.tobytes())
    sha3_256_hash = hasher.hexdigest()
    return sha3_256_hash
