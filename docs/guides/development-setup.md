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
python blc.py auth test

# Test Graph API
python blc.py graph users

# Test Dataverse connection
python blc.py dataverse test
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

### CLI Testing (Recommended)
```bash
# Test authentication
python blc.py auth test

# Test Graph API access
python blc.py graph users

# Test organization info
python blc.py graph org

# Test Dataverse connection
python blc.py dataverse test
```

**Expected Output:**
```
✅ Basic authentication successful!
✅ Organization access successful: [Your Organization]
👥 Found 73 users:
  • [User Name] ([email])
🏢 Organization: [Your Organization]
   ID: [org-id]
   Phone: [phone-number]
```

### Manual Testing
```bash
# Test authentication directly
python auth/graph.py

# Test Dataverse connection
python dataverse/list_tables.py
```

## 🖥️ CLI Usage

### Available Commands

```bash
# Show version and help
python blc.py --help
python blc.py version

# Authentication commands
python blc.py auth test      # Test authentication
python blc.py auth status    # Check token status

# Graph API commands
python blc.py graph users    # List users
python blc.py graph org      # Show organization info

# Dataverse commands
python blc.py dataverse list # List tables
python blc.py dataverse test # Test connection
```

### CLI Features
- **Rich output** with colors and formatting
- **Async support** for all operations
- **Error handling** with proper exit codes
- **Help system** with command documentation

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

#### 5. Dataverse 403 Error
**Problem**: `"The user is not a member of the organization"`

**Solution**:
- This is expected if Dataverse environment is not configured
- Dataverse requires separate environment setup
- Use Graph API commands for now

## 🔧 Development Workflow

### Running Scripts
```bash
# Use CLI for most operations
python blc.py [command] [action]

# Or run scripts directly with PYTHONPATH
PYTHONPATH=/path/to/life-cockpit python script.py
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
python blc.py auth test

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
│   └── list_tables.py  # Table listing (httpx implementation)
├── utils/              # Shared utilities
│   ├── __init__.py
│   ├── config.py       # Configuration management
│   └── logger.py       # Logging setup
├── tests/              # Test suite
├── logs/               # Application logs
├── docs/               # Documentation
├── blc.py              # CLI entry point
├── .env                # Environment variables (gitignored)
├── env.example         # Environment template
├── requirements.txt    # Python dependencies
└── README.md          # Project overview
```

## 🎯 Next Steps

After completing setup:

1. **Configure Dataverse environment** (if needed)
2. **Build workflow modules** (email automation, reminders)
3. **Add more CLI commands** for business operations
4. **Implement automation workflows**

## 📚 Additional Resources

- [Project Log](../project_log.md) - Development progress and lessons learned
- [Architecture](../architecture.md) - System design overview
- [Roadmap](../roadmap.md) - Development phases and goals
- [Microsoft Graph API Documentation](https://docs.microsoft.com/en-us/graph/)
- [Azure Identity Documentation](https://docs.microsoft.com/en-us/python/api/overview/azure/identity-readme)
- [Typer CLI Documentation](https://typer.tiangolo.com/)
- [httpx Documentation](https://www.python-httpx.org/)

---

*Last Updated: August 20, 2025*
