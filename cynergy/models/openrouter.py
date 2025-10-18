"""OpenRouter Model Implementations for Cynergy with Qwen/Qwen3-Coder support"""
import os
from typing import Optional, List, Dict, Any
import json
import logging
import aiohttp

logger = logging.getLogger(__name__)


class OpenRouterModel:
    def __init__(self, model: str = "qwen/qwen3-coder", api_key: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: Optional[int] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise ValueError("OpenRouter API key not provided. Set OPENROUTER_API_KEY environment variable or pass api_key parameter.")

    async def generate(self, messages, tools=None, **kwargs):
        """
        Generate a response from the OpenRouter API
        """
        try:
            # Prepare the request payload
            openrouter_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Prepare tools for OpenRouter API
            openrouter_tools = None
            if tools:
                openrouter_tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters or {"type": "object", "properties": {}}
                        }
                    }
                    for tool in tools
                ]

            # Prepare the payload
            payload = {
                "model": self.model,
                "messages": openrouter_messages,
                "temperature": self.temperature,
            }

            if self.max_tokens:
                payload["max_tokens"] = self.max_tokens

            if openrouter_tools:
                payload["tools"] = openrouter_tools

            # Add any additional kwargs
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value

            # Make the API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/cynergy-ai/cynergy",  # Optional: for analytics
                "X-Title": "Cynergy Framework"  # Optional: for analytics
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        raise Exception(f"OpenRouter API error: {response.status} - {error_text}")
                    
                    response_data = await response.json()

            # Extract the content and tool calls from the response
            choices = response_data.get("choices", [])
            if not choices:
                raise Exception("No choices returned from OpenRouter API")

            message = choices[0].get("message", {})
            content = message.get("content", "")

            from cynergy.core.agent import ToolCall, AgentResponse
            tool_calls = []

            # Handle tool calls
            if "tool_calls" in message and message["tool_calls"]:
                for tc in message["tool_calls"]:
                    try:
                        arguments = tc["function"].get("arguments", "{}")
                        if isinstance(arguments, str):
                            try:
                                arguments = json.loads(arguments)
                            except json.JSONDecodeError:
                                # If JSON parsing fails, pass it as a string
                                arguments = {"arguments_str": arguments}

                        tool_calls.append(
                            ToolCall(
                                tool_name=tc["function"]["name"],
                                arguments=arguments,
                                call_id=tc.get("id", str(hash(tc["function"]["name"]))),
                            )
                        )
                    except (KeyError, TypeError) as e:
                        logger.warning(f"Error parsing tool call: {e}")
                        continue

            return AgentResponse(
                content=content,
                tool_calls=tool_calls
            )
        except Exception as e:
            logger.error(f"Error with OpenRouter API: {e}")
            raise


class QwenModel(OpenRouterModel):
    """
    Specialized model class for Qwen models via OpenRouter
    """
    def __init__(self, model: str = "qwen/qwen3-coder", api_key: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: Optional[int] = None):
        # Default to the free Qwen3-Coder model
        if model == "qwen/qwen3-coder":
            model = "qwen/qwen-3.5-coder:free"  # Use the free tier if available
            
        super().__init__(model=model, api_key=api_key, temperature=temperature, max_tokens=max_tokens)


class OllamaModel:
    """
    Local model support through Ollama
    """
    def __init__(self, model: str = "llama3", temperature: float = 0.7, 
                 max_tokens: Optional[int] = None, base_url: str = "http://localhost:11434"):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.base_url = base_url.rstrip('/')

    async def generate(self, messages, tools=None, **kwargs):
        """
        Generate response from local Ollama instance
        """
        try:
            # Prepare the request payload
            formatted_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": self.temperature,
                "stream": False
            }

            if self.max_tokens:
                payload["options"] = {"num_predict": self.max_tokens}

            # Add any additional kwargs
            for key, value in kwargs.items():
                if key not in payload:
                    payload[key] = value

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status} - {error_text}")
                        raise Exception(f"Ollama API error: {response.status} - {error_text}")
                    
                    response_data = await response.json()

            content = response_data.get("message", {}).get("content", "")

            from cynergy.core.agent import AgentResponse
            return AgentResponse(content=content, tool_calls=[])
            
        except Exception as e:
            logger.error(f"Error with Ollama API: {e}")
            raise


class MultiProviderModel:
    """
    Model that can switch between different providers based on availability and cost
    """
    def __init__(self, providers: List[Dict[str, Any]]):
        """
        Initialize with a list of providers in order of preference
        Each provider dict should have 'type', 'model', and optional 'config'
        """
        self.providers = providers
        self.current_provider_index = 0
        self.provider_instances = []
        
        for provider_info in providers:
            provider_type = provider_info["type"]
            model_name = provider_info["model"]
            config = provider_info.get("config", {})
            
            if provider_type == "openrouter":
                instance = OpenRouterModel(model=model_name, **config)
            elif provider_type == "ollama":
                instance = OllamaModel(model=model_name, **config)
            elif provider_type == "qwen":
                instance = QwenModel(model=model_name, **config)
            else:
                raise ValueError(f"Unsupported provider type: {provider_type}")
                
            self.provider_instances.append(instance)

    async def generate(self, messages, tools=None, **kwargs):
        """
        Try providers in order until one succeeds
        """
        last_error = None
        
        for i, provider in enumerate(self.provider_instances):
            try:
                return await provider.generate(messages, tools=tools, **kwargs)
            except Exception as e:
                logger.warning(f"Provider {i} failed: {e}")
                last_error = e
                continue
        
        # If all providers failed, raise the last error
        raise last_error or Exception("All providers failed")