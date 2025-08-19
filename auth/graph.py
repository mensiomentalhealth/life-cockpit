import asyncio
"""
Microsoft Graph API authentication and client management.

Provides OAuth2 authentication using client credentials flow for service-to-service
authentication with Microsoft Graph API.
"""

from typing import Optional
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)


class GraphAuthManager:
    """Manages Microsoft Graph API authentication and client creation."""
    
    def __init__(self):
        self.config = get_config()
        self._credential: Optional[ClientSecretCredential] = None
        self._client: Optional[GraphServiceClient] = None
    
    def _create_credential(self) -> ClientSecretCredential:
        """Create Azure credential for authentication."""
        try:
            credential = ClientSecretCredential(
                tenant_id=self.config.azure_tenant_id,
                client_id=self.config.azure_client_id,
                client_secret=self.config.azure_client_secret
            )
            logger.info("Azure credential created successfully")
            return credential
        except Exception as e:
            logger.error(f"Failed to create Azure credential: {e}")
            raise
    
    def _create_client(self, credential: ClientSecretCredential) -> GraphServiceClient:
        """Create Graph service client with the provided credential."""
        try:
            client = GraphServiceClient(credentials=credential)
            logger.info("Graph service client created successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to create Graph service client: {e}")
            raise
    
    def get_client(self) -> GraphServiceClient:
        """Get or create Graph service client with authentication."""
        if self._client is None:
            if self._credential is None:
                self._credential = self._create_credential()
            self._client = self._create_client(self._credential)
        return self._client
    
    async def test_basic_auth(self) -> bool:
        """Test basic authentication without requiring specific API permissions."""
        try:
            client = self.get_client()
            logger.info("✅ Basic authentication successful!")
            logger.info("   - Credentials created successfully")
            logger.info("   - Graph service client created successfully")
            logger.info("   - Ready to make API calls (once permissions are granted)")
            return True
        except Exception as e:
            logger.error(f"❌ Basic authentication failed: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test Graph API connection by making a simple API call."""
        try:
            client = self.get_client()
            
            # Step 1: Test organization access (should work with Organization.Read.All permission)
            logger.info("Step 1: Testing organization access...")
            try:
                organization = await client.organization.get()
                if organization and organization.value:
                    org = organization.value[0]
                    logger.info(f"✅ Organization access successful: {org.display_name}")
                    logger.info("🎉 Graph API connection test completed successfully!")
                    return True
                else:
                    logger.warning("⚠️ Organization access successful but no org data found")
                    logger.info("🎉 Graph API connection test completed successfully!")
                    return True
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ Organization access failed: {error_msg}")
                if "Authorization_RequestDenied" in error_msg:
                    logger.error("💡 This suggests missing 'Organization.Read.All' permission")
                else:
                    logger.error(f"❌ Unexpected error: {error_msg}")
                    return False
            
            # Step 2: Try user access (requires User.Read.All permission)
            logger.info("Step 2: Testing user access...")
            try:
                users = await client.users.get()
                if users and users.value:
                    logger.info(f"✅ User access successful! Found {len(users.value)} users")
                    # Log first user as example
                    first_user = users.value[0]
                    logger.info(f"   Example user: {first_user.display_name} ({first_user.user_principal_name})")
                    logger.info("🎉 Graph API connection test completed successfully!")
                    return True
                else:
                    logger.warning("⚠️ User access successful but no users found")
                    logger.info("🎉 Graph API connection test completed successfully!")
                    return True
            except Exception as e:
                error_msg = str(e)
                logger.error(f"❌ User access failed: {error_msg}")
                if "Authorization_RequestDenied" in error_msg:
                    logger.error("💡 This suggests missing 'User.Read.All' permission")
                    logger.info("   This is expected if you haven't granted User.Read.All permission")
                else:
                    logger.error(f"❌ Unexpected error: {error_msg}")
                    return False
            
            # If we get here, all tests failed but authentication worked
            logger.warning("⚠️ Authentication successful but no API access granted")
            logger.info("💡 You may need to grant one of these permissions:")
            logger.info("   - Organization.Read.All") 
            logger.info("   - User.Read.All")
            return False
                
        except Exception as e:
            logger.error(f"❌ Graph API connection failed with unexpected error: {e}")
            return False
    
    async def get_current_user(self) -> Optional[dict]:
        """Get current user information (note: limited with client credentials flow)."""
        try:
            client = self.get_client()
            # With client credentials flow, we can only get users if we have User.Read.All permission
            users = await client.users.get()
            if users and users.value:
                user = users.value[0]
                return {
                    "id": user.id,
                    "display_name": user.display_name,
                    "user_principal_name": user.user_principal_name,
                    "mail": user.mail
                }
            return None
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Failed to get user information: {error_msg}")
            return None

    async def test_token_permissions(self) -> bool:
        """Test what permissions are actually granted in the token."""
        try:
            client = self.get_client()
            
            # Get the credential to access token info
            if self._credential:
                # Try to get a fresh token
                token = self._credential.get_token("https://graph.microsoft.com/.default")
                logger.info(f"✅ Token acquired successfully")
                logger.info(f"   Token expires: {token.expires_on}")
                
                # Test a very basic API call that should work with minimal permissions
                try:
                    # Try to get organization info (should work with Organization.Read.All)
                    logger.info("Testing organization access...")
                    org = await client.organization.get()
                    if org and org.value:
                        logger.info(f"✅ Organization access successful: {org.value[0].display_name}")
                        return True
                    else:
                        logger.warning("⚠️ Organization access successful but no org data found")
                        return True
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"❌ Organization access failed: {error_msg}")
                    
                    # Try user access (should work with User.Read.All)
                    try:
                        logger.info("Testing user access...")
                        users = await client.users.get()
                        if users and users.value:
                            logger.info(f"✅ User access successful! Found {len(users.value)} users")
                            first_user = users.value[0]
                            logger.info(f"   Example user: {first_user.display_name}")
                            return True
                        else:
                            logger.warning("⚠️ User access successful but no users found")
                            return True
                    except Exception as e2:
                        error_msg2 = str(e2)
                        logger.error(f"❌ User access failed: {error_msg2}")
                        
                        logger.info("💡 Debugging info:")
                        logger.info(f"   Client ID: {self.config.azure_client_id}")
                        logger.info(f"   Tenant ID: {self.config.azure_tenant_id}")
                        logger.info("   Make sure you've granted admin consent for the permissions")
                        
                        return False
            else:
                logger.error("❌ No credential available")
                return False
                
        except Exception as e:
            logger.error(f"❌ Token permission test failed: {e}")
            return False


# Global instance for easy access
_auth_manager: Optional[GraphAuthManager] = None


def get_auth_manager() -> GraphAuthManager:
    """Get the global authentication manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = GraphAuthManager()
    return _auth_manager


async def test_graph_connection() -> bool:
    """Test Graph API connection (legacy function for compatibility)."""
    auth_manager = get_auth_manager()
    return await auth_manager.test_connection()


def get_graph_client() -> GraphServiceClient:
    """Get authenticated Graph service client."""
    auth_manager = get_auth_manager()
    return auth_manager.get_client()

async def main():
    logger.info('Testing Microsoft Graph API authentication...')
    
    # Test basic authentication first
    auth_manager = get_auth_manager()
    basic_auth_success = await auth_manager.test_basic_auth()
    
    if basic_auth_success:
        logger.info('✅ Basic authentication test completed successfully!')
        
        # Test token permissions to debug the issue
        logger.info('Testing token permissions...')
        token_success = await auth_manager.test_token_permissions()
        
        if token_success:
            logger.info('🎉 Token permissions test completed successfully!')
        else:
            logger.warning('⚠️ Token permissions test failed')
            logger.info('💡 This suggests the API permissions may not be properly granted')
        
        # Now test API access
        logger.info('Testing API access...')
        api_success = await auth_manager.test_connection()
        
        if api_success:
            logger.info('🎉 Full authentication and API test completed successfully!')
        else:
            logger.warning('⚠️ Authentication works but API access needs permissions')
            logger.info('💡 Please check admin consent for the API permissions')
    else:
        logger.error('❌ Basic authentication test failed!')
        logger.error('💡 Check your Azure credentials in .env file')

if __name__ == '__main__':
    asyncio.run(main())
