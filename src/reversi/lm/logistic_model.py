#
# logistic_model.py
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

import argparse

from dataclasses import dataclass
from pathlib import Path
from typing import List, Any, Callable

from pydantic import ConfigDict, validate_call

from reversi.tools.state_machine import StateMachine, Worker, Context, Verbosity, Relevance
from reversi.base_model import BaseModel

# Import worker factories
from reversi.lm.wrk_config import wrk_config
from reversi.lm.wrk_positions import wrk_positions
from reversi.lm.wrk_features import wrk_features
from reversi.lm.wrk_su_analysis import wrk_su_analysis
from reversi.lm.wrk_indexes import wrk_indexes
from reversi.lm.wrk_effect_size import wrk_effect_size
from reversi.lm.wrk_wmaps import wrk_wmaps
from reversi.lm.wrk_design_matrix import wrk_design_matrix
from reversi.lm.wrk_zed import wrk_zed
from reversi.lm.wrk_gradient import wrk_gradient
from reversi.lm.wrk_optimize import wrk_optimize
from reversi.lm.wrk_generate import wrk_generate
from reversi.lm.wrk_vld_positions import wrk_vld_positions
from reversi.lm.wrk_validate import wrk_validate
from reversi.lm.wrk_analytics import wrk_analytics
from reversi.lm.wrk_save import wrk_save
from reversi.lm.wrk_client_check import wrk_client_check
from reversi.lm.wrk_plot import wrk_plot



__all__ = ['LMContext', 'LogisticModel']



#
# Helper methods.
#

def _check_config_file_path(config_file_path: Path | str) -> Path:
    if not isinstance(config_file_path, (str, Path)):
        raise TypeError('Argument config_file_path is not an instance of str or Path')
    cfp = Path(config_file_path)
    if not cfp.exists():
        raise FileNotFoundError(f"No such file: '{config_file_path}'")
    if not cfp.is_file():
        raise IsADirectoryError(f"File path is not a file: '{config_file_path}'")
    return cfp

def _check_base_dir_override(base_dir_override: Path | str) -> Path:
    if not isinstance(base_dir_override, (str, Path)):
        raise TypeError('Argument base_dir_override is not an instance of str or Path')
    bdo = Path(base_dir_override)
    if not bdo.exists():
        raise FileNotFoundError(f"No such file: '{base_dir_override}'")
    if not bdo.is_dir():
        raise NotADirectoryError(f"File path is not a directory: '{base_dir_override}'")
    return bdo

#: ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

@dataclass
class LMContext(Context):
    """
    Context for the Reversi Logistic Model pipeline.
    Holds all data artifacts and configuration state shared across workers.
    """
    config_file_path: Path
    base_dir_override: Path | None = None
    use_cache: bool | None = None

    # Data artifacts populated by the workers

    # Configuration attribute:
    cfg: Any = None
    # The config fingerprint (D-142): the sha3_256 hex of the
    # normalized dump (cfg.model_dump_json(indent=4)) — computed at
    # CONFIG, consumed by the SAVE config record and the analytics
    # report.
    config_checksum: str | None = None

    # Game positions and game values attributes:
    rds_checksum: str | None = None
    positions: Any = None
    game_values: Any = None
    training_pop_stats: Any = None

    # Features attribute:
    feature_set: Any = None

    # Feature analysis attribute (the SU level, step 3): the
    # corpus frequency tables (the marginal + the joint)
    # published by the SU_ANALYSIS worker for the EFFECT_SIZE
    # level (the cross-level blackboard, the D-099
    # pre-declared fields).
    su_analysis_tables: Any = None

    # Indexes attribute:
    hlp_indexes_checksum: str | None = None
    hlp_indexes: Any = None

    # Wmaps attributes:
    wmaps_obj_checksum: str | None = None
    feature_w_ranges: Any = None
    iwmap_feature_offset: Any = None
    iwmap: Any = None
    wmap: Any = None
    wmap_fallback: Any = None
    w: Any = None

    # Design Matrix attribute:
    design_matrix_checksum: str | None = None
    design_matrix: Any = None

    # ZED attributes:
    zed_checksum: str | None = None
    y2z: Any = None
    z2y: Any = None
    z: Any = None

    # Loss and gradient closure attribute:
    fg: Any = None

    # Optimization outcome attribute:
    w_checksum: str | None = None
    opt_info: Any = None

    # Full exploded weight array:
    dense_w_checksum: str | None = None
    w_dense: Any = None

    # Game Position for Validation attributes:
    vld_rds_checksum: str | None = None
    vld_positions: Any = None
    vld_game_values: Any = None
    vld_pop_stats: Any = None

    # Validation attributes:
    vld_metrics: Any = None
    # The validation forward-pass series: published by VALIDATE
    # so PLOT renders them instead of re-running the pass, and so
    # CLIENT_CHECK compares against the validation's own residuals.
    vld_y_pred: Any = None
    vld_rn: Any = None
    # The top-20 extreme-residual records: a list of dicts with
    # the raw values (index, mover, opponent, game_value, fitted,
    # residual), descending by |residual|.
    vld_outliers: Any = None

    # Analytic attributes:
    train_metrics: Any = None
    train_dense_metrics: Any = None
    # The dense training residuals in Y: published by ANALYTICS
    # so PLOT renders them instead of re-running the pass.
    train_dense_rn: Any = None
    analytics_report: Any = None

    # Injected by StateMachine: the lambda defaults are the
    # pre-injection fallback, under the same D-069
    # *_for_current_level names the machine injects (D-074/R1).
    log_event: Callable = lambda *args: None
    get_cache_file_path_for_current_level: Callable = lambda: None
    get_cache_file_full_path_for_current_level: Callable = lambda: None


# --- Level 0: CREATED (Kept here as it's just a dummy blocker) ---

def _created_up(ctx: LMContext) -> None:
    ctx.log_event(Relevance.ERROR, "Executing CREATED up worker should never happen.")
    raise RuntimeError("Executing created step should never happen.")

def _created_down(ctx: LMContext) -> None:
    ctx.log_event(Relevance.ERROR, "Executing CREATED down worker should never happen.")
    raise RuntimeError("Cleaning created step should never happen.")


class LogisticModel(BaseModel):
    """
    Facade for the Reversi Logistic Model pipeline.
    Orchestrates the state machine and the shared context.
    """

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self,
                 config_file_path: str | Path,
                 verbosity: Verbosity = Verbosity.STANDARD,
                 base_dir_override: str | Path | None = None):
        """
        Build the LM facade: validate the domain paths, create the
        shared LMContext, assemble the worker pipeline and hand the
        parts to the StateMachine (via BaseModel).
        """

        # 1. Validate domain specific paths
        config_file_path = _check_config_file_path(config_file_path)
        if base_dir_override is not None:
            base_dir_override = _check_base_dir_override(base_dir_override)

        # 2. Initialize the shared context
        context = LMContext(
            config_file_path=config_file_path,
            base_dir_override=base_dir_override
        )

        # 3. Build the pipeline using the factory functions
        workers: List[Worker] = [
            Worker("CREATED", _created_up, _created_down),
            wrk_config(),
            wrk_features(),
            wrk_su_analysis(),
            wrk_positions(),
            wrk_indexes(),
            wrk_effect_size(),
            wrk_wmaps(),
            wrk_design_matrix(),
            wrk_zed(),
            wrk_gradient(),
            wrk_optimize(),
            wrk_generate(),
            wrk_vld_positions(),
            wrk_validate(),
            wrk_analytics(),
            wrk_save(),
            wrk_client_check(),
            wrk_plot()
        ]

        # 4. Call the superclass constructor with the assembled parts
        super().__init__(workers=workers, context=context, verbosity=verbosity)

    def _configured_target_level(self) -> int | str | None:
        """The LMConfig.target_level of the loaded configuration: the
        pipeline stop the config asks for, honored by run() when no
        explicit target is given. It is read AFTER the CONFIG level ran
        (run() moves there first); "last" (the field default) and a
        blank value mean the whole pipeline. A context without a
        loaded config (or one that does not carry the field) resolves
        to None — the same "last" outcome."""
        cfg = self.context.cfg
        if cfg is None:
            return None
        return getattr(cfg, "target_level", None)


# ---

@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def build_model(json_config: Path, verbosity: Verbosity) -> None:
    rlm = LogisticModel(json_config, verbosity=verbosity)
    rlm.move_to_last()

    return

#: ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

#
#
# How to run the logistic_model pipeline.
#
# Run from the workspace root (the directory containing .venv and src).
#
# -0- Activate the environment.
#
# $ source .venv/bin/activate
#
# -1- Run the pipeline.
#
# $ time python3 -m reversi.lm.logistic_model <your_rlm_config_file.json>
#

if __name__ == '__main__':

    # Initialize the parser and describe the script
    parser = argparse.ArgumentParser(description="Script to run model optimization.")

    # 1. Direct conversion to Path object
    parser.add_argument('config', type=Path, help='Json configuration file.')

    # Dictionary mapping lowercase strings to their corresponding Enum members
    verbosity_map = {e.name.lower(): e for e in Verbosity}

    # 2. Use string choices for clean CLI help/error messages, then convert via lambda
    parser.add_argument(
        '--verbosity',
        type=str,
        choices=list(verbosity_map.keys()),
        default='standard',
        help="Logging verbosity level"
    )

    # Parse the command-line arguments
    args = parser.parse_args()

    # 3. Resolve the string choice back to the actual Verbosity Enum object
    verbosity_enum = verbosity_map[args.verbosity.lower()]

    # Build the model using validated types
    build_model(args.config, verbosity_enum)
