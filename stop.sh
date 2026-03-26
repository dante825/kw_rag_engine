#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd /Users/kangwei/development/repo/kw_rag_engine

if [ ! -f .service_pids ]; then
    echo -e "${YELLOW}No PID file found. Checking for orphaned processes...${NC}"

    FRONTEND_PIDS=$(pgrep -f "npm run dev|vite" 2>/dev/null)
    BACKEND_PIDS=$(pgrep -f "python.*backend" 2>/dev/null)

    if [ -n "$FRONTEND_PIDS" ] || [ -n "$BACKEND_PIDS" ]; then
        [ -n "$BACKEND_PIDS" ] && kill $BACKEND_PIDS 2>/dev/null && echo -e "${GREEN}✓ Backend stopped (PIDs: $BACKEND_PIDS)${NC}" || true
        [ -n "$FRONTEND_PIDS" ] && kill $FRONTEND_PIDS 2>/dev/null && echo -e "${GREEN}✓ Frontend stopped (PIDs: $FRONTEND_PIDS)${NC}" || true
        echo -e "${GREEN}✓ Orphaned services stopped${NC}"
    else
        echo -e "${GREEN}No orphaned processes found.${NC}"
    fi
    exit 0
fi

read -r BACKEND_PID FRONTEND_PID < .service_pids

echo -e "${YELLOW}Stopping services...${NC}"

if kill -0 $BACKEND_PID 2>/dev/null; then
    pkill -P $BACKEND_PID 2>/dev/null
    kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✓ Backend stopped (PID: $BACKEND_PID)${NC}" || echo -e "${RED}✗ Failed to stop backend${NC}"
else
    echo -e "${YELLOW}Backend not running (stale PID)${NC}"
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    pkill -P $FRONTEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null && echo -e "${GREEN}✓ Frontend stopped (PID: $FRONTEND_PID)${NC}" || echo -e "${RED}✗ Failed to stop frontend${NC}"
else
    echo -e "${YELLOW}Frontend not running (stale PID)${NC}"
fi

rm -f .service_pids
echo -e "${GREEN}✓ All services stopped${NC}"
