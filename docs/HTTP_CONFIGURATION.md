# HTTPS Endpoint Configuration

## Overview

The IDE DevOps MCP Server now supports HTTP/HTTPS endpoints in addition to the traditional stdio transport. This allows the server to be used as a web service.

## Usage

### HTTP Mode
```bash
python -m azure_devops_mcp myorg --mode http --port 8000
```

### HTTPS Mode
For HTTPS support, you can use a reverse proxy like nginx or run behind a load balancer with SSL termination.

Example with uvicorn SSL (requires SSL certificates):
```bash
# Note: This would require modifying the code to pass SSL parameters to uvicorn
python -m azure_devops_mcp myorg --mode http --host 0.0.0.0 --port 8443
```

## Current Implementation

The HTTP mode currently uses FastMCP with the following features:
- **Transport**: Streamable HTTP using FastMCP's `streamable_http_app()`
- **Server**: Uvicorn ASGI server
- **Tools**: Currently includes a test tool (`test_connection`)

## Available Endpoints

When running in HTTP mode, the server exposes:
- Root endpoint: `http://host:port/`
- MCP protocol endpoints for tool execution
- Tool listing and metadata endpoints

## Current Limitations

1. **Tool Configuration**: Currently only a test tool is configured for FastMCP mode
2. **Full Azure DevOps Tools**: The existing tools need to be adapted from `@server.call_tool()` to `@mcp.tool()` decorators
3. **Authentication**: HTTP mode doesn't yet integrate the full authentication flow

## Future Enhancements

1. **Complete Tool Port**: Adapt all Azure DevOps tools to work with FastMCP
2. **Authentication Integration**: Add proper Azure authentication for HTTP requests
3. **HTTPS Support**: Built-in SSL support with certificate configuration
4. **API Documentation**: Auto-generated OpenAPI/Swagger documentation
5. **Rate Limiting**: Request throttling and authentication middleware

## Development Notes

### Porting Tools to FastMCP

To port existing tools from regular MCP Server to FastMCP:

```python
# Before (regular MCP Server)
@server.call_tool()
async def my_tool(arguments: Dict[str, Any]) -> List[TextContent]:
    # implementation
    pass

# After (FastMCP)
@mcp.tool()
async def my_tool(param1: str, param2: int = 10) -> str:
    """Tool description."""
    # implementation
    return result
```

### Key Differences

1. **Decorator**: `@server.call_tool()` → `@mcp.tool()`
2. **Parameters**: Function parameters instead of `arguments` dict
3. **Type Hints**: Direct parameter typing instead of parsing from dict
4. **Return Types**: Simpler return types instead of `List[TextContent]`

## Testing

Test the HTTP server:
```bash
# Start server
python -m azure_devops_mcp myorg --mode http --port 8000

# Test in another terminal
curl http://localhost:8000/
```

Test with the example script:
```bash
python examples/http_server_example.py
```