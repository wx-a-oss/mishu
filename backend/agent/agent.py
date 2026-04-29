from typing import Callable, Awaitable

from backend.agent.conversation import Conversation
from backend.llm.base import BaseLLMProvider
from backend.tools.registry import get_tool_schemas, execute_tool

MAX_ITERATIONS = 10

OnToolStart = Callable[[str, dict], Awaitable[None]]
OnToolEnd = Callable[[str, str], Awaitable[None]]


class Agent:
    def __init__(
        self,
        provider: BaseLLMProvider,
        on_tool_start: OnToolStart | None = None,
        on_tool_end: OnToolEnd | None = None,
    ):
        self.provider = provider
        self.conversation = Conversation()
        self.on_tool_start = on_tool_start
        self.on_tool_end = on_tool_end

    async def run(self, user_message: str) -> str:
        self.conversation.add_user_message(user_message)
        tools = get_tool_schemas()

        for _ in range(MAX_ITERATIONS):
            response = await self.provider.chat(self.conversation.get_messages(), tools)

            if not response.tool_calls:
                text = response.text or ""
                if text:
                    self.conversation.add_assistant_message(text)
                return text

            raw_tool_calls = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": str(tc.arguments)},
                }
                for tc in response.tool_calls
            ]
            self.conversation.add_assistant_tool_calls(raw_tool_calls)

            for tc in response.tool_calls:
                if self.on_tool_start:
                    await self.on_tool_start(tc.name, tc.arguments)

                result = await execute_tool(tc.name, tc.arguments)

                if self.on_tool_end:
                    await self.on_tool_end(tc.name, result)

                self.conversation.add_tool_result(tc.id, result)

        return "I've reached the maximum number of tool calls for this request. Please provide further instructions."
