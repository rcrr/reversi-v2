#
# wrk_optimize.py
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

from typing import TYPE_CHECKING

from pydantic import validate_call, ConfigDict
from reversi.tools import binio
from reversi.tools.state_machine import Worker, Relevance
from reversi.tools.opt_lbfgs import lbfgs
from reversi.lm.hlp_optimize import (optimization_info_dict,
                                save_optimization_checkpoint,
                                load_optimization_checkpoint,
                                is_optimization_cache_consistent,
                                is_optimization_status_converged,
                                weights_compute_sha3_256_hash)

if TYPE_CHECKING:
    from twolm.logistic_model import RLMContext



__all__ = ['lm_worker_optimize']



def _up(ctx: "RLMContext") -> None:
    ctx.log_event(Relevance.INFO, "Starting OPTIMIZE worker...")

    opt_cfg = ctx.cfg.optimization
    checkpoint_path = ctx.cfg.base_dir / opt_cfg.checkpoint_file

    w_init = ctx.w
    initial_sl, initial_yl, initial_rho = None, None, None
    initial_iter = 0

    min_grad_value, _ = opt_cfg.min_grad

    # 1. Check for existing checkpoint
    cp = None
    if checkpoint_path.exists() and ctx.use_cache:
        try:
            cp = load_optimization_checkpoint(checkpoint_path)
        except (RuntimeError, binio.BinaryFormatError, OSError) as exc:
            # R2 (D-096): a checkpoint that cannot be parsed or verified
            # (e.g. truncated by a crash mid-save) must not kill the
            # worker: delete it and its sidecar, then start from scratch.
            ctx.log_event(Relevance.WARN, f"Checkpoint could not be loaded ({exc}). Deleting it and starting from scratch.")
            checkpoint_path.unlink(missing_ok=True)
            checkpoint_path.with_name(checkpoint_path.name + ".SHA3-256").unlink(missing_ok=True)

    if cp is not None:
        ctx.log_event(Relevance.INFO, "Checkpoint found, checking consistency ...")

        if not is_optimization_cache_consistent(ctx, cp):
            ctx.log_event(Relevance.WARN, "Checkpoint config mismatch. Starting from scratch.")

        elif is_optimization_status_converged(ctx, cp) or cp['iters'] >= ctx.cfg.optimization.max_iters:
            ctx.log_event(Relevance.INFO, f"Checkpoint: optimization already completed. ({cp['reason']}). Loading final weights.")
            ctx.log_event(Relevance.INFO, f"Iterations ({cp['iters']}/{cp['max_iters']}).")
            ctx.w = cp['w']
            w_checksum = weights_compute_sha3_256_hash(cp['w'])
            ctx.w_checksum = w_checksum
            ctx.log_event(Relevance.INFO, f"Weight vector checksum (w_checksum): {w_checksum}.")
            ctx.opt_info = optimization_info_dict(cp)
            return # Skip optimization entirely!

        elif cp['iters'] < ctx.cfg.optimization.max_iters:
            ctx.log_event(Relevance.INFO, f"Checkpoint found. Resuming optimization from iteration {cp['iters']}.")
            w_init = cp['w']
            initial_sl = cp['sl']
            initial_yl = cp['yl']
            initial_rho = cp['rho']
            initial_iter = cp['iters']
        # M2 (D-096): the old trailing else ("state is unrecognized") was
        # unreachable: iters is an int, so iters >= max_iters or
        # iters < max_iters always holds.

    # 2. Setup wrappers
    def logger_fn(msg: str):
        ctx.log_event(Relevance.INFO, msg)

    def save_fn(w, sl, yl, rho, k, f, g_norm):
        save_optimization_checkpoint(
            filepath=checkpoint_path,
            design_matrix_checksum=ctx.design_matrix_checksum,
            zed_checksum=ctx.zed_checksum,
            ridge_regularization=ctx.cfg.stat_model.ridge_regularization,
            min_grad_value=min_grad_value,
            max_iters=opt_cfg.max_iters,
            m=opt_cfg.m,
            converged=False,
            reason="INCOMPLETE",
            # M5 (D-096): completed-count semantics, as in the final save
            # (k is the 0-based index of the just-completed iteration).
            iters=k + 1,
            f=f,
            g_norm=g_norm,
            w=w,
            sl=sl,
            yl=yl,
            rho=rho
        )
        ctx.log_event(Relevance.DEBUG, f"Intermediate checkpoint saved at iteration {k}.")

    # 3. Run L-BFGS
    w_opt, info = lbfgs(
        fg=ctx.fg,
        x0=w_init,
        c1=opt_cfg.c1,
        c2=opt_cfg.c2,
        min_grad=opt_cfg.min_grad,
        min_p_fun_decrease=opt_cfg.min_p_fun_decrease,
        max_iters=opt_cfg.max_iters,
        m=opt_cfg.m,
        log_every_n=opt_cfg.log_every_n,
        logger=logger_fn,
        save_every_n=opt_cfg.save_every_n,
        save_fn=save_fn,
        initial_sl=initial_sl,
        initial_yl=initial_yl,
        initial_rho=initial_rho,
        initial_iter=initial_iter
    )

    # 4. Update context and save final checkpoint
    ctx.w = w_opt
    ctx.opt_info = optimization_info_dict(info)
    ctx.log_event(Relevance.INFO, f"Optimization finished. Reason: {info['reason']}. Final Loss: {info['f']:.8e}")
    w_checksum = weights_compute_sha3_256_hash(w_opt)
    ctx.w_checksum = w_checksum
    ctx.log_event(Relevance.INFO, f"Weight vector checksum (w_checksum): {w_checksum}.")

    save_optimization_checkpoint(
        filepath=checkpoint_path,
        design_matrix_checksum=ctx.design_matrix_checksum,
        zed_checksum=ctx.zed_checksum,
        ridge_regularization=ctx.cfg.stat_model.ridge_regularization,
        min_grad_value=min_grad_value,
        max_iters=opt_cfg.max_iters,
        m=opt_cfg.m,
        converged=info['converged'],
        reason=info['reason'],
        iters=info['iters'],
        f=info['f'],
        g_norm=info['g_norm'],
        w=info['w'],
        sl=info['sl'],
        yl=info['yl'],
        rho=info['rho']
    )

def _down(ctx: "RLMContext") -> None:
    ctx.log_event(Relevance.INFO, "Clearing optimization attributes...")
    ctx.fg = None
    # R4 (D-096): also clear the OPTIMIZE-owned artifacts. ctx.w is kept:
    # it is the (re-optimized) WMAPS weight vector, and the WMAPS cache
    # restores the zero-initialized value when that level recomputes.
    ctx.w_checksum = None
    ctx.opt_info = None

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def lm_worker_optimize() -> Worker:
    """Factory function that returns the OPTIMIZE worker instance."""
    return Worker("OPTIMIZE", _up, _down)
