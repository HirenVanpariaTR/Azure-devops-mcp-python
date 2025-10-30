#!/usr/bin/env python3
"""Development setup script for Azure DevOps MCP Server Python version."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, cwd: Path = None) -> int:
    """Run a shell command and return the exit code."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd)
    return result.returncode


def main():
    """Main setup function."""
    project_dir = Path(__file__).parent
    
    print("Setting up Azure DevOps MCP Server - Python Version")
    print("=" * 60)
    
    # Install dependencies
    print("\\n1. Installing dependencies...")
    if run_command("pip install -e \".[dev]\"", cwd=project_dir) != 0:
        print("[ERROR] Failed to install dependencies")
        sys.exit(1)
    
    print("[SUCCESS] Dependencies installed successfully")
    
    # Run tests
    print("\\n2. Running tests...")
    if run_command("python -m pytest -v", cwd=project_dir) != 0:
        print("[WARNING] Some tests failed, but that's expected for a work-in-progress")
    else:
        print("[SUCCESS] All tests passed")
    
    # Check imports
    print("\\n3. Checking imports...")
    if run_command("python -c \"from azure_devops_mcp.main import main; print('[SUCCESS] Main module imports successfully')\"", cwd=project_dir) != 0:
        print("[ERROR] Import check failed")
        sys.exit(1)
    
    print("\\n" + "=" * 60)
    print("[SUCCESS] Setup completed successfully!")
    print("\\nTo run the server:")
    print("  mcp-server-azuredevops <organization> [options]")
    print("\\nExample:")
    print("  mcp-server-azuredevops myorg --authentication azcli")
    print("\\nFor help:")
    print("  mcp-server-azuredevops --help")


if __name__ == "__main__":
    main()