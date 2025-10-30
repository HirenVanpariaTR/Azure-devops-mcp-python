"""Work items tools for Azure DevOps MCP server."""

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


def get_link_type_from_name(name: str) -> str:
    """Convert link name to Azure DevOps link type."""
    link_types = {
        "parent": "System.LinkTypes.Hierarchy-Reverse",
        "child": "System.LinkTypes.Hierarchy-Forward",
        "duplicate": "System.LinkTypes.Duplicate-Forward",
        "duplicate of": "System.LinkTypes.Duplicate-Reverse",
        "related": "System.LinkTypes.Related",
        "successor": "System.LinkTypes.Dependency-Forward",
        "predecessor": "System.LinkTypes.Dependency-Reverse",
        "tested by": "Microsoft.VSTS.Common.TestedBy-Forward",
        "tests": "Microsoft.VSTS.Common.TestedBy-Reverse",
        "affects": "Microsoft.VSTS.Common.Affects-Forward",
        "affected by": "Microsoft.VSTS.Common.Affects-Reverse",
        "artifact": "ArtifactLink"
    }
    return link_types.get(name.lower(), name)


def configure_work_item_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure work item tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def wit_list_backlogs(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve a list of backlogs for a given project and team."""
        try:
            project = arguments.get("project")
            team = arguments.get("team")
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not team:
                return [TextContent(type="text", text="Error: team parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                work_client = connection.clients.get_work_client()
                team_context = {"project": project, "team": team}
                backlogs = work_client.get_backlogs(team_context)
                
                return [TextContent(
                    type="text",
                    text=json.dumps([backlog.__dict__ if hasattr(backlog, '__dict__') else str(backlog) for backlog in backlogs], indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Backlogs listing requested",
                        "project": project,
                        "team": team,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing backlogs: {str(e)}")]
    
    @server.call_tool()
    async def wit_my_work_items(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve my work items."""
        try:
            project = arguments.get("project")
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Query for work items assigned to me
                wiql = "SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.AssignedTo] = @Me"
                if project:
                    wiql += f" AND [System.TeamProject] = '{project}'"
                
                query_result = wit_client.query_by_wiql({"query": wiql})
                
                if query_result.work_items:
                    work_item_ids = [wi.id for wi in query_result.work_items]
                    work_items = wit_client.get_work_items(work_item_ids)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps([wi.__dict__ if hasattr(wi, '__dict__') else str(wi) for wi in work_items], indent=2, default=str)
                    )]
                else:
                    return [TextContent(type="text", text="No work items found")]
                    
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "My work items requested",
                        "project": project,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting my work items: {str(e)}")]
    
    @server.call_tool()
    async def wit_get_work_item(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get a single work item by ID."""
        try:
            id = arguments.get("id")
            fields = arguments.get("fields", [])
            expand = arguments.get("expand")
            
            if not id:
                return [TextContent(type="text", text="Error: id parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                work_item = wit_client.get_work_item(
                    id=id,
                    fields=fields,
                    expand=expand
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(work_item.__dict__ if hasattr(work_item, '__dict__') else str(work_item), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work item retrieval requested",
                        "id": id,
                        "fields": fields,
                        "expand": expand,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting work item: {str(e)}")]
    
    @server.call_tool()
    async def wit_create_work_item(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Create a new work item."""
        try:
            project = arguments.get("project")
            work_item_type = arguments.get("type")
            title = arguments.get("title")
            fields = arguments.get("fields", {})
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not work_item_type:
                return [TextContent(type="text", text="Error: type parameter is required")]
            if not title:
                return [TextContent(type="text", text="Error: title parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Prepare document for work item creation
                document = [
                    {"op": "add", "path": "/fields/System.Title", "value": title}
                ]
                
                # Add additional fields
                for field_name, field_value in fields.items():
                    document.append({
                        "op": "add",
                        "path": f"/fields/{field_name}",
                        "value": field_value
                    })
                
                work_item = wit_client.create_work_item(
                    document=document,
                    project=project,
                    type=work_item_type
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(work_item.__dict__ if hasattr(work_item, '__dict__') else str(work_item), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work item creation requested",
                        "project": project,
                        "type": work_item_type,
                        "title": title,
                        "fields": fields,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error creating work item: {str(e)}")]
    
    @server.call_tool()
    async def wit_update_work_item(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Update an existing work item."""
        try:
            id = arguments.get("id")
            fields = arguments.get("fields", {})
            
            if not id:
                return [TextContent(type="text", text="Error: id parameter is required")]
            if not fields:
                return [TextContent(type="text", text="Error: fields parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Prepare document for work item update
                document = []
                for field_name, field_value in fields.items():
                    document.append({
                        "op": "replace",
                        "path": f"/fields/{field_name}",
                        "value": field_value
                    })
                
                work_item = wit_client.update_work_item(
                    document=document,
                    id=id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(work_item.__dict__ if hasattr(work_item, '__dict__') else str(work_item), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work item update requested",
                        "id": id,
                        "fields": fields,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error updating work item: {str(e)}")]
    
    @server.call_tool()
    async def wit_get_work_items_batch_by_ids(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get multiple work items by their IDs."""
        try:
            ids = arguments.get("ids", [])
            fields = arguments.get("fields", [])
            expand = arguments.get("expand")
            
            if not ids:
                return [TextContent(type="text", text="Error: ids parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                work_items = wit_client.get_work_items(
                    ids=ids,
                    fields=fields,
                    expand=expand
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps([wi.__dict__ if hasattr(wi, '__dict__') else str(wi) for wi in work_items], indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work items batch retrieval requested",
                        "ids": ids,
                        "fields": fields,
                        "expand": expand,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting work items batch: {str(e)}")]
    
    @server.call_tool()
    async def wit_list_work_item_comments(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """List comments for a work item."""
        try:
            project = arguments.get("project")
            work_item_id = arguments.get("workItemId")
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not work_item_id:
                return [TextContent(type="text", text="Error: workItemId parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                comments = wit_client.get_comments(project, work_item_id)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(comments.__dict__ if hasattr(comments, '__dict__') else str(comments), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work item comments listing requested",
                        "project": project,
                        "workItemId": work_item_id,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing work item comments: {str(e)}")]
    
    @server.call_tool()
    async def wit_get_work_items_for_iteration(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get work items for a specific iteration."""
        try:
            project = arguments.get("project")
            team = arguments.get("team")
            iteration_path = arguments.get("iterationPath")
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not team:
                return [TextContent(type="text", text="Error: team parameter is required")]
            if not iteration_path:
                return [TextContent(type="text", text="Error: iterationPath parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Query for work items in the iteration
                wiql = f"SELECT [System.Id], [System.Title], [System.State] FROM WorkItems WHERE [System.IterationPath] = '{iteration_path}' AND [System.TeamProject] = '{project}'"
                
                query_result = wit_client.query_by_wiql({"query": wiql})
                
                if query_result.work_items:
                    work_item_ids = [wi.id for wi in query_result.work_items]
                    work_items = wit_client.get_work_items(work_item_ids)
                    
                    return [TextContent(
                        type="text",
                        text=json.dumps([wi.__dict__ if hasattr(wi, '__dict__') else str(wi) for wi in work_items], indent=2, default=str)
                    )]
                else:
                    return [TextContent(type="text", text="No work items found for iteration")]
                    
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work items for iteration requested",
                        "project": project,
                        "team": team,
                        "iterationPath": iteration_path,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting work items for iteration: {str(e)}")]
    
    @server.call_tool()
    async def wit_add_work_item_comment(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Add a comment to a work item."""
        try:
            project = arguments.get("project")
            work_item_id = arguments.get("workItemId")
            text = arguments.get("text")
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not work_item_id:
                return [TextContent(type="text", text="Error: workItemId parameter is required")]
            if not text:
                return [TextContent(type="text", text="Error: text parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                comment = wit_client.add_comment(
                    project=project,
                    work_item_id=work_item_id,
                    comment_create={"text": text}
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(comment.__dict__ if hasattr(comment, '__dict__') else str(comment), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work item comment addition requested",
                        "project": project,
                        "workItemId": work_item_id,
                        "text": text,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error adding work item comment: {str(e)}")]
    
    @server.call_tool()
    async def wit_work_items_link(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Link two work items together."""
        try:
            source_id = arguments.get("sourceId")
            target_id = arguments.get("targetId")
            link_type = arguments.get("linkType", "related")
            
            if not source_id:
                return [TextContent(type="text", text="Error: sourceId parameter is required")]
            if not target_id:
                return [TextContent(type="text", text="Error: targetId parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Create patch to add relationship
                patch = [{
                    "op": "add",
                    "path": "/relations/-",
                    "value": {
                        "rel": get_link_type_from_name(link_type),
                        "url": f"{org_url}/_apis/wit/workItems/{target_id}"
                    }
                }]
                
                updated_work_item = wit_client.update_work_item(
                    document=patch,
                    id=source_id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(updated_work_item.__dict__ if hasattr(updated_work_item, '__dict__') else str(updated_work_item), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work items linking requested",
                        "sourceId": source_id,
                        "targetId": target_id,
                        "linkType": link_type,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error linking work items: {str(e)}")]
    
    @server.call_tool()
    async def wit_work_item_unlink(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Remove a link between work items."""
        try:
            source_id = arguments.get("sourceId")
            target_id = arguments.get("targetId")
            link_type = arguments.get("linkType", "related")
            
            if not source_id:
                return [TextContent(type="text", text="Error: sourceId parameter is required")]
            if not target_id:
                return [TextContent(type="text", text="Error: targetId parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Get the work item to find the relation index
                work_item = wit_client.get_work_item(id=source_id, expand="relations")
                
                if hasattr(work_item, 'relations') and work_item.relations:
                    relation_index = -1
                    target_url = f"{org_url}/_apis/wit/workItems/{target_id}"
                    
                    for i, relation in enumerate(work_item.relations):
                        if relation.url == target_url and relation.rel == get_link_type_from_name(link_type):
                            relation_index = i
                            break
                    
                    if relation_index >= 0:
                        patch = [{
                            "op": "remove",
                            "path": f"/relations/{relation_index}"
                        }]
                        
                        updated_work_item = wit_client.update_work_item(
                            document=patch,
                            id=source_id
                        )
                        
                        return [TextContent(
                            type="text",
                            text=json.dumps(updated_work_item.__dict__ if hasattr(updated_work_item, '__dict__') else str(updated_work_item), indent=2, default=str)
                        )]
                    else:
                        return [TextContent(type="text", text="Link not found between the specified work items")]
                else:
                    return [TextContent(type="text", text="No relations found on the source work item")]
                    
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work items unlinking requested",
                        "sourceId": source_id,
                        "targetId": target_id,
                        "linkType": link_type,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error unlinking work items: {str(e)}")]
    
    @server.call_tool()
    async def wit_get_work_item_type(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get work item type information."""
        try:
            project = arguments.get("project")
            type_name = arguments.get("type")
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not type_name:
                return [TextContent(type="text", text="Error: type parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                work_item_type = wit_client.get_work_item_type(project, type_name)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(work_item_type.__dict__ if hasattr(work_item_type, '__dict__') else str(work_item_type), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work item type retrieval requested",
                        "project": project,
                        "type": type_name,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting work item type: {str(e)}")]
    
    @server.call_tool()
    async def wit_get_query(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get a work item query."""
        try:
            project = arguments.get("project")
            query_id = arguments.get("queryId")
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not query_id:
                return [TextContent(type="text", text="Error: queryId parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                query = wit_client.get_query(project, query_id)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(query.__dict__ if hasattr(query, '__dict__') else str(query), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Query retrieval requested",
                        "project": project,
                        "queryId": query_id,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting query: {str(e)}")]
    
    @server.call_tool()
    async def wit_get_query_results_by_id(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Get query results by query ID."""
        try:
            project = arguments.get("project")
            query_id = arguments.get("queryId")
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not query_id:
                return [TextContent(type="text", text="Error: queryId parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                query_result = wit_client.query_by_id(project, query_id)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(query_result.__dict__ if hasattr(query_result, '__dict__') else str(query_result), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Query results retrieval requested",
                        "project": project,
                        "queryId": query_id,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting query results: {str(e)}")]
    
    @server.call_tool()
    async def wit_update_work_items_batch(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Update multiple work items in batch."""
        try:
            project = arguments.get("project")
            work_items = arguments.get("workItems", [])
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not work_items:
                return [TextContent(type="text", text="Error: workItems parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Process each work item update
                results = []
                for work_item in work_items:
                    work_item_id = work_item.get("id")
                    fields = work_item.get("fields", {})
                    
                    if work_item_id and fields:
                        # Prepare document for work item update
                        document = []
                        for field_name, field_value in fields.items():
                            document.append({
                                "op": "replace",
                                "path": f"/fields/{field_name}",
                                "value": field_value
                            })
                        
                        updated_work_item = wit_client.update_work_item(
                            document=document,
                            id=work_item_id
                        )
                        
                        results.append(updated_work_item.__dict__ if hasattr(updated_work_item, '__dict__') else str(updated_work_item))
                
                return [TextContent(
                    type="text",
                    text=json.dumps(results, indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work items batch update requested",
                        "project": project,
                        "workItems": work_items,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error updating work items batch: {str(e)}")]
    
    @server.call_tool()
    async def wit_add_artifact_link(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Add an artifact link to a work item."""
        try:
            work_item_id = arguments.get("workItemId")
            artifact_uri = arguments.get("artifactUri")
            link_type = arguments.get("linkType", "ArtifactLink")
            comment = arguments.get("comment", "")
            
            if not work_item_id:
                return [TextContent(type="text", text="Error: workItemId parameter is required")]
            if not artifact_uri:
                return [TextContent(type="text", text="Error: artifactUri parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Create patch to add artifact relationship
                patch = [{
                    "op": "add",
                    "path": "/relations/-",
                    "value": {
                        "rel": link_type,
                        "url": artifact_uri,
                        "attributes": {
                            "comment": comment
                        } if comment else {}
                    }
                }]
                
                updated_work_item = wit_client.update_work_item(
                    document=patch,
                    id=work_item_id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(updated_work_item.__dict__ if hasattr(updated_work_item, '__dict__') else str(updated_work_item), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Artifact link addition requested",
                        "workItemId": work_item_id,
                        "artifactUri": artifact_uri,
                        "linkType": link_type,
                        "comment": comment,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error adding artifact link: {str(e)}")]
    
    @server.call_tool()
    async def wit_list_backlog_work_items(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve a list of work items for a given project, team, and backlog category."""
        try:
            project = arguments.get("project")
            team = arguments.get("team")
            backlog_id = arguments.get("backlogId")
            
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            if not team:
                return [TextContent(type="text", text="Error: team parameter is required")]
            if not backlog_id:
                return [TextContent(type="text", text="Error: backlogId parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                work_client = connection.clients.get_work_client()
                team_context = {"project": project, "team": team}
                work_items = work_client.get_backlog_level_work_items(team_context, backlog_id)
                
                return [TextContent(
                    type="text",
                    text=json.dumps(work_items.__dict__ if hasattr(work_items, '__dict__') else str(work_items), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Backlog work items listing requested",
                        "project": project,
                        "team": team,
                        "backlogId": backlog_id,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing backlog work items: {str(e)}")]
    
    @server.call_tool()
    async def wit_add_child_work_items(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Add child work items to a parent work item."""
        try:
            parent_id = arguments.get("parentId")
            child_ids = arguments.get("childIds", [])
            
            if not parent_id:
                return [TextContent(type="text", text="Error: parentId parameter is required")]
            if not child_ids:
                return [TextContent(type="text", text="Error: childIds parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Create patches to add child relationships
                patches = []
                for child_id in child_ids:
                    patches.append({
                        "op": "add",
                        "path": "/relations/-",
                        "value": {
                            "rel": "System.LinkTypes.Hierarchy-Forward",
                            "url": f"{org_url}/_apis/wit/workItems/{child_id}"
                        }
                    })
                
                updated_work_item = wit_client.update_work_item(
                    document=patches,
                    id=parent_id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(updated_work_item.__dict__ if hasattr(updated_work_item, '__dict__') else str(updated_work_item), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Child work items addition requested",
                        "parentId": parent_id,
                        "childIds": child_ids,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error adding child work items: {str(e)}")]
    
    @server.call_tool()
    async def wit_link_work_item_to_pull_request(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Link a work item to a pull request."""
        try:
            work_item_id = arguments.get("workItemId")
            pull_request_id = arguments.get("pullRequestId")
            repository_id = arguments.get("repositoryId")
            project = arguments.get("project")
            
            if not work_item_id:
                return [TextContent(type="text", text="Error: workItemId parameter is required")]
            if not pull_request_id:
                return [TextContent(type="text", text="Error: pullRequestId parameter is required")]
            if not repository_id:
                return [TextContent(type="text", text="Error: repositoryId parameter is required")]
            if not project:
                return [TextContent(type="text", text="Error: project parameter is required")]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                wit_client = connection.clients.get_work_item_tracking_client()
                
                # Create patch to add pull request relationship
                patch = [{
                    "op": "add",
                    "path": "/relations/-",
                    "value": {
                        "rel": "ArtifactLink",
                        "url": f"vstfs:///Git/PullRequestId/{project}%2F{repository_id}%2F{pull_request_id}",
                        "attributes": {
                            "name": "Pull Request"
                        }
                    }
                }]
                
                updated_work_item = wit_client.update_work_item(
                    document=patch,
                    id=work_item_id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(updated_work_item.__dict__ if hasattr(updated_work_item, '__dict__') else str(updated_work_item), indent=2, default=str)
                )]
            except AttributeError:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Work item to pull request link requested",
                        "workItemId": work_item_id,
                        "pullRequestId": pull_request_id,
                        "repositoryId": repository_id,
                        "project": project,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error linking work item to pull request: {str(e)}")]