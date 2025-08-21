# Multi-Channel Message Automation Workflow

**Scheduled Messages Queue Processing**

This document outlines the multi-channel message automation workflow that processes scheduled messages from client sessions and replaces the Power Automate script. Supports email, SMS, Teams, Telegram, and WhatsApp.

## 📋 **Current Process Flow**

### **1. Message Creation (Dynamics)**
```
Client Session Status = 'fulfilled'
    ↓
Trigger: Create scheduled email
    ↓
Copy session data to scheduled message
    ↓
Set sendTime = session end time
    ↓
Set status = 'draft'
```

### **2. Manual Review (Dynamics)**
```
Review scheduled messages queue
    ↓
Approve messages → status = 'revised'
    ↓
Reject messages → status = 'cancelled'
```

### **3. Automated Processing (Power Automate → Logic Apps)**
```
Periodic trigger (every 15 minutes)
    ↓
Query scheduled messages where:
  - status = 'revised'
  - sendTime <= utcNow()
    ↓
Process each message:
  - Route to appropriate service (email/SMS/Teams/Telegram/WhatsApp)
  - Send via channel-specific service
  - Log to messages_log
  - Update status = 'sent'
  - Set processedTime = utcNow()
```

## 🏗️ **Dataverse Schema**

### **Scheduled Messages Table**
```sql
-- scheduled_messages table
CREATE TABLE scheduled_messages (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    session_id NVARCHAR(255),           -- Reference to client session
    client_id NVARCHAR(255),            -- Client identifier
    message_type NVARCHAR(50),          -- 'email', 'sms', 'telegram', 'whatsapp'
    recipient NVARCHAR(255),            -- Email address, phone number, etc.
    subject NVARCHAR(500),              -- Email subject (for emails)
    body NVARCHAR(MAX),                 -- Message content
    template NVARCHAR(100),             -- Template used
    send_time DATETIME2,                -- When to send the message
    status NVARCHAR(50),                -- 'draft', 'revised', 'sent', 'cancelled', 'failed'
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE(),
    processed_time DATETIME2,           -- When message was processed
    error_message NVARCHAR(MAX),        -- Error details if failed
    metadata NVARCHAR(MAX)              -- JSON metadata
);
```

### **Messages Log Table**
```sql
-- messages_log table
CREATE TABLE messages_log (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    message_id UNIQUEIDENTIFIER,        -- Reference to scheduled_message
    message_type NVARCHAR(50),          -- 'email', 'sms', 'telegram', 'whatsapp'
    recipient NVARCHAR(255),            -- Recipient address
    subject NVARCHAR(500),              -- Subject (for emails)
    body NVARCHAR(MAX),                 -- Message content
    status NVARCHAR(50),                -- 'sent', 'delivered', 'failed'
    sent_at DATETIME2 DEFAULT GETUTCDATE(),
    delivered_at DATETIME2,             -- When message was delivered
    error_message NVARCHAR(MAX),        -- Error details if failed
    provider NVARCHAR(100),             -- Email/SMS provider used
    message_id_external NVARCHAR(255),  -- External provider message ID
    metadata NVARCHAR(MAX)              -- JSON metadata
);
```

## 🔄 **Replacement Architecture**

### **Current: Power Automate**
```
Power Automate Flow
    ↓
Outlook Connector
    ↓
Dataverse Updates
```

### **New: Logic Apps + Azure Functions**
```
Logic App (Scheduled Trigger)
    ↓
Azure Function (Message Processor)
    ↓
Multi-Channel Services:
  - Email (SendGrid/SMTP)
  - SMS (Twilio)
  - Teams (Microsoft Graph)
  - Telegram (Bot API)
  - WhatsApp (Business API)
    ↓
Dataverse Updates
```

## 🚀 **Implementation Plan**

### **Phase 1: Core Message Processing**
- [ ] **Azure Function**: Message processor for multi-channel sending
- [ ] **Logic App**: Scheduled trigger (every 15 minutes)
- [ ] **Dataverse Integration**: Query and update scheduled messages
- [ ] **Email Service**: SendGrid integration for email sending
- [ ] **SMS Service**: Twilio integration for text messages
- [ ] **Logging**: Update messages_log table

### **Phase 2: Advanced Channel Support**
- [ ] **Teams Integration**: Microsoft Graph API for Teams messages
- [ ] **Telegram Integration**: Telegram Bot API
- [ ] **WhatsApp Integration**: WhatsApp Business API
- [ ] **Channel Routing**: Intelligent routing to appropriate service
- [ ] **Template Engine**: Channel-specific message templates

### **Phase 3: Advanced Features**
- [ ] **Retry Logic**: Failed message retry with exponential backoff
- [ ] **Rate Limiting**: Respect provider rate limits
- [ ] **Template Engine**: Dynamic message templating
- [ ] **Analytics**: Message delivery tracking and reporting

## 🔧 **Technical Implementation**

### **Azure Function: Message Processor**
```python
@safe_operation(Classification.BUSINESS, "scheduled-message-process")
async def process_scheduled_messages(run_id: str, dry_run: bool = False):
    """Process scheduled messages from the queue"""
    
    # Query pending messages
    messages = await dataverse.query_records(
        'scheduled_messages',
        filter="status eq 'revised' and send_time le utcNow()"
    )
    
    results = []
    for message in messages:
        try:
            # Process based on message type
            if message['message_type'] == 'email':
                result = await process_email_message(message, dry_run)
            elif message['message_type'] == 'sms':
                result = await process_sms_message(message, dry_run)
            # ... other message types
            
            results.append(result)
            
        except Exception as e:
            # Log error and mark message as failed
            await mark_message_failed(message['id'], str(e))
            results.append({'status': 'failed', 'error': str(e)})
    
    return {
        'processed_count': len(results),
        'success_count': len([r for r in results if r['status'] == 'success']),
        'failed_count': len([r for r in results if r['status'] == 'failed']),
        'results': results
    }
```

### **Logic App Workflow**
```json
{
  "triggers": {
    "recurrence": {
      "recurrence": {
        "frequency": "Minute",
        "interval": 15
      },
      "type": "Recurrence"
    }
  },
  "actions": {
    "process_messages": {
      "type": "Http",
      "inputs": {
        "method": "POST",
        "uri": "https://your-function.azurewebsites.net/api/process-scheduled-messages",
        "headers": {
          "Content-Type": "application/json"
        },
        "body": {
          "run_id": "@guid()",
          "timestamp": "@utcNow()"
        }
      }
    }
  }
}
```

## 📊 **Message Processing Logic**

### **Multi-Channel Message Processing**
```python
async def process_message(message: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
    """Process a message based on its type"""
    
    message_type = message.get('message_type', 'email')
    
    if dry_run:
        return {
            'status': 'dry_run',
            'message_id': message['id'],
            'message_type': message_type,
            'recipient': message['recipient']
        }
    
    try:
        # Route to appropriate service based on message type
        if message_type == 'email':
            result = await process_email_message(message)
        elif message_type == 'sms':
            result = await process_sms_message(message)
        elif message_type == 'teams':
            result = await process_teams_message(message)
        elif message_type == 'telegram':
            result = await process_telegram_message(message)
        elif message_type == 'whatsapp':
            result = await process_whatsapp_message(message)
        else:
            raise ValueError(f"Unsupported message type: {message_type}")
        
        # Log to messages_log
        await log_message_sent(
            message_id=message['id'],
            message_type=message_type,
            recipient=message['recipient'],
            subject=message.get('subject'),
            body=message['body'],
            provider=result['provider'],
            external_id=result['external_id']
        )
        
        # Update scheduled message status
        await update_message_status(
            message_id=message['id'],
            status='sent',
            processed_time=datetime.utcnow().isoformat()
        )
        
        return result
        
    except Exception as e:
        # Mark message as failed
        await update_message_status(
            message_id=message['id'],
            status='failed',
            error_message=str(e)
        )
        raise
```

### **Channel-Specific Processing**
```python
async def process_email_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process an email message via SendGrid"""
    email_result = await sendgrid_service.send_email(
        to=message['recipient'],
        subject=message['subject'],
        body=message['body'],
        template=message.get('template')
    )
    return {
        'status': 'success',
        'external_id': email_result['message_id'],
        'provider': 'sendgrid'
    }

async def process_sms_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process an SMS message via Twilio"""
    sms_result = await twilio_service.send_sms(
        to=message['recipient'],
        body=message['body']
    )
    return {
        'status': 'success',
        'external_id': sms_result['message_id'],
        'provider': 'twilio'
    }

async def process_teams_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process a Teams message via Microsoft Graph"""
    teams_result = await teams_service.send_message(
        channel_id=message['channel_id'],
        body=message['body']
    )
    return {
        'status': 'success',
        'external_id': teams_result['message_id'],
        'provider': 'microsoft_graph'
    }

async def process_telegram_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process a Telegram message via Bot API"""
    telegram_result = await telegram_service.send_message(
        chat_id=message['chat_id'],
        text=message['body']
    )
    return {
        'status': 'success',
        'external_id': telegram_result['message_id'],
        'provider': 'telegram'
    }

async def process_whatsapp_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """Process a WhatsApp message via Business API"""
    whatsapp_result = await whatsapp_service.send_message(
        to=message['recipient'],
        message=message['body']
    )
    return {
        'status': 'success',
        'external_id': whatsapp_result['message_id'],
        'provider': 'whatsapp_business'
    }
```

## 🛡️ **Safety & Compliance**

### **Guardrails**
- **Dry-run mode**: Test without sending actual messages
- **Approval workflow**: Require approval for message processing
- **Rate limiting**: Respect email/SMS provider limits
- **Error handling**: Comprehensive error logging and retry logic

### **Compliance**
- **HIPAA compliance**: Ensure no PHI in error logs
- **Audit trail**: Complete logging of all message processing
- **Data retention**: Proper cleanup of old message logs
- **Access controls**: Secure access to message processing

## 🔍 **Monitoring & Debugging**

### **Key Metrics**
- Messages processed per run
- Success/failure rates
- Processing time
- Provider response times
- Error rates by message type

### **Logging**
- All message processing attempts
- Provider responses
- Error details (sanitized)
- Performance metrics

### **Alerts**
- High failure rates
- Provider outages
- Processing delays
- Queue backlogs

## 🚀 **Deployment Steps**

### **1. Create Azure Function**
```bash
# Deploy message processor function
python blc.py functions deploy message-processor
```

### **2. Create Logic App**
```bash
# Create scheduled trigger Logic App
python blc.py logic-apps create
# Type: scheduled
# Name: scheduled-messages-processor
# Function URL: https://your-function.azurewebsites.net/api/process-scheduled-messages
# Schedule: */15 * * * * (every 15 minutes)
```

### **3. Test with Sandbox**
```bash
# Enable sandbox mode
python blc.py sandbox enable

# Test message processing
python blc.py functions test-message-processor
```

### **4. Deploy to Production**
```bash
# Disable sandbox mode
python blc.py sandbox disable

# Test with real data
python blc.py functions test-message-processor --approve
```

---

*This workflow replaces the Power Automate script with a more robust, scalable, and maintainable solution using Logic Apps and Azure Functions.*
