#!/usr/bin/env python3
"""
Hello Dataverse - Authentication and Table Listing Script

This script demonstrates:
1. Microsoft Graph API authentication
2. Dataverse connection and table listing
3. Structured logging and error handling

Usage:
    python dataverse/list_tables.py
"""

import asyncio
import sys
import httpx
from typing import List, Dict, Any, Optional

from utils.config import get_config
from utils.logger import get_logger, setup_logging
from auth.graph import get_auth_manager

logger = get_logger(__name__)


async def get_dataverse_tables(impersonate_user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get actual tables from Dataverse using Web API.
    
    Args:
        impersonate_user_id: Optional user ID to impersonate for audit attribution
    """
    try:
        config = get_config()
        auth_manager = get_auth_manager()

        # Ensure credential is created by getting the client first
        auth_manager.get_client()

        # Get a fresh token for Dataverse (use Dataverse environment scope)
        credential = auth_manager._credential
        dataverse_url = config.dataverse_url.rstrip('/')
        token = credential.get_token(f"{dataverse_url}/.default")

        # Dataverse Web API endpoint for entities
        api_url = f"{dataverse_url}/api/data/v9.2/EntityDefinitions"

        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0',
            'Prefer': 'return=representation,odata.include-annotations="*"'
        }
        
        # Add impersonation header if user ID provided
        if impersonate_user_id:
            headers['MSCRMCallerID'] = impersonate_user_id
            logger.info(f"Impersonating user: {impersonate_user_id}")

        logger.info(f"Calling Dataverse Web API: {api_url}")
        logger.info(f"Using token scope: {dataverse_url}/.default")

        async with httpx.AsyncClient(timeout=60.0) as client:  # 60 second timeout
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
        logger.error(f"Failed to get Dataverse tables: {e}")
        return []

async def list_dataverse_tables(impersonate_user_id: Optional[str] = None) -> bool:
    """
    Lists all tables in Dataverse using Web API.
    
    Args:
        impersonate_user_id: Optional user ID to impersonate for audit attribution
    """
    try:
        tables = await get_dataverse_tables(impersonate_user_id)
        
        if tables:
            print(f"📊 Found {len(tables)} user entities in Dataverse:")
            
            # Group by entity type
            custom_entities = [t for t in tables if t['entity_type'] == 'Custom']
            standard_entities = [t for t in tables if t['entity_type'] == 'Standard']
            
            if custom_entities:
                print(f"\n🔧 Custom Entities ({len(custom_entities)}):")
                for table in custom_entities[:10]:  # Show first 10
                    print(f"  • {table['display_name']} ({table['name']})")
                if len(custom_entities) > 10:
                    print(f"  ... and {len(custom_entities) - 10} more")
            
            if standard_entities:
                print(f"\n📋 Standard Entities ({len(standard_entities)}):")
                for table in standard_entities[:5]:  # Show first 5
                    print(f"  • {table['display_name']} ({table['name']})")
                if len(standard_entities) > 5:
                    print(f"  ... and {len(standard_entities) - 5} more")
            
            print(f"\n💡 Total: {len(tables)} entities available")
            return True
        else:
            print("⚠️ No tables found or connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_dataverse_connection(impersonate_user_id: Optional[str] = None) -> bool:
    """
    Test Dataverse connection with optional user impersonation.
    
    Args:
        impersonate_user_id: Optional user ID to impersonate for audit attribution
    """
    try:
        config = get_config()
        auth_manager = get_auth_manager()

        # Ensure credential is created by getting the client first
        auth_manager.get_client()
        
        # Get token for Dataverse
        credential = auth_manager._credential
        dataverse_url = config.dataverse_url.rstrip('/')
        token = credential.get_token(f"{dataverse_url}/.default")

        # Test endpoint - WhoAmI
        api_url = f"{dataverse_url}/api/data/v9.2/WhoAmI"

        headers = {
            'Authorization': f'Bearer {token.token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'OData-MaxVersion': '4.0',
            'OData-Version': '4.0'
        }
        
        if impersonate_user_id:
            headers['MSCRMCallerID'] = impersonate_user_id

        logger.info(f"Testing Dataverse connection: {api_url}")

        async with httpx.AsyncClient(timeout=30.0) as client:  # 30 second timeout
            response = await client.get(api_url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                user_id = data.get('UserId', 'Unknown')
                business_unit_id = data.get('BusinessUnitId', 'Unknown')
                
                logger.info(f"✅ Dataverse connection successful!")
                logger.info(f"   User ID: {user_id}")
                logger.info(f"   Business Unit ID: {business_unit_id}")
                
                if impersonate_user_id:
                    logger.info(f"   Impersonating: {impersonate_user_id}")
                
                return True
            else:
                logger.error(f"❌ Dataverse connection failed: {response.status_code} - {response.text}")
                return False

    except Exception as e:
        logger.error(f"❌ Dataverse connection error: {e}")
        return False

async def main():
    """Main function for testing Dataverse connection."""
    print("🔍 Testing Dataverse connection...")
    
    # Test basic connection
    success = await test_dataverse_connection()
    
    if success:
        print("✅ Dataverse connection successful!")
        print("   Ready for data operations")
        
        # Test getting tables
        await list_dataverse_tables()
    else:
        print("❌ Dataverse connection failed")
        print("   Check environment configuration")

if __name__ == "__main__":
    asyncio.run(main())
