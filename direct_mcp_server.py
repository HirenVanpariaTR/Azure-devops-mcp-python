#!/usr/bin/env python3
"""
Direct MCP Server Startup for Azure Web App
"""
import os
import sys
import traceback

def log(message):
    """Simple logging function"""
    print(f"[MCP-START] {message}", flush=True)

def main():
    """Start MCP server directly with uvicorn"""
    log("=== Starting Azure DevOps MCP Server ===")
    
    # Get environment variables
    org = os.getenv("AZURE_DEVOPS_ORG")
    port = int(os.getenv("PORT", "8000"))
    
    if not org:
        log("ERROR: AZURE_DEVOPS_ORG environment variable is required")
        sys.exit(1)
    
    log(f"Organization: {org}")
    log(f"Port: {port}")
    
    try:
        # Import required modules
        from mcp.server import FastMCP
        from azure_devops_mcp.auth import create_authenticator
        from azure_devops_mcp.shared.domains import DomainsManager
        from azure_devops_mcp import __version__
        import uvicorn
        
        log("All modules imported successfully")
        
        # Initialize MCP server
        mcp = FastMCP("Azure DevOps MCP")
        
        # Set up PAT authentication
        current_pat_token = None
        
        @mcp.tool()
        async def test_connection() -> str:
            """Test Azure DevOps connection."""
            if not current_pat_token:
                return "Error: PAT token not provided in X-Azure-DevOps-PAT header"
            return f"Connected to Azure DevOps organization: {org}"
        
        @mcp.tool()
        async def get_server_info() -> dict:
            """Get server information."""
            return {
                "name": "Azure DevOps MCP",
                "version": __version__,
                "organization": org,
                "authentication": "PAT via X-Azure-DevOps-PAT header"
            }
        
        # Create ASGI app with PAT header extraction
        def create_app():
            base_app = mcp.streamable_http_app()
            
            async def app(scope, receive, send):
                nonlocal current_pat_token
                
                if scope["type"] == "http":
                    # Extract PAT token from headers
                    headers = dict(scope.get("headers", []))
                    for key, value in headers.items():
                        key_str = key.decode() if isinstance(key, bytes) else key
                        if key_str.lower() == "x-azure-devops-pat":
                            current_pat_token = value.decode() if isinstance(value, bytes) else value
                            break
                
                return await base_app(scope, receive, send)
            
            return app
        
        app = create_app()
        
        log(f"Starting uvicorn server on 0.0.0.0:{port}")
        
        # Start server with uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        log(f"CRITICAL ERROR: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()