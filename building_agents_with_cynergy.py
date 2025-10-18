"""
# Building AI Agents with Cynergy Framework

This comprehensive example demonstrates how to build powerful AI agents using the Cynergy framework.
The Cynergy framework provides advanced capabilities for creating agentic AI applications.

## Key Features of Cynergy:
1. Multi-model support (OpenRouter, OpenAI, Anthropic, Ollama, etc.)
2. Enhanced memory management (conversation, episodic, semantic, working)
3. Comprehensive tool ecosystem
4. Workflow orchestration
5. Security policies and rate limiting
6. Tracing and observability
"""

import asyncio
import os
from typing import Dict, Any

# Import core components from Cynergy
from cynergy import (
    Agent,           # Core agent class
    QwenModel,       # Qwen model via OpenRouter (free tier)
    OpenAIModel,     # OpenAI models
    OllamaModel,     # Local Ollama models
    MultiProviderModel,  # Model that switches between providers
    MemoryManager,   # Enhanced memory management
    tool,            # Tool decorator
    tool_registry    # Registry of pre-built tools
)

# Example 1: Simple Agent with Qwen (Free Model)
async def create_simple_qwen_agent():
    """
    Create a simple agent using the free Qwen model from OpenRouter.
    This is great for getting started without API costs.
    """
    print("🚀 Creating a simple Qwen agent...")
    
    # Create a Qwen model using OpenRouter (free tier)
    # You'll need an OpenRouter API key for this: https://openrouter.ai/keys
    try:
        qwen_model = QwenModel(model="qwen/qwen-3.5-coder:free")
        agent = Agent(
            name="QwenAssistant",
            model=qwen_model,
            system_prompt="You are Qwen, an expert AI coding assistant. Provide concise, helpful responses with examples when needed."
        )
        
        # Test the agent
        response = await agent.run("What is the fibonacci sequence and how can it be implemented efficiently in Python?")
        print(f"Qwen Response: {response[:200]}...")
        
        return agent
    except ValueError as e:
        print(f"⚠️  API key issue: {e}")
        print("💡 To use Qwen, set OPENROUTER_API_KEY environment variable.")
        return None


# Example 2: Agent with Enhanced Memory Management
async def create_memory_enhanced_agent():
    """
    Create an agent with advanced memory management capabilities.
    This includes conversation, episodic, semantic, and working memory.
    """
    print("\n🧠 Creating an agent with enhanced memory...")
    
    # Configure memory with custom settings
    memory_config = {
        "conversation": {
            "max_turns": 100,
            "compression_enabled": True
        },
        "working": {
            "ttl": 600  # 10 minute TTL for working memory
        },
        "episodic": {
            "episode_tags": ["task", "session", "interaction"]
        },
        "semantic": {
            "relevance_threshold": 0.5
        }
    }
    
    # Create enhanced memory manager
    memory_manager = MemoryManager(config=memory_config)
    
    try:
        # Create agent with enhanced memory
        agent = Agent(
            name="MemoryEnhancedAgent",
            model=QwenModel(model="qwen/qwen-3.5-coder:free"),
            memory=memory_manager,
            system_prompt="You are an advanced AI assistant with memory capabilities. Remember important information across conversations."
        )
        
        # Add information to working memory
        agent.memory.set_working_item("project_goals", ["Build amazing AI agents", "Use Cynergy framework", "Create value"])
        print("✅ Added project goals to working memory")
        
        # Test memory retrieval
        retrieved_goals = agent.memory.get_working_item("project_goals")
        print(f"Retrieved from memory: {retrieved_goals}")
        
        return agent
    except ValueError:
        print("⚠️  API key required for this example.")
        return None


# Example 3: Agent with Custom Tools
@tool(name="calculator", description="Perform mathematical calculations")
def calculator(a: float, b: float, operation: str = "add") -> Dict[str, Any]:
    """
    Simple calculator tool for mathematical operations.
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Cannot divide by zero"
    }
    
    if operation in operations:
        result = operations[operation](a, b)
        return {"success": True, "result": result, "operation": operation, "input": {"a": a, "b": b}}
    else:
        return {"success": False, "error": f"Unknown operation: {operation}"}


async def create_agent_with_custom_tools():
    """
    Create an agent with custom tools alongside built-in tools.
    """
    print("\n🛠️  Creating an agent with custom tools...")
    
    try:
        # Create agent with Qwen model
        agent = Agent(
            name="ToolAgent",
            model=QwenModel(model="qwen/qwen-3.5-coder:free"),
            system_prompt="You are an agent with access to various tools. Use them when appropriate to solve problems."
        )
        
        # Add custom tool
        agent.add_tool(calculator)
        
        # Add pre-built tools from registry
        agent.add_tool(tool_registry.get_tool("calculate"))  # Built-in calculator
        agent.add_tool(tool_registry.get_tool("execute_python"))  # Python execution
        agent.add_tool(tool_registry.get_tool("list_directory"))  # Directory listing
        agent.add_tool(tool_registry.get_tool("read_file"))  # File reading
        agent.add_tool(tool_registry.get_tool("write_file"))  # File writing
        
        print(f"✅ Agent has {len(agent.tools)} tools: {list(agent.tools.keys())}")
        
        # Test with a mathematical request
        response = await agent.run("Calculate 24.5 * 17.8 and then add 100 to the result.")
        print(f"Tool response: {response}")
        
        return agent
    except ValueError:
        print("⚠️  API key required for this example.")
        return None


# Example 4: Multi-Provider Agent (Fallback Strategy)
async def create_multi_provider_agent():
    """
    Create an agent that can use multiple model providers with fallback strategy.
    This provides resilience and can optimize costs by using free models when available.
    """
    print("\n🔄 Creating a multi-provider agent...")
    
    # Define providers in order of preference
    providers = [
        {
            "type": "qwen",
            "model": "qwen/qwen-3.5-coder:free",
            "config": {"temperature": 0.7}
        },
        {
            "type": "ollama",
            "model": "llama3",
            "config": {"temperature": 0.7}
        },
        {
            "type": "openrouter",
            "model": "openchat/openchat-7b:free",
            "config": {"temperature": 0.7}
        }
    ]
    
    # Try to create multi-provider model
    try:
        multi_model = MultiProviderModel(providers)
        
        agent = Agent(
            name="MultiProviderAgent",
            model=multi_model,
            system_prompt="You are an AI agent that can use multiple AI providers as needed. Provide helpful responses regardless of the model used."
        )
        
        response = await agent.run("Explain the benefits of using a multi-provider approach for AI agents.")
        print(f"Multi-provider response: {response[:200]}...")
        
        return agent
    except Exception as e:
        print(f"⚠️  Multi-provider setup failed: {e}")
        # Fallback to a single provider
        try:
            agent = Agent(
                name="FallbackAgent",
                model=QwenModel(model="qwen/qwen-3.5-coder:free"),
                system_prompt="You are a helpful assistant."
            )
            return agent
        except ValueError:
            print("⚠️  API key required for fallback as well.")
            return None


# Example 5: Complete Agent Application
async def create_complete_agent_application():
    """
    Create a complete agent application combining all features.
    """
    print("\n🎯 Creating a complete agent application...")
    
    try:
        # Use Qwen model with enhanced memory
        model = QwenModel(model="qwen/qwen-3.5-coder:free")
        
        # Enhanced memory configuration
        memory_config = {
            "conversation": {"max_turns": 50, "compression_enabled": True},
            "working": {"ttl": 1200}  # 20 minute TTL
        }
        memory_manager = MemoryManager(config=memory_config)
        
        # Create agent with comprehensive setup
        agent = Agent(
            name="CompleteAgent",
            model=model,
            memory=memory_manager,
            system_prompt="""
You are a comprehensive AI assistant with multiple capabilities:
- You can perform calculations using tools
- You can execute Python code when needed
- You can read and write files
- You have memory capabilities to remember context
- You can handle complex multi-step tasks
- You provide helpful, accurate responses
""",
            max_iterations=15,
            self_healing=True
        )
        
        # Add all available tools
        for tool_name in tool_registry.get_all_tool_names():
            agent.add_tool(tool_registry.get_tool(tool_name))
        
        # Add custom calculator tool
        agent.add_tool(calculator)
        
        print(f"✅ Complete agent created with {len(agent.tools)} tools and enhanced memory")
        
        # Demonstrate multi-step interaction
        print("\n--- Multi-step interaction example ---")
        
        # First, set up a context in working memory
        agent.memory.set_working_item("current_project", {
            "name": "Cynergy Agent Demo",
            "status": "in_progress",
            "tasks": ["research", "development", "testing", "deployment"]
        })
        
        # Ask a question that uses memory
        response1 = await agent.run("What project are we currently working on and what are the tasks?")
        print(f"Context query: {response1}")
        
        # Ask a question that requires tools
        response2 = await agent.run("Calculate the factorial of 5 using Python code execution.")
        print(f"Tool usage: {response2}")
        
        return agent
    except ValueError:
        print("⚠️  API key required for this example.")
        return None


async def main():
    """
    Main function demonstrating all agent creation examples.
    """
    print("🌟 Building AI Agents with Cynergy Framework")
    print("=" * 60)
    
    agents = []
    
    # Example 1: Simple Qwen Agent
    simple_agent = await create_simple_qwen_agent()
    if simple_agent:
        agents.append(simple_agent)
    
    # Example 2: Memory Enhanced Agent
    memory_agent = await create_memory_enhanced_agent()
    if memory_agent:
        agents.append(memory_agent)
    
    # Example 3: Agent with Custom Tools
    tool_agent = await create_agent_with_custom_tools()
    if tool_agent:
        agents.append(tool_agent)
    
    # Example 4: Multi-Provider Agent
    multi_agent = await create_multi_provider_agent()
    if multi_agent:
        agents.append(multi_agent)
    
    # Example 5: Complete Agent Application
    complete_agent = await create_complete_agent_application()
    if complete_agent:
        agents.append(complete_agent)
    
    print(f"\n✅ Created {len(agents)} agents successfully!")
    
    if agents:
        print("\n📋 Agent Summary:")
        for i, agent in enumerate(agents, 1):
            print(f"  {i}. {agent.name} - State: {agent.state}, Tools: {len(agent.tools)}")
    
    print("\n✨ You now know how to build powerful AI agents with Cynergy!")
    print("\n🔑 Key concepts learned:")
    print("   - Different model options (Qwen, OpenAI, Ollama, Multi-provider)")
    print("   - Enhanced memory management (4 types: conversation, episodic, semantic, working)")
    print("   - Tool integration (custom and pre-built)")
    print("   - Multi-step workflows and context management")
    print("   - Error handling and fallback strategies")
    
    print("\n🔗 Next steps:")
    print("   - Set up API keys for OpenRouter or OpenAI")
    print("   - Explore workflow orchestration capabilities")
    print("   - Build domain-specific agents")
    print("   - Implement security policies")
    print("   - Add observability and tracing")


# Additional Helper: Environment Setup Guide
def environment_setup_guide():
    """
    Provide guidance on setting up the environment for Cynergy agents.
    """
    print("\n🔐 Environment Setup Guide:")
    print("=" * 40)
    
    print("\nRequired Environment Variables:")
    print("# For OpenRouter models (including free Qwen):")
    print("export OPENROUTER_API_KEY='your-api-key-here'")
    print("\n# For OpenAI models:")
    print("export OPENAI_API_KEY='your-api-key-here'")
    print("\n# For Anthropic models:")
    print("export ANTHROPIC_API_KEY='your-api-key-here'")
    
    print("\nOptional Environment Variables:")
    print("# For local Ollama:")
    print("# Install Ollama from https://ollama.ai and pull models with: ollama pull llama3")
    
    print("\nInstallation:")
    print("pip install cynergy-ai")  # Adjust as needed for actual package name
    
    print("\nAPI Key Sources:")
    print("- OpenRouter: https://openrouter.ai/keys (has free tier)")
    print("- OpenAI: https://platform.openai.com/api-keys")
    print("- Anthropic: https://console.anthropic.com/settings/keys")


if __name__ == "__main__":
    # Show environment setup guide
    environment_setup_guide()
    
    # Run the main examples
    asyncio.run(main())