# Mishu

An AI agent that takes natural language commands and executes them by controlling your computer — managing files, automating browsers, and driving mouse and keyboard. Powered by LLM function calling with a pluggable provider architecture.

## Features

- **File Operations** — Read, write, update, delete files and manage directories
- **Browser Automation** — Navigate pages, auto-login with stored credentials, scrape content, click, type (Playwright)
- **Desktop Automation** — Mouse clicks, keyboard input, hotkeys, screenshots (PyAutoGUI)
- **Pluggable LLM** — OpenAI out of the box, extensible to Claude, Ollama, and others
- **Multiple Interfaces** — CLI and web UI included, architected for Discord/Telegram
- **Credential Store** — Single `credentials.json` for all website logins
- **Safety Controls** — Configurable directory allowlist, browser headless toggle, PyAutoGUI failsafe

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+

### Install

```bash
# Python dependencies
pip install -r requirements.txt
playwright install chromium

# Frontend dependencies
cd frontend && npm install && cd ..
```

### Configure

```bash
cp .env.example .env
cp credentials.json.example credentials.json
```

Add your OpenAI API key to `.env`:

```
OPENAI_API_KEY=sk-your-key-here
```

### Run

**CLI:**

```bash
python cli.py
```

**Web UI:**

```bash
# Terminal 1 — backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev
```

Open http://localhost:5173.

## Usage Examples

```
> List all files in ./workspace
> Read the file ./workspace/config.yaml
> Open https://github.com and take a screenshot
> Login to github.com
> Create a new file at ./workspace/notes.txt with "Hello World"
```

## Configuration

### Environment Variables (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *(required)* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | Model to use |
| `LLM_PROVIDER` | `openai` | LLM provider (`openai`, extensible) |
| `BROWSER_HEADLESS` | `false` | `true` for invisible browser, `false` to watch it work |
| `ALLOWED_DIRECTORIES` | `./workspace` | Comma-separated paths the agent can access |

### Website Credentials (`credentials.json`)

```json
{
  "sites": {
    "github.com": {
      "url": "https://github.com/login",
      "username_field": "input#login_field",
      "password_field": "input#password",
      "submit_button": "input[type=submit]",
      "username": "your-username",
      "password": "your-password"
    }
  }
}
```

Each site entry needs: `url`, `username_field`, `password_field`, `submit_button` (CSS selectors), `username`, and `password`.

## Project Structure

```
mishu/
├── cli.py                       # CLI entrypoint
├── requirements.txt             # Python dependencies
├── .env                         # API keys & settings (gitignored)
├── credentials.json             # Website credentials (gitignored)
│
├── backend/
│   ├── main.py                  # FastAPI app — WebSocket + static serving
│   ├── config.py                # Settings, credential loading, path validation
│   ├── llm/
│   │   ├── base.py              # BaseLLMProvider abstract class
│   │   ├── openai_provider.py   # OpenAI implementation
│   │   └── registry.py          # Provider factory
│   ├── tools/
│   │   ├── base.py              # BaseTool abstract class
│   │   ├── registry.py          # Tool discovery + dispatch
│   │   ├── file_ops.py          # File & directory operations (6 tools)
│   │   ├── browser.py           # Playwright browser automation (6 tools)
│   │   └── desktop.py           # PyAutoGUI desktop control (5 tools)
│   ├── agent/
│   │   ├── agent.py             # Core loop: user → LLM → tools → repeat
│   │   └── conversation.py      # Message history + system prompt
│   └── interfaces/
│       ├── base.py              # BaseInterface abstract class
│       └── web.py               # WebSocket handler for React UI
│
└── frontend/                    # React + Vite
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx              # Chat layout
        ├── components/
        │   ├── ChatMessage.jsx  # Message bubbles
        │   ├── ChatInput.jsx    # Input + send
        │   └── ToolStatus.jsx   # Live tool execution indicator
        └── hooks/
            └── useWebSocket.js  # WebSocket connection + state
```

## Deployment

### Production (Single Server)

```bash
cd frontend && npm run build && cd ..
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The backend auto-serves the built frontend at http://localhost:8000.

### Docker

```bash
docker build -t mishu .
docker run -p 8000:8000 --env-file .env -v ./credentials.json:/app/credentials.json mishu
```

> **Note:** Desktop automation (PyAutoGUI) requires a display server and won't work in a headless container. Browser automation works in headless mode.

### systemd

```ini
[Unit]
Description=Mishu AI Agent
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/mishu
ExecStart=/path/to/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always
EnvironmentFile=/path/to/mishu/.env

[Install]
WantedBy=multi-user.target
```

## Extending

### Add a New LLM Provider

1. Create `backend/llm/your_provider.py` — subclass `BaseLLMProvider`
2. Register in `backend/llm/registry.py`
3. Set `LLM_PROVIDER=your_provider` in `.env`

### Add a New Tool

1. Create a class in `backend/tools/` — subclass `BaseTool`
2. Define `name`, `description`, `parameters` (JSON Schema), and `execute()`
3. Register in `backend/tools/registry.py`

Tools are auto-discovered by the LLM via function calling schemas.

### Add a New Interface (Discord, Telegram, etc.)

1. Create `backend/interfaces/your_interface.py` — subclass `BaseInterface`
2. Instantiate `Agent` with a provider and wire up message passing
3. The agent core is interface-agnostic

## Ports

| Service | Port | URL |
|---------|------|-----|
| FastAPI backend | 8000 | http://localhost:8000 |
| Vite dev server | 5173 | http://localhost:5173 |
| WebSocket | 8000 | ws://localhost:8000/ws |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `OPENAI_API_KEY not set` | Copy `.env.example` to `.env` and add your key |
| Playwright browser not found | Run `playwright install chromium` |
| File access denied | Add the directory to `ALLOWED_DIRECTORIES` in `.env` |
| WebSocket won't connect | Ensure backend is running on port 8000 |
| PyAutoGUI fails on macOS | Grant accessibility permissions: System Settings > Privacy & Security > Accessibility |
| Browser login fails | Verify CSS selectors in `credentials.json` match the login page |

## License

MIT
