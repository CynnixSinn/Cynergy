"""
Data models for the Cynergy Studio API
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class NodeType(str, Enum):
    AGENT = "agent"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    TASK = "task"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class NodeData:
    """Data for a workflow node"""
    id: str
    type: NodeType
    name: str
    agent_config: Optional[Dict[str, Any]] = None  # Agent-specific configuration
    position_x: float = 0.0
    position_y: float = 0.0
    parameters: Optional[Dict[str, Any]] = None


@dataclass
class EdgeData:
    """Data for a workflow edge"""
    id: str
    source_id: str
    target_id: str
    condition: Optional[str] = None  # Optional condition for conditional edges
    label: Optional[str] = None


@dataclass
class WorkflowManifest:
    """Workflow manifest that can be saved and executed"""
    id: str
    name: str
    description: str
    nodes: List[NodeData]
    edges: List[EdgeData]
    version: str = "1.0"
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class WorkflowVersion:
    """A version of a workflow"""
    id: str
    workflow_id: str
    version_number: str
    manifest: WorkflowManifest
    created_at: datetime = field(default_factory=datetime.now)
    author: str = "system"


@dataclass
class SimulationRequest:
    """Request for workflow simulation"""
    workflow_id: str
    input_data: Dict[str, Any]
    simulate_tracing: bool = True


@dataclass
class SimulationResponse:
    """Response from workflow simulation"""
    session_id: str
    status: str
    results: Dict[str, Any]
    trace: Dict[str, Any]
    completed: bool


@dataclass
class ExecutionRequest:
    """Request for workflow execution"""
    workflow_id: str
    input_data: Dict[str, Any]
    execute_tracing: bool = True


@dataclass
class ExecutionResponse:
    """Response from workflow execution"""
    session_id: str
    status: str
    results: Dict[str, Any]
    trace: Dict[str, Any]
    completed: bool


@dataclass
class TraceInfo:
    """Information about a workflow execution trace"""
    session_id: str
    workflow_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    nodes_executed: List[str] = field(default_factory=list)
    error: Optional[str] = None