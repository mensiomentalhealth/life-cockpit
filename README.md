# Life Cockpit - Personal Automation & AI Environment

A modular Python-based automation environment for Microsoft 365 ecosystem integration, built to replace GUI workflows with script-based automation.

## 🎯 Project Goals

- **Replace GUI workflows** (Power Automate, etc.) with script-based automation
- **Integrate Microsoft 365 ecosystem** (Graph API, Dataverse, Logic Apps)
- **Modular and reusable** architecture
- **Multiple execution contexts** (terminal, Cursor, external triggers)

## 🏗️ Architecture

```
life-cockpit/
├── auth/               # Graph API / Azure auth logic
│   └── graph.py
├── dataverse/          # Dataverse operations
│   └── list_tables.py
├── sessions/           # Session-related logic
│   └── get_sessions.py
├── reminders/          # Reminder workflows
│   └── send_reminders.py
├── stripe/             # Stripe logic
│   └── charge_client.py
├── utils/              # Shared functions (logging, config, etc.)
│   ├── logger.py
│   └── config.py
├── tests/              # Test suite
├── logs/               # Application logs
├── .env                # Secrets (gitignored)
├── env.example         # Environment template
├── requirements.txt
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

2. **Test Connection**
   ```bash
   python dataverse/list_tables.py
   ```

## 🔧 Configuration

- **Microsoft Graph API**: OAuth2 authentication
- **Dataverse**: Service principal authentication
- **Logging**: Structured logging with rotation
- **Secrets**: Environment-based secure handling

## 📋 Current Scripts

- `dataverse/list_tables.py` - Authenticate and list Dataverse tables
- More coming soon...

## 🔐 Security

- All secrets stored in `.env` (gitignored)
- OAuth2 flow for Microsoft Graph
- Service principal for Dataverse
- No hardcoded credentials

## 📝 Development

This project uses:
- Python 3.8+
- Microsoft Graph SDK
- Dataverse SDK
- Structured logging
- Modular architecture


## �� Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- **[Documentation Index](docs/index.md)** - Start here for navigation
- **[Architecture](docs/architecture.md)** - System design overview
- **[Setup Guide](docs/setup.md)** - Installation and configuration
- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[Contributing](docs/contributing.md)** - How to contribute to the project
---

*Built for automation, designed for productivity.*
