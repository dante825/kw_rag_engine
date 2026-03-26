#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="/Users/kangwei/development/repo/kw_rag_engine"

cd "$PROJECT_DIR" || exit 1

if [ -f .service_pids ]; then
    echo -e "${YELLOW}Services may already be running. Use ./stop.sh first.${NC}"
    exit 1
fi

if [ ! -d "backend" ]; then
    echo -e "${RED}Error: backend directory not found${NC}"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo -e "${RED}Error: frontend directory not found${NC}"
    exit 1
fi

(
    cd backend
    PYTHONPATH="$PROJECT_DIR" /Users/kangwei/opt/anaconda3/envs/data_protector/bin/python -u -m backend.main 2>&1 | while IFS= read -r line; do
        echo "$(date '+%Y-%m-%d %H:%M:%S') $line"
    done > "$PROJECT_DIR/backend.log"
) &
BACKEND_PID=$!

(cd frontend && npm run dev > "$PROJECT_DIR/frontend.log" 2>&1) &
FRONTEND_PID=$!

echo "$BACKEND_PID $FRONTEND_PID" > .service_pids

sleep 2

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID, port 8000)${NC}"
else
    echo -e "${RED}✗ Backend failed to start (PID: $BACKEND_PID)${NC}"
fi

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID, port 5173)${NC}"
else
    echo -e "${RED}✗ Frontend failed to start (PID: $FRONTEND_PID)${NC}"
fi

echo -e "${YELLOW}PIDs saved to .service_pids${NC}"
