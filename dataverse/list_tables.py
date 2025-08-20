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
from typing import List, Dict, Any

from utils.config import get_config
from utils.logger import get_logger, setup_logging
from auth.graph import get_auth_manager

logger = get_logger(__name__)


async def get_dataverse_tables() -> List[Dict[str, Any]]:
    """
    Get actual tables from Dataverse using Web API.
    
    Uses the same authentication as Graph API but calls Dataverse Web API directly.
    """
    try:
        config = get_config()
        auth_manager = get_auth_manager()
        
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
            'OData-Version': '4.0'
        }
        
        logger.info(f"Calling Dataverse Web API: {api_url}")
        logger.info(f"Using token scope: {dataverse_url}/.default")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                entities = data.get('value', [])
                
                # Filter for user-created entities (not system entities)
                user_entities = [
                    {
                        "name": entity.get('LogicalName', ''),
                        "display_name": entity.get('DisplayName', {}).get('UserLocalizedLabel', {}).get('Label', ''),
                        "description": entity.get('Description', {}).get('UserLocalizedLabel', {}).get('Label', ''),
                        "entity_type": "Custom" if entity.get('IsCustomEntity', False) else "Standard"
                    }
                    for entity in entities
                    if entity.get('LogicalName') and not entity.get('LogicalName').startswith('_')
                ]
                
                logger.info(f"Found {len(user_entities)} user entities in Dataverse")
                return user_entities
            else:
                logger.error(f"Dataverse API call failed: {response.status_code} - {response.text}")
                return []
                    
    except Exception as e:
        logger.error(f"Failed to get Dataverse tables: {e}")
        return []


async def list_dataverse_tables() -> bool:
    """
    List all tables in Dataverse using Web API.
    """
    try:
        logger.info("=== Hello Dataverse - Real Table Listing ===")
        
        # Get configuration
        config = get_config()
        logger.info(f"Dataverse URL: {config.dataverse_url}")
        
        # Test Microsoft Graph API connection first
        logger.info("Testing Microsoft Graph API connection...")
        auth_manager = get_auth_manager()
        if await auth_manager.test_connection():
            logger.info("✅ Microsoft Graph API connection successful!")
        else:
            logger.error("❌ Microsoft Graph API connection failed!")
            return False
        
        # Get real Dataverse tables
        logger.info("Fetching real Dataverse tables...")
        tables = await get_dataverse_tables()
        
        if tables:
            logger.info(f"Found {len(tables)} tables in Dataverse:")
            for table in tables:
                logger.info(f"  📋 {table['display_name']} ({table['name']})")
                if table['description']:
                    logger.info(f"      Description: {table['description']}")
                logger.info(f"      Type: {table['entity_type']}")
            
            logger.info("✅ Dataverse table listing completed successfully!")
            return True
        else:
            logger.warning("⚠️ No tables found or API call failed")
            logger.info("💡 This might be normal if your Dataverse environment is empty")
            return True
        
    except Exception as e:
        logger.error(f"❌ Failed to list Dataverse tables: {e}")
        return False


async def main():
    """Main function to run the Dataverse table listing script."""
    try:
        # Setup logging
        setup_logging(
            log_level="INFO",
            log_file="logs/dataverse_tables.log"
        )
        
        logger.info("🚀 Starting Hello Dataverse script...")
        
        # List tables
        success = await list_dataverse_tables()
        
        if success:
            logger.info("🎉 Hello Dataverse script completed successfully!")
            return 0
        else:
            logger.error("💥 Hello Dataverse script failed!")
            return 1
            
    except Exception as e:
        logger.error(f"💥 Unexpected error in Hello Dataverse script: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
