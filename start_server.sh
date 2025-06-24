#!/bin/bash

# RAG Scraper Server Startup Script
# This script starts the Flask web server for the RAG Scraper application

echo "========================================"
echo "  RAG Scraper Server Startup"
echo "========================================"
echo ""
echo "🚀 Starting server..."
echo ""
echo "📍 Access the web interface at:"
echo "   Primary:     http://127.0.0.1:8085"
echo "   Alternative: http://localhost:8085"
echo ""
echo "⚠️  Important: Include 'http://' in your browser"
echo "⚠️  Port 8085 (NOT 8080)"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Activate virtual environment and start server
./venv/bin/python start_server.py