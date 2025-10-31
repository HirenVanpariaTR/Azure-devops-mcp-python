#!/usr/bin/env python3
"""
Robust MCP Server with Fallback Error Server
"""
import os
import sys
import traceback
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

# Global variables for error tracking
startup_error = None
startup_logs = []

def log(message):
    """Logging function that captures to both stdout and startup_logs"""
    full_message = f"[MCP-ROBUST] {message}"
    print(full_message, flush=True)
    startup_logs.append(full_message)

class ErrorHandler(BaseHTTPRequestHandler):
    """Fallback HTTP handler when MCP server fails to start"""
    
    def do_GET(self):
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'error': 'MCP Server startup failed',
            'startup_error': str(startup_error) if startup_error else 'Unknown error',
            'startup_logs': startup_logs,
            'traceback': traceback.format_exc() if startup_error else None
        }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        log(f"Error server: {format % args}")

def start_error_server(port):
    """Start fallback error server"""
    try:
        log(f"Starting error server on port {port}")
        server = HTTPServer(('0.0.0.0', port), ErrorHandler)
        server.serve_forever()
    except Exception as e:
        log(f"Error server failed: {e}")

def start_mcp_server():
    """Attempt to start MCP server"""
    global startup_error
    
    try:
        log("Attempting to start MCP server...")
        
        # Get environment variables
        org = os.getenv("AZURE_DEVOPS_ORG")
        port = int(os.getenv("PORT", "8000"))
        
        if not org:
            raise Exception("AZURE_DEVOPS_ORG environment variable is required")
        
        log(f"Organization: {org}")
        log(f"Port: {port}")
        
        # Import required modules
        log("Importing MCP modules...")
        from mcp.server import FastMCP
        import uvicorn
        
        log("Creating MCP server...")
        mcp = FastMCP("Azure DevOps MCP")
        
        # Simple test tools
        @mcp.tool()
        async def test_connection() -> str:
            """Test connection tool"""
            return f"Connected to Azure DevOps organization: {org}"
        
        @mcp.tool()
        async def health_check() -> dict:
            """Health check tool"""
            return {"status": "healthy", "organization": org}
        
        log("Creating ASGI app...")
        app = mcp.streamable_http_app()
        
        log(f"Starting uvicorn on 0.0.0.0:{port}")
        
        # Start uvicorn server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=True
        )
        
    except Exception as e:
        startup_error = e
        log(f"MCP server startup failed: {e}")
        log(f"Full traceback: {traceback.format_exc()}")
        raise

def main():
    """Main function with fallback error handling"""
    log("=== Azure DevOps MCP Server (Robust) ===")
    
    port = int(os.getenv("PORT", "8000"))
    
    try:
        # Try to start MCP server
        start_mcp_server()
        
    except Exception as e:
        log(f"MCP server failed to start: {e}")
        
        # Start error server as fallback
        log("Starting fallback error server...")
        start_error_server(port)

if __name__ == "__main__":
    main()