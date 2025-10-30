#!/bin/bash
# Azure Web App Startup Script
# This script starts the IDE DevOps MCP server in PAT authentication mode

echo "=== IDE DevOps MCP - Azure Web App Startup ==="
echo "Python version: $(python --version)"
echo "Current working directory: $(pwd)"
echo "Contents: $(ls -la)"

# Check if required environment variables are set
if [ -z "$AZURE_DEVOPS_ORG" ]; then
    echo "ERROR: AZURE_DEVOPS_ORG environment variable is required"
    exit 1
fi

echo "Organization: $AZURE_DEVOPS_ORG"
echo "Port: ${PORT:-8000}"
echo "Authentication: PAT via X-Azure-DevOps-PAT header"

# Upgrade pip and install dependencies
echo "Upgrading pip..."
python -m pip install --upgrade pip

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt --verbose

# Verify installation
echo "Verifying MCP installation..."
python -c "import mcp.server; print('MCP server module imported successfully')" || {
    echo "ERROR: Failed to import MCP server module"
    echo "Trying alternative installation..."
    python -m pip install mcp --force-reinstall
    python -c "import mcp.server; print('MCP server module imported successfully after reinstall')" || {
        echo "CRITICAL ERROR: Cannot import MCP module"
        exit 1
    }
}

echo "Dependencies installed and verified successfully!"

# Start the server
echo "Starting Azure DevOps MCP server..."
python -m azure_devops_mcp.main \
    "$AZURE_DEVOPS_ORG" \
    --authentication pat \
    --mode http \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --domains all

echo "Server startup complete!"