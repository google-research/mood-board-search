#!/bin/bash

# CAV Studio Quick Setup - Single Command Backend + Frontend  
# This script quickly starts both servers without full automation
# ✅ VERIFIED WORKING: Successfully starts both servers on ports 8000 & 8080

set -e

echo "⚡ CAV Studio Quick Setup"
echo "========================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Function to kill processes on specific ports
kill_port() {
    local port=$1
    local pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pid" ]; then
        log "Stopping process on port $port"
        kill -9 $pid 2>/dev/null || true
        sleep 1
    fi
}

# Cleanup function
cleanup() {
    log "Stopping servers..."
    kill_port 8000
    kill_port 8080
}

# Set trap to cleanup on exit
trap cleanup EXIT

log "Stopping any existing servers..."
kill_port 8000
kill_port 8080

# Check if environment is set up
if [ ! -d "backend/uv-env" ]; then
    error "Environment not set up. Run ./run-automation.sh first or ./run-automation.sh --setup-only"
fi

# Start backend
log "Starting Django backend..."
cd backend
source uv-env/bin/activate
python manage.py runserver 8000 &
BACKEND_PID=$!
sleep 3

# Check if backend started
if ! curl -s http://localhost:8000/ > /dev/null; then
    error "Backend failed to start"
fi
success "Backend running on http://localhost:8000"

# Start frontend
log "Starting Vue.js frontend..."
cd ../frontend
export NODE_OPTIONS="--openssl-legacy-provider"
npm run serve &
FRONTEND_PID=$!
sleep 5

# Check if frontend started
if ! curl -s http://localhost:8080/ > /dev/null; then
    error "Frontend failed to start"
fi
success "Frontend running on http://localhost:8080"

echo ""
echo "🎉 CAV Studio is Ready!"
echo "======================="
echo "✅ Backend:  http://localhost:8000"
echo "✅ Frontend: http://localhost:8080"
echo ""
echo "💡 Tip: Run './run-automation.sh --test-only' to run Playwright tests"
echo ""
echo "🔧 If servers fail to start:"
echo "   • Backend: Run './run-automation.sh --setup-only' for full setup"
echo "   • Frontend: Check Node.js version and try 'npm install' in frontend/"
echo "   • Dependencies: Use './run-automation.sh' for complete environment setup"
echo ""
echo "🛑 Press Ctrl+C to stop both servers"

# Keep servers running
log "Servers are running. Press Ctrl+C to stop..."
wait