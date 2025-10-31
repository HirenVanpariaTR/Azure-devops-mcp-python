#!/usr/bin/env python3
"""
Simplified Azure Web App Startup Script with Better Error Handling
"""

import os
import sys
import subprocess
import traceback

def log(message):
    """Simple logging function"""
    print(f"[STARTUP] {message}")
    sys.stdout.flush()

def main():
    """Main startup function"""
    log("=== Azure DevOps MCP - Python Startup (Simplified) ===")
    log(f"Python version: {sys.version}")
    log(f"Current working directory: {os.getcwd()}")
    
    # Get environment variables
    org = os.getenv("AZURE_DEVOPS_ORG")
    port = os.getenv("PORT", "8000")
    
    if not org:
        log("ERROR: AZURE_DEVOPS_ORG environment variable is required")
        sys.exit(1)
    
    log(f"Organization: {org}")
    log(f"Port: {port}")
    log(f"Authentication: PAT via X-Azure-DevOps-PAT header")
    
    # Try to import required modules first
    try:
        log("Testing imports...")
        import mcp
        log(f"MCP version: {mcp.__version__}")
        
        import uvicorn
        log("uvicorn imported successfully")
        
        from azure_devops_mcp.main import main as mcp_main
        log("Azure DevOps MCP module imported successfully")
        
    except Exception as e:
        log(f"CRITICAL ERROR: Failed to import required modules: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
    
    # Start the server
    try:
        log("Starting MCP server...")
        
        # Set up sys.argv for the MCP main function
        sys.argv = [
            "main.py",
            org,
            "--authentication", "pat",
            "--mode", "http", 
            "--host", "0.0.0.0",
            "--port", port,
            "--domains", "all"
        ]
        
        log("Calling MCP main function...")
        mcp_main()
        
    except Exception as e:
        log(f"CRITICAL ERROR: Failed to start server: {e}")
        log(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()