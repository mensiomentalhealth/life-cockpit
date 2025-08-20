# API Reference

This document provides a comprehensive reference for the Life Cockpit API modules and their interfaces.

## 📚 Module Overview

### Core Modules
- **`auth/`** - Microsoft Graph API authentication
- **`dataverse/`** - Dataverse operations and data access
- **`utils/`** - Shared utilities (config, logging)
- **`blc.py`** - CLI entry point

## 🔐 Authentication Module (`auth/`)

### `auth.graph.GraphAuthManager`

Main authentication manager for Microsoft Graph API.

#### Constructor
```python
GraphAuthManager()
```
Creates a new authentication manager instance.

#### Methods

##### `get_client() -> GraphServiceClient`
Returns an authenticated Microsoft Graph service client.

##### `test_basic_auth() -> bool`
Tests basic authentication without requiring specific API permissions.

##### `test_connection() -> bool`
Tests full Graph API connectivity with organization access.

##### `test_token_permissions() -> bool`
Tests what permissions are actually granted in the token.

##### `get_current_user() -> Optional[dict]`
Gets current user information (limited with client credentials flow).

### `auth.dataverse.DataverseAuthManager`

Main authentication manager for Dataverse Web API.

#### Constructor
```python
DataverseAuthManager()
```
Creates a new Dataverse authentication manager instance.

#### Methods

##### `get_credential() -> ClientSecretCredential`
Returns the Azure credential for authentication.

##### `get_dataverse_url() -> str`
Returns the configured Dataverse environment URL.

##### `get_token(impersonate_user_id: Optional[str] = None) -> str`
Gets access token for Dataverse API with optional user impersonation.

**Parameters:**
- `impersonate_user_id`: Optional user ID for audit attribution

##### `test_connection(impersonate_user_id: Optional[str] = None) -> bool`
Tests Dataverse API connection using WhoAmI endpoint.

**Parameters:**
- `impersonate_user_id`: Optional user ID for audit attribution

##### `get_entity_definitions(impersonate_user_id: Optional[str] = None) -> List[Dict[str, Any]]`
Gets all entity definitions from Dataverse.

**Parameters:**
- `impersonate_user_id`: Optional user ID for audit attribution

**Returns:**
- List of entity dictionaries with keys: `name`, `display_name`, `description`, `entity_type`

### `auth.graph.get_auth_manager() -> GraphAuthManager`
Returns the global authentication manager instance (singleton).

### `auth.graph.test_graph_connection() -> bool`
Legacy function for testing Graph API connection.

### `auth.graph.get_graph_client() -> GraphServiceClient`
Returns authenticated Graph service client.

## 📊 Dataverse Module (`dataverse/`)

### `dataverse.list_tables.test_dataverse_connection(impersonate_user_id: Optional[str] = None) -> bool`
Tests Dataverse connection using WhoAmI endpoint.

**Parameters:**
- `impersonate_user_id`: Optional user ID for audit attribution

**Returns:**
- `True` if connection successful, `False` if failed

### `dataverse.list_tables.get_dataverse_tables(impersonate_user_id: Optional[str] = None) -> List[Dict[str, Any]]`
Gets all Dataverse tables/entities using the centralized auth manager.

**Parameters:**
- `impersonate_user_id`: Optional user ID for audit attribution

**Returns:**
- List of table dictionaries with keys: `name`, `display_name`, `description`, `entity_type`

### `dataverse.list_tables.list_dataverse_tables(impersonate_user_id: Optional[str] = None) -> bool`
Lists all tables in Dataverse with formatted output.

**Parameters:**
- `impersonate_user_id`: Optional user ID for audit attribution

**Returns:**
- `True` if successful, `False` if failed

**Note:** This function prints formatted output to console showing custom and standard entities.

## ⚙️ Utilities Module (`utils/`)

### `utils.config.Settings`
Pydantic settings class for application configuration.

#### Fields
- `azure_client_id: str` - Azure AD application client ID
- `azure_client_secret: str` - Azure AD application client secret
- `azure_tenant_id: str` - Azure AD tenant ID
- `graph_scopes: str` - Microsoft Graph API scopes
- `dataverse_url: str` - Dataverse environment URL
- `log_level: str` - Logging level (default: "INFO")
- `log_file: Optional[str]` - Log file path
- `app_name: str` - Application name (default: "life-cockpit")
- `app_version: str` - Application version (default: "1.0.0")

### `utils.config.get_config() -> Settings`
Returns validated configuration instance.

### `utils.config.get_azure_config() -> dict`
Returns Azure configuration as a dictionary.

### `utils.config.get_dataverse_config() -> dict`
Returns Dataverse configuration as a dictionary.

### `utils.config.get_logging_config() -> dict`
Returns logging configuration as a dictionary.

### `utils.logger.get_logger(name: str) -> Logger`
Returns a structured logger instance.

### `utils.logger.setup_logging(log_level: str, log_file: Optional[str]) -> None`
Sets up logging configuration.

## 🖥️ CLI Interface (`blc.py`)

### Main Commands

#### `version`
Shows Life Cockpit version with rich panel display.

#### `auth <action>`
Authentication management commands.

**Actions:**
- `test` - Test Microsoft Graph API authentication
- `status` - Check authentication status and token info

#### `graph <action>`
Microsoft Graph API operations.

**Actions:**
- `users` - List users from Microsoft Graph
- `org` - Show organization information

#### `dataverse <action>`
Dataverse operations.

**Actions:**
- `list` - List Dataverse tables
- `test` - Test Dataverse connection

## 🔧 Configuration

### Environment Variables

Required environment variables (set in `.env` file):

```bash
# Microsoft Graph API Configuration
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here
AZURE_TENANT_ID=your_tenant_id_here

# Dataverse Configuration
DATAVERSE_URL=https://your-org.crm.dynamics.com

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/cockpit.log

# Application Configuration
APP_NAME=life-cockpit
APP_VERSION=1.0.0
```

## 🚨 Error Handling

### Common Exceptions

#### `ValueError`
Raised when configuration validation fails.

#### `ModuleNotFoundError`
Raised when Python path is not set correctly.

#### `GraphError`
Raised when Microsoft Graph API calls fail.

### Error Codes

- **403 Forbidden**: Permission denied (check Azure AD permissions)
- **404 Not Found**: Resource not found
- **401 Unauthorized**: Authentication failed

## 📝 Usage Examples

### Basic Authentication
```python
from auth.graph import get_auth_manager

auth_manager = get_auth_manager()
client = auth_manager.get_client()
```

### Configuration Access
```python
from utils.config import get_config

config = get_config()
print(f"App: {config.app_name} v{config.app_version}")
```

### Logging
```python
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Application started")
```

### CLI Usage
```bash
# Test authentication
python blc.py auth test

# List users
python blc.py graph users

# Test Dataverse
python blc.py dataverse test
```

## 🔄 Async Support

All API methods that make HTTP requests are async and should be awaited:

```python
import asyncio
from auth.graph import get_auth_manager

async def main():
    auth_manager = get_auth_manager()
    success = await auth_manager.test_connection()
    print(f"Connection: {'✅' if success else '❌'}")

asyncio.run(main())
```

## 📊 Dependencies

### Core Dependencies
- `azure-identity>=1.15.0` - Azure authentication
- `msgraph-sdk>=1.0.0` - Microsoft Graph SDK
- `python-dotenv>=1.0.0` - Environment configuration
- `pydantic>=2.5.0` - Configuration validation
- `httpx>=0.25.0` - HTTP client
- `typer>=0.9.0` - CLI framework
- `rich>=13.7.0` - Rich output
- `structlog>=23.2.0` - Structured logging

---

*Last Updated: August 20, 2025*
*API Version: 1.0.0*
