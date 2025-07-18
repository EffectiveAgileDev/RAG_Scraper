#!/bin/bash
# Persistent Flask server startup script

# Kill any existing Flask processes
pkill -f "python.*run_app" 2>/dev/null

# Navigate to project directory
cd /home/rod/AI/Projects/RAG_Scraper

# Activate virtual environment
source venv/bin/activate

# Export Flask environment variables
export FLASK_APP=src.web_interface.app_factory
export PYTHONUNBUFFERED=1

# Set default log level if not already set
if [ -z "$LOG_LEVEL" ]; then
    export LOG_LEVEL=INFO
fi

# Create log directory if it doesn't exist
mkdir -p logs

# Start Flask with proper error handling and logging
echo "Starting RAG_Scraper server..."
echo "Server will run at: http://localhost:8085"
echo "Logs: logs/server.log"

# Use nohup to keep server running in background
nohup python run_app.py >> logs/server.log 2>&1 &

# Show the PID and wait a moment to ensure startup
echo "Server starting in background..."
sleep 2
echo "Server PID: $(pgrep -f 'python.*run_app')"
echo "Use 'pkill -f python.*run_app' to stop"