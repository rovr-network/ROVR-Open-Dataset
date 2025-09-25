#!/bin/bash
# Data File Decryption Tool Installation Script

echo "🔧 Data File Decryption Tool Installation Script"
echo "================================================="

# Check Python version
echo "🐍 Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Error: Python 3.7 or higher is required"
    exit 1
fi

# Check pip
echo "📦 Checking pip..."
python3 -m pip --version
if [ $? -ne 0 ]; then
    echo "❌ Error: pip package manager is required"
    exit 1
fi

# Install dependencies
echo "📥 Installing dependencies..."
python3 -m pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "🚀 Installation complete! You can now use the decryption tool:"
    echo "   python3 data_decryptor.py --help"
    echo ""
    echo "📖 View usage examples:"
    echo "   python3 example_usage.py"
else
    echo "❌ Dependencies installation failed"
    exit 1
fi
