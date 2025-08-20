# Troubleshooting Guide

Common issues and their solutions when working with Life Cockpit.

## 🚨 Authentication Issues

### 403 Authorization_RequestDenied

**Symptoms:**
```
❌ Organization access failed: Authorization_RequestDenied
💡 This suggests missing 'Organization.Read.All' permission
```

**Causes:**
- Missing Azure AD permissions
- Wrong permission type (Delegated vs Application)
- Admin consent not granted

**Solutions:**
1. **Check Permission Type:**
   - Go to Azure Portal → App Registrations → Your App → API Permissions
   - Ensure permissions are **Application** (not Delegated)
   - Required permissions: `Organization.Read.All`, `User.Read.All`

2. **Grant Admin Consent:**
   - Click "Grant admin consent" button in API Permissions
   - Wait 5-10 minutes for propagation

3. **Verify App Registration:**
   - Ensure app has Client Secret configured
   - Check Tenant ID matches your organization

### ModuleNotFoundError: No module named 'utils'

**Symptoms:**
```
ModuleNotFoundError: No module named 'utils'
```

**Causes:**
- Running script from wrong directory
- Python path not set correctly

**Solutions:**
```bash
# Run from project root
cd /path/to/life-cockpit
python auth/graph.py

# Or set PYTHONPATH
export PYTHONPATH="/path/to/life-cockpit:$PYTHONPATH"
python auth/graph.py
```

### 401 Unauthorized

**Symptoms:**
```
❌ Authentication failed: 401 Unauthorized
```

**Causes:**
- Invalid client credentials
- Expired client secret
- Wrong tenant ID

**Solutions:**
1. **Regenerate Client Secret:**
   - Azure Portal → App Registrations → Your App → Certificates & Secrets
   - Create new client secret
   - Update `.env` file

2. **Verify Credentials:**
   ```bash
   # Check environment variables
   echo $AZURE_CLIENT_ID
   echo $AZURE_TENANT_ID
   # Don't echo client secret for security
   ```

## 🔧 Configuration Issues

### ValueError: Configuration validation failed

**Symptoms:**
```
ValueError: Configuration validation failed
```

**Causes:**
- Missing required environment variables
- Invalid environment variable values

**Solutions:**
1. **Check .env file:**
   ```bash
   # Ensure all required variables are set
   AZURE_CLIENT_ID=your_client_id
   AZURE_CLIENT_SECRET=your_client_secret
   AZURE_TENANT_ID=your_tenant_id
   DATAVERSE_URL=https://your-org.crm.dynamics.com
   ```

2. **Validate format:**
   - No quotes around values
   - No trailing spaces
   - Correct URLs

### Environment Variables Not Loading

**Symptoms:**
```
❌ Configuration error: Missing required environment variables
```

**Causes:**
- `.env` file not in project root
- `python-dotenv` not installed
- Wrong file name

**Solutions:**
```bash
# Ensure .env file exists in project root
ls -la .env

# Install python-dotenv if missing
pip install python-dotenv

# Check file permissions
chmod 600 .env
```

## 📊 Dataverse Issues

### 403 Forbidden: The user is not a member of the organization

**Symptoms:**
```
❌ Dataverse API call failed: 403 - The user is not a member of the organization
```

**Causes:**
- Service principal not added to Dataverse environment
- Wrong Dataverse URL
- Missing Dataverse permissions

**Solutions:**
1. **Add Service Principal to Dataverse:**
   - Go to Dataverse environment → Settings → Security → Users
   - Add new user with service principal email
   - Assign appropriate security roles

2. **Verify Dataverse URL:**
   ```bash
   # Check URL format
   DATAVERSE_URL=https://your-org.crm.dynamics.com
   ```

3. **Check Permissions:**
   - Ensure app has Dataverse permissions in Azure AD
   - Grant admin consent for Dataverse permissions

### 404 Not Found: EntityDefinitions

**Symptoms:**
```
❌ Dataverse API call failed: 404 - Not Found
```

**Causes:**
- Wrong API endpoint
- Invalid Dataverse URL
- API version mismatch

**Solutions:**
1. **Verify API endpoint:**
   ```python
   # Correct endpoint format
   api_url = f"{dataverse_url}/api/data/v9.2/EntityDefinitions"
   ```

2. **Check Dataverse URL:**
   - Ensure URL is correct and accessible
   - Test in browser: `https://your-org.crm.dynamics.com`

## 🔄 Async/Await Issues

### RuntimeWarning: coroutine was never awaited

**Symptoms:**
```
RuntimeWarning: coroutine 'test_graph_connection' was never awaited
```

**Causes:**
- Calling async function without await
- Not running in async context

**Solutions:**
```python
# Correct async usage
async def main():
    success = await test_graph_connection()
    print(f"Result: {success}")

# Run with asyncio
import asyncio
asyncio.run(main())
```

### TypeError: 'coroutine' object is not iterable

**Symptoms:**
```
TypeError: 'coroutine' object is not iterable
```

**Causes:**
- Using async function in sync context
- Missing await keyword

**Solutions:**
```python
# Wrong
result = test_graph_connection()

# Correct
result = await test_graph_connection()
```

## 🐍 Python Environment Issues

### ImportError: No module named 'msgraph'

**Symptoms:**
```
ImportError: No module named 'msgraph'
```

**Causes:**
- Dependencies not installed
- Wrong virtual environment
- Missing requirements

**Solutions:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep msgraph
```

### Version Conflicts

**Symptoms:**
```
ImportError: cannot import name 'X' from 'Y'
```

**Causes:**
- Incompatible package versions
- Conflicting dependencies

**Solutions:**
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Check for conflicts
pip check

# Recreate virtual environment if needed
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🖥️ CLI Issues

### Command Not Found: blc

**Symptoms:**
```
bash: blc: command not found
```

**Causes:**
- Running from wrong directory
- Python path issues
- Script not executable

**Solutions:**
```bash
# Run from project root
python blc.py --help

# Make executable (optional)
chmod +x blc.py
./blc.py --help
```

### Typer Command Errors

**Symptoms:**
```
Error: No such command 'xyz'
```

**Causes:**
- Invalid command name
- Missing command implementation
- Typer version issues

**Solutions:**
```bash
# Check available commands
python blc.py --help

# Check Typer version
pip show typer

# Update Typer if needed
pip install --upgrade typer
```

## 🔍 Debugging Tips

### Enable Debug Logging

```bash
# Set debug level
export LOG_LEVEL=DEBUG

# Run with verbose output
python blc.py auth test --verbose
```

### Check Token Details

```python
# Add to your code for debugging
from auth.graph import get_auth_manager

auth_manager = get_auth_manager()
credential = auth_manager._credential
token = credential.get_token("https://graph.microsoft.com/.default")
print(f"Token expires: {token.expires_on}")
print(f"Token scopes: {token.scopes}")
```

### Test Individual Components

```bash
# Test authentication only
python -c "from auth.graph import get_auth_manager; print('Auth OK')"

# Test configuration only
python -c "from utils.config import get_config; print('Config OK')"

# Test CLI only
python blc.py version
```

## 📞 Getting Help

### Before Asking for Help

1. **Check this guide** for your specific error
2. **Enable debug logging** and capture full error output
3. **Test individual components** to isolate the issue
4. **Check recent changes** that might have caused the problem

### Information to Include

When reporting issues, include:
- **Error message** (full text)
- **Command that failed**
- **Environment details** (OS, Python version)
- **Recent changes** made
- **Debug logs** if available

### Resources

- **Project Log**: [docs/project_log.md](project_log.md) - Recent issues and solutions
- **Development Setup**: [docs/guides/development-setup.md](guides/development-setup.md) - Setup guide
- **API Reference**: [docs/api-reference.md](api-reference.md) - Technical details

---

*Last Updated: August 20, 2025*
