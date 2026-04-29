import asyncio
import json

from backend.agent.agent import Agent
from backend.llm.registry import get_provider

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"


async def _on_tool_start(name: str, args: dict):
    args_short = json.dumps(args, ensure_ascii=False)
    if len(args_short) > 80:
        args_short = args_short[:80] + "..."
    print(f"  {DIM}{YELLOW}[Tool] {name}({args_short}){RESET}")


async def _on_tool_end(name: str, result: str):
    preview = result[:120].replace("\n", " ")
    if len(result) > 120:
        preview += "..."
    print(f"  {DIM}{GREEN}  → {preview}{RESET}")


async def main():
    print(f"{BOLD}{CYAN}Mishu{RESET} — AI Agent with Computer Use")
    print(f"{DIM}Type 'exit' or 'quit' to stop. Ctrl+C also works.{RESET}\n")

    provider = get_provider()
    agent = Agent(provider, on_tool_start=_on_tool_start, on_tool_end=_on_tool_end)

    while True:
        try:
            user_input = input(f"{BOLD}> {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{DIM}Goodbye!{RESET}")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print(f"{DIM}Goodbye!{RESET}")
            break

        try:
            response = await agent.run(user_input)
            print(f"\n{CYAN}Mishu:{RESET} {response}\n")
        except Exception as e:
            print(f"\n{YELLOW}Error: {e}{RESET}\n")


if __name__ == "__main__":
    asyncio.run(main())
