"""Workflow orchestration for Cynergy agents"""
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio
import json
from uuid import uuid4

from cynergy.core.agent import Agent, Message, AgentResponse, tool
from cynergy.memory.memory_manager import MemoryManager


class WorkflowStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowTask:
    """A task within a workflow"""
    id: str
    name: str
    agent_name: str
    input_data: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)  # Task IDs this task depends on
    timeout: Optional[int] = None  # Timeout in seconds
    retry_count: int = 0
    max_retries: int = 3
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "agent_name": self.agent_name,
            "input_data": self.input_data,
            "dependencies": self.dependencies,
            "timeout": self.timeout,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


@dataclass
class Workflow:
    """A complete workflow with multiple tasks"""
    id: str
    name: str
    tasks: List[WorkflowTask] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: WorkflowTask):
        """Add a task to the workflow"""
        self.tasks.append(task)

    def get_ready_tasks(self) -> List[WorkflowTask]:
        """Get tasks that are ready to run (dependencies satisfied)"""
        ready_tasks = []
        completed_task_ids = {task.id for task in self.tasks if task.status == TaskStatus.COMPLETED}
        
        for task in self.tasks:
            if task.status != TaskStatus.PENDING:
                continue
                
            # Check if all dependencies are completed
            if all(dep in completed_task_ids for dep in task.dependencies):
                ready_tasks.append(task)
        
        return ready_tasks

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tasks": [task.to_dict() for task in self.tasks],
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result,
            "error": self.error,
            "metadata": self.metadata
        }


class AgentRegistry:
    """Registry for managing agents in workflows"""
    def __init__(self):
        self.agents: Dict[str, Agent] = {}

    def register_agent(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(name)

    def get_all_agent_names(self) -> List[str]:
        """Get all registered agent names"""
        return list(self.agents.keys())


class WorkflowOrchestrator:
    """Main orchestrator for executing workflows"""
    def __init__(self):
        self.agent_registry = AgentRegistry()
        self.workflows: Dict[str, Workflow] = {}
        self.running_workflows: Dict[str, asyncio.Task] = {}

    def register_agent(self, agent: Agent):
        """Register an agent with the orchestrator"""
        self.agent_registry.register_agent(agent)

    async def execute_task(self, task: WorkflowTask, agent: Agent) -> WorkflowTask:
        """Execute a single task"""
        task.status = TaskStatus.RUNNING
        task.start_time = datetime.now()

        try:
            if task.timeout:
                response = await asyncio.wait_for(
                    agent.run(json.dumps(task.input_data)),
                    timeout=task.timeout
                )
            else:
                response = await agent.run(json.dumps(task.input_data))

            task.result = {"output": response, "status": "success"}
            task.status = TaskStatus.COMPLETED
        except asyncio.TimeoutError:
            task.error = f"Task timed out after {task.timeout} seconds"
            task.status = TaskStatus.FAILED
            
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                # Schedule retry after a delay
                await asyncio.sleep(1)  # Wait 1 second before retry
                return await self.execute_task(task, agent)
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                # Schedule retry after a delay
                await asyncio.sleep(1)  # Wait 1 second before retry
                return await self.execute_task(task, agent)

        task.end_time = datetime.now()
        return task

    async def execute_workflow(self, workflow_id: str) -> Workflow:
        """Execute a complete workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()

        try:
            # Execute tasks until all are completed or failed
            while any(task.status in [TaskStatus.PENDING, TaskStatus.RUNNING] for task in workflow.tasks):
                ready_tasks = workflow.get_ready_tasks()
                
                if not ready_tasks:
                    # Check if there are still running tasks
                    running_tasks = [t for t in workflow.tasks if t.status == TaskStatus.RUNNING]
                    if not running_tasks:
                        # No ready tasks and no running tasks means we have a cycle or failed tasks
                        remaining_pending = [t for t in workflow.tasks if t.status == TaskStatus.PENDING]
                        if remaining_pending:
                            raise Exception(f"Workflow has circular dependencies or unsatisfiable dependencies: {[t.id for t in remaining_pending]}")
                        break
                    
                    # Wait for running tasks to complete
                    await asyncio.sleep(0.1)
                    continue

                # Execute all ready tasks concurrently
                tasks_to_execute = []
                for task in ready_tasks:
                    agent = self.agent_registry.get_agent(task.agent_name)
                    if not agent:
                        task.status = TaskStatus.FAILED
                        task.error = f"Agent {task.agent_name} not found"
                        continue

                    tasks_to_execute.append(self.execute_task(task, agent))

                if tasks_to_execute:
                    await asyncio.gather(*tasks_to_execute, return_exceptions=True)

            # Check if workflow completed successfully
            failed_tasks = [t for t in workflow.tasks if t.status == TaskStatus.FAILED]
            if failed_tasks:
                workflow.status = WorkflowStatus.FAILED
                workflow.error = f"Workflow failed with {len(failed_tasks)} failed tasks"
            else:
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now()
                workflow.result = {
                    "tasks": {t.id: t.result for t in workflow.tasks},
                    "summary": f"Workflow completed successfully with {len(workflow.tasks)} tasks"
                }

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)

        return workflow

    def create_workflow(self, name: str, tasks: List[WorkflowTask], metadata: Optional[Dict[str, Any]] = None) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            id=str(uuid4()),
            name=name,
            tasks=tasks,
            metadata=metadata or {}
        )
        self.workflows[workflow.id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)

    def list_workflows(self) -> List[Workflow]:
        """List all workflows"""
        return list(self.workflows.values())

    def cancel_workflow(self, workflow_id: str):
        """Cancel a running workflow"""
        if workflow_id in self.running_workflows:
            task = self.running_workflows[workflow_id]
            task.cancel()
            del self.running_workflows[workflow_id]

            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.FAILED
            workflow.error = "Workflow cancelled by user"

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status summary of a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return None

        task_statuses = [task.status.value for task in workflow.tasks]
        status_counts = {
            "pending": task_statuses.count("pending"),
            "running": task_statuses.count("running"),
            "completed": task_statuses.count("completed"),
            "failed": task_statuses.count("failed"),
        }

        return {
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "tasks": status_counts,
            "error": workflow.error
        }


# Enhanced workflow tools
@tool(name="create_workflow", description="Create a new workflow with tasks")
def create_workflow(name: str, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a workflow from task definitions"""
    try:
        workflow_tasks = []
        for task_def in tasks:
            task = WorkflowTask(
                id=task_def.get("id", str(uuid4())),
                name=task_def["name"],
                agent_name=task_def["agent_name"],
                input_data=task_def.get("input_data", {}),
                dependencies=task_def.get("dependencies", []),
                timeout=task_def.get("timeout"),
                max_retries=task_def.get("max_retries", 3)
            )
            workflow_tasks.append(task)

        # Get global orchestrator instance (in a real implementation, you'd have access to it)
        # For now, we'll create a temporary orchestrator
        temp_orchestrator = WorkflowOrchestrator()
        workflow = temp_orchestrator.create_workflow(name, workflow_tasks)
        
        return {
            "success": True,
            "workflow_id": workflow.id,
            "name": workflow.name,
            "task_count": len(workflow.tasks),
            "message": f"Created workflow '{name}' with {len(workflow.tasks)} tasks"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create workflow"
        }


@tool(name="execute_workflow", description="Execute a workflow by ID")
def execute_workflow(workflow_id: str) -> Dict[str, Any]:
    """Execute a workflow by its ID"""
    # This would need access to the global orchestrator instance
    # For this example, we'll return an appropriate message
    return {
        "success": False,
        "error": "Workflow execution requires access to the global orchestrator instance",
        "workflow_id": workflow_id,
        "message": "In a real implementation, this tool would execute the workflow"
    }


@tool(name="get_workflow_status", description="Get the status of a workflow")
def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """Get the status of a workflow"""
    # This would need access to the global orchestrator instance
    return {
        "success": False,
        "error": "Workflow status requires access to the global orchestrator instance",
        "workflow_id": workflow_id,
        "message": "In a real implementation, this tool would return the workflow status"
    }


# Add the orchestrator to a global variable so it can be accessed
global_orchestrator = WorkflowOrchestrator()