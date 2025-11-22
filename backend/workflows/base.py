"""
Base Workflow Infrastructure

Provides the foundation for composable, multi-step workflows.
Adapted from writers-factory-core.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Single step in a workflow."""

    name: str
    func: Callable
    kwargs: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[Exception] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    @property
    def duration_ms(self) -> Optional[float]:
        """Duration in milliseconds if completed."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None

    @property
    def status(self) -> str:
        if self.error:
            return "failed"
        if self.result is not None:
            return "completed"
        if self.started_at:
            return "running"
        return "pending"

    async def execute(self, context: Dict[str, Any]) -> Any:
        """Execute this step with the given context."""
        self.started_at = datetime.now(timezone.utc)
        try:
            self.result = await self.func(context, **self.kwargs)
            self.completed_at = datetime.now(timezone.utc)
            return self.result
        except Exception as e:
            self.error = e
            self.completed_at = datetime.now(timezone.utc)
            raise


@dataclass
class WorkflowResult:
    """Container for workflow execution results."""

    workflow_name: str
    success: bool
    steps: List[WorkflowStep]
    final_result: Any = None
    context: Dict[str, Any] = field(default_factory=dict)
    total_duration_ms: float = 0.0
    error: Optional[str] = None

    def get_step_result(self, step_name: str) -> Optional[Any]:
        """Get result from a specific step."""
        for step in self.steps:
            if step.name == step_name:
                return step.result
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            'workflow': self.workflow_name,
            'success': self.success,
            'duration_ms': self.total_duration_ms,
            'error': self.error,
            'steps': [
                {
                    'name': s.name,
                    'status': s.status,
                    'duration_ms': s.duration_ms,
                    'error': str(s.error) if s.error else None,
                }
                for s in self.steps
            ],
            'final_result': self.final_result,
        }


class Workflow(ABC):
    """
    Base class for all workflows.

    Workflows are composable, multi-step processes that:
    - Execute steps in sequence
    - Pass context between steps
    - Track progress and timing
    - Handle errors gracefully
    """

    def __init__(self):
        self.steps: List[WorkflowStep] = []
        self.context: Dict[str, Any] = {}
        self._progress_callback: Optional[Callable[[int, int, str], None]] = None

    def add_step(
        self,
        name: str,
        func: Callable,
        **kwargs
    ) -> "Workflow":
        """
        Add a step to the workflow.

        The function should be async and accept (context, **kwargs).
        """
        step = WorkflowStep(name=name, func=func, kwargs=kwargs)
        self.steps.append(step)
        return self

    def on_progress(self, callback: Callable[[int, int, str], None]) -> "Workflow":
        """
        Set progress callback: callback(current_step, total_steps, step_name)
        """
        self._progress_callback = callback
        return self

    async def execute(
        self,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> WorkflowResult:
        """
        Execute all steps in sequence.

        Returns WorkflowResult with all step results and final output.
        """
        start_time = datetime.now(timezone.utc)

        if initial_context:
            self.context.update(initial_context)

        total_steps = len(self.steps)
        error_msg = None

        for i, step in enumerate(self.steps):
            # Update progress
            if self._progress_callback:
                self._progress_callback(i + 1, total_steps, step.name)

            logger.info(f"[{self.__class__.__name__}] Step {i+1}/{total_steps}: {step.name}")

            try:
                result = await step.execute(self.context)
                # Add result to context for next steps
                self.context[f"step_{i}_result"] = result
                self.context[step.name.lower().replace(' ', '_')] = result
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Failed at step '{step.name}': {e}")
                error_msg = f"Step '{step.name}' failed: {str(e)}"
                break

        end_time = datetime.now(timezone.utc)
        duration_ms = (end_time - start_time).total_seconds() * 1000

        # Get final result from last successful step
        final_result = None
        for step in reversed(self.steps):
            if step.result is not None:
                final_result = step.result
                break

        return WorkflowResult(
            workflow_name=self.__class__.__name__,
            success=error_msg is None,
            steps=self.steps,
            final_result=final_result,
            context=self.context,
            total_duration_ms=duration_ms,
            error=error_msg,
        )

    @abstractmethod
    async def run(self, **kwargs) -> WorkflowResult:
        """
        Main entry point for the workflow.

        Subclasses should implement this to:
        1. Add steps with add_step()
        2. Call execute() with initial context
        3. Return the WorkflowResult
        """
        pass

    def reset(self) -> "Workflow":
        """Reset workflow for re-execution."""
        self.steps = []
        self.context = {}
        return self
