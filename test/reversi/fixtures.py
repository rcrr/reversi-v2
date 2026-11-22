"""
Rebuildable LM test fixtures (the sticky ModelWeights artifacts).

A fixture is a trained LogisticModel model, built ONCE by this helper and consumed (tier-
agnostic) by the test modules that need a real saved model on disk — the multi-ply
evaluation-function tests first. A fixture is "a bit more sticky" than the transient
setUp-built artifacts: it lives under build/tmp/fixtures/ (git-ignored, the build/ pattern),
survives for sessions of weeks, and is rebuilt on demand.

The artifact is a SINGLE self-verifying model file (the sidecar record is retired: the
sha3_256 fingerprint is embedded in the file and model_weights_read_file checks it on every
load) — so presence is "the .dat exists", and integrity is enforced at consumption. If the
ModelWeights FORMAT ever changes, this helper is not expected to know: clean + rebuild.

Usage (from the workspace root):

    python -m test.reversi.fixtures create rlm_fixture_simple_ec20 [--force]
    python -m test.reversi.fixtures clean rlm_fixture_simple_ec20

The consumer idiom (a test setUp):

    from test.reversi.fixtures import require_lm_fixture
    model_path = require_lm_fixture('rlm_fixture_simple_ec20')
"""

import argparse
import shutil
from pathlib import Path

from reversi.lm.logistic_model import LogisticModel
from reversi.tools.state_machine import Verbosity

__all__ = [
    'FIXTURE_ROOT',
    'FIXTURE_CONFIG_DIR',
    'lm_fixture_config_path',
    'lm_fixture_dir',
    'lm_fixture_model_path',
    'clean_lm_fixture',
    'create_lm_fixture',
    'require_lm_fixture',
]

#: The fixture artifact root (git-ignored: the build/ pattern).
FIXTURE_ROOT = Path('build/tmp/fixtures')

#: The fixture config (SOURCE) directory (committed).
FIXTURE_CONFIG_DIR = Path('test/reversi/data')


def lm_fixture_config_path(name: str) -> Path:
    """
    The committed config JSON of the fixture.

    Args:
        name: the fixture name (e.g. 'rlm_fixture_simple_ec20').

    Returns:
        Path: test/reversi/data/<name>.json
    """
    return FIXTURE_CONFIG_DIR / f'{name}.json'


def lm_fixture_dir(name: str) -> Path:
    """
    The fixture artifact directory (the pipeline base_dir of the build).

    Args:
        name: the fixture name.

    Returns:
        Path: build/tmp/fixtures/<name>
    """
    return FIXTURE_ROOT / name


def lm_fixture_model_path(name: str) -> Path:
    """
    The fixture model file (the single self-verifying artifact).

    Args:
        name: the fixture name.

    Returns:
        Path: build/tmp/fixtures/<name>/<name>.dat
    """
    return lm_fixture_dir(name) / f'{name}.dat'


def clean_lm_fixture(name: str) -> None:
    """
    Remove the whole fixture directory (idempotent: a missing directory is a no-op).

    Args:
        name: the fixture name.
    """
    shutil.rmtree(lm_fixture_dir(name), ignore_missing=True)


def create_lm_fixture(name: str, force_rebuild: bool = False) -> Path:
    """
    Build the fixture model if it is not there yet.

    Idempotent: an existing model file short-circuits (no pipeline run) unless
    force_rebuild is True, in which case the fixture is cleaned first. The pipeline runs the
    standard worker chain STOPPED at the CLIENT_CHECK level (SAVE + the client-check
    integrity gate included; PLOT + FINAL_LOG_PRINT skipped) — the config carries
    plot.enable = false as well.

    Args:
        name: the fixture name (its config must exist in test/reversi/data/).
        force_rebuild: clean the fixture directory before building.

    Returns:
        Path: the model file path.

    Raises:
        ValueError: the fixture config is missing.
    """
    config_path = lm_fixture_config_path(name)
    if not config_path.is_file():
        raise ValueError(f'no fixture config for {name!r}: {config_path} is missing')

    model_path = lm_fixture_model_path(name)
    if model_path.is_file():
        if not force_rebuild:
            return model_path
        clean_lm_fixture(name)

    # The CONFIG worker requires the base dir to EXIST (it validates, it does not create).
    lm_fixture_dir(name).mkdir(parents=True, exist_ok=True)

    rlm = LogisticModel(config_path, verbosity=Verbosity.STANDARD)
    rlm.move_to_step('CLIENT_CHECK')
    return model_path


def require_lm_fixture(name: str) -> Path:
    """
    The consumer gate: the fixture model path, or a clear, actionable error naming the exact
    build command (a missing fixture is a local state to fix, not an environment limitation).

    Args:
        name: the fixture name.

    Returns:
        Path: the model file path (its existence; integrity is checked at load time).

    Raises:
        RuntimeError: the model file is missing — the message names the build command.
    """
    model_path = lm_fixture_model_path(name)
    if model_path.is_file():
        return model_path
    raise RuntimeError(
        f'LM fixture {name!r} is missing ({model_path} not found) — build it first: '
        f'python -m test.reversi.fixtures create {name}')


def _main() -> None:
    """The small CLI: create / clean one or more fixtures."""
    parser = argparse.ArgumentParser(description='Build / clean the rebuildable LM test fixtures.')
    parser.add_argument('command', choices=['create', 'clean'])
    parser.add_argument('names', nargs='+', help='the fixture names (e.g. rlm_fixture_simple_ec20)')
    parser.add_argument('--force', action='store_true', help='clean before creating (rebuild)')
    args = parser.parse_args()

    for name in args.names:
        if args.command == 'clean':
            clean_lm_fixture(name)
            print(f'cleaned {name}')
        else:
            path = create_lm_fixture(name, force_rebuild=args.force)
            print(f'created {path}')


if __name__ == '__main__':
    _main()
