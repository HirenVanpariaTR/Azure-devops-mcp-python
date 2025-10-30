# Azure Web App Deployment Guide

## Prerequisites

1. **Azure Account**: Active Azure subscription
2. **Azure CLI**: Installed and logged in
3. **Azure DevOps**: Organization and PAT token ready

## Step 1: Prepare the Application

### Required Files
- `requirements.txt` - Python dependencies
- `startup.sh` or `startup.cmd` - Startup script
- Source code in `azure_devops_mcp/` directory

### Environment Variables to Set in Azure Web App
```
AZURE_DEVOPS_ORG=your-organization-name
```

## Step 2: Deploy to Azure Web App

### Option A: Deploy via Azure CLI

```bash
# 1. Create Resource Group
az group create --name rg-devops-mcp --location eastus

# 2. Create App Service Plan
az appservice plan create --name asp-devops-mcp --resource-group rg-devops-mcp --sku B1 --is-linux

# 3. Create Web App
az webapp create --name devops-mcp-server --resource-group rg-devops-mcp --plan asp-devops-mcp --runtime "PYTHON:3.11"

# 4. Configure Environment Variables
az webapp config appsettings set --name devops-mcp-server --resource-group rg-devops-mcp --settings AZURE_DEVOPS_ORG="tr-corp-legal-tracker"

# 5. Configure Startup Command (Option A - Bash script)
az webapp config set --name devops-mcp-server --resource-group rg-devops-mcp --startup-file "deploy/startup.sh"

# 5. Configure Startup Command (Option B - Python script, more reliable)
az webapp config set --name devops-mcp-server --resource-group rg-devops-mcp --startup-file "python deploy/startup.py"

# 6. Deploy Code (from project root)
az webapp up --name devops-mcp-server --resource-group rg-devops-mcp
```

### Option B: Deploy via Azure Portal

1. **Create Web App**:
   - Go to Azure Portal → Create Resource → Web App
   - Name: `devops-mcp-server`
   - Runtime: Python 3.11
   - Operating System: Linux
   - App Service Plan: Basic B1 or higher

2. **Configure Settings**:
   - Go to Configuration → Application Settings
   - Add: `AZURE_DEVOPS_ORG` = `your-organization-name`
   - General Settings → Startup Command: `deploy/startup.sh`

3. **Deploy Code**:
   - Use Deployment Center with GitHub, Azure Repos, or ZIP deploy
   - Upload the entire project folder

## Step 3: Test the Deployment

### Get the Web App URL
```bash
az webapp show --name devops-mcp-server --resource-group rg-devops-mcp --query "defaultHostName" --output tsv
```

### Test with curl
```bash
# Replace YOUR_APP_NAME and YOUR_PAT_TOKEN
curl -X POST "devops-mcp-server.azurewebsites.net/mcp" \
  -H "Content-Type: application/json" \
  -H "X-Azure-DevOps-PAT: YOUR_PAT_TOKEN" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "test_connection",
      "arguments": {}
    }
  }'
```

### Test Server Info
```bash
curl "https://YOUR_APP_NAME.azurewebsites.net/"
```

## Step 4: Monitor and Troubleshoot

### Check Logs
```bash
az webapp log tail --name devops-mcp-server --resource-group rg-devops-mcp
```

### Quick Fix for MCP Import Error
If you see "ModuleNotFoundError: No module named 'mcp'", run these commands:

```bash
# Option 1: Switch to Python startup script (recommended)
az webapp config set --name devops-mcp-server --resource-group rg-devops-mcp --startup-file "python deploy/startup.py"

# Option 2: Update startup command to install dependencies first
az webapp config set --name devops-mcp-server --resource-group rg-devops-mcp --startup-file "pip install -r requirements.txt && python -m azure_devops_mcp.main $AZURE_DEVOPS_ORG --authentication pat --mode http --host 0.0.0.0 --port $PORT --domains all"

# Restart the web app to apply changes
az webapp restart --name devops-mcp-server --resource-group rg-devops-mcp
```

### Common Issues

1. **MCP Module Not Found Error**: 
   ```
   ModuleNotFoundError: No module named 'mcp'
   ```
   **Solution**: 
   - Use the Python startup script: `az webapp config set --name devops-mcp-server --resource-group rg-devops-mcp --startup-file "python deploy/startup.py"`
   - Or manually install dependencies by adding this to your startup command: `pip install -r requirements.txt &&`

2. **Startup Errors**: Check logs for missing dependencies
3. **Port Conflicts**: Azure Web Apps use PORT environment variable
4. **Authentication Errors**: Verify AZURE_DEVOPS_ORG is set correctly

### Expected Response
```json
{
  "status": "success", 
  "message": "Connected to Azure DevOps organization: your-org",
  "organization": "your-org",
  "connection_url": "https://dev.azure.com/your-org"
}
```

## Security Considerations

1. **PAT Token Security**: Never log PAT tokens, rotate regularly
2. **HTTPS Only**: Enable HTTPS-only in Azure Web App settings
3. **Access Restrictions**: Configure IP restrictions if needed
4. **Application Insights**: Enable for monitoring and diagnostics

## Production Checklist

- [ ] Environment variables configured
- [ ] Startup command set correctly
- [ ] HTTPS-only enabled
- [ ] Application Insights configured
- [ ] Health check endpoint configured
- [ ] Log retention configured
- [ ] Scaling rules defined (if needed)
- [ ] Backup strategy in place

## Cost Optimization

- Start with B1 (Basic) tier for testing
- Monitor CPU/Memory usage
- Scale up/out as needed
- Consider App Service Environment for high-traffic scenarios

Your Azure DevOps MCP server should now be running on Azure Web App with PAT header authentication! 🚀