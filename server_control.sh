#!/bin/bash
# RAG_Scraper Server Control Script

case "$1" in
    start)
        echo "Starting RAG_Scraper server..."
        screen -dmS rag_scraper ./start_server_persistent.sh
        sleep 2
        if curl -s http://localhost:8085 > /dev/null; then
            echo "✅ Server started successfully at http://localhost:8085"
            echo "📋 View logs: tail -f logs/server.log"
            echo "🖥️  Attach to screen: screen -r rag_scraper"
        else
            echo "❌ Server failed to start. Check logs/server.log"
        fi
        ;;
    
    stop)
        echo "Stopping RAG_Scraper server..."
        screen -S rag_scraper -X quit 2>/dev/null
        pkill -f "python.*run_app" 2>/dev/null
        echo "✅ Server stopped"
        ;;
    
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
    
    status)
        if curl -s http://localhost:8085 > /dev/null 2>&1; then
            echo "✅ Server is RUNNING at http://localhost:8085"
            echo "📋 PID: $(pgrep -f "python.*run_app")"
        else
            echo "❌ Server is NOT running"
        fi
        ;;
    
    logs)
        echo "📋 Showing recent logs (Ctrl+C to exit):"
        tail -f logs/server.log
        ;;
    
    attach)
        echo "🖥️  Attaching to server screen (Ctrl+A,D to detach):"
        screen -r rag_scraper
        ;;
        
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|attach}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the server in background"
        echo "  stop    - Stop the server"
        echo "  restart - Restart the server"
        echo "  status  - Check if server is running"
        echo "  logs    - View server logs"
        echo "  attach  - Attach to server screen session"
        exit 1
        ;;
esac