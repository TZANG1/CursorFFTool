"""
Configuration for Future Founder Finder
"""

import os
from typing import Dict, Any

class Config:
    """Configuration class"""
    
    def __init__(self):
        # GitHub API configuration
        self.GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # Get from environment variable
        self.GITHUB_API = 'https://api.github.com'
        
        # Logging configuration
        self.LOG_LEVEL = 'INFO'
        self.LOG_FILE = 'logs/app.log'
        
        # Rate limiting configuration
        self.RATE_LIMITS: Dict[str, Any] = {
            'github': {
                'requests_per_hour': 5000,  # GitHub's free tier limit
                'buffer': 500  # Keep some requests as buffer
            }
        } 