#!/usr/bin/env python3
"""
Azure Web App Python Startup Script
Alternative to startup.sh for more reliable startup in Azure environments
"""

import os
import sys
import subprocess
import importlib.util

def log(message):
    """Simple logging function"""
    print(f"[STARTUP] {message}")

def install_dependencies():
    """Install Python dependencies"""
    log("Installing Python dependencies...")
    
    try:
        # Upgrade pip first
        log("Upgrading pip...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        log("Installing requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--verbose"])
        
        return True
    except subprocess.CalledProcessError as e:
        log(f"ERROR: Failed to install dependencies: {e}")
        return False

def verify_mcp_installation():
    """Verify that MCP can be imported"""
    log("Verifying MCP installation...")
    
    try:
        # Try to import mcp.server
        spec = importlib.util.find_spec("mcp.server")
        if spec is None:
            log("ERROR: mcp.server module not found")
            return False
            
        # Actually import it
        import mcp.server
        log("MCP server module imported successfully")
        return True
        
    except ImportError as e:
        log(f"ERROR: Failed to import MCP: {e}")
        
        # Try reinstalling
        log("Attempting to reinstall MCP...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp", "--force-reinstall"])
            import mcp.server
            log("MCP server module imported successfully after reinstall")
            return True
        except Exception as e2:
            log(f"CRITICAL ERROR: Cannot import MCP module even after reinstall: {e2}")
            return False

def start_server():
    """Start the Azure DevOps MCP server"""
    log("Starting Azure DevOps MCP server...")
    
    # Get environment variables
    org = os.getenv("AZURE_DEVOPS_ORG")
    port = os.getenv("PORT", "8000")
    
    if not org:
        log("ERROR: AZURE_DEVOPS_ORG environment variable is required")
        sys.exit(1)
    
    log(f"Organization: {org}")
    log(f"Port: {port}")
    log(f"Authentication: PAT via X-Azure-DevOps-PAT header")
    
    # Start the server
    try:
        from azure_devops_mcp.main import main
        
        # Call the main function with arguments
        sys.argv = [
            "main.py",
            org,
            "--authentication", "pat",
            "--mode", "http", 
            "--host", "0.0.0.0",
            "--port", port,
            "--domains", "all"
        ]
        
        log("Calling main function...")
        main()
        
    except Exception as e:
        log(f"ERROR: Failed to start server: {e}")
        import traceback
        log(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    """Main startup function"""
    log("=== Azure DevOps MCP - Python Startup ===")
    log(f"Python version: {sys.version}")
    log(f"Current working directory: {os.getcwd()}")
    log(f"Contents: {os.listdir('.')}")
    
    # Install dependencies
    if not install_dependencies():
        log("CRITICAL: Failed to install dependencies")
        sys.exit(1)
    
    # Verify MCP installation
    if not verify_mcp_installation():
        log("CRITICAL: MCP module verification failed")
        sys.exit(1)
    
    # Start the server
    start_server()

if __name__ == "__main__":
    main()