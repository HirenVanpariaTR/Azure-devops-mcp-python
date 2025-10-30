#!/bin/bash

# Azure DevOps MCP - Quick Deploy Script
# This script deploys the Azure DevOps MCP server to Azure Web App

set -e

# Configuration - Update these values
RESOURCE_GROUP="rg-devops-mcp"
APP_SERVICE_PLAN="asp-devops-mcp"
WEB_APP_NAME="devops-mcp-server-$(date +%s)"  # Unique name with timestamp
LOCATION="eastus"
AZURE_DEVOPS_ORG=""  # Set your organization name here

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Azure CLI is installed and logged in
check_prerequisites() {
    echo_info "Checking prerequisites..."
    
    if ! command -v az &> /dev/null; then
        echo_error "Azure CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! az account show &> /dev/null; then
        echo_error "Not logged in to Azure CLI. Please run 'az login' first."
        exit 1
    fi
    
    if [ -z "$AZURE_DEVOPS_ORG" ]; then
        echo_warning "AZURE_DEVOPS_ORG not set in script. You'll need to set it manually later."
    fi
    
    echo_success "Prerequisites check passed!"
}

# Create Azure resources
create_resources() {
    echo_info "Creating Azure resources..."
    
    # Create resource group
    echo_info "Creating resource group: $RESOURCE_GROUP"
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output table
    
    # Create App Service Plan
    echo_info "Creating App Service Plan: $APP_SERVICE_PLAN"
    az appservice plan create \
        --name "$APP_SERVICE_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --sku B1 \
        --is-linux \
        --output table
    
    # Create Web App
    echo_info "Creating Web App: $WEB_APP_NAME"
    az webapp create \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --runtime "PYTHON:3.11" \
        --output table
    
    echo_success "Azure resources created successfully!"
}

# Configure the web app
configure_webapp() {
    echo_info "Configuring Web App..."
    
    # Set environment variables
    if [ -n "$AZURE_DEVOPS_ORG" ]; then
        echo_info "Setting AZURE_DEVOPS_ORG environment variable"
        az webapp config appsettings set \
            --name "$WEB_APP_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --settings AZURE_DEVOPS_ORG="$AZURE_DEVOPS_ORG" \
            --output table
    fi
    
    # Set startup command
    echo_info "Setting startup command"
    az webapp config set \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --startup-file "deploy/startup.sh" \
        --output table
    
    # Enable HTTPS only
    echo_info "Enabling HTTPS only"
    az webapp update \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --https-only true \
        --output table
    
    echo_success "Web App configured successfully!"
}

# Deploy the application
deploy_app() {
    echo_info "Deploying application..."
    
    # Create a deployment package
    echo_info "Creating deployment package..."
    
    # Make sure we're in the project root
    if [ ! -f "azure_devops_mcp/main.py" ]; then
        echo_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Deploy using az webapp up
    az webapp up \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$APP_SERVICE_PLAN" \
        --location "$LOCATION" \
        --runtime "PYTHON:3.11" \
        --output table
    
    echo_success "Application deployed successfully!"
}

# Get deployment information
show_deployment_info() {
    echo_info "Getting deployment information..."
    
    WEBAPP_URL=$(az webapp show \
        --name "$WEB_APP_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "defaultHostName" \
        --output tsv)
    
    echo_success "Deployment completed!"
    echo ""
    echo "🌐 Web App URL: https://$WEBAPP_URL"
    echo "🔧 Resource Group: $RESOURCE_GROUP"
    echo "📦 App Name: $WEB_APP_NAME"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Set AZURE_DEVOPS_ORG if not already set:"
    echo "   az webapp config appsettings set --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP --settings AZURE_DEVOPS_ORG=\"your-org-name\""
    echo ""
    echo "2. Test the deployment:"
    echo "   python deploy/test_azure_webapp.py $WEBAPP_URL your-pat-token your-org-name"
    echo ""
    echo "3. Monitor logs:"
    echo "   az webapp log tail --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP"
}

# Main execution
main() {
    echo_info "🚀 Azure DevOps MCP - Azure Web App Deployment"
    echo "=================================================="
    
    check_prerequisites
    create_resources
    configure_webapp
    deploy_app
    show_deployment_info
    
    echo_success "🎉 Deployment script completed!"
}

# Run main function
main "$@"