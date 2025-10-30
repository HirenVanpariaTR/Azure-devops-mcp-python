"""Tools configuration for Azure DevOps MCP server."""

from typing import Callable, Set

from mcp.server import Server

from azure_devops_mcp.shared.domains import Domain


def configure_all_tools(
    server: Server,
    token_provider: Callable[[], str],
    org_url: str,
    user_agent_provider: Callable[[], str],
    enabled_domains: Set[str]
) -> None:
    """Configure all tools based on enabled domains.
    
    Args:
        server: MCP server instance
        token_provider: Function that returns access token
        org_url: Azure DevOps organization URL
        user_agent_provider: Function that returns user agent string
        enabled_domains: Set of enabled domain names
    """
    
    def configure_if_domain_enabled(domain: str, configure_fn: Callable[[], None]) -> None:
        """Configure tools if domain is enabled."""
        if domain in enabled_domains:
            configure_fn()
    
    # Import tool configuration functions
    from azure_devops_mcp.tools.core import configure_core_tools
    from azure_devops_mcp.tools.work import configure_work_tools
    from azure_devops_mcp.tools.pipelines import configure_pipeline_tools
    from azure_devops_mcp.tools.repositories import configure_repo_tools
    from azure_devops_mcp.tools.work_items import configure_work_item_tools
    from azure_devops_mcp.tools.wiki import configure_wiki_tools
    from azure_devops_mcp.tools.test_plans import configure_test_plan_tools
    from azure_devops_mcp.tools.search import configure_search_tools
    from azure_devops_mcp.tools.advanced_security import configure_advsec_tools
    
    # Configure tools for each enabled domain
    configure_if_domain_enabled(
        Domain.CORE.value,
        lambda: configure_core_tools(server, token_provider, org_url, user_agent_provider)
    )
    
    configure_if_domain_enabled(
        Domain.WORK.value,
        lambda: configure_work_tools(server, token_provider, org_url, user_agent_provider)
    )
    
    configure_if_domain_enabled(
        Domain.PIPELINES.value,
        lambda: configure_pipeline_tools(server, token_provider, org_url, user_agent_provider)
    )
    
    configure_if_domain_enabled(
        Domain.REPOSITORIES.value,
        lambda: configure_repo_tools(server, token_provider, org_url, user_agent_provider)
    )
    
    configure_if_domain_enabled(
        Domain.WORK_ITEMS.value,
        lambda: configure_work_item_tools(server, token_provider, org_url, user_agent_provider)
    )
    
    configure_if_domain_enabled(
        Domain.WIKI.value,
        lambda: configure_wiki_tools(server, token_provider, org_url, user_agent_provider)
    )
    
    configure_if_domain_enabled(
        Domain.TEST_PLANS.value,
        lambda: configure_test_plan_tools(server, token_provider, org_url, user_agent_provider)
    )
    
    configure_if_domain_enabled(
        Domain.SEARCH.value,
        lambda: configure_search_tools(server, token_provider, org_url, user_agent_provider)
    )
    
    configure_if_domain_enabled(
        Domain.ADVANCED_SECURITY.value,
        lambda: configure_advsec_tools(server, token_provider, org_url, user_agent_provider)
    )