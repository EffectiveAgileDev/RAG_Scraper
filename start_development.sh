#!/bin/bash
# Development startup script for RAG_Scraper
# This script sets development-appropriate log levels and environment variables

# Set development environment variables
export LOG_LEVEL=DEBUG
export FLASK_ENV=development
export PYTHONUNBUFFERED=1

# Start the server using the existing control script
echo "Starting RAG_Scraper in development mode..."
echo "Log level: $LOG_LEVEL"
echo "Flask environment: $FLASK_ENV"
echo ""

./server_control.sh start