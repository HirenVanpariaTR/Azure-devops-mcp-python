"""Authentication module for Azure DevOps MCP server."""

import os
from typing import Optional

from azure.identity import (
    AzureCliCredential,
    ChainedTokenCredential,
    DefaultAzureCredential,
    InteractiveBrowserCredential,
)
from azure.core.credentials import TokenCredential


SCOPES = ["499b84ac-1321-427f-aa17-267ca6975798/.default"]


class OAuthAuthenticator:
    """OAuth authenticator for Azure DevOps."""
    
    CLIENT_ID = "0d50963b-7bb9-4fe7-94c7-a99af00b5136"
    DEFAULT_AUTHORITY = "https://login.microsoftonline.com/common"
    ZERO_TENANT_ID = "00000000-0000-0000-0000-000000000000"
    
    def __init__(self, tenant_id: Optional[str] = None):
        """Initialize OAuth authenticator.
        
        Args:
            tenant_id: Optional tenant ID for authentication
        """
        self.tenant_id = tenant_id
        authority = self.DEFAULT_AUTHORITY
        
        if tenant_id and tenant_id != self.ZERO_TENANT_ID:
            authority = f"https://login.microsoftonline.com/{tenant_id}"
        
        self.credential = InteractiveBrowserCredential(
            client_id=self.CLIENT_ID,
            authority=authority,
        )
    
    async def get_token(self) -> str:
        """Get access token for Azure DevOps.
        
        Returns:
            Access token string
            
        Raises:
            Exception: If token acquisition fails
        """
        try:
            token = self.credential.get_token(*SCOPES)
            if not token or not token.token:
                raise Exception("Failed to obtain Azure DevOps OAuth token.")
            return token.token
        except Exception as e:
            raise Exception(f"Failed to obtain Azure DevOps OAuth token: {e}")


def create_authenticator(auth_type: str, tenant_id: Optional[str] = None, pat_token: Optional[str] = None):
    """Create authenticator function based on type.
    
    Args:
        auth_type: Authentication type ('azcli', 'env', 'interactive', or 'pat')
        tenant_id: Optional tenant ID
        pat_token: Optional PAT token for 'pat' authentication
        
    Returns:
        Async function that returns access token or PAT token
    """
    
    async def get_token() -> str:
        if auth_type == "pat":
            # Return PAT token directly for basic authentication
            if not pat_token:
                raise Exception("PAT token is required for 'pat' authentication")
            return pat_token
            
        elif auth_type in ["azcli", "env"]:
            if auth_type != "env":
                os.environ["AZURE_TOKEN_CREDENTIALS"] = "dev"
            
            credential: TokenCredential = DefaultAzureCredential()
            
            if tenant_id:
                # Use Azure CLI credential if tenant_id is provided for multi-tenant scenarios
                azure_cli_credential = AzureCliCredential(tenant_id=tenant_id)
                credential = ChainedTokenCredential(azure_cli_credential, credential)
            
            try:
                token = credential.get_token(*SCOPES)
                if not token or not token.token:
                    raise Exception("Failed to obtain token from credential chain")
                return token.token
            except Exception as e:
                raise Exception(
                    "Failed to obtain Azure DevOps token. "
                    "Ensure you have Azure CLI logged in or use interactive authentication."
                ) from e
        
        else:  # interactive authentication
            authenticator = OAuthAuthenticator(tenant_id)
            return await authenticator.get_token()
    
    return get_token