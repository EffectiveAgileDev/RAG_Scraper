"""Flask web application for RAG_Scraper."""
import os
import json
import tempfile
from flask import Flask, render_template_string, request, jsonify, send_file
from werkzeug.exceptions import BadRequest
import secrets

from src.config.url_validator import URLValidator
from src.config.scraping_config import ScrapingConfig
from src.scraper.restaurant_scraper import RestaurantScraper
from src.scraper.advanced_progress_monitor import AdvancedProgressMonitor
from src.file_generator.file_generator_service import (
    FileGeneratorService,
    FileGenerationRequest,
)


# Global Advanced Progress Monitor instance
advanced_monitor = AdvancedProgressMonitor()

# Global scraper instance for progress tracking
active_scraper = None

# Global file generator service for persistent configuration
file_generator_service = None


def create_app(testing=False):
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = secrets.token_hex(16)
    app.config["TESTING"] = testing
    app.config["DEBUG"] = False  # Always False for security
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max request size

    # Upload folder configuration
    if testing:
        app.config["UPLOAD_FOLDER"] = tempfile.gettempdir()
    else:
        app.config["UPLOAD_FOLDER"] = os.path.join(os.path.expanduser("~"), "Downloads")

    # Initialize file generator service
    global file_generator_service
    config_file = os.path.join(app.config["UPLOAD_FOLDER"], "rag_scraper_config.json")
    file_generator_service = FileGeneratorService(config_file)

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    # Main interface route
    @app.route("/")
    def index():
        """Serve main interface."""
        html_template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>RAG_Scraper // Data Extraction Terminal</title>
            <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {
                    --bg-primary: #0a0a0a;
                    --bg-secondary: #111111;
                    --bg-tertiary: #1a1a1a;
                    --accent-green: #00ff88;
                    --accent-amber: #ffaa00;
                    --accent-cyan: #00aaff;
                    --text-primary: #ffffff;
                    --text-secondary: #cccccc;
                    --text-muted: #888888;
                    --border-glow: rgba(0, 255, 136, 0.3);
                    --shadow-neon: 0 0 20px rgba(0, 255, 136, 0.1);
                }

                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }

                body {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    background: var(--bg-primary);
                    color: var(--text-primary);
                    min-height: 100vh;
                    background-image: 
                        radial-gradient(circle at 25% 25%, rgba(0, 255, 136, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 75% 75%, rgba(255, 170, 0, 0.1) 0%, transparent 50%);
                    overflow-x: hidden;
                }

                .matrix-bg {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none;
                    z-index: 0;
                    opacity: 0.1;
                }

                .main-container {
                    position: relative;
                    z-index: 10;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 2rem;
                }

                .header {
                    text-align: center;
                    margin-bottom: 3rem;
                    position: relative;
                }

                .header::before {
                    content: '';
                    position: absolute;
                    top: -10px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 100px;
                    height: 2px;
                    background: linear-gradient(90deg, transparent, var(--accent-green), transparent);
                    animation: scan 2s ease-in-out infinite;
                }

                @keyframes scan {
                    0%, 100% { opacity: 0.3; width: 100px; }
                    50% { opacity: 1; width: 200px; }
                }

                .title {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: clamp(2rem, 5vw, 3.5rem);
                    font-weight: 700;
                    background: linear-gradient(45deg, var(--accent-green), var(--accent-cyan));
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 0.5rem;
                    letter-spacing: -0.02em;
                }

                .subtitle {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 1rem;
                    color: var(--text-primary);
                    margin-bottom: 1rem;
                }

                .status-bar {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    color: var(--accent-green);
                    border: 1px solid var(--border-glow);
                    padding: 0.5rem 1rem;
                    border-radius: 0;
                    background: rgba(0, 255, 136, 0.05);
                    display: inline-block;
                    box-shadow: var(--shadow-neon);
                }

                .extraction-panel {
                    background: var(--bg-secondary);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0;
                    padding: 2rem;
                    margin-bottom: 2rem;
                    position: relative;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                }

                .extraction-panel::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 1px;
                    background: linear-gradient(90deg, transparent, var(--accent-green), transparent);
                }

                .panel-header {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    color: var(--accent-green);
                    margin-bottom: 1.5rem;
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                }

                .data-flow {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    margin-bottom: 2rem;
                    flex-wrap: wrap;
                    gap: 1rem;
                    opacity: 0.4;
                    transition: all 0.3s ease;
                }

                .data-flow.active {
                    opacity: 1;
                }

                .data-flow.active .flow-step {
                    animation: pipeline-pulse 2s ease-in-out infinite;
                }

                .data-flow.active .flow-step:nth-child(1) {
                    animation-delay: 0s;
                }

                .data-flow.active .flow-step:nth-child(2) {
                    animation-delay: 0.5s;
                }

                .data-flow.active .flow-step:nth-child(3) {
                    animation-delay: 1s;
                }

                .flow-step {
                    flex: 1;
                    min-width: 120px;
                    text-align: center;
                    position: relative;
                }

                .flow-icon {
                    width: 60px;
                    height: 60px;
                    margin: 0 auto 0.5rem;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.5rem;
                    border: 2px solid;
                    transition: all 0.3s ease;
                }

                .flow-step:nth-child(1) .flow-icon {
                    border-color: var(--accent-cyan);
                    background: rgba(0, 170, 255, 0.1);
                    color: var(--accent-cyan);
                }

                .flow-step:nth-child(2) .flow-icon {
                    border-color: var(--accent-amber);
                    background: rgba(255, 170, 0, 0.1);
                    color: var(--accent-amber);
                }

                .flow-step:nth-child(3) .flow-icon {
                    border-color: var(--accent-green);
                    background: rgba(0, 255, 136, 0.1);
                    color: var(--accent-green);
                }

                .flow-step::after {
                    content: '→';
                    position: absolute;
                    right: -20px;
                    top: 30px;
                    color: var(--text-muted);
                    font-size: 1.5rem;
                    animation: pulse 2s ease-in-out infinite;
                }

                .flow-step:last-child::after {
                    display: none;
                }

                @keyframes pulse {
                    0%, 100% { opacity: 0.5; }
                    50% { opacity: 1; }
                }

                @keyframes pipeline-pulse {
                    0%, 100% { 
                        transform: scale(1);
                        box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
                    }
                    50% { 
                        transform: scale(1.05);
                        box-shadow: 0 0 20px rgba(0, 255, 136, 0.6);
                    }
                }

                .flow-label {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                    color: var(--text-secondary);
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }

                .input-group {
                    margin-bottom: 2rem;
                    position: relative;
                }

                .input-label {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    color: var(--text-secondary);
                    margin-bottom: 0.5rem;
                    display: block;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }

                .terminal-input {
                    width: 100%;
                    background: var(--bg-tertiary);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0;
                    color: var(--text-primary);
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    padding: 1rem;
                    transition: all 0.3s ease;
                    resize: vertical;
                }

                .terminal-input:focus {
                    outline: none;
                    border-color: var(--accent-green);
                    box-shadow: 0 0 0 2px rgba(0, 255, 136, 0.2);
                    background: rgba(0, 255, 136, 0.05);
                }

                .terminal-input::placeholder {
                    color: var(--text-muted);
                    font-style: italic;
                }

                .url-textarea {
                    min-height: 120px;
                    font-family: 'JetBrains Mono', monospace;
                }

                .format-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 1rem;
                    margin-top: 1rem;
                }

                .format-option {
                    background: var(--bg-tertiary);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0;
                    padding: 1rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                }

                .format-option::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 2px;
                    background: var(--accent-green);
                    transition: all 0.3s ease;
                }

                .format-option:hover::before,
                .format-option.selected::before {
                    left: 0;
                }

                .format-option:hover {
                    border-color: var(--accent-green);
                    background: rgba(0, 255, 136, 0.05);
                    transform: translateY(-2px);
                }

                .format-option.selected {
                    border-color: var(--accent-green);
                    background: rgba(0, 255, 136, 0.1);
                    box-shadow: var(--shadow-neon);
                }

                .format-option input {
                    display: none;
                }

                .format-title {
                    font-family: 'JetBrains Mono', monospace;
                    font-weight: 600;
                    margin-bottom: 0.5rem;
                    color: var(--text-primary);
                }

                .format-desc {
                    font-size: 0.75rem;
                    color: var(--text-muted);
                    line-height: 1.4;
                }

                .field-selection-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 0.75rem;
                    margin-top: 1rem;
                }

                .field-option {
                    background: var(--bg-tertiary);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0;
                    padding: 0.75rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    display: flex;
                    align-items: flex-start;
                    gap: 0.5rem;
                }

                .field-option:hover {
                    border-color: var(--accent-amber);
                    background: rgba(255, 170, 0, 0.05);
                }

                .field-option input[type="checkbox"] {
                    margin: 0;
                    accent-color: var(--accent-amber);
                }

                .field-option .field-title {
                    font-family: 'JetBrains Mono', monospace;
                    font-weight: 600;
                    font-size: 0.75rem;
                    color: var(--text-primary);
                    margin-bottom: 0.25rem;
                }

                .field-option .field-desc {
                    font-size: 0.6875rem;
                    color: var(--text-muted);
                    line-height: 1.3;
                }

                .action-bar {
                    display: flex;
                    gap: 1rem;
                    flex-wrap: wrap;
                    margin-top: 2rem;
                }

                .cmd-button {
                    background: var(--bg-tertiary);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    color: var(--text-primary);
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    padding: 0.75rem 1.5rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    overflow: hidden;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    font-weight: 500;
                }

                .cmd-button::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: -100%;
                    width: 100%;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
                    transition: all 0.5s ease;
                }

                .cmd-button:hover::before {
                    left: 100%;
                }

                .cmd-button.primary {
                    border-color: var(--accent-green);
                    color: var(--accent-green);
                }

                .cmd-button.primary:hover {
                    background: var(--accent-green);
                    color: var(--bg-primary);
                    box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
                }

                .cmd-button:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                .terminal-output {
                    background: var(--bg-tertiary);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 0;
                    padding: 1.5rem;
                    margin-top: 2rem;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    line-height: 1.6;
                    display: none;
                    position: relative;
                }

                .terminal-output::before {
                    content: '// EXTRACTION OUTPUT';
                    position: absolute;
                    top: -10px;
                    left: 1rem;
                    background: var(--bg-secondary);
                    color: var(--accent-green);
                    padding: 0 0.5rem;
                    font-size: 0.75rem;
                }

                .progress-bar {
                    height: 4px;
                    background: rgba(255, 255, 255, 0.1);
                    margin: 1rem 0;
                    overflow: hidden;
                    position: relative;
                }

                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
                    width: 0%;
                    transition: width 0.3s ease;
                    position: relative;
                }

                .progress-fill::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    right: 0;
                    width: 20px;
                    height: 100%;
                    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.6));
                    animation: scan-progress 2s ease-in-out infinite;
                }

                @keyframes scan-progress {
                    0%, 100% { transform: translateX(0); opacity: 0; }
                    50% { transform: translateX(-10px); opacity: 1; }
                }

                .validation-output {
                    margin-top: 0.5rem;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                }

                .valid-url {
                    color: var(--accent-green);
                }

                .invalid-url {
                    color: #ff5555;
                }

                .file-links {
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                    margin-top: 1rem;
                }

                .file-link {
                    display: inline-flex;
                    align-items: center;
                    color: var(--accent-cyan);
                    text-decoration: none;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    padding: 0.5rem 1rem;
                    border: 1px solid rgba(0, 170, 255, 0.3);
                    background: rgba(0, 170, 255, 0.1);
                    transition: all 0.3s ease;
                }

                .file-link:hover {
                    border-color: var(--accent-cyan);
                    background: rgba(0, 170, 255, 0.2);
                    transform: translateX(5px);
                }

                .file-link::before {
                    content: '📁';
                    margin-right: 0.5rem;
                }

                .success {
                    border-color: var(--accent-green);
                    background: rgba(0, 255, 136, 0.1);
                    color: var(--text-primary);
                }

                .error {
                    border-color: #ff5555;
                    background: rgba(255, 85, 85, 0.1);
                    color: var(--text-primary);
                }

                /* Scraping Mode Selector Styles */
                .scraping-mode-selector {
                    margin-bottom: 1rem;
                }

                .mode-toggle-group {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 0.75rem;
                    margin-top: 0.75rem;
                }

                .mode-option {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 1rem;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    background: var(--bg-tertiary);
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                    text-align: center;
                }

                .mode-option input[type="radio"] {
                    display: none;
                }

                .mode-option:hover {
                    border-color: var(--accent-cyan);
                    background: rgba(0, 170, 255, 0.1);
                    transform: translateY(-2px);
                }

                .mode-option.active {
                    border-color: var(--accent-green);
                    background: rgba(0, 255, 136, 0.1);
                    box-shadow: 0 0 15px rgba(0, 255, 136, 0.2);
                }

                .mode-icon {
                    font-size: 1.5rem;
                    margin-bottom: 0.5rem;
                }

                .mode-title {
                    font-family: 'JetBrains Mono', monospace;
                    font-weight: 600;
                    font-size: 0.875rem;
                    color: var(--text-primary);
                    margin-bottom: 0.25rem;
                }

                .mode-desc {
                    font-size: 0.75rem;
                    color: var(--text-muted);
                    line-height: 1.3;
                }

                /* Multi-Page Configuration Panel Styles */
                .config-panel-header {
                    cursor: pointer;
                    transition: all 0.3s ease;
                    position: relative;
                }

                .config-panel-header:hover {
                    background: rgba(255, 255, 255, 0.05);
                }

                .config-toggle {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    width: 100%;
                    cursor: pointer;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    color: var(--accent-amber);
                    padding: 0.75rem;
                    border: 1px solid rgba(255, 170, 0, 0.3);
                    background: rgba(255, 170, 0, 0.05);
                    transition: all 0.3s ease;
                }

                .config-icon {
                    margin-right: 0.5rem;
                    font-size: 1rem;
                }

                .expand-icon {
                    transition: transform 0.3s ease;
                    font-family: monospace;
                    color: var(--accent-amber);
                }

                .expand-icon.expanded {
                    transform: rotate(180deg);
                }

                .config-panel {
                    overflow: hidden;
                    transition: all 0.4s ease;
                    border: 1px solid rgba(255, 170, 0, 0.2);
                    border-top: none;
                    background: var(--bg-tertiary);
                }

                .config-panel.collapsed {
                    max-height: 0;
                    opacity: 0;
                    border-color: transparent;
                }

                .config-panel:not(.collapsed) {
                    max-height: 600px;
                    opacity: 1;
                    padding: 1.5rem;
                }

                .config-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 1.5rem;
                }

                .config-item {
                    display: flex;
                    flex-direction: column;
                    gap: 0.5rem;
                }

                .config-label {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                    color: var(--accent-green);
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }

                .config-input {
                    font-size: 0.875rem;
                    padding: 0.5rem;
                }

                .terminal-slider {
                    -webkit-appearance: none;
                    appearance: none;
                    height: 4px;
                    background: rgba(255, 255, 255, 0.1);
                    outline: none;
                    border-radius: 0;
                    cursor: pointer;
                }

                .terminal-slider::-webkit-slider-thumb {
                    -webkit-appearance: none;
                    appearance: none;
                    width: 16px;
                    height: 16px;
                    background: var(--accent-green);
                    cursor: pointer;
                    border-radius: 0;
                    border: 1px solid var(--accent-green);
                    box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
                }

                .terminal-slider::-moz-range-thumb {
                    width: 16px;
                    height: 16px;
                    background: var(--accent-green);
                    cursor: pointer;
                    border-radius: 0;
                    border: 1px solid var(--accent-green);
                    box-shadow: 0 0 10px rgba(0, 255, 136, 0.3);
                }

                .slider-value {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                    color: var(--accent-amber);
                    margin-top: 0.25rem;
                }

                .config-desc {
                    font-size: 0.6875rem;
                    color: var(--text-muted);
                    line-height: 1.4;
                    font-style: italic;
                }

                @media (max-width: 768px) {
                    .main-container {
                        padding: 1rem;
                    }
                    
                    .data-flow {
                        flex-direction: column;
                    }
                    
                    .flow-step::after {
                        display: none;
                    }
                    
                    .action-bar {
                        flex-direction: column;
                    }
                }

                /* Custom scrollbar */
                ::-webkit-scrollbar {
                    width: 8px;
                }

                ::-webkit-scrollbar-track {
                    background: var(--bg-secondary);
                }

                ::-webkit-scrollbar-thumb {
                    background: var(--accent-green);
                    border-radius: 4px;
                }

                ::-webkit-scrollbar-thumb:hover {
                    background: var(--accent-cyan);
                }

                /* Enhanced Results Display Styles */
                .results-container {
                    margin-top: 1rem;
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    background: var(--bg-secondary);
                    overflow: hidden;
                }

                .results-header {
                    background: var(--bg-tertiary);
                    padding: 0.75rem 1rem;
                    border-bottom: 1px solid var(--border-color);
                }

                .results-header h3 {
                    margin: 0;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    color: var(--accent-green);
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                }

                .results-content {
                    max-height: 400px;
                    overflow-y: auto;
                }

                .no-results {
                    padding: 2rem;
                    text-align: center;
                    color: var(--text-muted);
                }

                .no-results .status-message {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    margin-bottom: 0.5rem;
                }

                .no-results .status-subtitle {
                    font-size: 0.75rem;
                    opacity: 0.7;
                }

                .sites-results {
                    padding: 1rem;
                }

                .site-result {
                    margin-bottom: 1.5rem;
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    background: var(--bg-primary);
                    overflow: hidden;
                }

                .site-result:last-child {
                    margin-bottom: 0;
                }

                .site-header {
                    background: var(--bg-tertiary);
                    padding: 0.75rem 1rem;
                    border-bottom: 1px solid var(--border-color);
                    cursor: pointer;
                    transition: all 0.2s ease;
                }

                .site-header:hover {
                    background: var(--bg-secondary);
                }

                .site-url {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.8rem;
                    color: var(--accent-cyan);
                    margin-bottom: 0.25rem;
                    word-break: break-all;
                }

                .pages-summary {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                    color: var(--accent-amber);
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                }

                .expand-toggle {
                    margin-left: auto;
                    color: var(--text-muted);
                    transition: transform 0.2s ease;
                }

                .expand-toggle.expanded {
                    transform: rotate(180deg);
                }

                .pages-list {
                    padding: 1rem;
                    border-top: 1px solid var(--border-color);
                    display: none;
                }

                .pages-list.expanded {
                    display: block;
                }

                .page-item {
                    display: flex;
                    align-items: center;
                    padding: 0.5rem;
                    margin-bottom: 0.5rem;
                    border: 1px solid var(--border-color);
                    border-radius: 3px;
                    background: var(--bg-secondary);
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                }

                .page-item:last-child {
                    margin-bottom: 0;
                }

                .page-item.status-success {
                    border-left: 3px solid var(--accent-green);
                }

                .page-item.status-failed {
                    border-left: 3px solid var(--accent-red);
                }

                .page-url {
                    flex: 1;
                    color: var(--text-primary);
                    margin-right: 1rem;
                    word-break: break-all;
                }

                .page-status {
                    padding: 0.2rem 0.5rem;
                    border-radius: 2px;
                    font-size: 0.6875rem;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-right: 0.5rem;
                }

                .page-status.success {
                    background: var(--accent-green);
                    color: var(--bg-primary);
                }

                .page-status.failed {
                    background: var(--accent-red);
                    color: var(--bg-primary);
                }

                .page-time {
                    color: var(--text-muted);
                    font-size: 0.6875rem;
                    min-width: 60px;
                    text-align: right;
                }

                .show-all-link {
                    margin-top: 0.5rem;
                    padding: 0.5rem;
                    text-align: center;
                    color: var(--accent-cyan);
                    cursor: pointer;
                    border: 1px dashed var(--border-color);
                    border-radius: 3px;
                    transition: all 0.2s ease;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                }

                .show-all-link:hover {
                    background: var(--bg-tertiary);
                    border-color: var(--accent-cyan);
                }

                .processing-stats {
                    display: flex;
                    gap: 1rem;
                    font-size: 0.6875rem;
                    color: var(--text-muted);
                }

                .stat-item {
                    display: flex;
                    align-items: center;
                    gap: 0.25rem;
                }

                .stat-icon {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                }

                .stat-icon.success {
                    background: var(--accent-green);
                }

                .stat-icon.failed {
                    background: var(--accent-red);
                }

                /* Page Relationships Display Styles */
                .relationship-enabled {
                    position: relative;
                }

                .relationship-tree {
                    margin-top: 1rem;
                    padding: 1rem;
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    background: var(--bg-tertiary);
                }

                .relationship-tree-header {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.875rem;
                    color: var(--accent-green);
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    margin-bottom: 1rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }

                .page-item.relationship-root {
                    border-left: 4px solid var(--accent-green);
                    background: linear-gradient(90deg, rgba(0, 255, 136, 0.1) 0%, transparent 100%);
                }

                .page-item.relationship-child {
                    border-left: 4px solid var(--accent-cyan);
                    background: linear-gradient(90deg, rgba(0, 204, 255, 0.05) 0%, transparent 100%);
                }

                .page-item.relationship-orphaned {
                    border-left: 4px solid var(--accent-amber);
                    background: linear-gradient(90deg, rgba(255, 193, 7, 0.1) 0%, transparent 100%);
                }

                .relationship-indicator {
                    display: inline-flex;
                    align-items: center;
                    padding: 0.2rem 0.5rem;
                    border-radius: 3px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.6875rem;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    margin-right: 0.5rem;
                }

                .relationship-indicator.ROOT {
                    background: var(--accent-green);
                    color: var(--bg-primary);
                }

                .relationship-indicator.child {
                    background: var(--accent-cyan);
                    color: var(--bg-primary);
                    font-size: 0.75rem;
                }

                .relationship-indicator.orphaned {
                    background: var(--accent-amber);
                    color: var(--bg-primary);
                }

                .indentation {
                    display: inline-block;
                    margin-right: 0.5rem;
                    color: var(--text-muted);
                    font-family: 'JetBrains Mono', monospace;
                }

                .depth-0 .indentation::before {
                    content: '';
                }

                .depth-1 .indentation::before {
                    content: '  └─ ';
                    color: var(--accent-cyan);
                }

                .depth-2 .indentation::before {
                    content: '    └─ ';
                    color: var(--accent-cyan);
                }

                .depth-3 .indentation::before {
                    content: '      └─ ';
                    color: var(--accent-cyan);
                }

                .depth-4 .indentation::before {
                    content: '        └─ ';
                    color: var(--accent-cyan);
                }

                .depth-5 .indentation::before {
                    content: '          └─ ';
                    color: var(--accent-cyan);
                }

                .parent-reference {
                    font-size: 0.6875rem;
                    color: var(--text-muted);
                    font-style: italic;
                    margin-left: 0.5rem;
                }

                .discovery-info {
                    font-size: 0.6875rem;
                    color: var(--accent-amber);
                    margin-left: 0.5rem;
                    padding: 0.1rem 0.3rem;
                    background: rgba(255, 193, 7, 0.1);
                    border-radius: 2px;
                }

                .children-count {
                    font-size: 0.6875rem;
                    color: var(--accent-green);
                    margin-left: 0.5rem;
                    padding: 0.1rem 0.3rem;
                    background: rgba(0, 255, 136, 0.1);
                    border-radius: 2px;
                }

                .depth-level {
                    font-size: 0.6875rem;
                    color: var(--text-muted);
                    margin-left: 0.5rem;
                }

                .relationship-stats {
                    margin-top: 1rem;
                    padding: 0.75rem;
                    background: var(--bg-secondary);
                    border-radius: 3px;
                    border: 1px solid var(--border-color);
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                }

                .relationship-stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 0.5rem;
                }

                .stat-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .stat-label {
                    color: var(--text-muted);
                }

                .stat-value {
                    color: var(--accent-green);
                    font-weight: bold;
                }

                .tree-toggle {
                    cursor: pointer;
                    margin-left: 0.5rem;
                    padding: 0.2rem;
                    border-radius: 2px;
                    transition: all 0.2s ease;
                    font-size: 0.6875rem;
                }

                .tree-toggle:hover {
                    background: var(--bg-secondary);
                    color: var(--accent-cyan);
                }

                .tree-toggle.expanded {
                    transform: rotate(180deg);
                }

                .children-list {
                    margin-left: 1rem;
                    margin-top: 0.5rem;
                    border-left: 1px dashed var(--border-color);
                    padding-left: 1rem;
                    display: none;
                }

                .children-list.expanded {
                    display: block;
                }

                .broken-relationship {
                    border-left-color: var(--accent-red) !important;
                    background: linear-gradient(90deg, rgba(220, 53, 69, 0.1) 0%, transparent 100%);
                }

                .relationship-warning {
                    color: var(--accent-red);
                    font-size: 0.6875rem;
                    margin-left: 0.5rem;
                    padding: 0.1rem 0.3rem;
                    background: rgba(220, 53, 69, 0.1);
                    border-radius: 2px;
                }

                .relationship-tooltip {
                    position: relative;
                    cursor: help;
                    margin-left: 0.25rem;
                    color: var(--accent-cyan);
                    font-size: 0.75rem;
                }

                .relationship-tooltip:hover::after {
                    content: attr(data-tooltip);
                    position: absolute;
                    bottom: 100%;
                    left: 50%;
                    transform: translateX(-50%);
                    background: var(--bg-primary);
                    color: var(--text-primary);
                    padding: 0.5rem;
                    border-radius: 4px;
                    border: 1px solid var(--border-color);
                    white-space: nowrap;
                    z-index: 1000;
                    font-size: 0.6875rem;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
                }

                .orphaned-section {
                    margin-top: 1rem;
                    padding: 0.75rem;
                    background: rgba(255, 193, 7, 0.05);
                    border: 1px dashed var(--accent-amber);
                    border-radius: 4px;
                }

                .orphaned-section-header {
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.75rem;
                    color: var(--accent-amber);
                    text-transform: uppercase;
                    letter-spacing: 0.1em;
                    margin-bottom: 0.5rem;
                }

                .highlight-relationship-chain .page-item {
                    opacity: 0.3;
                    transition: opacity 0.2s ease;
                }

                .highlight-relationship-chain .page-item.highlighted {
                    opacity: 1;
                    box-shadow: 0 0 10px rgba(0, 204, 255, 0.3);
                }
            </style>
        </head>
        <body>
            <div class="matrix-bg"></div>
            
            <div class="main-container">
                <header class="header">
                    <h1 class="title">RAG Scraper</h1>
                    <p class="subtitle">DATA EXTRACTION TERMINAL</p>
                    <div class="status-bar">SYSTEM_READY // AWAITING_TARGET_URLs</div>
                </header>

                <div class="extraction-panel">
                    <div class="panel-header">DATA FLOW PIPELINE</div>
                    
                    <div class="data-flow">
                        <div class="flow-step">
                            <div class="flow-icon">🌐</div>
                            <div class="flow-label">WEB_SCAN</div>
                        </div>
                        <div class="flow-step">
                            <div class="flow-icon">⚡</div>
                            <div class="flow-label">EXTRACT</div>
                        </div>
                        <div class="flow-step">
                            <div class="flow-icon">📊</div>
                            <div class="flow-label">RAG_DATA</div>
                        </div>
                    </div>

                    <form id="scrapeForm">
                        <div class="input-group">
                            <label class="input-label" for="urls">TARGET_URLS:</label>
                            <textarea 
                                id="urls" 
                                name="urls" 
                                class="terminal-input url-textarea"
                                placeholder="https://restaurant1.com
https://restaurant2.com
https://restaurant3.com
// Enter restaurant URLs to extract..."
                                required></textarea>
                            <div id="urlValidation" class="validation-output"></div>
                        </div>
                        
                        <div class="input-group">
                            <label class="input-label" for="outputDir">OUTPUT_DIRECTORY:</label>
                            <input 
                                type="text" 
                                id="outputDir" 
                                name="outputDir" 
                                class="terminal-input"
                                placeholder="~/Downloads // Leave empty for default">
                        </div>

                        <!-- Multi-Page Configuration Panel -->
                        <div class="input-group">
                            <div class="scraping-mode-selector">
                                <label class="input-label">SCRAPING_MODE:</label>
                                <div class="mode-toggle-group">
                                    <label class="mode-option active" data-mode="single">
                                        <input type="radio" name="scrapingMode" value="single" checked>
                                        <span class="mode-icon">📄</span>
                                        <span class="mode-title">SINGLE_PAGE</span>
                                        <span class="mode-desc">Process each URL as single page</span>
                                    </label>
                                    <label class="mode-option" data-mode="multi">
                                        <input type="radio" name="scrapingMode" value="multi">
                                        <span class="mode-icon">📚</span>
                                        <span class="mode-title">MULTI_PAGE</span>
                                        <span class="mode-desc">Discover and crawl related pages</span>
                                    </label>
                                </div>
                            </div>
                            
                            <div class="config-panel-header" onclick="toggleMultiPageConfig()" id="multiPageHeader" style="display: none;">
                                <label class="input-label config-toggle">
                                    <span class="config-icon">⚙️</span>
                                    MULTI_PAGE_CONFIG
                                    <span class="expand-icon" id="configExpandIcon">▼</span>
                                </label>
                            </div>
                            <div id="multiPageConfig" class="config-panel collapsed">
                                <div class="config-grid">
                                    <div class="config-item">
                                        <label class="config-label" for="maxPages">MAX_PAGES_PER_SITE:</label>
                                        <input 
                                            type="number" 
                                            id="maxPages" 
                                            name="maxPages" 
                                            class="terminal-input config-input"
                                            value="50"
                                            min="1"
                                            max="500"
                                            placeholder="50" />
                                        <div class="config-desc">Maximum pages to scrape per website</div>
                                    </div>
                                    
                                    <div class="config-item">
                                        <label class="config-label" for="crawlDepth">CRAWL_DEPTH:</label>
                                        <input 
                                            type="range" 
                                            id="crawlDepth" 
                                            name="crawlDepth" 
                                            class="terminal-slider"
                                            value="2"
                                            min="1"
                                            max="5" />
                                        <div class="slider-value">Depth: <span id="depthValue">2</span></div>
                                        <div class="config-desc">How deep to follow page links</div>
                                    </div>
                                    
                                    <div class="config-item">
                                        <label class="config-label" for="includePatterns">INCLUDE_PATTERNS:</label>
                                        <input 
                                            type="text" 
                                            id="includePatterns" 
                                            name="includePatterns" 
                                            class="terminal-input config-input"
                                            placeholder="menu,food,restaurant"
                                            value="menu,food,restaurant" />
                                        <div class="config-desc">URL patterns to include (comma-separated)</div>
                                    </div>
                                    
                                    <div class="config-item">
                                        <label class="config-label" for="excludePatterns">EXCLUDE_PATTERNS:</label>
                                        <input 
                                            type="text" 
                                            id="excludePatterns" 
                                            name="excludePatterns" 
                                            class="terminal-input config-input"
                                            placeholder="admin,login,cart"
                                            value="admin,login,cart" />
                                        <div class="config-desc">URL patterns to exclude (comma-separated)</div>
                                    </div>
                                    
                                    <div class="config-item">
                                        <label class="config-label" for="rateLimit">RATE_LIMIT_MS:</label>
                                        <input 
                                            type="range" 
                                            id="rateLimit" 
                                            name="rateLimit" 
                                            class="terminal-slider"
                                            value="1000"
                                            min="100"
                                            max="5000"
                                            step="100" />
                                        <div class="slider-value">Delay: <span id="rateLimitValue">1000ms</span></div>
                                        <div class="config-desc">Delay between requests (ethical scraping)</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="input-group">
                            <label class="input-label" for="fileMode">AGGREGATION_MODE:</label>
                            <select id="fileMode" name="fileMode" class="terminal-input">
                                <option value="single">UNIFIED // Single file for all targets</option>
                                <option value="multiple">SEGMENTED // Individual files per target</option>
                            </select>
                        </div>
                        
                        <div class="input-group">
                            <label class="input-label">OUTPUT_FORMAT:</label>
                            <div class="format-grid">
                                <label class="format-option selected" data-format="text">
                                    <input type="radio" id="fileFormatText" name="fileFormat" value="text" checked>
                                    <div class="format-title">TEXT</div>
                                    <div class="format-desc">Raw structured data for RAG ingestion</div>
                                </label>
                                <label class="format-option" data-format="pdf">
                                    <input type="radio" id="fileFormatPdf" name="fileFormat" value="pdf">
                                    <div class="format-title">PDF</div>
                                    <div class="format-desc">Formatted document for human review</div>
                                </label>
                                <label class="format-option" data-format="json">
                                    <input type="radio" id="fileFormatJson" name="fileFormat" value="json">
                                    <div class="format-title">JSON</div>
                                    <div class="format-desc">Structured data for system integration</div>
                                </label>
                            </div>
                        </div>
                        
                        <div id="jsonFieldSelection" class="input-group" style="display: none;">
                            <label class="input-label">JSON_FIELD_SELECTION:</label>
                            <div class="field-selection-grid">
                                <label class="field-option">
                                    <input type="checkbox" name="jsonFields" value="core_fields" checked>
                                    <div class="field-title">CORE FIELDS</div>
                                    <div class="field-desc">Name, address, phone, hours</div>
                                </label>
                                <label class="field-option">
                                    <input type="checkbox" name="jsonFields" value="extended_fields" checked>
                                    <div class="field-title">EXTENDED FIELDS</div>
                                    <div class="field-desc">Cuisine, features, parking</div>
                                </label>
                                <label class="field-option">
                                    <input type="checkbox" name="jsonFields" value="contact_fields" checked>
                                    <div class="field-title">CONTACT FIELDS</div>
                                    <div class="field-desc">Email, social media, delivery</div>
                                </label>
                                <label class="field-option">
                                    <input type="checkbox" name="jsonFields" value="descriptive_fields">
                                    <div class="field-title">DESCRIPTIVE FIELDS</div>
                                    <div class="field-desc">Ambiance, dietary options</div>
                                </label>
                            </div>
                        </div>
                        
                        <div class="action-bar">
                            <button type="submit" id="submitBtn" class="cmd-button primary">EXECUTE_EXTRACTION</button>
                            <button type="button" id="validateBtn" class="cmd-button">VALIDATE_TARGETS</button>
                            <button type="button" id="clearBtn" class="cmd-button">RESET_TERMINAL</button>
                        </div>
                    </form>
                </div>
                
                <div id="progressContainer" class="terminal-output">
                    <div class="progress-bar">
                        <div id="progressFill" class="progress-fill"></div>
                    </div>
                    <div id="progressText">INITIALIZING_EXTRACTION_SEQUENCE...</div>
                    <div id="currentUrl"></div>
                    <div id="timeEstimate"></div>
                    <div id="memoryUsage"></div>
                </div>
                
                <div id="resultsContainer" class="results-container" style="display: none;">
                    <div class="results-header">
                        <h3>📊 SCRAPING_RESULTS</h3>
                    </div>
                    <div class="results-content" id="resultsContent">
                        <div class="no-results" id="noResults">
                            <div class="status-message">No results available</div>
                            <div class="status-subtitle">Complete a scraping operation to see detailed results</div>
                        </div>
                        <div class="sites-results" id="sitesResults" style="display: none;">
                            <!-- Site results will be populated here -->
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Terminal UI Elements
                const form = document.getElementById('scrapeForm');
                const urlsInput = document.getElementById('urls');
                const submitBtn = document.getElementById('submitBtn');
                const validateBtn = document.getElementById('validateBtn');
                const clearBtn = document.getElementById('clearBtn');
                const progressContainer = document.getElementById('progressContainer');
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                const currentUrl = document.getElementById('currentUrl');
                const timeEstimate = document.getElementById('timeEstimate');
                const memoryUsage = document.getElementById('memoryUsage');
                const resultsContainer = document.getElementById('resultsContainer');
                const resultsContent = document.getElementById('resultsContent');
                const noResults = document.getElementById('noResults');
                const sitesResults = document.getElementById('sitesResults');
                const urlValidation = document.getElementById('urlValidation');
                const statusBar = document.querySelector('.status-bar');
                const formatOptions = document.querySelectorAll('.format-option');
                const dataFlow = document.querySelector('.data-flow');
                
                let progressInterval;
                let terminalEffects = true;

                // Initialize terminal effects
                document.addEventListener('DOMContentLoaded', function() {
                    initializeTerminalEffects();
                    setupFormatSelection();
                    setupSliderUpdates();
                    setupModeSelection();
                });

                function initializeTerminalEffects() {
                    // Create matrix background effect
                    createMatrixEffect();
                    
                    // Add terminal cursor effect to inputs
                    addTerminalCursorEffect();
                    
                    // Initialize status updates
                    updateSystemStatus('SYSTEM_READY // AWAITING_TARGET_URLs');
                }

                function createMatrixEffect() {
                    const matrixBg = document.querySelector('.matrix-bg');
                    const chars = '01';
                    const columns = Math.floor(window.innerWidth / 20);
                    
                    for (let i = 0; i < 50; i++) {
                        const char = document.createElement('div');
                        char.textContent = chars[Math.floor(Math.random() * chars.length)];
                        char.style.position = 'absolute';
                        char.style.left = Math.random() * 100 + '%';
                        char.style.top = Math.random() * 100 + '%';
                        char.style.color = 'rgba(0, 255, 136, 0.1)';
                        char.style.fontSize = '12px';
                        char.style.fontFamily = 'JetBrains Mono, monospace';
                        char.style.animation = `float ${3 + Math.random() * 4}s ease-in-out infinite`;
                        matrixBg.appendChild(char);
                    }
                }

                function addTerminalCursorEffect() {
                    const inputs = document.querySelectorAll('.terminal-input');
                    inputs.forEach(input => {
                        input.addEventListener('focus', function() {
                            this.style.animation = 'terminal-cursor 1s ease-in-out infinite';
                        });
                        input.addEventListener('blur', function() {
                            this.style.animation = 'none';
                        });
                    });
                }

                function setupFormatSelection() {
                    const jsonFieldSelection = document.getElementById('jsonFieldSelection');
                    
                    formatOptions.forEach(option => {
                        option.addEventListener('click', function() {
                            formatOptions.forEach(opt => opt.classList.remove('selected'));
                            this.classList.add('selected');
                            const radio = this.querySelector('input[type="radio"]');
                            radio.checked = true;
                            
                            // Show/hide JSON field selection based on format choice
                            if (radio.value === 'json') {
                                jsonFieldSelection.style.display = 'block';
                                updateSystemStatus(`JSON_FORMAT_SELECTED // FIELD_CUSTOMIZATION_AVAILABLE`);
                            } else {
                                jsonFieldSelection.style.display = 'none';
                                updateSystemStatus(`FORMAT_SELECTED // ${radio.value.toUpperCase()}_MODE_ACTIVE`);
                            }
                        });
                    });
                }

                // Multi-Page Configuration Panel Functions
                function toggleMultiPageConfig() {
                    const configPanel = document.getElementById('multiPageConfig');
                    const expandIcon = document.getElementById('configExpandIcon');
                    
                    if (configPanel.classList.contains('collapsed')) {
                        configPanel.classList.remove('collapsed');
                        expandIcon.classList.add('expanded');
                        updateSystemStatus('MULTI_PAGE_CONFIG // PANEL_EXPANDED');
                    } else {
                        configPanel.classList.add('collapsed');
                        expandIcon.classList.remove('expanded');
                        updateSystemStatus('MULTI_PAGE_CONFIG // PANEL_COLLAPSED');
                    }
                }

                function setupSliderUpdates() {
                    // Crawl depth slider
                    const crawlDepthSlider = document.getElementById('crawlDepth');
                    const depthValue = document.getElementById('depthValue');
                    
                    if (crawlDepthSlider && depthValue) {
                        crawlDepthSlider.addEventListener('input', function() {
                            depthValue.textContent = this.value;
                            updateSystemStatus(`CRAWL_DEPTH_SET // LEVEL_${this.value}`);
                        });
                    }

                    // Rate limit slider
                    const rateLimitSlider = document.getElementById('rateLimit');
                    const rateLimitValue = document.getElementById('rateLimitValue');
                    
                    if (rateLimitSlider && rateLimitValue) {
                        rateLimitSlider.addEventListener('input', function() {
                            rateLimitValue.textContent = this.value + 'ms';
                            updateSystemStatus(`RATE_LIMIT_SET // ${this.value}MS_DELAY`);
                        });
                    }

                    // Max pages input
                    const maxPagesInput = document.getElementById('maxPages');
                    if (maxPagesInput) {
                        maxPagesInput.addEventListener('input', function() {
                            updateSystemStatus(`MAX_PAGES_SET // LIMIT_${this.value}_PAGES`);
                        });
                    }

                    // Pattern inputs
                    const includePatterns = document.getElementById('includePatterns');
                    const excludePatterns = document.getElementById('excludePatterns');
                    
                    if (includePatterns) {
                        includePatterns.addEventListener('input', function() {
                            const patterns = this.value.split(',').length;
                            updateSystemStatus(`INCLUDE_PATTERNS_SET // ${patterns}_FILTERS_ACTIVE`);
                        });
                    }

                    if (excludePatterns) {
                        excludePatterns.addEventListener('input', function() {
                            const patterns = this.value.split(',').length;
                            updateSystemStatus(`EXCLUDE_PATTERNS_SET // ${patterns}_FILTERS_ACTIVE`);
                        });
                    }
                }

                function setupModeSelection() {
                    const modeOptions = document.querySelectorAll('.mode-option');
                    const multiPageHeader = document.getElementById('multiPageHeader');
                    const multiPageConfig = document.getElementById('multiPageConfig');
                    
                    modeOptions.forEach(option => {
                        option.addEventListener('click', function() {
                            // Update active state
                            modeOptions.forEach(opt => opt.classList.remove('active'));
                            this.classList.add('active');
                            
                            // Update radio button
                            const radio = this.querySelector('input[type="radio"]');
                            radio.checked = true;
                            
                            // Show/hide multi-page configuration
                            const mode = radio.value;
                            if (mode === 'multi') {
                                multiPageHeader.style.display = 'block';
                                updateSystemStatus('MULTI_PAGE_MODE // ADVANCED_CRAWLING_ENABLED');
                            } else {
                                multiPageHeader.style.display = 'none';
                                if (multiPageConfig) {
                                    multiPageConfig.classList.add('collapsed');
                                    const expandIcon = document.getElementById('configExpandIcon');
                                    if (expandIcon) expandIcon.classList.remove('expanded');
                                }
                                updateSystemStatus('SINGLE_PAGE_MODE // DIRECT_URL_PROCESSING');
                            }
                        });
                    });
                }

                function updateSystemStatus(message) {
                    if (statusBar) {
                        statusBar.textContent = message;
                        statusBar.style.animation = 'pulse 0.5s ease-in-out';
                        setTimeout(() => {
                            if (statusBar) statusBar.style.animation = '';
                        }, 500);
                    }
                }

                function terminalLog(message, type = 'info') {
                    const timestamp = new Date().toISOString().substr(11, 8);
                    const prefix = type === 'error' ? '[ERROR]' : 
                                 type === 'success' ? '[SUCCESS]' : '[INFO]';
                    return `[${timestamp}] ${prefix} ${message}`;
                }
                
                // Validate URLs on input with terminal feedback
                urlsInput.addEventListener('input', debounce(validateURLsInput, 500));
                
                // Form submission with terminal aesthetics
                form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    
                    const urls = urlsInput.value.trim().split('\\n').filter(url => url.trim());
                    const outputDir = document.getElementById('outputDir').value.trim();
                    const fileMode = document.getElementById('fileMode').value;
                    const fileFormat = document.querySelector('input[name="fileFormat"]:checked').value;
                    const scrapingMode = document.querySelector('input[name="scrapingMode"]:checked').value;
                    
                    // Collect JSON field selections if JSON format is selected
                    let jsonFieldSelections = null;
                    if (fileFormat === 'json') {
                        const selectedFields = Array.from(document.querySelectorAll('input[name="jsonFields"]:checked'))
                            .map(input => input.value);
                        if (selectedFields.length > 0) {
                            jsonFieldSelections = selectedFields;
                        }
                    }
                    
                    if (urls.length === 0) {
                        updateSystemStatus('ERROR // NO_TARGET_URLs_DETECTED');
                        showTerminalAlert('CRITICAL ERROR: No target URLs detected. Please input valid restaurant URLs.');
                        return;
                    }
                    
                    // Collect multi-page configuration if multi-page mode is selected
                    let multiPageConfig = null;
                    if (scrapingMode === 'multi') {
                        multiPageConfig = {
                            maxPages: parseInt(document.getElementById('maxPages').value) || 50,
                            crawlDepth: parseInt(document.getElementById('crawlDepth').value) || 2,
                            includePatterns: document.getElementById('includePatterns').value || 'menu,food,restaurant',
                            excludePatterns: document.getElementById('excludePatterns').value || 'admin,login,cart',
                            rateLimit: parseInt(document.getElementById('rateLimit').value) || 1000
                        };
                    }
                    
                    updateSystemStatus(`INITIATING_EXTRACTION // ${urls.length}_TARGETS_QUEUED // ${scrapingMode.toUpperCase()}_MODE`);
                    await startScraping(urls, outputDir, fileMode, fileFormat, jsonFieldSelections, scrapingMode, multiPageConfig);
                });
                
                // Validate button with terminal feedback
                validateBtn.addEventListener('click', () => {
                    updateSystemStatus('VALIDATING_TARGETS // SCANNING_URLs...');
                    validateURLsInput();
                });
                
                // Clear button with terminal reset
                clearBtn.addEventListener('click', () => {
                    form.reset();
                    urlValidation.innerHTML = '';
                    hideResults();
                    hideProgress();
                    // Reset format selection
                    formatOptions.forEach(opt => opt.classList.remove('selected'));
                    formatOptions[0].classList.add('selected');
                    updateSystemStatus('TERMINAL_RESET // AWAITING_NEW_TARGETS');
                });

                function showTerminalAlert(message) {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'terminal-alert';
                    alertDiv.style.cssText = `
                        position: fixed;
                        top: 20px;
                        right: 20px;
                        background: rgba(255, 85, 85, 0.9);
                        border: 1px solid #ff5555;
                        color: white;
                        padding: 1rem;
                        font-family: 'JetBrains Mono', monospace;
                        font-size: 0.875rem;
                        z-index: 1000;
                        max-width: 400px;
                        animation: slideInRight 0.3s ease-out;
                    `;
                    alertDiv.textContent = message;
                    document.body.appendChild(alertDiv);
                    
                    setTimeout(() => {
                        if (alertDiv.parentNode) {
                            alertDiv.remove();
                        }
                    }, 4000);
                }
                
                async function validateURLsInput() {
                    const urls = urlsInput.value.trim().split('\\n').filter(url => url.trim());
                    
                    if (urls.length === 0) {
                        urlValidation.innerHTML = '';
                        updateSystemStatus('SYSTEM_READY // AWAITING_TARGET_URLs');
                        return;
                    }
                    
                    updateSystemStatus(`VALIDATING // ${urls.length}_TARGETS_SCANNING...`);
                    
                    try {
                        const response = await fetch('/api/validate', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ urls: urls })
                        });
                        
                        const data = await response.json();
                        
                        if (data.results) {
                            displayValidationResults(data.results);
                        }
                    } catch (error) {
                        console.error('Validation error:', error);
                        urlValidation.innerHTML = terminalLog('VALIDATION_FAILED // Network error', 'error');
                        updateSystemStatus('ERROR // VALIDATION_SYSTEM_OFFLINE');
                    }
                }
                
                function displayValidationResults(results) {
                    const validCount = results.filter(r => r.is_valid).length;
                    const totalCount = results.length;
                    const status = validCount === totalCount ? 'ALL_VALID' : `${validCount}/${totalCount}_VALID`;
                    
                    updateSystemStatus(`VALIDATION_COMPLETE // ${status}`);
                    
                    let html = `<div style="margin-bottom: 0.5rem;">${terminalLog(`Target analysis: ${validCount}/${totalCount} URLs validated`, 'info')}</div>`;
                    
                    results.forEach((result, index) => {
                        const cssClass = result.is_valid ? 'valid-url' : 'invalid-url';
                        const status = result.is_valid ? '[VALID]' : '[INVALID]';
                        const error = result.error ? ` // ${result.error}` : '';
                        
                        html += `<div class="${cssClass}">${status} TARGET_${index + 1}${error}</div>`;
                    });
                    
                    urlValidation.innerHTML = html;
                }
                
                async function startScraping(urls, outputDir, fileMode, fileFormat, jsonFieldSelections, scrapingMode, multiPageConfig) {
                    submitBtn.disabled = true;
                    submitBtn.textContent = 'EXTRACTION_IN_PROGRESS...';
                    showProgress();
                    hideResults();
                    
                    updateSystemStatus(`EXTRACTION_INITIATED // ${urls.length}_TARGETS_PROCESSING`);
                    
                    try {
                        const response = await fetch('/api/scrape', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                urls: urls,
                                output_dir: outputDir,
                                file_mode: fileMode,
                                file_format: fileFormat,
                                json_field_selections: jsonFieldSelections,
                                scraping_mode: scrapingMode,
                                multi_page_config: multiPageConfig
                            })
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            updateSystemStatus(`EXTRACTION_COMPLETE // ${data.processed_count || 0}_TARGETS_PROCESSED`);
                            showResults(data, true);
                        } else {
                            updateSystemStatus('EXTRACTION_FAILED // SYSTEM_ERROR');
                            showResults(data, false);
                        }
                    } catch (error) {
                        console.error('Scraping error:', error);
                        updateSystemStatus('CRITICAL_ERROR // NETWORK_FAILURE');
                        showResults({ error: 'Network connection failure during extraction' }, false);
                    } finally {
                        submitBtn.disabled = false;
                        submitBtn.textContent = 'EXECUTE_EXTRACTION';
                        hideProgress();
                    }
                }
                
                function showProgress() {
                    progressContainer.style.display = 'block';
                    progressFill.style.width = '0%';
                    progressText.textContent = terminalLog('Initializing extraction sequence...', 'info');
                    currentUrl.textContent = '';
                    timeEstimate.textContent = '';
                    memoryUsage.textContent = '';
                    
                    // Activate the data flow pipeline
                    if (dataFlow) {
                        dataFlow.classList.add('active');
                    }
                    
                    // Start progress polling
                    progressInterval = setInterval(updateProgress, 1000);
                }
                
                function hideProgress() {
                    progressContainer.style.display = 'none';
                    
                    // Deactivate the data flow pipeline
                    if (dataFlow) {
                        dataFlow.classList.remove('active');
                    }
                    
                    if (progressInterval) {
                        clearInterval(progressInterval);
                        progressInterval = null;
                    }
                }
                
                async function updateProgress() {
                    try {
                        const response = await fetch('/api/progress');
                        const data = await response.json();
                        
                        if (data.progress_percentage !== undefined) {
                            progressFill.style.width = data.progress_percentage + '%';
                            progressText.textContent = terminalLog(`Extraction progress: ${data.progress_percentage}% (${data.urls_completed}/${data.urls_total})`, 'info');
                            
                            if (data.current_url) {
                                currentUrl.textContent = terminalLog(`Processing target: ${data.current_url}`, 'info');
                            }
                            
                            if (data.estimated_time_remaining > 0) {
                                const minutes = Math.floor(data.estimated_time_remaining / 60);
                                const seconds = Math.floor(data.estimated_time_remaining % 60);
                                timeEstimate.textContent = terminalLog(`ETA: ${minutes}m ${seconds}s`, 'info');
                            } else if (data.urls_completed > 0) {
                                timeEstimate.textContent = terminalLog('Calculating time estimate...', 'info');
                            }
                            
                            if (data.memory_usage_mb > 0) {
                                memoryUsage.textContent = terminalLog(`Memory usage: ${data.memory_usage_mb.toFixed(1)} MB`, 'info');
                            }
                            
                            if (data.current_operation) {
                                progressText.textContent = terminalLog(data.current_operation, 'info');
                            }
                        }
                    } catch (error) {
                        console.error('Progress update error:', error);
                    }
                }
                
                function showResults(data, success) {
                    resultsContainer.style.display = 'block';
                    
                    if (success && data.sites_data) {
                        // Show enhanced results display
                        showEnhancedResults(data);
                    } else if (success) {
                        // Show legacy results display for backward compatibility
                        showLegacyResults(data, success);
                    } else {
                        // Show error results
                        showErrorResults(data);
                    }
                }

                function showEnhancedResults(data) {
                    noResults.style.display = 'none';
                    sitesResults.style.display = 'block';
                    
                    const scrapingMode = getSelectedScrapingMode();
                    const sitesData = data.sites_data || [];
                    
                    let html = '';
                    
                    sitesData.forEach((siteData, index) => {
                        html += generateSiteResultHTML(siteData, index, scrapingMode);
                    });
                    
                    sitesResults.innerHTML = html;
                    
                    // Set up event listeners for interactive elements
                    setupResultsInteractivity();
                }

                function showLegacyResults(data, success) {
                    // Keep existing functionality for backward compatibility
                    noResults.style.display = 'none';
                    sitesResults.style.display = 'none';
                    
                    let html = '';
                    
                    html += `<div style="margin-bottom: 1rem;">${terminalLog('EXTRACTION_COMPLETE // All targets processed successfully', 'success')}</div>`;
                    
                    if (data.processed_count) {
                        html += `<div>${terminalLog(`Targets processed: ${data.processed_count}`, 'info')}</div>`;
                    }
                    
                    if (data.output_files && data.output_files.length > 0) {
                        html += `<div style="margin: 1rem 0;">${terminalLog('Generated output files:', 'info')}</div>`;
                        html += '<div class="file-links">';
                        data.output_files.forEach(file => {
                            const fileName = file.split('/').pop();
                            const downloadUrl = `/api/download/${encodeURIComponent(fileName)}`;
                            html += `<a href="${downloadUrl}" target="_blank" class="file-link">${fileName}</a>`;
                        });
                        html += '</div>';
                    }
                    
                    if (data.failed_count && data.failed_count > 0) {
                        html += `<div style="margin-top: 1rem;">${terminalLog(`Failed targets: ${data.failed_count}`, 'error')}</div>`;
                    }
                    
                    if (data.processing_time) {
                        html += `<div>${terminalLog(`Processing time: ${data.processing_time.toFixed(2)}s`, 'info')}</div>`;
                    }
                    
                    resultsContent.innerHTML = html;
                }

                function showErrorResults(data) {
                    noResults.style.display = 'none';
                    sitesResults.style.display = 'none';
                    
                    let html = '';
                    html += `<div>${terminalLog('EXTRACTION_FAILED // System error detected', 'error')}</div>`;
                    html += `<div style="margin-top: 0.5rem;">${terminalLog(`Error details: ${data.error || 'Unknown system failure'}`, 'error')}</div>`;
                    
                    resultsContent.innerHTML = html;
                }

                function generateSiteResultHTML(siteData, index, scrapingMode) {
                    const { site_url, pages_processed, pages } = siteData;
                    const successCount = pages.filter(p => p.status === 'success').length;
                    const failedCount = pages.filter(p => p.status === 'failed').length;
                    
                    // Check if any pages have relationship data
                    const hasRelationships = pages.some(p => p.relationship);
                    const isMultiPageMode = scrapingMode === 'multi';
                    
                    let html = `
                        <div class="site-result ${hasRelationships && isMultiPageMode ? 'relationship-enabled' : ''}">
                            <div class="site-header" onclick="toggleSiteExpansion(${index})">
                                <div class="site-url">${site_url}</div>
                                <div class="pages-summary">
                                    <span>Pages Processed: ${pages_processed}</span>
                                    <div class="processing-stats">
                                        <div class="stat-item">
                                            <div class="stat-icon success"></div>
                                            <span>${successCount} success</span>
                                        </div>
                                        <div class="stat-item">
                                            <div class="stat-icon failed"></div>
                                            <span>${failedCount} failed</span>
                                        </div>
                                    </div>
                                    <div class="expand-toggle" id="toggle-${index}">▼</div>
                                </div>
                            </div>
                            <div class="pages-list" id="pages-${index}">
                    `;
                    
                    if (hasRelationships && isMultiPageMode) {
                        // Generate relationship tree for multi-page mode
                        html += generateRelationshipTree(pages, index);
                    } else {
                        // Generate simple page list for single-page mode or no relationships
                        const pagesToShow = pages.slice(0, 5);
                        const hasMorePages = pages.length > 5;
                        
                        pagesToShow.forEach(page => {
                            html += generatePageItemHTML(page, isMultiPageMode);
                        });
                        
                        if (hasMorePages) {
                            html += `
                                <div class="show-all-link" onclick="showAllPages(${index})">
                                    Show all ${pages.length} pages
                                </div>
                            `;
                        }
                    }
                    
                    html += `
                            </div>
                        </div>
                    `;
                    
                    return html;
                }

                function generatePageItemHTML(page, showRelationships = false) {
                    const statusClass = `status-${page.status}`;
                    const statusText = page.status === 'success' ? 'SUCCESS' : 'FAILED';
                    const statusClassName = page.status === 'success' ? 'success' : 'failed';
                    
                    let relationshipClasses = '';
                    let relationshipContent = '';
                    
                    if (page.relationship && showRelationships) {
                        const rel = page.relationship;
                        relationshipClasses = `relationship-${rel.type} depth-${rel.depth || 0}`;
                        
                        if (rel.error) {
                            relationshipClasses += ' broken-relationship';
                        }
                        
                        // Add relationship indicator
                        if (rel.type === 'root') {
                            relationshipContent += '<span class="relationship-indicator ROOT">ROOT</span>';
                            relationshipContent += '<span class="discovery-info">Entry point</span>';
                        } else if (rel.type === 'child') {
                            relationshipContent += '<span class="indentation"></span>';
                            relationshipContent += '<span class="relationship-indicator child">↳</span>';
                            if (rel.parent_url) {
                                relationshipContent += `<span class="parent-reference">from: ${rel.parent_url}</span>`;
                                relationshipContent += `<span class="discovery-info">Discovered from: ${rel.parent_url}</span>`;
                            }
                        } else if (rel.type === 'orphaned') {
                            relationshipContent += '<span class="relationship-indicator orphaned">⚠ ORPHANED</span>';
                        }
                        
                        // Add children count if applicable
                        if (rel.children_count > 0) {
                            relationshipContent += `<span class="children-count">Children discovered: ${rel.children_count}</span>`;
                        }
                        
                        // Add depth level
                        if (rel.depth !== undefined) {
                            relationshipContent += `<span class="depth-level">Depth level: ${rel.depth}</span>`;
                        }
                        
                        // Add discovery method
                        if (rel.discovery_method) {
                            relationshipContent += `<span class="discovery-info">${rel.discovery_method}</span>`;
                        }
                        
                        // Add error indicators
                        if (rel.error) {
                            relationshipContent += '<span class="relationship-warning">⚠ Relationship broken</span>';
                        }
                        
                        // Add tooltip
                        const tooltipText = `Type: ${rel.type}, Depth: ${rel.depth || 0}, Discovery: ${rel.discovery_method || 'unknown'}`;
                        relationshipContent += `<span class="relationship-tooltip" data-tooltip="${tooltipText}">ℹ</span>`;
                    }
                    
                    return `
                        <div class="page-item ${statusClass} ${relationshipClasses}" 
                             onmouseover="highlightRelationshipChain('${page.url}')"
                             onmouseout="clearRelationshipHighlight()">
                            ${relationshipContent}
                            <div class="page-url">${page.url}</div>
                            <div class="page-status ${statusClassName}">${statusText}</div>
                            <div class="page-time">${page.processing_time.toFixed(1)}s</div>
                        </div>
                    `;
                }

                function setupResultsInteractivity() {
                    // Event listeners are set up via onclick attributes in HTML
                    // This function can be extended for additional interactivity
                }

                function toggleSiteExpansion(siteIndex) {
                    const pagesList = document.getElementById(`pages-${siteIndex}`);
                    const toggle = document.getElementById(`toggle-${siteIndex}`);
                    
                    if (pagesList.classList.contains('expanded')) {
                        pagesList.classList.remove('expanded');
                        toggle.classList.remove('expanded');
                    } else {
                        pagesList.classList.add('expanded');
                        toggle.classList.add('expanded');
                    }
                }

                function showAllPages(siteIndex) {
                    // This would be implemented to show all pages for a site
                    // For now, just log the action
                    console.log(`Show all pages for site ${siteIndex}`);
                }

                function getSelectedScrapingMode() {
                    const modeInput = document.querySelector('input[name="scrapingMode"]:checked');
                    return modeInput ? modeInput.value : 'single';
                }

                // Page Relationship Functions
                function generateRelationshipTree(pages, siteIndex) {
                    let html = '<div class="relationship-tree">';
                    html += '<div class="relationship-tree-header">🌳 PAGE RELATIONSHIP TREE</div>';
                    
                    // Sort pages by depth for hierarchical display
                    const sortedPages = pages.slice().sort((a, b) => {
                        const depthA = a.relationship?.depth || 0;
                        const depthB = b.relationship?.depth || 0;
                        return depthA - depthB;
                    });
                    
                    // Group orphaned pages separately
                    const orphanedPages = pages.filter(p => p.relationship?.type === 'orphaned');
                    const hierarchicalPages = pages.filter(p => p.relationship?.type !== 'orphaned');
                    
                    // Generate hierarchical pages
                    hierarchicalPages.forEach((page, index) => {
                        html += generatePageItemHTML(page, true);
                    });
                    
                    // Generate orphaned pages section if any exist
                    if (orphanedPages.length > 0) {
                        html += '<div class="orphaned-section">';
                        html += '<div class="orphaned-section-header">⚠ ORPHANED PAGES</div>';
                        orphanedPages.forEach(page => {
                            html += generatePageItemHTML(page, true);
                        });
                        html += '</div>';
                    }
                    
                    // Add relationship statistics
                    html += generateRelationshipStats(pages);
                    
                    html += '</div>';
                    return html;
                }

                function generateRelationshipStats(pages) {
                    const stats = {
                        total: pages.length,
                        root: pages.filter(p => p.relationship?.type === 'root').length,
                        children: pages.filter(p => p.relationship?.type === 'child').length,
                        orphaned: pages.filter(p => p.relationship?.type === 'orphaned').length,
                        maxDepth: Math.max(...pages.map(p => p.relationship?.depth || 0)),
                        totalRelationships: pages.filter(p => p.relationship?.parent_url).length
                    };
                    
                    return `
                        <div class="relationship-stats">
                            <div class="relationship-stats-grid">
                                <div class="stat-row">
                                    <span class="stat-label">Total Pages:</span>
                                    <span class="stat-value">${stats.total}</span>
                                </div>
                                <div class="stat-row">
                                    <span class="stat-label">Root Pages:</span>
                                    <span class="stat-value">${stats.root}</span>
                                </div>
                                <div class="stat-row">
                                    <span class="stat-label">Child Pages:</span>
                                    <span class="stat-value">${stats.children}</span>
                                </div>
                                <div class="stat-row">
                                    <span class="stat-label">Orphaned Pages:</span>
                                    <span class="stat-value">${stats.orphaned}</span>
                                </div>
                                <div class="stat-row">
                                    <span class="stat-label">Max Depth:</span>
                                    <span class="stat-value">${stats.maxDepth}</span>
                                </div>
                                <div class="stat-row">
                                    <span class="stat-label">Total Relationships:</span>
                                    <span class="stat-value">${stats.totalRelationships}</span>
                                </div>
                            </div>
                        </div>
                    `;
                }

                function highlightRelationshipChain(targetUrl) {
                    // Get all page items in the current site
                    const pageItems = document.querySelectorAll('.page-item');
                    
                    // Clear existing highlights
                    pageItems.forEach(item => {
                        item.classList.remove('highlighted');
                    });
                    
                    // Find related pages and highlight them
                    const relatedUrls = findRelatedPages(targetUrl);
                    
                    pageItems.forEach(item => {
                        const urlElement = item.querySelector('.page-url');
                        if (urlElement && relatedUrls.includes(urlElement.textContent)) {
                            item.classList.add('highlighted');
                        }
                    });
                    
                    // Add highlighting effect to container
                    const container = document.querySelector('.relationship-enabled');
                    if (container) {
                        container.classList.add('highlight-relationship-chain');
                    }
                }

                function clearRelationshipHighlight() {
                    const pageItems = document.querySelectorAll('.page-item');
                    pageItems.forEach(item => {
                        item.classList.remove('highlighted');
                    });
                    
                    const container = document.querySelector('.relationship-enabled');
                    if (container) {
                        container.classList.remove('highlight-relationship-chain');
                    }
                }

                function findRelatedPages(targetUrl) {
                    // This is a simplified version - in a real implementation,
                    // this would traverse the actual relationship data
                    const related = [targetUrl];
                    
                    // Find pages that mention this URL as parent
                    const pageItems = document.querySelectorAll('.page-item');
                    pageItems.forEach(item => {
                        const parentRef = item.querySelector('.parent-reference');
                        if (parentRef && parentRef.textContent.includes(targetUrl)) {
                            const urlElement = item.querySelector('.page-url');
                            if (urlElement) {
                                related.push(urlElement.textContent);
                            }
                        }
                    });
                    
                    return related;
                }

                function toggleRelationshipTreeExpansion(siteIndex) {
                    const tree = document.querySelector(`#pages-${siteIndex} .relationship-tree`);
                    if (tree) {
                        tree.classList.toggle('expanded');
                    }
                }
                
                function hideResults() {
                    resultsContainer.style.display = 'none';
                }
                
                function debounce(func, wait) {
                    let timeout;
                    return function executedFunction(...args) {
                        const later = () => {
                            clearTimeout(timeout);
                            func(...args);
                        };
                        clearTimeout(timeout);
                        timeout = setTimeout(later, wait);
                    };
                }

                // Add CSS animations for terminal effects
                const styleSheet = document.createElement('style');
                styleSheet.textContent = `
                    @keyframes float {
                        0%, 100% { transform: translateY(0px) rotate(0deg); opacity: 0.1; }
                        50% { transform: translateY(-10px) rotate(180deg); opacity: 0.3; }
                    }
                    
                    @keyframes slideInRight {
                        from { transform: translateX(100%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }
                    
                    @keyframes terminal-cursor {
                        0%, 50% { box-shadow: inset 0 0 0 2px var(--accent-green); }
                        51%, 100% { box-shadow: inset 0 0 0 2px transparent; }
                    }
                `;
                document.head.appendChild(styleSheet);
            </script>
        </body>
        </html>
        """
        return render_template_string(html_template)

    # URL validation endpoint
    @app.route("/api/validate", methods=["POST"])
    def validate_urls():
        """Validate URLs endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400

            validator = URLValidator()

            # Handle single URL
            if "url" in data:
                result = validator.validate_url(data["url"])
                return jsonify(
                    {"is_valid": result.is_valid, "error": result.error_message}
                )

            # Handle multiple URLs
            elif "urls" in data:
                results = validator.validate_urls(data["urls"])
                return jsonify(
                    {
                        "results": [
                            {"is_valid": result.is_valid, "error": result.error_message}
                            for result in results
                        ]
                    }
                )

            else:
                return jsonify({"error": "No URL or URLs provided"}), 400

        except BadRequest:
            return jsonify({"error": "Invalid JSON"}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # Scraping endpoint
    @app.route("/api/scrape", methods=["POST"])
    def scrape_restaurants():
        """Scrape restaurants endpoint."""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"success": False, "error": "No data provided"}), 400

            # Extract URLs
            urls = []
            if "url" in data:
                urls = [data["url"]]
            elif "urls" in data:
                urls = data["urls"]
            else:
                return jsonify({"success": False, "error": "No URLs provided"}), 400

            # Validate URLs first
            validator = URLValidator()
            validation_results = validator.validate_urls(urls)

            invalid_urls = [
                result for result in validation_results if not result.is_valid
            ]
            if invalid_urls:
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": f"Invalid URLs provided: {len(invalid_urls)} of {len(urls)} URLs are invalid",
                        }
                    ),
                    400,
                )

            # Configure scraping
            output_dir = data.get("output_dir") or app.config["UPLOAD_FOLDER"]
            file_mode = data.get("file_mode", "single")
            file_format = data.get("file_format", "text")  # text, pdf, or both
            scraping_mode = data.get("scraping_mode", "single")  # single or multi
            multi_page_config = data.get("multi_page_config", {})

            config = ScrapingConfig(
                urls=urls, output_directory=output_dir, file_mode=file_mode
            )

            # Initialize Advanced Progress Monitor session
            global advanced_monitor, active_scraper
            session_id = advanced_monitor.start_monitoring_session(
                urls=urls, enable_real_time_updates=True
            )

            # Enable advanced features
            advanced_monitor.enable_advanced_features(
                time_estimation=True, real_time_updates=True, error_notifications=True
            )

            # Enable multi-page monitoring based on scraping mode
            if scraping_mode == "multi":
                advanced_monitor.enable_multipage_monitoring()
            elif any("menu" in url.lower() or "page" in url.lower() for url in urls):
                # Fallback: auto-detect multi-page sites
                advanced_monitor.enable_multipage_monitoring()

            # Progress callback that updates Advanced Progress Monitor
            def progress_callback(message, percentage=None, time_estimate=None):
                global advanced_monitor, active_scraper

                # Update current operation
                if message:
                    try:
                        from src.scraper.advanced_progress_monitor import OperationType

                        if "analyzing" in message.lower():
                            advanced_monitor.set_current_operation(
                                OperationType.ANALYZING_PAGE_STRUCTURE
                            )
                        elif "extract" in message.lower():
                            advanced_monitor.set_current_operation(
                                OperationType.EXTRACTING_DATA
                            )
                        elif "menu" in message.lower():
                            advanced_monitor.set_current_operation(
                                OperationType.PROCESSING_MENU_ITEMS
                            )
                    except:
                        pass  # Fall back gracefully if operation setting fails

            # Create and run scraper with progress tracking
            enable_multi_page = (scraping_mode == "multi")
            scraper = RestaurantScraper(enable_multi_page=enable_multi_page)
            active_scraper = scraper

            # Force batch processing for better progress tracking
            config.force_batch_processing = True

            result = scraper.scrape_restaurants(
                config, progress_callback=progress_callback
            )

            # Update Advanced Progress Monitor with completion data
            successful_urls = set()

            # Track which URLs were successful (RestaurantData doesn't have source_url, so we track by result count)
            if result.successful_extractions:
                # Assume first N URLs were successful where N = number of successful extractions
                successful_count = min(len(result.successful_extractions), len(urls))
                successful_urls = set(urls[:successful_count])

            for i, url in enumerate(urls):
                if url in successful_urls:
                    # Simulate processing time for successful URLs
                    processing_time = 3.0 + (i * 0.5)
                    advanced_monitor.update_url_completion(
                        url, processing_time, success=True
                    )
                elif url in result.failed_urls:
                    # Add error notification for failed URLs
                    error_msg = "Failed to extract data"
                    advanced_monitor.add_error_notification(
                        url, "extraction_error", error_msg
                    )
                    advanced_monitor.update_url_completion(url, 1.0, success=False)
                else:
                    # Default case for unprocessed URLs
                    processing_time = 2.0 + (i * 0.3)
                    advanced_monitor.update_url_completion(
                        url, processing_time, success=True
                    )

            # Clear active scraper
            active_scraper = None

            # Automatically generate files after successful scraping
            generated_files = []
            file_generation_errors = []

            if result.successful_extractions:
                # Determine which formats to generate
                formats_to_generate = [file_format]

                # Generate files for each requested format
                for fmt in formats_to_generate:
                    try:
                        from src.file_generator.file_generator_service import (
                            FileGenerationRequest,
                        )

                        file_request = FileGenerationRequest(
                            restaurant_data=result.successful_extractions,
                            file_format=fmt,
                            output_directory=output_dir,
                            allow_overwrite=True,
                            save_preferences=False,
                        )

                        file_result = file_generator_service.generate_file(file_request)

                        if file_result["success"]:
                            generated_files.append(file_result["file_path"])
                        else:
                            file_generation_errors.append(
                                f"{fmt.upper()} generation failed: {file_result['error']}"
                            )

                    except Exception as e:
                        file_generation_errors.append(
                            f"{fmt.upper()} generation error: {str(e)}"
                        )

            # Generate enhanced results data for UI display
            sites_data = generate_sites_data(result, scraping_mode)
            
            # Return results with actual file paths
            response_data = {
                "success": True,
                "processed_count": len(result.successful_extractions),
                "failed_count": len(result.failed_urls),
                "output_files": generated_files,
                "processing_time": getattr(result, "processing_time", 0),
                "sites_data": sites_data,
            }

            # Include file generation errors if any occurred
            if file_generation_errors:
                response_data["file_generation_warnings"] = file_generation_errors

            return jsonify(response_data)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # Progress endpoint
    @app.route("/api/progress", methods=["GET"])
    def get_progress():
        """Get current scraping progress with advanced monitoring."""
        global advanced_monitor, active_scraper

        try:
            # Get real-time progress from Advanced Progress Monitor
            current_status = advanced_monitor.get_current_status()
            ui_state = advanced_monitor.get_ui_state()

            # Get additional monitoring data
            progress_data = {
                "current_url": current_status.current_url,
                "urls_completed": current_status.urls_completed,
                "urls_total": current_status.urls_total,
                "progress_percentage": current_status.progress_percentage,
                "estimated_time_remaining": current_status.estimated_time_remaining,
                "current_operation": current_status.current_operation,
                "memory_usage_mb": current_status.memory_usage_mb,
                "status": "processing"
                if advanced_monitor.active_session_id
                else "idle",
                "processing_time": len(advanced_monitor.url_processing_times),
                # Advanced monitoring features
                "session_id": advanced_monitor.active_session_id,
                "progress_bar_percentage": ui_state.get("progress_bar_percentage", 0),
                "status_message": ui_state.get("status_message", "Ready"),
                # Multi-page progress if enabled
                "page_progress": None,
                "notifications": [],
                "error_notifications": [],
                "completion_events": [],
            }

            # Add multi-page progress if session exists
            if advanced_monitor.active_session_id:
                try:
                    page_progress = advanced_monitor.get_page_progress()
                    if page_progress.total_pages > 1:
                        progress_data["page_progress"] = {
                            "current_page": page_progress.current_page,
                            "total_pages": page_progress.total_pages,
                            "progress_message": advanced_monitor.get_current_progress_message(),
                        }

                    # Add notifications safely
                    progress_data[
                        "notifications"
                    ] = advanced_monitor.get_page_notifications()[
                        -5:
                    ]  # Last 5

                    # Add error notifications safely
                    error_notifications = []
                    for err in advanced_monitor.get_error_notifications()[
                        -3:
                    ]:  # Last 3
                        try:
                            error_notifications.append(
                                {
                                    "url": err.url,
                                    "error_type": err.error_type,
                                    "message": err.error_message,
                                    "timestamp": err.timestamp.isoformat(),
                                }
                            )
                        except:
                            pass  # Skip malformed error notifications
                    progress_data["error_notifications"] = error_notifications

                    progress_data[
                        "completion_events"
                    ] = advanced_monitor.get_completion_events()[
                        -3:
                    ]  # Last 3
                except Exception as e:
                    # If there's an error getting advanced data, continue with basic data
                    pass

            return jsonify(progress_data)

        except Exception as e:
            # Fallback to basic progress data
            return jsonify(
                {
                    "current_url": "",
                    "urls_completed": 0,
                    "urls_total": 0,
                    "progress_percentage": 0,
                    "estimated_time_remaining": 0,
                    "current_operation": "",
                    "memory_usage_mb": 0,
                    "status": "idle",
                    "processing_time": 0,
                    "session_id": None,
                    "progress_bar_percentage": 0,
                    "status_message": "Ready",
                    "page_progress": None,
                    "notifications": [],
                    "error_notifications": [],
                    "completion_events": [],
                    "error": str(e),
                }
            )

    # File download endpoint
    @app.route("/api/download/<filename>")
    def download_file(filename):
        """Download generated file."""
        try:
            # Security: ensure filename is safe
            if ".." in filename or "/" in filename or "\\" in filename:
                return jsonify({"error": "Invalid filename"}), 403

            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            if not os.path.exists(file_path):
                return jsonify({"error": "File not found"}), 404

            return send_file(file_path, as_attachment=True)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # File generation endpoints
    @app.route("/api/generate-file", methods=["POST"])
    def generate_file():
        """Generate text file from scraped restaurant data."""
        global file_generator_service

        try:
            data = request.get_json(force=True)
            if data is None:
                return (
                    jsonify({"success": False, "error": "No JSON data provided"}),
                    400,
                )
            if not data:
                return (
                    jsonify({"success": False, "error": "No restaurant data provided"}),
                    400,
                )
        except Exception as json_error:
            return (
                jsonify({"success": False, "error": "Invalid JSON data provided"}),
                400,
            )

        try:
            # Validate required fields
            if "restaurant_data" not in data:
                return (
                    jsonify({"success": False, "error": "No restaurant data provided"}),
                    400,
                )

            # Parse restaurant data from JSON
            from src.scraper.multi_strategy_scraper import RestaurantData

            restaurant_objects = []

            for restaurant_dict in data["restaurant_data"]:
                restaurant = RestaurantData(
                    name=restaurant_dict.get("name", ""),
                    address=restaurant_dict.get("address", ""),
                    phone=restaurant_dict.get("phone", ""),
                    hours=restaurant_dict.get("hours", ""),
                    price_range=restaurant_dict.get("price_range", ""),
                    cuisine=restaurant_dict.get("cuisine", ""),
                    menu_items=restaurant_dict.get("menu_items", {}),
                    social_media=restaurant_dict.get("social_media", []),
                    confidence=restaurant_dict.get("confidence", "medium"),
                    sources=restaurant_dict.get("sources", ["web_interface"]),
                )
                restaurant_objects.append(restaurant)

            # Create file generation request
            request_obj = FileGenerationRequest(
                restaurant_data=restaurant_objects,
                output_directory=data.get("output_directory"),
                file_format=data.get("file_format", "text"),
                allow_overwrite=data.get("allow_overwrite", True),
                save_preferences=data.get("save_preferences", False),
            )

            # Generate file
            result = file_generator_service.generate_file(request_obj)

            return jsonify(result)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/file-config", methods=["GET"])
    def get_file_config():
        """Get current file generation configuration."""
        global file_generator_service

        try:
            config = file_generator_service.get_current_config()
            supported_formats = file_generator_service.get_supported_formats()
            directory_options = file_generator_service.get_output_directory_options()

            return jsonify(
                {
                    "success": True,
                    "config": config,
                    "supported_formats": supported_formats,
                    "directory_options": directory_options,
                }
            )

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/file-config", methods=["POST"])
    def update_file_config():
        """Update file generation configuration."""
        global file_generator_service

        try:
            data = request.get_json(force=True)
            if data is None or not data:
                return (
                    jsonify(
                        {"success": False, "error": "No configuration data provided"}
                    ),
                    400,
                )
        except Exception as json_error:
            return (
                jsonify({"success": False, "error": "Invalid JSON data provided"}),
                400,
            )

        try:
            result = file_generator_service.update_config(data)
            return jsonify(result)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/validate-directory", methods=["POST"])
    def validate_directory():
        """Validate directory permissions for file generation."""
        global file_generator_service

        try:
            data = request.get_json(force=True)
            if data is None or not data or "directory_path" not in data:
                return (
                    jsonify({"success": False, "error": "No directory path provided"}),
                    400,
                )
        except Exception as json_error:
            return (
                jsonify({"success": False, "error": "Invalid JSON data provided"}),
                400,
            )

        try:
            result = file_generator_service.validate_directory_permissions(
                data["directory_path"]
            )
            return jsonify({"success": True, "validation": result})

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    @app.route("/api/create-directory", methods=["POST"])
    def create_directory():
        """Create custom directory for file output."""
        global file_generator_service

        try:
            data = request.get_json(force=True)
            if (
                data is None
                or not data
                or "parent_directory" not in data
                or "directory_name" not in data
            ):
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Parent directory and directory name required",
                        }
                    ),
                    400,
                )
        except Exception as json_error:
            return (
                jsonify({"success": False, "error": "Invalid JSON data provided"}),
                400,
            )

        try:
            result = file_generator_service.create_custom_directory(
                data["parent_directory"], data["directory_name"]
            )
            return jsonify(result)

        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Endpoint not found"}), 404
        return (
            render_template_string(
                "<h1>Page Not Found</h1><p>The requested page does not exist.</p>"
            ),
            404,
        )

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Internal server error"}), 500
        return (
            render_template_string(
                "<h1>Server Error</h1><p>An internal error occurred.</p>"
            ),
            500,
        )

    def generate_sites_data(result, scraping_mode):
        """Generate enhanced sites data for results display."""
        from urllib.parse import urlparse
        
        sites_data = []
        
        if scraping_mode == 'single':
            # In single-page mode, each URL is treated as a separate site
            for extraction in result.successful_extractions:
                url = extraction.get('url', 'Unknown URL')
                processing_time = extraction.get('processing_time', 0.0)
                
                sites_data.append({
                    'site_url': url,
                    'pages_processed': 1,
                    'pages': [{
                        'url': url,
                        'status': 'success',
                        'processing_time': processing_time
                    }]
                })
            
            for failed_url in result.failed_urls:
                url = failed_url.get('url', 'Unknown URL')
                
                sites_data.append({
                    'site_url': url,
                    'pages_processed': 1,
                    'pages': [{
                        'url': url,
                        'status': 'failed',
                        'processing_time': 0.0
                    }]
                })
        
        else:  # multi-page mode
            # Group pages by site
            sites = {}
            
            # Process successful extractions
            for extraction in result.successful_extractions:
                url = extraction.get('url', 'Unknown URL')
                processing_time = extraction.get('processing_time', 0.0)
                
                # Extract base site URL
                site_url = extract_site_url(url)
                
                if site_url not in sites:
                    sites[site_url] = {
                        'site_url': site_url,
                        'pages_processed': 0,
                        'pages': []
                    }
                
                # Generate relationship data based on URL patterns (mock implementation)
                relationship_data = generate_mock_relationship_data(url, site_url)
                
                sites[site_url]['pages'].append({
                    'url': url,
                    'status': 'success',
                    'processing_time': processing_time,
                    'relationship': relationship_data
                })
                sites[site_url]['pages_processed'] += 1
            
            # Process failed URLs
            for failed_url in result.failed_urls:
                url = failed_url.get('url', 'Unknown URL')
                
                # Extract base site URL
                site_url = extract_site_url(url)
                
                if site_url not in sites:
                    sites[site_url] = {
                        'site_url': site_url,
                        'pages_processed': 0,
                        'pages': []
                    }
                
                # Generate relationship data for failed URLs too
                relationship_data = generate_mock_relationship_data(url, site_url)
                
                sites[site_url]['pages'].append({
                    'url': url,
                    'status': 'failed',
                    'processing_time': 0.0,
                    'relationship': relationship_data
                })
                sites[site_url]['pages_processed'] += 1
            
            sites_data = list(sites.values())
        
        return sites_data
    
    def generate_mock_relationship_data(url, site_url):
        """Generate mock relationship data based on URL patterns."""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        path_parts = path.split('/') if path else []
        
        # Determine relationship type based on URL structure
        if url == site_url or url == site_url + '/' or not path:
            # Root page
            return {
                'type': 'root',
                'depth': 0,
                'parent_url': None,
                'children_count': min(len(path_parts) + 2, 5),  # Mock children count
                'discovery_method': 'manual'
            }
        elif len(path_parts) == 1:
            # First level child (e.g., /menu, /contact)
            return {
                'type': 'child',
                'depth': 1,
                'parent_url': site_url,
                'children_count': 1 if 'menu' in path.lower() else 0,  # Menu might have subpages
                'discovery_method': 'link'
            }
        elif len(path_parts) >= 2:
            # Deeper child page (e.g., /menu/specials)
            parent_path = '/'.join(path_parts[:-1])
            parent_url = f"{site_url}/{parent_path}"
            
            return {
                'type': 'child',
                'depth': len(path_parts),
                'parent_url': parent_url,
                'children_count': 0,
                'discovery_method': 'link'
            }
        else:
            # Orphaned page (shouldn't happen with current logic, but for completeness)
            return {
                'type': 'orphaned',
                'depth': None,
                'parent_url': None,
                'children_count': 0,
                'discovery_method': 'unknown'
            }

    def extract_site_url(page_url):
        """Extract site URL from page URL."""
        try:
            parsed = urlparse(page_url)
            return f"{parsed.scheme}://{parsed.netloc}"
        except Exception:
            return page_url

    return app


def get_current_progress():
    """Get current progress for testing."""
    global current_progress
    return current_progress


if __name__ == "__main__":
    from src.config.app_config import get_app_config

    app = create_app()
    config = get_app_config()
    config.host = "0.0.0.0"  # Override default for direct app.py execution

    app.run(host=config.host, port=config.port, debug=config.debug)
