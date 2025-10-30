#!/bin/bash
# Azure Web App Startup Script
# This script starts the IDE DevOps MCP server in PAT authentication mode

echo "=== IDE DevOps MCP - Azure Web App Startup ==="
echo "Starting server with PAT authentication..."

# Check if required environment variables are set
if [ -z "$AZURE_DEVOPS_ORG" ]; then
    echo "ERROR: AZURE_DEVOPS_ORG environment variable is required"
    exit 1
fi

echo "Organization: $AZURE_DEVOPS_ORG"
echo "Port: ${PORT:-8000}"
echo "Authentication: PAT via X-Azure-DevOps-PAT header"

# Start the server
python -m azure_devops_mcp.main \
    --authentication pat \
    --mode http \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --domains all

echo "Server startup complete!"