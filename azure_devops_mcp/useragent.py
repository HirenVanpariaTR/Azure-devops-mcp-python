"""User agent composition for Azure DevOps MCP server."""

from typing import Optional


class McpClientInfo:
    """MCP client information."""
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version


class UserAgentComposer:
    """Composes user agent string for HTTP requests."""
    
    def __init__(self, package_version: str):
        """Initialize user agent composer.
        
        Args:
            package_version: Version of the MCP server package
        """
        self._user_agent = f"AzureDevOps.MCP/{package_version} (python)"
        self._mcp_client_info_appended = False
    
    @property
    def user_agent(self) -> str:
        """Get current user agent string."""
        return self._user_agent
    
    def append_mcp_client_info(self, info: Optional[McpClientInfo]) -> None:
        """Append MCP client info to user agent.
        
        Args:
            info: MCP client information to append
        """
        if (not self._mcp_client_info_appended and 
            info and info.name and info.version):
            self._user_agent += f" {info.name}/{info.version}"
            self._mcp_client_info_appended = True