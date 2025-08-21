# Production Deployment Checklist

## 🎯 **Pre-Deployment Validation**

### ✅ **System Testing**
- [ ] **Production Validation Tests**: Run `python tests/test_production_validation.py`
- [ ] **Dynamics Integration**: Test with real Dynamics data
- [ ] **Messaging Factory**: Test all message types (email, Teams, Telegram, SMS, WhatsApp)
- [ ] **Error Handling**: Verify graceful error handling
- [ ] **Performance**: Confirm processing time < 30 seconds
- [ ] **Security**: No hardcoded secrets found

### ✅ **Infrastructure Setup**
- [ ] **Azure Resources**: Resource group, storage account, key vault
- [ ] **Function App**: Deployed and configured
- [ ] **Application Insights**: Created and linked
- [ ] **Key Vault**: Secrets stored and access policies configured
- [ ] **Logic Apps**: Workflow created and scheduled

### ✅ **Configuration**
- [ ] **Environment Variables**: All production values set
- [ ] **API Credentials**: Microsoft Graph API configured
- [ ] **Dataverse**: Production environment connected
- [ ] **Respond.io**: API keys configured (if using multi-channel)
- [ ] **Logging**: Production log level set to INFO

## 🚀 **Deployment Steps**

### 1. **Azure Infrastructure** (One-time setup)
```bash
# Run deployment script
./scripts/deploy-azure.sh

# Verify resources created
az resource list --resource-group life-cockpit-prod --output table
```

### 2. **Add Production Secrets**
```bash
# Add to Key Vault
az keyvault secret set --vault-name life-cockpit-kv --name "GRAPH-TENANT-ID" --value "your-tenant-id"
az keyvault secret set --vault-name life-cockpit-kv --name "GRAPH-CLIENT-ID" --value "your-client-id"
az keyvault secret set --vault-name life-cockpit-kv --name "GRAPH-CLIENT-SECRET" --value "your-client-secret"
az keyvault secret set --vault-name life-cockpit-kv --name "DATAVERSE-URL" --value "your-dataverse-url"
az keyvault secret set --vault-name life-cockpit-kv --name "DATAVERSE-CLIENT-ID" --value "your-dataverse-client-id"
az keyvault secret set --vault-name life-cockpit-kv --name "DATAVERSE-CLIENT-SECRET" --value "your-dataverse-client-secret"
az keyvault secret set --vault-name life-cockpit-kv --name "RESPOND-API-KEY" --value "your-respond-api-key"
az keyvault secret set --vault-name life-cockpit-kv --name "RESPOND-WORKSPACE-ID" --value "your-workspace-id"
```

### 3. **Deploy Functions**
```bash
# Deploy to Azure Functions
cd azure/functions
func azure functionapp publish life-cockpit-functions

# Verify deployment
az functionapp function show --name life-cockpit-functions --resource-group life-cockpit-prod --function-name dynamics_message_processor
```

### 4. **Test Production Deployment**
```bash
# Test production messaging
python blc.py messaging test --environment production

# Test Dynamics integration
python blc.py dynamics test --environment production

# Test web dashboard
python web/main.py --environment production
```

## 📊 **Monitoring Setup**

### 1. **Application Insights Dashboard**
- [ ] Import dashboard from `docs/monitoring-dashboard.md`
- [ ] Configure custom metrics
- [ ] Set up alert rules
- [ ] Test email notifications

### 2. **Key Metrics to Monitor**
- [ ] **Success Rate**: > 99%
- [ ] **Processing Time**: < 30 seconds
- [ ] **Error Rate**: < 1%
- [ ] **Function Execution**: Success rate > 99%
- [ ] **API Response Times**: Graph API, Respond.io

### 3. **Alert Configuration**
```bash
# Create alert for high error rate
az monitor metrics alert create \
    --name "high-error-rate" \
    --resource-group life-cockpit-prod \
    --scopes "/subscriptions/your-subscription-id/resourceGroups/life-cockpit-prod/providers/Microsoft.Insights/components/life-cockpit-insights" \
    --condition "avg customMetrics/error_rate > 5" \
    --window-size "PT5M" \
    --evaluation-frequency "PT1M"
```

## 🔄 **Go-Live Process**

### Phase 1: Parallel Testing (Week 1)
- [ ] Deploy to production
- [ ] Keep Power Automate running
- [ ] Monitor both systems
- [ ] Compare results
- [ ] Validate message delivery

### Phase 2: Gradual Migration (Week 2)
- [ ] Start with 10% of messages
- [ ] Monitor success rates
- [ ] Gradually increase to 50%
- [ ] Monitor for 48 hours
- [ ] Increase to 100%

### Phase 3: Full Cutover (Week 3)
- [ ] Disable Power Automate
- [ ] Monitor production system
- [ ] Verify all messages processed
- [ ] Document any issues
- [ ] Update documentation

## 🎯 **Success Criteria**

### Technical Success
- [ ] **99%+ Success Rate**: Message processing success rate
- [ ] **< 30s Processing Time**: Average processing time per message
- [ ] **< 1% Error Rate**: Error rate below 1%
- [ ] **Zero Data Loss**: All messages processed
- [ ] **Monitoring Working**: Real-time metrics visible

### Business Success
- [ ] **Replaced Power Automate**: No dependency on Power Automate
- [ ] **Improved Observability**: Better monitoring than Power Automate
- [ ] **Multi-Channel Support**: Ready for Telegram, SMS, WhatsApp
- [ ] **Scalable Architecture**: Can handle increased message volume
- [ ] **Cost Effective**: Lower operational costs

## 🔧 **Rollback Plan**

### If Issues Arise
1. **Immediate Rollback**
   ```bash
   # Disable Azure Functions
   az functionapp config appsettings set \
       --name life-cockpit-functions \
       --resource-group life-cockpit-prod \
       --settings ENABLED=false
   
   # Re-enable Power Automate
   # (Manual step in Power Automate portal)
   ```

2. **Investigate Issues**
   - Check Application Insights logs
   - Review error messages
   - Test in sandbox environment
   - Fix issues and redeploy

3. **Re-deploy After Fixes**
   ```bash
   # Re-enable and test
   az functionapp config appsettings set \
       --name life-cockpit-functions \
       --resource-group life-cockpit-prod \
       --settings ENABLED=true
   ```

## 📋 **Post-Deployment Tasks**

### Week 1
- [ ] Monitor system 24/7
- [ ] Review daily metrics
- [ ] Address any issues
- [ ] Document lessons learned

### Week 2
- [ ] Optimize performance if needed
- [ ] Add additional monitoring
- [ ] Plan Telegram integration
- [ ] Update documentation

### Month 1
- [ ] Performance review
- [ ] Cost analysis
- [ ] Feature enhancements
- [ ] Team training

## 🎉 **Celebration Checklist**

- [ ] **Power Automate Decommissioned**: Legacy system removed
- [ ] **100% Message Success**: All messages processed successfully
- [ ] **Team Trained**: Team familiar with new system
- [ ] **Documentation Updated**: All docs reflect new system
- [ ] **Monitoring Active**: Real-time monitoring working
- [ ] **Cost Savings Realized**: Lower operational costs
- [ ] **Scalability Proven**: System handles increased load
- [ ] **Multi-Channel Ready**: Ready for Telegram, SMS, WhatsApp

---

**🎯 Your messaging automation system is now production-ready and will provide a much more robust, programmable, and observable solution than Power Automate!**
