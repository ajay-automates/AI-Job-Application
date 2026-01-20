#!/bin/bash

# JobAutomate - Development Startup Script
# Starts all services needed for local development

set -e

echo "🚀 Starting JobAutomate Development Environment"
echo "================================================"

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "⚠️  tmux not found. Starting services in background..."
    
    # Start frontend
    echo "📱 Starting frontend..."
    cd "$SCRIPT_DIR/frontend"
    npm run dev > /tmp/jobautomater-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID (logs: /tmp/jobautomater-frontend.log)"
    
    # Start backend
    echo "🔧 Starting backend..."
    cd "$SCRIPT_DIR/backend"
    source venv/bin/activate 2>/dev/null || true
    python -m app.main > /tmp/jobautomater-backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID (logs: /tmp/jobautomater-backend.log)"
    
    # Start job aggregator
    echo "🤖 Starting job aggregator..."
    cd "$SCRIPT_DIR/../job-application-automator-mcp/job-board-aggregator"
    python run_server.py > /tmp/jobautomater-aggregator.log 2>&1 &
    AGGREGATOR_PID=$!
    echo "   Aggregator PID: $AGGREGATOR_PID (logs: /tmp/jobautomater-aggregator.log)"
    
    echo ""
    echo "✅ All services started!"
    echo ""
    echo "Services:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/api/docs"
    echo "  Aggregator: http://localhost:8080"
    echo ""
    echo "To stop all services:"
    echo "  kill $FRONTEND_PID $BACKEND_PID $AGGREGATOR_PID"
    echo ""
    echo "View logs:"
    echo "  tail -f /tmp/jobautomater-*.log"
    
else
    # Use tmux for better experience
    echo "Using tmux for service management..."
    
    SESSION="jobautomater"
    
    # Kill existing session if it exists
    tmux kill-session -t $SESSION 2>/dev/null || true
    
    # Create new session
    tmux new-session -d -s $SESSION -n "frontend"
    
    # Frontend window
    tmux send-keys -t $SESSION:0 "cd $SCRIPT_DIR/frontend && npm run dev" C-m
    
    # Backend window
    tmux new-window -t $SESSION -n "backend"
    tmux send-keys -t $SESSION:1 "cd $SCRIPT_DIR/backend && source venv/bin/activate && python -m app.main" C-m
    
    # Aggregator window
    tmux new-window -t $SESSION -n "aggregator"
    tmux send-keys -t $SESSION:2 "cd $SCRIPT_DIR/../job-application-automator-mcp/job-board-aggregator && python run_server.py" C-m
    
    echo ""
    echo "✅ All services started in tmux!"
    echo ""
    echo "Services:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/api/docs"
    echo "  Aggregator: http://localhost:8080"
    echo ""
    echo "To attach to tmux session:"
    echo "  tmux attach -t $SESSION"
    echo ""
    echo "To stop all services:"
    echo "  tmux kill-session -t $SESSION"
    echo ""
    echo "Navigate between windows in tmux:"
    echo "  Ctrl+B then 0 (frontend)"
    echo "  Ctrl+B then 1 (backend)"
    echo "  Ctrl+B then 2 (aggregator)"
    echo ""
    
    # Attach to session
    tmux attach -t $SESSION
fi
