"""Core tools for Azure DevOps MCP server."""

import json
from typing import Any, Callable, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent

from azure.devops.connection import Connection
from azure.devops.v7_1.core import CoreClient
from msrest.authentication import BasicAuthentication


# Tool names
CORE_TOOLS = {
    "list_project_teams": "core_list_project_teams",
    "list_projects": "core_list_projects", 
    "get_identity_ids": "core_get_identity_ids",
}


def filter_projects_by_name(projects: List[Dict[str, Any]], project_name_filter: str) -> List[Dict[str, Any]]:
    """Filter projects by name using case-insensitive partial match.
    
    Args:
        projects: List of project dictionaries
        project_name_filter: Name filter string
        
    Returns:
        Filtered list of projects
    """
    lower_filter = project_name_filter.lower()
    return [
        project for project in projects 
        if project.get("name", "").lower().find(lower_filter) >= 0
    ]


async def get_azure_devops_client(token: str, org_url: str) -> Connection:
    """Get Azure DevOps client connection.
    
    Args:
        token: Access token
        org_url: Organization URL
        
    Returns:
        Azure DevOps connection
    """
    credentials = BasicAuthentication("", token)
    return Connection(base_url=org_url, creds=credentials)


def configure_core_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure core tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def core_list_project_teams(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve a list of teams for the specified Azure DevOps project."""
        try:
            project = arguments.get("project")
            mine = arguments.get("mine", False)
            top = arguments.get("top", 100)
            skip = arguments.get("skip", 0)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            token = await token_provider()
            connection = await get_azure_devops_client(token, org_url)
            core_client: CoreClient = connection.clients.get_core_client()
            
            teams = await core_client.get_teams(
                project_id=project,
                mine=mine,
                top=top,
                skip=skip
            )
            
            if not teams:
                return [TextContent(
                    type="text",
                    text="No teams found"
                )]
            
            # Convert teams to serializable format
            teams_data = [
                {
                    "id": team.id,
                    "name": team.name,
                    "description": team.description,
                    "url": team.url,
                    "project_name": team.project_name,
                    "project_id": team.project_id
                }
                for team in teams
            ]
            
            return [TextContent(
                type="text",
                text=json.dumps(teams_data, indent=2)
            )]
            
        except Exception as e:
            error_message = str(e)
            return [TextContent(
                type="text", 
                text=f"Error fetching project teams: {error_message}"
            )]
    
    @server.call_tool()
    async def core_list_projects(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve a list of projects in your Azure DevOps organization."""
        try:
            state_filter = arguments.get("stateFilter", "wellFormed")
            top = arguments.get("top", 100)
            skip = arguments.get("skip", 0)
            continuation_token = arguments.get("continuationToken")
            project_name_filter = arguments.get("projectNameFilter")
            
            token = await token_provider()
            connection = await get_azure_devops_client(token, org_url)
            core_client: CoreClient = connection.clients.get_core_client()
            
            projects = await core_client.get_projects(
                state_filter=state_filter,
                top=top,
                skip=skip,
                continuation_token=continuation_token
            )
            
            if not projects:
                return [TextContent(
                    type="text",
                    text="No projects found"
                )]
            
            # Convert projects to serializable format
            projects_data = [
                {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "url": project.url,
                    "state": project.state,
                    "revision": project.revision,
                    "visibility": project.visibility,
                    "last_update_time": project.last_update_time.isoformat() if project.last_update_time else None
                }
                for project in projects
            ]
            
            # Apply name filter if provided
            if project_name_filter:
                projects_data = filter_projects_by_name(projects_data, project_name_filter)
            
            return [TextContent(
                type="text",
                text=json.dumps(projects_data, indent=2)
            )]
            
        except Exception as e:
            error_message = str(e)
            return [TextContent(
                type="text",
                text=f"Error fetching projects: {error_message}"
            )]
    
    @server.call_tool()
    async def core_get_identity_ids(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve Azure DevOps identity IDs for a provided search filter."""
        try:
            search_filter = arguments.get("searchFilter")
            
            if not search_filter:
                return [TextContent(
                    type="text",
                    text="Error: searchFilter parameter is required"
                )]
            
            # TODO: Implement identity search using Azure DevOps API
            # This would require using the Identities API client
            # For now, return a placeholder message
            return [TextContent(
                type="text",
                text="Identity search functionality not yet implemented in Python version"
            )]
            
        except Exception as e:
            error_message = str(e)
            return [TextContent(
                type="text",
                text=f"Error fetching identities: {error_message}"
            )]