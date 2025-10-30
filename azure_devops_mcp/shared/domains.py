"""Domain management for Azure DevOps MCP server."""

from enum import Enum
from typing import List, Optional, Set, Union


class Domain(str, Enum):
    """Available Azure DevOps MCP domains."""
    
    ADVANCED_SECURITY = "advanced-security"
    PIPELINES = "pipelines"
    CORE = "core"
    REPOSITORIES = "repositories"
    SEARCH = "search"
    TEST_PLANS = "test-plans"
    WIKI = "wiki"
    WORK = "work"
    WORK_ITEMS = "work-items"


ALL_DOMAINS = "all"


class DomainsManager:
    """Manages domain parsing and validation for Azure DevOps MCP server tools."""
    
    def __init__(self, domains_input: Optional[Union[str, List[str]]] = None):
        """Initialize the domains manager.
        
        Args:
            domains_input: Either "all", single domain name, array of domain names, 
                          or None (defaults to "all")
        """
        self.enabled_domains: Set[str] = set()
        self._parse_domains(domains_input)
    
    def _parse_domains(self, domains_input: Optional[Union[str, List[str]]]) -> None:
        """Parse and validate domains from input."""
        if not domains_input:
            self._enable_all_domains()
            return
        
        if isinstance(domains_input, list):
            self._handle_array_input(domains_input)
            return
        
        self._handle_string_input(domains_input)
    
    def _handle_array_input(self, domains_input: List[str]) -> None:
        """Handle array input of domains."""
        if len(domains_input) == 0 or ALL_DOMAINS in domains_input:
            self._enable_all_domains()
            return
        
        domains = [d.strip().lower() for d in domains_input]
        self._validate_and_add_domains(domains)
    
    def _handle_string_input(self, domains_input: str) -> None:
        """Handle string input of domains."""
        if domains_input == ALL_DOMAINS:
            self._enable_all_domains()
            return
        
        # Handle comma-separated domains
        domains = [d.strip().lower() for d in domains_input.split(",")]
        self._validate_and_add_domains(domains)
    
    def _validate_and_add_domains(self, domains: List[str]) -> None:
        """Validate and add domains to enabled set."""
        available_domains = [d.value for d in Domain]
        
        for domain in domains:
            if domain in available_domains:
                self.enabled_domains.add(domain)
            elif domain == ALL_DOMAINS:
                self._enable_all_domains()
            else:
                print(f"Error: Specified invalid domain '{domain}'. "
                      f"Please specify exactly as available domains: {', '.join(available_domains)}")
        
        if len(self.enabled_domains) == 0:
            self._enable_all_domains()
    
    def _enable_all_domains(self) -> None:
        """Enable all available domains."""
        for domain in Domain:
            self.enabled_domains.add(domain.value)
    
    def is_domain_enabled(self, domain: str) -> bool:
        """Check if a specific domain is enabled.
        
        Args:
            domain: Domain name to check
            
        Returns:
            True if domain is enabled
        """
        return domain in self.enabled_domains
    
    def get_enabled_domains(self) -> Set[str]:
        """Get all enabled domains.
        
        Returns:
            Set of enabled domain names
        """
        return self.enabled_domains.copy()
    
    @staticmethod
    def get_available_domains() -> List[str]:
        """Get list of all available domains.
        
        Returns:
            Array of available domain names
        """
        return [d.value for d in Domain]
    
    @staticmethod
    def parse_domains_input(domains_input: Optional[Union[str, List[str]]]) -> List[str]:
        """Parse domains input from string or array to a normalized array of strings.
        
        Args:
            domains_input: Domains input to parse
            
        Returns:
            Normalized array of domain strings
        """
        if not domains_input or DomainsManager._is_empty_domains_input(domains_input):
            return ["all"]
        
        if isinstance(domains_input, str):
            return [d.strip().lower() for d in domains_input.split(",")]
        
        return [d.strip().lower() for d in domains_input]
    
    @staticmethod
    def _is_empty_domains_input(domains_input: Optional[Union[str, List[str]]]) -> bool:
        """Check if domains input is empty."""
        if isinstance(domains_input, str) and domains_input.strip() == "":
            return True
        if isinstance(domains_input, list) and len(domains_input) == 0:
            return True
        return False