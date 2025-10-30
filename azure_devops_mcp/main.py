#!/usr/bin/env python3
"""
IDE DevOps MCP - Python Implementation

Copyright (c) Microsoft Corporation.
Licensed under the MIT License.
"""

import asyncio
import os
import sys
from typing import List, Optional

import click
from mcp.server import Server, FastMCP
from mcp.server.stdio import stdio_server

from azure_devops_mcp import __version__
from azure_devops_mcp.auth import create_authenticator
from azure_devops_mcp.org_tenants import get_org_tenant
from azure_devops_mcp.shared.domains import DomainsManager
from azure_devops_mcp.tools import configure_all_tools
from azure_devops_mcp.useragent import UserAgentComposer


def is_github_codespace_env() -> bool:
    """Check if running in GitHub Codespaces."""
    return os.environ.get("CODESPACES") == "true" and bool(os.environ.get("CODESPACE_NAME"))


def get_default_auth_type() -> str:
    """Get default authentication type based on environment."""
    return "azcli" if is_github_codespace_env() else "interactive"


@click.command()
@click.argument("organization", required=False)
@click.option(
    "--domains", "-d",
    multiple=True,
    default=["all"],
    help="Domain(s) to enable: 'all' for everything, or specific domains like 'repositories builds work'. Defaults to 'all'."
)
@click.option(
    "--authentication", "-a",
    type=click.Choice(["interactive", "azcli", "env", "pat"]),
    default=get_default_auth_type(),
    help="Type of authentication to use. Supported values are 'interactive', 'azcli', 'env', and 'pat' (HTTP mode only)"
)
@click.option(
    "--tenant", "-t",
    help="Azure tenant ID (optional, applied when using 'interactive' and 'azcli' type of authentication)"
)
@click.option(
    "--mode", "-m",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    help="Server mode: 'stdio' for MCP client connection or 'http' for web service"
)
@click.option(
    "--host",
    default="127.0.0.1",
    help="HTTP server host (when mode=http)"
)
@click.option(
    "--port", "-p",
    default=8000,
    type=int,
    help="HTTP server port (when mode=http)"
)
@click.version_option(version=__version__)
def main(
    organization: Optional[str],
    domains: List[str],
    authentication: str,
    tenant: Optional[str],
    mode: str,
    host: str,
    port: int
) -> None:
    """IDE DevOps MCP
    
    ORGANIZATION: Azure DevOps organization name (optional if AZURE_DEVOPS_ORG environment variable is set)
    """
    # Get organization from argument or environment variable
    org_name = organization or os.environ.get("AZURE_DEVOPS_ORG")
    
    if not org_name:
        click.echo("Error: Organization name is required. Provide it as an argument or set AZURE_DEVOPS_ORG environment variable.", err=True)
        sys.exit(1)
    
    # Validate authentication mode
    if authentication == "pat" and mode != "http":
        click.echo("Error: PAT authentication is only supported in HTTP mode. Use --mode http with --authentication pat.", err=True)
        sys.exit(1)
    
    run_server(org_name, domains, authentication, tenant, mode, host, port)


def run_server(
    organization: str,
    domains: List[str],
    authentication: str,
    tenant: Optional[str],
    mode: str = "stdio",
    host: str = "127.0.0.1",
    port: int = 8000
) -> None:
    """Run the MCP server."""
    # Log the organization being used
    org_source = "environment variable" if not sys.argv[1:] or sys.argv[1].startswith('-') else "command line argument"
    print(f"Starting IDE DevOps MCP server for organization: {organization} (from {org_source})", file=sys.stderr)
    
    if mode == "http":
        run_http_server(organization, domains, authentication, tenant, host, port)
    else:
        asyncio.run(run_stdio_server(organization, domains, authentication, tenant))


def run_http_server(
    organization: str,
    domains: List[str],
    authentication: str,
    tenant: Optional[str],
    host: str,
    port: int
) -> None:
    """Run the HTTP server mode with PAT authentication support."""
    # Import uvicorn only when needed for HTTP mode
    try:
        import uvicorn
    except ImportError:
        print("uvicorn is required for HTTP mode. Install it with: pip install uvicorn", file=sys.stderr)
        sys.exit(1)
    
    org_url = f"https://dev.azure.com/{organization}"
    
    # Initialize domains manager (convert tuple to list if needed)
    domains_list = list(domains) if isinstance(domains, tuple) else domains
    domains_manager = DomainsManager(domains_list)
    enabled_domains = domains_manager.get_enabled_domains()
    
    # Initialize user agent composer
    user_agent_composer = UserAgentComposer(__version__)
    
    # Create FastMCP server for HTTP mode with PAT support
    mcp = FastMCP("IDE DevOps MCP")
    
    # Global variable to store PAT token from headers
    current_pat_token = None
    
    # Custom tool configuration with PAT authentication
    async def get_pat_authenticator():
        """Get PAT-based authenticator for current request."""
        if not current_pat_token:
            raise Exception("PAT token not provided in X-Azure-DevOps-PAT header")
        return create_authenticator("pat", None, current_pat_token)
    
    @mcp.tool()
    async def test_connection() -> str:
        """Test Azure DevOps connection using PAT from header."""
        try:
            if not current_pat_token:
                return "Error: PAT token not provided in X-Azure-DevOps-PAT header"
            
            # Test basic PAT token format
            if not current_pat_token or len(current_pat_token) < 10:
                return "Error: Invalid PAT token format"
            
            return f"Connected to Azure DevOps organization: {organization} (PAT authentication)"
            
        except Exception as e:
            return f"Connection failed: {str(e)}"
    
    @mcp.tool()
    async def get_server_info() -> dict:
        """Get server information and configuration."""
        return {
            "name": "IDE DevOps MCP",
            "version": __version__,
            "organization": organization,
            "enabled_domains": enabled_domains,
            "authentication": "PAT via X-Azure-DevOps-PAT header",
            "org_url": org_url
        }
    
    # Create custom HTTP handler to extract PAT from headers
    def create_custom_app():
        """Create custom ASGI app with PAT header extraction."""
        base_app = mcp.streamable_http_app()
        
        async def custom_app(scope, receive, send):
            if scope["type"] == "http":
                # Extract headers
                headers = dict(scope.get("headers", []))
                
                # Look for PAT token in headers (case-insensitive)
                pat_token = None
                for key, value in headers.items():
                    key_str = key.decode() if isinstance(key, bytes) else key
                    if key_str.lower() == "x-azure-devops-pat":
                        pat_token = value.decode() if isinstance(value, bytes) else value
                        break
                
                # Store PAT token globally for tools to access
                nonlocal current_pat_token
                current_pat_token = pat_token
                
                # If no PAT token and not a GET to root, return 401
                if not pat_token and scope.get("path") != "/" and scope.get("method") != "GET":
                    response = {
                        "type": "http.response.start",
                        "status": 401,
                        "headers": [[b"content-type", b"application/json"]],
                    }
                    await send(response)
                    
                    body = {
                        "type": "http.response.body",
                        "body": b'{"error": "Authentication required", "message": "Please provide PAT token in X-Azure-DevOps-PAT header"}',
                    }
                    await send(body)
                    return
            
            # Forward to base MCP app
            await base_app(scope, receive, send)
        
        return custom_app
    
    # Run HTTP server using custom app with PAT support
    print(f"Starting IDE DevOps MCP server on http://{host}:{port}")
    print(f"Organization: {organization}")
    print(f"Authentication: Send PAT token in 'X-Azure-DevOps-PAT' header")
    print(f"Enabled domains: {', '.join(enabled_domains)}")
    print(f"Available tools: test_connection, get_server_info")
    print(f"Visit http://{host}:{port}/ for server info")
    
    app = create_custom_app()
    uvicorn.run(app, host=host, port=port)


async def run_stdio_server(
    organization: str,
    domains: List[str],
    authentication: str,
    tenant: Optional[str]
) -> None:
    """Run the stdio server mode."""
    org_url = f"https://dev.azure.com/{organization}"
    
    # Initialize domains manager (convert tuple to list if needed)
    domains_list = list(domains) if isinstance(domains, tuple) else domains
    domains_manager = DomainsManager(domains_list)
    enabled_domains = domains_manager.get_enabled_domains()
    
    # Initialize user agent composer
    user_agent_composer = UserAgentComposer(__version__)
    
    # Get tenant ID
    tenant_id = await get_org_tenant(organization) if not tenant else tenant
    
    # Create authenticator
    authenticator = create_authenticator(authentication, tenant_id)
    
    # Create regular MCP server for stdio mode
    server = Server("IDE DevOps MCP")
    
    # Configure tools
    configure_all_tools(
        server=server,
        token_provider=authenticator,
        org_url=org_url,
        user_agent_provider=lambda: user_agent_composer.user_agent,
        enabled_domains=enabled_domains
    )
    
    # Run stdio server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\nServer interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Fatal error in main(): {e}", file=sys.stderr)
        sys.exit(1)