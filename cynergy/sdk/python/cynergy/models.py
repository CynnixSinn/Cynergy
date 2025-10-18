"""LLM Model Implementations with enhanced features from both versions"""
import os
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)


class OpenAIModel:
    def __init__(self, model: str = "gpt-4", api_key: Optional[str] = None, 
                 temperature: float = 0.7, max_tokens: Optional[int] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise ValueError("OpenAI API key not provided")

    async def generate(self, messages, tools=None, **kwargs):
        try:
            import openai
            openai.api_key = self.api_key

            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            openai_tools = None
            if tools:
                openai_tools = [
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

            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=openai_messages,
                tools=openai_tools,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                **kwargs
            )

            message = response.choices[0].message

            from cynergy.core.agent import ToolCall, AgentResponse
            tool_calls = []
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls = [
                    ToolCall(
                        tool_name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                        call_id=tc.id
                    )
                    for tc in message.tool_calls
                ]

            return AgentResponse(
                content=message.content or "",
                tool_calls=tool_calls
            )
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        except Exception as e:
            logger.error(f"Error with OpenAI API: {e}")
            raise


class AnthropicModel:
    def __init__(self, model: str = "claude-sonnet-4-5-20250929", 
                 api_key: Optional[str] = None, temperature: float = 0.7, 
                 max_tokens: int = 4096):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not self.api_key:
            raise ValueError("Anthropic API key not provided")

    async def generate(self, messages, tools=None, **kwargs):
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.api_key)

            system_msg = next((m.content for m in messages if m.role == "system"), None)
            user_messages = [
                {"role": m.role, "content": m.content}
                for m in messages if m.role != "system"
            ]

            anthropic_tools = None
            if tools:
                anthropic_tools = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.parameters or {"type": "object", "properties": {}}
                    }
                    for tool in tools
                ]

            response = await client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_msg,
                messages=user_messages,
                tools=anthropic_tools,
                **kwargs
            )

            from cynergy.core.agent import ToolCall, AgentResponse
            content = ""
            tool_calls = []

            for block in response.content:
                if block.type == "text":
                    content += block.text
                elif block.type == "tool_use":
                    tool_calls.append(ToolCall(
                        tool_name=block.name,
                        arguments=block.input,
                        call_id=block.id
                    ))

            return AgentResponse(content=content, tool_calls=tool_calls)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            logger.error(f"Error with Anthropic API: {e}")
            raise


# Import OpenRouter models if available
try:
    from cynergy.models.openrouter import OpenRouterModel, QwenModel, OllamaModel, MultiProviderModel
except ImportError:
    # Define placeholder classes if dependencies are not available
    class OpenRouterModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("OpenRouter dependencies not installed. Run: pip install aiohttp")
    
    class QwenModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("OpenRouter dependencies not installed. Run: pip install aiohttp")
    
    class OllamaModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("OpenRouter dependencies not installed. Run: pip install aiohttp")
    
    class MultiProviderModel:
        def __init__(self, *args, **kwargs):
            raise ImportError("OpenRouter dependencies not installed. Run: pip install aiohttp")