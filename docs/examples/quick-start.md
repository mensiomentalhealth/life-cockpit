# Quick Start Guide - 5 Minutes to Life Cockpit

Get Life Cockpit running on a new machine in under 5 minutes!

## ⚡ Super Quick Setup

### 1. Clone & Setup (1 minute)
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

### 2. Configure Environment (2 minutes)
```bash
# Copy environment template
cp env.example .env

# Edit with your credentials
nano .env  # or your preferred editor
```

**Required in `.env`:**
```bash
AZURE_CLIENT_ID=your_client_id_here
AZURE_CLIENT_SECRET=your_client_secret_here
AZURE_TENANT_ID=your_tenant_id_here
DATAVERSE_URL=https://your-org.crm.dynamics.com
```

### 3. Test Everything (2 minutes)
```bash
# Test authentication
python blc.py auth test

# Test Graph API
python blc.py graph users

# Test organization info
python blc.py graph org
```

## 🎯 Expected Results

### ✅ Successful Authentication
```
✅ Basic authentication successful!
✅ Organization access successful: [Your Organization]
🎉 Full authentication and API test completed successfully!
```

### ✅ User List
```
👥 Found 73 users:
  • [User Name] ([email])
  • [User Name] ([email])
  ... and 63 more
```

### ✅ Organization Info
```
🏢 Organization: [Your Organization]
   ID: [org-id]
   Phone: [phone-number]
```

## 🚨 If Something Goes Wrong

### Authentication Fails
- Check your Azure AD app registration
- Ensure Application permissions (not Delegated)
- Grant admin consent for permissions

### Module Import Errors
```bash
# Set Python path
export PYTHONPATH="/path/to/life-cockpit:$PYTHONPATH"
```

### Dataverse 403 Error
- Expected if Dataverse not configured
- Use Graph API commands for now

## 🚀 Next Steps

Once basic setup works:

1. **Explore CLI commands:**
   ```bash
   python blc.py --help
   python blc.py version
   ```

2. **Test Dataverse (if configured):**
   ```bash
   python blc.py dataverse test
   ```

3. **Start building workflows:**
   - Check out the [Development Setup Guide](../guides/development-setup.md)
   - Review the [Architecture](../architecture.md)
   - Explore the [Project Log](../project_log.md)

## 📚 Need Help?

- **Setup Issues**: [Development Setup Guide](../guides/development-setup.md)
- **Authentication**: [Troubleshooting](../troubleshooting.md)
- **Architecture**: [Architecture Overview](../architecture.md)
- **Progress**: [Project Log](../project_log.md)

---

**Time to complete**: ~5 minutes  
**Prerequisites**: Python 3.8+, Git, Azure AD app registration  
**Status**: Ready for development! 🎉
