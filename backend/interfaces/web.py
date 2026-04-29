import json

from fastapi import WebSocket, WebSocketDisconnect

from backend.agent.agent import Agent
from backend.llm.registry import get_provider

_agents: dict[str, Agent] = {}


async def websocket_handler(websocket: WebSocket):
    await websocket.accept()
    session_id = str(id(websocket))

    async def on_tool_start(name: str, args: dict):
        await websocket.send_json({
            "type": "tool_start",
            "data": {"name": name, "args": args},
        })

    async def on_tool_end(name: str, result: str):
        preview = result[:500]
        await websocket.send_json({
            "type": "tool_end",
            "data": {"name": name, "result": preview},
        })

    provider = get_provider()
    agent = Agent(provider, on_tool_start=on_tool_start, on_tool_end=on_tool_end)
    _agents[session_id] = agent

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            user_message = msg.get("message", "")

            if not user_message:
                continue

            try:
                response = await agent.run(user_message)
                await websocket.send_json({
                    "type": "assistant_message",
                    "data": {"text": response},
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"text": f"{type(e).__name__}: {e}"},
                })
    except WebSocketDisconnect:
        _agents.pop(session_id, None)
