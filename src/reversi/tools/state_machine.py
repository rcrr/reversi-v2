#
# state_machine.py
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

from enum import IntEnum
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from contextlib import contextmanager
from typing import List, Callable
from pathlib import Path
from pydantic import validate_call, ConfigDict, ValidationError
import csv
import time


__all__ = ['Context', 'Worker', 'StateMachine', 'Verbosity', 'Relevance']


class Verbosity(IntEnum):
    """
    Logging verbosity levels: a log event is printed iff event.relevance >= verbosity (NONE =
    silent, VERY_LOW = ERROR only).
    """
    HIGH      = 0
    MODERATE  = 1
    STANDARD  = 2
    LOW       = 3
    VERY_LOW  = 4
    NONE      = 5

class Relevance(IntEnum):
    """Logging relevance levels."""
    TRACE     = 0
    DEBUG     = 1
    INFO      = 2
    WARN      = 3
    ERROR     = 4

class Context:
    """
    Base class for pipeline contexts. Holds the shared state and data artifacts passed between
    workers. Subclass this in the domain module to hold specific data (e.g., LMContext).
    """
    pass


class Worker:
    """
    Represents a single step in the pipeline. Uses composition to hold the callable logic for moving
    up and down.
    """
    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self, name: str, up_callable: Callable[[Context], None], down_callable: Callable[[Context], None]):
        """
        Creates a worker step.

        Args:
            name: The worker's name (unique within a machine, case-insensitive).
            up_callable: The forward step logic.
            down_callable: The backward (rollback) step logic.
        """
        self.name = name
        self._up_callable = up_callable
        self._down_callable = down_callable

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def up(self, context: Context) -> None:
        """
        Executes the forward step logic.

        Args:
            context: The shared pipeline context.
        """
        self._up_callable(context)

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def down(self, context: Context) -> None:
        """
        Executes the backward (rollback) step logic.

        Args:
            context: The shared pipeline context.
        """
        self._down_callable(context)

    def __repr__(self) -> str:
        """The repr: Worker('NAME')."""
        return f"Worker({self.name!r})"


class StateMachine:
    """
    Generic state machine orchestrating a sequence of Workers. It manages logging, history tracking,
    and state transitions. It is completely agnostic of the domain logic.

    State model: current_step is the index of the last executed step. Step 0 is the initial sentinel
    state: the workers[0] up/down callables are never invoked by the machine — by domain design the
    first worker is a sentinel (e.g. the LM pipeline's 'CREATED' bootstrap, which runs outside the
    machine). See move_to_step for the execution semantics of up/down moves.
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
        Typed record for one logged event (immutable; dataclasses.asdict() gives the dict form for
        file/DB dumps).
        """
        time: datetime
        step: int
        worker_name: str
        relevance: Relevance
        message: str

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def __init__(self,
                 workers: List[Worker],
                 context: Context,
                 verbosity: Verbosity = Verbosity.STANDARD):
        """
        Creates the state machine and injects the infrastructure helpers.

        Fails fast on duplicate worker names: name-based moves (move_to_step, move_to_last) resolve
        by name, so names must be unique, and the check is case-insensitive because name resolution
        is case-insensitive. Binds log_event + format_event_log and the two cache-path closures onto
        the context (the injection is a side effect — a context shared by two machines re-binds to
        the last one built on it), then logs the init DEBUG event.

        Args:
            workers: The ordered pipeline steps (workers[0] is the sentinel).
            context: The shared context (domain subclasses pass their own).
            verbosity: The display gate (STANDARD by default).

        Raises:
            ValueError: When two workers share a name (case-insensitive).
        """
        seen = set()
        for worker in workers:
            key = worker.name.upper()
            if key in seen:
                raise ValueError(
                    f"Duplicate worker name '{worker.name}': "
                    "worker names must be unique (case-insensitive)")
            seen.add(key)
        self.workers: List[Worker] = workers
        self.context: Context = context
        self.current_step: int = 0
        self.logs: List[StateMachine.LogEntry] = []
        self.history: List[StateMachine.StepMove] = []
        self.verbosity: Verbosity = verbosity

        # Inject infrastructure helpers into the Context so workers can use them transparently
        self.context.log_event = self.log_event
        self.context.format_event_log = self.format_event_log

        def _get_cache_file_path() -> Path:
            """Returns the cache file path for the currently executing worker."""
            if not self.workers:
                return Path()
            # current_step is updated BEFORE the worker executes, so it reflects the active worker
            level = self.current_step
            worker_name = self.workers[level].name
            # Note: context.cfg must be populated by a previous worker (e.g., ConfigWorker)
            cache_files_prefix = getattr(self.context, 'cfg').cache_files_prefix
            # Filename-prefix concatenation: the domain's cache_files_prefix is a *filename* prefix,
            # so "rlmwf_" + "01_CONFIG.dat" yields the flat "rlmwf_01_CONFIG.dat". A directory-like
            # prefix must end with a separator.
            return Path(f"{cache_files_prefix}{level:02}_{worker_name}.dat")

        self.context.get_cache_file_path_for_current_level = _get_cache_file_path

        def _get_cache_file_full_path() -> Path:
            """Returns the full cache file path using base_dir from context.cfg."""
            # Note: context.cfg must be populated by a previous worker (e.g., ConfigWorker)
            base_dir = getattr(self.context, 'cfg').base_dir
            return base_dir / _get_cache_file_path()

        self.context.get_cache_file_full_path_for_current_level = _get_cache_file_full_path

        self.log_event(Relevance.DEBUG, "StateMachine initialized.")

    def __repr__(self) -> str:
        """
        The lightweight repr: worker count, current step and verbosity.

        Context, logs and history are excluded on purpose — they can hold large domain data.
        """
        return (f"StateMachine(workers={len(self.workers)}, "
                f"current_step={self.current_step}, "
                f"verbosity={self.verbosity.name})")

    @contextmanager
    def _history_timer(self, step: int, worker_name: str, direction: str):
        """
        Times one step execution and appends its StepMove to the history.

        The timer's finally records the move even when the worker raises, so a failed attempt is in
        the history.

        Args:
            step: The step index.
            worker_name: The worker's name.
            direction: 'up' or 'down'.
        """
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
        """
        Executes one worker step, logging the start, completion and errors.

        The worker's exception is logged (ERROR) and re-raised; the current step stays at the
        failing worker so the log names it.

        Args:
            worker: The worker to execute.
            direction: 'up' or 'down' (anything else raises ValueError).

        Raises:
            ValueError: When direction is neither 'up' nor 'down'.
        """
        try:
            self.log_event(Relevance.INFO, f"Starting worker {worker.name}, {direction.upper()} step")
            step_start = time.perf_counter()
            if direction == 'up':
                worker.up(self.context)
            elif direction == 'down':
                worker.down(self.context)
            else:
                raise ValueError(
                    f"Unknown direction {direction!r}: "
                    "expected 'up' or 'down'")
            duration = time.perf_counter() - step_start
            self.log_event(Relevance.INFO, f"Completed {direction.upper()} step for {worker.name}")
            self.log_event(Relevance.DEBUG, f"Step {worker.name} {direction.upper()} duration: {duration:.3f} s")
        except Exception as e:
            self.log_event(Relevance.ERROR, f"Error in {worker.name} during {direction}: {str(e)}")
            raise

    @property
    def current_worker_name(self) -> str:
        """The name of the worker at current_step ('UNDEFINED' when there are no workers)."""
        if not self.workers:
            return "UNDEFINED"
        return self.workers[self.current_step].name

    @staticmethod
    def _format_event_line(entry: "StateMachine.LogEntry", verbosity_name: str) -> str:
        """
        Formats one buffered log event as the live console line.

        The [timestamp UTC] [step] [worker] [relevance:verbosity] message shape, the enum names (not
        numeric values) + the explicit UTC marker, the fixed-width 5/8 right-justified fields for
        the variable-length names. The single source of truth for the live line and the buffered
        replay (the FINAL_LOG_PRINT file).

        Args:
            entry: The buffered event record.
            verbosity_name: The verbosity enum name to embed in the line (the machine's verbosity —
                constant over a run).

        Returns:
            str: The formatted line (no trailing newline).
        """
        timestamp = entry.time.strftime("%Y-%m-%d %H:%M:%S")
        return (f"[{timestamp} UTC] [{entry.step:02}]"
                f"[{entry.worker_name:15}] "
                f"[{entry.relevance.name:>5}:{verbosity_name:>8}] "
                f"{entry.message}")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def log_event(self, relevance: Relevance, message: str) -> None:
        """
        Logs an event at the current step, printing it when the gate allows.

        Always appends the typed LogEntry to the buffer; the live print happens only when the
        event's relevance passes the machine's verbosity gate.

        Args:
            relevance: The event's relevance level.
            message: The event message.
        """
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
            print(self._format_event_line(event, self.verbosity.name))

    def format_event_log(self, min_relevance: Relevance = Relevance.TRACE) -> str:
        """
        Renders the buffered event log (from min_relevance upward) as live-line formatted text.

        Every buffered LogEntry at or above min_relevance — independent of the display verbosity
        gate — is formatted in the live console line format (the shared formatter) and joined with
        newlines: the content of the FINAL_LOG_PRINT file (which passes DEBUG, keeping the TRACE
        hot-loop detail out of the file).

        Args:
            min_relevance: The relevance floor of the render (the default TRACE = every entry).

        Returns:
            str: The newline-joined log (the empty string when no event was logged yet).
        """
        return "\n".join(self._format_event_line(entry, self.verbosity.name)
                         for entry in self.logs
                         if entry.relevance >= min_relevance)

    def show_event_log(self) -> None:
        """
        Prints the buffered event log as a table.

        The banner, the 66-underscore separator, the TIMESTAMP (UTC) / STEP / WORKER / RELEVANCE /
        MESSAGE header (UTC timestamps, 2-digit steps, relevance names instead of numeric values,
        aligned columns), one row per buffered event.
        """
        print(f"\n--- --- --- --- --- - EVENT LOG - --- --- --- --- ---")
        print(f"{'_' * 66}")
        print(f"{'TIMESTAMP (UTC)':<19} | {'STEP':<4} | {'WORKER':<15} | "
              f"{'RELEVANCE':<9} | MESSAGE")
        for entry in self.logs:
            timestamp = entry.time.strftime("%Y-%m-%d %H:%M:%S")
            step_str = f"{entry.step:02}"
            print(f"{timestamp:<19} | {step_str:<4} | "
                  f"{entry.worker_name:<15} | {entry.relevance.name:<9} | "
                  f"{entry.message}")

    def show_history_of_moves(self) -> None:
        """
        Prints the step history as a table.

        The Step / Worker / Dir / Start (UTC) / Dur (s) header (the Dur (s) column right-aligned
        over its right-aligned values), the 80-dash rule, one row per recorded step (the start at
        microsecond precision).
        """
        print(f"{'Step':<6} | {'Worker':<15} | {'Dir':<5} | "
              f"{'Start (UTC)':<26} | {'Dur (s)':>15}")
        print("-" * 80)
        for entry in self.history:
            start_str = entry.start.strftime("%Y-%m-%d %H:%M:%S.%f")
            dur = entry.duration.total_seconds()
            print(f"{entry.step:<6} | {entry.worker_name:<15} | {entry.direction:<5} | {start_str:<26} | {dur:>15.6f}")

    @validate_call(config=ConfigDict(arbitrary_types_allowed=True))
    def export_history_of_moves_as_csv(self, filename: str | Path) -> None:
        """
        Exports the step history to a CSV file.

        The columns: step, worker_name, direction, start_utc, finish_utc (ISO-8601 UTC) and
        duration_sec (float seconds). Missing parent directories are created so nested filenames
        work out of the box; a bare filename has parent '.', where mkdir(exist_ok=True) is a no-op.

        Args:
            filename: The output path.
        """
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        keys = ["step", "worker_name", "direction", "start_utc", "finish_utc", "duration_sec"]
        with open(path, "w", newline="") as f:
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

        Accepts a Python int index or the string name of the target worker (case-insensitive); bool
        is explicitly NOT a valid step. Up moves (t > current) execute up() of workers current+1..t,
        target included; down moves (t < current) execute down() of workers current..t+1, target
        excluded, leaving the state "steps 1..t done". Worker 0 is the sentinel initial state: it is
        never executed by the machine (see class docstring).

        Failure semantics: a failing worker's exception is logged and re-raised; current_step stays
        at the failed step k, so logs name the failing worker. A retry of a higher target does NOT
        re-execute k. To re-run it, first move to k-1 (which invokes k's down(), the domain
        rollback) and then move up. The machine is domain-agnostic: it cannot know whether a failed
        step is safely re-runnable, so handling a failure is the domain worker's responsibility.
        """
        try:
            target_index = self._validate_target_step(target_step)
        except ValidationError as exc:
            # Public contract (pinned): a wrong target type is a TypeError with the exact message,
            # not a raw pydantic ValidationError. The gate is a SEPARATE @validate_call function
            # from the move execution, so only gate errors are converted; a pydantic ValidationError
            # raised by a DOMAIN worker during the move (e.g. a config schema) propagates unchanged
            # — the machine is domain-agnostic.
            raise TypeError(
                "target_step must be an integer index or a string "
                "worker name.") from exc
        self._execute_move(target_index)

    @validate_call(config=ConfigDict(
        arbitrary_types_allowed=True, strict=True))
    def _validate_target_step(self, target_step: int | str) -> int:
        """
        Validates and resolves the move target (the strict gate).

        Strictly a Python int or a str — bool, float, np.int64 and friends are rejected here (a bare
        isinstance check would have accepted bool). A name resolves case-insensitively. Deliberately
        separate from the move execution: its ValidationErrors are the ones converted to the pinned
        public TypeError by move_to_step.

        Args:
            target_step: The target step index or worker name.

        Returns:
            int: The resolved 0-based step index.

        Raises:
            ValueError: When the name matches no worker.
            IndexError: When the index is out of bounds.
        """
        if isinstance(target_step, str):
            target_step = target_step.upper()
            target_index = next((i for i, w in enumerate(self.workers) if w.name.upper() == target_step), None)
            if target_index is None:
                raise ValueError(f"Worker '{target_step}' not found in the pipeline.")
        else:
            target_index = target_step

        if target_index < 0 or target_index >= len(self.workers):
            raise IndexError(f"Target step {target_index} is out of bounds.")
        return target_index

    def _execute_move(self, target_index: int) -> None:
        """
        Executes the step walk from current_step to the target.

        Up moves run the workers' up() from current+1 to the target (included); down moves run the
        workers' down() from current to target+1 (the target excluded), then set current_step to the
        target explicitly (the down loop's last iteration leaves it at target+1). The current step
        is updated BEFORE each execution so the logs reflect the active worker.

        Args:
            target_index: The resolved 0-based target index.
        """
        if target_index == self.current_step:
            return

        if target_index > self.current_step:
            steps = range(self.current_step + 1, target_index + 1)
            direction = 'up'
        else:
            steps = range(self.current_step, target_index, -1)
            direction = 'down'

        for step_idx in steps:
            worker = self.workers[step_idx]
            # Update the current step BEFORE execution so logs reflect the active worker
            self.current_step = step_idx

            with self._history_timer(step_idx, worker.name, direction):
                self._run_step(worker, direction)

        # If we moved down, the final step is the target step (which is less than the last executed step_idx)
        if direction == 'down':
            self.current_step = target_index

    def move_to_last(self) -> None:
        """Moves the state machine to the last (higher) step."""
        last = self.workers[-1] if self.workers else None
        if last is not None:
            self.move_to_step(last.name)
