@echo off
REM Azure Web App Startup Script for Windows
REM This script starts the IDE DevOps MCP server in PAT authentication mode

echo === IDE DevOps MCP - Azure Web App Startup ===
echo Starting server with PAT authentication...

REM Check if required environment variables are set
if "%AZURE_DEVOPS_ORG%"=="" (
    echo ERROR: AZURE_DEVOPS_ORG environment variable is required
    exit /b 1
)

echo Organization: %AZURE_DEVOPS_ORG%
if "%PORT%"=="" set PORT=8000
echo Port: %PORT%
echo Authentication: PAT via X-Azure-DevOps-PAT header

REM Start the server
python -m azure_devops_mcp.main --authentication pat --mode http --host 0.0.0.0 --port %PORT% --domains all

echo Server startup complete!