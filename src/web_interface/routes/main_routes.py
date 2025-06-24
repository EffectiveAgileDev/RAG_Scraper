"""Main routes for the web interface."""
from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    """Serve main interface."""
    return render_template('index.html')