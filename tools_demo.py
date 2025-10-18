"""
# Cynergy Tools Demo

This example demonstrates how to use and create tools with Cynergy agents.
Tools allow agents to interact with the external world and perform actions.
"""

import asyncio
import os
from cynergy import Agent, QwenModel, tool_registry, tool
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

# Example 1: Using Pre-built Tools
async def demo_prebuilt_tools():
    """Demo using the pre-built tools available in Cynergy"""
    print("🔍 Pre-built Tools Demo")
    print("-" * 30)
    
    # Show all available tools in the registry
    print("Available tools in Cynergy:")
    for i, tool_name in enumerate(tool_registry.get_all_tool_names(), 1):
        tool_obj = tool_registry.get_tool(tool_name)
        print(f"  {i}. {tool_name}: {tool_obj.description}")
    
    print(f"\nTotal tools available: {len(tool_registry.get_all_tool_names())}")
    
    # Create an agent and add pre-built tools
    mock_model = create_mock_model()
    agent = Agent(
        name="PrebuiltToolsAgent",
        model=mock_model,
        system_prompt="You are an agent with access to various tools. Use them when appropriate to solve problems."
    )
    
    # Add several pre-built tools
    tools_to_add = ["calculate", "list_directory", "read_file", "write_file", "execute_python"]
    for tool_name in tools_to_add:
        tool_obj = tool_registry.get_tool(tool_name)
        if tool_obj:
            agent.add_tool(tool_obj)
            print(f"✅ Added tool: {tool_name}")
    
    print(f"\nAgent now has {len(agent.tools)} tools: {list(agent.tools.keys())}")
    return agent

# Example 2: Creating Custom Tools
@tool(name="weather_check", description="Check weather for a given location")
def weather_check(location: str, units: str = "celsius") -> dict:
    """
    Simulate checking weather for a location.
    In a real implementation, this would call a weather API.
    """
    # Simulated weather data
    weather_data = {
        "location": location,
        "temperature": 22 if units == "celsius" else 72,
        "units": units,
        "conditions": "sunny",
        "humidity": 65
    }
    return weather_data

@tool(name="stock_price", description="Get current stock price for a company")
def stock_price(symbol: str) -> dict:
    """
    Simulate getting stock price for a company.
    In a real implementation, this would call a financial API.
    """
    # Simulated stock prices
    prices = {
        "AAPL": 175.43,
        "GOOGL": 2750.21,
        "MSFT": 405.52,
        "TSLA": 240.51,
        "AMZN": 3200.19
    }
    
    price = prices.get(symbol.upper(), 0.0)
    return {
        "symbol": symbol.upper(),
        "price": price,
        "currency": "USD"
    }

@tool(name="calculate_mortgage", description="Calculate monthly mortgage payment")
def calculate_mortgage(principal: float, interest_rate: float, years: int) -> dict:
    """
    Calculate monthly mortgage payment.
    
    Args:
        principal: Loan amount
        interest_rate: Annual interest rate (as percentage)
        years: Loan term in years
    
    Returns:
        Dictionary with payment details
    """
    monthly_rate = (interest_rate / 100) / 12
    num_payments = years * 12
    
    if monthly_rate == 0:
        monthly_payment = principal / num_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    
    total_payment = monthly_payment * num_payments
    total_interest = total_payment - principal
    
    return {
        "monthly_payment": round(monthly_payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "loan_details": {
            "principal": principal,
            "interest_rate": interest_rate,
            "years": years
        }
    }

async def demo_custom_tools():
    """Demo creating and using custom tools"""
    print("\n🔧 Custom Tools Demo")
    print("-" * 30)
    
    # Create an agent with custom tools
    mock_model = create_mock_model()
    agent = Agent(
        name="CustomToolsAgent",
        model=mock_model,
        system_prompt="You are an agent with access to custom tools for weather, stock prices, and mortgage calculations."
    )
    
    # Add custom tools to the agent
    agent.add_tool(weather_check)
    agent.add_tool(stock_price)
    agent.add_tool(calculate_mortgage)
    
    print("Custom tools added to agent:")
    for name, tool_obj in agent.tools.items():
        print(f"  • {name}: {tool_obj.description}")
    
    # Demonstrate using custom tools
    print("\nSimulating tool usage scenarios:")
    
    # Weather check - use the underlying function
    try:
        result = weather_check.func("New York", "celsius")
        print(f"  Weather in New York: {result['temperature']}°{result['units']}, {result['conditions']}")
    except Exception as e:
        print(f"  Weather check error: {e}")
    
    # Stock price - use the underlying function
    try:
        result = stock_price.func("AAPL")
        print(f"  Apple stock price: ${result['price']}")
    except Exception as e:
        print(f"  Stock price check error: {e}")
    
    # Mortgage calculation - use the underlying function
    try:
        result = calculate_mortgage.func(300000, 4.5, 30)
        print(f"  Mortgage for $300,000 at 4.5% for 30 years: ${result['monthly_payment']}/month")
    except Exception as e:
        print(f"  Mortgage calculation error: {e}")
    
    return agent

# Example 3: Tool Parameters and Validation
@tool(
    name="validate_email", 
    description="Validate if an email address is properly formatted"
)
def validate_email(email: str) -> dict:
    """
    Validate email format using basic regex.
    Returns validation result.
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(pattern, email) is not None
    
    return {
        "email": email,
        "is_valid": is_valid,
        "validation_notes": "Email format appears valid" if is_valid else "Invalid email format"
    }

@tool(
    name="format_currency",
    description="Format a number as currency with specified locale"
)
def format_currency(amount: float, currency_code: str = "USD", locale: str = "en_US") -> str:
    """
    Format a number as currency.
    """
    # Simple formatting for demo purposes
    currency_symbols = {
        "USD": "$",
        "EUR": "€", 
        "GBP": "£",
        "JPY": "¥"
    }
    
    symbol = currency_symbols.get(currency_code, currency_code)
    return f"{symbol}{amount:,.2f}"

async def demo_tool_parameters():
    """Demo tools with parameters and validation"""
    print("\n📝 Tool Parameters Demo")
    print("-" * 30)
    
    mock_model = create_mock_model()
    agent = Agent(
        name="ParameterizedToolsAgent",
        model=mock_model,
        system_prompt="You are an agent with tools that have specific parameters and validation."
    )
    
    # Add tools with parameters
    agent.add_tool(validate_email)
    agent.add_tool(format_currency)
    
    print("Tools with parameters and validation:")
    for name, tool_obj in agent.tools.items():
        print(f"  • {name}: {tool_obj.description}")
        # Show parameters if available
        if hasattr(tool_obj, 'parameters') and tool_obj.parameters:
            print(f"    Parameters: {tool_obj.parameters}")
    
    # Test tool parameter validation
    print("\nTesting parameter validation:")
    
    # Valid email
    try:
        result = validate_email.func("user@example@example.com")
        print(f"  Valid email test: {result}")
    except Exception as e:
        print(f"  Valid email test error: {e}")
    
    # Invalid email
    try:
        result = validate_email.func("invalid-email")
        print(f"  Invalid email test: {result}")
    except Exception as e:
        print(f"  Invalid email test error: {e}")
    
    # Currency formatting
    try:
        formatted = format_currency.func(1234.56, "USD")
        print(f"  Currency formatting: {formatted}")
    except Exception as e:
        print(f"  Currency formatting error: {e}")
    
    return agent

# Example 4: Tool Integration with Real Examples
async def demo_tool_integration():
    """Demo how tools integrate with agents in real scenarios"""
    print("\n🔗 Tool Integration Demo")
    print("-" * 30)
    
    # Create an agent with multiple tools for a complex task
    mock_model = create_mock_model()
    agent = Agent(
        name="IntegrationAgent",
        model=mock_model,
        system_prompt="You are an agent that can integrate multiple tools to solve complex problems."
    )
    
    # Add various tools
    agent.add_tool(stock_price)
    agent.add_tool(weather_check)
    agent.add_tool(calculate_mortgage)
    agent.add_tool(validate_email)
    agent.add_tool(format_currency)
    
    print(f"Integration agent created with {len(agent.tools)} tools")
    
    # Simulate how an agent might use multiple tools for a complex request
    print("\nSimulating complex multi-tool request:")
    
    # Example: Calculate mortgage and format as currency
    try:
        mortgage_result = calculate_mortgage.func(500000, 3.75, 15)
        monthly_payment = mortgage_result['monthly_payment']
        monthly_formatted = format_currency.func(monthly_payment, "USD")
        print(f"  15-year mortgage at $500k: {monthly_formatted}/month")
    except Exception as e:
        print(f"  Mortgage calculation error: {e}")
    
    # Example: Check stock and format
    try:
        stock_result = stock_price.func("TSLA")
        stock_formatted = format_currency.func(stock_result['price'], "USD")
        print(f"  Tesla stock: {stock_formatted}")
    except Exception as e:
        print(f"  Stock check error: {e}")
    
    # Example: Validate email
    try:
        email_result = validate_email.func("contact@example.com")
        print(f"  Email validation: {email_result['is_valid']}")
    except Exception as e:
        print(f"  Email validation error: {e}")
    
    return agent

async def main():
    """Main function demonstrating all tool capabilities"""
    print("🚀 Cynergy Tools Demo")
    print("=" * 50)
    print("This demo shows how to use and create tools with Cynergy agents\n")
    
    # Demo 1: Pre-built tools
    prebuilt_agent = await demo_prebuilt_tools()
    
    # Demo 2: Custom tools
    custom_agent = await demo_custom_tools()
    
    # Demo 3: Tool parameters
    parameter_agent = await demo_tool_parameters()
    
    # Demo 4: Tool integration
    integration_agent = await demo_tool_integration()
    
    print("\n" + "=" * 50)
    print("📋 Tool Capabilities Summary:")
    print("• Pre-built tools: Calculate, file operations, code execution, web search, etc.")
    print("• Custom tools: Create your own specialized functions")
    print("• Parameter validation: Tools with type hints and validation")
    print("• Tool integration: Multiple tools for complex tasks")
    print("• JSON schema: Automatic parameter schema generation")
    
    print("\n💡 Best Practices:")
    print("• Use pre-built tools for common operations")
    print("• Create custom tools for domain-specific functions")
    print("• Always handle errors in tool functions")
    print("• Provide clear descriptions for tool discovery")
    print("• Use proper type hints for parameters")
    
    print("\n🔗 Tool Creation Process:")
    print("1. Define function with appropriate parameters")
    print("2. Use @tool decorator to register it")
    print("3. Add to agent with agent.add_tool()")
    print("4. Agent can now use the tool automatically")

if __name__ == "__main__":
    asyncio.run(main())