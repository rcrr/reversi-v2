#
# state_machine.py
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

from enum import IntEnum
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from contextlib import contextmanager
from typing import List, Callable, Any
from pathlib import Path
import csv



__all__ = ['Context', 'Worker', 'StateMachine', 'Verbosity', 'Relevance']



class Verbosity(IntEnum):
    """
    Logging verbosity levels: a log event is printed iff
    event.relevance >= verbosity (NONE = silent, VERY_LOW = ERROR only).
    """
    HIGH      = 0
    MODERATE  = 1
    STANDARD  = 2
    LOW       = 3
    VERY_LOW  = 4
    NONE      = 5

class Relevance(IntEnum):
    """
    Logging relevance levels.
    """
    TRACE     = 0
    DEBUG     = 1
    INFO      = 2
    WARN      = 3
    ERROR     = 4

class Context:
    """
    Base class for pipeline contexts.
    Holds the shared state and data artifacts passed between workers.
    Subclass this in the domain module to hold specific data (e.g., RLMContext).
    """
    pass


class Worker:
    """
    Represents a single step in the pipeline.
    Uses composition to hold the callable logic for moving up and down.
    """
    def __init__(self, name: str, up_callable: Callable[[Context], None], down_callable: Callable[[Context], None]):
        self.name = name
        self._up_callable = up_callable
        self._down_callable = down_callable

    def up(self, context: Context) -> None:
        """Execute the forward step logic."""
        self._up_callable(context)

    def down(self, context: Context) -> None:
        """Execute the backward (rollback) step logic."""
        self._down_callable(context)


class StateMachine:
    """
    Generic state machine orchestrating a sequence of Workers.
    It manages logging, history tracking, and state transitions.
    It is completely agnostic of the domain logic.

    State model: current_step is the index of the last executed
    step. Step 0 is the initial sentinel state (nothing has been
    executed): the workers[0] up/down callables are never invoked
    by the machine — by domain design the first worker is a
    sentinel (e.g. the RLM pipeline's 'CREATED' bootstrap, which
    runs outside the machine). See move_to_step for the execution
    semantics of up/down moves.
    """

    @dataclass
    class StepMove:
        step: int
        worker_name: str
        direction: str
        start: datetime
        finish: datetime
        duration: timedelta

    @dataclass(frozen=True)
    class LogEntry:
        """
        Typed record for one logged event (immutable;
        dataclasses.asdict() gives the dict form for file/DB dumps).
        """
        time: datetime
        step: int
        worker_name: str
        relevance: Relevance
        message: str

    def __init__(self,
                 workers: List[Worker],
                 context: Context,
                 verbosity: Verbosity = Verbosity.STANDARD):
        self.workers: List[Worker] = workers
        self.context: Context = context
        self.current_step: int = 0
        self.logs: List[StateMachine.LogEntry] = []
        self.history: List[StateMachine.StepMove] = []
        self.verbosity: Verbosity = verbosity
        
        # Inject infrastructure helpers into the Context so workers can use them transparently
        self.context.log_event = self.log_event
        
        def _get_cache_file_path() -> Path:
            """Returns the cache file path for the currently executing worker."""
            if not self.workers:
                return Path()
            # current_step is updated BEFORE the worker executes, so it reflects the active worker
            level = self.current_step
            worker_name = self.workers[level].name
            # Note: context.cfg must be populated by a previous worker (e.g., ConfigWorker)
            cache_files_prefix = getattr(self.context, 'cfg').cache_files_prefix
            file_name = f"{cache_files_prefix}{level:02}_{worker_name}.dat"
            return Path(file_name)
            
        self.context.get_cache_file_path_for_next_level = _get_cache_file_path
        
        def _get_cache_file_full_path() -> Path:
            """Returns the full cache file path using base_dir from context.cfg."""
            # Note: context.cfg must be populated by a previous worker (e.g., ConfigWorker)
            base_dir = getattr(self.context, 'cfg').base_dir
            return base_dir / _get_cache_file_path()
            
        self.context.get_cache_file_full_path_for_next_level = _get_cache_file_full_path

        self.log_event(Relevance.DEBUG, "StateMachine initialized.")

    @contextmanager
    def _history_timer(self, step: int, worker_name: str, direction: str):
        start = datetime.now(timezone.utc)
        try:
            yield
        finally:
            finish = datetime.now(timezone.utc)
            self.history.append(self.StepMove(
                step=step,
                worker_name=worker_name,
                direction=direction,
                start=start,
                finish=finish,
                duration=finish - start
            ))

    def _run_step(self, worker: Worker, direction: str):
        try:
            self.log_event(Relevance.INFO, f"Starting worker {worker.name}, {direction.upper()} step")            
            if direction == 'up':
                worker.up(self.context)
            else:
                worker.down(self.context)
            self.log_event(Relevance.INFO, f"Completed {direction.upper()} step for {worker.name}")
        except Exception as e:
            self.log_event(Relevance.ERROR, f"Error in {worker.name} during {direction}: {str(e)}")
            raise

    @property
    def current_worker_name(self) -> str:
        if not self.workers:
            return "UNDEFINED"
        return self.workers[self.current_step].name

    def log_event(self, relevance: Relevance, message: str) -> None:
        """Logs an event using the current state step and worker."""
        evt_time = datetime.now(timezone.utc)
        event = self.LogEntry(
            time=evt_time,
            step=self.current_step,
            worker_name=self.current_worker_name,
            relevance=relevance,
            message=message,
        )
        self.logs.append(event)
        if relevance >= self.verbosity:
            timestamp = evt_time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] [{self.current_step:02}][{self.current_worker_name:15}] [{relevance}:{self.verbosity}] {message}")

    def show_event_log(self) -> None:
        print(f"\n--- --- --- --- --- - EVENT LOG - --- --- --- --- ---")
        print(f"______________________________________________________")
        print(f"TIMESTAMP           | STEP | WORKER           | R | MESSAGE")
        for entry in self.logs:
            timestamp = entry.time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp} | {entry.step:04} | {entry.worker_name:15} | {entry.relevance} | {entry.message}")

    def show_history_of_moves(self) -> None:
        print(f"{'Step':<6} | {'Worker':<15} | {'Dir':<5} | {'Start (UTC)':<26} | {'Dur (s)':<14}")
        print("-" * 80)
        for entry in self.history:
            start_str = entry.start.strftime("%Y-%m-%d %H:%M:%S.%f")
            dur = entry.duration.total_seconds()
            print(f"{entry.step:<6} | {entry.worker_name:<15} | {entry.direction:<5} | {start_str:<26} | {dur:>15.6f}")

    def export_history_of_moves_as_csv(self, filename: str | Path) -> None:
        keys = ["step", "worker_name", "direction", "start_utc", "finish_utc", "duration_sec"]
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            for entry in self.history:
                writer.writerow({
                    "step": entry.step,
                    "worker_name": entry.worker_name,
                    "direction": entry.direction,
                    "start_utc": entry.start.isoformat(),
                    "finish_utc": entry.finish.isoformat(),
                    "duration_sec": entry.duration.total_seconds()
                })

    def move_to_step(self, target_step: int | str) -> None:
        """
        Moves the state machine to the target step.
        Accepts an integer index or the string name of the target
        worker (case-insensitive). Up moves (t > current) execute
        up() of workers current+1..t, target included; down moves
        (t < current) execute down() of workers current..t+1,
        target excluded, leaving the state "steps 1..t done".
        Worker 0 is the sentinel initial state: it is never
        executed by the machine (see class docstring).

        Failure semantics: a failing worker's exception is logged
        and re-raised; current_step stays at the failed step k, so
        logs name the failing worker. A retry of a higher target
        does NOT re-execute k. To re-run it, first move to k-1
        (which invokes k's down(), the domain rollback) and then
        move up. The machine is domain-agnostic: it cannot know
        whether a failed step is safely re-runnable, so handling a
        failure is the domain worker's responsibility (D-060).
        """
        if isinstance(target_step, str):
            target_step = target_step.upper()
            target_index = next((i for i, w in enumerate(self.workers) if w.name.upper() == target_step), None)
            if target_index is None:
                raise ValueError(f"Worker '{target_step}' not found in the pipeline.")
            target_step = target_index

        if not isinstance(target_step, int):
            raise TypeError("target_step must be an integer index or a string worker name.")

        if target_step < 0 or target_step >= len(self.workers):
            raise IndexError(f"Target step {target_step} is out of bounds.")

        if target_step == self.current_step:
            return

        if target_step > self.current_step:
            steps = range(self.current_step + 1, target_step + 1)
            direction = 'up'
        else:
            steps = range(self.current_step, target_step, -1)
            direction = 'down'

        for step_idx in steps:
            worker = self.workers[step_idx]
            # Update the current step BEFORE execution so logs reflect the active worker
            self.current_step = step_idx
            
            with self._history_timer(step_idx, worker.name, direction):
                self._run_step(worker, direction)
        
        # If we moved down, the final step is the target step (which is less than the last executed step_idx)
        if direction == 'down':
            self.current_step = target_step

    def move_to_last(self) -> None:
        """
        Moves the state machine to the last (higher) step.
        """
        last = self.workers[-1] if self.workers else None
        if last is not None:
            self.move_to_step(last.name)
