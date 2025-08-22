# Monitoring Dashboard Configuration

## 📊 **Production Monitoring Setup**

Your messaging automation system includes comprehensive monitoring capabilities. This guide helps you set up dashboards and alerts for production monitoring.

## 🎯 **Key Metrics to Monitor**

### 1. **Message Processing Metrics**
- **Success Rate**: Target > 99%
- **Processing Time**: Target < 30 seconds per message
- **Error Rate**: Target < 1%
- **Messages Processed per Hour/Day**

### 2. **Dynamics Integration Metrics**
- **Records Queried**: Number of records processed from `cre92_scheduledmessage`
- **Query Performance**: Time to query pending messages
- **Update Success Rate**: Success rate of marking messages as sent

### 3. **Provider Health Metrics**
- **Graph API Status**: Email/Teams message success rates
- **Respond.io Status**: Telegram/SMS/WhatsApp success rates
- **API Rate Limits**: Monitor usage against limits

### 4. **System Health Metrics**
- **Function Execution Time**: Azure Function performance
- **Memory Usage**: Resource utilization
- **Error Logs**: Detailed error tracking

## 📈 **Azure Application Insights Dashboard**

### Create Custom Dashboard
```json:azure/monitoring/dashboard.json
{
  "lenses": {
    "0": {
      "order": 0,
      "parts": {
        "0": {
          "position": {
            "x": 0,
            "y": 0,
            "colSpan": 6,
            "rowSpan": 4
          },
          "metadata": {
            "inputs": [],
            "type": "Extension/Microsoft_OperationsManagementSuite_Workspace/PartType/LogsDashboardPart",
            "settings": {
              "content": {
                "Query": "traces\n| where timestamp > ago(1h)\n| where customDimensions.ProcessName == \"DynamicsMessageProcessor\"\n| summarize count() by bin(timestamp, 5m)\n| render timechart",
                "PartTitle": "Message Processing Volume (Last Hour)"
              }
            }
          }
        },
        "1": {
          "position": {
            "x": 6,
            "y": 0,
            "colSpan": 6,
            "rowSpan": 4
          },
          "metadata": {
            "inputs": [],
            "type": "Extension/Microsoft_OperationsManagementSuite_Workspace/PartType/LogsDashboardPart",
            "settings": {
              "content": {
                "Query": "traces\n| where timestamp > ago(1h)\n| where customDimensions.ProcessName == \"DynamicsMessageProcessor\"\n| where customDimensions.Status == \"success\"\n| summarize count() by bin(timestamp, 5m)\n| render timechart",
                "PartTitle": "Successful Messages (Last Hour)"
              }
            }
          }
        },
        "2": {
          "position": {
            "x": 0,
            "y": 4,
            "colSpan": 6,
            "rowSpan": 4
          },
          "metadata": {
            "inputs": [],
            "type": "Extension/Microsoft_OperationsManagementSuite_Workspace/PartType/LogsDashboardPart",
            "settings": {
              "content": {
                "Query": "traces\n| where timestamp > ago(1h)\n| where customDimensions.ProcessName == \"DynamicsMessageProcessor\"\n| where customDimensions.Status == \"failed\"\n| summarize count() by bin(timestamp, 5m)\n| render timechart",
                "PartTitle": "Failed Messages (Last Hour)"
              }
            }
          }
        },
        "3": {
          "position": {
            "x": 6,
            "y": 4,
            "colSpan": 6,
            "rowSpan": 4
          },
          "metadata": {
            "inputs": [],
            "type": "Extension/Microsoft_OperationsManagementSuite_Workspace/PartType/LogsDashboardPart",
            "settings": {
              "content": {
                "Query": "traces\n| where timestamp > ago(24h)\n| where customDimensions.ProcessName == \"DynamicsMessageProcessor\"\n| summarize count() by customDimensions.MessageType\n| render piechart",
                "PartTitle": "Messages by Type (Last 24 Hours)"
              }
            }
          }
        }
      }
    }
  }
}
```

### Setup Dashboard
```bash
# Create the dashboard
az monitor app-insights component create \
    --app life-cockpit-insights \
    --location eastus \
    --resource-group life-cockpit-prod \
    --application-type web

# Import dashboard (you'll need to do this via Azure Portal)
# Navigate to Application Insights > Dashboards > Import
```

## 🚨 **Alert Configuration**

### Create Alert Rules
```bash
# Alert for high error rate
az monitor metrics alert create \
    --name "high-error-rate" \
    --resource-group life-cockpit-prod \
    --scopes "/subscriptions/your-subscription-id/resourceGroups/life-cockpit-prod/providers/Microsoft.Insights/components/life-cockpit-insights" \
    --condition "avg customMetrics/error_rate > 5" \
    --window-size "PT5M" \
    --evaluation-frequency "PT1M" \
    --description "Alert when error rate exceeds 5%"

# Alert for processing delays
az monitor metrics alert create \
    --name "processing-delay" \
    --resource-group life-cockpit-prod \
    --scopes "/subscriptions/your-subscription-id/resourceGroups/life-cockpit-prod/providers/Microsoft.Insights/components/life-cockpit-insights" \
    --condition "avg customMetrics/processing_time > 60" \
    --window-size "PT5M" \
    --evaluation-frequency "PT1M" \
    --description "Alert when processing time exceeds 60 seconds"
```

### Email Notifications
```bash
# Create action group for email notifications
az monitor action-group create \
    --name "life-cockpit-alerts" \
    --resource-group life-cockpit-prod \
    --short-name "lc-alerts" \
    --action email "admin" "admin@yourcompany.com"

# Link action group to alerts
az monitor metrics alert update \
    --name "high-error-rate" \
    --resource-group life-cockpit-prod \
    --add-action "/subscriptions/your-subscription-id/resourceGroups/life-cockpit-prod/providers/Microsoft.Insights/actionGroups/life-cockpit-alerts"
```

## 📊 **Custom Metrics**

### Add Custom Metrics to Functions
```python:azure/functions/dynamics_message_processor/__init__.py
import azure.functions as func
import logging
import asyncio
import os
import sys
from opencensus.ext.azure.log_exporter import AzureLogHandler

# Add the parent directory to the path to import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from azure.dynamics_message_processor import dynamics_message_processor

# Setup custom metrics
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string='InstrumentationKey=your-instrumentation-key')
)

async def main(timer: func.TimerRequest) -> None:
    """Process Dynamics messages every 5 minutes"""
    
    start_time = time.time()
    logger.info('Dynamics Message Processor triggered')
    
    try:
        # Process messages
        result = await dynamics_message_processor.process_dynamics_messages()
        
        # Log custom metrics
        processing_time = time.time() - start_time
        success_rate = (result["success_count"] / result["processed_count"]) * 100 if result["processed_count"] > 0 else 0
        
        logger.info('Processing completed', extra={
            'custom_dimensions': {
                'processed_count': result["processed_count"],
                'success_count': result["success_count"],
                'failed_count': result["failed_count"],
                'processing_time_seconds': processing_time,
                'success_rate_percent': success_rate,
                'process_name': 'DynamicsMessageProcessor'
            }
        })
        
    except Exception as e:
        logger.error(f'Dynamics message processing failed: {str(e)}')
        raise

# For local testing
if __name__ == "__main__":
    asyncio.run(main(None))
```

## 📈 **Business Intelligence Dashboard**

### Power BI Integration
```sql
-- Query for Power BI dashboard
SELECT 
    DATE(timestamp) as Date,
    HOUR(timestamp) as Hour,
    customDimensions.MessageType as MessageType,
    customDimensions.Status as Status,
    COUNT(*) as MessageCount,
    AVG(CAST(customDimensions.ProcessingTimeSeconds as FLOAT)) as AvgProcessingTime
FROM traces 
WHERE timestamp > ago(30d)
    AND customDimensions.ProcessName = 'DynamicsMessageProcessor'
GROUP BY 
    DATE(timestamp),
    HOUR(timestamp),
    customDimensions.MessageType,
    customDimensions.Status
```

### Key Performance Indicators (KPIs)
1. **Message Processing Efficiency**
   - Success Rate: > 99%
   - Average Processing Time: < 30 seconds
   - Error Rate: < 1%

2. **Business Metrics**
   - Messages Sent per Day
   - Messages by Channel (Email, Teams, Telegram, etc.)
   - Client Engagement (messages per client)

3. **System Health**
   - Function Execution Success Rate
   - API Response Times
   - Resource Utilization

## 🔧 **Monitoring Setup Commands**

### Quick Setup Script
```bash
#!/bin/bash

# Setup monitoring for Life Cockpit
echo "📊 Setting up monitoring..."

# Create Application Insights if not exists
az monitor app-insights component create \
    --app life-cockpit-insights \
    --location eastus \
    --resource-group life-cockpit-prod \
    --application-type web

# Get instrumentation key
INSTRUMENTATION_KEY=$(az monitor app-insights component show \
    --app life-cockpit-insights \
    --resource-group life-cockpit-prod \
    --query "instrumentationKey" \
    --output tsv)

echo "🔑 Instrumentation Key: $INSTRUMENTATION_KEY"

# Update function app settings
az functionapp config appsettings set \
    --name life-cockpit-functions \
    --resource-group life-cockpit-prod \
    --settings \
    APPINSIGHTS_INSTRUMENTATIONKEY="$INSTRUMENTATION_KEY"

echo "✅ Monitoring setup complete!"
echo "📈 View your dashboard at: https://portal.azure.com/#@your-tenant/resource/subscriptions/your-subscription/resourceGroups/life-cockpit-prod/providers/Microsoft.Insights/components/life-cockpit-insights"
```

## 🎯 **Success Criteria**

Your monitoring setup is complete when:
- ✅ Custom metrics are being logged
- ✅ Dashboard shows real-time data
- ✅ Alerts are configured and working
- ✅ Error tracking is comprehensive
- ✅ Performance metrics are visible
- ✅ Business KPIs are tracked

---

**Your messaging automation system now has enterprise-grade monitoring and alerting!**
