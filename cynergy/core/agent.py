"""
Cynergy Core - Agent Base Class with handoff support
"""
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    COMPLETED = "completed"
    ERROR = "error"
    EXECUTING = "executing"
    WAITING = "waiting"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolCall:
    tool_name: str
    arguments: Dict[str, Any]
    call_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    result: Optional[Any] = None
    error: Optional[str] = None


@dataclass
class AgentResponse:
    content: str
    tool_calls: List[ToolCall] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Handoff:
    """Represents a handoff from one agent to another"""
    def __init__(
        self,
        target_agent: str,
        data: Dict[str, Any],
        condition: Optional[str] = None,
        fallback_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.target_agent = target_agent
        self.data = data
        self.condition = condition  # Optional condition for dynamic routing
        self.fallback_agent = fallback_agent
        self.metadata = metadata or {}
        self.id = str(uuid.uuid4())


class Tool:
    def __init__(self, name: str, description: str, func: Callable, 
                 parameters: Optional[Dict] = None):
        self.name = name
        self.description = description
        self.func = func
        self.parameters = parameters or {}

    def __call__(self, **kwargs):
        return self.func(**kwargs)


class Memory:
    def __init__(self, max_turns: int = 50):
        self.messages: List[Message] = []
        self.max_turns = max_turns

    def add(self, message: Message):
        self.messages.append(message)
        if len(self.messages) > self.max_turns * 2:
            system_msgs = [m for m in self.messages if m.role == "system"]
            recent = self.messages[-(self.max_turns * 2):]
            self.messages = system_msgs + recent

    def get_context(self) -> List[Message]:
        return self.messages

    def clear(self):
        self.messages = []


class Agent:
    def __init__(
        self,
        name: str,
        model: Any,
        tools: Optional[List[Tool]] = None,
        system_prompt: Optional[str] = None,
        memory: Optional[Union[Memory, 'cynergy.memory.memory_manager.MemoryManager']] = None,
        max_iterations: int = 10,
        self_healing: bool = True,
        max_retries: int = 3,
        tracer: Optional[Any] = None,
        metrics: Optional[Any] = None
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.model = model
        self.tools = {tool.name: tool for tool in (tools or [])}
        self.system_prompt = system_prompt or "You are a helpful AI assistant."
        
        # Use provided memory or create a default one
        if memory is None:
            # Try to import the enhanced memory manager
            try:
                from cynergy.memory.memory_manager import MemoryManager
                self.memory = MemoryManager()
            except ImportError:
                # Fall back to old memory if enhanced memory is not available
                self.memory = Memory()
        else:
            self.memory = memory
            
        self.max_iterations = max_iterations
        self.self_healing = self_healing
        self.max_retries = max_retries
        self.tracer = tracer
        self.metrics = metrics
        self.state = AgentState.IDLE
        self._iteration_count = 0

        # Add system prompt to memory based on type
        if hasattr(self.memory, 'add_message'):
            # Use enhanced memory
            self.memory.add_message(Message(role="system", content=self.system_prompt))
        else:
            # Use old memory
            self.memory.add(Message(role="system", content=self.system_prompt))

    async def run(self, prompt: str, context: Optional[Dict] = None) -> str:
        # Create a message for the prompt
        user_msg = Message(role="user", content=prompt, metadata=context or {})
        
        # Add message to memory based on type
        if hasattr(self.memory, 'add_message'):
            self.memory.add_message(user_msg)
        else:
            self.memory.add(user_msg)

        self.state = AgentState.THINKING
        self._iteration_count = 0

        while self._iteration_count < self.max_iterations:
            self._iteration_count += 1

            response = await self._generate_response()

            if not response.tool_calls:
                # Add assistant response to memory
                assistant_msg = Message(role="assistant", content=response.content)
                if hasattr(self.memory, 'add_message'):
                    self.memory.add_message(assistant_msg)
                else:
                    self.memory.add(assistant_msg)
                    
                self.state = AgentState.COMPLETED
                return response.content

            # Check for handoff tool calls
            handoff = None
            for tool_call in response.tool_calls:
                if tool_call.tool_name == "handoff":
                    # Extract handoff information from the tool call
                    handoff_data = tool_call.arguments
                    handoff = Handoff(
                        target_agent=handoff_data.get("target_agent"),
                        data=handoff_data.get("data", {}),
                        condition=handoff_data.get("condition"),
                        fallback_agent=handoff_data.get("fallback_agent")
                    )
                    break

            if handoff:
                # This agent wants to hand off to another agent
                return await self.handle_handoff(handoff)
            
            self.state = AgentState.ACTING
            await self._execute_tools(response.tool_calls)
            self.state = AgentState.THINKING

        return "Reached maximum iterations."

    async def _generate_response(self) -> AgentResponse:
        # Get context messages based on memory type
        if hasattr(self.memory, 'get_context_messages'):
            # Enhanced memory
            messages = self.memory.get_context_messages()
        else:
            # Old memory
            messages = self.memory.get_context()
        tools = list(self.tools.values()) if self.tools else None
        return await self.model.generate(messages, tools=tools)

    async def _execute_tools(self, tool_calls: List[ToolCall]):
        for tool_call in tool_calls:
            tool = self.tools.get(tool_call.tool_name)
            if not tool:
                tool_call.error = f"Tool {tool_call.tool_name} not found"
                continue

            try:
                if asyncio.iscoroutinefunction(tool.func):
                    result = await tool(**tool_call.arguments)
                else:
                    result = tool(**tool_call.arguments)

                tool_call.result = result
                
                # Add tool result to memory
                tool_result_msg = Message(
                    role="tool",
                    content=json.dumps({"result": result}),
                    metadata={"tool": tool_call.tool_name}
                )
                
                if hasattr(self.memory, 'add_message'):
                    self.memory.add_message(tool_result_msg)
                else:
                    self.memory.add(tool_result_msg)
            except Exception as e:
                tool_call.error = str(e)
                logger.error(f"Error executing tool {tool_call.tool_name}: {e}")

    def add_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def reset(self):
        if hasattr(self.memory, 'clear_all'):
            self.memory.clear_all()
        else:
            self.memory.clear()
        self.state = AgentState.IDLE
        self._iteration_count = 0
        
        # Add system prompt back to memory
        system_msg = Message(role="system", content=self.system_prompt)
        if hasattr(self.memory, 'add_message'):
            self.memory.add_message(system_msg)
        else:
            self.memory.add(Message(role="system", content=self.system_prompt))

    async def handle_handoff(self, handoff: Handoff) -> str:
        """Handle handoff to another agent (to be implemented by workflow engine)"""
        # This method will be overridden or supplemented by the workflow engine
        return f"Handoff to {handoff.target_agent} with data: {handoff.data}"


def tool(name: Optional[str] = None, description: Optional[str] = None):
    def decorator(func: Callable) -> Tool:
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or f"Execute {tool_name}"
        return Tool(name=tool_name, description=tool_desc, func=func)
    return decorator