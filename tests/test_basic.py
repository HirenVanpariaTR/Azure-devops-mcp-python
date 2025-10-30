"""Test configuration for Azure DevOps MCP server."""

import pytest


def test_imports():
    """Test that all modules can be imported."""
    from azure_devops_mcp import __version__
    from azure_devops_mcp.shared.domains import Domain, DomainsManager
    from azure_devops_mcp.auth import create_authenticator
    from azure_devops_mcp.tools import configure_all_tools
    
    assert __version__ == "2.2.1"
    assert Domain.CORE.value == "core"
    
    # Test domains manager
    manager = DomainsManager(["core", "pipelines"])
    assert manager.is_domain_enabled("core")
    assert manager.is_domain_enabled("pipelines")
    assert not manager.is_domain_enabled("wiki")


def test_domains_manager():
    """Test domains manager functionality."""
    from azure_devops_mcp.shared.domains import DomainsManager, Domain
    
    # Test "all" domains
    manager = DomainsManager(["all"])
    for domain in Domain:
        assert manager.is_domain_enabled(domain.value)
    
    # Test specific domains
    manager = DomainsManager(["core", "repositories"])
    assert manager.is_domain_enabled("core")
    assert manager.is_domain_enabled("repositories")
    assert not manager.is_domain_enabled("pipelines")
    
    # Test default (all)
    manager = DomainsManager()
    assert manager.is_domain_enabled("core")
    assert manager.is_domain_enabled("pipelines")