"""Advanced security tools for Azure DevOps MCP server."""

import json
from typing import Any, Callable, Dict, List, Optional

from mcp.server import Server
from mcp.types import TextContent
from azure.devops.connection import Connection


async def get_azure_devops_connection(token: str, org_url: str) -> Connection:
    """Create Azure DevOps connection.
    
    Args:
        token: Access token
        org_url: Organization URL
        
    Returns:
        Connection instance
    """
    from msrest.authentication import BasicAuthentication
    credentials = BasicAuthentication('', token)
    connection = Connection(base_url=org_url, creds=credentials)
    return connection


def configure_advsec_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure advanced security tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def advsec_get_alerts(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve Advanced Security alerts for a repository."""
        try:
            project = arguments.get("project")
            repository = arguments.get("repository")
            alert_type = arguments.get("alertType")
            states = arguments.get("states")
            severities = arguments.get("severities")
            rule_id = arguments.get("ruleId")
            rule_name = arguments.get("ruleName")
            tool_name = arguments.get("toolName")
            ref = arguments.get("ref")
            only_default_branch = arguments.get("onlyDefaultBranch", True)
            confidence_levels = arguments.get("confidenceLevels", ["high", "other"])
            validity = arguments.get("validity")
            top = arguments.get("top", 100)
            order_by = arguments.get("orderBy", "severity")
            continuation_token = arguments.get("continuationToken")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            if not repository:
                return [TextContent(
                    type="text",
                    text="Error: repository parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            # Note: Advanced Security API might not be available in all azure-devops versions
            # This is a placeholder implementation that would require additional configuration
            try:
                # Try to get advanced security alerts using REST API
                # This would need specific implementation based on available Azure DevOps SDK features
                result = {
                    "message": "Advanced Security alerts retrieval not fully implemented",
                    "project": project,
                    "repository": repository,
                    "parameters": {
                        "alertType": alert_type,
                        "states": states,
                        "severities": severities,
                        "ruleId": rule_id,
                        "ruleName": rule_name,
                        "toolName": tool_name,
                        "ref": ref,
                        "onlyDefaultBranch": only_default_branch,
                        "confidenceLevels": confidence_levels,
                        "validity": validity,
                        "top": top,
                        "orderBy": order_by
                    }
                }
            except Exception as api_error:
                result = {
                    "error": f"Advanced Security API not available: {str(api_error)}",
                    "note": "This feature requires Azure DevOps Advanced Security license"
                }
            
            return [TextContent(
                type="text",
                text=json.dumps(result.__dict__ if hasattr(result, '__dict__') else str(result), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching Advanced Security alerts: {str(e)}"
            )]
    
    @server.call_tool()
    async def advsec_get_alert_details(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get detailed information about a specific Advanced Security alert."""
        try:
            project = arguments.get("project")
            repository = arguments.get("repository") 
            alert_id = arguments.get("alertId")
            ref = arguments.get("ref")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            if not repository:
                return [TextContent(
                    type="text",
                    text="Error: repository parameter is required"
                )]
                
            if alert_id is None:
                return [TextContent(
                    type="text",
                    text="Error: alertId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            # Get alert details
            try:
                # This would need specific implementation based on available Azure DevOps SDK features
                result = {
                    "message": "Advanced Security alert details retrieval not fully implemented",
                    "project": project,
                    "repository": repository,
                    "alertId": alert_id,
                    "ref": ref,
                    "note": "This feature requires Azure DevOps Advanced Security license"
                }
            except Exception as api_error:
                result = {
                    "error": f"Advanced Security API not available: {str(api_error)}",
                    "note": "This feature requires Azure DevOps Advanced Security license"
                }
            
            return [TextContent(
                type="text",
                text=json.dumps(result.__dict__ if hasattr(result, '__dict__') else str(result), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching alert details: {str(e)}"
            )]