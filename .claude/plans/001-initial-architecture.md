# Mishu - AI Agent with Computer Use

## Overview
An LLM-driven agent that can control the computer (files, mouse, keyboard, browser) via CLI and web UI, extensible to Discord/Telegram and multiple LLM providers.

## Architecture

```
mishu/
├── backend/                    # Python (FastAPI)
│   ├── main.py                 # FastAPI app entrypoint
│   ├── config.py               # Settings, credential loading
│   ├── credentials.json        # Stored credentials (gitignored)
│   ├── .env                    # API keys (gitignored)
│   │
│   ├── llm/                    # LLM provider abstraction
│   │   ├── base.py             # Abstract LLM interface
│   │   ├── openai_provider.py  # OpenAI implementation
│   │   └── registry.py         # Provider registry (add Claude, etc. later)
│   │
│   ├── tools/                  # Agent tools (called by LLM)
│   │   ├── base.py             # Abstract tool interface
│   │   ├── file_ops.py         # Read, write, update, delete, list files
│   │   ├── browser.py          # Playwright: navigate, login, scrape
│   │   ├── desktop.py          # PyAutoGUI: mouse, keyboard, screenshot
│   │   └── registry.py         # Tool registry
│   │
│   ├── agent/                  # Agent orchestration
│   │   ├── agent.py            # Core agent loop (LLM ↔ tools)
│   │   └── conversation.py     # Conversation/history management
│   │
│   └── interfaces/             # Frontend adapters (extensible)
│       ├── base.py             # Abstract interface
│       ├── cli.py              # Terminal CLI interface
│       ├── web.py              # WebSocket handler for web UI
│       └── (discord.py)        # Future: Discord bot
│       └── (telegram.py)       # Future: Telegram bot
│
├── frontend/                   # Web UI (vanilla HTML/JS or simple React)
│   ├── index.html
│   ├── style.css
│   └── app.js                  # WebSocket chat client
│
├── requirements.txt
├── cli.py                      # CLI entrypoint
└── CLAUDE.md
```

## Implementation Plan (10 steps)

### Step 1: Project scaffolding & dependencies
- Create directory structure
- `requirements.txt`: fastapi, uvicorn, openai, playwright, pyautogui, python-dotenv, websockets
- `.env.example` with required keys
- `.gitignore` for .env, credentials.json, __pycache__
- `CLAUDE.md` with project conventions

### Step 2: Configuration & credential management
- `config.py`: Load `.env` (API keys) and `credentials.json` (website logins)
- `credentials.json` schema: `{ "sites": { "github.com": { "username": "...", "password": "..." } } }`
- Single source of truth for all secrets
- Export to env vars on startup if needed

### Step 3: LLM provider abstraction
- `llm/base.py`: Abstract class with `chat(messages, tools) -> response` and `get_tool_definitions() -> list`
- `llm/openai_provider.py`: OpenAI implementation using function calling
- `llm/registry.py`: `get_provider(name)` factory — add new providers by registering a class
- All providers return a unified response format: `{ "text": str, "tool_calls": list }`

### Step 4: Tool system
- `tools/base.py`: Abstract `Tool` class with `name`, `description`, `parameters` (JSON Schema), `execute(params)`
- `tools/registry.py`: Collects all tools, generates OpenAI function-calling schemas automatically
- Each tool is self-describing — the LLM sees the tool list and decides which to call

### Step 5: File operations tool
- `tools/file_ops.py`: Implements these operations:
  - `read_file(path)` — read file contents
  - `write_file(path, content)` — create/overwrite file
  - `update_file(path, old_text, new_text)` — find & replace in file
  - `delete_file(path)` — delete a file
  - `list_directory(path)` — list files in directory
  - `create_directory(path)` — create directory
- Safety: restrict to a configurable workspace root (no arbitrary system access)

### Step 6: Browser automation tool
- `tools/browser.py`: Playwright-based, implements:
  - `open_url(url)` — navigate to URL
  - `login_website(site_key)` — reads credentials from config, fills login form
  - `get_page_content()` — extract visible text/HTML
  - `click_element(selector)` — click on page element
  - `type_text(selector, text)` — type into input field
  - `screenshot()` — capture current page
- Manages a persistent browser session (reuse across tool calls)
- Login uses credentials from `credentials.json` keyed by site

### Step 7: Desktop automation tool
- `tools/desktop.py`: PyAutoGUI-based, implements:
  - `mouse_click(x, y)` — click at coordinates
  - `mouse_move(x, y)` — move mouse
  - `type_keyboard(text)` — type text
  - `hotkey(keys)` — press key combination (e.g., cmd+c)
  - `screenshot()` — capture screen, return base64
- Safety: add a configurable kill switch (PyAutoGUI failsafe)

### Step 8: Agent core
- `agent/agent.py`: The main loop:
  1. Receive user message
  2. Send to LLM with tool definitions
  3. If LLM returns tool calls → execute tools → send results back to LLM
  4. Repeat until LLM returns a text response
  5. Return response to user
- `agent/conversation.py`: Manages message history, token limits, context window
- Agent is interface-agnostic — CLI, web, and future Discord/Telegram all call the same agent

### Step 9: CLI interface
- `cli.py`: Simple REPL loop
  - `> ` prompt, type message, see response
  - Supports streaming output
  - Shows tool execution status (e.g., "Executing: read_file...")
  - Quit with `exit` or Ctrl+C

### Step 10: Web UI
- `backend/interfaces/web.py`: WebSocket endpoint on FastAPI
- `frontend/index.html`: Single-page chat UI
  - Message input, send button
  - Chat history with user/assistant bubbles
  - Shows tool execution in real-time
  - Responsive design, works on mobile
- WebSocket for real-time bidirectional communication

## Key Design Decisions

1. **Pluggable LLM providers**: Abstract base class → swap OpenAI for Claude/Ollama by adding one file
2. **Self-describing tools**: Each tool declares its own schema → LLM auto-discovers capabilities
3. **Interface-agnostic agent**: The agent core knows nothing about CLI/web/Discord → adding a new frontend is just a thin adapter
4. **Single credential store**: `credentials.json` + `.env` — one place for all secrets
5. **Safety first**: File ops restricted to workspace, PyAutoGUI failsafe enabled, no raw shell exec

## Tech Stack
- **Language**: Python 3.11+
- **Backend**: FastAPI + uvicorn
- **LLM**: OpenAI API (function calling)
- **Browser**: Playwright
- **Desktop**: PyAutoGUI
- **Frontend**: Vanilla HTML/CSS/JS (no build step, simple to start)
- **Communication**: WebSocket (real-time chat)
