# IDE DevOps MCP - Python Version

This is a Python implementation of the IDE DevOps MCP (Model Context Protocol) server.

## Installation

```bash
pip install azure-devops-mcp
```

## Usage

The server supports two modes:
- **stdio mode**: For MCP client connections (default)
- **http mode**: For web service endpoints

```bash
python -m azure_devops_mcp [organization] [options]
```

### Organization Configuration

The organization name can be provided in two ways:
1. **Command line argument**: `python -m azure_devops_mcp myorg`
2. **Environment variable**: Set `AZURE_DEVOPS_ORG=myorg` (useful for Azure Web App deployments)

If both are provided, the command line argument takes precedence.

### Options

- `organization`: Azure DevOps organization name (optional if `AZURE_DEVOPS_ORG` environment variable is set)
- `--domains`, `-d`: Domain(s) to enable: 'all' for everything, or specific domains like 'repositories builds work'. Defaults to 'all'.
- `--authentication`, `-a`: Type of authentication to use. Supported values are 'interactive', 'azcli' and 'env' (default: 'interactive')
- `--tenant`, `-t`: Azure tenant ID (optional, applied when using 'interactive' and 'azcli' type of authentication)
- `--mode`, `-m`: Server mode: 'stdio' for MCP client connection or 'http' for web service (default: 'stdio')
- `--host`: HTTP server host (when mode=http, default: '127.0.0.1')
- `--port`, `-p`: HTTP server port (when mode=http, default: 8000)

### Examples

```bash
# Basic usage with stdio mode (for MCP clients)
python -m azure_devops_mcp myorg

# Using environment variable (great for Azure Web Apps)
export AZURE_DEVOPS_ORG=myorg  # Linux/Mac
# or
set AZURE_DEVOPS_ORG=myorg     # Windows CMD
# or  
$env:AZURE_DEVOPS_ORG="myorg"  # PowerShell
python -m azure_devops_mcp

# HTTP server mode for web service
python -m azure_devops_mcp myorg --mode http --port 8080

# Use specific domains only
python -m azure_devops_mcp myorg --domains repositories pipelines

# Use Azure CLI authentication
python -m azure_devops_mcp myorg --authentication azcli

# Environment variable authentication with HTTP mode (ideal for cloud deployments)
export AZURE_DEVOPS_ORG=myorg
python -m azure_devops_mcp --authentication env --mode http --host 0.0.0.0 --port 8000
```

### HTTP Server Mode

When running in HTTP mode, the server provides a web API for MCP tools. This is useful for:
- Web applications that need Azure DevOps integration
- Testing tools without an MCP client  
- Building custom integrations
- Azure Web App deployments

#### Traditional HTTP Mode (Environment Variables)
```bash
python -m azure_devops_mcp myorg --mode http
```

#### PAT Header Authentication (Recommended for APIs)
```bash
# Start server with PAT authentication mode
python -m azure_devops_mcp myorg --mode http --authentication pat

# Client requests must include PAT in header
curl -X POST "http://127.0.0.1:8000/mcp" \
  -H "Content-Type: application/json" \
  -H "X-Azure-DevOps-PAT: your-personal-access-token" \
  -d '{"method": "tools/call", "params": {"name": "test_connection", "arguments": {}}}'
```

Visit `http://127.0.0.1:8000/` for server info and available endpoints.

**Note**: PAT authentication (`--authentication pat`) is only available in HTTP mode and requires clients to send the PAT token in the `X-Azure-DevOps-PAT` header with each request.

## Development

### Setup

```bash
git clone https://github.com/microsoft/azure-devops-mcp.git
cd azure-devops-mcp/python-version
pip install -e ".[dev]"
```

### Testing

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check .
```

## License

MIT License - see LICENSE.md for details.