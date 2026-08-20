#!/bin/bash

echo "🚀 Setting up AI Phishing Detection System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your VirusTotal API key and secret key"
fi

# Initialize database
echo "🗄️  Initializing database..."
flask init-db

# Seed database with admin user
echo "👤 Creating admin user..."
flask seed-db

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and add your VirusTotal API key"
echo "2. Update SECRET_KEY in .env with a strong random key"
echo "3. Run the application with: flask run"
echo "4. Or for development: python app.py"
echo ""
echo "🔐 Default admin credentials:"
echo "   Email: admin@ssipmt.com"
echo "   Password: Admin@123"
echo "   ⚠️  Change these credentials after first login!"
echo ""
