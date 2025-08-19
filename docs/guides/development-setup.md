# Development Setup Guide

This guide walks you through setting up the Life Cockpit development environment, including authentication, dependencies, and testing.

## 🚀 Quick Setup

### Prerequisites
- Python 3.8+ installed
- Git installed
- Access to Microsoft 365 tenant
- Azure AD app registration (see [Authentication Setup](#authentication-setup))

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd life-cockpit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp env.example .env

# Edit .env with your credentials
nano .env  # or your preferred editor
```

### 3. Test Setup
```bash
# Test basic setup
python test_setup.py

# Test authentication
PYTHONPATH=/path/to/life-cockpit python auth/graph.py

# Test Dataverse connection
PYTHONPATH=/path/to/life-cockpit python dataverse/list_tables.py
```

## 🔐 Authentication Setup

### Azure AD App Registration

1. **Go to Azure Portal** → Azure Active Directory → App registrations
2. **Create new registration** or use existing app
3. **Configure authentication**:
   - Supported account types: "Accounts in this organizational directory only"
   - Platform configuration: Web (for client credentials flow)

### Required API Permissions

Add these **Application permissions** (not Delegated):

#### Microsoft Graph Permissions
- `Application.Read.All` - Read application registrations
- `Organization.Read.All` - Read organization information  
- `User.Read.All` - Read all users in directory

#### Dataverse Permissions (for future use)
- `user_impersonation` - Dynamics CRM access

### Grant Admin Consent

After adding permissions:
1. Go to **API permissions** in your app registration
2. Click **"Grant admin consent for [Your Organization]"**
3. Confirm the action

### Environment Variables

Configure these in your `.env` file:

```bash
# Microsoft Graph API Configuration
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here
AZURE_TENANT_ID=your_tenant_id_here

# Dataverse Configuration
DATAVERSE_URL=https://your-org.crm.dynamics.com

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/cockpit.log

# Application Configuration
APP_NAME=life-cockpit
APP_VERSION=1.0.0
```

## 🧪 Testing Your Setup

### Authentication Test
```bash
PYTHONPATH=/path/to/life-cockpit python auth/graph.py
```

**Expected Output:**
```
✅ Basic authentication successful!
✅ Token acquired successfully
✅ Organization access successful: [Your Organization]
🎉 Graph API connection test completed successfully!
```

### Dataverse Test
```bash
PYTHONPATH=/path/to/life-cockpit python dataverse/list_tables.py
```

**Expected Output:**
```
✅ Microsoft Graph API connection successful!
✅ Dataverse table listing completed successfully!
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Authorization_RequestDenied (403)
**Problem**: `Insufficient privileges to complete the operation`

**Solution**: 
- Ensure you're using **Application permissions** (not Delegated)
- Grant admin consent for all permissions
- Check that your app registration has the correct permissions

#### 2. ModuleNotFoundError
**Problem**: `No module named 'utils'`

**Solution**:
```bash
# Set Python path when running scripts
PYTHONPATH=/path/to/life-cockpit python script.py

# Or add to your shell profile
export PYTHONPATH="/path/to/life-cockpit:$PYTHONPATH"
```

#### 3. Async/Await Issues
**Problem**: `RuntimeWarning: coroutine was never awaited`

**Solution**:
- Ensure all async functions are properly awaited
- Use `asyncio.run()` in main functions
- Check for mixed sync/async code

#### 4. Token Issues
**Problem**: Authentication fails with token errors

**Solution**:
- Verify client ID, secret, and tenant ID
- Check that app registration is properly configured
- Ensure admin consent is granted

## 🔧 Development Workflow

### Running Scripts
```bash
# Always set PYTHONPATH for imports to work
PYTHONPATH=/path/to/life-cockpit python script.py

# Or activate virtual environment and set path
source .venv/bin/activate
export PYTHONPATH="/path/to/life-cockpit:$PYTHONPATH"
python script.py
```

### Adding New Dependencies
```bash
# Install new package
pip install new-package

# Update requirements.txt
pip freeze > requirements.txt
```

### Testing Changes
```bash
# Test authentication changes
python auth/graph.py

# Test configuration changes
python -c "from utils.config import get_config; print(get_config())"

# Run all tests
python test_setup.py
```

## 📁 Project Structure

```
life-cockpit/
├── auth/               # Graph API authentication
│   ├── __init__.py
│   └── graph.py        # Authentication manager
├── dataverse/          # Dataverse operations
│   ├── __init__.py
│   └── list_tables.py  # Table listing (mock)
├── utils/              # Shared utilities
│   ├── __init__.py
│   ├── config.py       # Configuration management
│   └── logger.py       # Logging setup
├── tests/              # Test suite
├── logs/               # Application logs
├── docs/               # Documentation
├── .env                # Environment variables (gitignored)
├── env.example         # Environment template
├── requirements.txt    # Python dependencies
└── README.md          # Project overview
```

## 🎯 Next Steps

After completing setup:

1. **Implement real Dataverse connection** (replace mock data)
2. **Add CLI interface** for easier testing
3. **Build first workflow module** (email automation)
4. **Add more comprehensive tests**

## 📚 Additional Resources

- [Project Log](../project_log.md) - Development progress and lessons learned
- [Architecture](../architecture.md) - System design overview
- [Roadmap](../roadmap.md) - Development phases and goals
- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Azure Identity Documentation](https://docs.microsoft.com/en-us/python/api/overview/azure/identity-readme)

---

*Last Updated: August 19, 2025*
