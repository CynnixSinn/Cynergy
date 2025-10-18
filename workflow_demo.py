"""
# Cynergy Workflow Orchestration Demo

This example demonstrates workflow orchestration capabilities in Cynergy:
1. Creating workflows with multiple tasks
2. Task dependencies and execution order
3. Multi-agent workflows
4. Complex orchestrations
"""

import asyncio
from uuid import uuid4
from cynergy import (
    Agent, WorkflowOrchestrator, Workflow, WorkflowTask, 
    TaskStatus, WorkflowStatus, QwenModel
)
from unittest.mock import MagicMock

# Function to create a mock model for demonstration
def create_mock_model():
    """Create a mock model for demonstration when API keys aren't available"""
    mock_model = MagicMock()
    mock_model.generate = MagicMock(return_value=MagicMock(
        content="This is a mock response from the model. In a real implementation, this would connect to an actual AI service.",
        tool_calls=[]
    ))
    return mock_model

async def demo_basic_workflow():
    """Demo basic workflow creation and execution"""
    print("🔍 Basic Workflow Demo")
    print("-" * 30)
    
    # Create an orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Create simple agents to use in the workflow
    mock_model = create_mock_model()
    agent1 = Agent(name="ResearchAgent", model=mock_model, system_prompt="You are a research agent.")
    agent2 = Agent(name="AnalysisAgent", model=mock_model, system_prompt="You are an analysis agent.")
    agent3 = Agent(name="ReportingAgent", model=mock_model, system_prompt="You are a reporting agent.")
    
    # Register agents with orchestrator
    orchestrator.register_agent(agent1)
    orchestrator.register_agent(agent2)
    orchestrator.register_agent(agent3)
    
    print(f"Registered {len(orchestrator.agent_registry.agents)} agents with orchestrator")
    
    # Create workflow tasks
    tasks = [
        WorkflowTask(
            id=str(uuid4()),
            name="research_phase",
            agent_name="ResearchAgent",
            input_data={
                "prompt": "Research the benefits of AI agents in software development"
            }
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="analysis_phase",
            agent_name="AnalysisAgent",
            input_data={
                "prompt": "Analyze the research provided and identify key benefits",
            },
            dependencies=["research_phase"]  # This task depends on research_phase
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="report_generation",
            agent_name="ReportingAgent",
            input_data={
                "prompt": "Create a comprehensive report based on the analysis"
            },
            dependencies=["analysis_phase"]  # This task depends on analysis_phase
        )
    ]
    
    # Create the workflow
    workflow = orchestrator.create_workflow("AI Research Workflow", tasks)
    
    print(f"Created workflow: {workflow.name} (ID: {workflow.id})")
    print(f"Workflow has {len(workflow.tasks)} tasks:")
    for task in workflow.tasks:
        print(f"  • {task.name} -> Agent: {task.agent_name}")
        if task.dependencies:
            print(f"    Dependencies: {task.dependencies}")
    
    # Execute the workflow (simulated)
    print(f"\nWorkflow status: {workflow.status}")
    print("Tasks status:")
    for task in workflow.tasks:
        print(f"  • {task.name}: {task.status}")
    
    return orchestrator, workflow

async def demo_multi_agent_workflow():
    """Demo a more complex multi-agent workflow"""
    print("\n🔍 Multi-Agent Workflow Demo")
    print("-" * 30)
    
    orchestrator = WorkflowOrchestrator()
    
    # Create specialized agents
    mock_model = create_mock_model()
    coding_agent = Agent(name="CodingAgent", model=mock_model, system_prompt="You are a coding expert.")
    testing_agent = Agent(name="TestingAgent", model=mock_model, system_prompt="You are a testing expert.")
    review_agent = Agent(name="ReviewAgent", model=mock_model, system_prompt="You are a code review expert.")
    deployment_agent = Agent(name="DeploymentAgent", model=mock_model, system_prompt="You are a deployment expert.")
    
    # Register agents
    agents = [coding_agent, testing_agent, review_agent, deployment_agent]
    for agent in agents:
        orchestrator.register_agent(agent)
    
    print(f"Registered specialized agents: {[agent.name for agent in agents]}")
    
    # Create a software development workflow
    tasks = [
        WorkflowTask(
            id=str(uuid4()),
            name="code_implementation",
            agent_name="CodingAgent",
            input_data={
                "prompt": "Implement a function that calculates factorial using recursion",
                "language": "python"
            }
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="unit_tests",
            agent_name="TestingAgent",
            input_data={
                "prompt": "Create comprehensive unit tests for the factorial function",
                "requirements": ["test edge cases", "test performance", "test error handling"]
            },
            dependencies=["code_implementation"]
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="code_review",
            agent_name="ReviewAgent",
            input_data={
                "prompt": "Perform a detailed code review of the factorial implementation and tests",
                "focus": ["efficiency", "security", "best practices", "readability"]
            },
            dependencies=["unit_tests"]  # Review happens after both code and tests are done
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="deployment_preparation",
            agent_name="DeploymentAgent",
            input_data={
                "prompt": "Prepare deployment documentation and steps for the factorial function",
                "target_environment": "production"
            },
            dependencies=["code_review"]  # Only deploy after review
        )
    ]
    
    workflow = orchestrator.create_workflow("Software Development Workflow", tasks)
    
    print(f"Created complex workflow: {workflow.name}")
    print(f"Tasks with dependencies:")
    for task in workflow.tasks:
        print(f"  • {task.name} (Agent: {task.agent_name})")
        if task.dependencies:
            print(f"    -> Depends on: {', '.join(task.dependencies)}")
    
    # Simulate workflow execution
    print(f"\nInitial workflow status: {workflow.status}")
    for task in workflow.tasks:
        print(f"  {task.name}: {task.status}")
    
    return orchestrator, workflow

async def demo_conditional_workflow():
    """Demo workflow with conditional branching"""
    print("\n🔍 Conditional Workflow Demo")
    print("-" * 30)
    
    orchestrator = WorkflowOrchestrator()
    
    # Create agents
    mock_model = create_mock_model()
    analysis_agent = Agent(name="AnalysisAgent", model=mock_model, system_prompt="You analyze data.")
    high_priority_agent = Agent(name="HighPriorityAgent", model=mock_model, system_prompt="Handle high priority tasks.")
    low_priority_agent = Agent(name="LowPriorityAgent", model=mock_model, system_prompt="Handle low priority tasks.")
    reporting_agent = Agent(name="ReportingAgent", model=mock_model, system_prompt="Generate reports.")
    
    # Register agents
    for agent in [analysis_agent, high_priority_agent, low_priority_agent, reporting_agent]:
        orchestrator.register_agent(agent)
    
    # Create tasks with conditional logic
    tasks = [
        WorkflowTask(
            id=str(uuid4()),
            name="data_analysis",
            agent_name="AnalysisAgent",
            input_data={
                "prompt": "Analyze the provided dataset and determine priority level",
                "dataset": "user_support_tickets.json"
            }
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="high_priority_handling",
            agent_name="HighPriorityAgent",
            input_data={
                "prompt": "Handle high priority tickets requiring immediate attention",
            },
            dependencies=["data_analysis"]
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="low_priority_handling", 
            agent_name="LowPriorityAgent",
            input_data={
                "prompt": "Process low priority tickets in batch mode",
            },
            dependencies=["data_analysis"]
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="status_report",
            agent_name="ReportingAgent",
            input_data={
                "prompt": "Generate a status report on ticket processing",
            },
            dependencies=["high_priority_handling", "low_priority_handling"]  # Depends on both
        )
    ]
    
    workflow = orchestrator.create_workflow("Conditional Ticket Processing Workflow", tasks)
    
    print(f"Created conditional workflow: {workflow.name}")
    print("Tasks with dependencies:")
    for task in workflow.tasks:
        print(f"  • {task.name}")
        if task.dependencies:
            print(f"    -> Dependencies: {task.dependencies}")
    
    return orchestrator, workflow

async def demo_parallel_workflow():
    """Demo workflow with parallel execution paths"""
    print("\n🔍 Parallel Workflow Demo")
    print("-" * 30)
    
    orchestrator = WorkflowOrchestrator()
    
    # Create agents
    mock_model = create_mock_model()
    research_agent1 = Agent(name="ResearchAgent1", model=mock_model, system_prompt="Research technology trends.")
    research_agent2 = Agent(name="ResearchAgent2", model=mock_model, system_prompt="Research market trends.")
    research_agent3 = Agent(name="ResearchAgent3", model=mock_model, system_prompt="Research user behavior.")
    synthesis_agent = Agent(name="SynthesisAgent", model=mock_model, system_prompt="Synthesize research findings.")
    presentation_agent = Agent(name="PresentationAgent", model=mock_model, system_prompt="Create presentation.")
    
    # Register agents
    all_agents = [research_agent1, research_agent2, research_agent3, synthesis_agent, presentation_agent]
    for agent in all_agents:
        orchestrator.register_agent(agent)
    
    print(f"Registered {len(all_agents)} research agents")
    
    # Create parallel workflow tasks
    tasks = [
        # Parallel research tasks
        WorkflowTask(
            id=str(uuid4()),
            name="tech_research",
            agent_name="ResearchAgent1",
            input_data={
                "prompt": "Research latest technology trends in AI development",
                "timeframe": "last_6_months"
            }
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="market_research", 
            agent_name="ResearchAgent2",
            input_data={
                "prompt": "Research market trends for AI tools",
                "timeframe": "last_6_months"
            }
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="user_research",
            agent_name="ResearchAgent3", 
            input_data={
                "prompt": "Research user behavior and preferences for AI tools",
                "timeframe": "last_6_months"
            }
        ),
        # Synthesis task depends on all research tasks
        WorkflowTask(
            id=str(uuid4()),
            name="synthesis",
            agent_name="SynthesisAgent",
            input_data={
                "prompt": "Synthesize findings from all research tasks into comprehensive report"
            },
            dependencies=["tech_research", "market_research", "user_research"]
        ),
        # Final presentation
        WorkflowTask(
            id=str(uuid4()),
            name="create_presentation",
            agent_name="PresentationAgent",
            input_data={
                "prompt": "Create an executive presentation based on synthesis report"
            },
            dependencies=["synthesis"]
        )
    ]
    
    workflow = orchestrator.create_workflow("Parallel Research Workflow", tasks)
    
    print(f"Created parallel workflow: {workflow.name}")
    print("Execution flow:")
    print("  [tech_research]     ← Parallel execution")
    print("  [market_research]   ← starts simultaneously")
    print("  [user_research]     ←") 
    print("        ↓")
    print("  [synthesis]         ← Waits for all research to complete")
    print("        ↓") 
    print("  [create_presentation] ← Final step")
    
    # Show task execution order
    print(f"\nTasks in workflow ({len(workflow.tasks)} total):")
    for task in workflow.tasks:
        print(f"  • {task.name} -> Agent: {task.agent_name}")
        if task.dependencies:
            print(f"    Dependencies: {', '.join(task.dependencies)}")
    
    return orchestrator, workflow

async def demo_workflow_with_state():
    """Demo workflow that maintains state across tasks"""
    print("\n🔍 Stateful Workflow Demo")
    print("-" * 30)
    
    orchestrator = WorkflowOrchestrator()
    
    # Create agents for a project management workflow
    mock_model = create_mock_model()
    planning_agent = Agent(name="PlanningAgent", model=mock_model, system_prompt="Create project plans.")
    execution_agent = Agent(name="ExecutionAgent", model=mock_model, system_prompt="Execute project tasks.")
    monitoring_agent = Agent(name="MonitoringAgent", model=mock_model, system_prompt="Monitor project progress.")
    adjustment_agent = Agent(name="AdjustmentAgent", model=mock_model, system_prompt="Adjust project based on monitoring.")
    
    # Register agents
    for agent in [planning_agent, execution_agent, monitoring_agent, adjustment_agent]:
        orchestrator.register_agent(agent)
    
    # Create stateful workflow tasks
    tasks = [
        WorkflowTask(
            id=str(uuid4()),
            name="project_planning",
            agent_name="PlanningAgent",
            input_data={
                "prompt": "Create a detailed project plan for developing an AI agent",
                "constraints": ["timeline_30_days", "budget_10k", "team_size_3"]
            }
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="task_execution",
            agent_name="ExecutionAgent", 
            input_data={
                "prompt": "Execute the planned tasks while tracking time and resources",
            },
            dependencies=["project_planning"]
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="progress_monitoring",
            agent_name="MonitoringAgent",
            input_data={
                "prompt": "Monitor the execution progress and identify any deviations from the plan",
            },
            dependencies=["task_execution"]
        ),
        WorkflowTask(
            id=str(uuid4()),
            name="plan_adjustment",
            agent_name="AdjustmentAgent",
            input_data={
                "prompt": "Adjust the project plan based on monitoring results to ensure successful completion",
            },
            dependencies=["progress_monitoring"]
        )
    ]
    
    workflow = orchestrator.create_workflow("Stateful Project Management Workflow", tasks)
    
    print(f"Created stateful workflow: {workflow.name}")
    print("This workflow maintains project state across all tasks:")
    for task in workflow.tasks:
        print(f"  • {task.name}: {task.status}")
    
    # Simulate state updates (this would happen during execution)
    print(f"\nWorkflow maintains state: {workflow.status}")
    print(f"Trackable metrics: {workflow.metrics if hasattr(workflow, 'metrics') else 'Not implemented yet'}")
    
    return orchestrator, workflow

async def main():
    """Main function demonstrating all workflow capabilities"""
    print("🚀 Cynergy Workflow Orchestration Demo")
    print("=" * 50)
    print("This demo shows workflow orchestration features in Cynergy\n")
    
    # Demo 1: Basic workflow
    basic_orchestrator, basic_workflow = await demo_basic_workflow()
    
    # Demo 2: Multi-agent workflow
    multi_orchestrator, multi_workflow = await demo_multi_agent_workflow()
    
    # Demo 3: Conditional workflow
    cond_orchestrator, cond_workflow = await demo_conditional_workflow()
    
    # Demo 4: Parallel workflow
    parallel_orchestrator, parallel_workflow = await demo_parallel_workflow()
    
    # Demo 5: Stateful workflow
    state_orchestrator, state_workflow = await demo_workflow_with_state()
    
    print("\n" + "=" * 50)
    print("📋 Workflow Orchestration Summary:")
    print("• Basic Workflows: Simple task execution in defined order")
    print("• Multi-Agent Workflows: Different specialized agents for different tasks")
    print("• Conditional Workflows: Tasks that execute based on conditions")
    print("• Parallel Workflows: Multiple tasks executing simultaneously")
    print("• Stateful Workflows: Maintaining state across workflow execution")
    
    print("\n💡 Workflow Best Practices:")
    print("• Design clear task dependencies to ensure proper execution order")
    print("• Use appropriate agents for specialized tasks")
    print("• Implement error handling and fallback strategies")
    print("• Monitor workflow progress and metrics")
    print("• Consider parallel execution for independent tasks")
    print("• Use conditional logic for dynamic workflow behavior")
    
    print("\n🔗 Workflow Components:")
    print("• WorkflowOrchestrator: Central manager for workflows")
    print("• Workflow: Container for related tasks")
    print("• WorkflowTask: Individual unit of work with dependencies")
    print("• TaskStatus/WorkflowStatus: Track execution state")
    print("• Agent integration: Assign tasks to specialized agents")

if __name__ == "__main__":
    asyncio.run(main())