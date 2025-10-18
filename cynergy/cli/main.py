"""Cynergy CLI with features from both original versions"""
import click
import os
from pathlib import Path
import yaml
import json
import asyncio


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """Cynergy - Agentic AI Development Platform"""
    pass


@cli.command()
@click.argument("name")
@click.option("--template", "-t", default="basic", help="Agent template", type=click.Choice(['basic', 'web', 'enterprise', 'coder']))
@click.option("--path", "-p", default=".", help="Project path")
def init(name: str, template: str, path: str):
    """Initialize a new agent project"""
    project_path = Path(path) / name

    if project_path.exists():
        click.echo(f"Error: Directory {project_path} already exists", err=True)
        return

    project_path.mkdir(parents=True)
    (project_path / "tools").mkdir(exist_ok=True)
    (project_path / "tests").mkdir(exist_ok=True)
    (project_path / "connectors").mkdir(exist_ok=True)
    (project_path / "workflows").mkdir(exist_ok=True)

    # Create agent.yaml based on template
    if template == "enterprise":
        config = {
            "name": name,
            "model": {"provider": "openai", "name": "gpt-4"},
            "system_prompt": "You are an enterprise-grade AI assistant with advanced capabilities.",
            "tools": [],
            "memory": {"type": "conversation", "max_turns": 50},
            "policies": {
                "security": {"enabled": True},
                "rate_limiting": {"requests_per_minute": 10}
            },
            "connectors": []
        }
    elif template == "web":
        config = {
            "name": name,
            "model": {"provider": "openai", "name": "gpt-4"},
            "system_prompt": "You are a web-focused AI assistant.",
            "tools": [],
            "memory": {"type": "conversation", "max_turns": 30},
            "connectors": [
                {"type": "http", "name": "web_api", "config": {"base_url": "https://api.example.com"}}
            ]
        }
    elif template == "coder":
        config = {
            "name": name,
            "model": {"provider": "openrouter", "name": "qwen/qwen-3.5-coder:free"},
            "system_prompt": "You are an expert AI coding assistant specializing in Python development.",
            "tools": ["execute_python", "read_file", "write_file", "list_directory", "code_analyzer"],
            "memory": {
                "conversation": {"max_turns": 100, "compression_enabled": True},
                "working": {"ttl": 600}
            },
            "policies": {
                "security": {"enabled": True},
                "rate_limiting": {"requests_per_minute": 20}
            },
            "connectors": []
        }
    else:  # basic
        config = {
            "name": name,
            "model": {"provider": "openai", "name": "gpt-4"},
            "system_prompt": "You are a helpful AI assistant.",
            "tools": [],
            "memory": {"type": "conversation", "max_turns": 20}
        }

    with open(project_path / "agent.yaml", "w") as f:
        yaml.dump(config, f)

    # Create main.py based on template
    if template == "coder":
        main_content = f'''
from cynergy import Agent, QwenModel, MemoryManager, tool_registry
import asyncio

async def main():
    # Initialize agent with Qwen model and enhanced memory
    agent = Agent(
        name="{name}",
        model=QwenModel(model="qwen/qwen-3.5-coder:free"),  # Free tier
        memory=MemoryManager(config={{"conversation": {{"max_turns": 100}}}}),
        system_prompt="You are an expert coding assistant."
    )
    
    # Add development tools
    agent.add_tool(tool_registry.get_tool("execute_python"))
    agent.add_tool(tool_registry.get_tool("read_file"))
    agent.add_tool(tool_registry.get_tool("write_file"))
    agent.add_tool(tool_registry.get_tool("list_directory"))
    agent.add_tool(tool_registry.get_tool("code_analyzer"))
    
    print("🚀 {name} is ready! Ask me to help with coding tasks.")
    response = await agent.run("Hello! What can you help me with today?")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
        '''.strip()
    else:
        main_content = f'''
from cynergy import Agent, OpenAIModel
import asyncio

async def main():
    agent = Agent(
        name="{name}",
        model=OpenAIModel("gpt-4"),
        system_prompt="You are a helpful assistant."
    )

    response = await agent.run("Hello!")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
        '''.strip()

    with open(project_path / "main.py", "w") as f:
        f.write(main_content)

    # Create README
    with open(project_path / "README.md", "w") as f:
        readme_content = f"""# {name}

Agent created with Cynergy Framework

## Getting Started

1. Set up your API keys:
   ```bash
   # For OpenRouter (free Qwen access)
   export OPENROUTER_API_KEY=your_openrouter_api_key
   
   # For OpenAI (if using OpenAI models)
   export OPENAI_API_KEY=your_openai_api_key
   ```

2. Install dependencies:
   ```bash
   pip install cynergy[all]
   ```

3. Run the agent:
   ```bash
   python main.py
   ```

## Features

- **AI Model**: {'Qwen (Free)' if template == 'coder' else 'OpenAI GPT-4'}
- **Memory**: Enhanced memory management
- **Tools**: {'Development tools included' if template == 'coder' else 'Basic tools'}
- **Security**: {'Enabled' if template in ['enterprise', 'coder'] else 'Basic'}

## Project Structure

- `main.py`: Main agent implementation
- `agent.yaml`: Agent configuration
- `tools/`: Custom tools
- `connectors/`: Connector definitions
- `workflows/`: Workflow definitions
- `tests/`: Agent tests
"""
        f.write(readme_content)

    click.echo(f"✅ Created new Cynergy agent: {name}")
    click.echo(f"📁 Location: {project_path}")
    click.echo(f"\nNext steps:")
    click.echo(f"  cd {name}")
    click.echo(f"  python main.py")


@cli.command()
def demo():
    """Run a demonstration of Cynergy's enhanced features"""
    click.echo("🚀 Running Cynergy Enhanced Features Demo")
    click.echo("-" * 40)
    
    # Import and run the example
    try:
        import sys
        from pathlib import Path
        # Add the current directory to the path so we can import cynergy
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from example_enhanced import main as demo_main
        import asyncio
        
        click.echo("Running enhanced features demo...")
        asyncio.run(demo_main())
        
    except ImportError as e:
        click.echo(f"❌ Could not run demo: {e}")
        click.echo("💡 Run from the project root directory to see the demo")


@cli.command()
@click.option('--model', default='qwen/qwen-3.5-coder:free', help='Model to test (default: free Qwen)')
def test_model(model: str):
    """Test model connectivity"""
    click.echo(f"📡 Testing model: {model}")
    
    try:
        if "qwen" in model.lower():
            from cynergy import QwenModel
            model_instance = QwenModel(model=model)
        elif "openai" in model.lower():
            from cynergy import OpenAIModel
            model_instance = OpenAIModel(model)
        else:
            from cynergy import OpenAIModel  # fallback
            model_instance = OpenAIModel("gpt-3.5-turbo")
        
        click.echo(f"✅ Model {model} initialized successfully")
        click.echo("💡 Model is ready for use!")
        
    except Exception as e:
        click.echo(f"❌ Model test failed: {e}")
        click.echo("💡 Make sure your API keys are set correctly")


@cli.command()
def version():
    """Show version"""
    click.echo("Cynergy v0.2.0")


@cli.command()
@click.argument('agent_file')
def run(agent_file: str):
    """Run an agent script"""
    if not Path(agent_file).exists():
        click.echo(f"Error: Agent file '{agent_file}' does not exist", err=True)
        return
    
    click.echo(f"Running agent: {agent_file}")
    
    # In a real implementation, we would actually execute the agent
    # For now, we'll just show a message
    click.echo("Agent execution would happen here in a real implementation")


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=3000, type=int, help='Port to serve on')
def serve(host: str, port: int):
    """Start the Studio web server"""
    click.echo(f"Starting Cynergy Studio server on {host}:{port}")
    click.echo("This would start the server in a real implementation")
    click.echo(f"Visit http://{host}:{port} to access the studio")


@cli.command()
@click.argument('benchmark_file')
@click.option('--agent', required=True, help='Agent to evaluate')
def eval(benchmark_file: str, agent: str):
    """Run evaluations"""
    if not Path(benchmark_file).exists():
        click.echo(f"Error: Benchmark file '{benchmark_file}' does not exist", err=True)
        return
    
    click.echo(f"Evaluating agent '{agent}' against benchmark: {benchmark_file}")
    click.echo("Evaluation would happen here in a real implementation")


@cli.command()
@click.argument('action', type=click.Choice(['list', 'add', 'remove', 'test']))
@click.argument('name', required=False)
def connect(action: str, name: str):
    """Manage connectors"""
    if action == 'list':
        click.echo("Listing connectors...")
        click.echo("No connectors configured yet.")
    elif action == 'add':
        if not name:
            click.echo("Error: Connector name is required for add operation", err=True)
            return
        click.echo(f"Adding connector: {name}")
        click.echo("Connector addition would happen here in a real implementation")
    elif action == 'remove':
        if not name:
            click.echo("Error: Connector name is required for remove operation", err=True)
            return
        click.echo(f"Removing connector: {name}")
        click.echo("Connector removal would happen here in a real implementation")
    elif action == 'test':
        if not name:
            click.echo("Error: Connector name is required for test operation", err=True)
            return
        click.echo(f"Testing connector: {name}")
        click.echo("Connector testing would happen here in a real implementation")


@cli.command()
@click.argument('action', type=click.Choice(['list', 'view', 'export']))
@click.argument('session_id', required=False)
@click.option('--format', type=click.Choice(['json', 'jsonl']), default='json', help='Output format for export')
def trace(action: str, session_id: str, format: str):
    """Manage traces"""
    if action == 'list':
        click.echo("Listing recent traces...")
        click.echo("No traces available yet.")
    elif action == 'view':
        if not session_id:
            click.echo("Error: Session ID is required for view operation", err=True)
            return
        click.echo(f"Viewing trace for session: {session_id}")
        click.echo("Trace viewing would happen here in a real implementation")
    elif action == 'export':
        if not session_id:
            click.echo("Error: Session ID is required for export operation", err=True)
            return
        click.echo(f"Exporting trace for session: {session_id} in {format} format")
        click.echo("Trace export would happen here in a real implementation")


if __name__ == "__main__":
    cli()