#!/usr/bin/env python3
"""
IDE DevOps MCP - HTTP Server Example

This script demonstrates how to run the IDE DevOps MCP server in HTTP mode.
"""

from azure_devops_mcp.main import run_server

def main():
    """Run the server in HTTP mode for testing."""
    print("Starting IDE DevOps MCP Server in HTTP mode...")
    print("This will start a web server that exposes MCP tools via HTTP endpoints.")
    print("Press Ctrl+C to stop the server.")
    print()
    
    try:
        # Run server in HTTP mode
        run_server(
            organization="myorg",           # Replace with your Azure DevOps organization
            domains=["all"],               # Enable all tool domains
            authentication="interactive",   # Use interactive authentication
            tenant=None,                   # Auto-detect tenant
            mode="http",                   # HTTP mode instead of stdio
            host="127.0.0.1",             # Local host
            port=8000                      # Port 8000
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user.")

if __name__ == "__main__":
    main()