"""Wiki tools for Azure DevOps MCP server."""

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


def configure_wiki_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure wiki tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def wiki_get_wiki(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get the wiki by wikiIdentifier."""
        try:
            wiki_identifier = arguments.get("wikiIdentifier")
            project = arguments.get("project")
            
            if not wiki_identifier:
                return [TextContent(
                    type="text",
                    text="Error: wikiIdentifier parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wiki_client = connection.clients.get_wiki_client()
                
                wiki = wiki_client.get_wiki(
                    wiki_identifier=wiki_identifier,
                    project=project
                )
                
                if not wiki:
                    return [TextContent(
                        type="text",
                        text="No wiki found"
                    )]
                
                return [TextContent(
                    type="text",
                    text=json.dumps(wiki.__dict__ if hasattr(wiki, '__dict__') else str(wiki), indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if wiki client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Wiki retrieval requested",
                        "wikiIdentifier": wiki_identifier,
                        "project": project,
                        "note": "Wiki API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching wiki: {str(e)}"
            )]
    
    @server.call_tool()
    async def wiki_list_wikis(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """List all wikis in a project."""
        try:
            project = arguments.get("project")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wiki_client = connection.clients.get_wiki_client()
                
                wikis = wiki_client.get_all_wikis(project=project)
                
                return [TextContent(
                    type="text",
                    text=json.dumps([wiki.__dict__ if hasattr(wiki, '__dict__') else str(wiki) for wiki in wikis], indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if wiki client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Wikis listing requested",
                        "project": project,
                        "note": "Wiki API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing wikis: {str(e)}"
            )]
    
    @server.call_tool()
    async def wiki_list_pages(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """List all pages in a wiki."""
        try:
            project = arguments.get("project")
            wiki_identifier = arguments.get("wikiIdentifier")
            version_descriptor = arguments.get("versionDescriptor")
            recursion_level = arguments.get("recursionLevel", "full")
            include_content = arguments.get("includeContent", False)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not wiki_identifier:
                return [TextContent(
                    type="text",
                    text="Error: wikiIdentifier parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wiki_client = connection.clients.get_wiki_client()
                
                pages = wiki_client.get_page_tree(
                    project=project,
                    wiki_identifier=wiki_identifier,
                    version_descriptor=version_descriptor,
                    recursion_level=recursion_level,
                    include_content=include_content
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps([page.__dict__ if hasattr(page, '__dict__') else str(page) for page in pages], indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if wiki client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Wiki pages listing requested",
                        "project": project,
                        "wikiIdentifier": wiki_identifier,
                        "recursionLevel": recursion_level,
                        "includeContent": include_content,
                        "note": "Wiki API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing wiki pages: {str(e)}"
            )]
    
    @server.call_tool()
    async def wiki_get_page(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get wiki page metadata."""
        try:
            project = arguments.get("project")
            wiki_identifier = arguments.get("wikiIdentifier")
            page_path = arguments.get("pagePath")
            version_descriptor = arguments.get("versionDescriptor")
            recursion_level = arguments.get("recursionLevel", "none")
            include_content = arguments.get("includeContent", False)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not wiki_identifier:
                return [TextContent(
                    type="text",
                    text="Error: wikiIdentifier parameter is required"
                )]
                
            if not page_path:
                return [TextContent(
                    type="text",
                    text="Error: pagePath parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wiki_client = connection.clients.get_wiki_client()
                
                page = wiki_client.get_page(
                    project=project,
                    wiki_identifier=wiki_identifier,
                    path=page_path,
                    version_descriptor=version_descriptor,
                    recursion_level=recursion_level,
                    include_content=include_content
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(page.__dict__ if hasattr(page, '__dict__') else str(page), indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if wiki client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Wiki page metadata requested",
                        "project": project,
                        "wikiIdentifier": wiki_identifier,
                        "pagePath": page_path,
                        "recursionLevel": recursion_level,
                        "includeContent": include_content,
                        "note": "Wiki API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting wiki page: {str(e)}"
            )]
    
    @server.call_tool()
    async def wiki_get_page_content(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get wiki page content."""
        try:
            project = arguments.get("project")
            wiki_identifier = arguments.get("wikiIdentifier")
            page_path = arguments.get("pagePath")
            version_descriptor = arguments.get("versionDescriptor")
            include_content = arguments.get("includeContent", True)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not wiki_identifier:
                return [TextContent(
                    type="text",
                    text="Error: wikiIdentifier parameter is required"
                )]
                
            if not page_path:
                return [TextContent(
                    type="text",
                    text="Error: pagePath parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wiki_client = connection.clients.get_wiki_client()
                
                # Get page with content
                page = wiki_client.get_page(
                    project=project,
                    wiki_identifier=wiki_identifier,
                    path=page_path,
                    version_descriptor=version_descriptor,
                    include_content=include_content
                )
                
                # Extract content if available
                content = ""
                if hasattr(page, 'content'):
                    content = page.content
                elif hasattr(page, '__dict__') and 'content' in page.__dict__:
                    content = page.__dict__['content']
                
                result = {
                    "pagePath": page_path,
                    "content": content,
                    "metadata": page.__dict__ if hasattr(page, '__dict__') else str(page)
                }
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if wiki client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Wiki page content requested",
                        "project": project,
                        "wikiIdentifier": wiki_identifier,
                        "pagePath": page_path,
                        "includeContent": include_content,
                        "note": "Wiki API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error getting wiki page content: {str(e)}"
            )]
    
    @server.call_tool()
    async def wiki_create_or_update_page(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Create or update a wiki page."""
        try:
            project = arguments.get("project")
            wiki_identifier = arguments.get("wikiIdentifier")
            page_path = arguments.get("pagePath")
            content = arguments.get("content")
            comment = arguments.get("comment", "Updated via MCP")
            version_descriptor = arguments.get("versionDescriptor")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not wiki_identifier:
                return [TextContent(
                    type="text",
                    text="Error: wikiIdentifier parameter is required"
                )]
                
            if not page_path:
                return [TextContent(
                    type="text",
                    text="Error: pagePath parameter is required"
                )]
                
            if not content:
                return [TextContent(
                    type="text",
                    text="Error: content parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wiki_client = connection.clients.get_wiki_client()
                
                # Create page parameters
                page_parameters = {
                    "content": content
                }
                
                page = wiki_client.create_or_update_page(
                    parameters=page_parameters,
                    project=project,
                    wiki_identifier=wiki_identifier,
                    path=page_path,
                    version_descriptor=version_descriptor,
                    comment=comment
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(page.__dict__ if hasattr(page, '__dict__') else str(page), indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if wiki client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Wiki page create/update requested",
                        "project": project,
                        "wikiIdentifier": wiki_identifier,
                        "pagePath": page_path,
                        "content": content[:200] + "..." if len(content) > 200 else content,
                        "comment": comment,
                        "note": "Wiki API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating/updating wiki page: {str(e)}"
            )]