# Authentication Module API

The `auth` module provides Microsoft Graph API authentication and client management.

## 📚 Overview

The authentication module handles:
- Azure AD client credentials flow
- Microsoft Graph API client creation
- Token management and validation
- Connection testing and diagnostics

## 🔧 Classes

### `GraphAuthManager`

Main authentication manager for Microsoft Graph API.

#### Constructor
```python
GraphAuthManager()
```

Creates a new authentication manager instance using environment configuration.

#### Attributes

- `config: Settings` - Application configuration
- `_credential: ClientSecretCredential` - Azure credential instance
- `_client: Optional[GraphServiceClient]` - Cached Graph client

#### Methods

##### `get_client() -> GraphServiceClient`
Returns an authenticated Microsoft Graph service client.

**Returns:**
- `GraphServiceClient`: Authenticated Graph API client

**Example:**
```python
auth_manager = GraphAuthManager()
client = auth_manager.get_client()
users = await client.users.get()
```

##### `test_basic_auth() -> bool`
Tests basic authentication without requiring specific API permissions.

**Returns:**
- `bool`: True if authentication succeeds, False otherwise

**Example:**
```python
auth_manager = GraphAuthManager()
if auth_manager.test_basic_auth():
    print("✅ Basic authentication successful!")
```

##### `test_connection() -> bool`
Tests full Graph API connectivity with organization access.

**Returns:**
- `bool`: True if connection succeeds, False otherwise

**Example:**
```python
auth_manager = GraphAuthManager()
success = await auth_manager.test_connection()
if success:
    print("🎉 Graph API connection successful!")
```

##### `test_token_permissions() -> bool`
Tests what permissions are actually granted in the token.

**Returns:**
- `bool`: True if token has expected permissions, False otherwise

**Example:**
```python
auth_manager = GraphAuthManager()
success = await auth_manager.test_token_permissions()
if success:
    print("✅ Token permissions verified!")
```

##### `get_current_user() -> Optional[dict]`
Gets current user information (limited with client credentials flow).

**Returns:**
- `Optional[dict]`: User information or None if not available

**Note:** This method is limited with client credentials flow as there's no specific user context.

## 🔧 Functions

### `get_auth_manager() -> GraphAuthManager`
Returns the global authentication manager instance (singleton pattern).

**Returns:**
- `GraphAuthManager`: Global authentication manager instance

**Example:**
```python
from auth.graph import get_auth_manager

auth_manager = get_auth_manager()
client = auth_manager.get_client()
```

### `test_graph_connection() -> bool`
Legacy function for testing Graph API connection.

**Returns:**
- `bool`: True if connection succeeds, False otherwise

**Example:**
```python
from auth.graph import test_graph_connection

success = await test_graph_connection()
print(f"Connection test: {'✅' if success else '❌'}")
```

### `get_graph_client() -> GraphServiceClient`
Returns authenticated Graph service client.

**Returns:**
- `GraphServiceClient`: Authenticated Graph API client

**Example:**
```python
from auth.graph import get_graph_client

client = get_graph_client()
users = await client.users.get()
```

## 🔐 Configuration

### Required Environment Variables

```bash
# Azure AD Application Configuration
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here
AZURE_TENANT_ID=your_tenant_id_here

# Graph API Scopes
GRAPH_SCOPES=https://graph.microsoft.com/.default
```

### Azure AD App Registration Requirements

1. **Application Type**: Web app or API
2. **Authentication**: Client credentials flow
3. **API Permissions**: Application permissions (not Delegated)
   - `Organization.Read.All`
   - `User.Read.All`
   - `Application.Read.All` (optional)

## 🚨 Error Handling

### Common Exceptions

#### `ValueError`
Raised when configuration validation fails.

**Causes:**
- Missing required environment variables
- Invalid Azure AD credentials

**Example:**
```python
try:
    auth_manager = GraphAuthManager()
except ValueError as e:
    print(f"Configuration error: {e}")
```

#### `CredentialUnavailableError`
Raised when Azure credentials are invalid or expired.

**Causes:**
- Invalid client ID/secret
- Expired client secret
- Wrong tenant ID

**Example:**
```python
from azure.core.exceptions import CredentialUnavailableError

try:
    client = auth_manager.get_client()
except CredentialUnavailableError as e:
    print(f"Credential error: {e}")
```

#### `GraphError`
Raised when Microsoft Graph API calls fail.

**Causes:**
- Insufficient permissions
- Invalid API calls
- Network issues

**Example:**
```python
from msgraph.core import GraphError

try:
    users = await client.users.get()
except GraphError as e:
    print(f"Graph API error: {e}")
```

## 📝 Usage Examples

### Basic Authentication Test
```python
import asyncio
from auth.graph import get_auth_manager

async def test_auth():
    auth_manager = get_auth_manager()
    
    # Test basic auth
    if auth_manager.test_basic_auth():
        print("✅ Basic authentication successful!")
    
    # Test full connection
    if await auth_manager.test_connection():
        print("🎉 Full connection successful!")
    else:
        print("❌ Connection failed")

asyncio.run(test_auth())
```

### Get Users from Graph API
```python
import asyncio
from auth.graph import get_auth_manager

async def get_users():
    auth_manager = get_auth_manager()
    client = auth_manager.get_client()
    
    try:
        users = await client.users.get()
        print(f"Found {len(users.value)} users:")
        for user in users.value[:5]:  # Show first 5
            print(f"  • {user.display_name} ({user.user_principal_name})")
    except Exception as e:
        print(f"Error getting users: {e}")

asyncio.run(get_users())
```

### Organization Information
```python
import asyncio
from auth.graph import get_auth_manager

async def get_org_info():
    auth_manager = get_auth_manager()
    client = auth_manager.get_client()
    
    try:
        org = await client.organization.get()
        if org and org.value:
            org_info = org.value[0]
            print(f"🏢 Organization: {org_info.display_name}")
            print(f"   ID: {org_info.id}")
            print(f"   Phone: {org_info.business_phones[0] if org_info.business_phones else 'N/A'}")
    except Exception as e:
        print(f"Error getting org info: {e}")

asyncio.run(get_org_info())
```

## 🔍 Debugging

### Enable Debug Logging
```python
import logging
from auth.graph import get_auth_manager

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

auth_manager = get_auth_manager()
```

### Token Inspection
```python
from auth.graph import get_auth_manager

auth_manager = get_auth_manager()
credential = auth_manager._credential

# Get token details
token = credential.get_token("https://graph.microsoft.com/.default")
print(f"Token expires: {token.expires_on}")
print(f"Token type: {type(token)}")
```

### Permission Testing
```python
import asyncio
from auth.graph import get_auth_manager

async def test_permissions():
    auth_manager = get_auth_manager()
    
    # Test specific permissions
    success = await auth_manager.test_token_permissions()
    if success:
        print("✅ All required permissions are available")
    else:
        print("❌ Some permissions are missing")

asyncio.run(test_permissions())
```

## 🔄 Async Support

All methods that make HTTP requests are async and must be awaited:

```python
import asyncio
from auth.graph import get_auth_manager

async def main():
    auth_manager = get_auth_manager()
    
    # These are async methods
    success = await auth_manager.test_connection()
    client = auth_manager.get_client()
    users = await client.users.get()

# Run async function
asyncio.run(main())
```

## 📊 Dependencies

### Required Packages
- `azure-identity>=1.15.0` - Azure authentication
- `msgraph-sdk>=1.0.0` - Microsoft Graph SDK
- `pydantic>=2.5.0` - Configuration validation

### Optional Packages
- `structlog>=23.2.0` - Structured logging (if using logging)

---

*Last Updated: August 20, 2025*
*API Version: 1.0.0*
