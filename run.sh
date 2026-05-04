#!/bin/bash
set -e

echo "=== ChataBot ==="

# Backend
cd /root/ChataBot/backend
pip install -r requirements.txt -q

# Start FastAPI
uvicorn api:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Start scraper scheduler
python main.py &
SCRAPER_PID=$!

# Frontend
cd /root/ChataBot/frontend
npm install --silent
npm run dev &
FRONTEND_PID=$!

echo "API:      http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop."

trap "kill $API_PID $SCRAPER_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
