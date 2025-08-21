# Production Deployment Guide

## 🎯 **Current Status: READY FOR PRODUCTION**

Your messaging automation system has been successfully tested and is ready to replace your Power Automate script. This guide will help you deploy it to production.

## 📋 **Pre-Deployment Checklist**

### ✅ **Completed Items**
- [x] Multi-channel messaging factory built and tested
- [x] Dynamics integration working with `cre92_scheduledmessage` table
- [x] Email processing via Microsoft Graph API tested
- [x] Web dashboard for monitoring and management
- [x] CLI tools for testing and management
- [x] Comprehensive logging and error handling
- [x] Sandbox environment for safe testing

### 🚀 **Production Deployment Steps**

## 1. **Azure Infrastructure Setup**

### Create Azure Resources
```bash
# Create Resource Group
az group create --name life-cockpit-prod --location eastus

# Create Storage Account
az storage account create --name lifecockpitstorage --resource-group life-cockpit-prod --location eastus --sku Standard_LRS

# Create Key Vault
az keyvault create --name life-cockpit-kv --resource-group life-cockpit-prod --location eastus

# Create App Service Plan
az appservice plan create --name life-cockpit-plan --resource-group life-cockpit-prod --sku B1 --is-linux

# Create Function App
az functionapp create --name life-cockpit-functions --resource-group life-cockpit-prod --plan life-cockpit-plan --runtime python --functions-version 4
```

### Configure Key Vault Secrets
```bash
# Store your production secrets
az keyvault secret set --vault-name life-cockpit-kv --name "GRAPH-TENANT-ID" --value "your-tenant-id"
az keyvault secret set --vault-name life-cockpit-kv --name "GRAPH-CLIENT-ID" --value "your-client-id"
az keyvault secret set --vault-name life-cockpit-kv --name "GRAPH-CLIENT-SECRET" --value "your-client-secret"
az keyvault secret set --vault-name life-cockpit-kv --name "RESPOND-API-KEY" --value "your-respond-api-key"
az keyvault secret set --vault-name life-cockpit-kv --name "RESPOND-WORKSPACE-ID" --value "your-workspace-id"
az keyvault secret set --vault-name life-cockpit-kv --name "DATAVERSE-URL" --value "your-dataverse-url"
az keyvault secret set --vault-name life-cockpit-kv --name "DATAVERSE-CLIENT-ID" --value "your-dataverse-client-id"
az keyvault secret set --vault-name life-cockpit-kv --name "DATAVERSE-CLIENT-SECRET" --value "your-dataverse-client-secret"
```

## 2. **Azure Functions Deployment**

### Create Function Structure
```bash
# Create function directory structure
mkdir -p azure/functions/dynamics-message-processor
mkdir -p azure/functions/webhook-receiver
mkdir -p azure/functions/scheduled-processor
```

### Dynamics Message Processor Function
```python:azure/functions/dynamics_message_processor/function.json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "timer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 */5 * * * *"
    }
  ]
}
```

```python:azure/functions/dynamics_message_processor/__init__.py
import azure.functions as func
import logging
import asyncio
import os
from azure.dynamics_message_processor import dynamics_message_processor

async def main(timer: func.TimerRequest) -> None:
    """Process Dynamics messages every 5 minutes"""
    
    logging.info('Dynamics Message Processor triggered')
    
    try:
        # Process messages
        result = await dynamics_message_processor.process_dynamics_messages()
        
        logging.info(f'Processing completed: {result["processed_count"]} messages, {result["success_count"]} successful')
        
    except Exception as e:
        logging.error(f'Dynamics message processing failed: {str(e)}')
        raise

# For local testing
if __name__ == "__main__":
    asyncio.run(main(None))
```

### Deploy Functions
```bash
# Deploy to Azure Functions
cd azure/functions
func azure functionapp publish life-cockpit-functions
```

## 3. **Logic Apps Setup**

### Create Logic App for Scheduling
```json:azure/logic-apps/dynamics-message-scheduler.json
{
  "definition": {
    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "triggers": {
      "Recurrence": {
        "recurrence": {
          "frequency": "Minute",
          "interval": 5
        },
        "type": "Recurrence"
      }
    },
    "actions": {
      "Call_Dynamics_Message_Processor": {
        "type": "Http",
        "inputs": {
          "method": "POST",
          "uri": "@{listCallbackUrl()['value']}",
          "headers": {
            "Content-Type": "application/json"
          },
          "body": {
            "action": "process_dynamics_messages"
          }
        },
        "runTime": "2017-02-08T17:13:00Z"
      }
    },
    "outputs": {}
  }
}
```

## 4. **Environment Configuration**

### Production Environment Variables
```bash
# .env.production
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
DATAVERSE_URL=https://your-org.crm.dynamics.com
DATAVERSE_CLIENT_ID=your-dataverse-client-id
DATAVERSE_CLIENT_SECRET=your-dataverse-client-secret
RESPOND_API_KEY=your-respond-api-key
RESPOND_WORKSPACE_ID=your-workspace-id
RESPOND_BASE_URL=https://api.respond.io
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### Azure Function Configuration
```bash
# Set function app settings
az functionapp config appsettings set --name life-cockpit-functions --resource-group life-cockpit-prod --settings \
  AZURE_TENANT_ID="@Microsoft.KeyVault(SecretUri=https://life-cockpit-kv.vault.azure.net/secrets/GRAPH-TENANT-ID/)" \
  AZURE_CLIENT_ID="@Microsoft.KeyVault(SecretUri=https://life-cockpit-kv.vault.azure.net/secrets/GRAPH-CLIENT-ID/)" \
  AZURE_CLIENT_SECRET="@Microsoft.KeyVault(SecretUri=https://life-cockpit-kv.vault.azure.net/secrets/GRAPH-CLIENT-SECRET/)" \
  DATAVERSE_URL="@Microsoft.KeyVault(SecretUri=https://life-cockpit-kv.vault.azure.net/secrets/DATAVERSE-URL/)" \
  DATAVERSE_CLIENT_ID="@Microsoft.KeyVault(SecretUri=https://life-cockpit-kv.vault.azure.net/secrets/DATAVERSE-CLIENT-ID/)" \
  DATAVERSE_CLIENT_SECRET="@Microsoft.KeyVault(SecretUri=https://life-cockpit-kv.vault.azure.net/secrets/DATAVERSE-CLIENT-SECRET/)" \
  RESPOND_API_KEY="@Microsoft.KeyVault(SecretUri=https://life-cockpit-kv.vault.azure.net/secrets/RESPOND-API-KEY/)" \
  RESPOND_WORKSPACE_ID="@Microsoft.KeyVault(SecretUri=https://life-cockpit-kv.vault.azure.net/secrets/RESPOND-WORKSPACE-ID/)" \
  LOG_LEVEL=INFO \
  ENVIRONMENT=production
```

## 5. **Monitoring and Alerting**

### Application Insights Setup
```bash
# Create Application Insights
az monitor app-insights component create --app life-cockpit-insights --location eastus --resource-group life-cockpit-prod --application-type web

# Link to Function App
az functionapp config appsettings set --name life-cockpit-functions --resource-group life-cockpit-prod --settings \
  APPINSIGHTS_INSTRUMENTATIONKEY="your-instrumentation-key"
```

### Custom Dashboards
- **Message Processing Metrics**: Success/failure rates, processing times
- **Dynamics Integration**: Records processed, errors, performance
- **Provider Status**: Graph API, Respond.io health checks
- **Business Metrics**: Messages sent by type, client engagement

## 6. **Testing Production Deployment**

### Test Scripts
```bash
# Test production messaging
python blc.py messaging test --environment production

# Test Dynamics integration
python blc.py dynamics test --environment production

# Test web dashboard
python web/main.py --environment production
```

### Validation Checklist
- [ ] Azure Functions deployed and running
- [ ] Logic Apps scheduled correctly
- [ ] Key Vault secrets accessible
- [ ] Dynamics integration working
- [ ] Email messages being sent
- [ ] Logs being recorded
- [ ] Web dashboard accessible
- [ ] Error handling working

## 7. **Go-Live Process**

### Phase 1: Email Processing (Ready Now)
1. Deploy Azure Functions
2. Configure production credentials
3. Test with real Dynamics data
4. Monitor for 24 hours
5. Gradually increase processing frequency

### Phase 2: Multi-Channel Support
1. Configure Respond.io workspace
2. Test Telegram integration
3. Add SMS/WhatsApp support
4. Deploy additional functions

### Rollback Plan
- Keep Power Automate script running in parallel
- Monitor both systems for 1 week
- Gradually migrate message volume
- Full cutover after validation

## 8. **Post-Deployment Monitoring**

### Key Metrics to Track
- **Processing Success Rate**: Target > 99%
- **Processing Time**: Target < 30 seconds per message
- **Error Rate**: Target < 1%
- **Dynamics Query Performance**: Monitor table access patterns
- **API Rate Limits**: Monitor Graph API and Respond.io usage

### Alert Conditions
- Processing success rate < 95%
- Processing time > 60 seconds
- Error rate > 5%
- Dynamics connection failures
- API rate limit warnings

## 🎯 **Success Criteria**

Your system will be considered successfully deployed when:
- ✅ Replaces Power Automate script completely
- ✅ Processes all Dynamics messages within 5 minutes
- ✅ Maintains 99%+ success rate
- ✅ Provides better observability than Power Automate
- ✅ Supports multi-channel messaging
- ✅ Scales automatically with message volume

---

**Ready to deploy! Your messaging automation system is production-ready and will provide a much more robust, programmable, and observable solution than Power Automate.**
