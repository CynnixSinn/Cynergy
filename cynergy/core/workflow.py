"""
Workflow engine for Cynergy that handles agent handoffs and pipeline execution
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import asyncio
import json
from .agent import Agent, Handoff, AgentState, Message, Tool, ToolCall, AgentResponse
from ..observe import get_tracer, Trace, TraceSpan


@dataclass
class WorkflowNode:
    """Represents a node in a workflow (an agent or task)"""
    id: str
    agent: Agent
    name: str
    type: str = "agent"  # Could be "agent", "conditional", "loop", etc.
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowEdge:
    """Represents an edge connecting two workflow nodes"""
    source_id: str
    target_id: str
    condition: Optional[str] = None  # Optional condition for conditional edges
    data_mapping: Optional[Dict[str, str]] = None  # How data flows from source to target


@dataclass
class Workflow:
    """Represents an entire workflow with nodes and edges"""
    id: str
    name: str
    description: str
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_node(self, node_id: str) -> Optional[WorkflowNode]:
        """Get a node by ID"""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None
    
    def get_outgoing_edges(self, node_id: str) -> List[WorkflowEdge]:
        """Get all edges that originate from a node"""
        return [edge for edge in self.edges if edge.source_id == node_id]
    
    def get_incoming_edges(self, node_id: str) -> List[WorkflowEdge]:
        """Get all edges that lead to a node"""
        return [edge for edge in self.edges if edge.target_id == node_id]


class WorkflowExecutor:
    """Executes workflows by managing handoffs between agents"""
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.tracer = get_tracer()
    
    def register_workflow(self, workflow: Workflow):
        """Register a workflow for execution"""
        self.workflows[workflow.id] = workflow
    
    def create_session(self, workflow_id: str, initial_input: Any) -> str:
        """Create a new execution session for a workflow"""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "workflow_id": workflow_id,
            "current_node_id": None,  # Will be set when execution starts
            "input_data": initial_input,
            "output_data": {},
            "execution_trace": [],
            "node_states": {},  # Track state of each node in the workflow
            "completed_nodes": set(),
            "start_time": datetime.now()
        }
        return session_id
    
    async def execute_workflow(self, session_id: str) -> Any:
        """Execute a workflow in a given session"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.active_sessions[session_id]
        workflow_id = session["workflow_id"]
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        start_node_id = workflow.nodes[0].id  # For now, start with the first node
        
        # Begin execution from the start node
        session["current_node_id"] = start_node_id
        result = await self._execute_node(session_id, start_node_id, session["input_data"])
        
        return result
    
    async def _execute_node(self, session_id: str, node_id: str, input_data: Any) -> Any:
        """Execute a single node in the workflow"""
        session = self.active_sessions[session_id]
        workflow = self.workflows[session["workflow_id"]]
        
        node = workflow.get_node(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found in workflow")
        
        # Add execution trace for this node
        trace_id = f"node_{node_id}_exec"
        span = self.tracer.start_span(
            name=f"execute_node_{node.id}",
            trace_id=session_id,
            parent_id=None  # This would be the main workflow trace
        )
        
        try:
            # Prepare input for the agent based on input_data and data mappings
            if isinstance(input_data, dict):
                agent_input = input_data.get("content", str(input_data))
            else:
                agent_input = str(input_data)
            
            # Run the agent with the input
            result = await node.agent.run(agent_input, context={"session_id": session_id})
            
            # Update session with the result
            session["output_data"][node_id] = result
            session["node_states"][node_id] = "completed"
            session["completed_nodes"].add(node_id)
            
            # Add result to trace
            span.attributes = {
                "node_id": node_id,
                "input": agent_input,
                "output": result,
                "agent_name": node.agent.name
            }
            
            # Check for handoff in the result
            if self._is_handoff_result(result):
                handoff_data = self._extract_handoff_data(result)
                return await self._handle_handoff(session_id, node_id, handoff_data)
            
            # Find next nodes based on outgoing edges
            next_edges = workflow.get_outgoing_edges(node_id)
            
            # If there are multiple outgoing edges, evaluate conditions
            if len(next_edges) == 1:
                # Simple path - no conditions to evaluate
                next_result = await self._execute_node(session_id, next_edges[0].target_id, result)
            elif len(next_edges) > 1:
                # Multiple paths - evaluate conditions
                next_result = await self._execute_conditional_paths(session_id, next_edges, result)
            else:
                # No more nodes to execute - workflow is complete
                next_result = result
            
            return next_result
            
        except Exception as e:
            # Mark node as failed and add to trace
            session["node_states"][node_id] = "failed"
            span.attributes = {
                "node_id": node_id,
                "error": str(e),
                "agent_name": node.agent.name
            }
            span.events.append({
                "name": "error",
                "timestamp": datetime.now(),
                "attributes": {"error": str(e)}
            })
            
            # Check if there's a fallback for this node
            fallback_edge = self._find_fallback_edge(workflow, node_id)
            if fallback_edge:
                return await self._execute_node(session_id, fallback_edge.target_id, input_data)
            else:
                raise e
        finally:
            self.tracer.end_span(span.id)
    
    def _is_handoff_result(self, result: str) -> bool:
        """Check if result indicates a handoff"""
        # Check if result contains handoff information
        return "Handoff to" in result and "with data:" in result
    
    def _extract_handoff_data(self, result: str) -> Dict[str, Any]:
        """Extract handoff data from result string (in a real system, this would be structured)"""
        # This is a simplified implementation - in a real system, handoff would be more structured
        return {"fallback": True}  # Placeholder
    
    async def _handle_handoff(self, session_id: str, current_node_id: str, handoff_data: Dict[str, Any]) -> Any:
        """Handle a handoff from one agent to another"""
        # In a real implementation, this would coordinate with the workflow's edge structure
        # For now, we'll just follow the next connected node in the workflow
        session = self.active_sessions[session_id]
        workflow = self.workflows[session["workflow_id"]]
        
        # Get the next node based on the handoff
        current_node = workflow.get_node(current_node_id)
        next_edges = workflow.get_outgoing_edges(current_node_id)
        
        if not next_edges:
            return f"Handoff: No next node found after {current_node_id}"
        
        # For now, execute the first connected node
        next_edge = next_edges[0]
        return await self._execute_node(session_id, next_edge.target_id, handoff_data)
    
    async def _execute_conditional_paths(self, session_id: str, edges: List[WorkflowEdge], input_data: Any) -> Any:
        """Execute conditional paths based on edge conditions"""
        session = self.active_sessions[session_id]
        results = []
        
        for edge in edges:
            # Evaluate condition (simplified for this example)
            # In a real system, this would be more sophisticated
            condition_met = True  # Default to true for now
            
            if condition_met or edge.condition is None:
                # Execute the target node
                result = await self._execute_node(session_id, edge.target_id, input_data)
                results.append(result)
        
        # For now, return the last result
        # In a real system, you might merge results or handle branching differently
        return results[-1] if results else input_data
    
    def _find_fallback_edge(self, workflow: Workflow, node_id: str) -> Optional[WorkflowEdge]:
        """Find a fallback edge for a given node"""
        # In a real system, fallback logic would be more sophisticated
        # For now, just return the first outgoing edge if it exists
        edges = workflow.get_outgoing_edges(node_id)
        return edges[0] if edges else None
    
    def get_execution_trace(self, session_id: str) -> List[Dict[str, Any]]:
        """Get the execution trace for a session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return []
        
        # In a real system, this would return the actual trace data
        # For now, we'll return what's in the tracer
        trace = self.tracer.get_trace(session_id)
        if trace:
            return json.loads(self.tracer.export_trace_json(session_id))
        return []
    
    async def simulate_workflow(self, workflow: Workflow, input_data: Any) -> Dict[str, Any]:
        """Simulate a workflow execution without actually calling external models"""
        # Create a special simulation session
        session_id = str(uuid.uuid4())
        
        # Create a mock tracer for simulation
        from ..observe import Tracer
        sim_tracer = Tracer()
        
        # Create mock agents with simulation behavior
        sim_agents = {}
        for node in workflow.nodes:
            # Create a simulation agent that mocks the real agent's behavior
            sim_agent = SimulationAgent(node.agent.name, node.agent.system_prompt)
            sim_agents[node.id] = sim_agent
        
        # Execute the workflow with simulation agents
        # This is a simplified simulation - in a real system, you'd run the full execution logic
        # but with mocked external dependencies
        
        results = {}
        for node in workflow.nodes:
            # Simulate the agent running
            result = f"[SIMULATION] Output from {node.agent.name}: Processing input '{input_data}'"
            results[node.id] = result
            
            # Add to trace
            span = sim_tracer.start_span(
                name=f"simulate_node_{node.id}",
                trace_id=session_id
            )
            span.attributes = {
                "node_id": node.id,
                "input": str(input_data),
                "output": result,
                "agent_name": node.agent.name
            }
            sim_tracer.end_span(span.id)
        
        # Export trace for simulation
        trace_data = json.loads(sim_tracer.export_trace_json(session_id)) if sim_tracer.get_trace(session_id) else {}
        
        return {
            "session_id": session_id,
            "results": results,
            "trace": trace_data,
            "completed": True
        }


class SimulationAgent:
    """A mock agent for simulation purposes"""
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
    
    async def run(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Simulate running an agent"""
        import random
        import time
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        # Return a mock response
        responses = [
            f"Processed '{prompt}' successfully",
            f"Analyzed input: {prompt[:50]}...",
            f"Handled request for: {prompt[:30]}",
            f"Completed task: {prompt[:20]}"
        ]
        return random.choice(responses)


# Global workflow executor instance
workflow_executor = WorkflowExecutor()


def get_workflow_executor() -> WorkflowExecutor:
    """Get the global workflow executor instance"""
    return workflow_executor