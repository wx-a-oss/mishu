#!/bin/bash
set -euo pipefail

# ============================================================
# Mishu — First-time setup script for Mac Mini
# Run this ONCE after cloning the repo on your Mac Mini.
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST_NAME="com.mishu.agent.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

echo "==> Setting up Mishu at: $PROJECT_DIR"

# 1. Create Python virtual environment
echo "==> Creating Python virtual environment..."
cd "$PROJECT_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 2. Install Playwright browsers
echo "==> Installing Playwright Chromium..."
playwright install chromium

# 3. Install frontend dependencies and build
echo "==> Building frontend..."
cd "$PROJECT_DIR/frontend"
npm install
npm run build

# 4. Create .env if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo "==> Creating .env from template..."
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo "    ** IMPORTANT: Edit .env and add your OPENAI_API_KEY **"
fi

# 5. Create credentials.json if it doesn't exist
if [ ! -f "$PROJECT_DIR/credentials.json" ]; then
    echo "==> Creating credentials.json from template..."
    cp "$PROJECT_DIR/credentials.json.example" "$PROJECT_DIR/credentials.json"
    echo "    ** IMPORTANT: Edit credentials.json with real credentials **"
fi

# 6. Create workspace directory
mkdir -p "$PROJECT_DIR/workspace"

# 7. Generate and install launchd plist
echo "==> Installing launchd service..."
mkdir -p "$LAUNCH_AGENTS_DIR"

VENV_PYTHON="$PROJECT_DIR/venv/bin/python"
UVICORN="$PROJECT_DIR/venv/bin/uvicorn"
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOG_DIR"

cat > "$LAUNCH_AGENTS_DIR/$PLIST_NAME" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mishu.agent</string>

    <key>ProgramArguments</key>
    <array>
        <string>${UVICORN}</string>
        <string>backend.main:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8000</string>
    </array>

    <key>WorkingDirectory</key>
    <string>${PROJECT_DIR}</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>${LOG_DIR}/mishu.stdout.log</string>

    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/mishu.stderr.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>${PROJECT_DIR}/venv/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

echo "==> Starting Mishu service..."
launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_NAME" 2>/dev/null || true
launchctl load "$LAUNCH_AGENTS_DIR/$PLIST_NAME"

sleep 3

if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo ""
    echo "============================================"
    echo "  Mishu is running at http://localhost:8000"
    echo "============================================"
else
    echo ""
    echo "WARNING: Mishu may not have started. Check logs:"
    echo "  cat $LOG_DIR/mishu.stderr.log"
fi

echo ""
echo "==> Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your OPENAI_API_KEY"
echo "  2. Edit credentials.json with real website credentials"
echo "  3. Set up the GitHub self-hosted runner (see README)"
echo ""
