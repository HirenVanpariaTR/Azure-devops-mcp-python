"""Pipelines tools for Azure DevOps MCP server."""

import json
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

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


def configure_pipeline_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure pipeline tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def pipelines_get_build_definitions(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieves a list of build definitions for a given project."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            repository_type = arguments.get("repositoryType")
            name = arguments.get("name")
            path = arguments.get("path")
            top = arguments.get("top")
            continuation_token = arguments.get("continuationToken")
            definition_ids = arguments.get("definitionIds")
            include_latest_builds = arguments.get("includeLatestBuilds")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            build_client = connection.clients.get_build_client()
            
            # Get build definitions
            definitions = build_client.get_definitions(
                project=project,
                name=name,
                repository_id=repository_id,
                repository_type=repository_type,
                top=top,
                continuation_token=continuation_token,
                definition_ids=definition_ids,
                path=path,
                include_latest_builds=include_latest_builds
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([def_.__dict__ if hasattr(def_, '__dict__') else str(def_) for def_ in definitions], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching build definitions: {str(e)}"
            )]
    
    @server.call_tool()
    async def pipelines_get_builds(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieves builds for a project."""
        try:
            project = arguments.get("project")
            definitions = arguments.get("definitions")
            queues = arguments.get("queues")
            build_number = arguments.get("buildNumber")
            min_time = arguments.get("minTime")
            max_time = arguments.get("maxTime")
            requested_for = arguments.get("requestedFor")
            reason_filter = arguments.get("reasonFilter")
            status_filter = arguments.get("statusFilter")
            result_filter = arguments.get("resultFilter")
            tag_filters = arguments.get("tagFilters")
            properties = arguments.get("properties")
            top = arguments.get("top", 50)
            continuation_token = arguments.get("continuationToken")
            max_builds_per_definition = arguments.get("maxBuildsPerDefinition")
            deleted_filter = arguments.get("deletedFilter")
            query_order = arguments.get("queryOrder")
            branch_name = arguments.get("branchName")
            build_ids = arguments.get("buildIds")
            repository_id = arguments.get("repositoryId")
            repository_type = arguments.get("repositoryType")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            build_client = connection.clients.get_build_client()
            
            # Convert datetime strings if provided
            min_finish_time = None
            max_finish_time = None
            if min_time:
                try:
                    min_finish_time = datetime.fromisoformat(min_time.replace('Z', '+00:00'))
                except:
                    pass
            if max_time:
                try:
                    max_finish_time = datetime.fromisoformat(max_time.replace('Z', '+00:00'))
                except:
                    pass
            
            # Get builds
            builds = build_client.get_builds(
                project=project,
                definitions=definitions,
                queues=queues,
                build_number=build_number,
                min_finish_time=min_finish_time,
                max_finish_time=max_finish_time,
                requested_for=requested_for,
                reason_filter=reason_filter,
                status_filter=status_filter,
                result_filter=result_filter,
                tag_filters=tag_filters,
                properties=properties,
                top=top,
                continuation_token=continuation_token,
                max_builds_per_definition=max_builds_per_definition,
                deleted_filter=deleted_filter,
                query_order=query_order,
                branch_name=branch_name,
                build_ids=build_ids,
                repository_id=repository_id,
                repository_type=repository_type
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([build.__dict__ if hasattr(build, '__dict__') else str(build) for build in builds], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching builds: {str(e)}"
            )]
    
    @server.call_tool()
    async def pipelines_get_build_changes(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieves the changes associated with a build."""
        try:
            project = arguments.get("project")
            build_id = arguments.get("buildId")
            continuation_token = arguments.get("continuationToken")
            top = arguments.get("top", 50)
            include_source_change = arguments.get("includeSourceChange", True)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            if not build_id:
                return [TextContent(
                    type="text",
                    text="Error: buildId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            build_client = connection.clients.get_build_client()
            
            # Get build changes
            changes = build_client.get_build_changes(
                project=project,
                build_id=build_id,
                continuation_token=continuation_token,
                top=top,
                include_source_change=include_source_change
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([change.__dict__ if hasattr(change, '__dict__') else str(change) for change in changes], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching build changes: {str(e)}"
            )]
    
    @server.call_tool()
    async def pipelines_get_build_log(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets the logs for a build."""
        try:
            project = arguments.get("project")
            build_id = arguments.get("buildId")
            log_id = arguments.get("logId")
            start_line = arguments.get("startLine")
            end_line = arguments.get("endLine")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            if not build_id:
                return [TextContent(
                    type="text",
                    text="Error: buildId parameter is required"
                )]
                
            if not log_id:
                return [TextContent(
                    type="text",
                    text="Error: logId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            build_client = connection.clients.get_build_client()
            
            # Get build log
            log = build_client.get_build_log(
                project=project,
                build_id=build_id,
                log_id=log_id,
                start_line=start_line,
                end_line=end_line
            )
            
            return [TextContent(
                type="text",
                text=str(log) if log else "No log content found"
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching build log: {str(e)}"
            )]
    
    @server.call_tool()
    async def pipelines_get_build_status(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets a build by ID."""
        try:
            project = arguments.get("project")
            build_id = arguments.get("buildId")
            property_filters = arguments.get("propertyFilters")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            if not build_id:
                return [TextContent(
                    type="text",
                    text="Error: buildId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            build_client = connection.clients.get_build_client()
            
            # Get build
            build = build_client.get_build(
                project=project,
                build_id=build_id,
                property_filters=property_filters
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(build.__dict__ if hasattr(build, '__dict__') else str(build), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching build status: {str(e)}"
            )]
    
    @server.call_tool()
    async def pipelines_run_pipeline(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Runs a pipeline."""
        try:
            project = arguments.get("project")
            pipeline_id = arguments.get("pipelineId")
            branch_name = arguments.get("branchName")
            parameters = arguments.get("parameters", {})
            resources = arguments.get("resources", {})
            staging_review_id = arguments.get("stagingReviewId")
            variables = arguments.get("variables", {})
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            if not pipeline_id:
                return [TextContent(
                    type="text",
                    text="Error: pipelineId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            # This would require the pipelines client
            # For now, return a placeholder response
            result = {
                "message": "Pipeline run initiated",
                "project": project,
                "pipelineId": pipeline_id,
                "branchName": branch_name,
                "parameters": parameters,
                "resources": resources,
                "variables": variables,
                "note": "Full pipeline run implementation requires additional Azure DevOps SDK configuration"
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error running pipeline: {str(e)}"
            )]