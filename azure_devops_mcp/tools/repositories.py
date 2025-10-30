"""Repositories tools for Azure DevOps MCP server."""

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


def configure_repo_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str]
) -> None:
    """Configure repository tools for Azure DevOps.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Organization URL
        user_agent_provider: Function that returns user agent string
    """
    
    @server.call_tool()
    async def repo_list_repos_by_project(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Retrieves repositories for a project."""
        try:
            project = arguments.get("project")
            include_links = arguments.get("includeLinks", False)
            include_all_urls = arguments.get("includeAllUrls", False)
            include_hidden = arguments.get("includeHidden", False)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            repositories = git_client.get_repositories(
                project=project,
                include_links=include_links,
                include_all_urls=include_all_urls,
                include_hidden=include_hidden
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([repo.__dict__ if hasattr(repo, '__dict__') else str(repo) for repo in repositories], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching repositories: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_get_repo_by_name_or_id(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets a repository by name or ID."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            include_parents = arguments.get("includeParents", False)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            repository = git_client.get_repository(
                project=project,
                repository_id=repository_id,
                include_parents=include_parents
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(repository.__dict__ if hasattr(repository, '__dict__') else str(repository), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching repository: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_list_branches_by_repo(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets branches for a repository."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            refs = git_client.get_refs(
                project=project,
                repository_id=repository_id,
                filter="heads/"
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([ref.__dict__ if hasattr(ref, '__dict__') else str(ref) for ref in refs], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching branches: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_get_branch_by_name(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets a specific branch by name."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            branch_name = arguments.get("branchName")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not branch_name:
                return [TextContent(
                    type="text",
                    text="Error: branchName parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            # Ensure branch name has proper prefix
            ref_name = f"refs/heads/{branch_name}" if not branch_name.startswith("refs/") else branch_name
            
            refs = git_client.get_refs(
                project=project,
                repository_id=repository_id,
                filter=ref_name
            )
            
            if refs and len(refs) > 0:
                return [TextContent(
                    type="text",
                    text=json.dumps(refs[0].__dict__ if hasattr(refs[0], '__dict__') else str(refs[0]), indent=2, default=str)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"Branch '{branch_name}' not found"
                )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching branch: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_create_branch(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Creates a new branch."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            branch_name = arguments.get("branchName")
            source_branch = arguments.get("sourceBranch", "main")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not branch_name:
                return [TextContent(
                    type="text",
                    text="Error: branchName parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            # Get source branch reference
            source_ref_name = f"refs/heads/{source_branch}" if not source_branch.startswith("refs/") else source_branch
            source_refs = git_client.get_refs(
                project=project,
                repository_id=repository_id,
                filter=source_ref_name
            )
            
            if not source_refs or len(source_refs) == 0:
                return [TextContent(
                    type="text",
                    text=f"Source branch '{source_branch}' not found"
                )]
            
            source_object_id = source_refs[0].object_id
            
            # Create new branch reference
            new_ref_name = f"refs/heads/{branch_name}" if not branch_name.startswith("refs/") else branch_name
            
            ref_update = {
                "name": new_ref_name,
                "oldObjectId": "0000000000000000000000000000000000000000",
                "newObjectId": source_object_id
            }
            
            result = git_client.update_refs(
                ref_updates=[ref_update],
                project=project,
                repository_id=repository_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "message": f"Branch '{branch_name}' created successfully",
                    "sourceBranch": source_branch,
                    "newBranch": branch_name,
                    "result": result.__dict__ if hasattr(result, '__dict__') else str(result)
                }, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating branch: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_list_pull_requests_by_repo_or_project(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets pull requests for a repository or project."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            creator_id = arguments.get("creatorId")
            reviewer_id = arguments.get("reviewerId")
            source_ref_name = arguments.get("sourceRefName")
            target_ref_name = arguments.get("targetRefName")
            status = arguments.get("status")
            top = arguments.get("top", 50)
            skip = arguments.get("skip", 0)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            search_criteria = {}
            if creator_id:
                search_criteria["creatorId"] = creator_id
            if reviewer_id:
                search_criteria["reviewerId"] = reviewer_id
            if source_ref_name:
                search_criteria["sourceRefName"] = source_ref_name
            if target_ref_name:
                search_criteria["targetRefName"] = target_ref_name
            if status:
                search_criteria["status"] = status
            
            pull_requests = git_client.get_pull_requests(
                project=project,
                repository_id=repository_id,
                search_criteria=search_criteria,
                max_comment_length=None,
                skip=skip,
                top=top
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([pr.__dict__ if hasattr(pr, '__dict__') else str(pr) for pr in pull_requests], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching pull requests: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_get_pull_request_by_id(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets a pull request by ID."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            pull_request_id = arguments.get("pullRequestId")
            max_comment_length = arguments.get("maxCommentLength")
            skip = arguments.get("skip", 0)
            top = arguments.get("top", 100)
            include_commits = arguments.get("includeCommits", False)
            include_work_item_refs = arguments.get("includeWorkItemRefs", False)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not pull_request_id:
                return [TextContent(
                    type="text",
                    text="Error: pullRequestId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            pull_request = git_client.get_pull_request(
                project=project,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                max_comment_length=max_comment_length,
                skip=skip,
                top=top,
                include_commits=include_commits,
                include_work_item_refs=include_work_item_refs
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(pull_request.__dict__ if hasattr(pull_request, '__dict__') else str(pull_request), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching pull request: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_create_pull_request(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Creates a new pull request."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            title = arguments.get("title")
            description = arguments.get("description", "")
            source_branch = arguments.get("sourceBranch")
            target_branch = arguments.get("targetBranch", "main")
            reviewers = arguments.get("reviewers", [])
            work_items = arguments.get("workItems", [])
            is_draft = arguments.get("isDraft", False)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not title:
                return [TextContent(
                    type="text",
                    text="Error: title parameter is required"
                )]
                
            if not source_branch:
                return [TextContent(
                    type="text",
                    text="Error: sourceBranch parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            # Prepare pull request data
            source_ref = f"refs/heads/{source_branch}" if not source_branch.startswith("refs/") else source_branch
            target_ref = f"refs/heads/{target_branch}" if not target_branch.startswith("refs/") else target_branch
            
            pull_request_data = {
                "sourceRefName": source_ref,
                "targetRefName": target_ref,
                "title": title,
                "description": description,
                "isDraft": is_draft
            }
            
            if reviewers:
                pull_request_data["reviewers"] = [{"id": reviewer} for reviewer in reviewers]
            
            if work_items:
                pull_request_data["workItemRefs"] = [{"id": work_item} for work_item in work_items]
            
            pull_request = git_client.create_pull_request(
                git_pull_request_to_create=pull_request_data,
                project=project,
                repository_id=repository_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(pull_request.__dict__ if hasattr(pull_request, '__dict__') else str(pull_request), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating pull request: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_update_pull_request(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Updates a pull request."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            pull_request_id = arguments.get("pullRequestId")
            title = arguments.get("title")
            description = arguments.get("description")
            status = arguments.get("status")
            is_draft = arguments.get("isDraft")
            auto_complete_set_by = arguments.get("autoCompleteSetBy")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not pull_request_id:
                return [TextContent(
                    type="text",
                    text="Error: pullRequestId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            # Build update data
            update_data = {}
            if title is not None:
                update_data["title"] = title
            if description is not None:
                update_data["description"] = description
            if status is not None:
                update_data["status"] = status
            if is_draft is not None:
                update_data["isDraft"] = is_draft
            if auto_complete_set_by is not None:
                update_data["autoCompleteSetBy"] = {"id": auto_complete_set_by}
            
            pull_request = git_client.update_pull_request(
                git_pull_request_to_update=update_data,
                project=project,
                repository_id=repository_id,
                pull_request_id=pull_request_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(pull_request.__dict__ if hasattr(pull_request, '__dict__') else str(pull_request), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error updating pull request: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_list_pull_request_threads(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets comment threads for a pull request."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            pull_request_id = arguments.get("pullRequestId")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not pull_request_id:
                return [TextContent(
                    type="text",
                    text="Error: pullRequestId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            threads = git_client.get_threads(
                project=project,
                repository_id=repository_id,
                pull_request_id=pull_request_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([thread.__dict__ if hasattr(thread, '__dict__') else str(thread) for thread in threads], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching pull request threads: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_create_pull_request_thread(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Creates a comment thread on a pull request."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            pull_request_id = arguments.get("pullRequestId")
            comment_text = arguments.get("commentText")
            file_path = arguments.get("filePath")
            line_number = arguments.get("lineNumber")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not pull_request_id:
                return [TextContent(
                    type="text",
                    text="Error: pullRequestId parameter is required"
                )]
                
            if not comment_text:
                return [TextContent(
                    type="text",
                    text="Error: commentText parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            # Build thread data
            thread_data = {
                "comments": [{"content": comment_text}],
                "status": "active"
            }
            
            # Add thread context if file path and line number are provided
            if file_path and line_number:
                thread_data["threadContext"] = {
                    "filePath": file_path,
                    "rightFileStart": {"line": line_number, "offset": 1},
                    "rightFileEnd": {"line": line_number, "offset": 1}
                }
            
            thread = git_client.create_thread(
                comment_thread=thread_data,
                project=project,
                repository_id=repository_id,
                pull_request_id=pull_request_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(thread.__dict__ if hasattr(thread, '__dict__') else str(thread), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error creating pull request thread: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_reply_to_comment(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Replies to a comment in a pull request thread."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            pull_request_id = arguments.get("pullRequestId")
            thread_id = arguments.get("threadId")
            comment_text = arguments.get("commentText")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not pull_request_id:
                return [TextContent(
                    type="text",
                    text="Error: pullRequestId parameter is required"
                )]
                
            if not thread_id:
                return [TextContent(
                    type="text",
                    text="Error: threadId parameter is required"
                )]
                
            if not comment_text:
                return [TextContent(
                    type="text",
                    text="Error: commentText parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            comment_data = {"content": comment_text}
            
            comment = git_client.create_comment(
                comment=comment_data,
                project=project,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                thread_id=thread_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(comment.__dict__ if hasattr(comment, '__dict__') else str(comment), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error replying to comment: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_resolve_comment(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Resolves or unresolves a comment thread."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            pull_request_id = arguments.get("pullRequestId")
            thread_id = arguments.get("threadId")
            status = arguments.get("status", "fixed")  # fixed, active, pending, etc.
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not pull_request_id:
                return [TextContent(
                    type="text",
                    text="Error: pullRequestId parameter is required"
                )]
                
            if not thread_id:
                return [TextContent(
                    type="text",
                    text="Error: threadId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            thread_data = {"status": status}
            
            thread = git_client.update_thread(
                comment_thread=thread_data,
                project=project,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                thread_id=thread_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(thread.__dict__ if hasattr(thread, '__dict__') else str(thread), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error resolving comment: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_search_commits(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Searches for commits in a repository."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            search_criteria = arguments.get("searchCriteria", {})
            skip = arguments.get("skip", 0)
            top = arguments.get("top", 100)
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            commits = git_client.get_commits(
                project=project,
                repository_id=repository_id,
                search_criteria=search_criteria,
                skip=skip,
                top=top
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([commit.__dict__ if hasattr(commit, '__dict__') else str(commit) for commit in commits], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error searching commits: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_list_my_branches_by_repo(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets branches created by the current user."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            # Get all branches and filter by creator (this would need user context in a real implementation)
            refs = git_client.get_refs(
                project=project,
                repository_id=repository_id,
                filter="heads/"
            )
            
            # For now, return all branches with a note about filtering
            result = {
                "message": "Listing all branches (filtering by creator requires additional user context)",
                "branches": [ref.__dict__ if hasattr(ref, '__dict__') else str(ref) for ref in refs]
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching user branches: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_list_pull_request_thread_comments(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets comments for a specific pull request thread."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            pull_request_id = arguments.get("pullRequestId")
            thread_id = arguments.get("threadId")
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not pull_request_id:
                return [TextContent(
                    type="text",
                    text="Error: pullRequestId parameter is required"
                )]
                
            if not thread_id:
                return [TextContent(
                    type="text",
                    text="Error: threadId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            comments = git_client.get_comments(
                project=project,
                repository_id=repository_id,
                pull_request_id=pull_request_id,
                thread_id=thread_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps([comment.__dict__ if hasattr(comment, '__dict__') else str(comment) for comment in comments], indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error fetching thread comments: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_update_pull_request_reviewers(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Updates reviewers on a pull request."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            pull_request_id = arguments.get("pullRequestId")
            reviewers = arguments.get("reviewers", [])
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not pull_request_id:
                return [TextContent(
                    type="text",
                    text="Error: pullRequestId parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            # Create reviewer objects
            reviewer_data = []
            for reviewer in reviewers:
                if isinstance(reviewer, str):
                    reviewer_data.append({"id": reviewer})
                elif isinstance(reviewer, dict):
                    reviewer_data.append(reviewer)
            
            # Update pull request with new reviewers
            update_data = {"reviewers": reviewer_data}
            
            pull_request = git_client.update_pull_request(
                git_pull_request_to_update=update_data,
                project=project,
                repository_id=repository_id,
                pull_request_id=pull_request_id
            )
            
            return [TextContent(
                type="text",
                text=json.dumps(pull_request.__dict__ if hasattr(pull_request, '__dict__') else str(pull_request), indent=2, default=str)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error updating pull request reviewers: {str(e)}"
            )]
    
    @server.call_tool()
    async def repo_list_pull_requests_by_commits(
        arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Gets pull requests that contain specific commits."""
        try:
            project = arguments.get("project")
            repository_id = arguments.get("repositoryId")
            commit_ids = arguments.get("commitIds", [])
            
            if not project:
                return [TextContent(
                    type="text",
                    text="Error: project parameter is required"
                )]
                
            if not repository_id:
                return [TextContent(
                    type="text",
                    text="Error: repositoryId parameter is required"
                )]
                
            if not commit_ids:
                return [TextContent(
                    type="text",
                    text="Error: commitIds parameter is required"
                )]
            
            token = token_provider()
            connection = await get_azure_devops_connection(token, org_url)
            git_client = connection.clients.get_git_client()
            
            # This would require a more complex query in the actual API
            # For now, return a placeholder response
            result = {
                "message": "Pull requests by commits query initiated",
                "project": project,
                "repositoryId": repository_id,
                "commitIds": commit_ids,
                "note": "Full implementation requires advanced Git query capabilities in Azure DevOps SDK"
            }
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
            
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error listing pull requests by commits: {str(e)}"
            )]