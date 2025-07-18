#!/bin/bash
# Production startup script for RAG_Scraper
# This script sets production-appropriate log levels and environment variables

# Set production environment variables
export LOG_LEVEL=WARNING
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

# Start the server using the existing control script
echo "Starting RAG_Scraper in production mode..."
echo "Log level: $LOG_LEVEL"
echo "Flask environment: $FLASK_ENV"
echo ""

./server_control.sh start