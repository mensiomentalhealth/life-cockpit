# Life Cockpit MVP Quick Start

**Safe Tinkering with Guardrails and Logic Apps Integration**

This guide will get you up and running with the MVP implementation in under 10 minutes, including safety guardrails and Logic Apps integration to replace Power Automate.

## 🚀 **Quick Setup (5 minutes)**

### **1. Environment Setup**
```bash
# Clone and setup (if not already done)
cd life-cockpit
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Enable Safety Guardrails**
```bash
# Enable local sandbox mode for safe development
export BLC_LOCAL_SANDBOX=true
export BLC_DRY_RUN_DEFAULT=true
export BLC_REQUIRE_APPROVAL=true

# Or set in your .env file
echo "BLC_LOCAL_SANDBOX=true" >> .env
echo "BLC_DRY_RUN_DEFAULT=true" >> .env
echo "BLC_REQUIRE_APPROVAL=true" >> .env
```

### **3. Test the System**
```bash
# Test basic functionality
python blc.py auth test
python blc.py dataverse test

# Test guardrails
python blc.py guardrails list
```

## 🛡️ **Safety Guardrails Overview**

### **Dry-Run Default**
All operations are safe by default - they show what they would do without making changes.

### **Approval Workflows**
Operations require explicit approval with `--approve` flag.

### **Run ID Tracking**
Every operation gets a unique ID for audit trails.

### **Classification System**
Operations are tagged as personal/business/clinical with different safety levels.

## 🎮 **Try It Out**

### **1. Test Guardrails**
```bash
# List active runs
python blc.py guardrails list

# Create a test run (will be in dry-run mode)
python blc.py functions test-webhook

# Check run status
python blc.py guardrails status
# Enter the run ID when prompted
```

### **2. Test Logic Apps Integration**
```bash
# List Logic Apps workflows
python blc.py logic-apps list

# Create a webhook listener (dry-run)
python blc.py logic-apps create
# Choose: webhook
# Name: test-webhook-listener
# Function URL: https://your-function.azurewebsites.net/api/webhook
```

### **3. Test Azure Functions**
```bash
# Test webhook processing
python blc.py functions test-webhook
# Entity: accounts
# Operation: Create

# Test email automation
python blc.py functions send-email
# To: test@example.com
# Subject: Test Email
# Body: This is a test email

# Test scheduled tasks
python blc.py functions execute-task
# Task: daily_backup
```

### **4. Sandbox Mode**
```bash
# Enable sandbox mode
python blc.py sandbox enable

# Test operations (they'll use mock data)
python blc.py dataverse list

# Export sandbox data
python blc.py sandbox export

# Reset sandbox data
python blc.py sandbox reset
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Safety Settings
BLC_LOCAL_SANDBOX=true          # Use mock services
BLC_DRY_RUN_DEFAULT=true        # Safe by default
BLC_REQUIRE_APPROVAL=true       # Require approval
BLC_CLASSIFICATION_ENFORCEMENT=true

# Azure Settings
AZURE_SUBSCRIPTION_ID=your_subscription_id
AZURE_RESOURCE_GROUP=life-cockpit-rg
AZURE_LOCATION=Canada East

# Function URLs (when ready)
AZURE_FUNCTION_DATAVERSE_WEBHOOK_URL=https://your-function.azurewebsites.net/api/webhook
AZURE_FUNCTION_EMAIL_AUTOMATION_URL=https://your-function.azurewebsites.net/api/email
AZURE_FUNCTION_SCHEDULED_TASK_URL=https://your-function.azurewebsites.net/api/task
```

### **Classification Levels**
- **Personal**: No approval needed, light safety
- **Business**: Single approval, moderate safety
- **Clinical**: Dual approval, strict safety

## 📋 **Common Workflows**

### **Replace Power Automate Webhook**
```bash
# 1. Create Logic App webhook listener
python blc.py logic-apps create
# Type: webhook
# Name: dataverse-webhook-listener
# Function URL: your-azure-function-url

# 2. Test webhook processing
python blc.py functions test-webhook
# Entity: accounts
# Operation: Create

# 3. Check run status
python blc.py guardrails list
```

### **Multi-Channel Message Automation**
```bash
# 1. Create message automation Logic App
python blc.py logic-apps create
# Type: scheduled
# Name: scheduled-messages-processor
# Function URL: your-message-function-url

# 2. Test message processing
python blc.py functions test-message-processor
# This processes all message types (email, SMS, Teams, etc.)

# 3. Approve if needed
python blc.py guardrails approve
# Enter run ID when prompted
```

### **Scheduled Tasks**
```bash
# 1. Create scheduled task Logic App
python blc.py logic-apps create
# Type: scheduled
# Name: daily-backup
# Function URL: your-task-function-url
# Schedule: 0 2 * * * (daily at 2 AM)

# 2. Test task execution
python blc.py functions execute-task
# Task: daily_backup
```

## 🔍 **Monitoring & Debugging**

### **Check Run Status**
```bash
# List all runs
python blc.py guardrails list

# Check specific run
python blc.py guardrails status
# Enter run ID when prompted
```

### **Sandbox Data**
```bash
# Export current sandbox state
python blc.py sandbox export

# Import sandbox data
python blc.py sandbox import

# Reset sandbox data
python blc.py sandbox reset
```

### **Logic Apps Status**
```bash
# List workflows
python blc.py logic-apps list

# Get workflow details
python blc.py logic-apps get
# Enter workflow name when prompted
```

## 🚨 **Safety Features**

### **Dry-Run Mode**
- All operations show what they would do
- No actual changes made
- Safe for experimentation

### **Approval Required**
- Operations need explicit approval
- Use `--approve` flag for actual execution
- Clinical operations require dual approval

### **Audit Trail**
- Every operation logged with run ID
- Complete audit trail
- Track all changes and approvals

### **Classification Enforcement**
- Operations tagged by risk level
- Different safety requirements per classification
- Automatic enforcement of safety rules

## 🔄 **Next Steps**

### **Phase 1: Safe Tinkering (Week 1)**
- ✅ Set up guardrails
- ✅ Test sandbox mode
- ✅ Create Logic Apps workflows
- ✅ Test Azure Functions

### **Phase 2: Real Integration (Week 2)**
- Deploy Azure Functions
- Connect to real Dataverse
- Set up Logic Apps triggers
- Test with real data

### **Phase 3: Production (Week 3)**
- Deploy to staging
- Test with synthetic data
- Deploy to production
- Monitor and optimize

## 🆘 **Troubleshooting**

### **Common Issues**

**Guardrails not working**
```bash
# Check environment variables
echo $BLC_LOCAL_SANDBOX
echo $BLC_DRY_RUN_DEFAULT

# Re-enable sandbox mode
python blc.py sandbox enable
```

**Logic Apps not found**
```bash
# Check Azure credentials
python blc.py auth test

# List Logic Apps
python blc.py logic-apps list
```

**Functions not responding**
```bash
# Test function connectivity
python blc.py functions test-webhook

# Check function URLs in environment
echo $AZURE_FUNCTION_DATAVERSE_WEBHOOK_URL
```

### **Getting Help**
- Check run status: `python blc.py guardrails list`
- Export sandbox data: `python blc.py sandbox export`
- Reset everything: `python blc.py sandbox reset`

---

**You're now ready to safely tinker and automate!** 🎉

*This MVP gives you the foundation to replace Power Automate with Logic Apps and Azure Functions while maintaining complete safety and control.*
