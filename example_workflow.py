# Example: Support Ticket Triage Workflow
# This demonstrates the handoff between agents in a real-world scenario

from cynergy import Agent, OpenAIModel, tool
from cynergy.core.workflow import Workflow, WorkflowNode, WorkflowEdge, get_workflow_executor
import asyncio


# Define tools for our agents
@tool(name="classify_ticket", description="Classify a support ticket by priority and category")
def classify_ticket(ticket_text: str) -> dict:
    # In a real system, this would call an ML model or complex logic
    if "urgent" in ticket_text.lower() or "emergency" in ticket_text.lower():
        priority = "high"
    elif "question" in ticket_text.lower():
        priority = "low"
    else:
        priority = "medium"
    
    if "billing" in ticket_text.lower():
        category = "billing"
    elif "technical" in ticket_text.lower() or "bug" in ticket_text.lower():
        category = "technical"
    else:
        category = "general"
    
    return {
        "priority": priority,
        "category": category,
        "estimated_resolution_time": f"{30 if priority == 'low' else 60 if priority == 'medium' else 120} minutes"
    }


@tool(name="create_support_case", description="Create a support case in the ticketing system")
def create_support_case(ticket_data: dict) -> str:
    # In a real system, this would create an actual ticket
    return f"Case #{hash(str(ticket_data)) % 10000} created for {ticket_data.get('category', 'general')} issue"


@tool(name="assign_to_specialist", description="Assign ticket to appropriate specialist")
def assign_to_specialist(specialist_type: str, ticket_id: str) -> str:
    # In a real system, this would assign to actual specialists
    specialists = {
        "billing": "Billing Specialist",
        "technical": "Technical Specialist", 
        "general": "General Support"
    }
    return f"Assigned to {specialists.get(specialist_type, 'General Support')}"


# Create our agents
triage_agent = Agent(
    name="TicketTriageAgent",
    model=OpenAIModel("gpt-3.5-turbo"),  # Using a model most people can access
    tools=[classify_ticket, create_support_case],
    system_prompt="You are a ticket triage agent. Classify incoming tickets by priority and category, then create support cases."
)

specialist_agent = Agent(
    name="SpecialistAgent", 
    model=OpenAIModel("gpt-3.5-turbo"),
    tools=[assign_to_specialist],
    system_prompt="You are a specialist assignment agent. Assign tickets to the appropriate specialist based on category."
)

summary_agent = Agent(
    name="SummaryAgent",
    model=OpenAIModel("gpt-3.5-turbo"), 
    system_prompt="You are a summary agent. Provide a concise summary of the ticket resolution process."
)


async def main():
    # Create the workflow
    nodes = [
        WorkflowNode(
            id="triage",
            agent=triage_agent,
            name="Ticket Triage",
            type="agent",
            config={"system_prompt": "Classify tickets and create cases"}
        ),
        WorkflowNode(
            id="specialist", 
            agent=specialist_agent,
            name="Specialist Assignment",
            type="agent",
            config={"system_prompt": "Assign to appropriate specialist"}
        ),
        WorkflowNode(
            id="summary",
            agent=summary_agent, 
            name="Summary",
            type="agent",
            config={"system_prompt": "Generate resolution summary"}
        )
    ]
    
    edges = [
        WorkflowEdge(
            source_id="triage",
            target_id="specialist",
            condition="ticket classified",
            data_mapping={"ticket_info": "ticket_data"}
        ),
        WorkflowEdge(
            source_id="specialist", 
            target_id="summary",
            condition="specialist assigned",
            data_mapping={"assignment_info": "assignment_result"}
        )
    ]
    
    workflow = Workflow(
        id="support-ticket-triage-workflow",
        name="Support Ticket Triage Workflow",
        description="Classifies support tickets, assigns to specialists, and provides summary",
        nodes=nodes,
        edges=edges
    )
    
    # Register workflow with executor
    executor = get_workflow_executor()
    executor.register_workflow(workflow)
    
    # Create a session and execute the workflow
    test_input = "URGENT: Customer cannot access billing portal and needs immediate help with invoice issue"
    session_id = executor.create_session(workflow.id, test_input)
    
    print(f"Executing workflow: {workflow.name}")
    print(f"Input: {test_input}")
    print("-" * 50)
    
    result = await executor.execute_workflow(session_id)
    
    print(f"Result: {result}")
    print("-" * 50)
    
    # Get execution trace
    trace = executor.get_execution_trace(session_id)
    print(f"Execution trace: {trace}")


if __name__ == "__main__":
    asyncio.run(main())