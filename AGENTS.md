# Mishu — AI Agent with Computer Use

## Project Overview
LLM-driven agent that controls the computer (files, browser, mouse/keyboard) via CLI and web UI.

## Tech Stack
- Backend: Python 3.11+, FastAPI, uvicorn
- LLM: OpenAI API (extensible via provider abstraction)
- Browser: Playwright
- Desktop: PyAutoGUI
- Frontend: React + Vite

## Commands
- `pip install -r requirements.txt` — install Python deps
- `cd frontend && npm install` — install frontend deps
- `python cli.py` — run CLI
- `uvicorn backend.main:app --reload` — run backend
- `cd frontend && npm run dev` — run frontend dev server

## Architecture
- `backend/llm/` — LLM provider abstraction (add new providers in registry.py)
- `backend/tools/` — Agent tools (add new tools by subclassing BaseTool)
- `backend/agent/` — Core agent loop
- `backend/interfaces/` — UI adapters (CLI, web, future: Discord/Telegram)

## Conventions
- All tools inherit from `BaseTool` and are auto-discovered
- All LLM providers inherit from `BaseLLMProvider`
- Config loaded from `.env` + `credentials.json`
- File operations restricted to `ALLOWED_DIRECTORIES`
