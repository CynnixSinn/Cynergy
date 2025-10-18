# 🔥 Cynergy Framework

> **The next evolution of agentic AI frameworks. Build, connect, and scale intelligent systems with supercharged autonomy.**

## 🚀 Quick Start

### Installation

```bash
pip install -e .
```

### Create Your First Agent

```python
from cynergy import Agent, OpenAIModel, tool

@tool(name="calculator", description="Perform calculations")
def calculator(expression: str) -> float:
    # In a real implementation, you'd want to use a safer eval or expression parser
    return eval(expression)

agent = Agent(
    name="MathAgent",
    model=OpenAIModel("gpt-4"),
    tools=[calculator],
    system_prompt="You are a math assistant."
)

# Run the agent
import asyncio
response = asyncio.run(agent.run("What is 25 * 17?"))
print(response)
```

### Using the CLI

```bash
# Initialize a new agent project
cynergy init my-agent

# Navigate to project
cd my-agent

# Run the agent
python main.py
```

## 🌟 Features

- 🧩 **Modular & Composable** - Plugin-based architecture
- 🌍 **Multi-Provider** - OpenAI, Anthropic, OpenRouter (with free Qwen/Qwen3-Coder), local models (Ollama)
- 🤖 **Free LLM Access** - Integrated with OpenRouter for free Qwen model access
- 🔌 **Extensible** - Custom tools and connectors
- 👨‍💻 **Developer-First** - CLI tools + APIs
- 🔒 **Secure** - Sandboxed execution
- 🎯 **Self-Healing** - Automatic retry and correction
- 🤝 **Handoffs** - Multi-agent coordination
- 📊 **Observability** - Full tracing and metrics
- 🛡️ **Policy Engine** - Safety and compliance enforcement
- 🧠 **Enhanced Memory** - Conversation, episodic, semantic, and working memory systems
- 🔄 **Workflow Orchestration** - Multi-step task coordination with dependencies
- 🛠️ **Advanced Tools** - File operations, code analysis, execution, and more
- 🚀 **Smart Model Selection** - Multi-provider model fallback for resilience

## Architecture

Cynergy is built around several core modules:

- **Core**: The engine that orchestrates agent execution
- **SDK**: Developer APIs for building agents
- **Connect**: Unified connector registry and adapters
- **Studio**: Web UI for agent design and monitoring
- **Observe**: Tracing and metrics collection
- **Eval**: Evaluation and benchmarking framework
- **Security**: Sandboxing and policy enforcement
- **CLI**: Command-line tools

## License

MIT License - see [LICENSE](LICENSE)