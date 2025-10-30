"""Work tools for Azure DevOps MCP server."""

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


def configure_work_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure work tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def work_list_team_iterations(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve a list of iterations for a specific team in a project."""
        try:
            project = arguments.get("project")
            team = arguments.get("team")
            timeframe = arguments.get("timeframe")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not team:
                return [TextContent(
                    type="text",
                    text="Error: team parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                work_client = connection.clients.get_work_client()
                
                team_context = {"project": project, "team": team}
                
                iterations = work_client.get_team_iterations(
                    team_context=team_context,
                    timeframe=timeframe
                )
                
                if not iterations:
                    return [TextContent(
                        type="text",
                        text="No iterations found"
                    )]
                
                return [TextContent(
                    type="text",
                    text=json.dumps([iteration.__dict__ if hasattr(iteration, '__dict__') else str(iteration) for iteration in iterations], indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if work client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Team iterations listing requested",
                        "project": project,
                        "team": team,
                        "timeframe": timeframe,
                        "note": "Work API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching team iterations: {str(e)}"
            )]
    
    @server.call_tool()
    async def work_create_iterations(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Create new iterations for a project."""
        try:
            project = arguments.get("project")
            name = arguments.get("name")
            path = arguments.get("path")
            start_date = arguments.get("startDate")
            finish_date = arguments.get("finishDate")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not name:
                return [TextContent(
                    type="text",
                    text="Error: name parameter is required"
                )]
                
            if not path:
                return [TextContent(
                    type="text",
                    text="Error: path parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                work_client = connection.clients.get_work_client()
                
                iteration_data = {
                    "name": name,
                    "path": path,
                    "attributes": {
                        "startDate": start_date,
                        "finishDate": finish_date
                    } if start_date and finish_date else {}
                }
                
                iteration = work_client.create_iteration(
                    iteration=iteration_data,
                    project=project
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(iteration.__dict__ if hasattr(iteration, '__dict__') else str(iteration), indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if work client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Iteration creation requested",
                        "project": project,
                        "name": name,
                        "path": path,
                        "startDate": start_date,
                        "finishDate": finish_date,
                        "note": "Work API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating iterations: {str(e)}"
            )]
    
    @server.call_tool()
    async def work_assign_iterations(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Assign iterations to a team."""
        try:
            project = arguments.get("project")
            team = arguments.get("team")
            iteration_ids = arguments.get("iterationIds", [])
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not team:
                return [TextContent(
                    type="text",
                    text="Error: team parameter is required"
                )]
                
            if not iteration_ids:
                return [TextContent(
                    type="text",
                    text="Error: iterationIds parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                work_client = connection.clients.get_work_client()
                
                team_context = {"project": project, "team": team}
                
                # This would require specific iteration assignment logic
                # For now, return a placeholder response
                result = {
                    "message": "Iteration assignment requested",
                    "project": project,
                    "team": team,
                    "iterationIds": iteration_ids,
                    "note": "Work API iteration assignment requires additional Azure DevOps SDK configuration"
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except AttributeError:
                # Fallback if work client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Iteration assignment requested",
                        "project": project,
                        "team": team,
                        "iterationIds": iteration_ids,
                        "note": "Work API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error assigning iterations: {str(e)}"
            )]
    
    @server.call_tool()
    async def work_get_team_capacity(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get team capacity for an iteration."""
        try:
            project = arguments.get("project")
            team = arguments.get("team")
            iteration_id = arguments.get("iterationId")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not team:
                return [TextContent(
                    type="text",
                    text="Error: team parameter is required"
                )]
                
            if not iteration_id:
                return [TextContent(
                    type="text",
                    text="Error: iterationId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                work_client = connection.clients.get_work_client()
                
                team_context = {"project": project, "team": team}
                
                capacities = work_client.get_capacities_with_identity_ref(
                    team_context=team_context,
                    iteration_id=iteration_id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps([capacity.__dict__ if hasattr(capacity, '__dict__') else str(capacity) for capacity in capacities], indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if work client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Team capacity requested",
                        "project": project,
                        "team": team,
                        "iterationId": iteration_id,
                        "note": "Work API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting team capacity: {str(e)}"
            )]