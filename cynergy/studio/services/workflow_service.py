"""
Services for the Cynergy Studio API
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json
import yaml
from cynergy.studio.models.workflow import (
    WorkflowManifest, NodeData, EdgeData, WorkflowVersion, 
    SimulationRequest, SimulationResponse, ExecutionRequest, ExecutionResponse, TraceInfo
)
from cynergy.core.workflow import get_workflow_executor, Workflow as CoreWorkflow, WorkflowNode, WorkflowEdge


class WorkflowService:
    """Service for managing workflows"""
    
    def __init__(self):
        self.executor = get_workflow_executor()
        self.workflows: Dict[str, WorkflowManifest] = {}
        self.versions: Dict[str, List[WorkflowVersion]] = {}
        self.traces: Dict[str, TraceInfo] = {}
    
    def list_workflows(self) -> List[WorkflowManifest]:
        """List all workflows"""
        return list(self.workflows.values())
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowManifest]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def save_workflow(self, manifest: WorkflowManifest) -> WorkflowManifest:
        """Save or update a workflow"""
        # Update the timestamp
        manifest.updated_at = datetime.now()
        
        # Add to our registry
        self.workflows[manifest.id] = manifest
        
        # Create a version
        version = WorkflowVersion(
            id=str(uuid.uuid4()),
            workflow_id=manifest.id,
            version_number=manifest.version,
            manifest=manifest
        )
        if manifest.id not in self.versions:
            self.versions[manifest.id] = []
        self.versions[manifest.id].append(version)
        
        # Register with the core executor
        core_workflow = self._convert_to_core_workflow(manifest)
        self.executor.register_workflow(core_workflow)
        
        return manifest
    
    def get_workflow_versions(self, workflow_id: str) -> List[WorkflowVersion]:
        """Get all versions of a workflow"""
        return self.versions.get(workflow_id, [])
    
    def get_workflow_version(self, workflow_id: str, version_number: str) -> Optional[WorkflowVersion]:
        """Get a specific version of a workflow"""
        versions = self.versions.get(workflow_id, [])
        for version in versions:
            if version.version_number == version_number:
                return version
        return None
    
    def revert_to_version(self, workflow_id: str, version_number: str) -> Optional[WorkflowManifest]:
        """Revert a workflow to a specific version"""
        version = self.get_workflow_version(workflow_id, version_number)
        if not version:
            return None
        
        # Update the current workflow to match this version
        manifest = version.manifest
        self.workflows[workflow_id] = manifest
        
        # Update the executor
        core_workflow = self._convert_to_core_workflow(manifest)
        self.executor.register_workflow(core_workflow)
        
        return manifest
    
    def simulate_workflow(self, request: SimulationRequest) -> SimulationResponse:
        """Simulate a workflow execution"""
        workflow = self.get_workflow(request.workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {request.workflow_id} not found")
        
        # Convert workflow to core workflow
        core_workflow = self._convert_to_core_workflow(workflow)
        
        # Run simulation
        import asyncio
        try:
            # Run the simulation (this might need to be adapted based on how the executor works)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            simulation_result = loop.run_until_complete(
                self.executor.simulate_workflow(core_workflow, request.input_data)
            )
            loop.close()
        except RuntimeError:
            # If there's already a running loop, create a new thread
            import threading
            from concurrent.futures import ThreadPoolExecutor
            
            def run_simulation():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.executor.simulate_workflow(core_workflow, request.input_data)
                )
                loop.close()
                return result
            
            with ThreadPoolExecutor() as executor:
                simulation_result = executor.submit(run_simulation).result()
        
        return SimulationResponse(**simulation_result)
    
    def execute_workflow(self, request: ExecutionRequest) -> ExecutionResponse:
        """Execute a workflow"""
        # Create a session for execution
        session_id = self.executor.create_session(request.workflow_id, request.input_data)
        
        # Execute the workflow asynchronously
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.executor.execute_workflow(session_id))
            loop.close()
        except RuntimeError:
            # If there's already a running loop, create a new thread
            import threading
            from concurrent.futures import ThreadPoolExecutor
            
            def run_execution():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    self.executor.execute_workflow(session_id)
                )
                loop.close()
                return result
            
            with ThreadPoolExecutor() as executor:
                result = executor.submit(run_execution).result()
        
        # Get trace information
        trace = self.executor.get_execution_trace(session_id)
        
        return ExecutionResponse(
            session_id=session_id,
            status="completed",
            results={"result": result},
            trace=trace,
            completed=True
        )
    
    def get_trace(self, session_id: str) -> Optional[TraceInfo]:
        """Get trace information for a session"""
        return self.traces.get(session_id)
    
    def _convert_to_core_workflow(self, manifest: WorkflowManifest) -> CoreWorkflow:
        """Convert a manifest workflow to a core workflow"""
        from cynergy.core.agent import Agent, Tool
        from cynergy.sdk.python.cynergy.models import OpenAIModel  # Just for demo; in real use, would be more flexible
        
        # Create core workflow nodes and edges
        core_nodes = []
        for node_data in manifest.nodes:
            # Create a mock agent for the node (in a real implementation, you'd use actual agent configs)
            mock_model = MockModel("gpt-3.5-turbo")  # Using mock model for now
            agent = Agent(
                name=node_data.name,
                model=mock_model
            )
            
            core_node = WorkflowNode(
                id=node_data.id,
                agent=agent,
                name=node_data.name,
                type=node_data.type.value,
                config=node_data.agent_config or {}
            )
            core_nodes.append(core_node)
        
        core_edges = []
        for edge_data in manifest.edges:
            core_edge = WorkflowEdge(
                source_id=edge_data.source_id,
                target_id=edge_data.target_id,
                condition=edge_data.condition,
                data_mapping=None  # Would be implemented based on actual requirements
            )
            core_edges.append(core_edge)
        
        # Create the core workflow
        core_workflow = CoreWorkflow(
            id=manifest.id,
            name=manifest.name,
            description=manifest.description,
            nodes=core_nodes,
            edges=core_edges,
            version=manifest.version
        )
        
        return core_workflow


class MockModel:
    """Mock model for demonstration purposes"""
    def __init__(self, model_name: str):
        self.model_name = model_name
    
    async def generate(self, messages, tools=None):
        from cynergy.core.agent import AgentResponse
        # Just return a mock response
        return AgentResponse(content=f"Mock response from {self.model_name}")


# Global workflow service instance
workflow_service = WorkflowService()


def get_workflow_service() -> WorkflowService:
    """Get the global workflow service instance"""
    return workflow_service