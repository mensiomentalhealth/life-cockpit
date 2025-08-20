# Deployment Guide

This guide covers deployment strategies for Life Cockpit, from current local development to future production Azure services.

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

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Azure

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
    
    - name: Run tests
      run: |
        pytest tests/ -v
    
    - name: Run linting
      run: |
        pip install flake8 black
        flake8 .
        black --check .

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Azure Functions
      uses: Azure/functions-action@v1
      with:
        app-name: life-cockpit-functions
        package: '.'
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
    
    - name: Deploy to Azure Container Registry
      uses: azure/docker-login@v1
      with:
        login-server: ${{ secrets.REGISTRY_LOGIN_SERVER }}
        username: ${{ secrets.REGISTRY_USERNAME }}
        password: ${{ secrets.REGISTRY_PASSWORD }}
    
    - name: Build and push image
      run: |
        docker build -t ${{ secrets.REGISTRY_LOGIN_SERVER }}/life-cockpit:${{ github.sha }} .
        docker push ${{ secrets.REGISTRY_LOGIN_SERVER }}/life-cockpit:${{ github.sha }}
```

### Azure DevOps Pipeline
```yaml
# azure-pipelines.yml
trigger:
- main

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.11'

stages:
- stage: Test
  displayName: 'Test Stage'
  jobs:
  - job: Test
    displayName: 'Run Tests'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
    
    - script: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-asyncio
      displayName: 'Install dependencies'
    
    - script: |
        pytest tests/ -v
      displayName: 'Run tests'

- stage: Deploy
  displayName: 'Deploy Stage'
  dependsOn: Test
  condition: succeeded()
  jobs:
  - deployment: DeployFunctionApp
    displayName: 'Deploy Function App'
    environment: 'production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: ArchiveFiles@2
            inputs:
              rootFolderOrFile: '$(System.DefaultWorkingDirectory)'
              includeRootFolder: false
              archiveType: 'zip'
              archiveFile: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
              replaceExistingArchive: true
          
          - task: AzureFunctionApp@1
            inputs:
              azureSubscription: 'Your-Azure-Subscription'
              appName: 'life-cockpit-functions'
              package: '$(Build.ArtifactStagingDirectory)/$(Build.BuildId).zip'
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
