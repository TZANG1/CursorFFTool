"""
Future Founder Finder - Flask Application Package
"""

from flask import Flask
from flask_cors import CORS
from config import Config
from loguru import logger
import os
import sys

def create_app(config_class=Config):
    """Application factory pattern for Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Enable CORS
    CORS(app)
    
    # Configure logging
    setup_logging(app)
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app

def setup_logging(app):
    """Configure application logging"""
    log_file = app.config.get('LOG_FILE', 'logs/app.log')
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure loguru
    logger.remove()  # Remove default handler
    logger.add(
        log_file,
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    )
    
    # Also log to console in debug mode
    if app.config.get('DEBUG', False):
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>"
        )

def init_extensions(app):
    """Initialize Flask extensions"""
    # Database initialization will be done in db_manager
    pass

def register_blueprints(app):
    """Register Flask blueprints"""
    try:
        from app.main import bp as main_bp
        app.register_blueprint(main_bp)
    except ImportError as e:
        print(f"Warning: Could not import main blueprint: {e}")
    
    # Import and register other blueprints as needed
    # from app.api import bp as api_bp
    # app.register_blueprint(api_bp, url_prefix='/api') 