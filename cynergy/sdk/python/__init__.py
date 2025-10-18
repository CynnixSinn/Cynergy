"""
Enhanced Cynergy Python SDK combining features from both versions
"""
from typing import Dict, Any, Optional, List, Callable
import asyncio
from cynergy.core.agent import Agent as CoreAgent, Tool as CoreTool
from cynergy.core import Memory
from cynergy.security import PolicyEngine
from cynergy.connect import BaseConnector
from cynergy.observe import get_tracer


class Agent:
    """Enhanced high-level agent interface with features from both versions"""
    
    def __init__(self, name: str, model: Any, tools: Optional[List[CoreTool]] = None,
                 system_prompt: Optional[str] = None, memory: Optional[Memory] = None,
                 policy_engine: Optional[PolicyEngine] = None, 
                 max_iterations: int = 10):
        self.name = name
        self.model = model
        self.core_agent = CoreAgent(
            name=name,
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            memory=memory,
            max_iterations=max_iterations,
            tracer=get_tracer()
        )
        self.policy_engine = policy_engine
    
    async def run(self, prompt: str, context: Optional[Dict] = None) -> str:
        """Run the agent with user input"""
        # Apply policy check if policy engine is available
        if self.policy_engine:
            policy_context = {"agent_id": self.name, "operation": prompt}
            policy_result = await self.policy_engine.evaluate(policy_context)
            if not policy_result.allowed:
                return f"Operation blocked by policy: {policy_result.reason}"
        
        return await self.core_agent.run(prompt, context)
    
    def add_tool(self, tool: CoreTool):
        """Add a tool that the agent can use"""
        self.core_agent.add_tool(tool)
    
    def add_connector(self, connector: BaseConnector):
        """Add a connector to the agent"""
        # Convert connector to a tool and register it
        tool = connector.to_tool()
        self.add_tool(tool)
    
    def reset(self):
        """Reset the agent's memory and state"""
        self.core_agent.reset()


class Tool(CoreTool):
    """Enhanced SDK wrapper for tools"""
    pass


def create_agent(name: str, model: Any, initial_context: Optional[Dict[str, Any]] = None) -> Agent:
    """Factory function to create a new agent with modern API"""
    agent = Agent(name=name, model=model)
    return agent


__all__ = ["Agent", "Tool", "create_agent"]