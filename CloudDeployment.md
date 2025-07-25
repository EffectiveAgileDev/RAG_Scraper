 Critical Changes for Cloud Deployment

  1. Containerization (High Priority)

  Add Dockerfile:
  FROM python:3.13-slim

  WORKDIR /app

  # Install system dependencies for Playwright
  RUN apt-get update && apt-get install -y \
      wget \
      gnupg \
      && rm -rf /var/lib/apt/lists/*

  # Copy and install Python dependencies
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # Install Playwright browsers
  RUN playwright install --with-deps chromium

  # Copy application code
  COPY src/ ./src/
  COPY *.py ./
  COPY *.json ./

  # Create directories for file storage
  RUN mkdir -p /app/uploads /app/output

  # Expose port
  EXPOSE $PORT

  # Use production server
  CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:$PORT", "--workers", "2",
  "src.web_interface.app_factory_refactored:create_app()"]

  Add docker-compose.yml for local testing:
  version: '3.8'
  services:
    web:
      build: .
      ports:
        - "8085:8085"
      environment:
        - PORT=8085
        - HOST=0.0.0.0
        - DEBUG=false
      volumes:
        - ./uploads:/app/uploads
        - ./output:/app/output

  2. Production Server Setup

  Update requirements.txt:
  # Add production server
  gunicorn==21.2.0

  # Add cloud storage
  boto3==1.34.0
  google-cloud-storage==2.10.0

  # Add security & monitoring
  flask-limiter==3.5.0
  flask-talisman==1.1.0
  redis==5.0.1

  3. Environment Configuration

  Create .env.example:
  # Server Configuration
  HOST=0.0.0.0
  PORT=8085
  DEBUG=false
  SECRET_KEY=your-secret-key-here

  # Storage Configuration
  UPLOAD_FOLDER=/app/uploads
  OUTPUT_DIRECTORY=/app/output

  # AI Configuration (optional)
  OPENAI_API_KEY=
  ANTHROPIC_API_KEY=
  OLLAMA_BASE_URL=

  # Cloud Storage (optional)
  AWS_S3_BUCKET=
  AWS_ACCESS_KEY_ID=
  AWS_SECRET_ACCESS_KEY=

  # Database (if using persistent storage)
  REDIS_URL=redis://localhost:6379

  4. Update Application Configuration

  Modify app startup to use environment variables:

● Read(run_app_venv.py)
  ⎿  Read 85 lines (ctrl+r to expand)

● Create production-ready startup file:

● Write(app.py)
  ⎿  Wrote 50 lines to app.py                                     
     #!/usr/bin/env python3
     """Production entry point for RAG_Scraper web application."""
     import os
     import sys
     from pathlib import Path
     # Add project root to Python path
     project_root = Path(__file__).parent
     sys.path.insert(0, str(project_root))
     … +40 lines (ctrl+r to expand)

● 5. Platform-Specific Files

  For Heroku - Create Procfile:
  web: gunicorn --bind 0.0.0.0:$PORT app:app

  For Heroku - Create runtime.txt:
  python-3.13

  For DigitalOcean App Platform - Create .do/app.yaml:
  name: rag-scraper
  services:
  - name: web
    source_dir: /
    github:
      repo: your-username/RAG_Scraper
      branch: master
    run_command: gunicorn --bind 0.0.0.0:$PORT app:app
    environment_slug: python
    instance_count: 1
    instance_size_slug: basic-xxs
    envs:
    - key: SECRET_KEY
      value: ${SECRET_KEY}
    - key: DEBUG
      value: "false"

  6. Add Health Checks


Write(src/web_interface/routes/health_routes.py)

╭───────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Create file                                                                                               │
│ ╭───────────────────────────────────────────────────────────────────────────────────────────────────────╮ │
│ │ src/web_interface/routes/health_routes.py                                                             │ │
│ │                                                                                                       │ │
│ │ """Health check routes for production deployment."""                                                  │ │
│ │ from datetime import datetime                                                                         │ │
│ │ from flask import Blueprint, jsonify                                                                  │ │
│ │ import psutil                                                                                         │ │
│ │ import os                                                                                             │ │
│ │                                                                                                       │ │
│ │ health_bp = Blueprint('health', __name__)                                                             │ │
│ │                                                                                                       │ │
│ │ @health_bp.route('/health')                                                                           │ │
│ │ def health_check():                                                                                   │ │
│ │     """Basic health check endpoint."""                                                                │ │
│ │     return jsonify({                                                                                  │ │
│ │         'status': 'healthy',                                                                          │ │
│ │         'timestamp': datetime.now().isoformat(),                                                      │ │
│ │         'version': '1.0.0'                                                                            │ │
│ │     })                                                                                                │ │
│ │                                                                                                       │ │
│ │ @health_bp.route('/ready')                                                                            │ │
│ │ def readiness_check():                                                                                │ │
│ │     """Readiness check for load balancers."""                                                         │ │
│ │     try:                                                                                              │ │
│ │         # Check system resources                                                                      │ │
│ │         memory_usage = psutil.virtual_memory().percent                                                │ │
│ │         disk_usage = psutil.disk_usage('/').percent                                                   │ │
│ │                                                                                                       │ │
│ │         # Simple resource checks                                                                      │ │
│ │         if memory_usage > 90:                                                                         │ │
│ │             return jsonify({'status': 'not ready', 'reason': 'high memory usage'}), 503               │ │
│ │         if disk_usage > 90:                                                                           │ │
│ │             return jsonify({'status': 'not ready', 'reason': 'high disk usage'}), 503                 │ │
│ │                                                                                                       │ │
│ │         return jsonify({                                                                              │ │
│ │             'status': 'ready',                                                                        │ │
│ │             'timestamp': datetime.now().isoformat(),                                                  │ │
│ │             'memory_usage': memory_usage,                                                             │ │
│ │             'disk_usage': disk_usage                                                                  │ │
│ │         })                                                                                            │ │
│ │     except Exception as e:                                                                            │ │
│ │         return jsonify({'status': 'not ready', 'error': str(e)}), 503                                 │ │
│ │                                                                                                       │ │
│ │ @health_bp.route('/metrics')                                                                          │ │
│ │ def metrics():                                                                                        │ │
│ │     """Basic metrics endpoint."""                                                                     │ │
│ │     try:                                                                                              │ │
│ │         return jsonify({                                                                              │ │
│ │             'timestamp': datetime.now().isoformat(),                                                  │ │
│ │             'memory': {                                                                               │ │
│ │                 'usage_percent': psutil.virtual_memory().percent,                                     │ │
│ │                 'available_mb': psutil.virtual_memory().available // 1024 // 1024                     │ │
│ │             },                                                                                        │ │
│ │             'disk': {                                                                                 │ │
│ │                 'usage_percent': psutil.disk_usage('/').percent,                                      │ │
│ │                 'free_gb': psutil.disk_usage('/').free // 1024 // 1024 // 1024                        │ │
│ │             },                                                                                        │ │
│ │             'cpu': {                                                                                  │ │
│ │                 'usage_percent': psutil.cpu_percent(interval=1)                                       │ │
│ │             }                                                                                         │ │
│ │         })                                                                                            │ │
│ │     except Exception as e:                                                                            │ │
│ │         return jsonify({'error': str(e)}), 500    
