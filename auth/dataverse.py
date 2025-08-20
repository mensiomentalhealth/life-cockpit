import asyncio
"""
Dataverse Web API authentication and client management.

Provides OAuth2 authentication using client credentials flow for service-to-service
authentication with Dataverse Web API.
"""

from typing import Optional, Dict, Any, List
import httpx
from azure.identity import ClientSecretCredential

from utils.config import get_config
from utils.logger import get_logger

logger = get_logger(__name__)


class DataverseAuthManager:
    """Manages Dataverse Web API authentication and client creation."""
    
    def __init__(self):
        self.config = get_config()
        self._credential: Optional[ClientSecretCredential] = None
        self._dataverse_url: Optional[str] = None
    
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
    
    def get_credential(self) -> ClientSecretCredential:
        """Get or create Azure credential for authentication."""
        if self._credential is None:
            self._credential = self._create_credential()
        return self._credential
    
    def get_dataverse_url(self) -> str:
        """Get the Dataverse environment URL."""
        if not self._dataverse_url:
            # Extract from the configured URL
            base_url = self.config.dataverse_url.rstrip('/')
            self._dataverse_url = base_url
        return self._dataverse_url
    
    async def get_token(self, impersonate_user_id: Optional[str] = None) -> str:
        """Get access token for Dataverse API."""
        try:
            credential = self.get_credential()
            dataverse_url = self.get_dataverse_url()
            token_scope = f"{dataverse_url}/.default"
            
            logger.info(f"Using token scope: {token_scope}")
            token = credential.get_token(token_scope)
            
            if impersonate_user_id:
                logger.info(f"Impersonating user: {impersonate_user_id}")
            
            return token.token
        except Exception as e:
            logger.error(f"Failed to get Dataverse token: {e}")
            raise
    
    async def test_connection(self, impersonate_user_id: Optional[str] = None) -> bool:
        """Test Dataverse API connection using WhoAmI endpoint."""
        try:
            token = await self.get_token(impersonate_user_id)
            dataverse_url = self.get_dataverse_url()
            api_url = f"{dataverse_url}/api/data/v9.2/WhoAmI"
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0'
            }
            
            if impersonate_user_id:
                headers['MSCRMCallerID'] = impersonate_user_id
            
            logger.info(f"Testing Dataverse connection: {api_url}")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(api_url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    user_id = data.get('UserId', 'Unknown')
                    business_unit_id = data.get('BusinessUnitId', 'Unknown')
                    
                    logger.info("✅ Dataverse connection successful!")
                    logger.info(f"   User ID: {user_id}")
                    logger.info(f"   Business Unit ID: {business_unit_id}")
                    return True
                else:
                    logger.error(f"Dataverse connection failed: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Dataverse connection test failed: {e}")
            return False
    
    async def get_entity_definitions(self, impersonate_user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all entity definitions from Dataverse."""
        try:
            token = await self.get_token(impersonate_user_id)
            dataverse_url = self.get_dataverse_url()
            api_url = f"{dataverse_url}/api/data/v9.2/EntityDefinitions"
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'OData-MaxVersion': '4.0',
                'OData-Version': '4.0',
                'Prefer': 'return=representation,odata.include-annotations="*"'
            }
            
            if impersonate_user_id:
                headers['MSCRMCallerID'] = impersonate_user_id
            
            logger.info(f"Calling Dataverse Web API: {api_url}")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(api_url, headers=headers)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        entities = data.get('value', [])
                        
                        if not entities:
                            logger.warning("No entities found in response")
                            return []
                        
                        # Filter for user-created entities (not system entities)
                        user_entities = []
                        for entity in entities:
                            try:
                                logical_name = entity.get('LogicalName', '')
                                if not logical_name or logical_name.startswith('_'):
                                    continue
                                    
                                display_name_obj = entity.get('DisplayName', {})
                                display_name = ''
                                if isinstance(display_name_obj, dict):
                                    user_label = display_name_obj.get('UserLocalizedLabel', {})
                                    if isinstance(user_label, dict):
                                        display_name = user_label.get('Label', '')
                                
                                description_obj = entity.get('Description', {})
                                description = ''
                                if isinstance(description_obj, dict):
                                    desc_label = description_obj.get('UserLocalizedLabel', {})
                                    if isinstance(desc_label, dict):
                                        description = desc_label.get('Label', '')
                                
                                entity_type = "Custom" if entity.get('IsCustomEntity', False) else "Standard"
                                
                                user_entities.append({
                                    "name": logical_name,
                                    "display_name": display_name,
                                    "description": description,
                                    "entity_type": entity_type
                                })
                            except Exception as e:
                                logger.warning(f"Error processing entity: {e}")
                                continue
                        
                        logger.info(f"Found {len(user_entities)} user entities in Dataverse")
                        return user_entities
                        
                    except Exception as e:
                        logger.error(f"JSON parsing error: {e}")
                        logger.error(f"Response length: {len(response.text)}")
                        logger.error(f"Response preview: {response.text[:500]}")
                        return []
                else:
                    logger.error(f"Dataverse API call failed: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Failed to get Dataverse entity definitions: {e}")
            return []
