#!/bin/bash

echo "🚀 Setting up Future Founder Finder..."
echo "======================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs templates

# Copy environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating .env file..."
    cp env_example.txt .env
    echo "✅ Created .env file. Please edit it with your configuration."
fi

# Test the setup
echo "🧪 Testing setup..."
python3 test_setup.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the app: python3 run.py"
echo "3. Open http://localhost:5000 in your browser"
echo ""
echo "To run the demo:"
echo "python3 demo.py" 