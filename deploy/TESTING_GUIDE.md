# 🚀 Testing on Azure Web App - Complete Guide

I've created a complete Azure Web App deployment package for you! Since I can't directly deploy to Azure from this environment, here's everything you need to test the PAT authentication on Azure Web App.

## 📁 Files Created

```
deploy/
├── requirements.txt          # Python dependencies
├── startup.sh               # Linux startup script  
├── startup.cmd             # Windows startup script
├── package.json            # App metadata
├── AZURE_DEPLOYMENT_GUIDE.md  # Detailed deployment guide
├── test_azure_webapp.py    # Test script for deployed app
└── deploy_to_azure.sh      # Automated deployment script
```

## 🏃‍♂️ Quick Start (Automated Deployment)

### Option 1: Use the Automated Script

```bash
# 1. Make the script executable
chmod +x deploy/deploy_to_azure.sh

# 2. Edit the script to set your organization
nano deploy/deploy_to_azure.sh  # Set AZURE_DEVOPS_ORG="your-org-name"

# 3. Run the deployment
./deploy/deploy_to_azure.sh
```

### Option 2: Manual Azure CLI Deployment

```bash
# 1. Login to Azure
az login

# 2. Create resources
az group create --name rg-devops-mcp --location eastus

az appservice plan create \
    --name asp-devops-mcp \
    --resource-group rg-devops-mcp \
    --sku B1 \
    --is-linux

az webapp create \
    --name your-unique-app-name \
    --resource-group rg-devops-mcp \
    --plan asp-devops-mcp \
    --runtime "PYTHON:3.11"

# 3. Configure environment
az webapp config appsettings set \
    --name your-unique-app-name \
    --resource-group rg-devops-mcp \
    --settings AZURE_DEVOPS_ORG="your-organization-name"

az webapp config set \
    --name your-unique-app-name \
    --resource-group rg-devops-mcp \
    --startup-file "deploy/startup.sh"

# 4. Deploy the code
az webapp up \
    --name your-unique-app-name \
    --resource-group rg-devops-mcp
```

## 🧪 Testing the Deployed App

### Method 1: Use the Test Script

```bash
# Test with the provided script
python deploy/test_azure_webapp.py \
    your-app-name.azurewebsites.net \
    your-pat-token \
    your-organization-name
```

### Method 2: Manual Testing with curl

```bash
# Test server info
curl "https://your-app-name.azurewebsites.net/"

# Test with PAT authentication
curl -X POST "https://your-app-name.azurewebsites.net/call" \
  -H "Content-Type: application/json" \
  -H "X-Azure-DevOps-PAT: your-personal-access-token" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "test_connection",
      "arguments": {}
    }
  }'

# Test without PAT (should fail with 401)
curl -X POST "https://your-app-name.azurewebsites.net/call" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call", 
    "params": {
      "name": "test_connection",
      "arguments": {}
    }
  }'
```

### Method 3: PowerShell Testing

```powershell
# Test server info
Invoke-RestMethod -Uri "https://your-app-name.azurewebsites.net/" -Method GET

# Test with PAT
$headers = @{"X-Azure-DevOps-PAT" = "your-personal-access-token"}
$body = @{
    method = "tools/call"
    params = @{
        name = "test_connection"
        arguments = @{}
    }
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "https://your-app-name.azurewebsites.net/call" `
    -Method POST `
    -Headers $headers `
    -Body $body `
    -ContentType "application/json"
```

## 🔍 Expected Results

### Server Info Response
```json
{
  "name": "IDE DevOps MCP",
  "version": "1.0.0",
  "organization": "your-org-name",
  "enabled_domains": [
    "work-items", "pipelines", "core", "search", 
    "work", "test-plans", "advanced-security", 
    "repositories", "wiki"
  ],
  "authentication": "PAT via X-Azure-DevOps-PAT header",
  "org_url": "https://dev.azure.com/your-org-name"
}
```

### Test Connection Success
```json
{
  "status": "success",
  "message": "Connected to Azure DevOps organization: your-org-name (PAT authentication)",
  "organization": "your-org-name"
}
```

### Authentication Failure (without PAT)
```json
{
  "error": "Authentication required",
  "message": "Please provide PAT token in 'X-Azure-DevOps-PAT' header"
}
```

## 🔧 Troubleshooting

### Check Deployment Logs
```bash
az webapp log tail --name your-app-name --resource-group rg-devops-mcp
```

### Common Issues:
1. **Startup Errors**: Check if all dependencies are in requirements.txt
2. **Environment Variables**: Ensure AZURE_DEVOPS_ORG is set
3. **Port Issues**: Azure automatically sets the PORT environment variable
4. **Authentication**: Make sure you're using a valid Azure DevOps PAT token

### Monitor Application
```bash
# Check app status
az webapp show --name your-app-name --resource-group rg-devops-mcp

# View configuration
az webapp config appsettings list --name your-app-name --resource-group rg-devops-mcp
```

## 🎯 What This Tests

✅ **PAT Header Authentication**: Validates X-Azure-DevOps-PAT header processing  
✅ **Environment Variables**: Tests AZURE_DEVOPS_ORG from Azure Web App settings  
✅ **HTTP Mode**: Verifies the server runs correctly in HTTP mode  
✅ **Security**: Confirms requests without PAT are rejected  
✅ **Azure Integration**: Tests deployment on actual Azure infrastructure  

## 🚀 Ready to Deploy!

Everything is prepared for you to test the PAT authentication on Azure Web App. The deployment will demonstrate:

1. **Real Azure Environment**: Running on actual Azure Web App infrastructure
2. **PAT Security**: Header-based authentication working end-to-end  
3. **Production Readiness**: All the components working together
4. **Scalability**: Ready for production workloads

Just run the deployment script or follow the manual steps, and you'll have a fully functional Azure DevOps MCP server with PAT authentication running on Azure! 🎉