"""Test plans tools for Azure DevOps MCP server."""

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


def configure_test_plan_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure test plan tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def testplan_list_test_plans(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieve a paginated list of test plans from an Azure DevOps project."""
        try:
            project = arguments.get("project")
            filter_active_plans = arguments.get("filterActivePlans", True)
            include_plan_details = arguments.get("includePlanDetails", False)
            continuation_token = arguments.get("continuationToken")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                test_plan_client = connection.clients.get_test_plan_client()
                
                test_plans = test_plan_client.get_test_plans(
                    project=project,
                    owner="",  # Empty string until we can figure out how to get owner id
                    continuation_token=continuation_token,
                    include_plan_details=include_plan_details,
                    filter_active_plans=filter_active_plans
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps([plan.__dict__ if hasattr(plan, '__dict__') else str(plan) for plan in test_plans], indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if test plan client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Test plan listing requested",
                        "project": project,
                        "filterActivePlans": filter_active_plans,
                        "includePlanDetails": include_plan_details,
                        "note": "Test Plan API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing test plans: {str(e)}"
            )]
    
    @server.call_tool()
    async def testplan_create_test_plan(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Creates a new test plan in the project."""
        try:
            project = arguments.get("project")
            name = arguments.get("name")
            iteration = arguments.get("iteration")
            description = arguments.get("description", "")
            
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
                
            if not iteration:
                return [TextContent(
                    type="text",
                    text="Error: iteration parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                test_plan_client = connection.clients.get_test_plan_client()
                
                test_plan_data = {
                    "name": name,
                    "description": description,
                    "iteration": iteration
                }
                
                test_plan = test_plan_client.create_test_plan(
                    test_plan_create_params=test_plan_data,
                    project=project
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(test_plan.__dict__ if hasattr(test_plan, '__dict__') else str(test_plan), indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if test plan client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Test plan creation requested",
                        "project": project,
                        "name": name,
                        "iteration": iteration,
                        "description": description,
                        "note": "Test Plan API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating test plan: {str(e)}"
            )]
    
    @server.call_tool()
    async def testplan_create_test_suite(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Creates a new test suite in a test plan."""
        try:
            project = arguments.get("project")
            plan_id = arguments.get("planId")
            suite_name = arguments.get("suiteName")
            parent_suite_id = arguments.get("parentSuiteId")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not plan_id:
                return [TextContent(
                    type="text",
                    text="Error: planId parameter is required"
                )]
                
            if not suite_name:
                return [TextContent(
                    type="text",
                    text="Error: suiteName parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                test_plan_client = connection.clients.get_test_plan_client()
                
                suite_data = {
                    "name": suite_name,
                    "suiteType": "staticTestSuite"
                }
                
                if parent_suite_id:
                    suite_data["parentSuite"] = {"id": parent_suite_id}
                
                test_suite = test_plan_client.create_test_suite(
                    test_suite_create_params=suite_data,
                    project=project,
                    plan_id=plan_id
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(test_suite.__dict__ if hasattr(test_suite, '__dict__') else str(test_suite), indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if test plan client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Test suite creation requested",
                        "project": project,
                        "planId": plan_id,
                        "suiteName": suite_name,
                        "parentSuiteId": parent_suite_id,
                        "note": "Test Plan API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating test suite: {str(e)}"
            )]
    
    @server.call_tool()
    async def testplan_create_test_case(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Creates a new test case."""
        try:
            project = arguments.get("project")
            title = arguments.get("title")
            description = arguments.get("description", "")
            test_steps = arguments.get("testSteps", [])
            assigned_to = arguments.get("assignedTo")
            priority = arguments.get("priority", 2)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not title:
                return [TextContent(
                    type="text",
                    text="Error: title parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            
            try:
                work_item_client = connection.clients.get_work_item_tracking_client()
                
                # Build work item data for test case
                document = [
                    {"op": "add", "path": "/fields/System.Title", "value": title},
                    {"op": "add", "path": "/fields/System.WorkItemType", "value": "Test Case"},
                    {"op": "add", "path": "/fields/System.Description", "value": description},
                    {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": priority}
                ]
                
                if assigned_to:
                    document.append({"op": "add", "path": "/fields/System.AssignedTo", "value": assigned_to})
                
                if test_steps:
                    steps_html = "<steps>"
                    for i, step in enumerate(test_steps, 1):
                        action = step.get("action", "")
                        expected = step.get("expectedResult", "")
                        steps_html += f'<step id="{i}"><parameterizedString isformatted="true">{action}</parameterizedString><parameterizedString isformatted="true">{expected}</parameterizedString><description/></step>'
                    steps_html += "</steps>"
                    document.append({"op": "add", "path": "/fields/Microsoft.VSTS.TCM.Steps", "value": steps_html})
                
                work_item = work_item_client.create_work_item(
                    document=document,
                    project=project,
                    type="Test Case"
                )
                
                return [TextContent(
                    type="text",
                    text=json.dumps(work_item.__dict__ if hasattr(work_item, '__dict__') else str(work_item), indent=2, default=str)
                )]
                
            except AttributeError:
                # Fallback if work item client is not available
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "message": "Test case creation requested",
                        "project": project,
                        "title": title,
                        "description": description,
                        "testSteps": test_steps,
                        "assignedTo": assigned_to,
                        "priority": priority,
                        "note": "Work Item Tracking API requires additional Azure DevOps SDK configuration"
                    }, indent=2)
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating test case: {str(e)}"
            )]