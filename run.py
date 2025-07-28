#!/usr/bin/env python3
"""
Future Founder Finder - Main Application Entry Point
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5001) 