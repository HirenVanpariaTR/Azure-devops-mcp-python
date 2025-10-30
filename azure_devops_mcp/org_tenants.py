"""Organization tenant management for Azure DevOps MCP server."""

import json
import os
import time
from pathlib import Path
from typing import Dict, Optional

import aiohttp


class OrgTenantCacheEntry:
    """Cache entry for organization tenant mapping."""
    
    def __init__(self, tenant_id: str, refreshed_on: float):
        self.tenant_id = tenant_id
        self.refreshed_on = refreshed_on
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for serialization."""
        return {
            "tenantId": self.tenant_id,
            "refreshedOn": self.refreshed_on
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> "OrgTenantCacheEntry":
        """Create from dictionary."""
        return cls(data["tenantId"], data["refreshedOn"])


# Cache configuration
CACHE_FILE = Path.home() / ".ado_orgs.cache"
CACHE_TTL_MS = 7 * 24 * 60 * 60 * 1000  # 1 week in milliseconds


async def load_cache() -> Dict[str, OrgTenantCacheEntry]:
    """Load organization tenant cache from file.
    
    Returns:
        Dictionary mapping organization names to cache entries
    """
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                cache_data = json.load(f)
                return {
                    org: OrgTenantCacheEntry.from_dict(entry)
                    for org, entry in cache_data.items()
                }
    except Exception:
        # Cache file doesn't exist or is invalid, return empty cache
        pass
    
    return {}


async def try_saving_cache(cache: Dict[str, OrgTenantCacheEntry]) -> None:
    """Try to save organization tenant cache to file.
    
    Args:
        cache: Cache dictionary to save
    """
    try:
        cache_data = {
            org: entry.to_dict()
            for org, entry in cache.items()
        }
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"Failed to save org tenants cache: {e}")


async def fetch_tenant_from_api(org_name: str) -> str:
    """Fetch tenant ID from Azure DevOps API.
    
    Args:
        org_name: Organization name
        
    Returns:
        Tenant ID string
        
    Raises:
        Exception: If API call fails or tenant ID not found
    """
    url = f"https://vssps.dev.azure.com/{org_name}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url) as response:
                if response.status != 404:
                    raise Exception(f"Expected status 404, got {response.status}")
                
                tenant_id = response.headers.get("x-vss-resourcetenant")
                if not tenant_id:
                    raise Exception("x-vss-resourcetenant header not found in response")
                
                return tenant_id
    
    except Exception as e:
        raise Exception(f"Failed to fetch tenant for organization {org_name}: {e}")


def is_cache_entry_expired(entry: OrgTenantCacheEntry) -> bool:
    """Check if cache entry is expired.
    
    Args:
        entry: Cache entry to check
        
    Returns:
        True if entry is expired
    """
    return (time.time() * 1000) - entry.refreshed_on > CACHE_TTL_MS


async def get_org_tenant(org_name: str) -> Optional[str]:
    """Get tenant ID for organization, using cache when possible.
    
    Args:
        org_name: Organization name
        
    Returns:
        Tenant ID if found, None otherwise
    """
    # Load cache
    cache = await load_cache()
    
    # Check if tenant is cached and not expired
    cached_entry = cache.get(org_name)
    if cached_entry and not is_cache_entry_expired(cached_entry):
        return cached_entry.tenant_id
    
    # Try to fetch fresh tenant from API
    try:
        tenant_id = await fetch_tenant_from_api(org_name)
        
        # Cache the result
        cache[org_name] = OrgTenantCacheEntry(tenant_id, time.time() * 1000)
        await try_saving_cache(cache)
        
        return tenant_id
    
    except Exception as e:
        # If we have an expired cache entry, return it as fallback
        if cached_entry:
            print(f"Failed to fetch fresh tenant for ADO org {org_name}, using expired cache entry: {e}")
            return cached_entry.tenant_id
        
        # No cache entry available, log and return None
        print(f"Failed to fetch tenant for ADO org {org_name}: {e}")
        return None