"""Search tools for Azure DevOps MCP server."""

import json
import requests
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlparse

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


def get_org_name_from_url(org_url: str) -> str:
    """Extract organization name from URL."""
    parsed = urlparse(org_url)
    if "dev.azure.com" in parsed.netloc:
        # Format: https://dev.azure.com/orgname
        return parsed.path.strip("/")
    elif "visualstudio.com" in parsed.netloc:
        # Format: https://orgname.visualstudio.com
        return parsed.netloc.split(".")[0]
    else:
        # Fallback
        return parsed.path.strip("/").split("/")[0] if parsed.path else "unknown"


def configure_search_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure search tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def search_code(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Search Azure DevOps Repositories for a given search text."""
        try:
            search_text = arguments.get("searchText")
            project = arguments.get("project", [])
            repository = arguments.get("repository", [])
            path = arguments.get("path", [])
            branch = arguments.get("branch", [])
            include_facets = arguments.get("includeFacets", False)
            skip = arguments.get("skip", 0)
            top = arguments.get("top", 5)
            
            if not search_text:
                return [TextContent(
                    type="text",
                    text="Error: searchText parameter is required"
                )]
            
            token = token_provider()
            org_name = get_org_name_from_url(org_url)
            
            # Build search request
            url = f"https://almsearch.dev.azure.com/{org_name}/_apis/search/codesearchresults?api-version=6.0-preview.1"
            
            request_body = {
                "searchText": search_text,
                "includeFacets": include_facets,
                "$skip": skip,
                "$top": top
            }
            
            # Add filters
            filters = {}
            if project:
                filters["Project"] = project if isinstance(project, list) else [project]
            if repository:
                filters["Repository"] = repository if isinstance(repository, list) else [repository]
            if path:
                filters["Path"] = path if isinstance(path, list) else [path]
            if branch:
                filters["Branch"] = branch if isinstance(branch, list) else [branch]
            
            if filters:
                request_body["filters"] = filters
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": user_agent_provider()
            }
            
            response = requests.post(url, json=request_body, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Error searching code: HTTP {response.status_code} - {response.text}"
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching code: {str(e)}"
            )]
    
    @server.call_tool()
    async def search_wiki(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Search Azure DevOps Wiki for a given search text."""
        try:
            search_text = arguments.get("searchText")
            project = arguments.get("project", [])
            wiki_name = arguments.get("wikiName", [])
            include_facets = arguments.get("includeFacets", False)
            skip = arguments.get("skip", 0)
            top = arguments.get("top", 5)
            
            if not search_text:
                return [TextContent(
                    type="text",
                    text="Error: searchText parameter is required"
                )]
            
            token = token_provider()
            org_name = get_org_name_from_url(org_url)
            
            # Build search request
            url = f"https://almsearch.dev.azure.com/{org_name}/_apis/search/wikisearchresults?api-version=6.0-preview.1"
            
            request_body = {
                "searchText": search_text,
                "includeFacets": include_facets,
                "$skip": skip,
                "$top": top
            }
            
            # Add filters
            filters = {}
            if project:
                filters["Project"] = project if isinstance(project, list) else [project]
            if wiki_name:
                filters["WikiName"] = wiki_name if isinstance(wiki_name, list) else [wiki_name]
            
            if filters:
                request_body["filters"] = filters
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": user_agent_provider()
            }
            
            response = requests.post(url, json=request_body, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Error searching wiki: HTTP {response.status_code} - {response.text}"
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching wiki: {str(e)}"
            )]
    
    @server.call_tool()
    async def search_workitem(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get Azure DevOps Work Item search results for a given search text."""
        try:
            search_text = arguments.get("searchText")
            project = arguments.get("project", [])
            work_item_type = arguments.get("workItemType", [])
            state = arguments.get("state", [])
            assigned_to = arguments.get("assignedTo", [])
            include_facets = arguments.get("includeFacets", False)
            skip = arguments.get("skip", 0)
            top = arguments.get("top", 5)
            
            if not search_text:
                return [TextContent(
                    type="text",
                    text="Error: searchText parameter is required"
                )]
            
            token = token_provider()
            org_name = get_org_name_from_url(org_url)
            
            # Build search request
            url = f"https://almsearch.dev.azure.com/{org_name}/_apis/search/workitemsearchresults?api-version=6.0-preview.1"
            
            request_body = {
                "searchText": search_text,
                "includeFacets": include_facets,
                "$skip": skip,
                "$top": top
            }
            
            # Add filters
            filters = {}
            if project:
                filters["Project"] = project if isinstance(project, list) else [project]
            if work_item_type:
                filters["WorkItemType"] = work_item_type if isinstance(work_item_type, list) else [work_item_type]
            if state:
                filters["State"] = state if isinstance(state, list) else [state]
            if assigned_to:
                filters["AssignedTo"] = assigned_to if isinstance(assigned_to, list) else [assigned_to]
            
            if filters:
                request_body["filters"] = filters
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": user_agent_provider()
            }
            
            response = requests.post(url, json=request_body, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Error searching work items: HTTP {response.status_code} - {response.text}"
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching work items: {str(e)}"
            )]