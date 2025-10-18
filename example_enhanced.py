"""
Comprehensive example demonstrating Cynergy's new features:
- OpenRouter integration with Qwen/Qwen3-Coder
- Enhanced memory management
- Workflow orchestration
- Advanced tools
"""
import asyncio
from cynergy import (
    Agent, QwenModel, OpenAIModel, MemoryManager, 
    WorkflowOrchestrator, WorkflowTask, 
    execute_python, read_file, write_file, 
    list_directory, code_analyzer, calculate,
    tool_registry
)
import json
from uuid import uuid4


async def main():
    print("🚀 Starting Cynergy Framework with Enhanced Features")
    print("=" * 60)
    
    # 1. DEMONSTRATE OPENROUTER INTEGRATION WITH QWEN
    print("\n🔧 1. Testing OpenRouter Integration with Qwen/Qwen3-Coder")
    print("-" * 50)
    
    try:
        # Initialize Qwen model (free tier)
        qwen_model = QwenModel(model="qwen/qwen-3.5-coder:free")
        
        # Create an agent with enhanced memory
        agent = Agent(
            name="QwenDevAgent",
            model=qwen_model,
            system_prompt="You are Qwen, an expert AI coding assistant. Provide concise, helpful responses with examples when needed.",
            memory=MemoryManager(config={
                "conversation": {"max_turns": 100, "compression_enabled": True},
                "working": {"ttl": 600}  # 10 minute TTL for working memory
            })
        )
        
        print("✅ Qwen model initialized with OpenRouter")
        
        # Test the agent with a coding question
        print("\nAsking Qwen a coding question...")
        response = await agent.run("What are the best practices for Python async programming?")
        print(f"Qwen Response: {response[:200]}...")
        
    except ValueError as e:
        if "API key not provided" in str(e):
            print(f"⚠️  API keys not configured: {e}")
            print("💡 To use OpenRouter with Qwen, set OPENROUTER_API_KEY environment variable")
            print("💡 To use OpenAI, set OPENAI_API_KEY environment variable")
            print("\n📋 Creating agent without model (for demonstration only)...")
            
            # Create a mock agent for demonstration
            from unittest.mock import MagicMock
            mock_model = MagicMock()
            mock_model.generate = MagicMock(return_value=MagicMock(content="Mock response for demonstration", tool_calls=[]))
            
            agent = Agent(
                name="DemoAgent",
                model=mock_model,
                system_prompt="This is a demonstration agent."
            )
            print("✅ Demo agent created with mock model for feature demonstration")
        else:
            raise
    except Exception as e:
        print(f"⚠️  Unexpected error: {e}")
        print("Creating demo agent for feature demonstration...")
        
        # Create a mock agent for demonstration
        from unittest.mock import MagicMock
        mock_model = MagicMock()
        mock_model.generate = MagicMock(return_value=MagicMock(content="Mock response for demonstration", tool_calls=[]))
        
        agent = Agent(
            name="DemoAgent",
            model=mock_model,
            system_prompt="This is a demonstration agent."
        )
        print("✅ Demo agent created with mock model for feature demonstration")
    
    # 2. DEMONSTRATE ENHANCED TOOLS
    print("\n🛠️  2. Testing Enhanced Tools")
    print("-" * 50)
    
    # Register additional tools with the agent
    agent.add_tool(tool_registry.get_tool("execute_python"))
    agent.add_tool(tool_registry.get_tool("read_file"))
    agent.add_tool(tool_registry.get_tool("write_file"))
    agent.add_tool(tool_registry.get_tool("list_directory"))
    agent.add_tool(tool_registry.get_tool("code_analyzer"))
    agent.add_tool(tool_registry.get_tool("calculate"))
    
    print(f"✅ Registered {len(agent.tools)} tools")
    print(f"Available tools: {list(agent.tools.keys())}")
    
    # Example: Code analysis
    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(10)
print(f"Fibonacci of 10 is: {result}")
"""
    
    print(f"\nAnalyzing code:\n{sample_code}")
    # Call the functions directly (they were imported earlier in the tool registration)
    from cynergy.tools.enhanced_tools import code_analyzer, calculate
    # Access the underlying function
    analysis = code_analyzer.func(sample_code, "python")
    print(f"Analysis result: {analysis}")
    
    # Example: Math calculation
    calc_result = calculate.func("24.5 * 17.8 + 100")
    print(f"\nCalculation '24.5 * 17.8 + 100': {calc_result}")
    
    # 3. DEMONSTRATE WORKFLOW ORCHESTRATION
    print("\n🔄 3. Testing Workflow Orchestration")
    print("-" * 50)
    
    # Create orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Register agents with orchestrator
    orchestrator.register_agent(agent)
    
    # Create a simple workflow: analyze code -> generate report
    workflow_tasks = [
        WorkflowTask(
            id=str(uuid4()),
            name="code_analysis",
            agent_name="QwenDevAgent",
            input_data={
                "prompt": "Analyze this Python function for best practices: def quicksort(arr): if len(arr) <= 1: return arr; pivot = arr[len(arr) // 2]; left = [x for x in arr if x < pivot]; middle = [x for x in arr if x == pivot]; right = [x for x in arr if x > pivot]; return quicksort(left) + middle + quicksort(right)"
            }
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="report_generation", 
            agent_name="QwenDevAgent",
            input_data={
                "prompt": "Create a summary report of the code analysis focusing on performance and best practices"
            },
            dependencies=["code_analysis"]  # This task depends on the previous one
        )
    ]
    
    # Create the workflow
    workflow = orchestrator.create_workflow("Code Analysis Workflow", workflow_tasks)
    print(f"✅ Created workflow '{workflow.name}' with ID: {workflow.id}")
    print(f"Tasks: {[task.name for task in workflow.tasks]}")
    
    # Note: In a real implementation, we would execute the workflow
    print("\n💡 Workflow execution would happen here in a full implementation")
    
    # 4. DEMONSTRATE ENHANCED MEMORY
    print("\n🧠 4. Testing Enhanced Memory Management")
    print("-" * 50)
    
    # The agent already has enhanced memory from the constructor
    print(f"Memory types available: Conversation, Episodic, Semantic, Working")
    
    # Add something to working memory
    if hasattr(agent.memory, 'set_working_item'):
        agent.memory.set_working_item("last_analysis", analysis, importance=0.8)
        retrieved = agent.memory.get_working_item("last_analysis")
        print(f"Stored and retrieved from working memory: {type(retrieved)}")
    
    # 5. SHOW ADVANCED FEATURES
    print("\n🌟 5. Additional Advanced Features")
    print("-" * 50)
    
    print("✅ Multi-provider model support (OpenRouter, OpenAI, Anthropic, Ollama)")
    print("✅ Enhanced memory with conversation, episodic, semantic, and working memory")
    print("✅ Comprehensive tool set (file operations, code analysis, execution, etc.)")
    print("✅ Workflow orchestration with dependency management")
    print("✅ Built-in security policies and rate limiting")
    print("✅ Tracing and observability")
    print("✅ Plugin system for extensibility")
    
    # 6. PROVIDE USAGE EXAMPLES
    print("\n📚 6. Usage Examples")
    print("-" * 50)
    
    examples = {
        "Simple Agent": """
from cynergy import Agent, QwenModel
agent = Agent(
    name="DevAssistant", 
    model=QwenModel(),
    system_prompt="You are a helpful coding assistant"
)
response = await agent.run("How do I implement a binary search in Python?")
""",
        "With Tools": """
from cynergy import tool_registry
agent.add_tool(tool_registry.get_tool("execute_python"))
response = await agent.run("Execute this Python code: print('Hello from Cynergy!')")
""",
        "With Workflow": """
orchestrator = WorkflowOrchestrator()
orchestrator.register_agent(agent)
# Create and execute complex multi-step workflows
"""
    }
    
    for name, example in examples.items():
        print(f"{name}: {example.strip()}")
    
    print(f"\n🎉 Cynergy Framework with Enhanced Features is ready to use!")
    print("✨ You can now build sophisticated AI applications with:")
    print("   - Free Qwen model access via OpenRouter")
    print("   - Advanced memory management")
    print("   - Comprehensive tool ecosystem")
    print("   - Workflow orchestration")
    print("   - Multi-agent collaboration")


if __name__ == "__main__":
    asyncio.run(main())