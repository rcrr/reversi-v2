#
# base_model.py
#
# This file is part of the reversi program
# http://github.com/rcrr/reversi-v2
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

from pathlib import Path
from typing import List

from pydantic import ConfigDict, validate_call

from reversi.tools.state_machine import StateMachine, Worker, Context, Verbosity


__all__ = ['BaseModel']


class BaseModel:
    """
    Base class for pipeline facades. Encapsulates the generic delegation to the StateMachine,
    avoiding boilerplate in concrete domain-specific model classes (e.g., LogisticModel, DeepNetworkModel).
    """

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, workers: List[Worker], context: Context, verbosity: Verbosity = Verbosity.STANDARD):
        """Create the facade: store the shared context and build the StateMachine."""
        self.context = context
        self.sm = StateMachine(
            workers=workers,
            context=context,
            verbosity=verbosity
        )

    @property
    def current_step(self) -> int:
        """The StateMachine's current step."""
        return self.sm.current_step

    @property
    def current_worker_name(self) -> str:
        """The StateMachine's current worker name."""
        return self.sm.current_worker_name

    @property
    def verbosity(self) -> Verbosity:
        """The StateMachine's verbosity."""
        return self.sm.verbosity

    @verbosity.setter
    def verbosity(self, value: Verbosity) -> None:
        """Set the StateMachine's verbosity."""
        self.sm.verbosity = value

    def move_to_step(self, target_step: int | str) -> None:
        """Move the pipeline to the specified step."""
        self.sm.move_to_step(target_step)

    def move_to_last(self) -> None:
        """Move the pipeline to the last step."""
        self.sm.move_to_last()

    def run(self, target_level: int | str | None = None) -> None:
        """
        Drive the pipeline to a target step.

        The first real level (step 1) runs first, so that the domain config is loaded before it can
        name its own target. The target resolves as the explicit argument, else the domain's
        configured target (see _configured_target_level), else the last step; the string "last" (any
        case) and a blank value mean the last step as well. Any level name is a legal stop (resolved
        case-insensitively by the machine), and the target step IS executed: the resulting state is
        "steps 1..target done".

        Failure semantics are the machine's: an unknown name raises its ValueError, a wrong-typed
        target its TypeError, and a failing worker leaves current_step at the failed step. A second
        run() with a DEEPER target RESUMES — the levels already done are not re-run, so their
        context artifacts stay published and the on-disk caches stay hot; a target BELOW the current
        step moves back instead, running the down() of the levels left behind.
        """
        if self.current_step < 1:
            self.move_to_step(1)
        target = (target_level if target_level is not None
                  else self._configured_target_level())
        if target is None or (isinstance(target, str)
                              and target.strip().lower() in ('', 'last')):
            self.move_to_last()
        else:
            self.move_to_step(target)

    def _configured_target_level(self) -> int | str | None:
        """
        The domain's configured stop target, resolved after the first level ran. The base default is
        None (the whole pipeline); a concrete facade overrides it to read its own config
        (LogisticModel reads LMConfig.target_level).
        """
        return None

    def show_event_log(self) -> None:
        """Delegates to the StateMachine's show_event_log."""
        self.sm.show_event_log()

    def show_history_of_moves(self) -> None:
        """Delegates to the StateMachine's show_history_of_moves."""
        self.sm.show_history_of_moves()

    def export_history_of_moves_as_csv(self, filename: str | Path) -> None:
        """Delegates to the StateMachine's export_history_of_moves_as_csv."""
        self.sm.export_history_of_moves_as_csv(filename)
