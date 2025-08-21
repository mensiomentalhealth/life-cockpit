# Life Cockpit - Personal Automation & AI Environment

A modular Python-based automation environment for Microsoft 365 ecosystem integration, built to replace GUI workflows with script-based automation.

## 🎯 Project Goals

- **Replace GUI workflows** (Power Automate, etc.) with script-based automation
- **Integrate Microsoft 365 ecosystem** (Graph API, Dataverse, Logic Apps)
- **Multi-channel messaging automation** (Email, Teams, Telegram, SMS, WhatsApp)
- **Modular and reusable** architecture
- **Multiple execution contexts** (terminal, Cursor, external triggers)

## 🏗️ Architecture

```
life-cockpit/
├── auth/               # Graph API / Azure auth logic
│   └── graph.py
├── azure/              # Azure Functions & Logic Apps
│   ├── functions/      # Azure Functions
│   │   ├── dynamics_message_processor/  # Dynamics message processing
│   │   ├── webhook_receiver/            # Webhook handling
│   │   ├── host.json                    # Function app config
│   │   └── local.settings.json          # Local development
│   ├── logic-apps/     # Logic Apps workflows
│   ├── messaging.py    # Multi-channel messaging factory
│   ├── message_processor.py  # Message processing logic
│   └── dynamics_message_processor.py  # Dynamics integration
├── dataverse/          # Dataverse operations
│   ├── auth.py         # AAD auth for Dataverse (sync)
│   ├── client.py       # httpx client (sync, pooling)
│   ├── dev.py          # CRUD + metadata + notes + probe (sync)
│   ├── circuit_breaker.py
│   └── list_tables.py  # legacy
├── sessions/           # Session-related logic
│   └── get_sessions.py
├── reminders/          # Reminder workflows
│   └── send_reminders.py
├── stripe/             # Stripe logic
│   └── charge_client.py
├── utils/              # Shared functions (logging, config, etc.)
│   ├── logger.py
│   ├── config.py
│   └── sandbox.py      # Sandbox environment
├── web/                # FastAPI web dashboard
│   ├── main.py         # Web server
│   ├── routes/         # API routes
│   └── templates/      # HTML templates
├── scripts/            # Deployment scripts
├── tests/              # Test suite
├── docs/               # Documentation
├── logs/               # Application logs
├── .env                # Secrets (gitignored)
├── env.example         # Environment template
├── env.production.example  # Production environment template
├── requirements.txt
├── blc.py              # CLI interface
└── README.md
```

## 🚀 Quick Start

1. **Setup Environment**
   ```bash
   # Clone and setup
   git clone <your-repo>
   cd life-cockpit
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   cp env.example .env
   # Edit .env with your Microsoft 365 credentials
   ```

2. **Test Messaging System**
   ```bash
   # Test the messaging factory
   python test_messaging.py
   
   # Test Dynamics integration
   python test_dynamics_simple.py
   
   # Use CLI interface
   python blc.py messaging test
   python blc.py dynamics test
   ```

3. **Start Web Dashboard**
   ```bash
   python web/main.py
   # Visit http://localhost:8000
   ```

## 🔧 Configuration

- **Microsoft Graph API**: OAuth2 authentication for email/Teams
- **Dataverse**: Service principal authentication
- **Respond.io**: API integration for Telegram/SMS/WhatsApp
- **Logging**: Structured logging with rotation
- **Secrets**: Environment-based secure handling

## 📋 Current Scripts

### Core Messaging System ✅ **PRODUCTION READY**
- **`azure/messaging.py`** - Multi-channel messaging factory
- **`azure/dynamics_message_processor.py`** - Dynamics integration
- **`azure/message_processor.py`** - Message processing logic
- **`web/main.py`** - FastAPI web dashboard

### CLI Interface
- **`blc.py messaging`** - Messaging system management
- **`blc.py dynamics`** - Dynamics integration testing
- **`blc.py functions`** - Azure Functions testing
- **`blc.py dataverse`** / **`blc.py dv`** - Dataverse CRUD and diagnostics (see `docs/api/dataverse.md`)
- **`blc.py sandbox`** - Sandbox environment management

#### Dataverse quick commands (dv alias)

```bash
# Probe environment and identity
python blc.py dv probe
python blc.py dv whoami

# Entity metadata
python blc.py dv entity-def account

# Query records
python blc.py dv query account --top 5 --select "name,accountid"

# Get a specific record
python blc.py dv get account <guid> --select "name"

# Create a note on a record (impersonate optional)
echo "Session summary generated." > note.md
python blc.py dv note account <guid> --subject "Summary" --body-file note.md [--as-user <systemuserid>]
```

### Legacy Scripts
- `dataverse/list_tables.py` - Authenticate and list Dataverse tables
- More coming soon...

## 🔐 Security

- All secrets stored in `.env` (gitignored)
- OAuth2 flow for Microsoft Graph
- Service principal for Dataverse
- No hardcoded credentials

## 🎯 **PRODUCTION DEPLOYMENT STATUS**

### ✅ **Phase 1: Email Processing - COMPLETE**
- **Dynamics Integration**: Queries `cre92_scheduledmessage` table
- **Message Processing**: Handles `MessageStatus = 'Revised'` or `MessageStatus = 2`
- **Scheduling**: Processes messages where `ScheduledTimestamp <= utcNow()` and `Sent = false`
- **Status Updates**: Marks messages as sent with `Sent = true`, `SentAt`, and `ModifiedOn`
- **Logging**: Records to `messages_log` table
- **Testing**: ✅ Successfully tested with real Dynamics data

### 🚀 **Phase 2: Multi-Channel Support - READY**
- **Email**: Microsoft Graph API ✅
- **Teams**: Microsoft Graph API ✅
- **Telegram**: Respond.io integration ✅
- **SMS**: Respond.io integration ✅
- **WhatsApp**: Respond.io integration ✅

### 📊 **Architecture Benefits**
- **Replace Power Automate**: More robust, programmable automation
- **Multi-Provider**: Easy to swap messaging providers
- **Scalable**: Handles multiple message types and channels
- **Observable**: Comprehensive logging and monitoring
- **Testable**: Full test suite with sandbox environment

## 🚀 **Next Steps for Production**

1. **Deploy to Azure**
   - Azure Functions for message processing
   - Logic Apps for scheduling
   - Azure Key Vault for secrets

2. **Configure Production APIs**
   - Real Microsoft Graph API credentials
   - Respond.io API keys
   - Production Dynamics environment

3. **Set Up Monitoring**
   - Azure Application Insights
   - Custom dashboards
   - Alert notifications

4. **Add Telegram Support**
   - Configure Respond.io workspace
   - Test Telegram message flow
   - Deploy to production

## 📝 Development

This project uses:
- Python 3.8+
- Microsoft Graph SDK
- Dataverse SDK
- FastAPI for web dashboard
- Structured logging
- Modular architecture

### Dataverse Troubleshooting

See `docs/dataverse-troubleshooting.md` for common issues (timeouts, 401/403/404) and diagnostic commands.

### Environment Variables

```bash
# Dataverse
DATAVERSE_URL=https://your-org.crm.dynamics.com

# Azure AD (AAD)
AAD_CLIENT_ID=...
AAD_CLIENT_SECRET=...
AAD_TENANT_ID=...
```


## �� Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[Documentation Index](docs/index.md)** - Start here for navigation
- **[Architecture](docs/architecture.md)** - System design overview
- **[Setup Guide](docs/setup.md)** - Installation and configuration
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Contributing](docs/contributing.md)** - How to contribute to the project
---

*Built for automation, designed for productivity.*
