#!/usr/bin/env python3
"""
Dataverse table listing and management.

Provides functionality to list and manage Dataverse tables/entities.
"""

import asyncio
from typing import List, Dict, Any, Optional

from auth.dataverse import DataverseAuthManager
from utils.logger import get_logger

logger = get_logger(__name__)


async def test_dataverse_connection(impersonate_user_id: Optional[str] = None) -> bool:
    """Test Dataverse connection using WhoAmI endpoint."""
    try:
        auth_manager = DataverseAuthManager()
        return await auth_manager.test_connection(impersonate_user_id)
    except Exception as e:
        logger.error(f"Dataverse connection test failed: {e}")
        return False


async def get_dataverse_tables(impersonate_user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all Dataverse tables/entities."""
    try:
        auth_manager = DataverseAuthManager()
        return await auth_manager.get_entity_definitions(impersonate_user_id)
    except Exception as e:
        logger.error(f"Failed to get Dataverse tables: {e}")
        return []


async def list_dataverse_tables(impersonate_user_id: Optional[str] = None) -> bool:
    """List Dataverse tables with formatted output."""
    tables = await get_dataverse_tables(impersonate_user_id)
    
    if tables:
        print(f"📊 Found {len(tables)} user entities in Dataverse:")
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


async def main():
    """Main function to orchestrate Dataverse tests."""
    print("🧪 Testing Dataverse Integration")
    print("=" * 40)
    
    # Test 1: Basic connection
    print("\n1️⃣ Testing Dataverse connection...")
    if await test_dataverse_connection():
        print("✅ Connection successful!")
    else:
        print("❌ Connection failed!")
        return
    
    # Test 2: List tables
    print("\n2️⃣ Listing Dataverse tables...")
    await list_dataverse_tables()


if __name__ == "__main__":
    asyncio.run(main())
