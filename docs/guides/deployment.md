# Deployment Guide

This guide covers deployment strategies for Life Cockpit, from current local development to future production Azure services.

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

Life Cockpit uses GitHub Actions for automated testing, security scanning, and deployment:

#### Workflow Stages
1. **Test** - Unit tests, linting, type checking
2. **Security** - CodeQL security analysis
3. **Deploy Staging** - Automatic deployment to staging (develop branch)
4. **Deploy Production** - Manual deployment to production (main branch)

#### Key Features
- **Multi-Python Testing** - Tests against Python 3.11 and 3.12
- **Code Quality** - Black, isort, mypy, flake8
- **Security Scanning** - GitHub CodeQL analysis
- **Coverage Reporting** - Codecov integration
- **Environment Protection** - Staging and production environments

#### Secrets Required
```bash
AZURE_CLIENT_ID=your_azure_client_id
AZURE_CLIENT_SECRET=your_azure_client_secret
AZURE_TENANT_ID=your_azure_tenant_id
DATAVERSE_URL=your_dataverse_url
```

## 🛡️ Rollback & Idempotency

### Rollback System

Life Cockpit includes a comprehensive rollback system for safe deployments:

#### Features
- **Automatic Rollback Points** - Created before critical operations
- **Time-based Expiration** - Rollback points expire after 30 days
- **Dependency Management** - Handles dependent rollback operations
- **Persistent Storage** - Rollback points stored in JSON format

#### Supported Operations
- **Dataverse Operations** - Create, update, delete with rollback
- **Configuration Changes** - Config modifications with restoration
- **Graph API Calls** - API operations with state tracking
- **Workflow Deployments** - Workflow changes with rollback

#### CLI Commands
```bash
# List rollback points
python blc.py rollback list

# Create rollback point (programmatic)
python blc.py rollback create

# Execute rollback (programmatic)
python blc.py rollback execute
```

#### Programmatic Usage
```python
from utils.rollback import get_rollback_manager

# Create rollback point
rollback_manager = get_rollback_manager()
point_id = rollback_manager.create_point(
    operation="dataverse_create",
    description="Create new client record",
    data={"entity_name": "client", "entity_id": "123"}
)

# Automatic rollback on failure
try:
    # Perform operation
    create_client_record()
except Exception:
    # Rollback automatically triggered
    rollback_manager.rollback(point_id)
```

### Idempotency

All operations in Life Cockpit are designed to be idempotent:

#### Principles
- **Safe Re-runs** - Operations can be safely re-executed
- **State Checking** - Check current state before modifications
- **Conditional Updates** - Only update if changes are needed
- **Conflict Resolution** - Handle concurrent modifications

#### Implementation
```python
# Example: Idempotent Dataverse update
async def update_client_record(client_id: str, data: dict):
    # Check current state
    current = await get_client_record(client_id)
    
    # Only update if changes exist
    if current != data:
        # Create rollback point
        rollback_id = create_rollback_point("dataverse_update", current)
        
        try:
            await update_record(client_id, data)
        except Exception:
            await rollback(rollback_id)
            raise
```

## 🏠 Current Deployment: Local Development

### Git-Based Backup
Currently, Life Cockpit uses Git for version control and backup:

```bash
# Regular backup workflow
git add .
git commit -m "feat: add new feature"
git push origin main

# Create backup branch
git checkout -b backup/$(date +%Y%m%d)
git push origin backup/$(date +%Y%m%d)
```

### Local System Requirements
- **Python 3.8+**: Core runtime
- **Virtual Environment**: Isolated dependencies
- **Environment Variables**: `.env` file with credentials
- **Git**: Version control and backup

### Local Setup
```bash
# Clone repository
git clone <repository-url>
cd life-cockpit

# Setup environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp env.example .env
# Edit .env with your credentials

# Test deployment
python blc.py version
python blc.py auth test
```

## 🚀 Future Azure Deployment

### Azure Services Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Azure Front   │    │   Logic Apps    │    │   Azure Funcs   │
│   Door/App      │    │   (Orchestration)│    │   (API Endpoints)│
│   Service       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Azure Key      │
                    │   Vault (Secrets)│
                    │                 │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Dataverse     │
                    │   (Data Store)  │
                    │                 │
                    └─────────────────┘
```

### 1. Azure Functions Deployment

#### Function App Structure
```
life-cockpit-functions/
├── host.json
├── local.settings.json
├── requirements.txt
├── auth/
│   ├── __init__.py
│   └── graph.py
├── dataverse/
│   ├── __init__.py
│   └── operations.py
├── comms/
│   ├── __init__.py
│   ├── email.py
│   └── notifications.py
└── HttpTriggers/
    ├── auth_test/
    │   ├── __init__.py
    │   └── function.json
    ├── graph_users/
    │   ├── __init__.py
    │   └── function.json
    └── dataverse_tables/
        ├── __init__.py
        └── function.json
```

#### Function Configuration
```json
// host.json
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[3.*, 4.0.0)"
  }
}
```

#### Example HTTP Trigger
```python
# HttpTriggers/auth_test/__init__.py
import azure.functions as func
import logging
from auth.graph import get_auth_manager

async def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    try:
        auth_manager = get_auth_manager()
        success = await auth_manager.test_connection()
        
        if success:
            return func.HttpResponse(
                "✅ Authentication successful!",
                status_code=200
            )
        else:
            return func.HttpResponse(
                "❌ Authentication failed",
                status_code=500
            )
    except Exception as e:
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )
```

### 2. Azure Logic Apps Integration

#### Event-Driven Workflows
```json
{
  "definition": {
    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "triggers": {
      "When_a_Dataverse_record_is_created": {
        "type": "ApiConnectionWebhook",
        "inputs": {
          "host": {
            "connection": {
              "name": "@parameters('$connections')['commondataserviceforapps']['connectionId']"
            }
          },
          "body": {
            "callbackUrl": "@{listCallbackUrl()}"
          }
        }
      }
    },
    "actions": {
      "Call_Azure_Function": {
        "type": "Http",
        "inputs": {
          "method": "POST",
          "uri": "@{parameters('functionUrl')}",
          "body": {
            "trigger": "dataverse_record_created",
            "data": "@{triggerBody()}"
          }
        }
      }
    }
  }
}
```

#### Scheduled Workflows
```json
{
  "definition": {
    "triggers": {
      "Daily_Reminder_Check": {
        "type": "Recurrence",
        "recurrence": {
          "frequency": "Day",
          "interval": 1,
          "schedule": {
            "hours": ["09:00"],
            "minutes": [0]
          }
        }
      }
    },
    "actions": {
      "Get_Sessions_Today": {
        "type": "Http",
        "inputs": {
          "method": "GET",
          "uri": "@{parameters('dataverseApiUrl')}/api/data/v9.2/contacts",
          "headers": {
            "Authorization": "@{parameters('bearerToken')}"
          }
        }
      }
    }
  }
}
```

### 3. Azure Key Vault Integration

#### Secret Management
```python
# utils/secrets.py
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def get_secret(secret_name: str) -> str:
    """Get secret from Azure Key Vault."""
    credential = DefaultAzureCredential()
    client = SecretClient(
        vault_url="https://your-keyvault.vault.azure.net/",
        credential=credential
    )
    return client.get_secret(secret_name).value

# Usage in configuration
AZURE_CLIENT_SECRET = get_secret("azure-client-secret")
DATAVERSE_URL = get_secret("dataverse-url")
```

#### Key Vault Configuration
```bash
# Azure CLI commands
az keyvault create --name life-cockpit-kv --resource-group life-cockpit-rg --location eastus

# Store secrets
az keyvault secret set --vault-name life-cockpit-kv --name "azure-client-secret" --value "your-secret"
az keyvault secret set --vault-name life-cockpit-kv --name "dataverse-url" --value "https://your-org.crm.dynamics.com"

# Grant access to Function App
az keyvault set-policy --name life-cockpit-kv --object-id <function-app-msi> --secret-permissions get list
```

### 4. Azure Container Instances (Future)

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "blc.py", "serve", "--host", "0.0.0.0", "--port", "8000"]
```

#### Container Deployment
```bash
# Build and push image
docker build -t life-cockpit:latest .
docker tag life-cockpit:latest your-registry.azurecr.io/life-cockpit:latest
docker push your-registry.azurecr.io/life-cockpit:latest

# Deploy to Azure Container Instances
az container create \
  --resource-group life-cockpit-rg \
  --name life-cockpit-container \
  --image your-registry.azurecr.io/life-cockpit:latest \
  --dns-name-label life-cockpit \
  --ports 8000 \
  --environment-variables \
    AZURE_CLIENT_ID=@azure-client-id \
    AZURE_TENANT_ID=@azure-tenant-id
```

## 🔍 Monitoring and Logging

### Application Insights
```python
# utils/monitoring.py
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

def setup_monitoring():
    """Setup Application Insights monitoring."""
    logger = logging.getLogger(__name__)
    logger.addHandler(AzureLogHandler(
        connection_string='InstrumentationKey=your-key'
    ))
    return logger

# Usage
logger = setup_monitoring()
logger.info("Application started", extra={
    "custom_dimensions": {
        "environment": "production",
        "version": "1.0.0"
    }
})
```

### Health Checks
```python
# health_check.py
from fastapi import FastAPI
from auth.graph import get_auth_manager
from dataverse.list_tables import list_dataverse_tables

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test authentication
        auth_manager = get_auth_manager()
        auth_ok = await auth_manager.test_connection()
        
        # Test Dataverse
        dataverse_ok = await list_dataverse_tables()
        
        if auth_ok and dataverse_ok:
            return {"status": "healthy", "services": {"auth": "ok", "dataverse": "ok"}}
        else:
            return {"status": "unhealthy", "services": {"auth": auth_ok, "dataverse": dataverse_ok}}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

## 🛡️ Security Considerations

### Network Security
- **Azure Front Door**: DDoS protection and global load balancing
- **Network Security Groups**: Restrict access to Azure resources
- **Private Endpoints**: Secure Dataverse and Key Vault access

### Identity and Access
- **Managed Identities**: For Azure service-to-service authentication
- **Role-Based Access Control (RBAC)**: Least privilege access
- **Azure AD B2B**: External user access (if needed)

### Data Protection
- **Encryption at Rest**: All data encrypted in Azure services
- **Encryption in Transit**: TLS 1.2+ for all communications
- **Key Vault**: Centralized secret management

## 📊 Performance Optimization

### Caching Strategy
```python
# utils/cache.py
import redis
from functools import wraps
import json

redis_client = redis.Redis(host='your-redis.redis.cache.windows.net', port=6380, ssl=True)

def cache_result(ttl=300):
    """Cache function results in Redis."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=600)  # Cache for 10 minutes
async def get_dataverse_tables():
    # Expensive operation
    pass
```

### Scaling Configuration
```json
// host.json for Azure Functions
{
  "version": "2.0",
  "functionTimeout": "00:05:00",
  "healthMonitor": {
    "enabled": true,
    "healthCheckInterval": "00:00:10",
    "healthCheckWindow": "00:02:00",
    "healthCheckThreshold": 6
  },
  "singleton": {
    "lockPeriod": "00:00:30",
    "listenerLockPeriod": "00:01:00"
  }
}
```

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Code review completed
- [ ] Security scan passed
- [ ] Performance benchmarks met
- [ ] Documentation updated

### Deployment Steps
1. **Create Azure Resources**
   - Resource Group
   - Key Vault
   - Function App
   - Logic Apps
   - Container Registry (if needed)

2. **Configure Secrets**
   - Store all sensitive data in Key Vault
   - Configure managed identities
   - Set up RBAC permissions

3. **Deploy Application**
   - Deploy Function App
   - Configure Logic Apps workflows
   - Set up monitoring

4. **Post-Deployment**
   - Run health checks
   - Verify all endpoints
   - Monitor logs and metrics
   - Test end-to-end workflows

### Rollback Plan
```bash
# Quick rollback to previous version
az functionapp deployment source config-zip \
  --resource-group life-cockpit-rg \
  --name life-cockpit-functions \
  --src previous-version.zip

# Or rollback container
az container restart \
  --resource-group life-cockpit-rg \
  --name life-cockpit-container
```

---

*This guide covers deployment from local development to production Azure services. For specific implementation details, see the API reference and development setup guides.*
