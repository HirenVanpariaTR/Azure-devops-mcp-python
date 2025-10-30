# Azure Web App Configuration Example

# This file demonstrates how to configure the IDE DevOps MCP server 
# for deployment to Azure Web App

## Method 1: Environment Variable Authentication (Traditional)
# Application Settings (Environment Variables) in Azure Web App:
# AZURE_DEVOPS_ORG=your-organization-name
# AZURE_DEVOPS_EXT_PAT=your-personal-access-token  (for 'env' authentication)

# Example startup command for Azure Web App:
# python -m azure_devops_mcp --authentication env --mode http --host 0.0.0.0 --port 8000

## Method 2: PAT Header Authentication (New - Recommended for APIs)
# Application Settings (Environment Variables) in Azure Web App:
# AZURE_DEVOPS_ORG=your-organization-name

# Example startup command for Azure Web App:
# python -m azure_devops_mcp --authentication pat --mode http --host 0.0.0.0 --port 8000

# Client requests must include PAT token in header:
# X-Azure-DevOps-PAT: your-personal-access-token

# Example client request:
# curl -X POST "http://your-webapp.azurewebsites.net/call" \
#   -H "Content-Type: application/json" \
#   -H "X-Azure-DevOps-PAT: your-personal-access-token" \
#   -d '{"method": "tools/call", "params": {"name": "test_connection", "arguments": {}}}'

# The server will automatically:
# 1. Read organization name from AZURE_DEVOPS_ORG environment variable
# 2. Require PAT authentication via X-Azure-DevOps-PAT header for each request
# 3. Start HTTP server accessible from external connections
# 4. Enable all domains by default

# Alternative with specific domains:
# python -m azure_devops_mcp --authentication pat --mode http --host 0.0.0.0 --port 8000 --domains repositories work-items pipelines