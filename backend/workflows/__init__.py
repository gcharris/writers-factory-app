"""
Workflows Module

Pre-built workflows that automate complex multi-step operations.
Ported from writers-factory-core and adapted for desktop app.
"""

from .base import Workflow, WorkflowStep, WorkflowResult
from .smart_scaffold import SmartScaffoldWorkflow

__all__ = [
    'Workflow',
    'WorkflowStep',
    'WorkflowResult',
    'SmartScaffoldWorkflow',
]
