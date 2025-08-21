# Dataverse Module API

The `dataverse` module provides Dataverse Web API integration for data operations.

## 📚 Overview

The Dataverse module handles:
- Dataverse Web API authentication
- Entity (table) operations
- Data querying and manipulation
- Connection testing and diagnostics

## 🔧 Dev Layer (sync) and CLI

The new dev layer is synchronous (terminal-first) with OData-correct primitives and optional impersonation.

### Dev Layer Functions (sync)
- `whoami(impersonate: str|None=None) -> dict`
- `entity_def(logical_name: str) -> dict  # {EntitySetName, PrimaryIdAttribute, PrimaryNameAttribute}`
- `entity_set(logical_name: str) -> str`
- `get(entity_set: str, id: str, select: str|None=None, expand: str|None=None) -> dict`
- `query(entity_set: str, filter: str="", select: str="", top: int=10) -> dict  # contains @odata.count`
- `create(entity_set: str, payload: dict, *, impersonate: str|None=None) -> dict  # {id}`
- `update(entity_set: str, id: str, payload: dict, *, impersonate: str|None=None) -> None`
- `delete(entity_set: str, id: str, *, impersonate: str|None=None) -> None`
- `create_note(regarding_logical: str, regarding_id: str, subject: str, notetext: str, *, impersonate: str|None=None) -> dict`
- `find_user_systemuserid(upn_or_domainname: str) -> str`
- `probe() -> dict  # token, whoami, metadata`

### CLI Verbs

```bash
# Probe
python blc.py dataverse probe

# Identity
python blc.py dataverse whoami [--as-user <systemuserid>]

# Entity metadata
python blc.py dataverse entity-def <logical_name>

# Records
python blc.py dataverse get <logical_name> <guid> [--select "..."] [--expand "..."]
python blc.py dataverse query <logical_name> [--filter "..."] [--select "..."] [--top 20]

# Write (use with care)
python blc.py dataverse create <logical_name> --data-file payload.json [--as-user <systemuserid>]
python blc.py dataverse update <logical_name> <guid> --data-file payload.json [--as-user <systemuserid>]
python blc.py dataverse delete <logical_name> <guid> [--as-user <systemuserid>]
python blc.py dataverse note <logical_name> <guid> --subject "..." --body-file note.md [--as-user <systemuserid>]
```

## 🔐 Authentication

### Token Acquisition
The module uses the same authentication as Graph API but with Dataverse-specific scopes:

```python
from auth.graph import get_auth_manager

auth_manager = get_auth_manager()
credential = auth_manager._credential

# Get token for Dataverse (different scope)
dataverse_url = config.dataverse_url.rstrip('/')
token = credential.get_token(f"{dataverse_url}/.default")
```

### Required Permissions
- **Dataverse Environment Access**: Service principal must be added as user
- **Security Roles**: Appropriate Dataverse security roles assigned
- **API Permissions**: Dataverse permissions in Azure AD (if applicable)

## 🌐 API Endpoints

### Entity Definitions
```
GET {dataverse_url}/api/data/v9.2/EntityDefinitions
```

**Headers:**
```python
headers = {
    'Authorization': f'Bearer {token.token}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'OData-MaxVersion': '4.0',
    'OData-Version': '4.0'
}
```

### Response Format
```json
{
    "value": [
        {
            "LogicalName": "account",
            "DisplayName": {
                "UserLocalizedLabel": {
                    "Label": "Account"
                }
            },
            "Description": {
                "UserLocalizedLabel": {
                    "Label": "Business that represents a customer or potential customer"
                }
            },
            "IsCustomEntity": false
        }
    ]
}
```

## 🚨 Error Handling

### Common HTTP Status Codes

#### 401 Unauthorized
**Causes:**
- Invalid or expired token
- Wrong token scope
- Missing authentication headers

**Solutions:**
```python
# Verify token scope
token = credential.get_token(f"{dataverse_url}/.default")
print(f"Token scope: {dataverse_url}/.default")
```

#### 403 Forbidden
**Causes:**
- Service principal not added to Dataverse
- Insufficient security roles
- Wrong Dataverse URL

**Solutions:**
1. Add service principal to Dataverse environment
2. Assign appropriate security roles
3. Verify Dataverse URL

#### 404 Not Found
**Causes:**
- Invalid API endpoint
- Wrong API version
- Dataverse environment not accessible

**Solutions:**
```python
# Verify endpoint
api_url = f"{dataverse_url}/api/data/v9.2/EntityDefinitions"
print(f"Calling: {api_url}")
```

## 📝 Usage Examples

### Basic Table Listing
```python
import asyncio
from dataverse.list_tables import get_dataverse_tables

async def basic_listing():
    try:
        tables = await get_dataverse_tables()
        
        if tables:
            print(f"📊 Found {len(tables)} tables in Dataverse:")
            for table in tables[:10]:  # Show first 10
                print(f"  • {table['display_name']} ({table['name']})")
                print(f"    Type: {table['entity_type']}")
                if table['description']:
                    print(f"    Description: {table['description']}")
                print()
        else:
            print("⚠️ No tables found or connection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(basic_listing())
```

### Filter Custom Entities
```python
import asyncio
from dataverse.list_tables import get_dataverse_tables

async def custom_entities():
    tables = await get_dataverse_tables()
    
    # Filter for custom entities only
    custom_tables = [t for t in tables if t['entity_type'] == 'Custom']
    
    print(f"🔧 Custom entities ({len(custom_tables)}):")
    for table in custom_tables:
        print(f"  • {table['display_name']} ({table['name']})")

asyncio.run(custom_entities())
```

### Connection Testing
```python
import asyncio
from dataverse.list_tables import list_dataverse_tables

async def test_connection():
    print("🔍 Testing Dataverse connection...")
    
    success = await list_dataverse_tables()
    
    if success:
        print("✅ Dataverse connection successful!")
        print("   Ready for data operations")
    else:
        print("❌ Dataverse connection failed")
        print("   Check environment configuration")

asyncio.run(test_connection())
```

## 🔍 Debugging & Troubleshooting

### Enable HTTP Debugging
```python
import httpx
import asyncio
from dataverse.list_tables import get_dataverse_tables

async def debug_request():
    # Enable debug logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        tables = await get_dataverse_tables()
        print(f"Success: {len(tables)} tables")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(debug_request())
```

### Troubleshooting Guide

See `docs/dataverse-troubleshooting.md` for common fixes (timeouts, 401/403/404, rate limiting) and probes.

### Token Debugging
```python
from auth.graph import get_auth_manager
from utils.config import get_config

async def debug_token():
    auth_manager = get_auth_manager()
    config = get_config()
    
    # Get token details
    credential = auth_manager._credential
    dataverse_url = config.dataverse_url.rstrip('/')
    token = credential.get_token(f"{dataverse_url}/.default")
    
    print(f"Token scope: {dataverse_url}/.default")
    print(f"Token expires: {token.expires_on}")
    print(f"Token type: {type(token)}")

asyncio.run(debug_token())
```

### URL Verification
```python
from utils.config import get_config

def verify_urls():
    config = get_config()
    
    print(f"Dataverse URL: {config.dataverse_url}")
    print(f"API Endpoint: {config.dataverse_url.rstrip('/')}/api/data/v9.2/EntityDefinitions")
    
    # Test URL format
    if not config.dataverse_url.startswith('https://'):
        print("⚠️ Warning: Dataverse URL should use HTTPS")
    
    if 'crm.dynamics.com' not in config.dataverse_url:
        print("⚠️ Warning: URL doesn't look like a Dataverse environment")

verify_urls()
```

## 🔄 Notes on Async

Core dev-layer operations are synchronous for terminal ergonomics. For async contexts (e.g., FastAPI handlers), wrap calls in threads or create an async variant using `httpx.AsyncClient` with the same OData semantics.

## 📊 Configuration

### Required Environment Variables

```bash
# Dataverse Configuration
DATAVERSE_URL=https://your-org.crm.dynamics.com

# Azure AD Configuration (for authentication)
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here
AZURE_TENANT_ID=your_tenant_id_here
```

### Dataverse Environment Setup

1. **Add Service Principal as User:**
   - Go to Dataverse environment
   - Settings → Security → Users
   - Add new user with service principal email
   - Assign appropriate security roles

2. **Verify Security Roles:**
   - System Administrator (for full access)
   - System Customizer (for custom entities)
   - Basic User (for read access)

## 🚀 Future Enhancements

### Planned Features
- **CRUD Operations**: Create, read, update, delete records
- **Query Builder**: Advanced filtering and querying
- **Batch Operations**: Bulk data operations
- **Change Tracking**: Monitor data changes
- **Relationship Management**: Handle entity relationships

### Example Future Usage
```python
# Future CRUD operations
from dataverse.operations import DataverseClient

client = DataverseClient()

# Create record
record = await client.create_record(
    entity_name="account",
    data={"name": "New Account", "telephone1": "555-0123"}
)

# Query records
accounts = await client.query_records(
    entity_name="account",
    filter="name eq 'New Account'"
)

# Update record
await client.update_record(
    entity_name="account",
    record_id=record["accountid"],
    data={"telephone1": "555-0124"}
)
```

## 📊 Dependencies

### Required Packages
- `httpx>=0.25.0` - HTTP client for API calls
- `azure-identity>=1.15.0` - Azure authentication
- `pydantic>=2.5.0` - Configuration validation

### Optional Packages
- `structlog>=23.2.0` - Structured logging

---

*Last Updated: August 20, 2025*
*API Version: 1.0.0*
