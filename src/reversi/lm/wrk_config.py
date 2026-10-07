#
# wrk_config.py
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

import os
import json5
import hashlib

from typing import TYPE_CHECKING
from pathlib import Path

from pydantic import ConfigDict, validate_call

from reversi.tools.state_machine import Worker, Relevance
from reversi.lm.hlp_config_schemas import LMConfig

if TYPE_CHECKING:
    from reversi.lm.logistic_model import LMContext



__all__ = ['wrk_config']



def _up(ctx: "LMContext") -> None:
    """
    Run the CONFIG level: load + validate the LM JSON5 config, publish the model (ctx.cfg), the
    use_cache flag and the config fingerprint (the sha3_256 of the normalized dump) on the context.
    """
    ctx.log_event(Relevance.INFO, f"Loading configuration file '{ctx.config_file_path}' ...")
    cfg = _load(ctx)
    ctx.log_event(Relevance.INFO, f"Configuration file {ctx.config_file_path} loaded.")
    _validate(ctx, cfg)
    ctx.log_event(Relevance.INFO, f"Configuration file {ctx.config_file_path} validated.")
    ctx.log_event(Relevance.INFO, f"Model name: {cfg.name}")
    ctx.log_event(Relevance.INFO, f"Model description: {cfg.description}")
    ctx.log_event(Relevance.INFO, f"Model base_dir: {cfg.base_dir}")
    ctx.use_cache = cfg.use_cache
    ctx.cfg = cfg
    # The config fingerprint: the sha3_256 of the normalized dump (the effective configuration of
    # the run, the base_dir override included) — the single source of truth for the SAVE config
    # record and the analytics report.
    ctx.config_checksum = hashlib.sha3_256(
        cfg.model_dump_json(indent=4).encode()).hexdigest()
    ctx.log_event(Relevance.INFO,
                  f"Configuration fingerprint (sha3_256): {ctx.config_checksum}")


def _down(ctx: "LMContext") -> None:
    """Clear the three context attributes the CONFIG level publishes."""
    ctx.log_event(Relevance.INFO, "Clearing configuration...")
    ctx.cfg = None
    ctx.use_cache = None
    ctx.config_checksum = None


def _load(ctx: "LMContext") -> LMConfig:
    """
    Load the config file (json5, UTF-8), apply the optional base_dir override to the raw dict, and
    return the domain model.
    """
    with ctx.config_file_path.open("r", encoding="utf-8") as f:
        config_raw_data = json5.load(f)
        ctx.log_event(Relevance.DEBUG, f"JSON file '{ctx.config_file_path}' read.")

    if ctx.base_dir_override is not None:
        config_raw_data['base_dir'] = ctx.base_dir_override
        ctx.log_event(Relevance.DEBUG, f"Value for base_dir changed to '{ctx.base_dir_override}'.")

    cfg = LMConfig(**config_raw_data)
    return cfg


def _validate(ctx: "LMContext", cfg: LMConfig) -> None:
    """Run the config gates (the base_dir checks, the precise OS exception types)."""
    _validate_base_dir(ctx, cfg)


def _validate_base_dir(ctx: "LMContext", cfg: LMConfig) -> None:
    """
    The three base_dir gates, each logged at ERROR before the raise: FileNotFoundError (doesn't
    exist), NotADirectoryError (is not a directory), PermissionError (is not writable).
    """
    if not cfg.base_dir.exists():
        error_message = f"The base dir: '{cfg.base_dir}' doesn't exist."
        ctx.log_event(Relevance.ERROR, error_message)
        raise FileNotFoundError(error_message)
    if not cfg.base_dir.is_dir():
        error_message = f"The base dir: '{cfg.base_dir}' is not a directory."
        ctx.log_event(Relevance.ERROR, error_message)
        raise NotADirectoryError(error_message)
    is_writable = os.access(cfg.base_dir, os.W_OK)
    if not is_writable:
        error_message = f"The base dir: '{cfg.base_dir}' is not writable."
        ctx.log_event(Relevance.ERROR, error_message)
        raise PermissionError(error_message)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def wrk_config() -> Worker:
    """Return the CONFIG worker instance."""
    return Worker("CONFIG", _up, _down)
