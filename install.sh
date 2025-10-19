#!/bin/bash

# Enhanced Kubernetes AI Agent Installation Script

echo "🚀 Installing Enhanced Kubernetes AI Agent..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version+ is required, but you have $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 detected"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl is not installed or not in PATH"
    echo "Please install kubectl and ensure it's configured to access your cluster"
    echo "Visit: https://kubernetes.io/docs/tasks/tools/"
else
    echo "✅ kubectl detected"
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Google API Key (required)
GOOGLE_API_KEY=your-google-api-key-here

# Optional configuration
K8S_MODEL=gemini-2.0-flash
K8S_TEMPERATURE=0.1
K8S_MAX_TOKENS=2048
K8S_NAMESPACE=default
K8S_MAX_REPLICAS=10
EOF
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file and add your Google API key"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your Google API key"
echo "2. Ensure kubectl is configured for your cluster"
echo "3. Run: python3 k8s.py"
echo ""
echo "For help, run: python3 k8s.py --help"