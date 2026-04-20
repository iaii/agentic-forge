#!/bin/bash

# First attempt to find explicitly named uvicorn instances
PIDS=$(pgrep -f "backend.main:app")

# Second attempt: Check exactly what is holding our port 18564
PORT_PIDS=$(lsof -ti :18564)

if [ -z "$PIDS" ] && [ -z "$PORT_PIDS" ]; then
    echo "No active uvicorn or port processes found."
else
    echo "Conflicting processes found. Executing kill orders..."
    
    # 1. Kill by process name pattern
    if [ ! -z "$PIDS" ]; then
        pkill -9 -f "backend.main:app"
    fi
    
    # 2. Kill by actual socket usage
    if [ ! -z "$PORT_PIDS" ]; then
        # Loop over PIDs ignoring errors
        for PID in $PORT_PIDS; do
            kill -9 $PID 2>/dev/null
        done
    fi
    
    echo "All conflicting processes have been forcefully terminated."
fi
