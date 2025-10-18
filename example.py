# Example usage of the combined Cynergy system
from cynergy import Agent, OpenAIModel, tool
from cynergy.connect import HTTPConnector
from cynergy.security import PolicyEngine, RateLimitPolicy
from cynergy.observe import get_tracer
import asyncio


@tool(name="calculator", description="Perform mathematical calculations")
def calculator(a: float, b: float, operation: str = "add") -> float:
    """Simple calculator tool"""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")


async def main():
    # Create a policy engine with rate limiting
    policy_engine = PolicyEngine()
    rate_limit_policy = RateLimitPolicy("agent_rate_limit", {"requests_per_minute": 5})
    policy_engine.add_policy(rate_limit_policy)
    
    # Create an HTTP connector
    api_connector = HTTPConnector("example_api", {
        "base_url": "https://jsonplaceholder.typicode.com",
        "headers": {"Content-Type": "application/json"}
    })
    
    # Create an agent with OpenAI model
    agent = Agent(
        name="ExampleAgent",
        model=OpenAIModel("gpt-3.5-turbo"),  # Using a model that most people can access
        tools=[calculator],
        system_prompt="You are a helpful assistant that can perform calculations and access external APIs.",
        policy_engine=policy_engine
    )
    
    # Add the connector as a tool
    agent.add_connector(api_connector)
    
    # Run the agent
    print("Running example agent...")
    response = await agent.run("What is 24.5 multiplied by 17.8?")
    print(f"Response: {response}")
    
    print("\nRunning second request...")
    response2 = await agent.run("What is 100 divided by 4?")
    print(f"Response: {response2}")
    
    # Example of what would happen with rate limiting
    # (In this example, the rate limit won't be hit since we're only making 2 requests)
    print("\nThis example demonstrates the combined features of both Cynergy versions:")
    print("- Modern agent implementation with decorator-based tools")
    print("- Advanced policy engine for security and rate limiting")
    print("- Connector system for external API access")
    print("- Tracing and observability features")


if __name__ == "__main__":
    asyncio.run(main())