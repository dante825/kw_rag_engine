#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /Users/kangwei/development/repo/kw_rag_engine

if [ ! -f .service_pids ]; then
    echo -e "${YELLOW}No PID file found.${NC}"
    exit 0
fi

read -r BACKEND_PID FRONTEND_PID < .service_pids

echo "=== Service Status ==="
echo

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Backend  - Running (PID: $BACKEND_PID, port 8000)"
else
    echo -e "${RED}✗${NC} Backend  - Not running (stale PID: $BACKEND_PID)"
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Frontend - Running (PID: $FRONTEND_PID, port 5173)"
else
    echo -e "${RED}✗${NC} Frontend - Not running (stale PID: $FRONTEND_PID)"
fi

echo
echo "=== Log Files ==="
[ -f backend.log ] && echo "Backend:  tail -f backend.log"
[ -f frontend.log ] && echo "Frontend: tail -f frontend.log"
