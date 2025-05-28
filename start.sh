#!/bin/bash

# Colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${GREEN}   Smart AI Learning Platform Starter   ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Detect OS for proper terminal commands
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    TERMINAL_CMD="start"
    ACTIVATE_ENV="source .venv/Scripts/activate"
    CHECK_ENV_EXISTS="if exist .venv (echo Found virtual environment) else (echo Creating virtual environment... && python -m venv .venv)"
    OPEN_URL="start http://localhost:3000"
else
    # macOS/Linux
    TERMINAL_CMD="open -a Terminal"
    ACTIVATE_ENV="source .venv/bin/activate"
    CHECK_ENV_EXISTS="if [ -d \".venv\" ]; then echo Found virtual environment; else echo Creating virtual environment...; python3 -m venv .venv; fi"
    OPEN_URL="open http://localhost:3000"
fi

# Move to the project root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo -e "${YELLOW}Starting backend server...${NC}"

# Start backend in a new terminal window
cd "$ROOT_DIR/backend"
$TERMINAL_CMD <<EOF
cd "$ROOT_DIR/backend"
echo "Starting backend server..."
$CHECK_ENV_EXISTS
$ACTIVATE_ENV
pip install -r requirements.txt
echo "Backend server starting at http://127.0.0.1:8000"
uvicorn main:app --reload
EOF

echo -e "${YELLOW}Starting frontend development server...${NC}"

# Start frontend in a new terminal window
cd "$ROOT_DIR/frontend"
$TERMINAL_CMD <<EOF
cd "$ROOT_DIR/frontend"
echo "Starting frontend development server..."
npm install
echo "Frontend server starting at http://localhost:3000"
npm run dev
EOF

echo -e "${GREEN}Starting the application...${NC}"
echo -e "${BLUE}Backend API: ${NC}http://127.0.0.1:8000"
echo -e "${BLUE}Frontend:   ${NC}http://localhost:3000"

# Wait a moment for servers to start
sleep 5

# Open the application in the default browser
echo -e "${YELLOW}Opening application in browser...${NC}"
$OPEN_URL

echo -e "${GREEN}Application started successfully!${NC}"
echo -e "${YELLOW}Press Ctrl+C in terminal windows to stop the servers${NC}"