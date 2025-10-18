"""
# Cynergy Model Options Demo

This example demonstrates the different model options available in Cynergy:
1. Qwen via OpenRouter (free tier)
2. OpenAI models
3. Anthropic models
4. Local Ollama models
5. Multi-provider fallback strategy
"""

import asyncio
import os
from unittest.mock import MagicMock
from cynergy import (
    QwenModel, OpenAIModel, AnthropicModel, OllamaModel, 
    MultiProviderModel, Agent
)

# Function to create a mock model for demonstration
def create_mock_model():
    """Create a mock model for demonstration when API keys aren't available"""
    mock_model = MagicMock()
    mock_model.generate = MagicMock(return_value=MagicMock(
        content="This is a mock response from the model. In a real implementation, this would connect to an actual AI service.",
        tool_calls=[]
    ))
    return mock_model

async def demo_qwen_model():
    """Demo Qwen model via OpenRouter (free tier)"""
    print("🔍 Qwen Model Demo")
    print("-" * 30)
    
    # Check if API key is available
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if api_key:
        print("✅ Using real Qwen model (free tier)")
        try:
            model = QwenModel(model="qwen/qwen-3.5-coder:free")
            print(f"Model: {model.model}")
            print(f"Temperature: {model.temperature}")
            return model
        except Exception as e:
            print(f"❌ Error creating Qwen model: {e}")
            return create_mock_model()
    else:
        print("⚠️  OPENROUTER_API_KEY not found, using mock model for demo")
        print("💡 To use real Qwen model, get a free API key from https://openrouter.ai/keys")
        return create_mock_model()

async def demo_openai_model():
    """Demo OpenAI models"""
    print("\n🔍 OpenAI Model Demo")
    print("-" * 30)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key:
        print("✅ Using real OpenAI model")
        try:
            model = OpenAIModel(model="gpt-3.5-turbo")
            print(f"Model: {model.model}")
            print(f"Temperature: {model.temperature}")
            return model
        except Exception as e:
            print(f"❌ Error creating OpenAI model: {e}")
            return create_mock_model()
    else:
        print("⚠️  OPENAI_API_KEY not found, using mock model for demo")
        print("💡 To use OpenAI models, get an API key from https://platform.openai.com/api-keys")
        return create_mock_model()

async def demo_anthropic_model():
    """Demo Anthropic models (Claude)"""
    print("\n🔍 Anthropic Model Demo")
    print("-" * 30)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if api_key:
        print("✅ Using real Anthropic model")
        try:
            model = AnthropicModel(model="claude-3-haiku-20240307")
            print(f"Model: {model.model}")
            print(f"Temperature: {model.temperature}")
            return model
        except Exception as e:
            print(f"❌ Error creating Anthropic model: {e}")
            return create_mock_model()
    else:
        print("⚠️  ANTHROPIC_API_KEY not found, using mock model for demo")
        print("💡 To use Anthropic models, get an API key from https://console.anthropic.com/settings/keys")
        return create_mock_model()

async def demo_ollama_model():
    """Demo local Ollama models"""
    print("\n🔍 Ollama Model Demo (Local) - No API Key Required")
    print("-" * 30)
    
    # Check if Ollama is running
    try:
        model = OllamaModel(model="llama3")
        print("✅ Using local Ollama model")
        print(f"Model: {model.model}")
        print(f"Temperature: {model.temperature}")
        print(f"Base URL: {model.base_url}")
        print("💡 To use Ollama, install from https://ollama.ai and pull models: ollama pull llama3")
        return model
    except Exception as e:
        print(f"⚠️  Ollama not available or not running: {e}")
        print("💡 Install Ollama from https://ollama.ai and run: ollama pull llama3")
        return create_mock_model()

async def demo_multi_provider_model():
    """Demo multi-provider model with fallback strategy"""
    print("\n🔍 Multi-Provider Model Demo (Fallback Strategy)")
    print("-" * 30)
    
    # Define providers with fallback order
    providers = [
        {
            "type": "qwen",
            "model": "qwen/qwen-3.5-coder:free",
            "config": {
                "temperature": 0.7,
                "api_key": os.getenv("OPENROUTER_API_KEY")
            }
        },
        {
            "type": "ollama", 
            "model": "llama3",
            "config": {
                "temperature": 0.7
            }
        },
        {
            "type": "openrouter",
            "model": "openchat/openchat-7b:free",
            "config": {
                "temperature": 0.7,
                "api_key": os.getenv("OPENROUTER_API_KEY")
            }
        }
    ]
    
    try:
        model = MultiProviderModel(providers)
        print("✅ Multi-provider model created with fallback strategy")
        print("Fallback order:")
        for i, provider_info in enumerate(model.providers, 1):
            print(f"  {i}. {provider_info['type']}: {provider_info['model']}")
        return model
    except Exception as e:
        print(f"⚠️  Error creating multi-provider model: {e}")
        return create_mock_model()

async def demo_model_comparison():
    """Compare different models by creating agents with each"""
    print("\n🔍 Model Comparison Demo")
    print("-" * 30)
    
    models = {
        "Qwen (Free)": await demo_qwen_model(),
        "OpenAI (GPT)": await demo_openai_model(), 
        "Anthropic (Claude)": await demo_anthropic_model(),
        "Ollama (Local)": await demo_ollama_model(),
    }
    
    # Create agents with each model
    print("\nCreating agents with different models:")
    for model_name, model in models.items():
        try:
            agent = Agent(
                name=f"{model_name.replace(' ', '')}Agent",
                model=model,
                system_prompt=f"You are an AI assistant powered by {model_name}. Provide helpful responses."
            )
            print(f"✅ {agent.name} with {model_name}")
        except Exception as e:
            print(f"❌ Failed to create agent with {model_name}: {e}")

async def main():
    """Main function demonstrating all model options"""
    print("🚀 Cynergy Model Options Demo")
    print("=" * 50)
    print("This demo shows the different AI model options available in Cynergy\n")
    
    # Demo each model type
    qwen_model = await demo_qwen_model()
    openai_model = await demo_openai_model()
    anthropic_model = await demo_anthropic_model()
    ollama_model = await demo_ollama_model()
    multi_model = await demo_multi_provider_model()
    
    # Compare models
    await demo_model_comparison()
    
    print("\n" + "=" * 50)
    print("📋 Model Options Summary:")
    print("• Qwen (via OpenRouter): Free tier available, great for coding tasks")
    print("• OpenAI: GPT models, very capable and well-documented") 
    print("• Anthropic: Claude models, excellent for reasoning and analysis")
    print("• Ollama: Local models, private and no API costs")
    print("• Multi-Provider: Fallback strategy for reliability")
    
    print("\n💡 Cost Considerations:")
    print("• Qwen (Free): Limited free tier through OpenRouter")
    print("• OpenAI/Anthropic: Pay-per-use based on tokens")
    print("• Ollama: Free (just compute costs for running locally)")
    
    print("\n🔗 API Key Setup:")
    print("• OpenRouter: https://openrouter.ai/keys (includes free Qwen)")
    print("• OpenAI: https://platform.openai.com/api-keys")
    print("• Anthropic: https://console.anthropic.com/settings/keys")
    print("• Ollama: No API key needed, just install locally")

if __name__ == "__main__":
    asyncio.run(main())