"""
# Complete Guide to Building AI Agents with Cynergy

This comprehensive guide demonstrates all aspects of building AI agents using the Cynergy framework.

## What You'll Learn

1. **Model Options**: Different AI models you can use with Cynergy
2. **Tools**: How to use and create tools for your agents
3. **Memory**: Advanced memory management capabilities
4. **Workflows**: Orchestration of multi-agent workflows
5. **Complete Examples**: Practical implementations

## File Structure

- `building_agents_with_cynergy.py` - Comprehensive overview
- `model_options_demo.py` - Different model options (Qwen, OpenAI, Ollama, etc.)
- `tools_demo.py` - Using and creating tools
- `memory_demo.py` - Memory management features
- `workflow_demo.py` - Workflow orchestration

## Getting Started

To run any of the examples:

```bash
# Run the comprehensive example
python building_agents_with_cynergy.py

# Run specific demos
python model_options_demo.py
python tools_demo.py
python memory_demo.py
python workflow_demo.py
```

## Key Features of Cynergy

### 1. Multi-Model Support
- **Qwen (Free)**: Access to Qwen models via OpenRouter (free tier)
- **OpenAI**: GPT models for advanced reasoning
- **Anthropic**: Claude models for analysis
- **Ollama**: Local models for privacy
- **Multi-Provider**: Fallback strategies

### 2. Advanced Memory System
- **Conversation Memory**: Dialogue history with compression
- **Episodic Memory**: Event storage with tags
- **Semantic Memory**: Knowledge retrieval
- **Working Memory**: Short-term storage with TTL

### 3. Comprehensive Tool Ecosystem
- Pre-built tools: file operations, code execution, calculations
- Custom tool creation with @tool decorator
- Tool integration with agents
- JSON schema generation

### 4. Workflow Orchestration
- Multi-agent workflows
- Task dependencies
- Parallel execution
- State management
- Conditional logic

## Example Use Cases

### Simple Agent
```python
from cynergy import Agent, QwenModel

# Create a simple agent
agent = Agent(
    name="MyAssistant", 
    model=QwenModel(),  # Free Qwen model
    system_prompt="You are a helpful assistant"
)

# Run the agent
response = await agent.run("Explain quantum computing in simple terms")
```

### Agent with Tools
```python
from cynergy import tool_registry

# Add pre-built tools
agent.add_tool(tool_registry.get_tool("calculate"))
agent.add_tool(tool_registry.get_tool("execute_python"))

# Or create custom tools
@tool(name="weather_check", description="Check weather for a location")
def weather_check(location: str):
    # Implementation here
    pass

agent.add_tool(weather_check)
```

### Agent with Enhanced Memory
```python
from cynergy import MemoryManager

# Configure memory
memory_config = {
    "conversation": {"max_turns": 100, "compression_enabled": True},
    "working": {"ttl": 600}  # 10 minute TTL
}
memory_manager = MemoryManager(config=memory_config)

# Create agent with enhanced memory
agent = Agent(
    name="MemoryAgent",
    model=QwenModel(),
    memory=memory_manager
)
```

### Multi-Agent Workflow
```python
from cynergy import WorkflowOrchestrator, WorkflowTask

# Create orchestrator and agents
orchestrator = WorkflowOrchestrator()
orchestrator.register_agent(agent1)
orchestrator.register_agent(agent2)

# Define tasks with dependencies
tasks = [
    WorkflowTask(
        name="task1",
        agent_name="Agent1",
        input_data={"prompt": "Do initial analysis"}
    ),
    WorkflowTask(
        name="task2", 
        agent_name="Agent2",
        input_data={"prompt": "Build on analysis"},
        dependencies=["task1"]  # Depends on task1
    )
]

# Create and execute workflow
workflow = orchestrator.create_workflow("My Workflow", tasks)
```

## Environment Setup

For full functionality, set up these environment variables:

```bash
# For OpenRouter models (including free Qwen)
export OPENROUTER_API_KEY='your-api-key'

# For OpenAI models
export OPENAI_API_KEY='your-api-key'

# For Anthropic models
export ANTHROPIC_API_KEY='your-api-key'
```

Get your API keys from:
- OpenRouter: https://openrouter.ai/keys
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/settings/keys

For local models, install Ollama: https://ollama.ai

## Next Steps

1. Explore the individual demo files for detailed examples
2. Experiment with different model providers
3. Build custom tools for your specific use case
4. Create complex multi-agent workflows
5. Implement your own specialized agents

The Cynergy framework provides a complete platform for building sophisticated AI agents with minimal code!
"""