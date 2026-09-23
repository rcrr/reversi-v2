#
# hlp_config_schemas.py
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

from pydantic import (BaseModel, Field, PositiveInt, NonNegativeInt,
                      field_validator, field_serializer,
                      ConfigDict, model_validator)

from typing import List, Annotated, Optional, Any, Tuple

from pathlib import Path

from reversi.board import (Bitboard,
                         bitboard_from_hex_str)
from reversi.lm.hlp_plot import PLOT_NAMES  # the plot vocabulary (D-149)



__all__ = ['LMConfig']



class LMBaseConfig(BaseModel):
    properties: dict[str, Any] = Field(default_factory=dict)

StatusString = Annotated[str, Field(pattern=r"^[A-Z]{3}$")]

class ValidationDataSetConfig(LMBaseConfig):
    bid: List[NonNegativeInt]
    status: List[StatusString]

class OptimizationConfig(LMBaseConfig):
    """
    Configuration for the L-BFGS optimizer.
    """
    max_iters: int = Field(default=500, ge=1, description="Maximum number of iterations.")
    m: int = Field(default=50, ge=1, description="Memory size (number of stored vector pairs).")
    c1: float = Field(default=1e-4, gt=0, lt=1, description="Armijo condition constant.")
    c2: float = Field(default=0.9, gt=0, lt=1, description="Wolfe condition constant. Must be > c1.")
    min_grad: Tuple[float, int] = Field(default=(1e-5, 3), description="Stopping tolerance for gradient norm and consecutive iterations.")
    min_p_fun_decrease: Tuple[float, int] = Field(default=(1e-14, 7), description="Minimum relative loss decrease and consecutive iterations.")
    log_every_n: int = Field(default=0, ge=0, description="Frequency of logging. 0 = no log, 1 = every iteration.")
    save_every_n: int = Field(default=0, ge=0, description="Frequency of saving checkpoints. 0 = no save.")
    checkpoint_file: Path = Field(..., description="Checkpoint file name used to save optimization status.")
    high_performance_fg: bool = Field(
        default=False,
        description="Build the high-performance numba fg closure at the "
                    "GRADIENT level. False (the default) keeps the classic "
                    "vectorized-numpy closure.")

    @model_validator(mode="after")
    def check_wolfe_constants(self) -> "OptimizationConfig":
        """Enforce c2 > c1 (the strong-Wolfe condition pair)."""
        if self.c2 <= self.c1:
            raise ValueError(
                f"c2 ({self.c2}) must be greater than c1 ({self.c1}) "
                "for the strong-Wolfe conditions."
            )
        return self

class AnalyticsConfig(LMBaseConfig):
    """
    Configuration for model analytics report generation.
    """
    detailed_report: List[str] = Field(
        default_factory=list, 
        description="List of feature names to include detailed row-by-row tables for in the analytics TXT report."
    )
    report_file_name: str = Field(
        default="model_analytics_report.txt",
        description="Filename for the detailed analytics report."
    )
    
class PlotConfig(LMBaseConfig):
    """
    Configuration for the PLOT level (D-149): the matplotlib
    diagnostic figures written after CLIENT_CHECK (the 18th level).
    The plots WHITELIST decides what is generated (a listed name is
    written, an unlisted name is skipped, an empty list makes the
    level a no-op); the enable master switch dominates (false = do
    nothing, even with names listed).
    """
    enable: bool = Field(
        default=True,
        description="Master switch: false makes the PLOT level a "
                    "no-op, even when plot names are listed (D-149).")
    format: str = Field(
        default="png",
        description="Output format: 'png', 'pdf', or a "
                    "comma-separated pair (e.g. 'pdf,png' — both).")
    dpi: int = Field(
        default=150, ge=50, le=1200,
        description="Raster resolution, for the png output.")
    dir_name: Path = Field(
        default=Path("plots"),
        description="Output directory: an ABSOLUTE path is used "
                    "as-is (it may live outside base_dir); a "
                    "relative path resolves under base_dir.")
    plots: List[str] = Field(
        default_factory=list,
        description="Whitelist of plot names to generate (D-149); "
                    "an empty list makes the PLOT level a no-op. "
                    "Valid names: " + ", ".join(PLOT_NAMES))

    @field_validator("format")
    @classmethod
    def check_format(cls, v: str) -> str:
        """Normalize the format pair: whitespace stripped, every
        token must be 'png' or 'pdf', no duplicates, at least one."""
        parts = [p.strip() for p in v.split(",")]
        bad = [p for p in parts if p not in ("png", "pdf")]
        if bad:
            raise ValueError(
                f"Unknown plot format token {bad}; use 'png', 'pdf' "
                "or a comma-separated pair (e.g. 'pdf,png').")
        if len(parts) != len(set(parts)):
            raise ValueError(f"Duplicate plot format in {v!r}.")
        return ",".join(parts)

    @field_validator("plots")
    @classmethod
    def check_plots(cls, v: List[str]) -> List[str]:
        """Fail fast (at the CONFIG level) on unknown names and
        deduplicate preserving order (a repeated name would
        regenerate the same file twice)."""
        unknown = [n for n in v if n not in PLOT_NAMES]
        if unknown:
            raise ValueError(
                f"Unknown plot name(s) {unknown}; valid names: "
                + ", ".join(PLOT_NAMES))
        return list(dict.fromkeys(v))


class CorpusConfig(LMBaseConfig):
    """
    Configuration for the SU_ANALYSIS corpus (the
    SU-analysis corpus generator): the MT19937 seed, the total
    positions. The ec arrest rule (the empty_count window, the
    design section 2.1 "mele con mele" window) is the ROOT
    `empty_count` (D-281) — the corpus is arrested at the SAME ec
    the DB extraction uses (the value lives at the config root).
    """
    seed: int = Field(
        default=42,
        description="The MT19937 corpus seed (the 'uno per tutti').")
    total_positions: PositiveInt = Field(
        default=10_000_000,
        description="The total positions to generate (the "
                    "default 1e7 — minutes at the wave tier).")


class SuAnalysisConfig(LMBaseConfig):
    """
    Configuration for the SU_ANALYSIS level (pipeline step
    3): the corpus generator + the SU / the dispersion / the
    never-observed audit kernels. The enable master switch is
    FALSE by default (the SU analysis is OPTIONAL, opt-in; the
    production configs are untouched, the experiment configs
    opt in). The su_pairs are the explicit (feature, feature)
    pairs for the joint analysis (the canonical sorted form +
    the dedupe); the fail-fast against the feature set is at
    the LMConfig level (it needs the feature_set field). The
    rarity_thresholds are the optional per-bin frequency
    thresholds for the report's 'Section B: Rarity report'
    (the half-open bins [0, t1), [t1, t2), ..., [tk, inf) —
    the first bin the zero-frequency codes); None or an empty
    list leaves the section off (the default).
    """
    enable: bool = Field(
        default=False,
        description="Master switch: false makes the SU_ANALYSIS "
                    "level a no-op (the SU analysis is OPTIONAL, "
                    "opt-in).")
    corpus: CorpusConfig = Field(
        default_factory=CorpusConfig,
        description="The corpus generator spec (the seed, the "
                    "total positions, the ec arrest rule).")
    su_pairs: List[Tuple[str, str]] = Field(
        default_factory=list,
        description="The explicit (feature, feature) pairs for "
                    "the joint analysis; an empty list "
                    "makes no joint (the default corpus cost). "
                    "Canonical sorted form + dedupe; the fail-"
                    "fast against the feature set is at the "
                    "LMConfig level.")
    rarity_thresholds: Optional[List[int]] = Field(
        default=None,
        description="The per-bin frequency thresholds for the "
                    "optional report 'Section B: Rarity report' "
                    "(the half-open bins [0, t1), [t1, t2), ... "
                    "[tk, inf) — the first bin the zero-"
                    "frequency codes). None or an empty list "
                    "leaves the section off (the default). "
                    "Positive strictly-increasing integers.")
    dir_name: Path = Field(
        default=Path("su_analysis"),
        description="Output directory: an ABSOLUTE path is used "
                    "as-is (it may live outside base_dir); a "
                    "relative path resolves under base_dir.")
    report_file_name: str = Field(
        default="su_analysis_report.txt",
        description="The TXT report filename.")
    export_csv: bool = Field(
        default=False,
        description="Whether to export the CSV (the optional; the "
                    "console + the TXT are always written).")

    @field_validator("su_pairs")
    @classmethod
    def check_su_pairs(cls, v: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Canonical order (each pair sorted) + dedupe.
        The fail-fast against the feature set is at the LMConfig
        level (it needs the feature_set field)."""
        canonical = [tuple(sorted(pair)) for pair in v]
        return list(dict.fromkeys(canonical))

    @field_validator("rarity_thresholds")
    @classmethod
    def check_rarity_thresholds(cls, v: Optional[List[int]]
                                ) -> Optional[List[int]]:
        """None or empty = the rarity section off (the default).
        Otherwise: positive strictly-increasing integers."""
        if not v:
            return v
        if any(t <= 0 for t in v):
            raise ValueError("the rarity thresholds must be "
                             "positive integers")
        if any(a >= b for a, b in zip(v, v[1:])):
            raise ValueError("the rarity thresholds must be "
                             "strictly increasing")
        return v


class EffectSizeConfig(LMBaseConfig):
    """
    Configuration for the EFFECT_SIZE level (the
    eta²/omega² + the adherence, step 6). The enable master
    switch is FALSE by default (opt-in). The
    top_k_adherence is the number of the most deviant features
    reported in the console (the TV descending).
    """
    enable: bool = Field(
        default=False,
        description="Master switch: false makes the EFFECT_SIZE "
                    "level a no-op (the effect size is "
                    "OPTIONAL, opt-in).")
    top_k_adherence: int = Field(
        default=20, ge=1,
        description="The number of the most deviant features "
                    "reported in the console (the TV descending).")
    dir_name: Path = Field(
        default=Path("effect_size"),
        description="Output directory: an ABSOLUTE path is used "
                    "as-is (it may live outside base_dir); a "
                    "relative path resolves under base_dir.")
    report_file_name: str = Field(
        default="effect_size_report.txt",
        description="The TXT report filename.")
    export_csv: bool = Field(
        default=False,
        description="Whether to export the CSV (the optional; the "
                    "console + the TXT are always written).")


class RegabDBConnectionConfig(LMBaseConfig):
    """
    Configuration for connecting to the Regab database.
    """
    dbname: str
    user: str
    host: str
    port: int = 5432
    password: Optional[str] = None

class RegabDataSetConfig(LMBaseConfig):
    """
    Configuration for a Regab data set, including the database connection and filtering criteria.
    """
    regab_db_connection: RegabDBConnectionConfig
    bid: List[NonNegativeInt]
    status: List[StatusString]

class PatternConfig(LMBaseConfig):
    """
    Configuration for a pattern, including its name and mask.
    """
    name: str
    mask: Bitboard = Field(..., description="A 64-bit hex string: 16 hex digits, no 0x prefix, case-insensitive.")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("mask", mode="before")
    @classmethod
    def parse_hex_to_bitboard(cls, h: str) -> Bitboard:
        """
        Converts a hex string (e.g., '0000000000000107' — 16 digits,
        no 0x prefix) into a Bitboard.
        """
        return bitboard_from_hex_str(h)

    @field_serializer("mask")
    def serialize_mask_to_hex(self, mask: Bitboard) -> str:
        return f"{mask:016X}"

class PatternSetConfig(LMBaseConfig):
    """
    Configuration for a set of patterns, including the name and a list of individual pattern configurations.
    """
    name: str
    patterns: List[PatternConfig] = Field(default_factory=list)

class MobilityFeatureConfig(LMBaseConfig):
    """
    Configuration for a mobility feature.
    """
    name: str
    mask: Bitboard = Field(..., description="Legal moves mask in HEX format, no 0x prefix, just 16 digits.")
    amask: Bitboard = Field(..., description="Anti legal moves mask in HEX format, no 0x prefix, just 16 digits.")
 
    model_config = ConfigDict(arbitrary_types_allowed=True) 

    @field_validator("mask", "amask", mode="before")
    @classmethod
    def parse_hex_to_bitboard(cls, h: str) -> Bitboard:
        """
        Converts a hex string (e.g., '0000000000000107' — 16 digits,
        no 0x prefix) into a Bitboard.
        """
        return bitboard_from_hex_str(h)

    @field_serializer("mask", "amask")
    def serialize_mask_to_hex(self, mask: Bitboard) -> str:
        return f"{mask:016X}"
    
class MobilitySetConfig(LMBaseConfig):
    """
    Configuration for a set of mobility features, including the name and a list of individual configurations.
    """
    name: str
    mobility_features: List[MobilityFeatureConfig] = Field(default_factory=list)

class FeatureSetConfig(LMBaseConfig):
    """
    Configuration for the set of features.
    """
    name: Optional[str] = 'NoNameFeatureSet'
    intercept: Optional[bool] = False
    mobility_set: Optional[MobilitySetConfig] = None
    pattern_set: Optional[PatternSetConfig] = None
    
class StatModelConfig(LMBaseConfig):
    """
    Configuration for a statistical model, including the frequency cut-off threshold.
    """
    frequency_cut_off: PositiveInt = 1
    logit_clipping: float = Field(default=0.05, gt=0, lt=0.5)
    ridge_regularization: float = Field(default=0.00, ge=0.00)

class LMConfig(LMBaseConfig):
    """
    Configuration for the Reversi Logistic Model, including general settings,
    data set configuration.
    """
    name: str
    empty_count: int = Field(
        ..., ge=0, le=60,
        description="The empty_count (the ec, the game phase window, "
                    "the 'mele con mele' constraint) — the single "
                    "source for the SU corpus generation, the DB "
                    "extraction (training + validation), and the "
                    "saved model. D-280: the consolidated field, "
                    "replacing the redundant su_analysis.corpus.ec + "
                    "regab_data_set.ec.")
    description: str
    base_dir: Path
    output: Path = Field(..., description="Output filename for the saved binary model weights.")
    use_cache: bool = True
    cache_files_prefix: str = Field(
        default="rlmwf_",
        description="Filename prefix for the level specific cache files."
    )
    regab_allow_duplicate: bool = Field(
        default=True,
        description="Duplicate game positions policy (D-143). The same "
        "(mover, opponent) key can be recorded more than once in the DB; "
        "True (the default, the pre-existing behaviour) keeps every row, "
        "False deduplicates keeping the first occurrence (the lowest seq). "
        "The duplicate count is logged at the POSITIONS and VLD_POSITIONS "
        "levels, and the validation-vs-training overlap is logged at "
        "VLD_POSITIONS (log only, no action)."
    )
    client_check_tol: float = Field(
        default=1e-8, gt=0,
        description="CLIENT_CHECK level tolerance (D-148): the "
        "maximum absolute difference (Y space) admitted between the "
        "validation residuals recomputed from the SAVED model file "
        "(the client's Evaluation Function) and the in-memory "
        "validation residuals (the VALIDATE forward pass). The two "
        "are expected bit-identical (the same f32 pipeline over the "
        "bit-exact file round-trip); the tolerance guards against "
        "pipeline drift and file corruption. Y space, because Y "
        "values are comparable across models (different "
        "logit_clipping); Z values are distorted per model."
    )
    plot: PlotConfig = Field(default_factory=PlotConfig)
    regab_data_set: RegabDataSetConfig
    feature_set: FeatureSetConfig
    stat_model: StatModelConfig
    optimization: OptimizationConfig
    validation_data_set: ValidationDataSetConfig
    analytics: AnalyticsConfig = Field(default_factory=AnalyticsConfig)
    su_analysis: SuAnalysisConfig = Field(
        default_factory=SuAnalysisConfig,
        description="The SU_ANALYSIS level config (the SU "
                    "level, step 3; the enable default FALSE, "
                    "opt-in).")
    effect_size: EffectSizeConfig = Field(
        default_factory=EffectSizeConfig,
        description="The EFFECT_SIZE level config (the "
                    "eta²/omega² + the adherence, step 6; the "
                    "enable default FALSE, opt-in).")
    target_level: str = Field(
        default="last",
        description="The pipeline stop target (the design "
                    "section 3.6): a level name (case-"
                    "insensitive, the fail-fast ValueError in the "
                    "StateMachine) or 'last' (the full pipeline). "
                    "Consumed by the facade's run() when no explicit "
                    "target is given; a blank value means 'last' too.")

    @model_validator(mode="after")
    def check_su_pairs_feature_set(self) -> "LMConfig":
        """The fail-fast against the feature set:
        every name in the su_analysis.su_pairs must be a
        feature in the feature_set (the mobility names + the
        pattern names)."""
        if self.feature_set is not None:
            names = set()
            if self.feature_set.mobility_set is not None:
                names.update(f.name for f in
                             self.feature_set.mobility_set
                             .mobility_features)
            if self.feature_set.pattern_set is not None:
                names.update(p.name for p in
                             self.feature_set.pattern_set.patterns)
            for pair in self.su_analysis.su_pairs:
                for name in pair:
                    if name not in names:
                        raise ValueError(
                            f"su_pairs feature name {name!r} is "
                            "not in the feature set; valid names: "
                            + ", ".join(sorted(names)))
        return self
