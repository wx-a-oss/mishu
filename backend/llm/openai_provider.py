import json

from openai import AsyncOpenAI

from backend.config import get_config
from backend.llm.base import BaseLLMProvider, LLMResponse, ToolCall


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        config = get_config()
        self.client = AsyncOpenAI(api_key=config.openai_api_key)
        self.model = config.openai_model

    async def chat(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        kwargs = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = [
                {"type": "function", "function": t} for t in tools
            ]

        response = await self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message

        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                ))

        return LLMResponse(text=message.content, tool_calls=tool_calls)
