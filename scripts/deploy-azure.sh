#!/bin/bash

# Life Cockpit Azure Deployment Script
# This script deploys the messaging automation system to Azure

set -e

# Configuration
RESOURCE_GROUP="life-cockpit-prod"
LOCATION="eastus"
STORAGE_ACCOUNT="lifecockpitstorage"
KEY_VAULT="life-cockpit-kv"
APP_SERVICE_PLAN="life-cockpit-plan"
FUNCTION_APP="life-cockpit-functions"
APP_INSIGHTS="life-cockpit-insights"

echo "🚀 Deploying Life Cockpit to Azure..."

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first."
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo "❌ Please log in to Azure first: az login"
    exit 1
fi

echo "📋 Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "💾 Creating storage account..."
az storage account create \
    --name $STORAGE_ACCOUNT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS

echo "🔐 Creating Key Vault..."
az keyvault create \
    --name $KEY_VAULT \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION

echo "📊 Creating Application Insights..."
az monitor app-insights component create \
    --app $APP_INSIGHTS \
    --location $LOCATION \
    --resource-group $RESOURCE_GROUP \
    --application-type web

echo "🏗️ Creating App Service Plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku B1 \
    --is-linux

echo "⚡ Creating Function App..."
az functionapp create \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --runtime python \
    --functions-version 4 \
    --storage-account $STORAGE_ACCOUNT

echo "🔧 Configuring Function App settings..."
# Get the instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app $APP_INSIGHTS \
    --resource-group $RESOURCE_GROUP \
    --query "instrumentationKey" \
    --output tsv)

az functionapp config appsettings set \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY" \
    AZURE_TENANT_ID="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT.vault.azure.net/secrets/GRAPH-TENANT-ID/)" \
    AZURE_CLIENT_ID="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT.vault.azure.net/secrets/GRAPH-CLIENT-ID/)" \
    AZURE_CLIENT_SECRET="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT.vault.azure.net/secrets/GRAPH-CLIENT-SECRET/)" \
    DATAVERSE_URL="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT.vault.azure.net/secrets/DATAVERSE-URL/)" \
    DATAVERSE_CLIENT_ID="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT.vault.azure.net/secrets/DATAVERSE-CLIENT-ID/)" \
    DATAVERSE_CLIENT_SECRET="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT.vault.azure.net/secrets/DATAVERSE-CLIENT-SECRET/)" \
    RESPOND_API_KEY="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT.vault.azure.net/secrets/RESPOND-API-KEY/)" \
    RESPOND_WORKSPACE_ID="@Microsoft.KeyVault(SecretUri=https://$KEY_VAULT.vault.azure.net/secrets/RESPOND-WORKSPACE-ID/)" \
    LOG_LEVEL=INFO \
    ENVIRONMENT=production

echo "📝 Setting up Key Vault access policies..."
# Get the function app's managed identity
FUNCTION_PRINCIPAL_ID=$(az functionapp identity assign \
    --name $FUNCTION_APP \
    --resource-group $RESOURCE_GROUP \
    --query "principalId" \
    --output tsv)

# Grant access to Key Vault
az keyvault set-policy \
    --name $KEY_VAULT \
    --object-id $FUNCTION_PRINCIPAL_ID \
    --secret-permissions get list

echo "✅ Azure infrastructure deployed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Add your secrets to Key Vault:"
echo "   az keyvault secret set --vault-name $KEY_VAULT --name 'GRAPH-TENANT-ID' --value 'your-tenant-id'"
echo "   az keyvault secret set --vault-name $KEY_VAULT --name 'GRAPH-CLIENT-ID' --value 'your-client-id'"
echo "   az keyvault secret set --vault-name $KEY_VAULT --name 'GRAPH-CLIENT-SECRET' --value 'your-client-secret'"
echo "   az keyvault secret set --vault-name $KEY_VAULT --name 'DATAVERSE-URL' --value 'your-dataverse-url'"
echo "   az keyvault secret set --vault-name $KEY_VAULT --name 'DATAVERSE-CLIENT-ID' --value 'your-dataverse-client-id'"
echo "   az keyvault secret set --vault-name $KEY_VAULT --name 'DATAVERSE-CLIENT-SECRET' --value 'your-dataverse-client-secret'"
echo "   az keyvault secret set --vault-name $KEY_VAULT --name 'RESPOND-API-KEY' --value 'your-respond-api-key'"
echo "   az keyvault secret set --vault-name $KEY_VAULT --name 'RESPOND-WORKSPACE-ID' --value 'your-workspace-id'"
echo ""
echo "2. Deploy the functions:"
echo "   cd azure/functions"
echo "   func azure functionapp publish $FUNCTION_APP"
echo ""
echo "3. Test the deployment:"
echo "   python blc.py functions test-dynamics-processor"
echo ""
echo "🎉 Your messaging automation system is ready for production!"
