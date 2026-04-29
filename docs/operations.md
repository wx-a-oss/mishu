# Mishu — Operations Guide

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm

### 1. Install Dependencies

```bash
# Python
pip install -r requirements.txt
playwright install chromium

# Frontend
cd frontend && npm install
```

### 2. Configure

```bash
cp .env.template .env
cp credentials.json.template credentials.json
```

Edit `.env`:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
LLM_PROVIDER=openai
BROWSER_HEADLESS=false
ALLOWED_DIRECTORIES=./workspace,~/Documents
```

Edit `credentials.json` with real website credentials (see Credential Management below).

### 3. Run

**CLI mode:**

```bash
python cli.py
```

**Web UI mode (two terminals):**

```bash
# Terminal 1 — backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend dev server
cd frontend && npm run dev
```

Open http://localhost:5173 in your browser.

---

## Project File Map

```
mishu/
├── cli.py                          # CLI entrypoint
├── requirements.txt                # Python dependencies
├── .env                            # API keys & settings (gitignored)
├── .env.example                    # Template for .env
├── credentials.json                # Website login credentials (gitignored)
├── credentials.json.example        # Template for credentials.json
├── .gitignore
├── CLAUDE.md                       # Project conventions for Claude Code
│
├── backend/
│   ├── main.py                     # FastAPI app — WebSocket + static serving
│   ├── config.py                   # Settings loader — .env, credentials, path validation
│   │
│   ├── llm/                        # LLM provider abstraction
│   │   ├── base.py                 # BaseLLMProvider abstract class + data types
│   │   ├── openai_provider.py      # OpenAI API implementation
│   │   └── registry.py             # Provider factory — get_provider()
│   │
│   ├── tools/                      # Agent tools (called by LLM)
│   │   ├── base.py                 # BaseTool abstract class
│   │   ├── registry.py             # Tool discovery, schema generation, dispatch
│   │   ├── file_ops.py             # read_file, write_file, update_file, delete_file, list_directory, create_directory
│   │   ├── browser.py              # open_url, login_website, get_page_content, click_element, type_text, take_screenshot
│   │   └── desktop.py              # mouse_click, mouse_move, type_keyboard, press_hotkey, take_desktop_screenshot
│   │
│   ├── agent/
│   │   ├── agent.py                # Core agent loop — LLM ↔ tool execution cycle
│   │   └── conversation.py         # Message history + system prompt
│   │
│   └── interfaces/
│       ├── base.py                 # BaseInterface abstract class
│       └── web.py                  # WebSocket handler for React UI
│
└── frontend/                       # React + Vite
    ├── index.html                  # HTML shell
    ├── package.json                # Node dependencies
    ├── vite.config.js              # Vite config — dev proxy to backend
    └── src/
        ├── main.jsx                # React entrypoint
        ├── index.css               # Global styles + CSS variables
        ├── App.jsx                 # Main chat layout
        ├── App.css                 # Layout styles
        ├── components/
        │   ├── ChatMessage.jsx     # User/assistant message bubble
        │   ├── ChatMessage.css
        │   ├── ChatInput.jsx       # Text input + send button
        │   ├── ChatInput.css
        │   ├── ToolStatus.jsx      # "Running: tool_name..." indicator
        │   └── ToolStatus.css
        └── hooks/
            └── useWebSocket.js     # WebSocket connection + state management
```

---

## Configuration Reference

### .env Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o` | OpenAI model to use |
| `LLM_PROVIDER` | `openai` | LLM provider name (extensible) |
| `BROWSER_HEADLESS` | `false` | `true` = invisible browser, `false` = visible window |
| `ALLOWED_DIRECTORIES` | `./workspace` | Comma-separated paths the agent can access |

### credentials.json Schema

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

Each site entry requires:
- `url` — the login page URL
- `username_field` — CSS selector for the username/email input
- `password_field` — CSS selector for the password input
- `submit_button` — CSS selector for the submit/login button
- `username` — your username or email
- `password` — your password

---

## Deployment (Mac Mini)

### First-Time Setup

```bash
git clone https://github.com/YOUR_USER/mishu.git ~/mishu
cd ~/mishu
./scripts/setup.sh
```

The setup script:
1. Creates a Python venv and installs dependencies
2. Installs Playwright Chromium
3. Builds the React frontend
4. Creates `.env` and `credentials.json` from templates
5. Generates and installs a launchd plist at `~/Library/LaunchAgents/com.mishu.agent.plist`
6. Starts the Mishu service

After setup, edit your config:
```bash
nano ~/mishu/.env              # Add OPENAI_API_KEY
nano ~/mishu/credentials.json  # Add real website credentials
```

### CI/CD — Auto-Deploy on Push

Uses a GitHub Actions self-hosted runner on the Mac Mini.

**Setup steps:**

1. Push repo to GitHub
2. Go to repo → Settings → Actions → Runners → New self-hosted runner (macOS)
3. Follow GitHub's commands on your Mac Mini to install the runner
4. Install the runner as a service: `./svc.sh install && ./svc.sh start`
5. Set the deploy path: `echo "MISHU_DIR=$HOME/mishu" >> ~/actions-runner/.env`

**What happens on each push to `main`:**
1. GitHub Actions workflow triggers
2. Self-hosted runner on Mac Mini picks up the job
3. Pulls latest code via `git fetch + reset --hard`
4. Installs Python deps, rebuilds frontend
5. Restarts the launchd service
6. Runs health check on `http://localhost:8000/health`

**Workflow file:** `.github/workflows/deploy.yml`
**Manual deploy:** `./scripts/deploy.sh`

### Service Management (launchd)

```bash
# View status
launchctl list | grep mishu

# Stop
launchctl unload ~/Library/LaunchAgents/com.mishu.agent.plist

# Start
launchctl load ~/Library/LaunchAgents/com.mishu.agent.plist

# View logs
tail -f ~/mishu/logs/mishu.stdout.log
tail -f ~/mishu/logs/mishu.stderr.log
```

The service auto-starts on boot and auto-restarts on crash (KeepAlive = true).

---

## Common Operations

### Add a New Website to Credentials

Edit `credentials.json`, add an entry under `sites`:

```json
"twitter.com": {
  "url": "https://twitter.com/login",
  "username_field": "input[name='text']",
  "password_field": "input[name='password']",
  "submit_button": "button[data-testid='LoginForm_Login_Button']",
  "username": "your-handle",
  "password": "your-password"
}
```

Then tell the agent: "login to twitter.com"

### Add a New Allowed Directory

Edit `.env`, append to `ALLOWED_DIRECTORIES`:

```
ALLOWED_DIRECTORIES=./workspace,~/Documents,~/Projects
```

Restart the backend.

### Switch to a Different OpenAI Model

Edit `.env`:

```
OPENAI_MODEL=gpt-4o-mini
```

Restart the backend.

### Add a New LLM Provider

1. Create `backend/llm/your_provider.py` — subclass `BaseLLMProvider`
2. Register in `backend/llm/registry.py` — add to `PROVIDERS` dict
3. Set `LLM_PROVIDER=your_provider` in `.env`

### Add a New Tool

1. Create a class in `backend/tools/` — subclass `BaseTool`
2. Define `name`, `description`, `parameters` (JSON Schema), and `execute()`
3. Import and register in `backend/tools/registry.py`

The LLM auto-discovers new tools via function calling schemas.

---

## Ports

| Service | Port | URL |
|---------|------|-----|
| FastAPI backend | 8000 | http://localhost:8000 |
| Vite dev server | 5173 | http://localhost:5173 |
| WebSocket | 8000 | ws://localhost:8000/ws |

In dev mode, Vite proxies `/ws` to the backend automatically (configured in `vite.config.js`).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `OPENAI_API_KEY not set` | Copy `.env.example` to `.env` and add your key |
| Playwright browser not found | Run `playwright install chromium` |
| File access denied | Add the directory to `ALLOWED_DIRECTORIES` in `.env` |
| WebSocket won't connect | Make sure backend is running on port 8000 |
| PyAutoGUI fails on macOS | Grant Terminal/IDE accessibility permissions in System Settings → Privacy & Security → Accessibility |
| Browser login fails | Check CSS selectors in `credentials.json` match the actual login page |
