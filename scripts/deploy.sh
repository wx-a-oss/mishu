#!/bin/bash
set -euo pipefail

# ============================================================
# Mishu — Manual deploy script
# Use this to deploy manually if needed. The GitHub Actions
# workflow calls equivalent steps automatically.
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PLIST="$HOME/Library/LaunchAgents/com.mishu.agent.plist"

echo "==> Deploying Mishu..."

cd "$PROJECT_DIR"

echo "==> Pulling latest code..."
git fetch origin main
git reset --hard origin/main

echo "==> Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "==> Building frontend..."
cd "$PROJECT_DIR/frontend"
npm install
npm run build

echo "==> Restarting service..."
launchctl unload "$PLIST" 2>/dev/null || true
sleep 2
launchctl load "$PLIST"

sleep 5

if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    echo "==> Deploy complete. Mishu is healthy."
else
    echo "==> WARNING: Health check failed. Check logs:"
    echo "    cat $PROJECT_DIR/logs/mishu.stderr.log"
    exit 1
fi
