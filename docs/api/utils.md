# Utilities Module API

The `utils` module provides shared utilities for configuration management and logging.

## 📚 Overview

The utilities module includes:
- **Configuration Management**: Environment-based settings with validation
- **Logging**: Structured logging with file rotation
- **Common Utilities**: Shared helper functions

## 🔧 Configuration Module (`utils.config`)

### `Settings` Class

Pydantic settings class for application configuration.

#### Constructor
```python
Settings()
```

Creates a new settings instance, loading values from environment variables.

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `azure_client_id` | `str` | Required | Azure AD application client ID |
| `azure_client_secret` | `str` | Required | Azure AD application client secret |
| `azure_tenant_id` | `str` | Required | Azure AD tenant ID |
| `graph_scopes` | `str` | `"https://graph.microsoft.com/.default"` | Microsoft Graph API scopes |
| `dataverse_url` | `str` | Required | Dataverse environment URL |
| `log_level` | `str` | `"INFO"` | Logging level |
| `log_file` | `Optional[str]` | `None` | Log file path |
| `app_name` | `str` | `"life-cockpit"` | Application name |
| `app_version` | `str` | `"1.0.0"` | Application version |

#### Example
```python
from utils.config import Settings

# Create settings instance
settings = Settings()

print(f"App: {settings.app_name} v{settings.app_version}")
print(f"Log Level: {settings.log_level}")
```

### Functions

#### `get_config() -> Settings`
Returns validated configuration instance.

**Returns:**
- `Settings`: Validated configuration object

**Example:**
```python
from utils.config import get_config

config = get_config()
print(f"Azure Tenant: {config.azure_tenant_id}")
```

#### `get_azure_config() -> dict`
Returns Azure configuration as a dictionary.

**Returns:**
- `dict`: Azure configuration dictionary

**Example:**
```python
from utils.config import get_azure_config

azure_config = get_azure_config()
print(f"Client ID: {azure_config['client_id']}")
```

#### `get_dataverse_config() -> dict`
Returns Dataverse configuration as a dictionary.

**Returns:**
- `dict`: Dataverse configuration dictionary

**Example:**
```python
from utils.config import get_dataverse_config

dv_config = get_dataverse_config()
print(f"Dataverse URL: {dv_config['url']}")
```

#### `get_logging_config() -> dict`
Returns logging configuration as a dictionary.

**Returns:**
- `dict`: Logging configuration dictionary

**Example:**
```python
from utils.config import get_logging_config

log_config = get_logging_config()
print(f"Log Level: {log_config['level']}")
```

## 📝 Logging Module (`utils.logger`)

### `get_logger(name: str) -> Logger`
Returns a structured logger instance.

**Parameters:**
- `name: str` - Logger name (usually `__name__`)

**Returns:**
- `Logger`: Structured logger instance

**Example:**
```python
from utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Application started")
logger.error("Something went wrong", extra={"error_code": 500})
```

### `setup_logging(log_level: str, log_file: Optional[str]) -> None`
Sets up logging configuration.

**Parameters:**
- `log_level: str` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file: Optional[str]` - Log file path (optional)

**Example:**
```python
from utils.logger import setup_logging

# Setup logging
setup_logging(log_level="DEBUG", log_file="logs/app.log")
```

## 🔧 Configuration Examples

### Basic Configuration Usage
```python
from utils.config import get_config
from utils.logger import get_logger

# Get configuration
config = get_config()

# Setup logging
logger = get_logger(__name__)

# Use configuration
logger.info(f"Starting {config.app_name} v{config.app_version}")
logger.info(f"Log level: {config.log_level}")
logger.info(f"Dataverse URL: {config.dataverse_url}")
```

### Environment Variable Validation
```python
from utils.config import Settings

try:
    settings = Settings()
    print("✅ Configuration loaded successfully")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("Please check your .env file")
```

### Configuration Access Patterns
```python
from utils.config import get_config, get_azure_config, get_dataverse_config

# Get full config
config = get_config()

# Get specific configs
azure_config = get_azure_config()
dv_config = get_dataverse_config()

# Access values
print(f"Azure Client ID: {azure_config['client_id']}")
print(f"Dataverse URL: {dv_config['url']}")
print(f"App Name: {config.app_name}")
```

## 📝 Logging Examples

### Basic Logging
```python
from utils.logger import get_logger

logger = get_logger(__name__)

# Different log levels
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Structured Logging
```python
from utils.logger import get_logger

logger = get_logger(__name__)

# Log with extra context
logger.info("User action", extra={
    "user_id": "123",
    "action": "login",
    "ip_address": "192.168.1.1"
})

# Log errors with context
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed", extra={
        "operation": "risky_operation",
        "error": str(e),
        "user_id": "123"
    })
```

### Logging Setup
```python
from utils.logger import setup_logging, get_logger

# Setup logging first
setup_logging(
    log_level="INFO",
    log_file="logs/cockpit.log"
)

# Then get logger
logger = get_logger(__name__)
logger.info("Logging system initialized")
```

## 🔍 Debugging Configuration

### Configuration Validation
```python
from utils.config import get_config

def validate_config():
    try:
        config = get_config()
        
        # Check required fields
        required_fields = [
            'azure_client_id',
            'azure_client_secret', 
            'azure_tenant_id',
            'dataverse_url'
        ]
        
        for field in required_fields:
            value = getattr(config, field)
            if not value:
                print(f"❌ Missing required field: {field}")
            else:
                print(f"✅ {field}: {'*' * len(value)}")  # Hide sensitive values
        
        # Check optional fields
        print(f"✅ Log level: {config.log_level}")
        print(f"✅ App name: {config.app_name}")
        print(f"✅ App version: {config.app_version}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")

validate_config()
```

### Environment Variable Debugging
```python
import os
from utils.config import get_config

def debug_env_vars():
    # Check environment variables
    env_vars = [
        'AZURE_CLIENT_ID',
        'AZURE_CLIENT_SECRET',
        'AZURE_TENANT_ID',
        'DATAVERSE_URL',
        'LOG_LEVEL',
        'APP_NAME',
        'APP_VERSION'
    ]
    
    print("Environment Variables:")
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var or 'ID' in var:
                print(f"  {var}: {'*' * len(value)}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: ❌ Not set")
    
    # Try to load config
    try:
        config = get_config()
        print("\n✅ Configuration loaded successfully")
    except Exception as e:
        print(f"\n❌ Configuration failed: {e}")

debug_env_vars()
```

## 🚨 Error Handling

### Configuration Errors

#### `ValueError`
Raised when required environment variables are missing.

**Example:**
```python
from utils.config import get_config

try:
    config = get_config()
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please check your .env file")
```

#### `ValidationError`
Raised when environment variable values are invalid.

**Example:**
```python
from pydantic import ValidationError
from utils.config import Settings

try:
    settings = Settings()
except ValidationError as e:
    print(f"Validation error: {e}")
    for error in e.errors():
        print(f"  Field: {error['loc']}, Error: {error['msg']}")
```

### Logging Errors

#### `PermissionError`
Raised when log file cannot be created due to permissions.

**Example:**
```python
from utils.logger import setup_logging

try:
    setup_logging(log_level="INFO", log_file="/root/logs/app.log")
except PermissionError:
    print("Cannot create log file - permission denied")
    # Fall back to console logging
    setup_logging(log_level="INFO")
```

## 🔄 Async Support

The utilities module is primarily synchronous, but can be used in async contexts:

```python
import asyncio
from utils.config import get_config
from utils.logger import get_logger

async def async_function():
    # Configuration is thread-safe
    config = get_config()
    logger = get_logger(__name__)
    
    logger.info("Starting async operation")
    
    # Your async code here
    await asyncio.sleep(1)
    
    logger.info("Async operation completed")

# Run async function
asyncio.run(async_function())
```

## 📊 Dependencies

### Required Packages
- `pydantic>=2.5.0` - Configuration validation
- `python-dotenv>=1.0.0` - Environment variable loading
- `structlog>=23.2.0` - Structured logging

### Optional Packages
- `rich>=13.7.0` - Rich console output (for CLI)

## 🔧 Environment Variables

### Required Variables
```bash
# Azure AD Configuration
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here
AZURE_TENANT_ID=your_tenant_id_here

# Dataverse Configuration
DATAVERSE_URL=https://your-org.crm.dynamics.com
```

### Optional Variables
```bash
# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/cockpit.log

# Application Configuration
APP_NAME=life-cockpit
APP_VERSION=1.0.0

# Graph API Configuration
GRAPH_SCOPES=https://graph.microsoft.com/.default
```

## 📝 Best Practices

### Configuration
- Use `.env` files for local development
- Never commit sensitive values to version control
- Validate configuration at startup
- Use type hints for configuration access

### Logging
- Use structured logging with context
- Set appropriate log levels
- Include relevant metadata in log entries
- Use log rotation for production

### Error Handling
- Validate configuration early
- Provide clear error messages
- Handle missing environment variables gracefully
- Log configuration issues appropriately

---

*Last Updated: August 20, 2025*
*API Version: 1.0.0*
